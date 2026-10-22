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

`switch` describes the mapped status, not a comparison with the current camera.
Only `kept_previous` with a camera ID produces `keep`. If all cameras are
unavailable or below the visibility threshold, the packed profile returns
`fallback` and the host emits `action=fallback` instead; see
[Metrics](METRICS.md).

Real adapters can map this to OBS, vMix, ATEM, FFmpeg, or another router.
