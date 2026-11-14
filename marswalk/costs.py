import numpy as np
from scipy.ndimage import binary_dilation
from .params import AgentModel

def slope_deg(dem, cell_m):
    gy, gx = np.gradient(np.nan_to_num(dem, nan=np.nanmean(dem)), cell_m)
    return np.degrees(np.arctan(np.hypot(gx, gy)))

def build_cost(dem, cell_m, ridge, sand, rocks, agent: AgentModel):
    """Per-cell multiplier >= 1 (cost of crossing the cell); np.inf = blocked."""
    slope = slope_deg(dem, cell_m)
    cost = np.ones_like(dem, dtype="float64")
    cost += agent.slope_weight * (slope / agent.max_slope_deg) ** 2
    cost += np.where(ridge, agent.ridge_penalty, 0.0)
    cost += np.where(sand, agent.sand_penalty, 0.0)
    blocked = slope > agent.max_slope_deg
    if agent.rock_blocked:
        k = int(np.ceil(agent.rock_margin_m / cell_m))
        blocked |= binary_dilation(rocks, iterations=max(k, 1))
    blocked |= np.isnan(dem)
    cost[blocked] = np.inf
    return cost, slope
