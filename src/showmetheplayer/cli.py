from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .director import DEFAULT_PROFILE, build_switch_command, decide_from_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="showmetheplayer")
    subcommands = parser.add_subparsers(dest="command", required=True)

    decide = subcommands.add_parser("decide")
    decide.add_argument("--input", required=True)
    decide.add_argument("--profile", default=str(DEFAULT_PROFILE))
    decide.add_argument("--state")
    decide.add_argument("--out")
    decide.add_argument("--switch-out")

    args = parser.parse_args(argv)
    try:
        if args.command == "decide":
            return _decide(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def _decide(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if args.state and Path(args.state).exists():
        payload["state"] = json.loads(Path(args.state).read_text(encoding="utf-8"))
    result = decide_from_payload(payload, profile=args.profile)
    report = result
    switch = build_switch_command(result)

    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.state:
        Path(args.state).write_text(json.dumps(result.get("state") or {}, indent=2, sort_keys=True), encoding="utf-8")
    if args.switch_out:
        Path(args.switch_out).write_text(json.dumps(switch, indent=2, sort_keys=True), encoding="utf-8")

    selected = switch.get("camera_id") or "-"
    print(f"{switch['action']} camera={selected} status={switch['status']} confidence={switch['confidence']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
