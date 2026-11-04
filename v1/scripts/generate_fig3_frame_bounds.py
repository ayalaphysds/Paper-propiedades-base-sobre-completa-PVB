#!/usr/bin/env python3
"""
generate_fig3_frame_bounds.py
Milestone M2: Simulation Script for Figure 3.

Figure 3: Continuous frame operator spectrum, Duffin-Schaeffer bounds, and discrete Gram matrix:
(a) Continuous spectrum sigma(k_r) = exp(-1/2 * k_r^2 * w0^2) vs spatial frequency k_r,
    highlighting the paraxial bandlimited cutoff K_max.
(b) Duffin-Schaeffer frame bounds A = exp(-1/2 * K_max^2 * w0^2), B = 1.0, and condition number
    kappa = B / A vs optical numerical aperture NA in [0.01, 0.15] (lambda = 1550 nm).
(c) Singular value spectrum of concentric discrete multi-ring Gram matrix G_ij = gamma_l(r_i, r_j; w0)
    for M = 12 concentric multiplexed rings across various channel separations Delta r / w0.

Author: Sebastián Ayala (Cauquenes, Chile)
Paper: Overcomplete Perfect Vortex Beams
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ive

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


def calculate_exact_overlap(r1: float, r2: float, w0: float, l: int = 1) -> float:
    """Exact overlap between two PVB rings."""
    arg12 = (r1 * r2) / (w0**2)
    arg11 = (r1**2) / (w0**2)
    arg22 = (r2**2) / (w0**2)

    exp_factor = np.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
    ive_12 = ive(l, arg12)
    ive_11 = ive(l, arg11)
    ive_22 = ive(l, arg22)

    den = np.sqrt(ive_11 * ive_22)
    if den <= 0.0:
        return float(exp_factor)
    return float(np.clip(exp_factor * (ive_12 / den), 0.0, 1.0))


def generate_figure_3(output_path: Path = None):
    """Generates publication-quality 3-panel Figure 3."""
    if output_path is None:
        output_path = PROJECT_ROOT / "v1" / "figures" / "fig3_frame_spectrum_bounds.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.6), constrained_layout=True)

    # ----------------------------------------------------
    # Panel (a): Continuous Frame Spectrum vs Spatial Frequency
    # ----------------------------------------------------
    ax_a = axes[0]
    # Spatial frequency kr in [0, 25] mm^-1
    kr_vals = np.linspace(0.0, 25.0, 300)  # mm^-1
    w0_cases = [0.05, 0.10, 0.15, 0.20]   # mm
    colors_a = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]

    for w0_val, col in zip(w0_cases, colors_a):
        # Continuous eigenvalue spectrum: sigma(kr) = exp(-1/2 * (kr * w0)^2)
        spectrum = np.exp(-0.5 * (kr_vals * w0_val)**2)
        ax_a.plot(kr_vals, spectrum, "-", color=col, label=rf"$w_0 = {w0_val:.2f}$ mm")

    # Mark representative paraxial cut K_max = 10 mm^-1
    K_cut = 10.0  # mm^-1
    ax_a.axvline(K_cut, color="gray", linestyle=":", linewidth=1.5, label=r"$K_{\mathrm{max}} = 10\,\mathrm{mm}^{-1}$")
    ax_a.axvspan(0.0, K_cut, color="green", alpha=0.07, label=r"$\mathcal{H}_{\mathrm{band}}$ (paraxial)")

    ax_a.set_xlabel(r"Transverse spatial frequency $k_r$ [$\mathrm{mm}^{-1}$]")
    ax_a.set_ylabel(r"Frame spectrum $\sigma(k_r)$")
    ax_a.set_title(r"\textbf{(a)} Continuous frame spectrum")
    ax_a.set_xlim(0.0, 25.0)
    ax_a.set_ylim(0.0, 1.05)
    ax_a.legend(loc="upper right", frameon=True, framealpha=0.9)

    # ----------------------------------------------------
    # Panel (b): Frame Bounds A, B and Condition Number kappa vs NA
    # ----------------------------------------------------
    ax_b = axes[1]
    lambda_opt = 1.55e-3  # mm (1550 nm)
    k0 = 2.0 * np.pi / lambda_opt  # mm^-1
    NA_vals = np.linspace(0.01, 0.15, 200)

    # Micro-waists for high-NA fiber / waveguide regime
    w0_micro = [1.0e-3, 2.0e-3, 3.0e-3]  # mm (1 um, 2 um, 3 um)
    micro_labels = [r"$w_0 = 1.0\,\mu\mathrm{m}$", r"$w_0 = 2.0\,\mu\mathrm{m}$", r"$w_0 = 3.0\,\mu\mathrm{m}$"]
    colors_b = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for w_m, lbl, col in zip(w0_micro, micro_labels, colors_b):
        K_max_arr = k0 * NA_vals
        # Frame bound A = exp(-1/2 * (K_max * w_m)^2)
        A_arr = np.exp(-0.5 * (K_max_arr * w_m)**2)
        kappa_arr = 1.0 / A_arr  # B = 1.0, so kappa = B / A = 1 / A

        ax_b.plot(NA_vals, kappa_arr, "-", color=col, label=lbl)

    ax_b.set_xlabel(r"Numerical aperture $\mathrm{NA}$")
    ax_b.set_ylabel(r"Condition number $\kappa = B / A$")
    ax_b.set_title(r"\textbf{(b)} Frame condition number ($\lambda = 1550$ nm)")
    ax_b.set_xlim(0.01, 0.15)
    ax_b.set_ylim(1.0, 6.5)
    ax_b.legend(loc="upper left", frameon=True, framealpha=0.9)

    # ----------------------------------------------------
    # Panel (c): Concentric Discrete Multi-Ring Gram Matrix Singular Values
    # ----------------------------------------------------
    ax_c = axes[2]
    M_rings = 12
    r_center = 1.0  # mm
    w0_c = 0.10     # mm
    l_charge = 1

    # Vary channel separation Delta r / w0 in [0.5, 0.75, 1.0, 1.5]
    sep_ratios = [0.5, 0.75, 1.0, 1.5]
    colors_c = ["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4"]
    markers_c = ["o", "s", "^", "D"]

    for ratio, col, mark in zip(sep_ratios, colors_c, markers_c):
        delta_r = ratio * w0_c
        ring_radii = r_center + (np.arange(M_rings) - (M_rings - 1) / 2.0) * delta_r

        # Assemble M x M Gram matrix
        G = np.zeros((M_rings, M_rings))
        for i in range(M_rings):
            for j in range(M_rings):
                G[i, j] = calculate_exact_overlap(ring_radii[i], ring_radii[j], w0_c, l=l_charge)

        # Compute singular values (ordered descending)
        s = np.linalg.svd(G, compute_uv=False)
        kappa_M = s[0] / s[-1]

        mode_indices = np.arange(1, M_rings + 1)
        ax_c.semilogy(mode_indices, s, marker=mark, color=col, markersize=5,
                      label=rf"$\Delta r = {ratio} w_0$ ($\kappa = {kappa_M:.1f}$)")

    ax_c.set_xlabel(r"Singular value index $m$")
    ax_c.set_ylabel(r"Singular value $s_m$")
    ax_c.set_title(r"\textbf{(c)} Discrete multi-ring Gram spectrum ($M=12$)")
    ax_c.set_xticks(np.arange(1, M_rings + 1))
    ax_c.set_ylim(1e-4, 5.0)
    ax_c.legend(loc="lower left", frameon=True, framealpha=0.9)

    # Save high-resolution vector PDF
    fig.savefig(output_path, format="pdf", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Successfully generated Figure 3: {output_path}")


if __name__ == "__main__":
    out_file = PROJECT_ROOT / "v1" / "figures" / "fig3_frame_spectrum_bounds.pdf"
    generate_figure_3(out_file)
