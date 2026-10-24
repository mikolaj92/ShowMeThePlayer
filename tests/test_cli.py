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
        self.assertEqual(
            example["state"]["previous_decision"]["selected_candidate_id"],
            "camera_1",
        )

    def test_docs_show_stateful_keep_and_stateless_switch(self):
        architecture = (ROOT / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
        metrics = (ROOT / "docs/METRICS.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        stateful = (
            "{\n"
            '  "action": "switch",\n'
            '  "camera_id": "camera_1",\n'
            '  "decision_id": "decision_mojo",\n'
            '  "status": "selected",\n'
            '  "confidence": 0.7959999999999998,\n'
            '  "reason": "tie_breaker_keep_current"\n'
            "}"
        )
        stateless = (
            "{\n"
            '  "action": "switch",\n'
            '  "camera_id": "camera_3",\n'
            '  "decision_id": "decision_mojo",\n'
            '  "status": "selected",\n'
            '  "confidence": 0.8179999999999998,\n'
            '  "reason": "constrained_weighted_score_selected_highest_score"\n'
            "}"
        )

        self.assertIn(stateful, architecture)
        self.assertIn(stateless, architecture)
        self.assertIn("previous_decision", architecture)
        self.assertIn("min_improvement", architecture)
        self.assertIn("at least one camera in this example is eligible", architecture)
        self.assertIn("action=fallback", architecture)
        self.assertIn("at least one camera is", metrics)
        self.assertIn("action: fallback", metrics)
        self.assertIn("previous_decision", readme)
        self.assertIn("camera_1", readme)
        self.assertIn("camera_3", readme)

    def test_decide_writes_report_state_and_switch_command(self):
        for initial_state, camera in ((None, "camera_1"), ("{}", "camera_3")):
            with self.subTest(initial_state=initial_state), tempfile.TemporaryDirectory() as tmp:
                report = Path(tmp) / "decision_report.json"
                state = Path(tmp) / "state.json"
                switch = Path(tmp) / "switch_command.json"
                if initial_state is not None:
                    state.write_text(initial_state)
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "showmetheplayer.cli",
                        "decide",
                        "--input",
                        "examples/metrics/round_1.json",
                        "--out", str(report),
                        "--state", str(state),
                        "--switch-out", str(switch),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"switch camera={camera} status=selected", result.stdout)
                decision = json.loads(report.read_text())["decision"]
                self.assertEqual(decision["objective_id"], "best_player_view")
                self.assertEqual(tuple(json.loads(switch.read_text())[key] for key in ("action", "camera_id")), ("switch", camera))
                self.assertTrue(state.exists())


if __name__ == "__main__":
    unittest.main()
