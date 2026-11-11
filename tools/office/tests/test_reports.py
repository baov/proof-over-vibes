import unittest

from floor.reports import parse_brief, parse_front_matter, split_front_matter


class FrontMatterTest(unittest.TestCase):
    def test_front_matter_reads_keys(self):
        text = "---\nrole: reviewer\nstatus: done\nverdict: NO-GO\nreasons: []\n---\nbody"
        self.assertEqual(
            parse_front_matter(text),
            {"role": "reviewer", "status": "done", "verdict": "NO-GO", "reasons": "[]"},
        )

    def test_missing_front_matter_is_empty(self):
        self.assertEqual(parse_front_matter("just prose"), {})

    def test_unclosed_front_matter_is_empty(self):
        self.assertEqual(parse_front_matter("---\nrole: reviewer\n"), {})


class SplitTest(unittest.TestCase):
    def test_split_returns_front_matter_and_body(self):
        front, body = split_front_matter("---\nstatus: done\n---\nHello\nworld")
        self.assertEqual(front, {"status": "done"})
        self.assertEqual(body, "Hello\nworld")

    def test_split_without_front_matter_keeps_all_text_as_body(self):
        self.assertEqual(split_front_matter("---\nrole: pla"), ({}, "---\nrole: pla"))


class BriefTest(unittest.TestCase):
    def test_brief_reads_counter_and_limit(self):
        self.assertEqual(parse_brief("Iteration counter: 2\nIteration limit: 5"), (2, 5))
        self.assertEqual(parse_brief("- Iterations: 1 (limit 3)"), (1, 3))

    def test_brief_defaults(self):
        self.assertEqual(parse_brief("nothing here"), (0, 5))


if __name__ == "__main__":
    unittest.main()
