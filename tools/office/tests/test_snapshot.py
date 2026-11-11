from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from floor.roles import ROLE_TEAM
from floor.snapshot import MAX_REPORT_CHARS, build_snapshot, read_report, role_about

RUN = ".plans/in-progress/feat"


def put(root: Path, rel: str, text: str, mtime: float) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    os.utime(path, (mtime, mtime))


def report(role: str, status: str = "done", verdict: str | None = None) -> str:
    lines = ["---", f"role: {role}", f"status: {status}"]
    if verdict:
        lines.append(f"verdict: {verdict}")
    return "\n".join(lines + ["---", "body"])


def brief(n: int = 0) -> str:
    return f"Iteration counter: {n}\nIteration limit: 5\n"


class DurationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def roles(self) -> dict:
        return build_snapshot(self.root)["runs"][0]["roles"]

    def test_finished_report_took_the_time_since_the_previous_file(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/plan.md", report("planner"), 190)
        put(self.root, f"{RUN}/developer-0.md", report("developer"), 400)
        roles = self.roles()
        self.assertEqual(roles["planner"]["reports"][0]["duration"], 90)
        self.assertEqual(roles["developer"]["reports"][0]["duration"], 210)

    def test_orchestrator_and_unfinished_reports_have_no_duration(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/plan.md", report("planner", status="blocked"), 190)
        roles = self.roles()
        self.assertIsNone(roles["orchestrator"]["reports"][0]["duration"])
        self.assertIsNone(roles["planner"]["reports"][0]["duration"])

    def test_first_file_of_a_run_has_no_duration(self):
        put(self.root, f"{RUN}/plan.md", report("planner"), 190)
        self.assertIsNone(self.roles()["planner"]["reports"][0]["duration"])


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def run0(self) -> dict:
        return build_snapshot(self.root)["runs"][0]

    def test_empty_root_gives_no_runs(self):
        self.assertEqual(build_snapshot(self.root)["runs"], [])

    def test_snapshot_lists_role_teams_even_without_a_run(self):
        teams = build_snapshot(self.root)["role_teams"]
        self.assertEqual(teams, ROLE_TEAM)

    def test_brief_only_makes_orchestrator_work(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        run = self.run0()
        self.assertEqual(run["active_role"], "orchestrator")
        self.assertEqual(run["roles"]["orchestrator"]["state"], "working")
        self.assertEqual(len(run["roles"]), len(ROLE_TEAM))
        others = [r for r, v in run["roles"].items() if r != "orchestrator"]
        self.assertTrue(all(run["roles"][r]["state"] == "idle" for r in others))

    def test_planner_done_makes_developer_work(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/plan.md", report("planner"), 200)
        run = self.run0()
        self.assertEqual(run["kind"], "story")
        self.assertEqual(run["active_role"], "developer")
        self.assertEqual(run["roles"]["planner"]["state"], "done")
        self.assertEqual(run["roles"]["developer"]["state"], "working")

    def test_feature_route_follows_stories_file(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/stories.md", report("product-owner"), 200)
        self.assertEqual(self.run0()["kind"], "feature")
        self.assertEqual(self.run0()["active_role"], "architect")
        put(self.root, f"{RUN}/architect.md", report("architect"), 300)
        self.assertEqual(self.run0()["active_role"], "planner")

    def test_reviewer_no_go_sends_developer_back(self):
        put(self.root, f"{RUN}/brief.md", brief(1), 100)
        put(self.root, f"{RUN}/developer-1.md", report("developer"), 200)
        put(self.root, ".reviews/b-d-1.md", report("reviewer", verdict="NO-GO"), 300)
        run = self.run0()
        self.assertEqual(run["active_role"], "developer")
        self.assertEqual(run["iteration"], 1)
        self.assertEqual(run["roles"]["reviewer"]["verdict"], "NO-GO")

    def test_reviewer_go_is_ready_to_merge(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/developer-1.md", report("developer"), 200)
        put(self.root, ".reviews/b-d-1.md", report("reviewer", verdict="GO"), 300)
        run = self.run0()
        self.assertIsNone(run["active_role"])
        self.assertTrue(run["ready_to_merge"])
        self.assertEqual(run["roles"]["reviewer"]["verdict"], "GO")

    def test_blocked_report_stays_active_and_blocked(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/developer-1.md", report("developer", "blocked"), 200)
        run = self.run0()
        self.assertEqual(run["active_role"], "developer")
        self.assertEqual(run["roles"]["developer"]["state"], "blocked")
        self.assertFalse(run["human_needed"])

    def test_escalate_needs_human(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/architect.md", report("architect", "escalate"), 200)
        run = self.run0()
        self.assertTrue(run["human_needed"])
        self.assertEqual(run["roles"]["architect"]["state"], "escalate")

    def test_limit_reached_activates_failure_analyst(self):
        put(self.root, f"{RUN}/brief.md", brief(5), 100)
        put(self.root, ".reviews/b-d-5.md", report("reviewer", verdict="NO-GO"), 300)
        run = self.run0()
        self.assertEqual(run["active_role"], "failure-analyst")
        self.assertEqual(run["roles"]["failure-analyst"]["state"], "working")

    def test_limit_reached_with_improvement_folder_needs_human(self):
        put(self.root, f"{RUN}/brief.md", brief(5), 100)
        put(self.root, ".reviews/b-d-5.md", report("reviewer", verdict="NO-GO"), 300)
        put(self.root, f"{RUN}-harness-improvement/plan.md", report("planner"), 50)
        run = next(r for r in build_snapshot(self.root)["runs"] if r["slug"] == "feat")
        self.assertIsNone(run["active_role"])
        self.assertTrue(run["human_needed"])
        self.assertEqual(run["roles"]["failure-analyst"]["state"], "done")

    def test_half_written_report_is_working_not_an_error(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/plan.md", "---\nrole: pla", 200)
        run = self.run0()
        self.assertEqual(run["roles"]["planner"]["state"], "working")
        self.assertEqual(run["active_role"], "planner")

    def test_bug_proof_go_sends_to_developer(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/diagnostician.md", report("diagnostician"), 200)
        self.assertEqual(self.run0()["kind"], "bug")
        self.assertEqual(self.run0()["active_role"], "reviewer")
        put(self.root, ".reviews/x-proof.md", report("reviewer", verdict="GO"), 300)
        self.assertEqual(self.run0()["active_role"], "developer")

    def test_done_and_aborted_stages(self):
        put(self.root, ".plans/done/a/brief.md", brief(), 100)
        put(self.root, ".plans/aborted/b/brief.md", brief(), 200)
        stages = {r["slug"]: r["stage"] for r in build_snapshot(self.root)["runs"]}
        self.assertEqual(stages, {"a": "done", "b": "aborted"})

    def test_runs_sorted_newest_first(self):
        put(self.root, ".plans/in-progress/old/brief.md", brief(), 100)
        put(self.root, ".plans/in-progress/new/brief.md", brief(), 500)
        slugs = [r["slug"] for r in build_snapshot(self.root)["runs"]]
        self.assertEqual(slugs, ["new", "old"])

    def test_feature_reads_latest_story_subfolder(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/stories.md", report("product-owner"), 110)
        put(self.root, f"{RUN}/architect.md", report("architect"), 120)
        put(self.root, f"{RUN}/story-1/plan.md", report("planner"), 130)
        put(self.root, f"{RUN}/story-1/developer-1.md", report("developer"), 140)
        put(self.root, f"{RUN}/story-2/plan.md", report("planner"), 200)
        run = self.run0()
        self.assertEqual(run["kind"], "feature")
        self.assertEqual(run["active_role"], "developer")
        self.assertEqual(run["roles"]["developer"]["state"], "working")

    def test_brief_rewritten_after_a_no_go_keeps_the_review(self):
        # The orchestrator bumps the counter in brief.md after each NO-GO.
        put(self.root, f"{RUN}/brief.md", brief(0), 100)
        put(self.root, f"{RUN}/developer-0.md", report("developer"), 200)
        put(self.root, ".reviews/b-d-0.md", report("reviewer", verdict="NO-GO"), 300)
        put(self.root, f"{RUN}/brief.md", brief(1), 310)
        run = self.run0()
        self.assertEqual(run["active_role"], "developer")
        self.assertEqual(run["roles"]["reviewer"]["verdict"], "NO-GO")

    def test_failure_analyst_still_active_after_the_counter_bump(self):
        put(self.root, f"{RUN}/brief.md", brief(4), 100)
        put(self.root, f"{RUN}/developer-4.md", report("developer"), 200)
        put(self.root, ".reviews/b-d-4.md", report("reviewer", verdict="NO-GO"), 300)
        put(self.root, f"{RUN}/brief.md", brief(5), 310)
        self.assertEqual(self.run0()["active_role"], "failure-analyst")

    def test_a_rewritten_brief_does_not_steal_another_runs_review(self):
        put(self.root, ".plans/in-progress/a/plan.md", report("planner"), 100)
        put(self.root, ".plans/in-progress/b/brief.md", brief(), 150)
        put(self.root, ".plans/in-progress/b/plan.md", report("planner"), 160)
        put(self.root, ".plans/in-progress/a/brief.md", brief(1), 300)
        put(self.root, ".reviews/b-d-1.md", report("reviewer", verdict="GO"), 350)
        runs = {r["slug"]: r for r in build_snapshot(self.root)["runs"]}
        self.assertTrue(runs["b"]["ready_to_merge"])
        self.assertFalse(runs["a"]["ready_to_merge"])

    def test_harness_improvement_folder_is_not_a_run(self):
        put(self.root, f"{RUN}/brief.md", brief(5), 100)
        put(self.root, ".reviews/b-d-5.md", report("reviewer", verdict="NO-GO"), 300)
        put(self.root, f"{RUN}-harness-improvement/plan.md", report("failure-analyst"), 400)
        runs = build_snapshot(self.root)["runs"]
        self.assertEqual([r["slug"] for r in runs], ["feat"])
        self.assertTrue(runs[0]["human_needed"])

    def test_archived_run_keeps_ready_to_merge(self):
        put(self.root, ".plans/done/feat/brief.md", brief(), 100)
        put(self.root, ".plans/done/feat/developer-1.md", report("developer"), 200)
        put(self.root, ".reviews/b-d-1.md", report("reviewer", verdict="GO"), 300)
        run = self.run0()
        self.assertEqual(run["stage"], "done")
        self.assertTrue(run["ready_to_merge"])
        self.assertIsNone(run["active_role"])

    def test_role_history_lists_files_in_write_order(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/developer-2.md", report("developer"), 300)
        put(self.root, f"{RUN}/developer-1.md", report("developer", "blocked"), 200)
        history = self.run0()["roles"]["developer"]["reports"]
        self.assertEqual([h["name"] for h in history], ["developer-1.md", "developer-2.md"])
        self.assertEqual(history[0]["status"], "blocked")
        self.assertEqual(self.run0()["roles"]["architect"]["reports"], [])

    def test_read_report_returns_front_matter_and_body(self):
        put(self.root, f"{RUN}/plan.md", report("planner").replace("body", "The plan."), 200)
        got = read_report(self.root, "feat", "planner")
        self.assertEqual(got["name"], "plan.md")
        self.assertEqual(got["path"], ".plans/in-progress/feat/plan.md")
        self.assertEqual(got["front"]["status"], "done")
        self.assertEqual(got["body"].strip(), "The plan.")
        self.assertFalse(got["truncated"])

    def test_read_report_index_selects_an_earlier_file(self):
        put(self.root, f"{RUN}/developer-1.md", report("developer").replace("body", "first"), 200)
        put(self.root, f"{RUN}/developer-2.md", report("developer").replace("body", "second"), 300)
        self.assertEqual(read_report(self.root, "feat", "developer")["body"].strip(), "second")
        self.assertEqual(read_report(self.root, "feat", "developer", 0)["body"].strip(), "first")
        self.assertIsNone(read_report(self.root, "feat", "developer", 5))

    def test_read_report_unknown_run_role_or_empty_history_is_none(self):
        put(self.root, f"{RUN}/plan.md", report("planner"), 200)
        self.assertIsNone(read_report(self.root, "nope", "planner"))
        self.assertIsNone(read_report(self.root, "feat", "../../etc/passwd"))
        self.assertIsNone(read_report(self.root, "feat", "reviewer"))

    def test_read_report_caps_the_body(self):
        put(self.root, f"{RUN}/plan.md", report("planner").replace("body", "x" * (MAX_REPORT_CHARS + 500)), 200)
        got = read_report(self.root, "feat", "planner")
        self.assertEqual(len(got["body"]), MAX_REPORT_CHARS)
        self.assertTrue(got["truncated"])

    def test_orchestrator_history_is_the_brief(self):
        put(self.root, f"{RUN}/brief.md", "Objective: ship it.\n" + brief(2), 100)
        run = self.run0()
        self.assertEqual([h["name"] for h in run["roles"]["orchestrator"]["reports"]], ["brief.md"])
        got = read_report(self.root, "feat", "orchestrator")
        self.assertIn("Objective: ship it.", got["body"])
        self.assertEqual(run["roles"]["orchestrator"]["state"], "working")

    def test_each_role_says_which_file_it_is_expected_to_write(self):
        roles = self.runs_with_brief()["roles"]
        self.assertEqual(roles["planner"]["expects"], "plan.md")
        self.assertEqual(roles["developer"]["expects"], "developer-<n>.md")
        self.assertIsNone(roles["auditor"]["expects"])

    def runs_with_brief(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        return self.run0()

    def test_run_route_follows_the_kind(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        self.assertEqual(self.run0()["route"], ["orchestrator", "planner", "developer", "reviewer"])
        put(self.root, f"{RUN}/stories.md", report("product-owner"), 110)
        self.assertEqual(self.run0()["route"], ["orchestrator", "product-owner", "architect", "planner", "developer", "reviewer"])

    def test_bug_route_starts_with_the_diagnostician(self):
        put(self.root, f"{RUN}/diagnostician.md", report("diagnostician"), 110)
        self.assertEqual(self.run0()["route"], ["orchestrator", "diagnostician", "reviewer", "developer"])

    def test_snapshot_names_the_project(self):
        self.assertEqual(build_snapshot(self.root)["project"], self.root.name)

    def test_role_about_is_the_first_sentence_of_the_agent_description(self):
        agents = self.root / "agents"
        agents.mkdir()
        (agents / "reviewer.md").write_text("---\nname: reviewer\ndescription: Reads the diff. Returns a verdict.\n---\nbody")
        about = role_about(agents)
        self.assertEqual(about["reviewer"], "Reads the diff.")
        self.assertNotIn("planner", about)
        self.assertEqual(role_about(self.root / "missing"), {})

    def test_run_counts_the_decisions_nobody_read(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        self.assertEqual(self.run0()["decisions"], {"pending": 0, "unread": 0})
        log = (
            "### D-1 Currency\n- status: answered-by-delegate\n- request: feat\n\n"
            "### D-2 Rounding\n- status: human-needed\n- request: feat\n\n"
            "### D-3 Elsewhere\n- status: answered-by-delegate\n- request: other\n"
        )
        put(self.root, "docs/business/decisions.md", log, 100)
        self.assertEqual(self.run0()["decisions"], {"pending": 1, "unread": 1})

    def test_review_attaches_to_the_latest_started_run(self):
        put(self.root, ".plans/in-progress/old/brief.md", brief(), 100)
        put(self.root, ".plans/in-progress/new/brief.md", brief(), 200)
        put(self.root, ".reviews/b-d-1.md", report("reviewer", verdict="GO"), 300)
        runs = {r["slug"]: r for r in build_snapshot(self.root)["runs"]}
        self.assertTrue(runs["new"]["ready_to_merge"])
        self.assertFalse(runs["old"]["ready_to_merge"])


if __name__ == "__main__":
    unittest.main()
