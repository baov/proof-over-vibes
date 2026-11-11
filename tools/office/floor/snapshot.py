"""Derive who works now from the files a run writes.

Read-only. A role is only visible through the files it writes: the snapshot
says which role the files point at, not what a role is thinking.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path

from .decisions import decision_counts
from .reports import parse_brief, parse_front_matter, split_front_matter
from .roles import ROLE_TEAM

STAGES = ("in-progress", "done", "aborted")
HARNESS_SUFFIX = "-harness-improvement"
MAX_REPORT_CHARS = 100_000
AGENTS_DIR = Path(__file__).resolve().parents[3] / "agents"
STATES = ("done", "blocked", "escalate")

REPORT_FILES = {
    "stories.md": "product-owner",
    "architect.md": "architect",
    "plan.md": "planner",
    "diagnostician.md": "diagnostician",
    "cartographer.md": "cartographer",
    "harness-engineer.md": "harness-engineer",
    "product-manager.md": "product-manager",
}
DEVELOPER_NOTE = re.compile(r"^developer-\d+\.md$")

# role -> role that works after it, per kind of run. The reviewer is decided apart.
FOLLOW = {
    "feature": {
        "product-owner": "architect",
        "architect": "planner",
        "planner": "developer",
        "developer": "reviewer",
    },
    "story": {"planner": "developer", "developer": "reviewer"},
    "bug": {"diagnostician": "reviewer", "developer": "reviewer"},
}
OTHER_FOLLOW = {"cartographer": "harness-engineer"}

# The roles a run goes through, in order, for the page's pipeline strip.
ROUTES = {
    "feature": ["orchestrator", "product-owner", "architect", "planner", "developer", "reviewer"],
    "story": ["orchestrator", "planner", "developer", "reviewer"],
    "bug": ["orchestrator", "diagnostician", "reviewer", "developer"],
}

# The file each role writes, as shown to the reader. None: this page does not read it.
EXPECTS = {
    "orchestrator": "brief.md",
    "product-owner": "stories.md",
    "architect": "architect.md",
    "planner": "plan.md",
    "developer": "developer-<n>.md",
    "diagnostician": "diagnostician.md",
    "reviewer": ".reviews/<branch>-<date>-<n>.md",
    "cartographer": "cartographer.md",
    "harness-engineer": "harness-engineer.md",
    "product-manager": "product-manager.md",
}


@dataclass
class Report:
    role: str
    mtime: float
    front: dict
    proof: bool = False
    path: Path | None = None

    @property
    def status(self) -> str:
        status = self.front.get("status")
        return status if status in STATES else "working"

    @property
    def verdict(self) -> str | None:
        verdict = self.front.get("verdict")
        return verdict if verdict in ("GO", "NO-GO") else None


def _mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def _read(path: Path) -> str | None:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return None


def _make_report(role: str, path: Path, proof: bool = False) -> Report | None:
    mtime, text = _mtime(path), _read(path)
    if mtime is None or text is None:
        return None
    return Report(role, mtime, parse_front_matter(text), proof, path)


def _reports_in(folder: Path) -> list[Report]:
    found = []
    try:
        files = sorted(p for p in folder.iterdir() if p.is_file())
    except OSError:
        return found
    for path in files:
        role = REPORT_FILES.get(path.name)
        if role is None and DEVELOPER_NOTE.match(path.name):
            role = "developer"
        report = _make_report(role, path) if role else None
        if report:
            found.append(report)
    return found


def _newest_inside(folder: Path) -> float:
    times = [_mtime(p) for p in folder.rglob("*") if p.is_file()]
    return max([t for t in times if t is not None], default=_mtime(folder) or 0.0)


def _latest_subfolder(run_dir: Path) -> Path | None:
    try:
        subs = [p for p in run_dir.iterdir() if p.is_dir()]
    except OSError:
        return None
    return max(subs, key=_newest_inside, default=None)


def _kind(reports: list[Report], has_subfolders: bool) -> str:
    roles = {r.role for r in reports}
    if "product-owner" in roles or has_subfolders:
        return "feature"
    if "diagnostician" in roles:
        return "bug"
    return "story"


def _decide(kind: str, last: Report, iteration: int, limit: int, improvement: bool):
    """Return (active_role, human_needed, ready_to_merge) from the newest report."""
    if last.status != "done":
        return last.role, False, False
    if last.role == "reviewer":
        if last.verdict == "GO":
            return ("developer", False, False) if last.proof else (None, False, True)
        if last.proof:
            return "diagnostician", False, False
        if iteration < limit:
            return "developer", False, False
        return (None, True, False) if improvement else ("failure-analyst", False, False)
    nxt = FOLLOW[kind].get(last.role) or OTHER_FOLLOW.get(last.role)
    return nxt, False, False


def _review_reports(root: Path) -> list[Report]:
    """The reviewer's reports: `.reviews/*.md`, and `reviews/*.md` when the file says `role: reviewer`.

    The role writes to `.reviews/`, but a project whose `.gitignore` hides it may get the reports
    in a visible `reviews/` instead; the front-matter keeps an unrelated folder from being read.
    """
    out = []
    for name, strict in ((".reviews", False), ("reviews", True)):
        try:
            files = sorted((root / name).glob("*.md"))
        except OSError:
            continue
        for path in files:
            report = _make_report("reviewer", path, proof=path.stem.endswith("-proof"))
            if report and (not strict or report.front.get("role") == "reviewer"):
                out.append(report)
    return out


def _start(run_dir: Path) -> float:
    """When the run began: the oldest file of its work folder.

    brief.md is rewritten at every iteration, so its own mtime moves; for a
    feature, only its latest story subfolder counts.
    """
    folder = _latest_subfolder(run_dir) or run_dir
    times = [_mtime(p) for p in folder.rglob("*") if p.is_file()]
    return min([t for t in times if t is not None], default=_mtime(folder) or 0.0)


def _brief_report(run_dir: Path, sub: Path | None) -> Report | None:
    """The brief is the Orchestrator's page: its objective, criteria and counter."""
    path = sub / "brief.md" if sub and (sub / "brief.md").exists() else run_dir / "brief.md"
    mtime = _mtime(path)
    return None if mtime is None else Report("orchestrator", mtime, {"status": "done"}, path=path)


def _history(reports: list[Report], role: str) -> list[Report]:
    return sorted((r for r in reports if r.role == role and r.path is not None), key=lambda r: (r.mtime, r.path.name))


def _took(reports: list[Report]) -> dict[int, float]:
    """How long each finished report took: from the newest file written before it to its own write.

    A role is only visible through its files, so a task starts when the previous file of the run
    appeared (the hand-off) and ends when the role's own report did. The first file of a run has
    nothing before it, and a report still being written is not finished: neither gets a duration.
    """
    took = {}
    for report in reports:
        if report.status != "done" or report.path is None or report.role == "orchestrator":
            continue  # the brief is rewritten every iteration: its own task has no start to measure
        before = [r.mtime for r in reports if r is not report and r.mtime < report.mtime]
        if before:
            took[id(report)] = round(report.mtime - max(before), 1)
    return took


def _summary(report: Report, took: dict[int, float]) -> dict:
    return {
        "name": report.path.name, "mtime": report.mtime, "status": report.status, "verdict": report.verdict,
        "duration": took.get(id(report)),
    }


def _run_view(root: Path, stage: str, run_dir: Path, reviews: list[Report]) -> tuple[dict, list[Report]] | None:
    sub = _latest_subfolder(run_dir)
    reports = _reports_in(run_dir) + (_reports_in(sub) if sub else []) + reviews
    brief_text = _read((sub / "brief.md") if sub and (sub / "brief.md").exists() else run_dir / "brief.md")
    has_brief = (run_dir / "brief.md").exists() or (sub is not None and (sub / "brief.md").exists())
    if not reports and not has_brief:
        return None
    iteration, limit = parse_brief(brief_text or "")
    kind = _kind(reports, sub is not None)
    slug = run_dir.name
    improvement = any((root / ".plans" / s / f"{slug}{HARNESS_SUFFIX}").is_dir() for s in STAGES)

    roles = {r: {"team": t, "state": "idle", "verdict": None} for r, t in ROLE_TEAM.items()}
    latest_by_role: dict[str, Report] = {}
    for rep in sorted(reports, key=lambda r: r.mtime):
        latest_by_role[rep.role] = rep
    for role, rep in latest_by_role.items():
        roles[role]["state"] = rep.status
        if role == "reviewer":
            roles[role]["verdict"] = rep.verdict
    if improvement:
        roles["failure-analyst"]["state"] = "done"
    brief = _brief_report(run_dir, sub)
    shown = reports + [brief] if brief else reports
    took = _took(shown)
    for role in roles:
        roles[role]["reports"] = [_summary(rep, took) for rep in _history(shown, role)]
        roles[role]["expects"] = EXPECTS.get(role)

    active, human, ready = None, False, False
    if reports:
        route_order = list(FOLLOW[kind]) + ["reviewer"]
        last = max(reports, key=lambda r: (r.mtime, route_order.index(r.role) if r.role in route_order else -1))
        decision = _decide(kind, last, iteration, limit, improvement)
        if stage == "in-progress":
            active, human, ready = decision
        elif stage == "done":
            ready = decision[2]
    elif stage == "in-progress":
        active = "orchestrator"
    if active and roles[active]["state"] not in ("blocked", "escalate"):
        roles[active]["state"] = "working"
    decisions = decision_counts(root, slug)
    human = human or any(v["state"] == "escalate" for v in roles.values()) or decisions["pending"] > 0

    updated = max([r.mtime for r in reports] + [_newest_inside(run_dir)])
    view = {
        "slug": slug, "stage": stage, "kind": kind,
        "iteration": iteration, "limit": limit,
        "active_role": active, "human_needed": human, "ready_to_merge": ready,
        "updated": updated, "route": list(ROUTES[kind]), "decisions": decisions, "roles": roles,
    }
    return view, shown


def role_about(agents_dir: Path = AGENTS_DIR) -> dict[str, str]:
    """One sentence per role, from the `description` of its agents/<role>.md, when that file is there."""
    about = {}
    for role in ROLE_TEAM:
        text = _read(Path(agents_dir) / f"{role}.md")
        description = parse_front_matter(text).get("description", "") if text else ""
        if description:
            about[role] = re.split(r"(?<=[.!?])\s", description, maxsplit=1)[0]
    return about


_ABOUT: dict[str, str] | None = None


def _cached_about() -> dict[str, str]:
    global _ABOUT
    if _ABOUT is None:
        _ABOUT = role_about()
    return _ABOUT


def _collect(root: Path) -> list[tuple[dict, list[Report]]]:
    """Every run as (view, its reports), newest first."""
    root = Path(root)
    reviews = _review_reports(root)
    run_dirs = []
    for stage in STAGES:
        folder = root / ".plans" / stage
        try:
            children = sorted(p for p in folder.iterdir() if p.is_dir() and not p.name.endswith(HARNESS_SUFFIX))
        except OSError:
            continue
        run_dirs.extend((stage, p) for p in children)

    # A feature archives story by story into .plans/done/<feature>/, so its slug can sit in two
    # stages at once. The live one speaks for the run: the archived twin would show twice, and a
    # rebase that rewrites its files would make it look newer and steal the reviews.
    seen: set[str] = set()
    run_dirs = [(s, d) for s, d in run_dirs if not (d.name in seen or seen.add(d.name))]

    # A review belongs to the run started most recently before it was written.
    starts = {d: _start(d) for _, d in run_dirs}
    owned: dict[Path, list[Report]] = {d: [] for _, d in run_dirs}
    for review in reviews:
        candidates = [d for d, t in starts.items() if t <= review.mtime]
        if candidates:
            owned[max(candidates, key=lambda d: starts[d])].append(review)

    runs = []
    for stage, run_dir in run_dirs:
        found = _run_view(root, stage, run_dir, owned[run_dir])
        if found:
            runs.append(found)
    runs.sort(key=lambda r: r[0]["updated"], reverse=True)
    return runs


def build_snapshot(root: Path, now: float | None = None) -> dict:
    return {
        "generated": time.time() if now is None else now,
        "project": Path(root).name,
        "role_teams": dict(ROLE_TEAM),
        "role_about": _cached_about(),
        "runs": [view for view, _ in _collect(root)],
    }


def read_report(root: Path, slug: str, role: str, index: int | None = None) -> dict | None:
    """The content of one report of a role in a run; the newest unless `index` picks another.

    The caller names a run and a role, never a path: the file is found from the same
    scan as the snapshot, so nothing outside the work folders can be read.
    """
    if role not in ROLE_TEAM:
        return None
    for view, reports in _collect(root):
        if view["slug"] != slug:
            continue
        history = _history(reports, role)
        if not history:
            return None
        position = len(history) - 1 if index is None else index
        if not 0 <= position < len(history):
            return None
        report = history[position]
        text = _read(report.path)
        if text is None:
            return None
        front, body = split_front_matter(text)
        try:
            shown = report.path.relative_to(Path(root)).as_posix()
        except ValueError:
            shown = report.path.name
        return {
            "role": role, "name": report.path.name, "path": shown, "mtime": report.mtime,
            "index": position, "count": len(history),
            "status": report.status, "verdict": report.verdict,
            "front": front, "body": body[:MAX_REPORT_CHARS], "truncated": len(body) > MAX_REPORT_CHARS,
        }
    return None
