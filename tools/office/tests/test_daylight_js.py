import shutil
import subprocess
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class DaylightJsTest(unittest.TestCase):
    def test_daylight_logic_passes_its_node_tests(self):
        result = subprocess.run(
            ["node", "--test", str(TESTS / "daylight.test.mjs")],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
