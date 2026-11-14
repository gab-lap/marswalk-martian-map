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
