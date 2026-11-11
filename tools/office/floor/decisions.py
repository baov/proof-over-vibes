"""The decision log of a project, read-only: which decisions nobody has read yet.

`docs/business/decisions.md` is written by the Product Owner and, when a person answers, by that
person. A decision that a role recommended and the orchestrator relayed (`answered-by-delegate`) is one
nobody read; `human-needed` is one that waits for a person. This module only reads the log.
"""

from __future__ import annotations

import re
from pathlib import Path

LOG = Path("docs") / "business" / "decisions.md"
MAX_ENTRIES = 300
OPEN = ("human-needed", "answered-by-delegate")
FIELDS = ("status", "answer", "source", "recommended", "request")

_HEADING = re.compile(r"^###\s+(D-(\d+))\s*(.*)$")
_FIELD = re.compile(r"^\s*-\s+([A-Za-z_-]+):\s*(.*)$")
_cache: dict[Path, tuple[float, int, list[dict]]] = {}


def parse_decisions(text: str) -> list[dict]:
    """The entries of the log: `### D-<n> <question>` followed by `- key: value` lines."""
    entries: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        heading = _HEADING.match(line)
        if heading:
            current = {"id": heading.group(1), "n": int(heading.group(2)), "title": heading.group(3).strip()}
            entries.append(current)
            continue
        field = _FIELD.match(line)
        if field and current is not None:
            current.setdefault(field.group(1).lower(), field.group(2).strip())
    return entries


def to_review(entries: list[dict]) -> list[dict]:
    """The decisions a person should still look at: pending ones first, then those nobody read.

    A later `answered` entry settles an earlier one when it has the same question, or when it names
    the earlier id in its source, its answer or its question (the log does not fix a field for it).
    """
    settled: set[str] = set()
    for later in entries:
        if later.get("status") != "answered":
            continue
        text = " ".join([later["title"], later.get("source", ""), later.get("answer", "")])
        for earlier in entries:
            if earlier["n"] >= later["n"] or earlier.get("status") not in OPEN:
                continue
            if earlier["title"].lower() == later["title"].lower() or re.search(rf"\b{earlier['id']}\b", text):
                settled.add(earlier["id"])
    review = [e for e in entries if e.get("status") in OPEN and e["id"] not in settled]
    review.sort(key=lambda e: (e["status"] != "human-needed", e["n"]))
    return review


def _read(root: Path) -> list[dict]:
    path = Path(root) / LOG
    try:
        stat = path.stat()
        cached = _cache.get(path)
        if cached and cached[0] == stat.st_mtime and cached[1] == stat.st_size:
            return cached[2]
        entries = parse_decisions(path.read_text(errors="replace"))
    except OSError:
        return []
    _cache[path] = (stat.st_mtime, stat.st_size, entries)
    return entries


def decisions_for(root: Path, run: str | None = None) -> list[dict]:
    """The decisions to review, for one run (by the `request:` field) or for all of them."""
    review = to_review(_read(root))
    if run is not None:
        review = [e for e in review if e.get("request") == run]
    return [{key: e.get(key, "") for key in ("id", "title", *FIELDS)} for e in review[:MAX_ENTRIES]]


def decision_counts(root: Path, run: str) -> dict:
    review = decisions_for(root, run)
    return {
        "pending": sum(1 for e in review if e["status"] == "human-needed"),
        "unread": sum(1 for e in review if e["status"] == "answered-by-delegate"),
    }
