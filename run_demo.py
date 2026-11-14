"""Marswalk pipeline (hand-placed test stops). Usage:
  python3 run_demo.py OUT                   synthetic TEST terrain (not Mars data)
  python3 run_demo.py OUT --dtm DTM.IMG     real DTM window, masks from the DTM (needs rasterio)
Default window 3300 10450 500 500. Outputs: 1_layers.png 2_costs.png 3_routes.png summary.json routes.json rover_cost.pgm/.yaml"""
import argparse, json, os, time
import numpy as np
from scipy.ndimage import distance_transform_edt, label
from marswalk import terrain, costs, planner, export, viz, report
from marswalk.params import (ASTRONAUT, ROVER, WALK_SPEED_M_S, ROVER_SPEED_M_S, ABORT_RADIUS_M,
                             RAD_DOSE_RATE_MICROGY_HR, EVA_RAD_LIMIT_MICROGY, RAD_STRESS_MULTIPLIER, BATTERY_DRAIN_PCT_PER_KM)

ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--dtm")
ap.add_argument("--window", nargs=4, type=int, default=[3300, 10450, 500, 500], metavar=("COL", "ROW", "W", "H"))
a = ap.parse_args(); out = a.out; os.makedirs(out, exist_ok=True)

if a.dtm:
    win = tuple(a.window)
    dem, CELL = terrain.load_dem(a.dtm, window_rect=win)
    ridge, sand, rocks = terrain.extract_masks(dem, CELL)
    source, title = os.path.basename(a.dtm), f"Crew & Rover Marswalk: HiRISE window {win}"
else:
    CELL = 1.0
    dem, ridge, sand, rocks = terrain.synthetic_boxwork(n=500, cell_m=CELL, seed=3)
    source, title = "synthetic test terrain (NOT Mars data)", "Crew & Rover Marswalk (TEST terrain, not Mars data)"

cost_a, slope = costs.build_cost(dem, CELL, ridge, sand, rocks, ASTRONAUT)
cost_r, _ = costs.build_cost(dem, CELL, ridge, sand, rocks, ROVER)

def largest_passable(cost):
    lab, n = label(np.isfinite(cost))
    if n == 0: return np.zeros(cost.shape, bool)
    return lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
def snap(mask, rc):
    _, (ir, ic) = distance_transform_edt(~mask, return_indices=True); return (int(ir[rc]), int(ic[rc]))

core = largest_passable(cost_r)
hab = snap(core, (250, 60)); stops = [snap(core, p) for p in [(140, 190), (330, 280), (200, 400)]]   # hand-placed test stops
stop_list = [{"rc": list(s), "type": "hand-placed test stop", "rover_visits": True, "rule": "hand-placed", "objective": "TBD"} for s in stops]

t0 = time.time()
astro_path, _ = planner.route_through(cost_a, [hab] + stops + [hab])
rover_path, _ = planner.route_through(cost_r, [hab] + stops)
print(f"planning time {time.time()-t0:.2f}s")
far_from_hab = lambda path: round(float(max(np.hypot(r - hab[0], c - hab[1]) for r, c in path)) * CELL, 1)

res = {"assumption_note": f"terrain: {source}; limits, speeds and the dose limit are assumptions"}
routes = {"meta": {"terrain_source": source, "window": None if not a.dtm else list(a.window), "cell_m": round(float(CELL), 4),
                   "grid_rows_cols": list(dem.shape), "mask_note": "ridge/sand/rock masks from the DTM",
                   "label_legend": "sourced = NASA dataset; derived = computed from DTM/route; assumed = our parameter; simulated = invented for the mockup"},
          "habitat_rc": list(hab), "abort_radius_m": report._lab(ABORT_RADIUS_M, "assumed"), "stops": stop_list}
if astro_path:
    s = planner.path_stats(astro_path, slope, CELL, WALK_SPEED_M_S)
    far = far_from_hab(astro_path); s["max_dist_from_hab_m"] = far; s["within_abort_radius"] = bool(far <= ABORT_RADIUS_M)
    rad = report.radiation_block(s["time_min"], RAD_DOSE_RATE_MICROGY_HR, EVA_RAD_LIMIT_MICROGY, RAD_STRESS_MULTIPLIER)
    s["radiation_dose_microGy"] = rad["scenarios"][0]["dose_uGy"]; s["radiation_go_nogo"] = rad["scenarios"][0]["verdict"]
    res["astronaut"] = s
    routes["astronaut"] = {"summary": s, "walk_speed_m_s": report._lab(WALK_SPEED_M_S, "assumed"),
                           "points": report.route_points(astro_path, dem, CELL, WALK_SPEED_M_S)}
    routes["radiation"] = rad
else:
    print("WARNING: no astronaut route found")
if rover_path:
    r = planner.path_stats(rover_path, slope, CELL, ROVER_SPEED_M_S); r["max_dist_from_hab_m"] = far_from_hab(rover_path)
    res["rover"] = r
    routes["rover"] = {"summary": r, "speed_m_s": report._lab(ROVER_SPEED_M_S, "assumed"),
                       "battery_note": "battery_pct is SIMULATED (drain per km invented for the mockup)",
                       "points": report.route_points(rover_path, dem, CELL, ROVER_SPEED_M_S, BATTERY_DRAIN_PCT_PER_KM)}
else:
    print("WARNING: no rover route found")
res["waypoints_rc"] = {"hab": list(hab), "stops": [list(p) for p in stops]}
json.dump(res, open(f"{out}/summary.json", "w"), indent=2); print(json.dumps(res, indent=2))
report.write_json(f"{out}/routes.json", routes)
viz.plot_layers(dem, ridge, rocks, slope, f"{out}/1_layers.png", CELL)
viz.plot_cost(cost_a, cost_r, f"{out}/2_costs.png")
viz.plot_routes(dem, CELL, astro_path, rover_path, stops, hab, ABORT_RADIUS_M, f"{out}/3_routes.png", title=title)
export.save_nav2_map(cost_r, f"{out}/rover_cost", CELL)
