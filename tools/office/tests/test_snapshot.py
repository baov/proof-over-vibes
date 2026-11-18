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


def report(role: str, status: str = "done", verdict: str | None = None, proof: str | None = None) -> str:
    lines = ["---", f"role: {role}", f"status: {status}"]
    if verdict:
        lines.append(f"verdict: {verdict}")
    if proof:
        lines.append(f"proof: {proof}")
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
        self.assertEqual(self.run0()["active_role"], "qa")
        put(self.root, f"{RUN}/example-map.md", report("qa"), 400)
        self.assertEqual(self.run0()["active_role"], "planner")

    def test_a_single_story_is_mapped_before_it_is_planned(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/example-map.md", report("qa"), 200)
        run = self.run0()
        self.assertEqual(run["kind"], "story")
        self.assertEqual(run["active_role"], "planner")

    def test_a_map_has_no_proof_and_is_not_a_no_go(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/example-map.md", report("qa"), 200)
        run = self.run0()
        self.assertIsNone(run["roles"]["qa"]["verdict"])
        self.assertEqual(run["iteration"], 0)
        self.assertFalse(run["ready_to_merge"])

    def test_a_map_with_questions_keeps_qa_blocked(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/example-map.md", report("qa", "blocked"), 200)
        run = self.run0()
        self.assertEqual(run["active_role"], "qa")
        self.assertEqual(run["roles"]["qa"]["state"], "blocked")

    def test_architect_again_for_a_story_hands_back_to_the_planner(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/stories.md", report("product-owner"), 110)
        put(self.root, f"{RUN}/architect.md", report("architect"), 120)
        put(self.root, f"{RUN}/example-map.md", report("qa"), 130)
        put(self.root, f"{RUN}/story-1/plan.md", report("planner", "blocked"), 140)
        put(self.root, f"{RUN}/story-1/architect.md", report("architect"), 150)
        self.assertEqual(self.run0()["active_role"], "planner")

    def neighbours(self, role: str, name: str) -> tuple:
        entry = next(r for r in self.run0()["roles"][role]["reports"] if r["name"] == name)
        return entry["from"], entry["to"]

    def test_reports_follow_their_rounds_even_when_the_dates_are_shuffled(self):
        # A run checked out from git: the dates say nothing, the round numbers do.
        put(self.root, f"{RUN}/brief.md", brief(1), 50)
        put(self.root, f"{RUN}/developer-1.md", report("developer"), 100)
        put(self.root, f"{RUN}/qa-0.md", report("qa", proof="NO-GO"), 200)
        put(self.root, f"{RUN}/developer-0.md", report("developer"), 300)
        put(self.root, f"{RUN}/qa-1.md", report("qa", proof="GO"), 150)
        history = [h["name"] for h in self.run0()["roles"]["developer"]["reports"]]
        self.assertEqual(history, ["developer-0.md", "developer-1.md"])
        self.assertEqual(self.neighbours("qa", "qa-0.md"),
                         ({"role": "developer", "index": 0}, {"role": "developer", "index": 1}))

    def test_the_example_map_comes_from_the_architect_and_goes_to_the_planner(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/stories.md", report("product-owner"), 110)
        put(self.root, f"{RUN}/architect.md", report("architect"), 120)
        put(self.root, f"{RUN}/example-map.md", report("qa"), 130)
        put(self.root, f"{RUN}/plan.md", report("planner"), 140)
        self.assertEqual(self.neighbours("qa", "example-map.md"),
                         ({"role": "architect", "index": 0}, {"role": "planner", "index": 0}))

    def test_a_single_story_map_comes_from_the_brief(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/example-map.md", report("qa"), 130)
        frm, to = self.neighbours("qa", "example-map.md")
        self.assertEqual(frm, {"role": "orchestrator", "index": 0})
        self.assertEqual(to, {"role": "planner", "index": None})  # not written yet: the next role at work

    def test_the_final_review_of_a_bug_comes_from_qa(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/diagnostician.md", report("diagnostician"), 110)
        put(self.root, ".reviews/b-proof.md", report("reviewer", verdict="GO"), 120)
        put(self.root, f"{RUN}/developer-0.md", report("developer"), 130)
        put(self.root, f"{RUN}/qa-0.md", report("qa", proof="GO"), 140)
        put(self.root, ".reviews/b-d-0.md", report("reviewer", verdict="GO"), 150)
        self.assertEqual(self.neighbours("reviewer", "b-proof.md"),
                         ({"role": "diagnostician", "index": 0}, {"role": "developer", "index": 0}))
        self.assertEqual(self.neighbours("reviewer", "b-d-0.md"), ({"role": "qa", "index": 0}, None))

    def test_a_review_without_a_round_number_falls_back_to_the_dates(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/developer-0.md", report("developer"), 110)
        put(self.root, f"{RUN}/qa-0.md", report("qa", proof="GO"), 120)
        put(self.root, ".reviews/final-review.md", report("reviewer", verdict="GO"), 130)
        self.assertEqual(self.neighbours("reviewer", "final-review.md"), ({"role": "qa", "index": 0}, None))

    def test_qa_works_after_the_developer(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/developer-0.md", report("developer"), 200)
        run = self.run0()
        self.assertEqual(run["active_role"], "qa")
        self.assertEqual(run["roles"]["qa"]["state"], "working")

    def test_qa_go_or_not_applicable_hands_over_to_the_reviewer(self):
        for proof in ("GO", "not-applicable"):
            with self.subTest(proof=proof):
                put(self.root, f"{RUN}/brief.md", brief(), 100)
                put(self.root, f"{RUN}/developer-0.md", report("developer"), 200)
                put(self.root, f"{RUN}/qa-0.md", report("qa", proof=proof), 300)
                run = self.run0()
                self.assertEqual(run["active_role"], "reviewer")
                self.assertEqual(run["roles"]["qa"]["verdict"], proof)

    def test_qa_no_go_sends_developer_back(self):
        put(self.root, f"{RUN}/brief.md", brief(1), 100)
        put(self.root, f"{RUN}/developer-0.md", report("developer"), 200)
        put(self.root, f"{RUN}/qa-0.md", report("qa", proof="NO-GO"), 300)
        run = self.run0()
        self.assertEqual(run["active_role"], "developer")
        self.assertEqual(run["roles"]["qa"]["verdict"], "NO-GO")
        self.assertFalse(run["ready_to_merge"])

    def test_qa_no_go_at_the_limit_activates_failure_analyst(self):
        put(self.root, f"{RUN}/brief.md", brief(5), 100)
        put(self.root, f"{RUN}/qa-4.md", report("qa", proof="NO-GO"), 300)
        self.assertEqual(self.run0()["active_role"], "failure-analyst")

    def test_qa_evidence_folder_is_not_a_story(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/developer-0.md", report("developer"), 200)
        put(self.root, f"{RUN}/qa-0.md", report("qa", proof="GO"), 300)
        put(self.root, f"{RUN}/qa-0/01-c1-start.png", "png", 310)
        run = self.run0()
        self.assertEqual(run["kind"], "story")
        self.assertEqual(run["active_role"], "reviewer")

    def test_diagnostician_repro_folder_is_not_a_story(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/diagnostician.md", report("diagnostician"), 200)
        put(self.root, f"{RUN}/repro/run.sh", "echo repro", 210)
        run = self.run0()
        self.assertEqual(run["kind"], "bug")
        self.assertEqual(run["active_role"], "reviewer")

    def test_redesign_waits_on_the_direction_then_follows_the_feature_route(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/ux-designer.md", report("ux-designer", "blocked"), 200)
        run = self.run0()
        self.assertEqual(run["kind"], "feature")
        self.assertEqual(run["active_role"], "ux-designer")
        self.assertEqual(run["roles"]["ux-designer"]["state"], "blocked")
        self.assertEqual(run["route"][:3], ["orchestrator", "ux-designer", "product-owner"])
        put(self.root, f"{RUN}/stories.md", report("product-owner"), 300)
        self.assertEqual(self.run0()["active_role"], "architect")

    def test_redesign_review_hands_back_then_waits_for_the_cut(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, f"{RUN}/ux-designer.md", report("ux-designer", "blocked"), 200)
        put(self.root, f"{RUN}/design-review.md", report("product-owner", "blocked"), 300)
        self.assertEqual(self.run0()["active_role"], "ux-designer")
        put(self.root, f"{RUN}/design-review.md", report("product-owner"), 300)
        run = self.run0()
        self.assertEqual(run["active_role"], "product-owner")
        self.assertEqual(run["roles"]["product-owner"]["reports"][0]["name"], "design-review.md")

    def test_redesign_waits_for_a_person_only_on_the_direction_or_a_change(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        asks = lambda *kinds: "---\nrole: ux-designer\nstatus: blocked\nreasons:\n" + "".join(  # noqa: E731
            f'  - "{k}: a question — 9"\n' for k in kinds) + "---\nbody\n"
        put(self.root, f"{RUN}/ux-designer.md", asks("direction", "rule"), 200)
        self.assertFalse(self.run0()["human_needed"])
        put(self.root, f"{RUN}/ux-designer.md", asks("direction", "change"), 210)
        self.assertTrue(self.run0()["human_needed"])

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

    def test_an_archived_run_does_not_wait_for_a_human_any_more(self):
        put(self.root, ".plans/done/feat/brief.md", brief(), 100)
        put(self.root, ".reviews/b-d-1.md", report("reviewer", "escalate", verdict="GO"), 200)
        run = self.run0()
        self.assertFalse(run["human_needed"])
        self.assertEqual(run["roles"]["reviewer"]["state"], "done")

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
        self.assertEqual(roles["qa"]["expects"], "example-map.md, then qa-<n>.md")
        self.assertIsNone(roles["auditor"]["expects"])

    def runs_with_brief(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        return self.run0()

    def test_run_route_follows_the_kind(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        self.assertEqual(self.run0()["route"], ["orchestrator", "planner", "developer", "qa", "reviewer"])
        put(self.root, f"{RUN}/stories.md", report("product-owner"), 110)
        self.assertEqual(self.run0()["route"], ["orchestrator", "product-owner", "architect", "planner", "developer", "qa", "reviewer"])

    def test_bug_route_starts_with_the_diagnostician(self):
        put(self.root, f"{RUN}/diagnostician.md", report("diagnostician"), 110)
        self.assertEqual(self.run0()["route"], ["orchestrator", "diagnostician", "reviewer", "developer", "qa"])

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

    def test_a_pending_decision_needs_a_human_and_an_unread_one_does_not(self):
        put(self.root, f"{RUN}/brief.md", brief(), 100)
        put(self.root, "docs/business/decisions.md", "### D-1 Currency\n- status: answered-by-delegate\n- request: feat\n", 100)
        self.assertFalse(self.run0()["human_needed"])
        put(self.root, "docs/business/decisions.md", "### D-2 Rounding\n- status: human-needed\n- request: feat\n", 100)
        self.assertTrue(self.run0()["human_needed"])

    def test_a_slug_in_two_stages_is_one_run_and_the_live_one_gets_the_review(self):
        put(self.root, ".plans/in-progress/feat/brief.md", brief(), 100)
        put(self.root, ".plans/done/feat/brief.md", brief(), 500)  # an archived story, files touched by a rebase
        put(self.root, ".reviews/b-d-1.md", report("reviewer", verdict="GO"), 600)
        runs = build_snapshot(self.root)["runs"]
        self.assertEqual([r["slug"] for r in runs], ["feat"])
        self.assertEqual(runs[0]["stage"], "in-progress")
        self.assertTrue(runs[0]["ready_to_merge"])

    def test_a_visible_reviews_folder_is_read_when_the_file_says_it_is_a_reviewer_report(self):
        put(self.root, ".plans/in-progress/feat/brief.md", brief(), 100)
        put(self.root, "reviews/notes.md", "---\ntitle: customer reviews\n---\nnice", 300)
        self.assertFalse(self.run0()["ready_to_merge"])
        self.assertEqual(self.run0()["roles"]["reviewer"]["reports"], [])
        put(self.root, "reviews/01-s1.md", report("reviewer", verdict="GO"), 400)
        self.assertTrue(self.run0()["ready_to_merge"])

    def test_review_attaches_to_the_latest_started_run(self):
        put(self.root, ".plans/in-progress/old/brief.md", brief(), 100)
        put(self.root, ".plans/in-progress/new/brief.md", brief(), 200)
        put(self.root, ".reviews/b-d-1.md", report("reviewer", verdict="GO"), 300)
        runs = {r["slug"]: r for r in build_snapshot(self.root)["runs"]}
        self.assertTrue(runs["new"]["ready_to_merge"])
        self.assertFalse(runs["old"]["ready_to_merge"])


if __name__ == "__main__":
    unittest.main()
