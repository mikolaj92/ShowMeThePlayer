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

The first switcher is deliberately a dry-run JSON command:

```json
{
  "action": "switch",
  "camera_id": "camera_3",
  "status": "selected"
}
```

Real adapters can map this to OBS, vMix, ATEM, FFmpeg, or another router.
