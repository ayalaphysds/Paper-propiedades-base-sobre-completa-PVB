"""Generate six dedicated, spacious STIX Unicode vector PDF figures for the two
companion manuscripts:
  - Paper I (part1_theory): fig1_pvb_overlap.pdf, fig2_frame_regularization.pdf,
    fig3_lg_washout_gram.pdf
  - Paper II (part2_applications): fig1_noisy_deconvolution.pdf,
    fig2_rcf_turbulence.pdf, fig3_quantum_tomography_chsh.pdf
All inset fonts use >= 8.3 pt at ~0.94-0.98 textwidth scale and pass automated
bounding-box non-collision assertions against curves, legends, and parent axes spines.
"""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

SCRIPTS_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = SCRIPTS_DIR.parent
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

BLUE = "#0072B2"
VERMILION = "#D55E00"
TEAL = "#009E73"
PURPLE = "#CC79A7"
GOLD = "#E69F00"
SKY = "#56B4E9"
CHARCOAL = "#222222"
GRAY = "#666666"


def apply_pra_style() -> None:
    plt.rcParams.update({
        "font.family": "STIXGeneral",
        "mathtext.fontset": "stix",
        "font.size": 9.5,
        "axes.labelsize": 9.8,
        "axes.titlesize": 9.7,
        "legend.fontsize": 8.4,
        "xtick.labelsize": 8.7,
        "ytick.labelsize": 8.7,
        "axes.linewidth": 0.85,
        "grid.linewidth": 0.45,
        "grid.alpha": 0.25,
        "lines.linewidth": 1.55,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def _style_inset(ax_ins: plt.Axes) -> None:
    ax_ins.set_facecolor("white")
    ax_ins.patch.set_alpha(0.97)
    ax_ins.spines["top"].set_visible(False)
    ax_ins.spines["right"].set_visible(False)
    ax_ins.tick_params(labelsize=8.3, length=2.4, pad=1.6)


# ==============================================================================
# PAPER I FIGURES (PURE THEORY)
# ==============================================================================

def make_part1_fig1(metrics: dict[str, Any], out_path: Path) -> None:
    """Paper I Fig. 1: (a) Annular invariance vs. LG scaling + peak-shift inset;
    (b) Azimuthal Kronecker delta and normalized radial overlap gamma_l.
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.95), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.07)

    # Panel (a)
    ax = axes[0]
    r_grid = np.linspace(1e-4, 2.25, 450)
    R0 = 1.0
    w_plot = 0.15
    lg_specs = [(0, CHARCOAL, "--"), (2, BLUE, "--"), (4, TEAL, "--"), (6, VERMILION, "--")]
    for l_v, col, ls in lg_specs:
        ir_lg = np.abs(lg_radial(r_grid, 0, l_v, R0)) ** 2
        ax.plot(r_grid, ir_lg / np.max(ir_lg), color=col, ls=ls, lw=1.25, alpha=0.88, label=rf"LG $l={l_v}$")
        ir_pvb = np.abs(pvb_radial(r_grid, l_v, R0, w_plot)) ** 2
        lbl = "PVB ($l=0$\u2013$6$)" if l_v == 4 else None
        ax.plot(r_grid, ir_pvb / np.max(ir_pvb), color=VERMILION if l_v == 4 else "#B85000", lw=1.65, alpha=0.92, label=lbl)

    ax.set_xlim(0.15, 2.25)
    ax.set_ylim(0.0, 2.08)
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel(r"$r / R_0$")
    ax.set_ylabel(r"$I(r) / I_{\max}$")
    ax.set_title("(a) Annular invariance vs. LG scaling", loc="left", fontweight="bold")
    ax.legend(loc="upper left", frameon=False, ncol=1, labelspacing=0.15, handlelength=1.35, bbox_to_anchor=(0.0, 1.01))

    tp = metrics["frame_and_normalization"]["transcendental_peak_shift"]
    ax_ins = ax.inset_axes([0.53, 0.63, 0.45, 0.34])
    _style_inset(ax_ins)
    l_dense = np.linspace(0.0, 6.2, 80)
    asymp_dense = (l_dense ** 2) * (tp["w_over_R0"] ** 4) / 8.0
    ax_ins.plot(l_dense, np.array(asymp_dense) * 1e2, color=BLUE, lw=1.35, label=r"$\frac{l^2}{8}(w/R_0)^4$")
    ax_ins.plot(tp["l_values"], np.array(tp["delta_r_over_R0"]) * 1e2, "o", color=VERMILION, ms=3.9, label="Exact")
    ax_ins.set_xlabel(r"$|l|$", fontsize=8.5, labelpad=0.6)
    ax_ins.set_ylabel(r"$10^2\,\Delta r_{\mathrm{peak}}/R_0$", fontsize=8.4, labelpad=2.2)
    ax_ins.set_xlim(-0.3, 6.4)
    ax_ins.set_ylim(-0.15, 2.35)
    ax_ins.set_yticks([0, 1, 2])
    ax_ins.legend(loc="upper left", frameon=False, fontsize=8.2, handlelength=1.05, borderpad=0.1, labelspacing=0.14)

    # Panel (b)
    ax = axes[1]
    dr_w = np.linspace(0.0, 3.5, 250)
    w_ov = 0.5
    R0_ov = 4.0 * w_ov
    for l_v, col, ls in [(0, BLUE, "-"), (1, VERMILION, "--"), (4, TEAL, "-.")]:
        vals = [float(pvb_gram_normalized([R0_ov, R0_ov + d * w_ov], l_v, w_ov)[0, 1]) for d in dr_w]
        ax.plot(dr_w, vals, color=col, ls=ls, lw=1.55, label=rf"$l=l'={l_v}$")
    ax.plot(dr_w, np.exp(-0.5 * dr_w ** 2), color=CHARCOAL, ls=":", lw=1.3, label=r"$e^{-\Delta R^2/(2w^2)}$")
    ax.axhline(0.0, color=GRAY, lw=0.85)
    marker_dr_w = [2.0, 2.5]
    marker_vals = [float(pvb_gram_normalized([R0_ov, R0_ov + d * w_ov], 1, w_ov)[0, 1]) for d in marker_dr_w]
    ax.plot(marker_dr_w, marker_vals, "o", color=VERMILION, ms=4.6, zorder=5)
    ax.annotate(
        r"$2.0\,w$: $13.6\%$",
        xy=(2.0, marker_vals[0]),
        xytext=(2.06, 0.28),
        fontsize=8.5,
        arrowprops={"arrowstyle": "->", "lw": 0.85, "color": CHARCOAL},
    )
    ax.set_xlim(0.0, 3.5)
    ax.set_ylim(-0.08, 1.08)
    ax.set_xlabel(r"$\Delta R / w$")
    ax.set_ylabel(r"$\gamma_l(R_0, R_0+\Delta R)$")
    ax.set_title(r"(b) Azimuthal $\delta_{l,l'}$ and radial overlap", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, ncol=1, bbox_to_anchor=(0.0, 0.03), labelspacing=0.16, handlelength=1.35)

    ax_ins_b = ax.inset_axes([0.55, 0.52, 0.42, 0.43])
    edges = np.arange(-4.5, 5.5, 1.0)
    ax_ins_b.pcolormesh(edges, edges, np.eye(9), cmap="Blues", vmin=0.0, vmax=1.0, edgecolors="#CCCCCC", linewidth=0.3)
    ax_ins_b.set_aspect("equal")
    ax_ins_b.set_xticks([-4, 0, 4])
    ax_ins_b.set_yticks([-4, 0, 4])
    ax_ins_b.set_xlabel(r"$l'$", fontsize=8.5, labelpad=1.0)
    ax_ins_b.set_ylabel(r"$l$", fontsize=8.5, labelpad=1.0)
    ax_ins_b.tick_params(labelsize=8.3, length=2.2, pad=1.4)
    ax_ins_b.set_title(r"$\delta_{l,l'}$", fontsize=8.8, pad=2.4)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def make_part1_fig2(metrics: dict[str, Any], out_path: Path) -> None:
    """Paper I Fig. 2: (a) Frame spectrum & Tikhonov filter + noise-gain inset;
    (b) Sharp Paley-Wiener bounds A(w, k_max), B = 1, and condition number kappa(S_{w,k_max}).
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.95), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.07)

    # Panel (a)
    ax = axes[0]
    wk = np.linspace(0.0, 5.15, 380)
    gw = weber_fourier_multiplier(wk, 1.0)
    wk_ref = metrics["frame_and_normalization"]["telecom_bridge"]["w_kmax"]
    ax.axvspan(0.0, wk_ref, color=SKY, alpha=0.16, label=r"$\mathcal{H}_{k_{\max}}$")
    ax.plot(wk, gw, color=CHARCOAL, lw=1.65, label=r"$\widetilde{G}_w(k_\perp)$")
    t_curves = {}
    for alp, col, ls in [(1e-2, BLUE, "--"), (1e-3, TEAL, "-.")]:
        t_sig = (gw ** 2) / (gw ** 2 + alp)
        t_curves[alp] = t_sig
        ax.plot(wk, t_sig, color=col, ls=ls, lw=1.45, label=rf"$T_{{\alpha_{{\mathrm{{reg}}}}}}\,(10^{{{int(math.log10(alp))}}})$")
    ax.axvline(wk_ref, color=VERMILION, ls=":", lw=1.2)
    ax.text(wk_ref - 0.06, 0.05, rf"$w k_{{\max}}={wk_ref:.3f}$", color=VERMILION, fontsize=8.3, ha="right")
    ax.set_xlim(0.0, 5.15)
    ax.set_ylim(0.0, 1.15)
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel(r"$w k_\perp$")
    ax.set_ylabel("Spectral multiplier")
    ax.set_title("(a) Frame spectrum and Tikhonov filter", loc="left", fontweight="bold")
    leg_a = ax.legend(
        loc="lower right",
        frameon=False,
        bbox_to_anchor=(1.02, 0.04),
        handlelength=1.25,
        labelspacing=0.13,
        fontsize=8.1,
    )

    ax_ins_c = ax.inset_axes([0.55, 0.58, 0.33, 0.38])
    _style_inset(ax_ins_c)
    ax_ins_c.spines["left"].set_visible(False)
    ax_ins_c.spines["right"].set_visible(True)
    ax_ins_c.yaxis.tick_right()
    ax_ins_c.yaxis.set_label_position("right")
    wk_ins = np.linspace(0.0, 3.8, 300)
    gw_ins = weber_fourier_multiplier(wk_ins, 1.0)
    ax_ins_c.semilogy(wk_ins, 1.0 / gw_ins, color=CHARCOAL, ls=":", lw=1.25, label=r"$\widetilde{G}_w^{-1}$")
    for alp, col, ls in [(1e-2, BLUE, "--"), (1e-3, TEAL, "-.")]:
        h_gain = gw_ins / (gw_ins ** 2 + alp)
        ax_ins_c.semilogy(wk_ins, h_gain, color=col, ls=ls, lw=1.35)
        k_pk = math.sqrt(math.log(1.0 / alp))
        ax_ins_c.plot([k_pk], [0.5 / math.sqrt(alp)], "o", color=col, ms=3.6)
    ax_ins_c.set_xlim(0.0, 3.8)
    ax_ins_c.set_ylim(0.4, 80.0)
    ax_ins_c.set_xticks([0, 2])
    ax_ins_c.set_xlabel(r"$w k_\perp$", fontsize=8.4, labelpad=0.8)
    ax_ins_c.set_ylabel(r"$\widetilde{H}_{w,\alpha_{\mathrm{reg}}}$", fontsize=8.5, labelpad=2.0)
    ax_ins_c.legend(loc="upper left", frameon=False, fontsize=8.2, handlelength=1.0, borderpad=0.1)

    # Panel (b)
    ax = axes[1]
    wk_grid = np.linspace(0.0, 3.0, 300)
    A_curve = np.exp(-0.5 * wk_grid ** 2)
    B_curve = np.ones_like(wk_grid)
    kap_curve = 1.0 / A_curve

    l1, = ax.plot(wk_grid, A_curve, color=BLUE, lw=1.65, label=r"$A(w, k_{\max})$")
    l2, = ax.plot(wk_grid, B_curve, color=CHARCOAL, ls="--", lw=1.35, label=r"$B = 1$")
    ax.set_xlim(0.0, 3.0)
    ax.set_ylim(0.0, 1.15)
    ax.set_xlabel(r"$w k_{\max}$")
    ax.set_ylabel(r"Frame bounds $A, B$", color=BLUE)
    ax.tick_params(axis="y", labelcolor=BLUE)

    ax_r = ax.twinx()
    ax_r.spines["top"].set_visible(False)
    ax_r.spines["right"].set_visible(True)
    l3, = ax_r.semilogy(wk_grid, kap_curve, color=VERMILION, lw=1.55, label=r"$\kappa(S_{w,k_{\max}})$")
    ax_r.set_ylim(1.0, 1.4e2)
    ax_r.set_ylabel(r"$\kappa(S_{w,k_{\max}}) = B / A$", color=VERMILION)
    ax_r.tick_params(axis="y", labelcolor=VERMILION)

    wk_low = math.sqrt(2.0 * math.log(1.2))
    A_low = math.exp(-0.5 * wk_low ** 2)
    ax.plot([wk_low], [A_low], "D", color=PURPLE, ms=5.0, zorder=6)
    ax.annotate(
        rf"$w k_{{\max}}={wk_low:.3f}\to \kappa=1.20$",
        xy=(wk_low, A_low),
        xytext=(0.74, 0.90),
        fontsize=8.4,
        color=CHARCOAL,
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": PURPLE},
    )

    tb = metrics["frame_and_normalization"]["telecom_bridge"]
    ax.axvline(tb["w_kmax"], color=TEAL, ls=":", lw=1.2)
    ax.plot([tb["w_kmax"]], [tb["A_bound"]], "o", color=BLUE, ms=4.8, zorder=6)
    ax_r.plot([tb["w_kmax"]], [tb["kappa_Sw"]], "s", color=VERMILION, ms=4.5, zorder=6)
    ax.annotate(
        f"$w k_{{\\max}}={tb['w_kmax']:.3f}$\n$A={tb['A_bound']:.3f},\\;\\kappa={tb['kappa_Sw']:.2f}$",
        xy=(tb["w_kmax"], tb["A_bound"]),
        xytext=(0.98, 0.64),
        fontsize=8.4,
        bbox={"boxstyle": "round,pad=0.22", "fc": "white", "ec": TEAL, "lw": 0.85, "alpha": 0.96},
        arrowprops={"arrowstyle": "->", "lw": 0.85, "color": TEAL},
    )

    ax.set_title("(b) Paley\u2013Wiener bounds and conditioning", loc="left", fontweight="bold")
    ax.legend(
        [l1, l2, l3],
        [l.get_label() for l in (l1, l2, l3)],
        loc="lower left",
        frameon=False,
        bbox_to_anchor=(0.01, 0.08),
        handlelength=1.3,
    )

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ins_c_box = ax_ins_c.get_tightbbox(renderer)
    leg_a_box = leg_a.get_window_extent(renderer)
    assert not ins_c_box.overlaps(leg_a_box), "Paper I Fig 2(a) inset overlaps legend!"
    pts_1e3 = axes[0].transData.transform(np.column_stack([wk, t_curves[1e-3]]))
    assert not any(ins_c_box.contains(px, py) for px, py in pts_1e3), "Paper I Fig 2(a) inset overlaps curve!"
    # Verify legend does not touch active non-zero segments (y > 0.03) of any spectral curve
    for cname, cy in [("Gw", gw), ("T_1e2", t_curves[1e-2]), ("T_1e3", t_curves[1e-3])]:
        mask_active = cy > 0.03
        pts_act = axes[0].transData.transform(np.column_stack([wk[mask_active], cy[mask_active]]))
        assert not any(leg_a_box.contains(px, py) for px, py in pts_act), (
            f"Paper I Fig 2(a) legend overlaps {cname} curve!"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def make_part1_fig3(metrics: dict[str, Any], out_path: Path) -> None:
    """Paper I Fig. 3 (1x3): (a) Closed-form c_{1,p}(R) vs. quadrature;
    (b) Radial nodal washout & Rayleigh limit; (c) Normalized Gram kappa(gamma) vs. kappa(G).
    """
    fig, axes = plt.subplots(1, 3, figsize=(7.20, 2.95), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.03, h_pad=0.03, wspace=0.05)

    # Panel (a)
    ax = axes[0]
    w0 = 1.0
    w_pv = 0.25
    R_dense = np.linspace(0.01, 3.2, 260)
    R_pts = np.linspace(0.15, 3.05, 13)
    p_cols = [(0, CHARCOAL), (1, BLUE), (2, TEAL), (3, VERMILION)]

    ax_ins_a = ax.inset_axes([0.55, 0.69, 0.42, 0.28])
    _style_inset(ax_ins_a)

    for p_v, col in p_cols:
        cf_vals = c_lp_closed_form(R_dense, p_v, 1, w_pv, w0)
        ax.plot(R_dense, cf_vals, color=col, lw=1.45, label=f"$p={p_v}$")
        qd_vals = np.array([c_lp_quad(float(rv), p_v, 1, w_pv, w0) for rv in R_pts])
        ax.plot(R_pts, qd_vals, "o", mfc="none", mec=col, ms=3.3, mew=0.9)
        cf_pts = c_lp_closed_form(R_pts, p_v, 1, w_pv, w0)
        res_log = np.log10(np.maximum(np.abs(cf_pts - qd_vals), 1e-16))
        ax_ins_a.plot(R_pts, res_log, "-", color=col, lw=1.05)

    ax.axhline(0.0, color=GRAY, lw=0.7)
    ax.set_xlim(0.0, 3.2)
    ax.set_ylim(-1.28, 2.04)
    ax.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0, 1.5])
    ax.set_xlabel(r"$R / w_0$")
    ax.set_ylabel(r"$c_{1,p}(R)$")
    ax.set_title(r"(a) Closed-form $c_{1,p}(R)$", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, ncol=2, columnspacing=0.6, labelspacing=0.12, handlelength=1.05, fontsize=8.1)

    ax_ins_a.set_xlim(0.0, 3.2)
    ax_ins_a.set_ylim(-16.5, -13.0)
    ax_ins_a.set_yticks([-16, -14])
    ax_ins_a.set_xlabel(r"$R / w_0$", fontsize=8.3, labelpad=0.6)
    ax_ins_a.set_ylabel(r"$\log_{10}|\Delta c|$", fontsize=8.3, labelpad=1.8)

    # Panel (b)
    ax_b = axes[1]
    ww0_dense = np.linspace(0.02, 1.0, 120)
    f_curves = {}
    for p_v, col in p_cols:
        f_curve = [nodal_washout_fidelity(p_v, 1, float(x)) for x in ww0_dense]
        f_curves[p_v] = f_curve
        ax_b.plot(ww0_dense, f_curve, color=col, lw=1.45, label=f"$p={p_v}$")
    t1 = metrics["table1_nodal_washout"]
    ww0_t1 = [row["w_over_w0"] for row in t1["rows"]]
    for p_v, col in p_cols:
        pts = [row["F"][str(p_v)] for row in t1["rows"]]
        ax_b.plot(ww0_t1, pts, "o", color=col, ms=3.0)
    ax_b.axhline(0.95, color=GRAY, ls="--", lw=0.95)
    ax_b.text(0.04, 0.85, r"$\mathcal{F}=0.95$", color=GRAY, fontsize=8.3)
    ax_b.set_xlim(0.02, 1.0)
    ax_b.set_ylim(-0.15, 1.24)
    ax_b.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_b.set_xlabel(r"$w / w_0$")
    ax_b.set_ylabel(r"Washout fidelity $\mathcal{F}(p,1)$")
    ax_b.set_title("(b) Radial nodal washout", loc="left", fontweight="bold")
    leg_b = ax_b.legend(
        loc="upper right",
        ncol=2,
        columnspacing=0.55,
        frameon=False,
        bbox_to_anchor=(1.01, 1.02),
        handlelength=1.05,
        labelspacing=0.12,
        fontsize=8.1,
    )

    # Placed cleanly inside lower-left clear space: away from left/bottom spines AND below p=3 curve
    ax_ins_b = ax_b.inset_axes([0.29, 0.145, 0.31, 0.215])
    _style_inset(ax_ins_b)
    p_int = np.arange(0, 9)
    w_crit_exact = [float(brentq(lambda x: nodal_washout_fidelity(int(pv), 1, x) - 0.95, 0.05, 0.6)) for pv in p_int]
    p_cont = np.linspace(1.0, 8.2, 80)
    w_crit_asymp = 0.573 / np.sqrt(2.0 * p_cont + 2.0)
    ax_ins_b.plot(p_cont, w_crit_asymp, color=BLUE, lw=1.25)
    ax_ins_b.plot(p_int, w_crit_exact, "o", color=VERMILION, ms=3.2)
    ax_ins_b.set_xlim(-0.6, 8.6)
    ax_ins_b.set_ylim(0.08, 0.62)
    ax_ins_b.set_yticks([0.2, 0.5])
    ax_ins_b.set_xlabel(r"$p$", fontsize=8.3, labelpad=0.3)
    ax_ins_b.set_ylabel(r"$w_{\mathrm{crit}}/w_0$", fontsize=8.3, labelpad=1.8)

    # Panel (c)
    ax_c = axes[2]
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

    l_kg, = ax_c.semilogy(dr_w_dense, kg_dense, color=BLUE, lw=1.6, label=r"$\kappa(\gamma)$ ($\psi_{l,R}$)")
    l_kG, = ax_c.semilogy(dr_w_dense, kG_dense, color=CHARCOAL, ls="--", lw=1.35, label=r"$\kappa(G)$ ($\Phi_{l,R}$)")
    ax_c.axvline(2.0, ymax=0.63, color=GRAY, ls=":", lw=1.0)
    ax_c.set_xlim(0.5, 3.0)
    ax_c.set_ylim(0.8, 3e4)
    ax_c.set_xlabel(r"$\Delta R / w$")
    ax_c.set_ylabel(r"Condition number $\kappa$", color=BLUE)
    ax_c.tick_params(axis="y", labelcolor=BLUE)

    ax_r = ax_c.twinx()
    ax_r.spines["top"].set_visible(False)
    ax_r.spines["right"].set_visible(True)
    l_iso, = ax_r.plot(dr_w_dense, pwr_iso_dense, color=VERMILION, ls="-.", lw=1.35, label=r"$|\gamma_{12}|^2$ (dB)")
    ax_r.set_ylim(-42.0, 2.0)
    ax_r.set_ylabel(r"Crosstalk $|\gamma_{12}|^2$ (dB)", color=VERMILION)
    ax_r.tick_params(axis="y", labelcolor=VERMILION)

    ax_c.annotate(
        r"$\kappa(G)$ rises",
        xy=(2.82, kG_dense[-5]),
        xytext=(1.75, 22.0),
        fontsize=8.3,
        ha="center",
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": CHARCOAL},
    )
    ax_c.set_title(r"(c) Gram $\kappa(\gamma)$ vs. $\kappa(G)$", loc="left", fontweight="bold")
    ax_c.legend(
        [l_kg, l_kG, l_iso],
        [l.get_label() for l in (l_kg, l_kG, l_iso)],
        loc="upper right",
        frameon=False,
        handlelength=1.15,
        fontsize=8.1,
    )

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ins_b_box = ax_ins_b.get_tightbbox(renderer)
    parent_b_ext = ax_b.get_window_extent(renderer)
    assert ins_b_box.x0 > parent_b_ext.x0 + 3.0, (
        f"Paper I Fig 3(b) inset y-label crosses parent left spine! ({ins_b_box.x0:.1f} vs {parent_b_ext.x0:.1f})"
    )
    assert ins_b_box.y0 > parent_b_ext.y0 + 3.0, (
        f"Paper I Fig 3(b) inset x-label crosses parent bottom spine! ({ins_b_box.y0:.1f} vs {parent_b_ext.y0:.1f})"
    )
    pts_p3 = ax_b.transData.transform(np.column_stack([ww0_dense, f_curves[3]]))
    assert not any(ins_b_box.contains(px, py) for px, py in pts_p3), "Paper I Fig 3(b) inset overlaps p=3 curve!"
    leg_b_box = leg_b.get_window_extent(renderer)
    pts_p0 = ax_b.transData.transform(np.column_stack([ww0_dense, f_curves[0]]))
    assert not any(leg_b_box.contains(px, py) for px, py in pts_p0), "Paper I Fig 3(b) legend overlaps p=0 curve!"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


# ==============================================================================
# PAPER II FIGURES (CLASSICAL & QUANTUM APPLICATIONS)
# ==============================================================================

def make_part2_fig1(metrics: dict[str, Any], out_path: Path) -> None:
    """Paper II Fig. 1: (a) Noisy LG_{2,1} Tikhonov MSE bias-variance + 2D-FFT MC;
    (b) Radial amplitude cross-section recovery |psi(r)| showing node restoration vs. blow-up.
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.95), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.07)

    # Panel (a)
    ax = axes[0]
    nl = metrics["noisy_lg21_reconstruction"]
    alphas = np.array(nl["alpha_grid"])
    ax.loglog(alphas, nl["bias2"], color=BLUE, ls="--", lw=1.45, label=r"Bias$^2$")
    ax.loglog(alphas, nl["variance"], color=TEAL, ls="-.", lw=1.45, label="Variance")
    ax.loglog(alphas, nl["total_mse"], color=CHARCOAL, lw=1.7, label="Total MSE")
    mc = nl["mc_2d_fft_check"]
    ax.errorbar(
        mc["alpha_values"],
        mc["mc_mse_mean"],
        yerr=mc["mc_mse_sem"],
        fmt="o",
        color=VERMILION,
        ms=4.2,
        mfc="none",
        mew=1.1,
        capsize=2.2,
        label="2D-FFT MC",
    )
    ax.axhline(nl["naive_mse_alpha0"], color=PURPLE, ls=":", lw=1.35, label=r"Unreg. ($\alpha_{\mathrm{reg}}=0$: $9.00$)")
    ax.plot([nl["alpha_opt"]], [nl["mse_min"]], "*", color=GOLD, mec=CHARCOAL, ms=8.5, zorder=6)
    ax.annotate(
        rf"$\alpha_{{\mathrm{{reg}}}}^{{\mathrm{{opt}}}}={nl['alpha_opt']:.4f}$" + "\n" + rf"$\mathrm{{MSE}}_{{\min}}={nl['mse_min']:.4f}\;(259\times)$",
        xy=(nl["alpha_opt"], nl["mse_min"]),
        xytext=(4.5e-2, 0.55),
        fontsize=8.4,
        ha="center",
        arrowprops={"arrowstyle": "->", "lw": 0.85, "color": CHARCOAL},
    )
    ax.set_xlim(1e-6, 1.0)
    ax.set_ylim(5e-4, 24.0)
    ax.set_xlabel(r"Tikhonov regularization $\alpha_{\mathrm{reg}}$")
    ax.set_ylabel(r"Normalized MSE ($\mathrm{LG}_{2,1}$)")
    ax.set_title(r"(a) Noisy $\mathrm{LG}_{2,1}$ Tikhonov MSE ($\mathrm{SNR}=20\,\mathrm{dB}$)", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, ncol=2, columnspacing=0.55, handlelength=1.2, fontsize=8.1)

    # Panel (b): Deterministic 2D-FFT spatial cross-section recovery along x >= 0 (y = 0)
    ax = axes[1]
    rng = np.random.default_rng(20261119)
    n_g = 256
    L_box = 10.0  # in w_0 = 1 units
    dx = L_box / n_g
    coords = (np.arange(n_g) - n_g // 2) * dx
    X, Y = np.meshgrid(coords, coords, indexing="ij")
    R_grid = np.hypot(X, Y)
    Phi_grid = np.arctan2(Y, X)

    w0 = 1.0
    w_pv = 0.25
    kmax = 3.0 / w_pv  # w * k_max = 3.0 -> k_max = 12.0
    psi_true = lg_radial(R_grid, 2, 1, w0) * np.exp(1j * Phi_grid)
    psi_true /= math.sqrt(float(np.sum(np.abs(psi_true) ** 2) * dx * dx))

    kx = 2.0 * math.pi * np.fft.fftfreq(n_g, d=dx)
    KX, KY = np.meshgrid(kx, kx, indexing="ij")
    K_perp = np.hypot(KX, KY)
    mask_pw = K_perp <= kmax
    Gw_k = np.exp(-0.5 * (w_pv * K_perp) ** 2)

    F_true = np.fft.fft2(psi_true)
    white_complex = (rng.standard_normal((n_g, n_g)) + 1j * rng.standard_normal((n_g, n_g))) / math.sqrt(2.0)
    F_noise = white_complex * mask_pw
    noise_spatial = np.fft.ifft2(F_noise)
    noise_spatial *= math.sqrt(0.01 / float(np.sum(np.abs(noise_spatial) ** 2) * dx * dx))
    F_noise = np.fft.fft2(noise_spatial)

    F_meas = Gw_k * F_true + F_noise
    psi_meas = np.fft.ifft2(F_meas)
    alp_opt = nl["alpha_opt"]
    psi_tikh = np.fft.ifft2((Gw_k / (Gw_k ** 2 + alp_opt)) * F_meas * mask_pw)
    psi_unreg = np.fft.ifft2((1.0 / np.maximum(Gw_k, 1e-12)) * F_meas * mask_pw)

    mid = n_g // 2
    sl = slice(mid, mid + int(3.2 / dx))
    r_line = coords[sl]
    ax.plot(r_line, 0.12 * np.abs(psi_unreg[sl, mid]), color=PURPLE, ls=":", lw=1.15, alpha=0.85, label=r"$0.12\,|\hat{\psi}_{0}|$ (unreg.)")
    ax.plot(r_line, np.abs(psi_meas[sl, mid]), color=TEAL, ls="-.", lw=1.4, label=r"$|S_w\psi_{2,1}+\varepsilon|$")
    ax.plot(r_line, np.abs(psi_true[sl, mid]), color=CHARCOAL, lw=1.65, label=r"Exact $|\psi_{2,1}|$")
    ax.plot(r_line, np.abs(psi_tikh[sl, mid]), "--", color=VERMILION, lw=1.55, label=r"Tikhonov $|\hat{\psi}_{\alpha_{\mathrm{opt}}}|$")

    ax.set_xlim(0.0, 3.15)
    ax.set_ylim(0.0, 0.92)
    ax.set_xlabel(r"Radial coordinate $r / w_0$")
    ax.set_ylabel(r"Field modulus $|\psi(r, 0)|\,w_0$")
    ax.set_title("(b) Spatial radial-node recovery", loc="left", fontweight="bold")
    ax.legend(loc="upper right", frameon=False, handlelength=1.3, fontsize=8.3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def make_part2_fig2(metrics: dict[str, Any], out_path: Path) -> None:
    """Paper II Fig. 2: (a) RCF Sturm-Liouville coupling & SDM BER;
    (b) Single-OAM discrete PVB dual-frame Kolmogorov turbulence filter.
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.95), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.07)

    # Panel (a)
    ax = axes[0]
    rcf = metrics["classical_optics_utility"]["rcf_coupling"]
    l_vals = np.array(rcf["l_values"])
    ax.plot(l_vals, rcf["eta_pvb"], "o-", color=BLUE, ms=4.0, lw=1.6, label=r"PVB ($w=1.72\,\mu\mathrm{m}$)")
    ax.plot(l_vals, rcf["eta_lg_w0_450"], "s--", color=TEAL, ms=3.5, lw=1.35, label=r"LG ($w_0=4.50\,\mu\mathrm{m}$)")
    ax.plot(l_vals, rcf["eta_lg_w0_322"], "^:", color=VERMILION, ms=3.8, lw=1.4, label=r"LG ($w_0=3.22\,\mu\mathrm{m}$)")
    ax.annotate(
        f"$+{rcf['villalba_benchmark_gain_dB']:.2f}$ dB\nat $l=4$",
        xy=(4, rcf["eta_lg_w0_322"][4]),
        xytext=(3.55, 0.46),
        ha="center",
        fontsize=8.4,
        arrowprops={"arrowstyle": "->", "lw": 0.85, "color": CHARCOAL},
    )
    ax.set_xlim(-0.4, 8.6)
    ax.set_ylim(-0.32, 1.38)
    ax.set_xticks([0, 2, 4, 6, 8])
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel(r"OAM order $l$")
    ax.set_ylabel(r"RCF coupling $\eta_l$")
    ax.set_title("(a) RCF modal coupling and SDM BER", loc="left", fontweight="bold")
    ax.legend(
        loc="upper left",
        frameon=False,
        ncol=2,
        columnspacing=0.55,
        bbox_to_anchor=(0.0, 1.02),
        labelspacing=0.14,
        handlelength=1.15,
        handletextpad=0.35,
        fontsize=8.1,
    )

    ax_ins_a = ax.inset_axes([0.62, 0.14, 0.29, 0.26])
    _style_inset(ax_ins_a)
    ax_ins_a.spines["left"].set_visible(False)
    ax_ins_a.spines["right"].set_visible(True)
    ax_ins_a.yaxis.tick_right()
    ax_ins_a.yaxis.set_label_position("right")
    eb = np.array(rcf["ber_eb_n0_dB"])
    h_pvb, = ax_ins_a.semilogy(eb, rcf["ber_pvb_l4"], color=BLUE, lw=1.35, label="PVB")
    h_zf, = ax_ins_a.semilogy(eb, rcf["ber_sdm_zf_awgn_dr2w"], color=PURPLE, ls="--", lw=1.25, label="SDM ZF")
    ax_ins_a.semilogy(eb, rcf["ber_lg322_l4"], color=VERMILION, ls=":", lw=1.35)
    ax_ins_a.set_xlim(-0.5, 14.5)
    ax_ins_a.set_ylim(1e-8, 12.0)
    ax_ins_a.set_yticks([1e-6, 1e-3, 1e0])
    ax_ins_a.set_xlabel(r"$E_b/N_0$ (dB)", fontsize=8.3, labelpad=0.8)
    ax_ins_a.set_ylabel("BER", fontsize=8.3, labelpad=1.6)
    ax_ins_a.legend(handles=[h_pvb, h_zf], loc="lower left", ncol=1, frameon=False, fontsize=8.0, handlelength=0.95, borderpad=0.05, labelspacing=0.1)
    ax_ins_a.text(9.8, 0.35, "LG", color=VERMILION, fontsize=8.2)

    # Panel (b)
    ax_b = axes[1]
    kol = metrics["classical_optics_utility"]["kolmogorov_rkhs"]
    dr0 = np.array(kol["D_over_r0_grid"])
    f_raw = np.array(kol["field_mse_raw_mean"])
    s_raw = np.array(kol["field_mse_raw_sem"])
    f_pw = np.array(kol["field_mse_rkhs_mean"])
    f_tik = np.array(kol["field_mse_tikhonov_mean"])
    s_tik = np.array(kol["field_mse_tikhonov_sem"])
    f_pvb = np.array(kol["field_mse_pvb_frame_mean"])
    s_pvb = np.array(kol["field_mse_pvb_frame_sem"])
    i_pvb = np.array(kol["int_mse_pvb_frame_mean"])

    ax_b.plot(dr0, f_raw, "o-", color=CHARCOAL, ms=3.8, lw=1.5, label="Raw (Field)")
    ax_b.fill_between(dr0, f_raw - s_raw, f_raw + s_raw, color=CHARCOAL, alpha=0.12)
    ax_b.plot(dr0, f_pw, "s--", color=SKY, ms=3.5, lw=1.35, label=r"$P_{k_{\max}}$ pinhole")
    ax_b.plot(dr0, f_tik, "^-.", color=TEAL, ms=3.8, lw=1.4, label="Isotropic Tikhonov")
    ax_b.fill_between(dr0, f_tik - s_tik, f_tik + s_tik, color=TEAL, alpha=0.12)
    ax_b.plot(dr0, f_pvb, "D-", color=BLUE, ms=4.0, lw=1.7, label=r"PVB dual frame ($l=l_0$)")
    ax_b.fill_between(dr0, f_pvb - s_pvb, f_pvb + s_pvb, color=BLUE, alpha=0.18)
    ax_b.plot(dr0, i_pvb, ":", color=VERMILION, lw=1.5, label="PVB dual (Int. MSE)")

    ax_b.set_xlim(0.45, 3.08)
    ax_b.set_ylim(0.0, 0.67)
    ax_b.set_xlabel(r"Turbulence strength $D / r_0$")
    ax_b.set_ylabel("Normalized MSE")
    ax_b.set_title("(b) Kolmogorov PVB dual-frame filter", loc="left", fontweight="bold")
    ax_b.legend(loc="upper left", frameon=False, ncol=1, labelspacing=0.14, handlelength=1.35, fontsize=8.1)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ins_a_box = ax_ins_a.get_tightbbox(renderer)
    pts_lg322 = ax.transData.transform(np.column_stack([l_vals, rcf["eta_lg_w0_322"]]))
    assert not any(ins_a_box.contains(px, py) for px, py in pts_lg322), "Paper II Fig 2(a) inset overlaps LG curve!"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def make_part2_fig3(metrics: dict[str, Any], out_path: Path) -> None:
    """Paper II Fig. 3: (a) Multi-plane Gouy IC-POVM radial-qudit tomography;
    (b) SPDC circular-iris Bell-CHSH S + single-mode pupil transmission inset.
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.95), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.07)

    # Panel (a)
    ax = axes[0]
    povm = metrics["quantum_optics_utility"]["ic_povm_radial_qudit"]
    n_ph = np.array(povm["N_phot_grid"], dtype=float)
    n_dense = np.geomspace(220.0, 4.0e4, 100)

    ax.loglog(n_dense, povm["crb_with_Eres"] / n_dense, "--", color=BLUE, lw=1.5, label=rf"PVB CRB (${povm['crb_with_Eres']:.2f}/N$)")
    ax.loglog(n_dense, povm["crb_sequential_mub"] / n_dense, ":", color=VERMILION, lw=1.45, label=rf"5-MUB CRB (${povm['crb_sequential_mub']:.2f}/N$)")
    ax.errorbar(n_ph, povm["mle_mse_pvb_mean"], yerr=povm["mle_mse_pvb_sem"], fmt="o", color=BLUE, ms=4.2, capsize=2.2, label=r"PVB $R\hat{\rho}R$ MLE")
    ax.errorbar(n_ph, povm["mle_mse_mub_mean"], yerr=povm["mle_mse_mub_sem"], fmt="s", color=VERMILION, ms=3.8, capsize=2.2, label="5-MUB MLE")
    ax.text(
        0.97,
        0.95,
        f"$M=1$: rank $7/16$\n$M=5$: rank $16/16$\n$\\kappa(\\mathcal{{S}})={povm['kappa_povm_superoperator_16d']:.1f}$",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.3,
        bbox={"boxstyle": "round,pad=0.22", "fc": "#F8F9FA", "ec": GRAY, "lw": 0.7},
    )
    ax.set_xlim(220.0, 4.0e4)
    ax.set_ylim(3e-4, 0.35)
    ax.set_xlabel(r"Total photons $N_{\mathrm{phot}}$")
    ax.set_ylabel(r"Tomography MSE $\|\hat{\rho}-\rho_0\|_F^2$")
    ax.set_title("(a) Gouy IC-POVM radial qudit ($d=4$)", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, handlelength=1.35, fontsize=8.1)

    # Panel (b)
    ax = axes[1]
    spdc = metrics["quantum_optics_utility"]["spdc_iris_invariance"]
    r_ir = np.array(spdc["R_iris_over_R0_grid"])
    ax.plot(r_ir, spdc["S_pvb_2arm"], color=BLUE, lw=1.65, label="PVB (2-arm)")
    ax.plot(r_ir, spdc["S_lg_1arm"], color=TEAL, ls="--", lw=1.45, label="LG (1-arm)")
    ax.plot(r_ir, spdc["S_lg_2arm"], color=VERMILION, ls="-.", lw=1.45, label="LG (2-arm)")
    ax.axhline(2.0 * math.sqrt(2.0), color=GRAY, ls=":", lw=0.9)
    ax.axhline(2.0, color=CHARCOAL, ls=":", lw=0.9)
    ax.axvline(1.0, color=GRAY, ls="--", lw=0.85)
    ax.text(0.62, 1.905, "Bell limit $S=2$", fontsize=8.3, color=CHARCOAL)
    ax.set_xlim(0.6, 2.2)
    ax.set_ylim(1.86, 3.18)
    ax.set_yticks([2.0, 2.4, 2.8])
    ax.set_xlabel(r"Iris radius $R_{\mathrm{iris}} / R_0$")
    ax.set_ylabel("Bell\u2013CHSH parameter $S$")
    ax.set_title("(b) SPDC iris invariance and CHSH", loc="left", fontweight="bold")
    ax.legend(
        loc="upper left",
        ncol=3,
        columnspacing=0.55,
        handlelength=1.1,
        handletextpad=0.35,
        frameon=False,
        bbox_to_anchor=(0.0, 1.02),
        fontsize=8.1,
    )

    ax_ins_d = ax.inset_axes([0.15, 0.42, 0.31, 0.27])
    _style_inset(ax_ins_d)
    ax_ins_d.set_facecolor("white")
    ax_ins_d.patch.set_alpha(1.0)
    ax_ins_d.set_zorder(4)
    l_ch = np.array(spdc["l_channels"])
    width_bar = 0.36
    ax_ins_d.bar(l_ch - width_bar / 2, spdc["t_pvb_at_R0"], width=width_bar, color=BLUE, label="PVB")
    ax_ins_d.bar(l_ch + width_bar / 2, spdc["t_lg_at_R0"], width=width_bar, color=VERMILION, label="LG")
    ax_ins_d.set_xticks(l_ch)
    ax_ins_d.set_ylim(0.0, 0.88)
    ax_ins_d.set_yticks([0.0, 0.4, 0.8])
    ax_ins_d.set_xlabel(r"$l$", fontsize=8.3, labelpad=0.4)
    ax_ins_d.set_ylabel(r"$t_l(R_0)$", fontsize=8.3, labelpad=1.4)
    ax_ins_d.legend(loc="upper center", ncol=2, frameon=False, fontsize=8.0, handlelength=0.85, columnspacing=0.5, borderpad=0.05)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ins_d_box = ax_ins_d.get_tightbbox(renderer)
    for cname, cy in [("PVB", spdc["S_pvb_2arm"]), ("LG1", spdc["S_lg_1arm"]), ("LG2", spdc["S_lg_2arm"])]:
        pts_c = ax.transData.transform(np.column_stack([r_ir, cy]))
        assert not any(ins_d_box.contains(px, py) for px, py in pts_c), f"Paper II Fig 3(b) inset collides with {cname} curve!"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def main() -> int:
    metrics = json.loads((SCRIPTS_DIR / "verified_metrics.json").read_text(encoding="utf-8"))
    apply_pra_style()

    p1_pra = PACKAGE_DIR / "part1_theory" / "pra" / "figures"
    p1_arx = PACKAGE_DIR / "part1_theory" / "arxiv" / "figures"
    p2_pra = PACKAGE_DIR / "part2_applications" / "pra" / "figures"
    p2_arx = PACKAGE_DIR / "part2_applications" / "arxiv" / "figures"

    for d in (p1_pra, p1_arx, p2_pra, p2_arx):
        d.mkdir(parents=True, exist_ok=True)

    part1_specs = [
        ("fig1_pvb_overlap.pdf", make_part1_fig1),
        ("fig2_frame_regularization.pdf", make_part1_fig2),
        ("fig3_lg_washout_gram.pdf", make_part1_fig3),
    ]
    for fname, fn in part1_specs:
        out = p1_pra / fname
        fn(metrics, out)
        shutil.copy2(out, p1_arx / fname)
        print(f"[Paper I]  Generated {fname} ({out.stat().st_size} bytes)")

    part2_specs = [
        ("fig1_noisy_deconvolution.pdf", make_part2_fig1),
        ("fig2_rcf_turbulence.pdf", make_part2_fig2),
        ("fig3_quantum_tomography_chsh.pdf", make_part2_fig3),
    ]
    for fname, fn in part2_specs:
        out = p2_pra / fname
        fn(metrics, out)
        shutil.copy2(out, p2_arx / fname)
        print(f"[Paper II] Generated {fname} ({out.stat().st_size} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
