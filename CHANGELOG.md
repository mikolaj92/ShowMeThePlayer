# Changelog

## Unreleased

- Install Splot from GitHub (`splot-runtime` @ v0.2.1) instead of pinning
  `tool.uv.sources` to a sibling `../Splot` checkout. `uv sync` no longer
  requires a local clone.

## 0.1.0

- Initial Splot-based camera director prototype.
- Added camera metrics adapter, Splot profile, CLI, dry-run switch command,
  example metrics, docs, and tests.
