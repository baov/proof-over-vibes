"""Self-tests of the harness scripts: python3 -m unittest discover -s tools/harness/selftest"""
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

H = Path(__file__).resolve().parent.parent


def project(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp())
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body))
    return root


def run(script: str, root: Path, *extra: str):
    r = subprocess.run([sys.executable, str(H / script), "--root", str(root), *extra],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


SRC = "src/copro_parking/"


class LayerTests(unittest.TestCase):
    def test_clean_project_passes(self):
        root = project({SRC + "domain/lot.py": "import dataclasses\nfrom enum import Enum\n",
                        SRC + "application/uc.py": "from copro_parking.domain import lot\nimport abc\n",
                        SRC + "infrastructure/repo.py": "import json, os\nfrom copro_parking.application import uc\n"})
        self.assertEqual(run("check_layers.py", root)[0], 0)

    def test_domain_io_and_outward_imports_flagged(self):
        root = project({SRC + "domain/a.py": "import json\nfrom copro_parking.infrastructure import repo\n"
                                              "def f():\n    import os\n",
                        SRC + "domain/b.py": "from ..application import uc\nfrom . import a\n",
                        SRC + "domain/c.py": "import requests\n"})
        code, out = run("check_layers.py", root)
        self.assertEqual(code, 2)
        self.assertIn("domain/a.py:1:", out)
        self.assertIn("domain/a.py:2:", out)
        self.assertIn("domain/a.py:4:", out)  # import inside a function
        self.assertIn("domain/b.py:1:", out)  # relative import resolved
        self.assertNotIn("domain/b.py:2:", out)
        self.assertIn("domain/c.py:1:", out)

    def test_application_must_not_import_infrastructure(self):
        root = project({SRC + "application/uc.py": "from copro_parking import infrastructure\n"})
        self.assertIn("application/uc.py:1:", run("check_layers.py", root)[1])

    def test_tests_and_infrastructure_unrestricted(self):
        root = project({"tests/test_x.py": "import json\nfrom copro_parking.infrastructure import r\n",
                        SRC + "infrastructure/r.py": "import json\nfrom copro_parking.domain import lot\n"})
        self.assertEqual(run("check_layers.py", root)[0], 0)

    def test_no_code_is_ok(self):
        self.assertEqual(run("check_layers.py", project({}))[0], 0)


class ShapeTests(unittest.TestCase):
    def test_flags_each_metric(self):
        body = "def f(a, b, c, d, e, g):\n" + "    if a:\n" * 1 + "".join(
            "        " * i + f"if b{i}:\n" for i in range(1, 1)) + "        pass\n"
        deep = "def deep(x):\n    if x:\n        for i in x:\n            while i:\n                if i:\n                    with i:\n                        pass\n"
        cx = "def cx(x):\n" + "".join(f"    if x == {i}:\n        return {i}\n" for i in range(11))
        long = "def long(x):\n" + "    x = 1\n" * 45
        root = project({"src/m.py": body + deep + cx + long})
        code, out = run("check_shape.py", root)
        self.assertEqual(code, 2)
        for inv in ("INV-003", "INV-004", "INV-005", "INV-006"):
            self.assertIn(inv, out)

    def test_small_function_and_self_ok(self):
        root = project({"src/m.py": "class A:\n    def f(self, a, b, c, d, e):\n        return a\n"})
        self.assertEqual(run("check_shape.py", root)[0], 0)


class MutationTests(unittest.TestCase):
    PROJ = {SRC + "__init__.py": "", SRC + "domain/__init__.py": "",
            SRC + "domain/rule.py": "def is_manager(role):\n    return role == 'manager'\n"}

    def test_weak_suite_leaves_survivors(self):
        weak = dict(self.PROJ, **{"tests/test_r.py": (
            "import unittest\nfrom copro_parking.domain.rule import is_manager\n"
            "class T(unittest.TestCase):\n    def test_manager(self):\n"
            "        is_manager('manager')\n")})  # asserts nothing
        code, out = run("run_mutation.py", project(weak))
        self.assertEqual(code, 0)
        self.assertIn("mutant survived", out)

    def test_strong_suite_kills_all_and_threshold_warns(self):
        strong = dict(self.PROJ, **{"tests/test_r.py": (
            "import unittest\nfrom copro_parking.domain.rule import is_manager\n"
            "class T(unittest.TestCase):\n    def test_manager(self):\n"
            "        self.assertTrue(is_manager('manager'))\n"
            "        self.assertFalse(is_manager('tenant'))\n")})
        code, out = run("run_mutation.py", project(strong), "--threshold", "100")
        self.assertEqual(code, 0)
        self.assertNotIn("mutant survived", out)

    def test_red_baseline_refused(self):
        red = dict(self.PROJ, **{"tests/test_r.py": (
            "import unittest\nclass T(unittest.TestCase):\n    def test_x(self):\n        self.fail()\n")})
        self.assertEqual(run("run_mutation.py", project(red))[0], 1)


if __name__ == "__main__":
    unittest.main()
