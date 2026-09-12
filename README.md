# ShowMeThePlayer

ShowMeThePlayer is a small Splot-based prototype for live camera selection:
given metrics from several football-pitch cameras, it decides which camera
should be allowed into the live stream.

It does not read video, run computer vision, or control OBS/vMix/Blackmagic.
Those are adapters around this package. This project owns the contract between
camera metrics, Splot arbitration, and a dry-run switch command.

```text
camera streams -> tracker metrics -> ShowMeThePlayer -> Splot -> switch command
```

## Quick Start

Splot is pulled from its immutable GitHub tag `v0.4.1`. No sibling clone is
required. Splot 0.4 is a thin binding to its Mojo engine, so the Modular Mojo
toolchain must be available on `PATH` (or through the Splot build environment).
PyPI's unrelated `splot` package will not work here.

```bash
uv sync

uv run showmetheplayer decide \
  --input examples/metrics/round_1.json \
  --out decision_report.json \
  --state state.json \
  --switch-out switch_command.json

uv run --extra dev pytest -q
```

The output report is a normal Splot decision report. `switch_command.json` is a
small dry-run command that an actual switcher adapter can consume later.

## Metrics Contract

Each camera metric is one candidate:

```json
{
  "camera_id": "camera_3",
  "player_visible": true,
  "visibility": 0.91,
  "occlusion": 0.12,
  "sharpness": 0.78,
  "face_angle": 0.64,
  "available": true
}
```

Splot handles scoring, constraints, keep-current behavior, hysteresis and
cooldown. ShowMeThePlayer only converts camera metrics into Splot candidates
and turns the decision into a switch command.

## Boundary

Missing on purpose:

- RTSP/NDI/video ingest
- player detection/tracking
- frame synchronization
- production switcher control
- low-latency streaming loop

Those should be separate adapters.
