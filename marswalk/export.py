import numpy as np

def save_nav2_map(cost, prefix, cell_m, origin_xy=(0.0, 0.0)):
    """Write <prefix>.pgm + <prefix>.yaml for Nav2's map_server (mode: scale).
    Row 0 of the array is the TOP of the image (north). Blocked = black (occupied),
    cost multiplier 1 = white (free), in-between = grey."""
    finite = np.isfinite(cost)
    norm = np.ones_like(cost)
    cmax = np.nanpercentile(cost[finite], 99)
    norm[finite] = np.clip((cost[finite] - 1.0) / max(cmax - 1.0, 1e-9), 0, 0.6)  # keep passable < occupied_thresh
    pix = (255 - np.round(norm * 255)).astype(np.uint8)
    pix[~finite] = 0
    h, w = pix.shape
    with open(f"{prefix}.pgm", "wb") as f:
        f.write(f"P5\n{w} {h}\n255\n".encode()); f.write(pix.tobytes())
    name = prefix.split("/")[-1]
    with open(f"{prefix}.yaml", "w") as f:
        f.write(f"image: {name}.pgm\nmode: scale\nresolution: {cell_m}\n"
                f"origin: [{origin_xy[0]}, {origin_xy[1]}, 0.0]\nnegate: 0\n"
                "occupied_thresh: 0.65\nfree_thresh: 0.25\n")
