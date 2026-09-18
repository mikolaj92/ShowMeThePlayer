# Architecture

ShowMeThePlayer is a host around Splot.

```text
metrics JSON
  -> showmetheplayer.director.metrics_to_candidates
  -> splot.fuse_json
  -> decision report
  -> switch command
```

Splot remains the generic arbiter. The football-camera assumptions live in the
profile and in the metric-to-candidate adapter.

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
Splot then selects the highest eligible score and the host emits a real
switch to `camera_3`:

```json
{
  "action": "switch",
  "camera_id": "camera_3",
  "status": "selected"
}
```

Real adapters can map this to OBS, vMix, ATEM, FFmpeg, or another router.
