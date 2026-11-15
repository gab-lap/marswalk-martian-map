"""Try a grid of mask settings on ONE window and save a contact sheet, so you can pick the best by eye.
Usage: python3 tools/tune_masks.py DTM.IMG ORTHO.JP2 [col row w h]     (run from the project folder; caches the window in ortho_window.npy)
       python3 tools/tune_masks.py --npy ortho_window.npy              (reuse the cache, fast)
Panels vary ORTHO_K (rows) and ORTHO_ZONE_REL (columns). Copy the values you like into marswalk/params.py."""
import sys, os, types, numpy as np
sys.path.insert(0, os.getcwd())
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from marswalk import terrain, params as P

if sys.argv[1] == "--npy":
    img = np.load(sys.argv[2])
else:
    win = tuple(int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else (3300, 10450, 500, 500)
    img = terrain.load_ortho(sys.argv[2], sys.argv[1], win); np.save("ortho_window.npy", img)
fig, axs = plt.subplots(3, 3, figsize=(16, 16))
for i, k in enumerate((0.35, 0.5, 0.7)):
    for j, rel in enumerate((0.5, 0.65, 0.8)):
        q = types.SimpleNamespace(**{n: getattr(P, n) for n in dir(P) if n.isupper()}); q.ORTHO_K, q.ORTHO_ZONE_REL = k, rel
        ridge, hollow, zone = terrain.ortho_masks(img, q)
        ax = axs[i, j]; lo, hi = np.nanpercentile(img, [2, 98]); ax.imshow(img, cmap="gray", vmin=lo, vmax=hi)
        ov = np.zeros(img.shape + (4,)); ov[ridge] = (1, .5, 0, .7); ov[hollow] = (.1, .4, 1, .7); ax.imshow(ov)
        if zone.any(): ax.contour(zone, levels=[.5], colors="yellow", linewidths=1.2)
        ax.set_title(f"K={k}  ZONE_REL={rel}  zone={zone.mean():.0%}"); ax.axis("off")
plt.tight_layout(); plt.savefig("tune_masks.png", dpi=80); print("saved tune_masks.png")
