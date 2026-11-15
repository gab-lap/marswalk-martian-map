"""Overview of the whole DTM footprint, drawn on the orthoimage, with a grid labelled in DTM cells (col, row).
Use it to find a window that shows the boxwork lattice, then pass that window to run_demo.py / check_window.py.
Usage: python3 overview_ortho.py DTM.IMG ORTHO.JP2 [grid_step_cells=500] [out.png]"""
import sys, numpy as np, rasterio
from rasterio.windows import from_bounds
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

dtm_path, ortho_path = sys.argv[1], sys.argv[2]
step = int(sys.argv[3]) if len(sys.argv) > 3 else 500
out = sys.argv[4] if len(sys.argv) > 4 else "overview.png"

with rasterio.open(dtm_path) as d:
    W, H, bounds, nodata = d.width, d.height, d.bounds, d.nodata
    sm = d.read(1, out_shape=(max(1, H // 8), max(1, W // 8))).astype("float64")
valid = (sm > -1e30) & np.isfinite(sm)
if nodata is not None: valid &= sm != nodata
print(f"DTM size {W} x {H} cells; valid coverage {valid.mean():.0%}")

with rasterio.open(ortho_path) as o:
    ow = from_bounds(*bounds, transform=o.transform)
    scale = max(1, int(np.ceil(max(ow.width, ow.height) / 3000)))
    img = o.read(1, window=ow, boundless=True, fill_value=0,
                 out_shape=(max(1, int(ow.height) // scale), max(1, int(ow.width) // scale))).astype("float64")
if not np.any(img > 0): print("WARNING: no orthoimage coverage over the DTM footprint")
lo, hi = np.percentile(img[img > 0], [2, 98]) if np.any(img > 0) else (0, 1)

fig, ax = plt.subplots(figsize=(12, min(24, max(6, 12 * H / W))))
ax.imshow(img, cmap="gray", vmin=lo, vmax=hi, extent=[0, W, H, 0])
ax.contour(np.linspace(0, W, valid.shape[1]), np.linspace(0, H, valid.shape[0]), valid, levels=[0.5], colors="yellow", linewidths=0.8)
for x in range(0, W, step): ax.axvline(x, color="cyan", lw=0.4)
for y in range(0, H, step): ax.axhline(y, color="cyan", lw=0.4)
ax.set_xticks(range(0, W, step)); ax.set_yticks(range(0, H, step)); ax.tick_params(labelsize=7)
ax.set_xlabel("DTM column (cells)"); ax.set_ylabel("DTM row (cells)")
ax.set_title("Orthoimage over the DTM footprint (yellow = DTM valid data); grid in DTM cells")
plt.tight_layout(); plt.savefig(out, dpi=120); print("saved", out)
