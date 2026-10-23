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
required. `uv sync` installs the matching Mojo 1.0.0 toolchain in `.venv`;
`uv run` makes it available to Splot. Compilation needs a C linker (macOS:
`xcode-select --install`; Ubuntu/Debian: `sudo apt install gcc`).

```bash
uv sync --locked

demo_dir=$(mktemp -d ./quick-start.XXXXXX)
uv run showmetheplayer decide \
  --input examples/metrics/round_1.json \
  --out "$demo_dir/decision_report.json" \
  --state "$demo_dir/state.json" \
  --switch-out "$demo_dir/switch_command.json"

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
not a generated decision report. `switch_command.json` is a dry-run command for a future switcher adapter.

The fresh output directory leaves `state.json` absent, so the demo uses the
input's `state.previous_decision` for `camera_1`. It prints
`switch camera=camera_1 status=selected confidence=0.796` and writes
`action=switch`, `camera_id=camera_1`, not `camera_3`. The host maps `selected`
or `routed` with a camera ID to `switch`, even when that camera is already current.
Only `kept_previous` with a camera ID maps to `keep`; see [Architecture](docs/ARCHITECTURE.md).

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
cooldown. ShowMeThePlayer builds Splot candidates, forwards `player_visible`,
sets candidate `visibility` to `0.0` when that flag is false, and turns the
decision into a switch command. See the [metrics contract](docs/METRICS.md)
for the profile's independent visibility threshold.

## Boundary

Missing on purpose:

- RTSP/NDI/video ingest
- player detection/tracking
- frame synchronization
- production switcher control
- low-latency streaming loop

Those should be separate adapters.
