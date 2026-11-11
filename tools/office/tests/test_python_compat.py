import unittest
from pathlib import Path

OFFICE = Path(__file__).resolve().parents[1]


class PythonCompatTest(unittest.TestCase):
    def test_modules_defer_annotations_for_older_python(self):
        # `X | None` in an annotation crashes at import before Python 3.10 unless deferred.
        for path in [*sorted((OFFICE / "floor").glob("*.py")), OFFICE / "serve.py"]:
            if path.name == "__init__.py":
                continue
            with self.subTest(module=path.name):
                self.assertIn("from __future__ import annotations", path.read_text())


if __name__ == "__main__":
    unittest.main()
