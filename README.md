# Marswalk: a crew-and-rover route planner for Mount Sharp

NASA Space Apps Challenge 2026 · Interplanetary Survival Guide: Martian Map · team: Employees of The Month

What exists so far:
- `run_demo.py`: runs the whole chain on synthetic terrain, or on a real DTM window (`--dtm`), with **hand-placed** test stops.
- `marswalk/viz.py`: three plots (layers, cost grids, routes).
- `marswalk/report.py`: per-point route profile, radiation scenarios and numbers labelled as sourced, derived, assumed or simulated; written to `routes.json` for a future tablet page.
- `marswalk/export.py` and `nav2_test/`: the rover cost grid is exported as a Nav2 map and tested with the Nav2 planner (ROS 2 Jazzy).
- Radiation budget in `params.py`: 8.75 µGy/h from the Curiosity RAD first-year summary, a 50 µGy excursion limit (assumed) and a hypothetical storm multiplier.

Try it:
```
python3 run_demo.py out                       # synthetic test terrain, not Mars
python3 run_demo.py out --dtm DTM.IMG         # real window 3300/10450, 500 x 500 (needs rasterio)
```
Outputs: `1_layers.png`, `2_costs.png`, `3_routes.png`, `summary.json`, `routes.json`, `rover_cost.pgm/.yaml`.

Known problem so far: the DTM does not resolve the boxwork lattice, so the ridge and hollow masks from the DTM are weak.
