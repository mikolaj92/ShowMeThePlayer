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

The first switcher is deliberately a dry-run JSON command:

```json
{
  "action": "switch",
  "camera_id": "camera_3",
  "status": "selected"
}
```

Real adapters can map this to OBS, vMix, ATEM, FFmpeg, or another router.
