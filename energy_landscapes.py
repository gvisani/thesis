"""
Three energy-landscape figures styled after the classic funnel diagram.
Color palette: blue (low energy) → cyan → green → yellow → orange → red (high energy).
Transparent background, no axes or labels.

Landscapes:
  1. landscape_single_min.png  – rugged terrain with one deep Gaussian well
  2. landscape_double_min.png  – rugged terrain with two deep Gaussian wells
  3. landscape_rugged.png      – pure rugged terrain, no clear minimum
"""

import numpy as np
import matplotlib.pyplot as plt


# ── Grid helper ───────────────────────────────────────────────────────────────

def _grid(lim=3.0, n=600):
    x = np.linspace(-lim, lim, n)
    X, Y = np.meshgrid(x, x)
    return X, Y


# ── Landscape generators ──────────────────────────────────────────────────────

def landscape_single_minimum(lim=3.0, n=600, noise_amp=1.2,
                              well_depth=3.8, well_sigma=0.8, seed=0):
    """Rugged landscape with one deep Gaussian well at centre."""
    X, Y = _grid(lim, n)
    rng = np.random.default_rng(seed)
    Z = np.zeros_like(X)
    for freq in [1.4, 2.0, 2.7, 3.5, 4.3, 5.2, 6.1]:
        px, py = rng.uniform(0, 2 * np.pi, 2)
        Z += (noise_amp / freq) * np.sin(freq * X + px) * np.cos(freq * Y + py)

    R = np.sqrt(X**2 + Y**2)
    Z -= well_depth * np.exp(-R**2 / (2 * well_sigma**2))

    Z -= Z.min()
    return X, Y, Z


def landscape_double_minimum(lim=3.0, n=600, noise_amp=1.2,
                              well_depth=3.3, well_sigma=0.8, seed=1):
    """Rugged landscape with two deep Gaussian wells, slightly offset from each other."""
    X, Y = _grid(lim, n)
    rng = np.random.default_rng(seed)
    Z = np.zeros_like(X)
    for freq in [1.4, 2.0, 2.7, 3.5, 4.3, 5.2, 6.1]:
        px, py = rng.uniform(0, 2 * np.pi, 2)
        Z += (noise_amp / freq) * np.sin(freq * X + px) * np.cos(freq * Y + py)

    # Wells perpendicular to camera azimuth -55° so both are visible side-by-side
    ox, oy = 1.0, 0.6
    R1 = np.sqrt((X - ox)**2 + (Y - oy)**2)
    R2 = np.sqrt((X + ox)**2 + (Y + oy)**2)
    Z -= well_depth * (np.exp(-R1**2 / (2 * well_sigma**2)) +
                       np.exp(-R2**2 / (2 * well_sigma**2)))

    Z -= Z.min()
    return X, Y, Z


def landscape_rugged(lim=3.0, n=600, noise_amp=1.2, seed=2):
    """Multi-scale bumps; no funnel — color_floor in render pushes it into warm zone."""
    X, Y = _grid(lim, n)
    rng = np.random.default_rng(seed)
    Z = np.zeros_like(X)
    for freq in [1.4, 2.0, 2.7, 3.5, 4.3, 5.2, 6.1]:
        px, py = rng.uniform(0, 2 * np.pi, 2)
        Z += (noise_amp / freq) * np.sin(freq * X + px) * np.cos(freq * Y + py)
    Z -= Z.min()
    return X, Y, Z


# ── Renderer ──────────────────────────────────────────────────────────────────

def _vmin_for_floor(zmin, zmax, color_floor):
    if color_floor == 0.0:
        return zmin
    return (zmin - color_floor * zmax) / (1.0 - color_floor)


def render(X, Y, Z, filename,
           color_floor=0.0, z_stretch=1.0,
           cmap="jet", elev=26, azim=-55, dpi=220, figsize=(7, 7)):
    fig = plt.figure(figsize=figsize, facecolor="none")
    ax  = fig.add_subplot(111, projection="3d", facecolor="none")

    zmin = float(np.nanmin(Z))
    zmax = float(np.nanmax(Z))
    ax.plot_surface(X, Y, Z, cmap=cmap,
                    vmin=_vmin_for_floor(zmin, zmax, color_floor),
                    vmax=zmax,
                    linewidth=0, antialiased=True, shade=True)

    ax.set_axis_off()
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("none")
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.line.set_color("none")

    xy_span = float(X.max() - X.min())
    z_span  = zmax - zmin
    ax.set_box_aspect([1, 1, z_stretch * z_span / xy_span])
    ax.view_init(elev=elev, azim=azim)

    stem = filename.rsplit(".", 1)[0]
    fig.savefig(f"{stem}.png", dpi=dpi,  transparent=True, bbox_inches="tight", pad_inches=0)
    fig.savefig(f"{stem}.svg", transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"saved  {stem}.png / .svg")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    render(*landscape_single_minimum(), "landscape_single_min.png")
    render(*landscape_double_minimum(), "landscape_double_min.png")
    render(*landscape_rugged(),          "landscape_rugged.png", color_floor=0.58)
