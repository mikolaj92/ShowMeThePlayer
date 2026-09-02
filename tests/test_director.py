import unittest

from showmetheplayer import (
    CameraMetric,
    build_switch_command,
    metric_to_candidate,
    run_director,
)


class DirectorTests(unittest.TestCase):
    def test_metric_to_candidate_normalizes_latency(self):
        candidate = metric_to_candidate(
            CameraMetric(
                camera_id="camera_1",
                player_visible=True,
                visibility=0.8,
                tracking_confidence=0.9,
                occlusion=0.1,
                sharpness=0.7,
                face_angle=0.6,
                latency_ms=250,
            )
        )

        self.assertEqual(candidate["id"], "camera_1")
        self.assertEqual(candidate["payload"]["latency"], 0.25)
        self.assertTrue(candidate["payload"]["player_visible"])

    def test_run_director_selects_best_visible_live_camera(self):
        result = run_director(
            [
                CameraMetric("camera_1", True, 0.6, 0.6, 0.2, 0.7, 0.6, 150),
                CameraMetric("camera_2", False, 1.0, 1.0, 0.0, 1.0, 1.0, 150),
                CameraMetric("camera_3", True, 0.9, 0.9, 0.1, 0.8, 0.8, 180),
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
