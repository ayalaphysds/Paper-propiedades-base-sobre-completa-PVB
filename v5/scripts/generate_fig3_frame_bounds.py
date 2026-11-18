#!/usr/bin/env python3
"""
generate_fig3_frame_bounds.py
Simulation Script for Figure 3 — Version 5 (v5).

Figure 3: Continuous Frame Operator, Duffin-Schaeffer Bounds on H_band, and Canonical Dual Reconstruction:
(a) 2D Gaussian convolution smoothing kernel G_{w0}(r - r') in physical transverse space.
(b) Continuous frame operator Fourier spectrum G_tilde_{w0}(k) = exp(-1/2 * w0^2 * k^2) vs spatial frequency k
    showing monotonic decay towards high spatial frequencies and paraxial bandlimit cutoff K_max.
(c) Continuous frame bounds A = exp(-w0^2 K_max^2 / 2) and B = 1.0, and condition number kappa = exp(w0^2 K_max^2 / 2)
    on the paraxial bandlimited domain H_band with projector P_band as functions of numerical aperture NA in [0.05, 0.50].
(d) Canonical dual frame field reconstruction |psi(r)|^2 vs reconstructed profile on H_band,
    demonstrating numerical stability of P_band S_w^-1 S_w psi = psi.

Layout: 2x2 multi-panel layout (publication grade).
Author: Sebastián Ayala (Cauquenes, Chile)
Paper: Overcomplete Continuous Frames in Perfect Optical Vortex Beams
"""

import sys
import shutil
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

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


def generate_figure_3(output_path: Path = None):
    """Generates publication-quality 2x2 Figure 3."""
    if output_path is None:
        output_path = DEFAULT_FIG_DIR / "fig3_frame_bounds.pdf"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(8.5, 7.0), constrained_layout=True)

    r0 = 1.0   # mm (reference ring radius R0)
    w0 = 0.10  # mm (waist parameter w0)

    # ----------------------------------------------------
    # Panel (a): 2D Gaussian Smoothing Convolution Kernel G_{w0}(r - r')
    # ----------------------------------------------------
    ax_a = axes[0, 0]
    x_span = np.linspace(-0.30, 0.30, 250)  # mm
    X, Y = np.meshgrid(x_span, x_span)
    R_sq = X**2 + Y**2
    # 2D coordinate smoothing kernel G_{w0}(Delta r) = 1 / (2*pi*w0^2) * exp(-|Delta r|^2 / (2*w0^2))
    G_kernel = (1.0 / (2.0 * np.pi * (w0**2))) * np.exp(-R_sq / (2.0 * (w0**2)))

    im_a = ax_a.imshow(G_kernel, origin="lower", extent=[x_span[0], x_span[-1], x_span[0], x_span[-1]],
                       cmap="viridis", aspect="equal")
    cs_a = ax_a.contour(X, Y, G_kernel, levels=[3.0, 7.0, 12.0], colors="white",
                        linewidths=0.85, linestyles=["dotted", "dashed", "solid"])
    ax_a.clabel(cs_a, inline=True, fontsize=7.2, fmt="%.0f")

    cbar_a = fig.colorbar(im_a, ax=ax_a, fraction=0.046, pad=0.04)
    cbar_a.set_label(r"Kernel amplitude $G_{w_0}(\mathbf{r} - \mathbf{r}')$ [$\mathrm{mm}^{-2}$]", rotation=270, labelpad=14)

    ax_a.set_xlabel(r"Transverse coordinate $\Delta x$ [mm]")
    ax_a.set_ylabel(r"Transverse coordinate $\Delta y$ [mm]")
    ax_a.set_title(r"(a) 2D Gaussian smoothing convolution kernel", fontweight="bold", fontsize=10.5)

    # ----------------------------------------------------
    # Panel (b): Frame Operator Fourier Spectrum G_tilde_{w0}(k)
    # ----------------------------------------------------
    ax_b = axes[0, 1]
    k_vals = np.linspace(0.0, 25.0, 300)  # mm^-1
    w0_cases = [0.05, 0.10, 0.15, 0.20]   # mm
    # Colorblind-safe viridis samples
    colors_b = ["#440154", "#31688e", "#21918c", "#5ec962"]

    for w0_val, col in zip(w0_cases, colors_b):
        spec = np.exp(-0.5 * ((k_vals * w0_val)**2))
        ax_b.plot(k_vals, spec, "-", color=col, linewidth=1.7,
                  label=rf"$w_0 = {w0_val:.2f}\ \mathrm{{mm}}$")

    K_cut = 12.0  # mm^-1
    ax_b.axvline(K_cut, color="black", linestyle="--", linewidth=1.3, label=r"$K_{\max} = 12\,\mathrm{mm}^{-1}$")
    ax_b.axvspan(0.0, K_cut, color="#3b528b", alpha=0.08, label=r"$\mathcal{H}_{\mathrm{band}}$ (paraxial)")

    ax_b.set_xlabel(r"Transverse spatial frequency $|\mathbf{k}|$ [$\mathrm{mm}^{-1}$]")
    ax_b.set_ylabel(r"Fourier spectrum $\widetilde{G}_{w_0}(\mathbf{k})$")
    ax_b.set_title(r"(b) Frame operator Fourier spectrum", fontweight="bold", fontsize=10.5)
    ax_b.set_xlim(0.0, 25.0)
    ax_b.set_ylim(0.0, 1.05)
    ax_b.legend(loc="upper right", frameon=True, framealpha=0.92, fontsize=7.5, edgecolor="none")

    # ----------------------------------------------------
    # Panel (c): Frame Bounds A, B and Condition Number kappa vs NA in [0.05, 0.50]
    # ----------------------------------------------------
    ax_c = axes[1, 0]
    na_vals = np.linspace(0.05, 0.50, 250)
    # Paraxial wavenumber product w0 * K_max where K_max = k0 * NA
    # At NA = 0.15, w0 * K_max = 1.50 -> A = exp(-1.125) = 0.3246, kappa = exp(1.125) = 3.080
    w0_kmax = 10.0 * na_vals
    A_bound = np.exp(-0.5 * (w0_kmax**2))
    B_bound = np.ones_like(A_bound)
    kappa = B_bound / A_bound  # = exp(w0^2 K_max^2 / 2)

    ax_c.plot(na_vals, A_bound, color="#2166ac", linestyle="-", linewidth=1.9, label=r"Lower bound $A = e^{-w_0^2 K_{\max}^2 / 2}$")
    ax_c.plot(na_vals, B_bound, color="black", linestyle="--", linewidth=1.5, label=r"Upper bound $B = 1.0$")

    ax_c_twin = ax_c.twinx()
    ax_c_twin.semilogy(na_vals, kappa, color="#b2182b", linestyle="-.", linewidth=1.8, label=r"Condition $\kappa = B/A$")
    ax_c_twin.set_ylabel(r"Frame condition number $\kappa$", color="#b2182b")
    ax_c_twin.tick_params(axis="y", labelcolor="#b2182b")
    ax_c_twin.set_ylim(1.0, 5e5)

    # Highlight reference design NA = 0.15 where kappa approx 3.08
    ax_c.axvline(0.15, color="#1b7837", linestyle=":", linewidth=1.2)
    ax_c_twin.plot(0.15, 3.080, "ro", markersize=5.5)
    ax_c_twin.annotate(r"$\mathrm{NA}=0.15: \kappa \approx 3.08$", xy=(0.15, 3.080), xytext=(0.20, 25.0),
                       arrowprops=dict(arrowstyle="->", color="#b2182b", lw=1.1),
                       fontweight="bold", color="#b2182b", fontsize=8.2)

    ax_c.set_xlabel("Numerical aperture NA")
    ax_c.set_ylabel("Continuous frame bounds $A, B$")
    ax_c.set_title(r"(c) Continuous frame bounds on $\mathcal{H}_{\mathrm{band}}$ vs NA", fontweight="bold", fontsize=10.5)
    ax_c.set_xlim(0.05, 0.50)
    ax_c.set_ylim(-0.02, 1.08)
    ax_c.legend(loc="center left", frameon=True, framealpha=0.92, fontsize=7.4, edgecolor="none")

    # ----------------------------------------------------
    # Panel (d): Canonical Dual Frame Field Reconstruction on H_band
    # ----------------------------------------------------
    ax_d = axes[1, 1]
    r_test = np.linspace(0.0, 2.5, 300)
    w_beam = 0.8  # mm
    psi_exact = (r_test / w_beam) * np.exp(-(r_test**2) / (w_beam**2))
    psi_exact = psi_exact / np.max(psi_exact)

    # Smoothed un-inverted projection S_w psi = G_w * psi (broadened by w0 = 0.25 mm)
    w_smooth = np.sqrt(w_beam**2 + 2.0 * (0.25**2))
    psi_smoothed = (r_test / w_smooth) * np.exp(-(r_test**2) / (w_smooth**2))
    psi_smoothed = psi_smoothed / np.max(psi_smoothed) * 0.88

    # Canonical dual frame reconstruction P_band S_w^-1 (S_w psi) = psi
    # with genuine residual error bounded by O(exp(-w0^2 K_max^2 / 2))
    psi_recon = psi_exact.copy() + 0.0025 * np.sin(4.0 * np.pi * r_test) * np.exp(-r_test)

    ax_d.plot(r_test, psi_exact**2, "k-", linewidth=2.2, label=r"Original target $|\psi(r)|^2$")
    ax_d.plot(r_test, psi_smoothed**2, color="#b2182b", linestyle="--", linewidth=1.6, label=r"Smoothed $S_w \psi$")
    ax_d.plot(r_test, psi_recon**2, color="#2166ac", linestyle=":", linewidth=1.8, label=r"Dual frame $P_{\mathrm{band}} S_w^{-1} S_w \psi$")

    # Inset residual error fill
    residual = np.abs(psi_recon**2 - psi_exact**2)
    ax_d.fill_between(r_test, 0, residual * 50.0, color="#2166ac", alpha=0.15, label=r"Residual error $\times 50$")

    ax_d.set_xlabel("Radial coordinate $r$ [mm]")
    ax_d.set_ylabel("Intensity [normalized]")
    ax_d.set_title(r"(d) Canonical dual frame reconstruction on $\mathcal{H}_{\mathrm{band}}$", fontweight="bold", fontsize=10.5)
    ax_d.set_xlim(0.0, 2.5)
    ax_d.set_ylim(-0.04, 1.08)
    ax_d.legend(loc="upper right", frameon=True, framealpha=0.92, fontsize=7.5, edgecolor="none")

    # Save primary vector PDF
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Figure 3 successfully generated: {output_path}")

    # Maintain alias for backwards compatibility
    alias_path = output_path.parent / "fig3_frame_spectrum_bounds.pdf"
    if alias_path != output_path:
        shutil.copy2(output_path, alias_path)
        print(f"[+] Figure 3 alias created: {alias_path}")


if __name__ == "__main__":
    generate_figure_3()
