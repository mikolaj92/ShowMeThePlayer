import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_decide_writes_report_state_and_switch_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "decision_report.json"
            state = Path(tmp) / "state.json"
            switch = Path(tmp) / "switch_command.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "showmetheplayer.cli",
                    "decide",
                    "--input",
                    "examples/metrics/round_1.json",
                    "--out",
                    str(report),
                    "--state",
                    str(state),
                    "--switch-out",
                    str(switch),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("camera=", result.stdout)
            self.assertEqual(json.loads(report.read_text())["profile_id"], "show_me_the_player_director")
            self.assertIn(json.loads(switch.read_text())["action"], {"keep", "switch", "wait", "fallback"})
            self.assertTrue(state.exists())


if __name__ == "__main__":
    unittest.main()
