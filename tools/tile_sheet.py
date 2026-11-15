"""Contact sheets of the orthoimage over the DTM footprint, one labelled tile per DTM window, to spot the boxwork lattice
(a weblike network of light ridges around darker hollows). Each tile is shown at reduced size; labels are the window's top-left (col, row).
Usage: python3 tile_sheet.py DTM.IMG ORTHO.JP2 [tile_cells=1000] [out_prefix=tiles] [col0 row0 col1 row1]
Then check candidates at full detail with:  python3 check_window.py DTM ORTHO col row 500 500 out.png"""
import sys, numpy as np, rasterio
from rasterio.windows import Window, from_bounds
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

dtm_path, ortho_path = sys.argv[1], sys.argv[2]
tile = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
prefix = sys.argv[4] if len(sys.argv) > 4 else "tiles"
PER, SHOW = 12, 500                                   # tiles per sheet, preview size in pixels

with rasterio.open(dtm_path) as d:
    W, H, nodata = d.width, d.height, d.nodata
    sm = d.read(1, out_shape=(max(1, H // 8), max(1, W // 8))).astype("float64")
    valid = (sm > -1e30) & np.isfinite(sm)
    if nodata is not None: valid &= sm != nodata
    c0, r0, c1, r1 = (int(v) for v in sys.argv[5:9]) if len(sys.argv) >= 9 else (0, 0, W, H)
    tiles = []
    for r in range(r0, min(r1, H) - tile + 1, tile):
        for c in range(c0, min(c1, W) - tile + 1, tile):
            frac = valid[r // 8:(r + tile) // 8, c // 8:(c + tile) // 8].mean()
            if frac >= 0.9: tiles.append((c, r, d.window_bounds(Window(c, r, tile, tile))))
print(f"{len(tiles)} tiles with >=90% DTM coverage -> {int(np.ceil(len(tiles) / PER))} sheets")

with rasterio.open(ortho_path) as o:
    for s in range(0, len(tiles), PER):
        chunk = tiles[s:s + PER]
        fig, axs = plt.subplots(4, 3, figsize=(12, 16)); axs = axs.ravel()
        for ax, (c, r, b) in zip(axs, chunk):
            img = o.read(1, window=from_bounds(*b, transform=o.transform), boundless=True, fill_value=0,
                         out_shape=(SHOW, SHOW)).astype("float64")
            lo, hi = np.percentile(img[img > 0], [2, 98]) if np.any(img > 0) else (0, 1)
            ax.imshow(img, cmap="gray", vmin=lo, vmax=hi); ax.set_title(f"col={c} row={r}  ({tile} cells wide)", fontsize=9)
        for ax in axs: ax.axis("off")
        plt.tight_layout(); name = f"{prefix}_{s // PER + 1}.png"; plt.savefig(name, dpi=100); plt.close(fig); print("saved", name)
