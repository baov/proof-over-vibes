from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from floor.decisions import decision_counts, decisions_for, parse_decisions, to_review

LOG = """# Decision log

Append only.

### D-1 Positioning
- status: answered
- answer: narrow and simple
- source: human; docs/product/research.md
- request: product

### D-2 Currency of the totals
- status: answered-by-delegate
- answer: the cart's currency
- source: glossary
- request: checkout-cart

### D-3 Rounding of the totals
- status: human-needed
- answer: pending
- source: none
- recommended: round half up
- request: checkout-cart

### D-4 Empty cart
- status: answered-by-delegate
- answer: allowed
- source: none
- request: other-run
"""


class ParseTest(unittest.TestCase):
    def test_entries_are_read_with_their_fields(self):
        entries = parse_decisions(LOG)
        self.assertEqual([e["id"] for e in entries], ["D-1", "D-2", "D-3", "D-4"])
        third = entries[2]
        self.assertEqual(third["title"], "Rounding of the totals")
        self.assertEqual(third["status"], "human-needed")
        self.assertEqual(third["recommended"], "round half up")
        self.assertEqual(third["request"], "checkout-cart")

    def test_text_before_the_first_entry_and_unknown_lines_are_ignored(self):
        entries = parse_decisions("Intro\n\n### D-7 Only one\n- status: answered\nsome prose\n- answer: yes\n")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["answer"], "yes")

    def test_an_entry_with_missing_fields_still_parses(self):
        entries = parse_decisions("### D-1 Bare\n")
        self.assertEqual(entries[0]["title"], "Bare")
        self.assertNotIn("status", entries[0])


class ToReviewTest(unittest.TestCase):
    def test_only_unread_and_pending_decisions_are_left_and_pending_come_first(self):
        review = to_review(parse_decisions(LOG))
        self.assertEqual([e["id"] for e in review], ["D-3", "D-2", "D-4"])

    def test_a_later_answer_with_the_same_title_supersedes(self):
        text = LOG + "\n### D-5 Currency of the totals\n- status: answered\n- answer: the customer's\n- source: human\n- request: checkout-cart\n"
        self.assertNotIn("D-2", [e["id"] for e in to_review(parse_decisions(text))])

    def test_a_later_answer_naming_the_entry_supersedes(self):
        text = LOG + "\n### D-5 Rounding, settled\n- status: answered\n- answer: half even\n- source: human; supersedes D-3\n- request: checkout-cart\n"
        review = [e["id"] for e in to_review(parse_decisions(text))]
        self.assertNotIn("D-3", review)
        self.assertIn("D-2", review)

    def test_naming_d_3_does_not_supersede_d_30(self):
        text = "### D-30 Thirty\n- status: answered-by-delegate\n\n### D-31 Later\n- status: answered\n- source: human; supersedes D-3\n"
        self.assertEqual([e["id"] for e in to_review(parse_decisions(text))], ["D-30"])


class FileTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, text: str) -> None:
        path = self.root / "docs" / "business" / "decisions.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_missing_log_gives_nothing(self):
        self.assertEqual(decisions_for(self.root, "checkout-cart"), [])
        self.assertEqual(decision_counts(self.root, "checkout-cart"), {"pending": 0, "unread": 0})

    def test_decisions_are_filtered_by_run(self):
        self.write(LOG)
        self.assertEqual([e["id"] for e in decisions_for(self.root, "checkout-cart")], ["D-3", "D-2"])
        self.assertEqual([e["id"] for e in decisions_for(self.root, None)], ["D-3", "D-2", "D-4"])
        self.assertEqual(decisions_for(self.root, "nope"), [])

    def test_counts_split_pending_and_unread(self):
        self.write(LOG)
        self.assertEqual(decision_counts(self.root, "checkout-cart"), {"pending": 1, "unread": 1})

    def test_a_changed_log_is_read_again(self):
        self.write(LOG)
        self.assertEqual(decision_counts(self.root, "checkout-cart")["unread"], 1)
        self.write(LOG + "\n### D-9 Another\n- status: answered-by-delegate\n- request: checkout-cart\n")
        self.assertEqual(decision_counts(self.root, "checkout-cart")["unread"], 2)


if __name__ == "__main__":
    unittest.main()
