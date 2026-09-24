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

The first switcher is deliberately a dry-run JSON command. Which camera it
names depends on whether the payload already has a current camera.

Quick Start uses `examples/metrics/round_1.json`. That file sets
`state.previous_decision.selected_candidate_id` to `camera_1`. Packed
hysteresis is `min_improvement = 0.15` with `close_margin = 0.05`; camera_3's
score margin over the current camera is too small, so Splot keeps
`camera_1` (`tie_breaker_keep_current`). The host maps Splot
`status=selected` to `action=switch` (`kept_previous` would map to `keep`):

```json
{
  "action": "switch",
  "camera_id": "camera_1",
  "status": "selected"
}
```

The same cameras without `previous_decision` have no current camera to keep.
Because at least one camera in this example is eligible, Splot selects the
highest eligible score and the host emits a real switch to `camera_3`:

```json
{
  "action": "switch",
  "camera_id": "camera_3",
  "status": "selected"
}
```

This stateless example does not guarantee a switch for every payload. If all
cameras are unavailable or below the visibility threshold, the packed profile
returns `fallback` and the host emits `action=fallback` instead; see
[Metrics](METRICS.md).

Real adapters can map this to OBS, vMix, ATEM, FFmpeg, or another router.
