# Changelog

## Unreleased

- Install the Mojo-backed Splot binding from immutable Git tag `v0.4.1`
  instead of a sibling checkout or superseded Python runtime.
- Migrate the director to Splot `fuse_json` and TOML-only profiles.
- Add one canonical Lokay product gate and remove mill leftovers.
- Add a `dev` extra so `uv run --extra dev pytest` can install pytest.

## 0.1.0

- Initial Splot-based camera director prototype.
- Added camera metrics adapter, Splot profile, CLI, dry-run switch command,
  example metrics, docs, and tests.
