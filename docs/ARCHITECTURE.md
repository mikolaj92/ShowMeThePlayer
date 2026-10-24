# Architecture

ShowMeThePlayer is a host around Splot.

```text
metrics JSON
  -> showmetheplayer.director.metrics_to_candidates
  -> splot.fuse_json
  -> decision report
  -> switch command
```

Splot is the generic arbiter; `profile.toml` is a demo policy, not a pitch specification.
`best_player_view` and the `camera_*` waves describe fixtures, not pitch roles or placement.
`CameraMetric` and the adapter zero visibility for hidden players; Splot applies
the minimum-visibility gate. A domain-specific profile is a separate change.

The first switcher is a dry-run JSON command, not proof of a camera change.
Quick Start runs with fresh output paths, so no saved state overrides the input:

```bash
demo_dir=$(mktemp -d ./quick-start.XXXXXX)
uv run showmetheplayer decide \
  --input examples/metrics/round_1.json \
  --out "$demo_dir/decision_report.json" \
  --state "$demo_dir/state.json" \
  --switch-out "$demo_dir/switch_command.json"
```

`examples/metrics/round_1.json` sets
`state.previous_decision.selected_candidate_id` to `camera_1`. Packed
hysteresis is `min_improvement = 0.15` with `close_margin = 0.05`; camera_3's
score margin over the current camera is too small, so Splot keeps
`camera_1` (`tie_breaker_keep_current`). The verified output is
`switch camera=camera_1 status=selected confidence=0.796`. The host maps
`status=selected` to `action=switch` even though the camera stays the same:

```json
{
  "action": "switch",
  "camera_id": "camera_1",
  "decision_id": "decision_mojo",
  "status": "selected",
  "confidence": 0.7959999999999998,
  "reason": "tie_breaker_keep_current"
}
```

With an existing `--state` file containing `{}`, input state is replaced;
at least one camera in this example is eligible, so the stateless result is:

```json
{
  "action": "switch",
  "camera_id": "camera_3",
  "decision_id": "decision_mojo",
  "status": "selected",
  "confidence": 0.8179999999999998,
  "reason": "constrained_weighted_score_selected_highest_score"
}
```

`build_switch_command` requires a dictionary at `result["decision"]`; a missing,
null, or non-dictionary value raises `TypeError`. A truthy
`selected_candidate_id` maps `kept_previous` to `keep`, and `selected` or `routed`
to `switch`, without comparing cameras. `fallback` maps to `action=fallback`
with or without an ID; other cases produce `wait`.

From the report's `decision`, `camera_id` comes from `selected_candidate_id`,
`decision_id` from `id`, and `reason` from `policy_reason`; each may be `null`.
`confidence` is converted to a number with `float(value or 0)`, defaulting to
`0.0` when missing, null, or empty. `status` is converted to text with
`str(value or "")`, defaulting to `""` when missing, null, or empty. The statuses
above are not a closed list.

If all cameras are unavailable or below the visibility threshold, the profile
returns `fallback`; see [Metrics](METRICS.md). Adapters can send commands to
OBS, vMix, ATEM, FFmpeg, or another router.
