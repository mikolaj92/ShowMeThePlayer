# Metrics

The input file has:

- `now`: ISO timestamp
- `state`: optional previous Splot state
- `cameras`: list of camera metrics

Required per camera:

- `camera_id`
- `player_visible`
- `visibility`
- `tracking_confidence`
- `occlusion`
- `sharpness`
- `face_angle`
- `latency_ms`
- `available`

Scores should already be normalized to `0..1`, except `latency_ms`. The adapter
normalizes latency as `min(latency_ms / 1000, 1)`, and the Splot profile prefers
lower latency.
