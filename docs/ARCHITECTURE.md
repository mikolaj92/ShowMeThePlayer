# Architecture

ShowMeThePlayer is a host around Splot.

```text
metrics JSON
  -> showmetheplayer.director.metrics_to_candidates
  -> splot.fuse_json
  -> decision report
  -> switch command
```

Splot remains the generic arbiter. The packaged `profile.toml` is currently a
generic/demo policy, not a football-pitch profile: its Polish language, generic
`best_player_view` description, and three `camera_*` waves describe the fixture
shape rather than pitch roles or camera placement. The football-specific input
contract currently appears in `CameraMetric` and
the `metric-to-candidate` adapter: they accept player-visibility metrics and zero
the visibility score when the player is hidden before passing candidates to
Splot, whose profile constraint applies the minimum-visibility gate.

Do not treat this profile as the ShowMeThePlayer domain specification. Moving
those football assumptions into a domain-specific profile is a separate change;
this host currently documents the boundary rather than implementing that
profile.

Quick Start uses `examples/metrics/round_1.json` and creates a fresh directory
with `output_dir=$(mktemp -d ./.quick-start.XXXXXX)`. Its
`--state "$output_dir/state.json"` file does not exist, preserving the input's
`state.previous_decision.selected_candidate_id` of `camera_1`. Packed hysteresis
(`min_improvement = 0.15`, `close_margin = 0.05`) retains `camera_1` with reason
`tie_breaker_keep_current`. The expected `$output_dir/switch_command.json`
below has `action=switch` because `status=selected` maps to `switch` with a
camera ID; this command does not necessarily mean the camera changed:

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

`build_switch_command` requires a dictionary at `result["decision"]`; a missing,
null, or non-dictionary value raises `TypeError`. A truthy
`selected_candidate_id` is required for `keep` (`kept_previous`) and `switch`
(`selected` or `routed`); otherwise, these statuses produce `wait`. `fallback`
produces `fallback` with or without an identifier; all other statuses produce
`wait`.

From the report's `decision`, `camera_id` comes from `selected_candidate_id`,
`decision_id` from `id`, and `reason` from `policy_reason`; each may be `null`.
`confidence` is converted to a number with `float(value or 0)`, defaulting to
`0.0` when missing, null, or empty. `status` is converted to text with
`str(value or "")`, defaulting to `""` when missing, null, or empty. The statuses
above are not a closed list.

The same cameras without `previous_decision` have no current camera to keep.
Because at least one camera in this example is eligible, Splot selects the
highest eligible score and the host emits a dry-run switch to `camera_3`:

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

This stateless example does not guarantee a switch for every payload. If all
cameras are unavailable or below the visibility threshold, the packed profile
returns `fallback` and the host emits `action=fallback` instead; see
[Metrics](METRICS.md).

Real adapters can map this to OBS, vMix, ATEM, FFmpeg, or another router.
