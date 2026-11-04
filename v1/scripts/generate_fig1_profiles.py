#!/usr/bin/env python3
"""
generate_fig1_profiles.py
Milestone M2: Simulation Script for Figure 1.

Figure 1: Radial intensity profiles and physical unfeasibility divergence:
(a) Radial intensity profiles I(r) for various w0 in [1.0, 0.5, 0.2, 0.1, 0.05, 0.02] mm (r0 = 1.0 mm, P = 1.0 W).
(b) Peak intensity divergence I_max vs 1/w0 (log-log scale), confirming 1/w0 scaling and comparison
    with dielectric air breakdown threshold.
(c) Topological radial shift Delta r_l vs l for multiple w0, comparing exact peak maximization
    against the analytical formula Delta r_l = (4l^2 - 1) w0^2 / (32 r0).

Author: Sebastián Ayala (Cauquenes, Chile)
Paper: Overcomplete Perfect Vortex Beams
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ive
from scipy.optimize import minimize_scalar

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Publication styling settings
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "figure.titlesize": 12,
    "lines.linewidth": 1.6,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "mathtext.fontset": "cm",
})


def calculate_pvb_intensity(r: np.ndarray, r0: float, w0: float, l: int = 1, P: float = 1.0) -> np.ndarray:
    r"""
    Computes exact physical PVB radial intensity I(r) normalized to total power P:
    P = 2*pi * \int_0^\infty r I(r) dr = 1.0 W.
    Using exponentially scaled modified Bessel function ive(l, z) to prevent numerical overflow:
    ive(l, z) = I_l(z) * exp(-z).
    """
    # Exact radial norm squared integral from Gradshteyn & Ryzhik 6.633.2:
    # \int_0^\infty r e^{-2(r^2+r0^2)/w0^2} I_l(2 r0 r / w0^2)^2 dr = (w0^2 / 4) * exp(-r0^2/w0^2) * I_l(r0^2/w0^2)
    norm_factor = 2.0 * np.pi * (w0**2 / 4.0) * float(ive(l, r0**2 / w0**2))
    
    # Field amplitude: exp(-(r - r0)^2 / w0^2) * ive(l, 2 r0 r / w0^2)
    arg = 2.0 * r0 * r / (w0**2)
    u_r = np.exp(-((r - r0)**2) / (w0**2)) * ive(l, arg)
    intensity = (P / norm_factor) * (u_r**2)
    return intensity


def find_topological_peak(r0: float, w0: float, l: int) -> float:
    """Finds exact peak radius r_peak = argmax I_l(r) using bounded scalar minimization."""
    def neg_field(r_val):
        arg = 2.0 * r0 * r_val / (w0**2)
        return -(np.exp(-((r_val - r0)**2) / (w0**2)) * ive(l, arg))**2

    # Bracket search around r0
    search_min = max(1e-4, r0 - 2.0 * w0)
    search_max = r0 + 3.0 * w0
    res = minimize_scalar(neg_field, bounds=(search_min, search_max), method="bounded")
    return float(res.x)


def generate_figure_1(output_path: Path = None):
    """Generates publication-quality 3-panel Figure 1."""
    if output_path is None:
        output_path = PROJECT_ROOT / "v1" / "figures" / "fig1_pvb_profiles_divergence.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.5), constrained_layout=True)
    
    # ----------------------------------------------------
    # Panel (a): Radial Intensity Profiles
    # ----------------------------------------------------
    ax_a = axes[0]
    r0 = 1.0  # mm
    P = 1.0   # W
    l_charge = 1
    w0_list = [1.0, 0.5, 0.2, 0.1, 0.05, 0.02]  # mm
    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(w0_list)))

    r_grid = np.linspace(0.0, 2.2, 1000)  # mm

    for w0_val, col in zip(w0_list, colors):
        I_profile = calculate_pvb_intensity(r_grid, r0, w0_val, l=l_charge, P=P)
        ax_a.plot(r_grid, I_profile, label=rf"$w_0 = {w0_val:.2f}$ mm", color=col)

    ax_a.set_xlabel(r"Radial coordinate $r$ [mm]")
    ax_a.set_ylabel(r"Intensity $I(r)$ [$\mathrm{W/mm}^2$]")
    ax_a.set_xlim(0.0, 2.2)
    ax_a.set_ylim(bottom=0.0)
    ax_a.axvline(r0, color="gray", linestyle=":", alpha=0.7, label=r"$r_0 = 1.0$ mm")
    ax_a.legend(loc="upper right", frameon=True, framealpha=0.9)
    ax_a.set_title(r"\textbf{(a)} Annular intensity profiles ($l=1$)")

    # ----------------------------------------------------
    # Panel (b): Peak Intensity Divergence vs 1/w0
    # ----------------------------------------------------
    ax_b = axes[1]
    # w0 spanning from 2 mm down to 10^-5 mm (10 nm)
    w0_sweep = np.logspace(-4.5, 0.3, 200)  # mm
    inv_w0 = 1.0 / w0_sweep                 # mm^-1
    
    # Analytical thin-ring scaling: I_max = P / (pi^(3/2) * sqrt(2) * r0 * w0)
    I_max_analytical = P / ((np.pi**1.5) * np.sqrt(2.0) * r0 * w0_sweep)  # W/mm^2
    
    # Exact peak intensities
    I_max_exact = [calculate_pvb_intensity(np.array([r0]), r0, w, l=l_charge, P=P)[0] for w in w0_sweep]

    ax_b.loglog(inv_w0, I_max_exact, "b-", label=r"Exact $I_{\mathrm{max}}(w_0)$")
    ax_b.loglog(inv_w0, I_max_analytical, "r--", alpha=0.8,
                label=r"Asymptotic $\propto w_0^{-1}$")

    # Dielectric breakdown of air: E_breakdown = 3 MV/m = 3e6 V/m
    # I_breakdown = 0.5 * eps0 * c * E^2 = E^2 / (2 * eta0) where eta0 = 376.73 Ohm
    # I_breakdown ~ 1.2e10 W/m^2 = 1.2e4 W/mm^2
    I_air_breakdown = 1.19e4  # W/mm^2
    ax_b.axhline(I_air_breakdown, color="darkred", linestyle="-.", linewidth=1.5,
                 label=r"Air breakdown ($1.2 \times 10^4\,\mathrm{W/mm}^2$)")

    # Highlight damage zone
    ax_b.fill_between(inv_w0, I_air_breakdown, 1e9, color="red", alpha=0.12)
    ax_b.text(5e1, 3.5e4, "Dielectric Breakdown\n& Plasma Region", color="darkred", fontsize=8.5, weight="bold")

    ax_b.set_xlabel(r"Inverse ring width $1/w_0$ [$\mathrm{mm}^{-1}$]")
    ax_b.set_ylabel(r"Peak Intensity $I_{\mathrm{max}}$ [$\mathrm{W/mm}^2$]")
    ax_b.set_title(r"\textbf{(b)} Peak intensity divergence ($P = 1$ W)")
    ax_b.set_ylim(1e-1, 1e8)
    ax_b.legend(loc="lower right", frameon=True, framealpha=0.9)

    # ----------------------------------------------------
    # Panel (c): Topological Radial Shift Delta r_l vs l
    # ----------------------------------------------------
    ax_c = axes[2]
    l_values = np.arange(0, 11)
    test_w0_vals = [0.20, 0.10, 0.05, 0.02]  # mm
    markers = ["o", "s", "^", "v"]
    shift_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for w0_val, mark, col in zip(test_w0_vals, markers, shift_colors):
        # Numerical peak calculation
        delta_r_num = []
        for l_val in l_values:
            r_pk = find_topological_peak(r0, w0_val, l_val)
            delta_r_num.append((r_pk - r0) * 1e3)  # in micrometers (um)
        
        # Analytical formula: Delta r_l = (4l^2 - 1) * w0^2 / (32 * r0) in um
        delta_r_theory = ((4.0 * (l_values**2) - 1.0) * (w0_val**2) / (32.0 * r0)) * 1e3

        ax_c.plot(l_values, delta_r_num, mark, color=col, markersize=5,
                  label=rf"$w_0 = {w0_val:.2f}$ mm (num)")
        ax_c.plot(l_values, delta_r_theory, "-", color=col, alpha=0.7, linewidth=1.2)

    ax_c.set_xlabel(r"Topological charge $l$")
    ax_c.set_ylabel(r"Radial peak shift $\Delta r_l$ [$\mu\mathrm{m}$]")
    ax_c.set_title(r"\textbf{(c)} Topological radial invariance")
    ax_c.set_xticks(l_values)
    ax_c.legend(loc="upper left", frameon=True, framealpha=0.9)

    # Save high-resolution vector PDF
    fig.savefig(output_path, format="pdf", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Successfully generated Figure 1: {output_path}")


if __name__ == "__main__":
    out_file = PROJECT_ROOT / "v1" / "figures" / "fig1_pvb_profiles_divergence.pdf"
    generate_figure_1(out_file)
