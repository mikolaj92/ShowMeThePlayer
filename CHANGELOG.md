# Changelog

## Unreleased

- Install the Mojo-backed Splot binding from immutable Git tag `v0.4.1`
  instead of a sibling checkout or superseded Python runtime.
- Migrate the director to Splot `fuse_json` and TOML-only profiles.
- Add one canonical Lokay product gate and remove mill leftovers.
- Add a `dev` extra so `uv run --extra dev pytest` can install pytest.
- Align the metrics contract with the packed 0.4 profile: document and adapt
  only fields Splot scores or the host uses as gates, and stop packing unused
  `tracking_confidence` and `latency`.
- Document that only `camera_id` is required per camera; other metric fields
  have silent defaults in `CameraMetric.from_dict`.

## 0.1.0

- Initial Splot-based camera director prototype.
- Added camera metrics adapter, Splot profile, CLI, dry-run switch command,
  example metrics, docs, and tests.
