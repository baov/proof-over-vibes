import os
import tempfile
import unittest
from pathlib import Path

from floor.docs import list_docs, read_doc


def put(root: Path, rel: str, text: str, mtime: float) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    os.utime(path, (mtime, mtime))


class DocsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_lists_docs_and_audit_newest_first_with_their_title(self):
        put(self.root, "docs/product/framing.md", "# Framing\n\nbody", 100)
        put(self.root, ".audit/app-2026-01-01.md", "---\nrole: x\n---\n# Cold audit\n", 200)
        put(self.root, "docs/notes.txt", "not markdown", 300)
        put(self.root, "README.md", "# Outside the folders", 400)
        listed = list_docs(self.root)
        self.assertEqual([d["path"] for d in listed], [".audit/app-2026-01-01.md", "docs/product/framing.md"])
        self.assertEqual([d["title"] for d in listed], ["Cold audit", "Framing"])

    def test_title_falls_back_to_the_file_name(self):
        put(self.root, "docs/plain.md", "no heading", 100)
        self.assertEqual(list_docs(self.root)[0]["title"], "plain")

    def test_reads_a_listed_document(self):
        put(self.root, "docs/product/framing.md", "# Framing\n\nbody", 100)
        doc = read_doc(self.root, "docs/product/framing.md")
        self.assertEqual(doc["title"], "Framing")
        self.assertIn("body", doc["body"])

    def test_refuses_what_is_not_listed(self):
        put(self.root, "README.md", "# Secret", 100)
        put(self.root, "docs/a.md", "# A", 100)
        for rel in ("README.md", "../README.md", "docs/../README.md", "docs/missing.md", ""):
            self.assertIsNone(read_doc(self.root, rel), rel)

    def test_a_link_leaving_the_root_is_not_listed(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        put(Path(outside.name), "secret.md", "# Secret", 100)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "leak.md").symlink_to(Path(outside.name) / "secret.md")
        self.assertEqual(list_docs(self.root), [])
        self.assertIsNone(read_doc(self.root, "docs/leak.md"))
