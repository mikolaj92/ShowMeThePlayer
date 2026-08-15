# Approach plan

<!-- lokay-approach source=deterministic repo=mikolaj92/ShowMeThePlayer issue=7 -->

Repository: `mikolaj92/ShowMeThePlayer`  
Issue: #7 — uv.sources pinuje splot na ../Splot — bez lokalnego klona import pada

## Goal

`pyproject.toml` ma `splot = { path = \"../Splot\", editable = true }`. README każe sklonować `Splot/` obok. Bez tego `uv sync` / import `splot` pada.

## Files likely touched

- `pyproject.toml`
- `director.py`
- `cli.py`

## Test plan

- Run the smallest useful tests for files touched

## Non-goals

- (none stated)

## Notes

- Trust intentional issue; this plan is evidence for later review, not a human gate.
- Coding agent may refine details but should stay on the stated goal and non-goals.
- Collector boundary: if implementation introduces unbounded collection, ship only a bounded collector patch that starts durably in the background after merge. The coding agent and mill must not populate data or wait for collection to finish.
