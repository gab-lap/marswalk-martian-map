import numpy as np
from scipy.ndimage import gaussian_filter

def load_dem(path, window_rect=None):
    """Load a DEM GeoTIFF or PDS .IMG (meters). Returns (dem, cell_m). rasterio is imported here so the synthetic test terrain runs without it."""
    import rasterio
    from rasterio.windows import Window
    with rasterio.open(path) as src:
        if window_rect:
            col_off, row_off, width, height = window_rect
            w = Window(col_off, row_off, width, height)
            dem = src.read(1, window=w).astype("float64")
        else:
            dem = src.read(1).astype("float64")
        
        cell_m = abs(src.transform.a)
        nodata = src.nodata
        
    if nodata is not None:
        dem[dem == nodata] = np.nan
    # Failsafe for PDS extreme negative nodata values
    dem[dem < -10000] = np.nan
    
    return dem, cell_m

def extract_masks(dem, cell_m):
    """Derive proxy hazard masks from the real DEM."""
    dem_filled = np.nan_to_num(dem, nan=np.nanmean(dem))
    
    # Ridge mask: Top-hat filter (local height relative to background)
    background = gaussian_filter(dem_filled, sigma=5.0 / cell_m)
    relative_height = dem_filled - background
    ridge = relative_height > 0.4  # Proxy ASSUMPTION: 40cm higher than local surroundings
    
    # Rock mask: Surface roughness proxy (local jaggedness)
    smoothed = gaussian_filter(dem_filled, sigma=1.0 / cell_m)
    roughness = np.abs(dem_filled - smoothed)
    rocks = roughness > 0.3  # Proxy ASSUMPTION: high local variance
    
    # Sand mask: Flat hollows (low slope, negative relative height)
    sand = (relative_height < -0.2) & ~rocks
    
    return ridge, sand, rocks

def _smooth_noise(n, rng, scale):
    from scipy.ndimage import gaussian_filter
    z = gaussian_filter(rng.standard_normal((n, n)), scale)
    return (z - z.mean()) / z.std()

def synthetic_boxwork(n=500, cell_m=1.0, seed=0, spacing_m=20.0, ridge_w_m=5.0):
    """TEST DATA ONLY: a made-up boxwork-like surface. Not Mars data.
    Scales follow published descriptions of Mount Sharp boxwork (decameter-scale network, ridges
    ~1-2 m tall and ~5 m across, hollows 10-20 m wide); 1 m cells match a HiRISE DTM.
    Ridge height varies along each ridge and the network has gaps. Returns dem, ridge, sand, rocks."""
    from scipy.ndimage import gaussian_filter
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:n, 0:n]
    theta = np.deg2rad(12)
    u = xx * np.cos(theta) + yy * np.sin(theta)
    v = -xx * np.sin(theta) + yy * np.cos(theta)
    period = spacing_m / cell_m              # centre-to-centre ridge spacing in cells
    w = ridge_w_m / 2 / cell_m               # ridge half-width in cells
    du = np.abs((u % period) - period / 2) - (period / 2 - w)
    dv = np.abs((v % period) - period / 2) - (period / 2 - w)
    ridge = (du > 0) | (dv > 0)
    ridge &= ~(_smooth_noise(n, rng, 5 / cell_m) > 0.3)          # openings in the network
    ridge_h = np.clip(1.2 + 0.5 * _smooth_noise(n, rng, 10 / cell_m), 0.4, 2.0)  # 0.4-2 m
    height = gaussian_filter(np.where(ridge, ridge_h, 0.0), 0.8)
    base = 0.04 * xx * cell_m + 1.5 * _smooth_noise(n, rng, 40 / cell_m)          # tilt + undulation
    dem = base + height
    rocks = np.zeros((n, n), bool)
    for _ in range(int(n * n * 0.0006)):
        r, c = rng.integers(0, n, 2)
        rocks[r:r + 2, c:c + 2] = True
    sand = ~ridge & ~rocks
    return dem, ridge, sand, rocks


def load_ortho(ortho_path, dtm_path, window_rect):
    """Orthoimage over the SAME ground area as the DTM window, resampled to the DTM grid (cell for cell). nan = no data."""
    import rasterio
    from rasterio.windows import Window, from_bounds
    col, row, w, h = window_rect
    with rasterio.open(dtm_path) as d:
        bounds = d.window_bounds(Window(col, row, w, h))
    with rasterio.open(ortho_path) as o:
        img = o.read(1, window=from_bounds(*bounds, transform=o.transform), boundless=True,
                     fill_value=0, out_shape=(h, w)).astype("float64")
    img[img <= 0] = np.nan
    return img


def ortho_masks(img, p):
    """Boxwork proxies from orthoimage brightness: (ridge, hollow, zone).
    hollow = dark, COMPACT blobs (size and elongation limited); ridge = light-toned fragments inside the lattice zone;
    zone = where compact hollows are dense (the lattice), away from bright bluff areas.
    p is the params module. These are PROXIES: brightness reflects material, shadow and illumination, not elevation.
    Tuned on a screenshot of the real 3300/10450 window only; re-check 4_ortho_masks.png on the real data."""
    from scipy.ndimage import gaussian_filter, label, find_objects, binary_fill_holes
    valid = np.isfinite(img)
    x = np.where(valid, img, np.nanmedian(img) if valid.any() else 0.0)
    lo, hi = np.percentile(x, [2, 98]); x = np.clip((x - lo) / max(hi - lo, 1e-9), 0, 1)
    c = gaussian_filter(x, p.ORTHO_SMOOTH_CELLS) - gaussian_filter(x, p.ORTHO_LOCAL_CELLS)
    sig = np.sqrt(gaussian_filter(c ** 2, p.ORTHO_LOCAL_CELLS)) + 1e-9
    dark = (c < -p.ORTHO_K * sig) & (c < -p.ORTHO_MIN_CONTRAST)
    light = (c > p.ORTHO_K * sig) & (c > p.ORTHO_MIN_CONTRAST)
    lab, n = label(dark, structure=np.ones((3, 3))); area = np.bincount(lab.ravel(), minlength=n + 1)
    keep = np.zeros(n + 1, bool)
    for i, sx in enumerate(find_objects(lab), 1):
        h, w = sx[0].stop - sx[0].start, sx[1].stop - sx[1].start
        keep[i] = (p.ORTHO_HOLLOW_MIN_CELLS <= area[i] <= p.ORTHO_HOLLOW_MAX_CELLS
                   and max(h, w) / max(1, min(h, w)) <= p.ORTHO_HOLLOW_MAX_ASPECT)
    compact = keep[lab]
    dens = gaussian_filter(compact.astype("float64"), p.ORTHO_ZONE_CELLS)
    zone = binary_fill_holes(dens > p.ORTHO_ZONE_REL * np.percentile(dens, 97)) & valid
    lz, nz = label(zone)
    if nz:
        size = np.bincount(lz.ravel(), minlength=nz + 1)
        bright = np.bincount(lz.ravel(), weights=x.ravel(), minlength=nz + 1) / np.maximum(size, 1)
        ok = (size >= p.ORTHO_ZONE_MIN_FRACTION * zone.size) & (bright <= p.ORTHO_ZONE_MAX_BRIGHTNESS); ok[0] = False
        zone = ok[lz]
    lr, nr = label(light & zone, structure=np.ones((3, 3)))
    kr = np.bincount(lr.ravel(), minlength=nr + 1) >= p.ORTHO_MIN_RIDGE_CELLS; kr[0] = False
    return kr[lr], compact & zone, zone


def synthetic_ortho(shape, seed=3):
    """TEST ONLY: fake orthoimage with a lattice patch (light ridges, dark hollows) in a rectangle, to exercise the mask and stop logic."""
    rng = np.random.default_rng(seed); h, w = shape
    r, c = np.indices(shape)
    img = 0.5 + 0.15 * np.sin(c / 90.0) + 0.05 * rng.normal(size=shape)
    zone = (r > 0.30 * h) & (r < 0.85 * h) & (c > 0.45 * w) & (c < 0.80 * w)
    u, v = (r + 0.3 * c) % 18, (c - 0.2 * r) % 18
    lattice = ((u < 3) | (v < 3)).astype(float)
    img = np.where(zone, 0.25 + 0.55 * lattice + 0.05 * rng.normal(size=shape), img)
    return np.clip(img, 0.01, 1.0)
