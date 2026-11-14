"""Exports for the tablet page: per-route profile, radiation scenarios, labelled numbers.
Every number carries a label: sourced / derived / assumed / simulated."""
import json, math
import numpy as np

def _lab(value, label, **extra):
    d = {"value": value, "label": label}; d.update(extra); return d

def route_points(path, dem, cell_m, speed_m_s, battery_drain_pct_per_km=None):
    """Per-point profile of a (row, col) path. x east, y north (m, origin bottom-left, as in the Nav2 export)."""
    h, _ = dem.shape
    gy, gx = np.gradient(np.nan_to_num(dem, nan=float(np.nanmean(dem))), cell_m)   # d/drow (south), d/dcol (east)
    pts, dist = [], 0.0
    for i, (r, c) in enumerate(path):
        if i:
            pr, pc = path[i - 1]; dist += math.hypot(r - pr, c - pc) * cell_m
        nr, nc = path[min(i + 1, len(path) - 1)]
        pr, pc = path[max(i - 1, 0)]
        de, dn = (nc - pc), -(nr - pr)                       # east, north step directions
        norm = math.hypot(de, dn) or 1.0
        ue, un = de / norm, dn / norm
        ge, gn = gx[r, c], -gy[r, c]                         # elevation gradient east, north
        along, cross = ge * ue + gn * un, -ge * un + gn * ue
        p = {"x_m": round(c * cell_m, 1), "y_m": round((h - 1 - r) * cell_m, 1),
             "elev_m": round(float(dem[r, c]), 2),
             "heading_deg": round(math.degrees(math.atan2(ue, un)) % 360, 1),
             "pitch_deg": round(math.degrees(math.atan(along)), 1),
             "roll_deg": round(math.degrees(math.atan(cross)), 1),
             "dist_m": round(dist, 1), "t_min": round(dist / speed_m_s / 60, 2)}
        if battery_drain_pct_per_km is not None:
            p["battery_pct"] = round(max(0.0, 100 - battery_drain_pct_per_km * dist / 1000), 1)
        pts.append(p)
    return pts

def radiation_block(time_min, rate_uGy_h, limit_uGy, stress_mult):
    hours = time_min / 60.0
    nominal = hours * rate_uGy_h
    def row(name, mult, label):
        dose = nominal * mult
        return {"name": name, "multiplier": mult, "dose_uGy": round(dose, 2),
                "verdict": "GO" if dose <= limit_uGy else "NO-GO", "label": label}
    return {
        "base_rate_uGy_per_h": _lab(rate_uGy_h, "sourced: MSL RAD first-year summary (~210 uGy/day); verify against PDS data"),
        "excursion_limit_uGy": _lab(limit_uGy, "assumed: no official EVA limit used here"),
        "excursion_time_min": _lab(round(time_min, 1), "derived: route length / walking speed"),
        "minutes_to_limit_nominal": _lab(round(limit_uGy / rate_uGy_h * 60, 0), "derived from the two lines above"),
        "multiplier_to_exceed_limit": _lab(round(limit_uGy / nominal, 1) if nominal else None, "derived"),
        "scenarios": [row("nominal", 1.0, "sourced rate"),
                      row("hypothetical stress test", stress_mult, "assumed multiplier, not from RAD data")],
    }

def write_json(path, payload):
    with open(path, "w") as f: json.dump(payload, f, indent=1)
