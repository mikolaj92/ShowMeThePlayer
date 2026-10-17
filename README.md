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

### CLI flags

| Flag | Meaning |
| --- | --- |
| `--input PATH` | Required input JSON file with camera metrics and optional state. |
| `--profile PATH` | Splot profile TOML file; defaults to the bundled `src/showmetheplayer/profiles/player-director/profile.toml`. |
| `--state PATH` | Optional JSON state file, read if it exists and written after a successful decision. |
| `--out PATH` | Optional output file for the raw Splot result JSON. |
| `--switch-out PATH` | Optional output file for the dry-run switch command JSON. |
| `-h`, `--help` | Show help: `showmetheplayer --help` or `showmetheplayer decide --help`. |

Without `--state`, the command uses the input JSON's `state` and does not write
a separate state file. With `--state`, a missing file leaves the input state
unchanged. An existing file replaces the input's entire `state`, even if the
file contains `{}`. After successful decision processing, the specified file
receives the new state, or `{}` if Splot returns no state.

The `--out` file contains the raw JSON envelope returned by Splot's `fuse_json`,
including `decision`, `state`, and `evaluations` (requested by this host); it is
not a generated decision report. `switch_command.json` is a small dry-run command
that an actual switcher adapter can consume later.

`examples/metrics/round_1.json` already carries `state.previous_decision` for
`camera_1`. On the first run above, if `state.json` does not exist, that input
state is used; the next run reads the saved file instead. Packed hysteresis
(`min_improvement = 0.15`) keeps that camera:
`switch camera=camera_1 status=selected`. The same cameras without
`previous_decision` switch to `camera_3`.

## Metrics Contract

See the [metrics contract](docs/METRICS.md) for the input payload, camera
field defaults, visibility threshold, and selection behavior.

## Boundary

Missing on purpose:

- RTSP/NDI/video ingest
- player detection/tracking
- frame synchronization
- production switcher control
- low-latency streaming loop

Those should be separate adapters.
