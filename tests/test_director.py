import unittest

from showmetheplayer import (
    CameraMetric,
    build_switch_command,
    metric_to_candidate,
    run_director,
)


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
        result = run_director(
            [
                CameraMetric("camera_1", True, 0.6, 0.2, 0.7, 0.6),
                CameraMetric("camera_2", False, 1.0, 0.0, 1.0, 1.0),
                CameraMetric("camera_3", True, 0.9, 0.1, 0.8, 0.8),
            ],
            now="2026-06-28T12:00:04+00:00",
        )
        switch = build_switch_command(result)

        self.assertEqual(result["decision"]["selected_candidate_id"], "camera_3")
        self.assertEqual(switch["action"], "switch")
        evaluations = result["evaluations"]
        self.assertTrue(
            any(item["candidate_id"] == "camera_2" and not item.get("eligible", True) for item in evaluations)
        )


if __name__ == "__main__":
    unittest.main()
