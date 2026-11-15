"""Side-by-side check: does the DTM window show boxwork? Hillshade from the DTM vs the SAME ground area in the orthoimage.
Usage: python3 check_window.py DTM.IMG ORTHO.JP2 [col row width height] [out.png]
(Default window 3100 6500 500 500.) Needs rasterio, numpy, matplotlib."""
import sys, numpy as np, rasterio
from rasterio.windows import Window, from_bounds
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

dtm_path, ortho_path = sys.argv[1], sys.argv[2]
col, row, w, h = (int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else (3100, 6500, 500, 500)
out = sys.argv[7] if len(sys.argv) > 7 else "window_check.png"

with rasterio.open(dtm_path) as d:
    win = Window(col, row, w, h)
    dem = d.read(1, window=win).astype("float64")
    nodata = d.nodata
    bounds = d.window_bounds(win)                       # left, bottom, right, top in the DTM's CRS
    cell = abs(d.transform.a)
    dtm_crs = d.crs
if nodata is not None: dem[dem == nodata] = np.nan
dem[dem < -1e30] = np.nan                               # PDS null values

with rasterio.open(ortho_path) as o:
    if o.crs != dtm_crs: print("WARNING: DTM and ortho CRS differ; the crop below may be misplaced:", dtm_crs, "vs", o.crs)
    ow = from_bounds(*bounds, transform=o.transform)
    scale = max(1, int(np.ceil(max(ow.width, ow.height) / 1500)))   # keep the preview manageable
    img = o.read(1, window=ow, boundless=True, fill_value=0,
                 out_shape=(int(ow.height) // scale, int(ow.width) // scale)).astype("float64")
    print("ortho pixel size (m):", abs(o.transform.a), "| DTM cell (m):", cell, "| crop shape:", img.shape)
if not np.any(img > 0): print("WARNING: the crop is empty; this window may lie outside the orthoimage footprint")

gy, gx = np.gradient(np.nan_to_num(dem, nan=np.nanmean(dem)), cell)
az, alt = np.radians(315), np.radians(45)
slope, aspect = np.arctan(np.hypot(gx, gy)), np.arctan2(-gx, gy)
hs = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
fig, ax = plt.subplots(1, 2, figsize=(14, 7))
ax[0].imshow(hs, cmap="gray"); ax[0].set_title(f"DTM hillshade, window col={col} row={row} {w}x{h} ({cell:.2f} m cells)")
lo, hi = np.percentile(img[img > 0], [2, 98]) if np.any(img > 0) else (0, 1)
ax[1].imshow(img, cmap="gray", vmin=lo, vmax=hi); ax[1].set_title("Orthoimage, same ground area")
for a in ax: a.axis("off")
plt.tight_layout(); plt.savefig(out, dpi=110); print("saved", out)
