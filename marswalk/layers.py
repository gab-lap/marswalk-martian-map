"""Layer PNGs (as data URIs) and a downsampled height grid for the tablet page's map toggles, 3D view and rover camera.
Everything here is DERIVED from the DTM / orthoimage; the ortho masks are the brightness proxy (see params.py)."""
import base64, io
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

def _uri(rgb):
    b = io.BytesIO(); plt.imsave(b, np.clip(rgb, 0, 1), format="png")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

def _gray(a):
    lo, hi = np.nanpercentile(a, [2, 98]); return np.clip((a - lo) / max(hi - lo, 1e-9), 0, 1)

def build(dem, slope, img, ridge, hollow, zone, cell_m, grid=200):
    d = np.nan_to_num(dem, nan=float(np.nanmean(dem)))
    hs = LightSource(azdeg=315, altdeg=35).hillshade(d, dx=cell_m, dy=cell_m)
    g = np.dstack([hs] * 3)
    sl = plt.cm.inferno(np.clip(np.nan_to_num(slope) / 30.0, 0, 1))[..., :3]
    layers = [{"name": "Hillshade", "src": _uri(g)}, {"name": "Slope", "src": _uri(sl)}]
    tex = g
    if img is not None:
        base = np.dstack([_gray(img)] * 3); ov = base.copy()
        ov[ridge] = 0.55 * ov[ridge] + 0.45 * np.array([0.97, 0.55, 0.1])
        ov[hollow] = 0.55 * ov[hollow] + 0.45 * np.array([0.1, 0.35, 0.9])
        layers.append({"name": "Ortho masks (proxy)", "src": _uri(ov)}); tex = base
    st = max(1, int(np.ceil(max(d.shape) / grid))); z = d[::st, ::st]
    return {"layers": layers,
            "terrain": {"rows": int(z.shape[0]), "cols": int(z.shape[1]), "step_m": round(st * cell_m, 3),
                        "z": [round(float(v), 1) for v in z.ravel()], "tex": _uri(tex),
                        "note": "derived: DTM downsampled; texture = orthoimage brightness (or hillshade if no ortho)"}}
