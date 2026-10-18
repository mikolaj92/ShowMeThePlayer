import json
import unittest
from pathlib import Path
from unittest.mock import patch

from splot import fuse_json

from showmetheplayer import (
    CameraMetric,
    build_switch_command,
    decide_from_payload,
    metric_to_candidate,
    run_director,
)

ROOT = Path(__file__).resolve().parents[1]


class DirectorTests(unittest.TestCase):
    def test_metric_to_candidate_keeps_profile_fields(self):
        candidate = metric_to_candidate(
            CameraMetric(
                camera_id="camera_1",
                player_visible=True,
                visibility=0.8,
                occlusion=0.1,
                sharpness=0.7,
                face_angle=0.6,
            )
        )

        self.assertEqual(candidate["id"], "camera_1")
        self.assertEqual(
            candidate["payload"],
            {
                "player_visible": True,
                "visibility": 0.8,
                "occlusion": 0.1,
                "sharpness": 0.7,
                "face_angle": 0.6,
                "available": True,
            },
        )
        self.assertNotIn("tracking_confidence", candidate["payload"])
        self.assertNotIn("latency", candidate["payload"])
        self.assertNotIn("latency_ms", candidate["metadata"])

    def test_from_dict_requires_only_camera_id(self):
        metric = CameraMetric.from_dict({"camera_id": "camera_1"})

        self.assertEqual(metric.camera_id, "camera_1")
        self.assertFalse(metric.player_visible)
        self.assertEqual(metric.visibility, 0.0)
        self.assertEqual(metric.occlusion, 1.0)
        self.assertEqual(metric.sharpness, 0.0)
        self.assertEqual(metric.face_angle, 0.0)
        self.assertTrue(metric.available)
        self.assertIsNone(metric.observed_at)

    def test_from_dict_raises_without_camera_id(self):
        with self.assertRaises(KeyError):
            CameraMetric.from_dict({"player_visible": True})

    def test_from_dict_ignores_unscored_leftover_fields(self):
        candidate = metric_to_candidate(
            CameraMetric.from_dict(
                {
                    "camera_id": "camera_1",
                    "player_visible": True,
                    "visibility": 0.8,
                    "occlusion": 0.1,
                    "sharpness": 0.7,
                    "face_angle": 0.6,
                    "available": True,
                    "tracking_confidence": 0.9,
                    "latency_ms": 250,
                }
            )
        )

        self.assertNotIn("tracking_confidence", candidate["payload"])
        self.assertNotIn("latency", candidate["payload"])
        self.assertNotIn("latency_ms", candidate["metadata"])

    def test_metric_to_candidate_zeros_visibility_when_player_hidden(self):
        candidate = metric_to_candidate(
            CameraMetric(
                camera_id="camera_2",
                player_visible=False,
                visibility=1.0,
                occlusion=0.0,
                sharpness=1.0,
                face_angle=1.0,
            )
        )

        self.assertEqual(candidate["payload"]["visibility"], 0.0)

    def test_run_director_selects_best_visible_live_camera(self):
        payload = json.loads((ROOT / "examples/metrics/round_1.json").read_text(encoding="utf-8"))
        payload["cameras"][1]["player_visible"] = False
        payload["state"]["previous_decision"].update(
            selected_candidate_id="camera_2", selected_candidate_ids=["camera_2"],
            action={"type": "select", "candidate_id": "camera_2"},
        )
        with patch("showmetheplayer.director.fuse_json", wraps=fuse_json) as fuse:
            result = decide_from_payload(payload)
            fuse.assert_called_once()
            self.assertEqual(fuse.call_args.args[0]["state"], payload["state"])
            self.assertEqual(fuse.call_args.args[0]["now"], payload["now"])

            for function, argument in ((decide_from_payload, {}), (decide_from_payload, {"cameras": []}), (run_director, [])):
                with self.subTest(function=function.__name__, argument=argument):
                    with self.assertRaisesRegex(ValueError, r"\Aat least one camera metric is required\Z"):
                        function(argument)
                    fuse.assert_called_once()
        switch = build_switch_command(result)

        self.assertEqual(result["decision"]["selected_candidate_id"], "camera_3")
        self.assertEqual(switch["action"], "switch")
        evaluations = result["evaluations"]
        self.assertTrue(
            any(item["candidate_id"] == "camera_2" and not item.get("eligible", True) for item in evaluations)
        )

    def test_quick_start_payload_keeps_camera_1_without_previous_decision_switches_camera_3(self):
        payload = json.loads((ROOT / "examples/metrics/round_1.json").read_text(encoding="utf-8"))

        for previous, camera in ((True, "camera_1"), (False, "camera_3")):
            with self.subTest(previous_decision=previous):
                if not previous:
                    del payload["state"]["previous_decision"]
                result = decide_from_payload(payload)
                switch = build_switch_command(result)
                self.assertEqual(result["decision"]["selected_candidate_id"], camera)
                self.assertEqual(switch["camera_id"], camera)
                self.assertEqual(switch["action"], "switch")
                self.assertEqual(switch["status"], "selected")


if __name__ == "__main__":
    unittest.main()
