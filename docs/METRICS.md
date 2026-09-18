# Metrics

The input file has:

- `now`: ISO timestamp
- `state`: optional previous Splot state
- `cameras`: list of camera metrics

When `state.previous_decision` names a live camera, Splot may keep it
(hysteresis / keep-current). Without that field the director selects the
highest eligible score and the host emits `action: switch`.

Required per camera:

- `camera_id`

`CameraMetric.from_dict` raises `KeyError` only when `camera_id` is missing.
Every other camera field is optional and filled with a silent default:

- `player_visible`: `false`
- `visibility`: `0`
- `occlusion`: `1`
- `sharpness`: `0`
- `face_angle`: `0`
- `available`: `true`
- `observed_at`: `null`

A camera that only has `camera_id` is therefore treated as live
(`available=true`) with no player in view and full occlusion.

Scores should already be normalized to `0..1`. The adapter zeros `visibility`
when `player_visible` is false. The packed Splot profile scores `visibility`,
`face_angle`, `sharpness`, and `occlusion`, plus a keep-current bonus, and
gates on `available` and a minimum visibility of `0.60`.
