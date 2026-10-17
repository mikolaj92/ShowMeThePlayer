# Metrics

The input file has:

- `now`: ISO timestamp
- `state`: optional previous Splot state; an existing CLI `--state` file replaces it
- `cameras`: list of camera metrics

`cameras` must be nonempty; a missing or empty list raises `ValueError` with the message `at least one camera metric is required`.

Without `--state`, or if its file does not exist, the input's `state` is used.
An existing file replaces that state entirely, including when it contains `{}`.
After successful decision processing, the specified file receives the new state,
or `{}` if Splot returns no state. Without the flag, no separate state file is
written. See [CLI flags](../README.md#cli-flags) for the full CLI reference.

When `state.previous_decision` names a live camera, Splot may keep it
(hysteresis / keep-current). Without that field, when at least one camera is
eligible, the director selects the highest eligible score and the host emits
`action: switch`. If all cameras are unavailable or below the visibility
threshold, the packed profile uses `when_constraints_block_all = "fallback"`,
and the host emits `action: fallback` instead. This also applies when cameras
supply only the required `camera_id`, since their visibility defaults to zero.

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

`player_visible` and `available` accept only JSON booleans (`true` or `false`).
Other values, including strings, numbers, and `null`, raise `TypeError` naming
the field. Missing flags default to `player_visible=false` and `available=true`.

A camera that only has `camera_id` is therefore treated as live
(`available=true`) with no player in view and full occlusion.

Scores should already be normalized to `0..1`. The host forwards `player_visible`
in the candidate payload, but the packed profile does not check that flag directly.
Candidate `visibility` equals the input value when `player_visible=true`;
when `player_visible=false`, the host sends `0.0` instead.

The packed Splot profile scores `visibility`, `face_angle`, `sharpness`, and
`occlusion`, plus a keep-current bonus, and gates on `available` and the independent
constraint `player_must_be_visible`: candidate `visibility >= 0.60`.
Thus `true/0.50` fails this threshold, `false/1.00` becomes `0.0` and fails,
and `true/0.60` passes this threshold alone. The flag being true is not sufficient.
