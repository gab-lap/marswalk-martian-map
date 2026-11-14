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
