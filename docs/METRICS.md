# Metrics

The input file has:

- `now`: ISO timestamp
- `state`: optional previous Splot state
- `cameras`: list of camera metrics

Required per camera:

- `camera_id`
- `player_visible`
- `visibility`
- `occlusion`
- `sharpness`
- `face_angle`
- `available`

Scores should already be normalized to `0..1`. The adapter zeros `visibility`
when `player_visible` is false. The packed Splot profile scores `visibility`,
`face_angle`, `sharpness`, and `occlusion`, plus a keep-current bonus, and
gates on `available` and a minimum visibility of `0.60`.
