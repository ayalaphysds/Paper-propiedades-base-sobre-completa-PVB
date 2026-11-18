"""
Generate three 100% vector PDF figures (2x2 layout) for V6 in APS PRA / arXiv style:
  1. V6/figures/fig1_frame_spectrum.pdf
  2. V6/figures/fig2_laguerre_regularization.pdf
  3. V6/figures/fig3_optics_utility.pdf

All curves and data points are computed strictly from first-principles mathematical
and physical equations via pvb_physics.py and verified_metrics.json (zero stylized
surrogates, zero raster imshow, zero Type 3 fonts, min font >= 7.8 pt).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.special import ive

SCRIPTS_DIR = Path(__file__).resolve().parent
FIGURES_DIR = SCRIPTS_DIR.parent / "figures"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pvb_physics import (
    c_lp_closed_form,
    c_lp_quad,
    lg_radial,
    nodal_washout_fidelity,
    pvb_gram_normalized,
    pvb_gram_unnormalized,
    pvb_radial,
    weber_fourier_multiplier,
)

# Colorblind-safe Okabe-Ito palette
BLUE = "#0072B2"
VERMILION = "#D55E00"
TEAL = "#009E73"
PURPLE = "#CC79A7"
GOLD = "#E69F00"
SKY = "#56B4E9"
CHARCOAL = "#1A1A1A"
GRAY = "#666666"


def apply_pra_style() -> None:
    """Configure APS Physical Review A vector PDF typography (CID TrueType, min >= 7.8 pt)."""
    plt.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.family": "serif",
            "mathtext.fontset": "cm",
            "font.size": 8.2,
            "axes.labelsize": 8.5,
            "axes.titlesize": 8.8,
            "xtick.labelsize": 7.8,
            "ytick.labelsize": 7.8,
            "legend.fontsize": 7.8,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.4,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linestyle": ":",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_vector_pdf(fig: plt.Figure, out_path: Path) -> None:
    """Save figure as a tight single-page vector PDF."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.07)
    plt.close(fig)


def _style_inset(ax_ins: plt.Axes) -> None:
    """Apply consistent clean styling and >= 7.8 pt tick font size to insets."""
    ax_ins.tick_params(labelsize=7.8, length=2.5, pad=1.5)
    ax_ins.spines["top"].set_visible(False)
    ax_ins.spines["right"].set_visible(False)
    ax_ins.patch.set_facecolor("white")
    ax_ins.patch.set_alpha(0.97)
    ax_ins.set_zorder(10)


def make_fig1(metrics: dict[str, Any], out_path: Path) -> None:
    """Figure 1: Annular invariance, OAM-radial decoupling, frame spectrum, Paley-Wiener bounds."""
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.9), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.05, hspace=0.08)

    # --- Panel (a): Normalized radial intensity PVB vs LG_{0,l} ---
    ax = axes[0, 0]
    r_over_R0 = np.linspace(0.15, 2.25, 450)
    R0 = 1.0
    w_pvb = 0.15 * R0
    w0_lg = R0
    l_set = [0, 2, 4, 6]
    colors = [CHARCOAL, BLUE, TEAL, VERMILION]

    for l_v, col in zip(l_set, colors):
        ipvb = np.abs(pvb_radial(r_over_R0 * R0, l_v, R0, w_pvb)) ** 2
        ipvb /= np.max(ipvb)
        ilg = np.abs(lg_radial(r_over_R0 * R0, 0, l_v, w0_lg)) ** 2
        ilg /= np.max(ilg)
        ax.plot(r_over_R0, ipvb, color=col, ls="-", lw=1.45, label=r"PVB ($l=0..6$)" if l_v == 6 else None)
        ax.plot(r_over_R0, ilg, color=col, ls="--", lw=1.15, alpha=0.85, label=f"LG $l={l_v}$")

    ax.set_xlim(0.15, 2.25)
    ax.set_ylim(0.0, 1.78)
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel(r"$r / R_0$")
    ax.set_ylabel(r"$I(r) / I_{\max}$")
    ax.set_title("(a) Annular invariance vs. LG scaling", loc="left", fontweight="bold")
    ax.legend(loc="upper left", frameon=False, ncol=1, labelspacing=0.12, handlelength=1.3, bbox_to_anchor=(0.0, 1.01))

    # Inset: exact transcendental peak shift vs asymptote l^2(w/R0)^4/8
    tp = metrics["frame_and_normalization"]["transcendental_peak_shift"]
    ax_ins = ax.inset_axes([0.60, 0.65, 0.38, 0.32])
    _style_inset(ax_ins)
    l_dense = np.linspace(0.0, 6.2, 80)
    asymp_dense = (l_dense ** 2) * (tp["w_over_R0"] ** 4) / 8.0
    ax_ins.plot(l_dense, np.array(asymp_dense) * 1e2, color=BLUE, lw=1.2, label=r"$\frac{l^2}{8}(w/R_0)^4$")
    ax_ins.plot(tp["l_values"], np.array(tp["delta_r_over_R0"]) * 1e2, "o", color=VERMILION, ms=3.5, label="Exact")
    ax_ins.set_xlabel(r"$|l|$", fontsize=7.8, labelpad=0.8)
    ax_ins.set_ylabel(
        r"$10^2\Delta r/R_0$",
        fontsize=7.8,
        labelpad=2.0,
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.4, "alpha": 0.92},
    )
    ax_ins.set_xlim(-0.3, 6.4)
    ax_ins.set_ylim(-0.15, 2.25)
    ax_ins.set_yticks([0, 1, 2])
    ax_ins.legend(loc="upper left", frameon=False, fontsize=7.8, handlelength=1.0, borderpad=0.1, labelspacing=0.15)

    # --- Panel (b): Radial overlap gamma_l & azimuthal delta_{l,l'} inset ---
    ax = axes[0, 1]
    dr_w = np.linspace(0.0, 3.5, 250)
    w_ov = 0.5
    R0_ov = 4.0 * w_ov
    for l_v, col, ls in [(0, BLUE, "-"), (1, VERMILION, "--"), (4, TEAL, "-.")]:
        vals = [float(pvb_gram_normalized([R0_ov, R0_ov + d * w_ov], l_v, w_ov)[0, 1]) for d in dr_w]
        ax.plot(dr_w, vals, color=col, ls=ls, lw=1.45, label=rf"$l=l'={l_v}$")
    ax.plot(dr_w, np.exp(-0.5 * dr_w ** 2), color=CHARCOAL, ls=":", lw=1.2, label=r"$e^{-\Delta R^2/(2w^2)}$")
    ax.axhline(0.0, color=GRAY, lw=1.0)
    marker_dr_w = [2.0, 2.5]
    marker_vals = [
        float(pvb_gram_normalized([R0_ov, R0_ov + d * w_ov], 1, w_ov)[0, 1])
        for d in marker_dr_w
    ]
    ax.plot(marker_dr_w, marker_vals, "o", color=VERMILION, ms=4.0, zorder=5)
    ax.annotate(
        rf"$2.0w$: ${100.0 * marker_vals[0]:.1f}\%$",
        xy=(2.0, marker_vals[0]),
        xytext=(2.06, 0.21),
        fontsize=7.8,
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": CHARCOAL},
    )
    ax.set_xlim(0.0, 3.5)
    ax.set_ylim(-0.06, 1.08)
    ax.set_xlabel(r"$\Delta R / w$")
    ax.set_ylabel(r"$\gamma_l(R_0, R_0+\Delta R)$")
    ax.set_title(r"(b) Azimuthal $\delta_{l,l'}$ & radial overlap", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, ncol=1, bbox_to_anchor=(0.0, 0.03), labelspacing=0.18, handlelength=1.3)

    # Inset: 9x9 vector pcolormesh of azimuthal orthogonality delta_{l,l'}
    ax_ins_b = ax.inset_axes([0.56, 0.53, 0.41, 0.43])
    edges = np.arange(-4.5, 5.5, 1.0)
    eye9 = np.eye(9)
    ax_ins_b.pcolormesh(edges, edges, eye9, cmap="Blues", vmin=0.0, vmax=1.0, edgecolors="#CCCCCC", linewidth=0.3)
    ax_ins_b.set_aspect("equal")
    ax_ins_b.set_xticks([-4, 0, 4])
    ax_ins_b.set_yticks([-4, 0, 4])
    ax_ins_b.set_xlabel(r"$l'$", fontsize=7.8, labelpad=1)
    ax_ins_b.set_ylabel(r"$l$", fontsize=7.8, labelpad=0)
    ax_ins_b.tick_params(labelsize=7.8, length=2.0, pad=1.0)
    ax_ins_b.set_title(r"$\delta_{l,l'}$", fontsize=7.8, pad=2)

    # --- Panel (c): Frame multiplier G_tilde_w & Tikhonov filter + noise-gain inset ---
    ax = axes[1, 0]
    wk = np.linspace(0.0, 3.5, 300)
    gw = weber_fourier_multiplier(wk, 1.0)
    wk_tel = metrics["frame_and_normalization"]["telecom_bridge"]["w_kmax"]
    ax.axvspan(0.0, wk_tel, color=SKY, alpha=0.16, label=r"$\mathcal{H}_{k_{\max}}$")
    ax.plot(wk, gw, color=CHARCOAL, lw=1.55, label=r"$\widetilde{G}_w$")
    for alp, col, ls in [(1e-2, BLUE, "--"), (1e-3, TEAL, "-.")]:
        t_sig = (gw ** 2) / (gw ** 2 + alp)
        ax.plot(wk, t_sig, color=col, ls=ls, lw=1.4, label=rf"$T_\alpha\,(10^{{{int(math.log10(alp))}}})$")
    ax.axvline(wk_tel, color=VERMILION, ls=":", lw=1.1)
    ax.text(wk_tel - 0.04, 0.05, rf"$w k_{{\max}}={wk_tel:.2f}$", color=VERMILION, fontsize=7.8, ha="right")
    ax.set_xlim(0.0, 3.5)
    ax.set_ylim(0.0, 1.12)
    ax.set_xlabel(r"$w k_\perp$")
    ax.set_ylabel("Spectral multiplier")
    ax.set_title(r"(c) Frame spectrum & Tikhonov filter", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, bbox_to_anchor=(0.0, 0.14), handlelength=1.4)

    # Inset: log-scale noise gain H_tilde_{w,alpha} vs naive G_tilde_w^{-1}
    ax_ins_c = ax.inset_axes([0.61, 0.52, 0.37, 0.44])
    _style_inset(ax_ins_c)
    ax_ins_c.semilogy(wk, 1.0 / gw, color=CHARCOAL, ls=":", lw=1.25, label=r"$\widetilde{G}_w^{-1}$")
    for alp, col, ls in [(1e-2, BLUE, "--"), (1e-3, TEAL, "-.")]:
        h_gain = gw / (gw ** 2 + alp)
        ax_ins_c.semilogy(wk, h_gain, color=col, ls=ls, lw=1.35)
        wk_pk = math.sqrt(math.log(1.0 / alp))
        h_pk = 1.0 / (2.0 * math.sqrt(alp))
        ax_ins_c.plot([wk_pk], [h_pk], "o", color=col, ms=3.5)
    ax_ins_c.set_xlim(0.0, 3.5)
    ax_ins_c.set_ylim(0.5, 90.0)
    ax_ins_c.set_yticks([1.0, 10.0])
    ax_ins_c.set_xlabel(r"$w k_\perp$", fontsize=7.8, labelpad=1)
    ax_ins_c.set_ylabel(
        r"$\widetilde{H}_{w,\alpha}$",
        fontsize=7.8,
        labelpad=5.0,
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.3, "alpha": 0.94},
    )
    ax_ins_c.legend(loc="upper left", frameon=False, fontsize=7.8, handlelength=1.2)

    # --- Panel (d): Paley-Wiener frame bounds A, B=1 & condition number kappa(S_w) ---
    ax = axes[1, 1]
    wk_max = np.linspace(0.0, 3.0, 250)
    A_curve = np.exp(-0.5 * wk_max ** 2)
    B_curve = np.ones_like(wk_max)
    kappa_curve = np.exp(0.5 * wk_max ** 2)

    l1, = ax.plot(wk_max, A_curve, color=BLUE, lw=1.55, label=r"$A(w,k_{\max})$")
    l2, = ax.plot(wk_max, B_curve, color=CHARCOAL, ls="--", lw=1.25, label=r"$B=1$")
    ax.set_xlim(0.0, 3.0)
    ax.set_ylim(0.0, 1.12)
    ax.set_xlabel(r"$w k_{\max}$")
    ax.set_ylabel(r"Frame bounds $A, B$", color=BLUE)
    ax.tick_params(axis="y", colors=BLUE)

    ax2 = ax.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(True)
    ax2.grid(False)
    l3, = ax2.semilogy(wk_max, kappa_curve, color=VERMILION, lw=1.55, label=r"$\kappa(S_w)$")
    ax2.set_ylim(1.0, 150.0)
    ax2.set_ylabel(r"$\kappa(S_w) = B/A$", color=VERMILION)
    ax2.tick_params(axis="y", colors=VERMILION, labelsize=7.8)

    tb = metrics["frame_and_normalization"]["telecom_bridge"]
    ax.axvline(tb["w_kmax"], color=TEAL, ls=":", lw=1.15)
    ax.plot([tb["w_kmax"]], [tb["A_bound"]], "o", color=BLUE, ms=4.5, zorder=5)
    ax2.plot([tb["w_kmax"]], [tb["kappa_Sw"]], "s", color=VERMILION, ms=4.2, zorder=5)
    ax.annotate(
        f"NA=0.20\n$A={tb['A_bound']:.3f}$\n$\\kappa={tb['kappa_Sw']:.2f}$",
        xy=(tb["w_kmax"], tb["A_bound"]),
        xytext=(1.62, 0.56),
        fontsize=7.8,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": TEAL, "alpha": 0.9},
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": TEAL},
    )
    ax.set_title("(d) Paley–Wiener bounds & conditioning", loc="left", fontweight="bold")
    ax.legend([l1, l2, l3], [l.get_label() for l in (l1, l2, l3)], loc="lower left", frameon=False, handlelength=1.4)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    h_lbl_box = ax_ins_c.yaxis.get_label().get_window_extent(renderer)
    for t_lbl in ax_ins_c.get_yticklabels():
        t_box = t_lbl.get_window_extent(renderer)
        assert h_lbl_box.x1 < t_box.x0, f"fig1(c) inset ylabel overlaps tick {t_lbl.get_text()}"

    save_vector_pdf(fig, out_path)


def make_fig2(metrics: dict[str, Any], out_path: Path) -> None:
    """Figure 2: Closed-form c_{l,p}(R), nodal washout, noisy LG_{2,1} MSE, Gram conditioning."""
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.9), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.05, hspace=0.08)

    # --- Panel (a): c_{1,p}(R) closed form vs quad + residual inset ---
    ax = axes[0, 0]
    w_ov_w0 = 0.25
    w0 = 1.0
    w_pv = w_ov_w0 * w0
    R_dense = np.linspace(0.01, 3.2, 220)
    R_pts = np.linspace(0.15, 3.05, 16)
    p_cols = [(0, CHARCOAL), (1, BLUE), (2, TEAL), (3, VERMILION)]

    ax_ins_a = ax.inset_axes([0.59, 0.67, 0.39, 0.30])
    _style_inset(ax_ins_a)

    for p_v, col in p_cols:
        cf_vals = c_lp_closed_form(R_dense, p_v, 1, w_pv, w0)
        ax.plot(R_dense, cf_vals, color=col, lw=1.4, label=f"$p={p_v}$")
        qd_vals = np.array([c_lp_quad(float(rv), p_v, 1, w_pv, w0) for rv in R_pts])
        ax.plot(R_pts, qd_vals, "o", mfc="none", mec=col, ms=3.5, mew=0.9)
        cf_pts = c_lp_closed_form(R_pts, p_v, 1, w_pv, w0)
        res_log = np.log10(np.maximum(np.abs(cf_pts - qd_vals), 1e-16))
        ax_ins_a.plot(R_pts, res_log, "-", color=col, lw=1.0)

    ax.axhline(0.0, color=GRAY, lw=0.7)
    ax.set_xlim(0.0, 3.2)
    ax.set_ylim(-0.84, 1.68)
    ax.set_xlabel(r"$R / w_0$")
    ax.set_ylabel(r"$c_{1,p}(R)$")
    ax.set_title(r"(a) Closed-form $c_{1,p}(R)$ vs. quadrature", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, ncol=1, labelspacing=0.18, handlelength=1.2)

    ax_ins_a.set_xlim(0.0, 3.2)
    ax_ins_a.set_ylim(-16.5, -13.0)
    ax_ins_a.set_yticks([-16, -14])
    ax_ins_a.set_xlabel(
        r"$R/w_0$",
        fontsize=7.8,
        labelpad=1.5,
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.3, "alpha": 0.92},
    )
    ax_ins_a.set_ylabel(
        r"$\log_{10}|\Delta c|$",
        fontsize=7.8,
        labelpad=2.5,
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.3, "alpha": 0.92},
    )

    # --- Panel (b): Nodal washout F(p, l=1, w/w0) + Rayleigh threshold inset ---
    ax = axes[0, 1]
    ww0_dense = np.linspace(0.02, 1.0, 120)
    for p_v, col in p_cols:
        f_curve = [nodal_washout_fidelity(p_v, 1, float(x)) for x in ww0_dense]
        ax.plot(ww0_dense, f_curve, color=col, lw=1.45, label=f"$p={p_v}$")
    t1 = metrics["table1_nodal_washout"]
    ww0_t1 = [row["w_over_w0"] for row in t1["rows"]]
    for p_v, col in p_cols:
        pts = [row["F"][str(p_v)] for row in t1["rows"]]
        ax.plot(ww0_t1, pts, "o", color=col, ms=3.0)
    ax.axhline(0.95, color=GRAY, ls="--", lw=1.0)
    ax.text(0.55, 0.968, r"$\mathcal{F}=0.95$", color=GRAY, fontsize=7.8)
    ax.set_xlim(0.02, 1.0)
    ax.set_ylim(0.15, 1.06)
    ax.set_xlabel(r"$w / w_0$")
    ax.set_ylabel(r"Washout fidelity $\mathcal{F}(p,1)$")
    ax.set_title(r"(b) Radial nodal washout & Rayleigh limit", loc="left", fontweight="bold")
    ax.legend(loc="upper right", frameon=False, handlelength=1.3, labelspacing=0.2)

    # Inset in lower-left empty corner: exact w_crit / w0 vs 0.573 / sqrt(2p + |l| + 1)
    ax_ins_b = ax.inset_axes([0.18, 0.11, 0.37, 0.36])
    _style_inset(ax_ins_b)
    from scipy.optimize import brentq
    p_int = np.arange(0, 9)
    w_crit_exact = []
    for pv in p_int:
        wr = float(brentq(lambda x: nodal_washout_fidelity(int(pv), 1, x) - 0.95, 0.05, 0.6))
        w_crit_exact.append(wr)
    p_cont = np.linspace(1.0, 8.2, 80)
    w_crit_asymp = 0.573 / np.sqrt(2.0 * p_cont + 2.0)
    ax_ins_b.plot(p_cont, w_crit_asymp, color=BLUE, lw=1.25, label=r"$0.573/\sqrt{2p+2}$")
    ax_ins_b.plot(p_int, w_crit_exact, "o", color=VERMILION, ms=3.3, label="Exact")
    ax_ins_b.set_xlim(-0.6, 8.6)
    ax_ins_b.set_ylim(0.08, 0.74)
    ax_ins_b.set_yticks([0.2, 0.4, 0.6])
    ax_ins_b.set_xlabel(r"$p$", fontsize=7.8, labelpad=1.0)
    ax_ins_b.set_ylabel(r"$w_{\mathrm{crit}}/w_0$", fontsize=7.8, labelpad=4.5)
    ax_ins_b.legend(
        loc="upper right",
        bbox_to_anchor=(1.02, 1.03),
        frameon=False,
        fontsize=7.8,
        handlelength=1.0,
        borderpad=0.1,
        borderaxespad=0.15,
        labelspacing=0.12,
    )

    # --- Panel (c): Worked noisy LG_{2,1} Tikhonov MSE trade-off ---
    ax = axes[1, 0]
    nl = metrics["noisy_lg21_reconstruction"]
    alphas = np.array(nl["alpha_grid"])
    ax.loglog(alphas, nl["bias2"], color=BLUE, ls="--", lw=1.35, label=r"Bias$^2$")
    ax.loglog(alphas, nl["variance"], color=TEAL, ls="-.", lw=1.35, label="Variance")
    ax.loglog(alphas, nl["total_mse"], color=CHARCOAL, lw=1.65, label="Total MSE")
    mc = nl["mc_2d_fft_check"]
    ax.errorbar(
        mc["alpha_values"],
        mc["mc_mse_mean"],
        yerr=mc["mc_mse_sem"],
        fmt="o",
        color=VERMILION,
        ms=4.0,
        mfc="none",
        mew=1.1,
        capsize=2.0,
        label="2D-FFT MC",
    )
    ax.axhline(nl["naive_mse_alpha0"], color=PURPLE, ls=":", lw=1.25, label=r"$S_w^{-1}\,(9.00)$")
    ax.plot([nl["alpha_opt"]], [nl["mse_min"]], "*", color=GOLD, mec=CHARCOAL, ms=8.0, zorder=6)
    ax.annotate(
        f"min MSE\n$={nl['mse_min']:.3f}$",
        xy=(nl["alpha_opt"], nl["mse_min"]),
        xytext=(1.6e-2, 0.25),
        fontsize=7.8,
        ha="center",
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": CHARCOAL},
    )
    ax.set_xlim(1e-6, 1.0)
    ax.set_ylim(5e-4, 20.0)
    ax.set_xlabel(r"Tikhonov $\alpha_{\mathrm{reg}}$")
    ax.set_ylabel(r"Normalized MSE ($\mathrm{LG}_{2,1}$)")
    ax.set_title(r"(c) Noisy $\mathrm{LG}_{2,1}$ Tikhonov MSE", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, ncol=2, columnspacing=0.7, handlelength=1.3)

    # --- Panel (d): Gram conditioning kappa(gamma) vs kappa(G) & power crosstalk ---
    ax = axes[1, 1]
    t2 = metrics["table2_gram_and_sdm"]
    p2 = t2["params"]
    dr_w_dense = np.linspace(0.5, 3.0, 60)
    kG_dense, kg_dense, pwr_iso_dense = [], [], []
    for drw in dr_w_dense:
        R_g = p2["R_min"] + np.arange(p2["N"]) * (drw * p2["w"])
        G_m = pvb_gram_unnormalized(R_g, p2["l"], p2["w"])
        g_m = pvb_gram_normalized(R_g, p2["l"], p2["w"])
        kG_dense.append(float(np.linalg.cond(G_m)))
        kg_dense.append(float(np.linalg.cond(g_m)))
        pwr_iso_dense.append(10.0 * math.log10(float(abs(g_m[0, 1]) ** 2)))

    l_kg, = ax.semilogy(dr_w_dense, kg_dense, color=BLUE, lw=1.6, label=r"$\kappa(\gamma)$ (norm.)")
    l_kG, = ax.semilogy(dr_w_dense, kG_dense, color=CHARCOAL, ls="--", lw=1.35, label=r"$\kappa(G)$ (unnorm.)")
    ax.axvline(2.0, color=GRAY, ls=":", lw=1.0)
    ax.set_xlim(0.5, 3.0)
    ax.set_ylim(0.8, 3e4)
    ax.set_xlabel(r"$\Delta R / w$")
    ax.set_ylabel(r"Condition number $\kappa$", color=BLUE)
    ax.tick_params(axis="y", colors=BLUE)

    ax2 = ax.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(True)
    ax2.grid(False)
    l_iso, = ax2.plot(dr_w_dense, pwr_iso_dense, color=VERMILION, ls="-.", lw=1.45, label=r"$|\gamma_{12}|^2$ (dB)")
    ax2.set_ylim(-42.0, 2.0)
    ax2.set_ylabel(r"Power crosstalk $|\gamma_{12}|^2$ (dB)", color=VERMILION, labelpad=2.5)
    ax2.tick_params(axis="y", colors=VERMILION, labelsize=7.8)

    ax.annotate(
        r"$\kappa(G)$ rises",
        xy=(2.75, kG_dense[-5]),
        xytext=(1.95, 16.0),
        fontsize=7.8,
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": CHARCOAL},
    )
    ax.set_title(r"(d) Gram $\kappa(\gamma)$ vs. $\kappa(G)$ & crosstalk", loc="left", fontweight="bold")
    ax.legend(
        [l_kg, l_kG, l_iso],
        [l.get_label() for l in (l_kg, l_kG, l_iso)],
        loc="upper right",
        frameon=False,
        handlelength=1.4,
    )

    save_vector_pdf(fig, out_path)


def make_fig3(metrics: dict[str, Any], out_path: Path) -> None:
    """Figure 3: Classical RCF/SDM, Kolmogorov RKHS turbulence, Gouy IC-POVM, SPDC Bell-CHSH."""
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.9), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.05, hspace=0.08)

    # --- Panel (a): Sturm-Liouville RCF coupling + BER inset ---
    ax = axes[0, 0]
    rcf = metrics["classical_optics_utility"]["rcf_coupling"]
    l_vals = np.array(rcf["l_values"])
    ax.plot(l_vals, rcf["eta_pvb"], "o-", color=BLUE, ms=3.8, lw=1.55, label=r"PVB ($w=1.72\,\mu$m)")
    ax.plot(l_vals, rcf["eta_lg_w0_450"], "s--", color=TEAL, ms=3.3, lw=1.3, label=r"LG ($w_0=4.50\,\mu$m)")
    ax.plot(l_vals, rcf["eta_lg_w0_322"], "^:", color=VERMILION, ms=3.5, lw=1.35, label=r"LG ($w_0=3.22\,\mu$m)")
    ax.annotate(
        f"$+{rcf['villalba_benchmark_gain_dB']:.2f}$ dB\nat $l=4$",
        xy=(4, rcf["eta_lg_w0_322"][4]),
        xytext=(3.95, 0.44),
        ha="center",
        fontsize=7.8,
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": CHARCOAL},
    )
    ax.set_xlim(-0.4, 8.6)
    ax.set_ylim(-0.28, 1.38)
    ax.set_xticks([0, 2, 4, 6, 8])
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel(r"OAM order $l$")
    ax.set_ylabel(r"RCF coupling $\eta_l$")
    ax.set_title("(a) RCF modal coupling & SDM BER", loc="left", fontweight="bold")
    leg_main_a = ax.legend(
        loc="upper left",
        frameon=False,
        ncol=2,
        columnspacing=0.6,
        bbox_to_anchor=(0.0, 1.02),
        labelspacing=0.14,
        handlelength=1.15,
        handletextpad=0.35,
    )

    # Inset: OOK BER vs Eb/N0 (dB) at l=4 + SDM ZF penalty (right y-axis avoids l=4,5)
    ax_ins_a = ax.inset_axes([0.675, 0.165, 0.240, 0.215])
    _style_inset(ax_ins_a)
    ax_ins_a.spines["left"].set_visible(False)
    ax_ins_a.spines["right"].set_visible(True)
    ax_ins_a.yaxis.tick_right()
    ax_ins_a.yaxis.set_label_position("right")
    eb = np.array(rcf["ber_eb_n0_dB"])
    h_pvb, = ax_ins_a.semilogy(eb, rcf["ber_pvb_l4"], color=BLUE, lw=1.25, label="PVB")
    h_zf, = ax_ins_a.semilogy(eb, rcf["ber_sdm_zf_awgn_dr2w"], color=PURPLE, ls="--", lw=1.15, label="SDM ZF")
    ax_ins_a.semilogy(eb, rcf["ber_lg322_l4"], color=VERMILION, ls=":", lw=1.25)
    ax_ins_a.set_xlim(-0.5, 14.5)
    ax_ins_a.set_ylim(1e-8, 12.0)
    ax_ins_a.set_yticks([1e-6, 1e-3, 1e0])
    ax_ins_a.set_xlabel(r"$E_b/N_0$ (dB)", fontsize=7.8, labelpad=0.8)
    ax_ins_a.set_ylabel(
        "BER",
        fontsize=7.8,
        labelpad=1.5,
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.25, "alpha": 0.92},
    )
    ax_ins_a.legend(
        handles=[h_pvb, h_zf],
        loc="lower left",
        ncol=1,
        frameon=False,
        fontsize=7.8,
        handlelength=0.75,
        handletextpad=0.25,
        labelspacing=0.03,
        borderpad=0.02,
        borderaxespad=0.06,
    )
    ax_ins_a.text(13.5, 0.35, "LG", color=VERMILION, fontsize=7.8, ha="right", va="bottom")

    # --- Panel (b): 2D Kolmogorov RKHS turbulence filtering ---
    ax = axes[0, 1]
    kol = metrics["classical_optics_utility"]["kolmogorov_rkhs"]
    dr0 = np.array(kol["D_over_r0_grid"])
    # Main curves: Scintillation Intensity MSE (mean +- 1 SEM) + Field MSE Tikhonov vs Raw dashed
    for key_m, key_s, col, label in [
        ("int_mse_raw_mean", "int_mse_raw_sem", CHARCOAL, "Raw (Int. MSE)"),
        ("int_mse_rkhs_mean", "int_mse_rkhs_sem", BLUE, r"$P_{\mathrm{RKHS}}$ (Int.)"),
        ("int_mse_tikhonov_mean", "int_mse_tikhonov_sem", TEAL, r"Tikhonov (Int.)"),
    ]:
        mu = np.array(kol[key_m])
        se = np.array(kol[key_s])
        ax.plot(dr0, mu, "o-", color=col, ms=3.3, lw=1.45, label=label)
        ax.fill_between(dr0, mu - se, mu + se, color=col, alpha=0.16)

    # Also plot Field MSE raw vs Tikhonov (dashed) for completeness
    ax.plot(dr0, kol["field_mse_raw_mean"], "--", color=VERMILION, lw=1.2, label="Raw (Field)")
    ax.plot(dr0, kol["field_mse_tikhonov_mean"], "-.", color=PURPLE, lw=1.25, label="Tikhonov (Field)")

    ax.set_xlim(0.45, 3.05)
    ax.set_ylim(0.0, 0.68)
    ax.set_xlabel(r"Turbulence strength $D / r_0$")
    ax.set_ylabel("Normalized MSE")
    ax.set_title("(b) Kolmogorov RKHS turbulence filter", loc="left", fontweight="bold")
    ax.legend(loc="upper left", frameon=False, handlelength=1.4, labelspacing=0.25)

    # --- Panel (c): Multi-plane Gouy IC-POVM radial qudit tomography ---
    ax = axes[1, 0]
    ic = metrics["quantum_optics_utility"]["ic_povm_radial_qudit"]
    n_ph = np.array(ic["N_phot_grid"], dtype=float)
    n_dense = np.logspace(2.4, 4.6, 80)

    ax.loglog(n_dense, ic["crb_with_Eres"] / n_dense, "--", color=BLUE, lw=1.35, label=r"PVB CRB ($41.80/N$)")
    ax.errorbar(
        n_ph,
        ic["mle_mse_pvb_mean"],
        yerr=ic["mle_mse_pvb_sem"],
        fmt="o",
        color=BLUE,
        ms=4.0,
        capsize=2.0,
        label=r"PVB $R\rho R$ MLE",
    )
    ax.loglog(n_dense, ic["crb_sequential_mub"] / n_dense, ":", color=VERMILION, lw=1.35, label=r"5-MUB CRB ($18.75/N$)")
    ax.errorbar(
        n_ph,
        ic["mle_mse_mub_mean"],
        yerr=ic["mle_mse_mub_sem"],
        fmt="s",
        color=VERMILION,
        ms=3.6,
        capsize=2.0,
        label="5-MUB MLE",
    )
    ax.text(
        0.96,
        0.93,
        f"$M=1$: rank {ic['single_plane_rank']}/16\n$M=5$: rank {ic['multi_plane_rank']}/16",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7.8,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": GRAY, "alpha": 0.9},
    )
    ax.set_xlim(240.0, 4.0e4)
    ax.set_ylim(3e-4, 0.35)
    ax.set_xlabel(r"Total photons $N_{\mathrm{phot}}$")
    ax.set_ylabel(r"Tomography MSE $\|\hat{\rho}-\rho_0\|_F^2$")
    ax.set_title("(c) Gouy IC-POVM radial qudit ($d=4$)", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, handlelength=1.4)

    # --- Panel (d): SPDC circular-iris Bell-CHSH S + t_l inset ---
    ax = axes[1, 1]
    spdc = metrics["quantum_optics_utility"]["spdc_iris_invariance"]
    r_ir = np.array(spdc["R_iris_over_R0_grid"])
    ax.plot(r_ir, spdc["S_pvb_2arm"], color=BLUE, lw=1.6, label="PVB (2-arm)")
    ax.plot(r_ir, spdc["S_lg_1arm"], color=TEAL, ls="--", lw=1.4, label="LG (1-arm)")
    ax.plot(r_ir, spdc["S_lg_2arm"], color=VERMILION, ls="-.", lw=1.4, label="LG (2-arm)")
    ax.axhline(2.0 * math.sqrt(2.0), color=GRAY, ls=":", lw=0.9)
    ax.axhline(2.0, color=CHARCOAL, ls=":", lw=0.9)
    ax.axvline(1.0, color=GRAY, ls="--", lw=0.8)
    ax.text(0.63, 1.915, "Bell limit $S=2$", fontsize=7.8, color=CHARCOAL)
    ax.set_xlim(0.6, 2.2)
    ax.set_ylim(1.88, 2.94)
    ax.set_xlabel(r"Iris radius $R_{\mathrm{iris}} / R_0$")
    ax.set_ylabel(r"Bell–CHSH parameter $S$")
    ax.set_title("(d) SPDC iris invariance & CHSH", loc="left", fontweight="bold")
    ax.legend(loc="upper left", frameon=False, bbox_to_anchor=(0.0, 0.90), handlelength=1.35)

    # Inset: t_l at R_iris = R0 for l=1..4
    ax_ins_d = ax.inset_axes([0.63, 0.16, 0.35, 0.32])
    _style_inset(ax_ins_d)
    l_ch = np.array(spdc["l_channels"])
    width_bar = 0.36
    ax_ins_d.bar(l_ch - width_bar / 2, spdc["t_pvb_at_R0"], width=width_bar, color=BLUE, label="PVB")
    ax_ins_d.bar(l_ch + width_bar / 2, spdc["t_lg_at_R0"], width=width_bar, color=VERMILION, label="LG")
    ax_ins_d.set_xticks(l_ch)
    ax_ins_d.set_ylim(0.0, 0.88)
    ax_ins_d.set_yticks([0.0, 0.4, 0.8])
    ax_ins_d.set_xlabel(r"$l$", fontsize=7.8, labelpad=1.0)
    ax_ins_d.set_ylabel(
        r"$t_l(R_0)$",
        fontsize=7.8,
        labelpad=1.5,
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.3, "alpha": 0.92},
    )
    ax_ins_d.legend(loc="upper center", ncol=2, frameon=False, fontsize=7.8, handlelength=0.9, columnspacing=0.7, borderpad=0.1)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax_a = axes[0, 0]
    ins_patch_a = ax_ins_a.patch.get_window_extent(renderer)
    ins_tight_a = ax_ins_a.get_tightbbox(renderer)
    assert ins_tight_a.y0 > ax_a.spines["bottom"].get_window_extent(renderer).y0 + 2.0
    pvb_pts = ax_a.transData.transform(np.column_stack([l_vals, rcf["eta_pvb"]]))
    assert leg_main_a.get_window_extent(renderer).y0 > float(np.max(pvb_pts[:, 1])) + 2.0
    l_dense = np.linspace(0.0, 8.0, 801)
    for cname, ys in [
        ("pvb", rcf["eta_pvb"]),
        ("lg450", rcf["eta_lg_w0_450"]),
        ("lg322", rcf["eta_lg_w0_322"]),
    ]:
        pts_m = ax_a.transData.transform(np.column_stack([l_vals, ys]))
        for lv, (px, py) in zip(l_vals, pts_m):
            assert not ins_tight_a.contains(px, py), f"fig3(a) marker {cname} l={lv} inside ax_ins_a tightbbox"
        pts_c = ax_a.transData.transform(np.column_stack([l_dense, np.interp(l_dense, l_vals, ys)]))
        assert not any(ins_patch_a.contains(px, py) for px, py in pts_c), f"fig3(a) curve {cname} crosses ax_ins_a"
    leg_d_box = ax_ins_d.get_legend().get_window_extent(renderer)
    bar_top_disp = ax_ins_d.transData.transform([(1.0, max(spdc["t_pvb_at_R0"]))])[0, 1]
    assert leg_d_box.y0 > bar_top_disp + 2.5, "fig3(d) bars too close to inset legend"

    save_vector_pdf(fig, out_path)


def generate_all_figures(metrics: dict[str, Any], figures_dir: Path = FIGURES_DIR) -> list[Path]:
    """Generate all three canonical V6 PDF figures from verified metrics & physics."""
    apply_pra_style()
    paths = [
        figures_dir / "fig1_frame_spectrum.pdf",
        figures_dir / "fig2_laguerre_regularization.pdf",
        figures_dir / "fig3_optics_utility.pdf",
    ]
    make_fig1(metrics, paths[0])
    make_fig2(metrics, paths[1])
    make_fig3(metrics, paths[2])
    return paths


def main() -> int:
    metrics_path = SCRIPTS_DIR / "verified_metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(f"Missing {metrics_path}; run verify_math_and_tables.py first.")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    paths = generate_all_figures(metrics, FIGURES_DIR)
    for p in paths:
        print(f"[generate_figures] Generated {p} ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
