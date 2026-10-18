# Metrics

The input file has:

- `now`: optional ISO timestamp
- `state`: optional previous Splot state; an existing CLI `--state` file replaces it
- `cameras`: required nonempty list of camera metrics

Missing or empty `cameras` raises `ValueError("at least one camera metric is required")`.

See [CLI flags](../README.md#cli-flags) for state-file replacement and output behavior.

When `state.previous_decision` names a live camera, Splot may keep it
(hysteresis / keep-current). Without that field, when at least one camera is
eligible, the director selects the highest eligible score and the host emits
`action: switch`. If all cameras are unavailable or below the visibility
threshold, the packed profile uses `when_constraints_block_all = "fallback"`,
and the host emits `action: fallback` instead. This also applies when cameras
supply only the required `camera_id`, since their visibility defaults to zero.

Each camera requires `camera_id`; omitting it raises `KeyError`.
Other fields default to:

- `player_visible`: `false`
- `visibility`: `0`
- `occlusion`: `1`
- `sharpness`: `0`
- `face_angle`: `0`
- `available`: `true`
- `observed_at`: `null`

`player_visible` and `available` accept only JSON booleans (`true` or `false`).
Other values, including strings, numbers, and `null`, raise `TypeError` naming
the field.

A camera that only has `camera_id` is therefore treated as live
(`available=true`) with no player in view and full occlusion.

The host clamps scores to `0..1` and forwards `player_visible`
in the candidate payload, but the packed profile does not check that flag directly.
Candidate `visibility` equals the input value when `player_visible=true`;
when `player_visible=false`, the host sends `0.0` instead.

The packed Splot profile scores `visibility`, `face_angle`, `sharpness`, and
`occlusion`, plus a keep-current bonus, and gates on `available` and the independent
constraint `player_must_be_visible`: candidate `visibility >= 0.60`.
Thus `true/0.50` fails this threshold, `false/1.00` becomes `0.0` and fails,
and `true/0.60` passes this threshold alone. The flag being true is not sufficient.
