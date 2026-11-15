# Changelog (dates are when the work was written)

## Baseline, Nov 6-13, 2026 (written BEFORE the Nov 14 9:00 hackathon start)
Synthetic terrain, per-agent costs, A* with no corner-cutting, Nav2 map export, planner-only Nav2 test, real-DTM loader and masks, MSL RAD-based radiation budget. Run on a Mount Sharp HiRISE DTM window on the owner's machine (Nov 11-13).

## v2, Nov 13, 2026 (also BEFORE the 9:00 start)
- `terrain.py`: rasterio imported inside `load_dem`, so synthetic terrain runs without it.
- `run_demo.py`: DTM path and window as arguments (no hardcoded path); synthetic fallback; writes `routes.json`.
- `marswalk/report.py` (new): per-point route profile for the tablet page; radiation scenarios; "minutes to limit"; labelled numbers.
- `params.py`: `RAD_STRESS_MULTIPLIER` (hypothetical, not from RAD data), `ROVER_SPEED_M_S`, `BATTERY_DRAIN_PCT_PER_KM` (simulated).
- `viz.py`: route plot title passed in (no longer says Mount Sharp on synthetic runs).
- Tested on synthetic terrain only; not re-run on the real DTM (file not available where this was edited).

## v3, Nov 13-14 night, 2026 (BEFORE the 9:00 Nov 14 start)
- Window locked to col 3300, row 10450, 500x500 (boxwork lattice beside a layered bluff), after checking four candidate windows against the orthoimage.
- Finding: the DTM does not resolve the lattice, so `terrain.load_ortho` and `terrain.ortho_masks` derive ridge, hollow and lattice-zone masks from orthoimage brightness (proxy).
- New `marswalk/stops.py`: rule-based habitat and three stops (lattice margin with rover, lattice interior, bluff contact) replacing hand-placed points.
- `run_demo.py` now uses argparse (`--dtm`, `--ortho`, `--window`), writes `4_ortho_masks.png`; rover visits the margin stop only.
- `tools/`: window check, overview and tile-sheet scripts.
- Tested on SYNTHETIC terrain with a fake lattice only. NOT yet run on the real window; masks and stop rules need tuning there.

## v4, Nov 14 early morning, 2026 (BEFORE the 9:00 Nov 14 start)
- Masks re-tuned on a screenshot of the real 3300/10450 overlay (v3 flagged bluff shadows as lattice and missed part of the lattice): hollows are now compact dark blobs (size and elongation limits), the lattice zone is the density of compact hollows (ORTHO_ZONE_REL 0.65), zone patches that are small or bright (bluff) are dropped, ridges only inside the zone.
- On that screenshot the zone follows the central lattice and no longer touches the bluff; it is conservative and still misses the weaker lattice at the far left. `tools/tune_masks.py` makes a 3x3 grid (ORTHO_K x ORTHO_ZONE_REL) for choosing settings on the real window.
- Still NOT run on the real arrays; tuned on a downsampled screenshot of the orthoimage panel only.
