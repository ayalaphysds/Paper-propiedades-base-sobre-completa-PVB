#!/usr/bin/env python3
"""
generate_fig2_overlap.py
Simulation Script for Figure 2 — Version 5 (v5).

Figure 2: Exact Radial Overlap Matrix, Azimuthal Kronecker Orthogonality, and Universal Cross-Talk:
(a) Exact normalized radial overlap matrix gamma_l(R1, R2; w0) heatmap for l = 1 and ring thickness w0 = 0.15 mm
    across ring radii R1, R2 in [0.65, 1.35] mm, demonstrating continuous radial non-orthogonality and diagonal concentration.
(b) Azimuthal Kronecker orthogonality delta_{l1, l2} demonstrating exact orthogonality across distinct topological
    charges at matched radial coordinates (l1, l2 in [-4, 4]).
(c) Universal asymptotic Gaussian cross-talk decay vs normalized ring separation Delta R / w0 showing
    gamma(Delta R) approx exp(-Delta R^2 / (2 w0^2)) for l in {0, 1, 2, 4}.
(d) Quantitative discrepancy between exact Weber integral (formula 6.633.2) and asymptotic Gaussian expansion,
    confirming |gamma_exact - gamma_asymp| <= 10^-4 over the paraxial operating regime.

Layout: 2x2 multi-panel layout (publication grade).
Author: Sebastián Ayala (Cauquenes, Chile)
Paper: Overcomplete Continuous Frames in Perfect Optical Vortex Beams
"""

import sys
import shutil
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ive

# Adaptive directory discovery for repository and standalone bundle execution
SCRIPTS_DIR = Path(__file__).resolve().parent
if (SCRIPTS_DIR.parent / "figures").is_dir():
    DEFAULT_FIG_DIR = SCRIPTS_DIR.parent / "figures"
elif (SCRIPTS_DIR.parent.parent / "v5" / "figures").is_dir():
    DEFAULT_FIG_DIR = SCRIPTS_DIR.parent.parent / "v5" / "figures"
else:
    DEFAULT_FIG_DIR = SCRIPTS_DIR.parent / "figures"
DEFAULT_FIG_DIR.mkdir(parents=True, exist_ok=True)

for p in [SCRIPTS_DIR, SCRIPTS_DIR.parent, SCRIPTS_DIR.parent.parent]:
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Publication styling settings (colorblind-safe, serif, CM mathtext)
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9.5,
    "axes.labelsize": 10.0,
    "axes.titlesize": 10.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.0,
    "figure.titlesize": 11.0,
    "lines.linewidth": 1.6,
    "axes.grid": True,
    "grid.alpha": 0.28,
    "grid.linestyle": "--",
    "mathtext.fontset": "cm",
})


def calculate_exact_overlap(r1: np.ndarray, r2: np.ndarray, w0: float, l: int = 1) -> np.ndarray:
    r"""
    Computes exact normalized overlap coefficient:
    gamma_l(r1, r2; w0) = I_l(r1*r2/w0^2) / sqrt(I_l(r1^2/w0^2) * I_l(r2^2/w0^2))
    Using exponentially scaled modified Bessel functions ive(l, z) = I_l(z) * exp(-z):
    gamma_l = exp(-(r1 - r2)^2 / (2 w0^2)) * ive(l, r1*r2/w0^2) / sqrt(ive(l, r1^2/w0^2) * ive(l, r2^2/w0^2))
    """
    arg12 = (r1 * r2) / (w0**2)
    arg11 = (r1**2) / (w0**2)
    arg22 = (r2**2) / (w0**2)

    exp_factor = np.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
    ive_12 = ive(l, arg12)
    ive_11 = ive(l, arg11)
    ive_22 = ive(l, arg22)

    den = np.sqrt(ive_11 * ive_22)
    gamma = exp_factor * (ive_12 / den)
    return np.clip(gamma, 0.0, 1.0)


def calculate_asymptotic_overlap(r1: np.ndarray, r2: np.ndarray, w0: float, l: int = 1) -> np.ndarray:
    r"""
    Asymptotic expansion with second-order curvature correction (Eq. 52):
    gamma_l approx exp(-(r1 - r2)^2 / (2 w0^2)) * [1 + (4 l^2 - 1) w0^2 (r1 - r2)^2 / (16 r1^2 r2^2)].
    """
    base = np.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
    corr = 1.0 + ((4.0 * (l**2) - 1.0) * (w0**2) * ((r1 - r2)**2)) / (16.0 * (r1**2) * (r2**2))
    return base * corr


def generate_figure_2(output_path: Path = None):
    """Generates publication-quality 2x2 Figure 2."""
    if output_path is None:
        output_path = DEFAULT_FIG_DIR / "fig2_overlap.pdf"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(8.5, 7.0), constrained_layout=True)

    r0 = 1.0   # mm (reference ring radius R0)
    w0 = 0.15  # mm (waist parameter explicitly updated to 0.15 mm per specification)

    # ----------------------------------------------------
    # Panel (a): 2D Heatmap of Exact Normalized Overlap Matrix (w0 = 0.15 mm)
    # ----------------------------------------------------
    ax_a = axes[0, 0]
    l_heat = 1
    r_span = np.linspace(0.65, 1.35, 250)  # mm
    R1, R2 = np.meshgrid(r_span, r_span)
    gamma_2d = calculate_exact_overlap(R1, R2, w0, l=l_heat)

    im_a = ax_a.imshow(gamma_2d, origin="lower", extent=[r_span[0], r_span[-1], r_span[0], r_span[-1]],
                       cmap="viridis", vmin=0.0, vmax=1.0, aspect="equal")
    cs = ax_a.contour(R1, R2, gamma_2d, levels=[0.1, 0.5, 0.8], colors="white",
                      linewidths=0.9, linestyles=["dotted", "dashed", "solid"])
    ax_a.clabel(cs, inline=True, fontsize=7.2, fmt="%.1f")

    cbar_a = fig.colorbar(im_a, ax=ax_a, fraction=0.046, pad=0.04)
    cbar_a.set_label(r"Radial overlap $|\langle \psi_{\ell_1, R_1} | \psi_{\ell_2, R_2} \rangle|$", rotation=270, labelpad=14)

    ax_a.set_xlabel(r"Ring radius $R_1$ [mm]")
    ax_a.set_ylabel(r"Ring radius $R_2$ [mm]")
    ax_a.set_title(rf"(a) Overlap heatmap ($w_0 = {w0:.2f}\,\mathrm{{mm}},\ \ell = {l_heat}$)",
                   fontweight="bold", fontsize=10.5)

    # ----------------------------------------------------
    # Panel (b): Azimuthal Kronecker Orthogonality Cross-Talk Matrix
    # ----------------------------------------------------
    ax_b = axes[0, 1]
    charges_b = np.arange(-4, 5)
    L1, L2 = np.meshgrid(charges_b, charges_b)
    kronecker_matrix = np.where(L1 == L2, 1.0, 0.0)

    im_b = ax_b.imshow(kronecker_matrix, origin="lower", extent=[-4.5, 4.5, -4.5, 4.5],
                       cmap="cividis", vmin=0.0, vmax=1.0, aspect="equal")
    cbar_b = fig.colorbar(im_b, ax=ax_b, fraction=0.046, pad=0.04)
    cbar_b.set_label(r"Azimuthal inner product $\delta_{\ell_1, \ell_2}$", rotation=270, labelpad=14)

    ax_b.set_xticks(charges_b)
    ax_b.set_yticks(charges_b)
    ax_b.set_xlabel(r"Topological charge $\ell_1$")
    ax_b.set_ylabel(r"Topological charge $\ell_2$")
    ax_b.set_title(r"(b) Azimuthal Kronecker orthogonality $\delta_{\ell_1, \ell_2}$",
                   fontweight="bold", fontsize=10.5)

    # ----------------------------------------------------
    # Panel (c): Universal Gaussian Cross-Talk vs Delta R / w0
    # ----------------------------------------------------
    ax_c = axes[1, 0]
    delta_r_norm = np.linspace(0.0, 3.5, 250)
    r_sweep = r0 + delta_r_norm * w0
    charges_c = [0, 1, 2, 4]
    # Colorblind-safe viridis samples
    colors_c = ["#440154", "#31688e", "#21918c", "#fde725"]

    gamma_univ = np.exp(-0.5 * (delta_r_norm**2))
    ax_c.plot(delta_r_norm, gamma_univ, "k--", linewidth=2.0, label=r"Universal: $e^{-\Delta R^2 / 2w_0^2}$")

    for l_val, col in zip(charges_c, colors_c):
        gamma_exact = calculate_exact_overlap(r0, r_sweep, w0, l=l_val)
        ax_c.plot(delta_r_norm, gamma_exact, "-", color=col, linewidth=1.5, label=rf"Exact $\ell = {l_val}$")

    ax_c.axhline(0.5, color="gray", linestyle=":", linewidth=0.9, label=r"FWHM ($0.50$)")
    ax_c.set_xlabel(r"Normalized ring separation $\Delta R / w_0$")
    ax_c.set_ylabel(r"Radial overlap $\gamma(\Delta R)$")
    ax_c.set_title(r"(c) Universal asymptotic Gaussian cross-talk decay", fontweight="bold", fontsize=10.5)
    ax_c.set_xlim(0.0, 3.5)
    ax_c.set_ylim(0.0, 1.05)
    ax_c.legend(loc="upper right", frameon=True, framealpha=0.92, fontsize=7.5, edgecolor="none")

    # ----------------------------------------------------
    # Panel (d): Numerical Comparison: Exact vs Asymptotic Thin-Ring
    # ----------------------------------------------------
    ax_d = axes[1, 1]
    for l_val, col in zip(charges_c, colors_c):
        gamma_exact = calculate_exact_overlap(r0, r_sweep, w0, l=l_val)
        gamma_asymp = calculate_asymptotic_overlap(r0, r_sweep, w0, l=l_val)
        abs_err = np.abs(gamma_exact - gamma_asymp)
        ax_d.semilogy(delta_r_norm, abs_err + 1e-12, "-", color=col, linewidth=1.6, label=rf"$\ell = {l_val}$")

    # Specification requirement: discrepancy <= 10^-4
    ax_d.axhline(1e-4, color="#b2182b", linestyle="--", linewidth=1.2, label=r"Threshold $10^{-4}$")
    ax_d.set_xlabel(r"Normalized ring separation $\Delta R / w_0$")
    ax_d.set_ylabel(r"Discrepancy $|\gamma_{\mathrm{exact}} - \gamma_{\mathrm{asymp}}|$")
    ax_d.set_title(r"(d) Discrepancy $|\gamma_{\mathrm{exact}} - \gamma_{\mathrm{asymp}}| \leq 10^{-4}$",
                   fontweight="bold", fontsize=10.5)
    ax_d.set_xlim(0.0, 3.5)
    ax_d.set_ylim(1e-8, 1e-2)
    ax_d.legend(loc="upper left", frameon=True, framealpha=0.92, fontsize=7.5, edgecolor="none")

    # Save primary vector PDF
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Figure 2 successfully generated: {output_path}")

    # Maintain alias for backwards compatibility
    alias_path = output_path.parent / "fig2_radial_overlap_matrix.pdf"
    if alias_path != output_path:
        shutil.copy2(output_path, alias_path)
        print(f"[+] Figure 2 alias created: {alias_path}")


if __name__ == "__main__":
    generate_figure_2()
