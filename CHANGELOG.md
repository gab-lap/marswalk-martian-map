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

