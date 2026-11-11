import os
import tempfile
import unittest
from pathlib import Path

from floor.decisions import decision_counts
from floor.demo import DEMO_STEPS, apply_step, run_demo
from floor.snapshot import build_snapshot

EXPECTED_ACTIVE = [
    "orchestrator", "product-owner", "architect", "planner",
    "developer", "reviewer", "developer", "reviewer", None,
]


class DemoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "project"
        self.root.mkdir()

    def test_demo_steps_walk_the_whole_route(self):
        active, iterations = [], []
        for index in range(len(DEMO_STEPS)):
            apply_step(self.root, index)
            run = build_snapshot(self.root)["runs"][0]
            active.append(run["active_role"])
            iterations.append(run["iteration"])
        self.assertEqual(active, EXPECTED_ACTIVE)
        self.assertEqual(iterations[5], 0)
        self.assertEqual(iterations[6], 1)
        self.assertTrue(run["ready_to_merge"])

    def test_run_demo_applies_every_step_with_the_given_pause(self):
        pauses = []
        run_demo(self.root, step_seconds=2.5, sleep=pauses.append)
        self.assertEqual(pauses, [2.5] * len(DEMO_STEPS))
        self.assertTrue(build_snapshot(self.root)["runs"][0]["ready_to_merge"])

    def test_demo_logs_decisions_nobody_read(self):
        run_demo(self.root, sleep=lambda _: None)
        self.assertEqual(decision_counts(self.root, "demo-feature"), {"pending": 1, "unread": 2})

    def test_demo_never_touches_outside_root(self):
        run_demo(self.root, sleep=lambda _: None)
        self.assertEqual(os.listdir(self.root.parent), ["project"])


if __name__ == "__main__":
    unittest.main()
