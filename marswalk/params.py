"""All tunable numbers live here. Every value is an ASSUMPTION unless a source is cited.
The challenge statement gives no limits; state these in the README and justify or cite them."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentModel:
    name: str
    max_slope_deg: float      # hard limit: steeper cells are blocked
    slope_weight: float       # extra cost as slope approaches the limit (quadratic)
    ridge_penalty: float      # added multiplier on ridge cells (inf = blocked)
    sand_penalty: float       # added multiplier on sandy hollows (trap risk)
    rock_blocked: bool = True # boulders block movement
    rock_margin_m: float = 1.0  # clearance kept around rocks

# ASSUMPTION values for testing the pipeline; replace with justified ones for the entry.
ASTRONAUT = AgentModel("astronaut", max_slope_deg=25.0, slope_weight=3.0,
                       ridge_penalty=2.0, sand_penalty=0.5)
ROVER     = AgentModel("rover", max_slope_deg=15.0, slope_weight=4.0,
                       ridge_penalty=float("inf"), sand_penalty=4.0, rock_margin_m=2.0)

WALK_SPEED_M_S = 1.0   # ASSUMPTION: average EVA walking speed over this terrain
ABORT_RADIUS_M = 400.0 # ASSUMPTION: max straight-line distance from rover/habitat

# RADIATION SAFETY BUDGET (Derived from MSL Curiosity RAD data)
RAD_DOSE_RATE_MICROGY_HR = 8.75  # Normal Gale Crater surface dose rate (~210 microGy/day)
RAD_STRESS_MULTIPLIER = 10.0     # HYPOTHETICAL stress test, NOT from RAD data (largest event in the first-year summary was ~260 vs ~180-225 uGy/day)
RAD_SPE_MULTIPLIER = RAD_STRESS_MULTIPLIER  # old name kept for compatibility
EVA_RAD_LIMIT_MICROGY = 50.0     # ASSUMPTION: Max allowed dose per surface excursion

ROVER_SPEED_M_S = 0.5            # ASSUMPTION: rover cruise speed
BATTERY_DRAIN_PCT_PER_KM = 4.0   # SIMULATED: invented for the tablet mockup, not a sourced figure

# --- Orthoimage-derived boxwork masks (ALL ASSUMPTIONS, tune on the real window; overlay in 4_ortho_masks.png) ---
ORTHO_SMOOTH_CELLS = 1.0          # light denoise before contrast
ORTHO_LOCAL_CELLS = 10            # scale of the local mean (hollows are ~10-30 cells wide)
ORTHO_K = 0.5                     # dark/light = differs from the local mean by K local-sigmas ...
ORTHO_MIN_CONTRAST = 0.08         # ... and by at least this much (brightness scaled 0-1 by the 2-98 percentile)
ORTHO_HOLLOW_MIN_CELLS = 15       # hollow = compact dark blob: size limits (cells) ...
ORTHO_HOLLOW_MAX_CELLS = 700
ORTHO_HOLLOW_MAX_ASPECT = 3.5     # ... and elongation limit (bluff shadows are long streaks)
ORTHO_ZONE_CELLS = 20             # smoothing scale of the hollow-density map
ORTHO_ZONE_REL = 0.65             # lattice zone = density above this fraction of the 97th percentile (0.5 spills, 0.8 too tight on the test window)
ORTHO_ZONE_MIN_FRACTION = 0.06    # drop lattice-zone patches smaller than this fraction of the window
ORTHO_ZONE_MAX_BRIGHTNESS = 0.6   # drop zone patches brighter than this on average (bright bluff, 0-1 scale)
ORTHO_MIN_RIDGE_CELLS = 15        # drop ridge specks smaller than this
HAB_DIST_FROM_LATTICE_M = 200.0   # RULE: habitat placed about this far from the lattice centre, on smooth ground
STOP_MARGIN_M = 20.0              # RULE: margin stop within this distance of the lattice edge
# Labels: ridge/hollow masks are an IMAGE-BRIGHTNESS PROXY (not elevation); brightness also reflects shadow and illumination.

DWELL_MIN_PER_STOP = 15.0        # ASSUMPTION: time spent working at each science stop (the walk alone is only ~10 min)
CAMERA_HEIGHT_M = 1.6            # ASSUMPTION: rover camera mast height for the simulated view
ROVER_RETURNS_TO_HAB = True       # ASSUMPTION: the rover drives back to the habitat after the last stop
