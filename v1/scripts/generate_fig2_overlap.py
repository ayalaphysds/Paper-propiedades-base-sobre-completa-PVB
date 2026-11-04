#!/usr/bin/env python3
"""
generate_fig2_overlap.py
Milestone M2: Simulation Script for Figure 2.

Figure 2: Exact radial overlap matrix and universal asymptotic Gaussian cross-talk:
(a) 2D heatmap of exact normalized overlap matrix gamma_l(r1, r2; w0) = I_l(r1*r2/w0^2) / sqrt(I_l(r1^2/w0^2)*I_l(r2^2/w0^2)).
(b) Universal asymptotic Gaussian cross-talk comparison: gamma_l(r0, r) vs |r - r0| / w0
    comparing exact Bessel against exp(-(r - r0)^2 / (2 w0^2)) for l in {0, 1, 3, 5}.
(c) Relative error of the Gaussian approximation |gamma_exact - gamma_asymp| / gamma_exact vs |r - r0| / w0,
    confirming the analytical second-order correction (4l^2 - 1) w0^2 (r - r0)^2 / (16 r0^4).

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


def calculate_exact_overlap(r1: np.ndarray, r2: np.ndarray, w0: float, l: int = 1) -> np.ndarray:
    r"""
    Computes exact normalized overlap coefficient:
    gamma_l(r1, r2; w0) = I_l(r1*r2/w0^2) / sqrt(I_l(r1^2/w0^2) * I_l(r2^2/w0^2))
    Using ive(l, z) = I_l(z) * exp(-z):
    gamma_l = exp(-(r1 - r2)^2 / (2 w0^2)) * ive(l, r1*r2/w0^2) / sqrt(ive(l, r1^2/w0^2) * ive(l, r2^2/w0^2))
    Handles 2D meshgrid inputs as well as 1D arrays.
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


def generate_figure_2(output_path: Path = None):
    """Generates publication-quality 3-panel Figure 2."""
    if output_path is None:
        output_path = PROJECT_ROOT / "v1" / "figures" / "fig2_radial_overlap_matrix.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.6), constrained_layout=True)

    # ----------------------------------------------------
    # Panel (a): 2D Heatmap of Exact Normalized Overlap Matrix
    # ----------------------------------------------------
    ax_a = axes[0]
    r0 = 1.0     # mm
    w0 = 0.10    # mm
    l_heat = 1

    r_span = np.linspace(0.65, 1.35, 250)  # mm
    R1, R2 = np.meshgrid(r_span, r_span)
    gamma_2d = calculate_exact_overlap(R1, R2, w0, l=l_heat)

    im = ax_a.imshow(gamma_2d, origin="lower", extent=[r_span[0], r_span[-1], r_span[0], r_span[-1]],
                     cmap="viridis", vmin=0.0, vmax=1.0, aspect="equal")
    
    # Add contour levels at 0.5, 0.8, 0.95
    cs = ax_a.contour(R1, R2, gamma_2d, levels=[0.1, 0.5, 0.8], colors="white",
                      linewidths=0.8, linestyles=["dotted", "dashed", "solid"])
    ax_a.clabel(cs, inline=True, fontsize=7.5, fmt="%.1f")

    cbar = fig.colorbar(im, ax=ax_a, fraction=0.046, pad=0.04)
    cbar.set_label(r"Overlap $\gamma_l(r_1, r_2)$", rotation=270, labelpad=14)

    ax_a.set_xlabel(r"Ring radius $r_1$ [mm]")
    ax_a.set_ylabel(r"Ring radius $r_2$ [mm]")
    ax_a.set_title(rf"\textbf{{(a)}} Overlap matrix $\gamma_{{{l_heat}}}(r_1, r_2)$ ($w_0 = {w0}$ mm)")

    # ----------------------------------------------------
    # Panel (b): Universal Asymptotic Gaussian Cross-Talk
    # ----------------------------------------------------
    ax_b = axes[1]
    l_cases = [0, 1, 3, 5]
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
    
    # Normalized radial separation delta_r / w0 in [0, 2.5]
    delta_norm = np.linspace(0.0, 2.5, 200)
    r_sweep = r0 + delta_norm * w0  # mm

    # Universal Gaussian curve: exp(- (delta_r)^2 / (2 w0^2))
    gamma_gaussian_universal = np.exp(- (delta_norm**2) / 2.0)

    # Plot universal Gaussian reference
    ax_b.plot(delta_norm, gamma_gaussian_universal, "k--", linewidth=2.2,
              label=r"Universal Gaussian: $\exp(-\Delta r^2 / 2w_0^2)$")

    for l_val, col in zip(l_cases, colors):
        gamma_exact_vals = calculate_exact_overlap(r0, r_sweep, w0, l=l_val)
        ax_b.plot(delta_norm, gamma_exact_vals, "-", color=col, alpha=0.85,
                  label=rf"Exact Bessel ($l = {l_val}$)")

    ax_b.set_xlabel(r"Normalized separation $|r - r_0| / w_0$")
    ax_b.set_ylabel(r"Normalized overlap $\gamma_l(r_0, r)$")
    ax_b.set_title(r"\textbf{(b)} Universal asymptotic cross-talk")
    ax_b.set_xlim(0.0, 2.5)
    ax_b.set_ylim(-0.02, 1.05)
    ax_b.legend(loc="upper right", frameon=True, framealpha=0.9)

    # ----------------------------------------------------
    # Panel (c): Relative Error of Gaussian Approximation
    # ----------------------------------------------------
    ax_c = axes[2]
    # Evaluate relative error: |gamma_exact - gamma_asymp| / gamma_exact
    for l_val, col in zip(l_cases, colors):
        gamma_exact_vals = calculate_exact_overlap(r0, r_sweep, w0, l=l_val)
        # Avoid division by zero at large separation
        valid_mask = gamma_exact_vals > 1e-12
        rel_error = np.abs(gamma_exact_vals - gamma_gaussian_universal) / gamma_exact_vals
        
        # Theoretical second-order correction: (4l^2 - 1) * w0^2 * (r - r0)^2 / (16 * r0^4)
        theory_correction = ((4.0 * (l_val**2) - 1.0) * (w0**2) * ((r_sweep - r0)**2)) / (16.0 * (r0**4))

        ax_c.semilogy(delta_norm[valid_mask], rel_error[valid_mask], "-", color=col,
                      label=rf"$l = {l_val}$ (exact / num)")
        if l_val > 0:
            ax_c.semilogy(delta_norm, np.abs(theory_correction), ":", color=col, alpha=0.7)

    ax_c.set_xlabel(r"Normalized separation $|r - r_0| / w_0$")
    ax_c.set_ylabel(r"Relative error $|\gamma_{\mathrm{exact}} - \gamma_{\mathrm{asymp}}| / \gamma_{\mathrm{exact}}$")
    ax_c.set_title(r"\textbf{(c)} Asymptotic accuracy ($r_0 / w_0 = 10$)")
    ax_c.set_xlim(0.0, 2.5)
    ax_c.set_ylim(1e-6, 1e-1)
    
    # Custom note on analytical correction
    ax_c.text(0.1, 2e-2, r"Dotted: $\frac{4l^2 - 1}{16} \frac{w_0^2 \Delta r^2}{r_0^4}$",
              fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    ax_c.legend(loc="lower right", frameon=True, framealpha=0.9)

    # Save vector PDF
    fig.savefig(output_path, format="pdf", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Successfully generated Figure 2: {output_path}")


if __name__ == "__main__":
    out_file = PROJECT_ROOT / "v1" / "figures" / "fig2_radial_overlap_matrix.pdf"
    generate_figure_2(out_file)
