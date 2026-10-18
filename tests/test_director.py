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
        payload = {
            "now": "2026-06-28T12:00:04+00:00",
            "state": {
                "session_id": "session_director",
                "objective_id": "best_player_view",
                "last_decision_at": "2026-06-28T11:59:00+00:00",
                "last_switch_at": "2026-06-28T11:59:00+00:00",
                "previous_decision": {
                    "id": "decision_previous_camera",
                    "status": "selected",
                    "objective_id": "best_player_view",
                    "selected_candidate_id": "camera_2",
                    "selected_candidate_ids": ["camera_2"],
                    "confidence": 1.0,
                    "action": {"type": "select", "candidate_id": "camera_2"},
                },
            },
            "cameras": [
                {"camera_id": "camera_1", "player_visible": True, "visibility": 0.6,
                 "occlusion": 0.2, "sharpness": 0.7, "face_angle": 0.6},
                {"camera_id": "camera_2", "player_visible": False, "visibility": 1.0,
                 "occlusion": 0.0, "sharpness": 1.0, "face_angle": 1.0},
                {"camera_id": "camera_3", "player_visible": True, "visibility": 0.9,
                 "occlusion": 0.1, "sharpness": 0.8, "face_angle": 0.8},
            ],
        }
        with patch("showmetheplayer.director.fuse_json", wraps=fuse_json) as fuse:
            result = decide_from_payload(payload)
            fuse.assert_called_once()
            request = fuse.call_args.args[0]
            self.assertEqual(request["state"], payload["state"])
            self.assertEqual(request["now"], payload["now"])

            for invalid in ({}, {"cameras": []}):
                with self.subTest(payload=invalid):
                    with self.assertRaisesRegex(
                        ValueError, r"\Aat least one camera metric is required\Z"
                    ):
                        decide_from_payload(invalid)
                    fuse.assert_called_once()
            with self.subTest(metrics=[]):
                with self.assertRaisesRegex(
                    ValueError, r"\Aat least one camera metric is required\Z"
                ):
                    run_director([])
                fuse.assert_called_once()
        switch = build_switch_command(result)

        self.assertEqual(result["decision"]["selected_candidate_id"], "camera_3")
        self.assertEqual(switch["action"], "switch")
        self.assertEqual(switch["camera_id"], "camera_3")
        evaluations = result["evaluations"]
        self.assertTrue(
            any(item["candidate_id"] == "camera_2" and not item.get("eligible", True) for item in evaluations)
        )

    def test_quick_start_payload_keeps_camera_1_without_previous_decision_switches_camera_3(self):
        payload = json.loads((ROOT / "examples/metrics/round_1.json").read_text(encoding="utf-8"))

        with_state = decide_from_payload(payload)
        with_state_switch = build_switch_command(with_state)
        self.assertEqual(with_state["decision"]["selected_candidate_id"], "camera_1")
        self.assertEqual(with_state_switch["camera_id"], "camera_1")
        self.assertEqual(with_state_switch["action"], "switch")
        self.assertEqual(with_state_switch["status"], "selected")

        without_previous = {
            "now": payload["now"],
            "state": {
                "session_id": payload["state"]["session_id"],
                "objective_id": payload["state"]["objective_id"],
            },
            "cameras": payload["cameras"],
        }
        without_state = decide_from_payload(without_previous)
        without_state_switch = build_switch_command(without_state)
        self.assertEqual(without_state["decision"]["selected_candidate_id"], "camera_3")
        self.assertEqual(without_state_switch["action"], "switch")
        self.assertEqual(without_state_switch["camera_id"], "camera_3")
        self.assertEqual(without_state_switch["status"], "selected")


if __name__ == "__main__":
    unittest.main()
