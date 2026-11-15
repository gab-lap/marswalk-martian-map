# Marswalk: a crew-and-rover route planner for Mount Sharp

NASA Space Apps Challenge 2026 · Interplanetary Survival Guide: Martian Map · team: Employees of The Month

What exists so far:
- `run_demo.py`: runs the full chain on synthetic terrain, a real DTM window (`--dtm`), or a DTM paired with a HiRISE orthoimage (`--ortho`) using rule-based stops.
- `marswalk/terrain.py`: extracts boxwork ridge, hollow, and lattice-zone masks from **orthoimage brightness** (since the 1 m DTM does not resolve the lattice), dropping bright patches such as the bluff (`ZONE_REL = 0.65` in `params.py`).
- `marswalk/stops.py`: chooses the habitat and three science stops by rules—the lattice margin (reachable by rover), the lattice interior (on foot), and the bluff contact (on foot).
- `marswalk/viz.py`: four diagnostic plots (`1_layers.png`, `2_costs.png`, `3_routes.png`, `4_ortho_masks.png`).
- `marswalk/report.py`: per-point route profile, radiation scenarios (8.75 µGy/h Curiosity RAD summary, 50 µGy excursion limit, hypothetical storm multiplier), and numbers labelled as sourced, derived, assumed, or simulated in `routes.json`.
- `marswalk/export.py` and `nav2_test/`: exports the rover cost grid as a Nav2 map (`rover_cost.pgm/.yaml`) and tests it with the ROS 2 Jazzy Nav2 planner.
- `tools/`: CLI helpers to check candidate windows (`check_window.py`), preview the orthoimage (`overview_ortho.py`, `tile_sheet.py`), and tune mask thresholds on a 3 × 3 grid (`tune_masks.py`).

Try it:
```bash
python3 run_demo.py out                                   # synthetic test terrain, not Mars
python3 run_demo.py out --dtm DTM.IMG --ortho ORTHO.JP2   # real window 3300/10450, 500 x 500 (needs rasterio)