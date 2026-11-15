"""RULE-BASED habitat and science stops (replaces hand-placed points). Rules, in order:
 habitat  : smooth, passable ground about HAB_DIST_FROM_LATTICE_M from the lattice centre
 stop 1   : lattice MARGIN reachable by the rover (rover base / gear cache and rendezvous)
 stop 2   : lattice INTERIOR (deepest point inside the lattice zone, astronaut only)
 stop 3   : BLUFF contact (astronaut-passable ground next to a large steep area near the lattice, astronaut only)
All are rules on proxy layers, not a scientific selection."""
import numpy as np
from scipy.ndimage import label, binary_dilation, distance_transform_edt

def largest_passable(cost):
    lab, n = label(np.isfinite(cost))
    if n == 0: return np.zeros(cost.shape, bool)
    return lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)

def _pick(mask, score):
    rr, cc = np.nonzero(mask); i = int(np.argmin(score(rr, cc))); return (int(rr[i]), int(cc[i]))

def choose_stops(slope, zone, ridge, cost_a, cost_r, cell_m, astro_max_slope, hab_dist_m, margin_m):
    core_r, core_a = largest_passable(cost_r), largest_passable(cost_a)
    rr, cc = np.nonzero(zone)
    if len(rr) == 0: raise ValueError("empty lattice zone: tune the ORTHO_* parameters")
    zr, zc = rr.mean(), cc.mean()
    near_zone = binary_dilation(zone, iterations=max(1, int(round(15 / cell_m))))
    for smax in (6.0, 10.0, 90.0):
        cand = core_r & ~near_zone & (slope < smax)
        if cand.any(): break
    hab = _pick(cand, lambda r, c: np.abs(np.hypot(r - zr, c - zc) * cell_m - hab_dist_m))
    ring = binary_dilation(zone, iterations=max(1, int(round(margin_m / cell_m)))) & ~ridge & core_r
    if not ring.any(): ring = core_r
    s1 = _pick(ring, lambda r, c: np.hypot(r - hab[0], c - hab[1]))
    inner = core_a & zone
    if not inner.any(): inner = core_a
    depth = distance_transform_edt(zone)
    s2 = _pick(inner, lambda r, c: -depth[r, c])
    steep = slope > astro_max_slope
    lab, n = label(steep)
    if n:
        big = np.bincount(lab.ravel()) >= 300; big[0] = False; steep = big[lab]
    band = binary_dilation(steep, iterations=6) & ~steep & core_a
    d_zone = distance_transform_edt(~zone) * cell_m
    far = np.hypot(*(np.indices(slope.shape) - np.array(s2)[:, None, None])) * cell_m > 60
    cand = band & far & (d_zone < 80)
    if not cand.any(): cand = band & far
    if not cand.any(): cand = core_a & far
    s3 = _pick(cand, lambda r, c: np.hypot(r - zr, c - zc))
    stops = [
        {"rc": list(s1), "type": "lattice margin", "rover_visits": True, "rule": "rover-reachable ground within the margin of the lattice zone, nearest the habitat",
         "objective": "Rover base and gear cache; first look at the boxwork from the margin; rendezvous point"},
        {"rc": list(s2), "type": "lattice interior", "rover_visits": False, "rule": "deepest point inside the lattice zone reachable on foot",
         "objective": "Ridge-crest and hollow-floor observations inside the lattice (astronaut on foot, rover stays at the margin)"},
        {"rc": list(s3), "type": "bluff contact", "rover_visits": False, "rule": "foot-passable ground beside a large steep area near the lattice",
         "objective": "Boxwork-to-bluff contact: layered bedrock beside the lattice"}]
    return hab, stops
