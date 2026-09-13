import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_quick_start_example_matches_packed_profile(self):
        example = json.loads((ROOT / "examples/metrics/round_1.json").read_text())
        profile = tomllib.loads(
            (ROOT / "src/showmetheplayer/profiles/player-director/profile.toml").read_text()
        )
        objective_id = profile["objective"]["id"]

        self.assertEqual(
            [camera["camera_id"] for camera in example["cameras"]],
            [wave["id"] for wave in profile["waves"]],
        )
        self.assertEqual(example["state"]["objective_id"], objective_id)
        self.assertEqual(
            example["state"]["previous_decision"]["objective_id"], objective_id
        )

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
            decision = json.loads(report.read_text())["decision"]
            self.assertEqual(decision["objective_id"], "best_player_view")
            self.assertIn(json.loads(switch.read_text())["action"], {"keep", "switch", "wait", "fallback"})
            self.assertTrue(state.exists())


if __name__ == "__main__":
    unittest.main()
