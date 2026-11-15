# Marswalk: a crew-and-rover route planner for Mount Sharp


NASA Space Apps Challenge 2026 · Interplanetary Survival Guide: Martian Map · team: Employees of The Month

What exists so far:
- `run_demo.py`: runs the full chain on synthetic terrain, a real DTM window (`--dtm`), or a DTM paired with a HiRISE orthoimage (`--ortho`) with rule-based stops, stop dwell times, and rover support routing.
- `marswalk/terrain.py`: extracts boxwork ridge, hollow, and lattice-zone masks from **orthoimage brightness** (since the 1 m DTM does not resolve the lattice), dropping bright patches such as the bluff (`ZONE_REL = 0.65` in `params.py`).
- `marswalk/stops.py`: chooses the habitat and three science stops by rules—the lattice margin, the lattice interior, and the bluff contact.
- **Rover support & return to base:** the rover drives to every stop it can reach; for stops inside the lattice or on steep ground, it drives to the nearest reachable support point (`rover_target_rc`), waits while the astronaut walks the remaining gap (`rover_gap_m`), and returns to the habitat after the last stop.
- **Stop dwell time:** each stop adds 15 min (`DWELL_MIN_PER_STOP` in `params.py`), so the radiation budget (8.75 µGy/h from Curiosity RAD, 50 µGy excursion limit, hypothetical storm multiplier) covers time spent working at stops as well as walking.
- `marswalk/layers.py` & `marswalk/report.py`: exports hillshade, slope, and ortho-mask layers plus a downsampled elevation grid alongside per-point profiles and labelled numbers (sourced, derived, assumed, simulated) into `routes.json`.
- `marswalk/viz.py`: four diagnostic plots (`1_layers.png`, `2_costs.png`, `3_routes.png`, `4_ortho_masks.png`).
- `marswalk/export.py` and `nav2_test/`: exports the rover cost grid as a Nav2 map (`rover_cost.pgm/.yaml`) and tests it with the ROS 2 Jazzy Nav2 planner.
- `tools/`: CLI helpers to check candidate windows (`check_window.py`), preview the orthoimage (`overview_ortho.py`, `tile_sheet.py`), and tune mask thresholds (`tune_masks.py`).

Real-window results (3300/10450, 500 × 500 m): astronaut 565 m, max slope 17.6°, 54 min total including dwell, 7.9 µGy dose (GO).

Try it:
```bash
python3 run_demo.py out                                   # synthetic test terrain, not Mars
python3 run_demo.py out --dtm DTM.IMG --ortho ORTHO.JP2   # real window 3300/10450, 500 x 500 (needs rasterio)