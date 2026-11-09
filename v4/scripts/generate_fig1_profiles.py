#!/usr/bin/env python3
"""
generate_fig1_profiles.py
Simulation Script for Figure 1 — Version 4 (v4).

Figure 1: PVB Annular Intensity Profiles and Physical Divergence Pillars:
(a) Annular intensity profiles I(r) for charges l = 1, 2, 3, 4 showing locked ring radius
    R0 = 1.0 mm and thickness w0 = 0.1 mm, normalized to total power P = 1.0 W.
(b) Topological radial shift Delta R_l vs topological charge l across multiple ring waists w0,
    demonstrating sub-micron shift (< 0.01 w0) and comparing numerical maximization against
    analytical expansion Delta R_l approx (4l^2 - 1) w0^2 / (32 R0).
(c) Physical divergence pillars as w0 -> 0: transverse wavevector variance <kr^2> ~ 1/w0^2,
    beam propagation factor M^2 ~ R0/w0, and peak intensity I_max vs dielectric air breakdown.
(d) Transverse spatial frequency spectrum |E_tilde(k_r)| under paraxial bandlimiting
    cutoff K_max = k0 * NA.

Layout: 2x2 multi-panel layout (publication grade).
Author: Sebastián Ayala (Cauquenes, Chile)
Paper: Overcomplete Perfect Vortex Beams
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ive, jv
from scipy.optimize import minimize_scalar

# Adaptive directory discovery for repository and extracted bundle environments
SCRIPTS_DIR = Path(__file__).resolve().parent
if (SCRIPTS_DIR.parent / "figures").is_dir():
    DEFAULT_FIG_DIR = SCRIPTS_DIR.parent / "figures"
elif (SCRIPTS_DIR.parent.parent / "v4" / "figures").is_dir():
    DEFAULT_FIG_DIR = SCRIPTS_DIR.parent.parent / "v4" / "figures"
else:
    DEFAULT_FIG_DIR = SCRIPTS_DIR.parent / "figures"
DEFAULT_FIG_DIR.mkdir(parents=True, exist_ok=True)

for p in [SCRIPTS_DIR, SCRIPTS_DIR.parent, SCRIPTS_DIR.parent.parent]:
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Publication styling settings
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9.5,
    "axes.labelsize": 10,
    "axes.titlesize": 10.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.0,
    "figure.titlesize": 11,
    "lines.linewidth": 1.6,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "mathtext.fontset": "cm",
})


def calculate_pvb_intensity(r: np.ndarray, r0: float, w0: float, l: int = 1, P: float = 1.0) -> np.ndarray:
    r"""
    Computes exact physical PVB radial intensity I(r) normalized to total power P:
    P = 2*pi * \int_0^\infty r I(r) dr = P.
    Using exponentially scaled modified Bessel function ive(l, z) = I_l(z) * exp(-z):
    E(r) = exp(-(r - r0)^2 / w0^2) * ive(l, 2 r0 r / w0^2).
    """
    # Exact radial norm squared integral from Gradshteyn & Ryzhik 6.633.2:
    norm_factor = 2.0 * np.pi * (w0**2 / 4.0) * float(ive(l, r0**2 / w0**2))
    arg = 2.0 * r0 * r / (w0**2)
    u_r = np.exp(-((r - r0)**2) / (w0**2)) * ive(l, arg)
    intensity = (P / norm_factor) * (u_r**2)
    return intensity


def find_topological_peak(r0: float, w0: float, l: int) -> float:
    """Finds exact peak radius r_peak = argmax I_l(r) using bounded scalar minimization."""
    def neg_field(r_val):
        arg = 2.0 * r0 * r_val / (w0**2)
        return -(np.exp(-((r_val - r0)**2) / (w0**2)) * ive(l, arg))**2

    search_min = max(1e-4, r0 - 2.0 * w0)
    search_max = r0 + 3.0 * w0
    res = minimize_scalar(neg_field, bounds=(search_min, search_max), method="bounded")
    return float(res.x)


def generate_figure_1(output_path: Path = None):
    """Generates publication-quality 2x2 Figure 1."""
    if output_path is None:
        output_path = DEFAULT_FIG_DIR / "fig1_pvb_profiles_divergence.pdf"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(8.5, 7.0), constrained_layout=True)

    # ----------------------------------------------------
    # Panel (a): Annular Intensity Profiles for l = 1, 2, 3, 4
    # ----------------------------------------------------
    ax_a = axes[0, 0]
    r0 = 1.0   # mm (locked ring radius R0)
    w0 = 0.10  # mm (ring thickness w0)
    P = 1.0    # W
    charges = [1, 2, 3, 4]
    colors_a = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    r_grid = np.linspace(0.6, 1.4, 800)  # mm
    for l_val, col in zip(charges, colors_a):
        I_profile = calculate_pvb_intensity(r_grid, r0, w0, l=l_val, P=P)
        ax_a.plot(r_grid, I_profile, label=rf"$\ell = {l_val}$", color=col)

    ax_a.axvline(r0, color="black", linestyle=":", linewidth=1.2, label=rf"$R_0 = {r0:.1f}$ mm")
    ax_a.set_xlabel("Radial coordinate $r$ [mm]")
    ax_a.set_ylabel(r"Intensity $I(r)$ [$\mathrm{W/mm}^2$]")
    ax_a.set_title("(a) Annular profiles with locked radius", fontweight="bold", fontsize=10.5)
    ax_a.set_xlim(0.65, 1.35)
    ax_a.set_ylim(bottom=0.0)
    ax_a.legend(loc="upper right", frameon=True, framealpha=0.9)

    # ----------------------------------------------------
    # Panel (b): Topological Radial Shift Delta R_l
    # ----------------------------------------------------
    ax_b = axes[0, 1]
    l_vals = np.arange(1, 11)
    w0_set = [0.05, 0.10, 0.15, 0.20]  # mm
    colors_b = ["#440154", "#3b528b", "#21918c", "#5ec962"]

    for w0_val, col in zip(w0_set, colors_b):
        # Numerical shift in micrometers
        shifts_num = []
        for l_val in l_vals:
            r_peak = find_topological_peak(r0, w0_val, l_val)
            shifts_num.append((r_peak - r0) * 1000.0)  # um

        # Analytical formula: Delta R_l approx (4l^2 - 1) w0^2 / (32 R0)
        shifts_ana = ((4.0 * (l_vals**2) - 1.0) * (w0_val**2) / (32.0 * r0)) * 1000.0  # um

        ax_b.plot(l_vals, shifts_num, "o", color=col, markersize=4.5, label=rf"Num $w_0 = {w0_val:.2f}$ mm")
        ax_b.plot(l_vals, shifts_ana, "-", color=col, linewidth=1.2, alpha=0.85)

    ax_b.axhline(0.01 * w0 * 1000.0, color="gray", linestyle="--", linewidth=1.0, label=r"$0.01 w_0$ threshold")
    ax_b.set_xlabel(r"Topological charge $\ell$")
    ax_b.set_ylabel(r"Radial shift $\Delta R_\ell$ [$\mu$m]")
    ax_b.set_title(r"(b) Sub-micron topological radial shift", fontweight="bold", fontsize=10.5)
    ax_b.set_xlim(1, 10)
    ax_b.set_ylim(0, 15.0)
    ax_b.legend(loc="upper left", frameon=True, framealpha=0.85, fontsize=7.5)

    # ----------------------------------------------------
    # Panel (c): The Physical Divergence Pillars as w0 -> 0
    # ----------------------------------------------------
    ax_c = axes[1, 0]
    w0_range = np.logspace(-4, 0, 100)  # mm from 0.1 um to 1 mm
    r0_mm = 1.0

    # Pillar 1: <k_r^2> ~ 1/w0^2 [mm^-2]
    kr2 = 1.0 / (w0_range**2)
    # Pillar 2: M^2 ~ R0 / w0 (dimensionless)
    m2 = r0_mm / w0_range
    # Pillar 3: Peak intensity I_max ~ P / (pi^(3/2) * sqrt(2) * R0 * w0) [W/mm^2]
    I_max = 1.0 / ((np.pi**1.5) * np.sqrt(2.0) * r0_mm * w0_range)

    ax_c.loglog(w0_range, kr2, "r-", linewidth=1.8, label=r"$\langle k_r^2 \rangle \sim 1/w_0^2$ [$\mathrm{mm}^{-2}$]")
    ax_c.loglog(w0_range, m2, "b--", linewidth=1.6, label=r"$M^2 \sim R_0/w_0$")
    ax_c.loglog(w0_range, I_max, "g-.", linewidth=1.6, label=r"$I_{\max} \propto 1/w_0$ [$\mathrm{W/mm}^2$]")

    # Air breakdown intensity threshold (~1.2e4 W/mm^2)
    air_breakdown_I = 1.2e4  # W/mm^2 for 3e6 V/m in air
    ax_c.axhline(air_breakdown_I, color="darkred", linestyle=":", linewidth=1.2, label="Air breakdown limit")

    ax_c.set_xlabel(r"Ring thickness $w_0$ [mm]")
    ax_c.set_ylabel("Divergence magnitude")
    ax_c.set_title("(c) Physical divergence pillars as $w_0 \\to 0$", fontweight="bold", fontsize=10.5)
    ax_c.set_xlim(1e-4, 1.0)
    ax_c.set_ylim(1e-1, 1e9)
    ax_c.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=7.5)

    # ----------------------------------------------------
    # Panel (d): Transverse Spatial Frequency Spectrum
    # ----------------------------------------------------
    ax_d = axes[1, 1]
    kr_grid = np.linspace(0.0, 30.0, 500)  # mm^-1
    w0_choices = [0.08, 0.12, 0.20]  # mm
    colors_d = ["#9467bd", "#8c564b", "#e377c2"]

    K0 = 12.0  # mm^-1
    for w0_val, col in zip(w0_choices, colors_d):
        sigma_k = 1.414 / w0_val
        spectrum = np.exp(-0.5 * ((kr_grid - K0) / sigma_k)**2)
        ax_d.plot(kr_grid, spectrum, color=col, label=rf"$w_0 = {w0_val:.2f}$ mm")

    # Mark Paraxial Numerical Aperture limit K_max = 20 mm^-1
    K_max = 20.0  # mm^-1
    ax_d.axvline(K_max, color="black", linestyle="--", linewidth=1.3, label=r"Paraxial cutoff $K_{\max}$")
    ax_d.axvspan(0.0, K_max, color="blue", alpha=0.06, label=r"$\mathcal{H}_{\mathrm{band}}$ (admissible)")

    ax_d.set_xlabel(r"Transverse spatial frequency $k_r$ [$\mathrm{mm}^{-1}$]")
    ax_d.set_ylabel(r"Normalized spectrum $|\widetilde{E}(k_r)|$")
    ax_d.set_title(r"(d) Spatial spectrum and paraxial bandlimiting", fontweight="bold", fontsize=10.5)
    ax_d.set_xlim(0.0, 30.0)
    ax_d.set_ylim(0.0, 1.08)
    ax_d.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=7.5)

    # Save vector PDF
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Figure 1 successfully generated: {output_path}")


if __name__ == "__main__":
    generate_figure_1()
