import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

def _base(ax, dem, cell_m):
    ls = LightSource(azdeg=315, altdeg=40)
    ax.imshow(ls.hillshade(np.nan_to_num(dem), vert_exag=2, dx=cell_m, dy=cell_m), cmap="gray")
    ax.set_xticks([]); ax.set_yticks([])

def plot_layers(dem, ridge, rocks, slope, out, cell_m=1.0):
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    _base(axs[0], dem, cell_m); axs[0].set_title("Terrain (hillshade)")
    axs[1].imshow(slope, cmap="magma"); axs[1].set_title("Slope (deg)")
    ov = np.zeros(dem.shape + (3,)); ov[ridge] = (0.9, 0.5, 0.1); ov[rocks] = (0.2, 0.6, 1.0)
    axs[2].imshow(ov); axs[2].set_title("Obstacles: ridges (orange), rocks (blue)")
    for a in axs: a.set_xticks([]); a.set_yticks([])
    fig.tight_layout(); fig.savefig(out, dpi=110); plt.close(fig)

def plot_cost(cost_a, cost_r, out):
    fig, axs = plt.subplots(1, 2, figsize=(11, 5))
    for ax, c, t in ((axs[0], cost_a, "Astronaut cost"), (axs[1], cost_r, "Rover cost")):
        m = np.ma.masked_invalid(np.where(np.isinf(c), np.nan, c))
        ax.imshow(m, cmap="viridis"); ax.set_title(t + " (white = blocked)")
        ax.set_facecolor("white"); ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout(); fig.savefig(out, dpi=110); plt.close(fig)

def plot_routes(dem, cell_m, astro, rover, stops, hab, abort_m, out, title="Crew & Rover Marswalk: Mount Sharp Boxwork (Gale Crater)"):
    fig, ax = plt.subplots(figsize=(8, 8)); _base(ax, dem, cell_m)
    if rover: ax.plot(*zip(*[(c, r) for r, c in rover]), "c-", lw=2.2, label="rover (Nav2-style cost)")
    if astro: ax.plot(*zip(*[(c, r) for r, c in astro]), "y-", lw=2.2, label="astronaut")
    ax.scatter([c for r, c in stops], [r for r, c in stops], c="lime", s=70, marker="*", label="science stops", zorder=5)
    ax.scatter([hab[1]], [hab[0]], c="red", s=90, marker="s", label="habitat / rover start", zorder=5)
    ax.add_patch(plt.Circle((hab[1], hab[0]), abort_m / cell_m, fill=False, ls="--", ec="red", label="abort radius"))
    ax.set_xlim(0, dem.shape[1]); ax.set_ylim(dem.shape[0], 0)
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title(title)
    fig.tight_layout(); fig.savefig(out, dpi=110); plt.close(fig)


def plot_ortho_masks(img, ridge, hollow, zone, out, cell_m=1.0):
    """Check overlay for the orthoimage-derived masks: ridges orange, hollows blue, lattice zone outline yellow."""
    import numpy as np
    fig, axs = plt.subplots(1, 2, figsize=(14, 7))
    lo, hi = (np.nanpercentile(img, [2, 98]) if np.isfinite(img).any() else (0, 1))
    for ax in axs: ax.imshow(img, cmap="gray", vmin=lo, vmax=hi); ax.axis("off")
    axs[0].set_title("Orthoimage (window)")
    ov = np.zeros(img.shape + (4,)); ov[ridge] = (1, 0.5, 0, 0.8); ov[hollow] = (0.1, 0.4, 1, 0.8)
    axs[1].imshow(ov); axs[1].contour(zone, levels=[0.5], colors="yellow", linewidths=1)
    axs[1].set_title("Ridge (orange) / hollow (blue) from brightness: a PROXY, not elevation; yellow = lattice zone")
    plt.tight_layout(); plt.savefig(out, dpi=110); plt.close(fig)
