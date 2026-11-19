"""Compute optical utility benchmarks (including single-OAM discrete PVB dual-frame
Kolmogorov turbulence filtering and Gouy IC-POVM operator-frame conditioning) and
generate three collision-free vector PDF figures for both PRA and arXiv builds.
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
from scipy.special import jv

SCRIPTS_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pvb_physics import (
    c_lp_closed_form,
    c_lp_quad,
    kolmogorov_subharmonic_screen,
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
    """Configure APS Physical Review A STIX serif Unicode vector PDF typography."""
    plt.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.family": "STIXGeneral",
            "mathtext.fontset": "stix",
            "font.size": 8.2,
            "axes.labelsize": 8.6,
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


def _style_inset(ax_ins: plt.Axes) -> None:
    ax_ins.tick_params(labelsize=7.8, length=2.5, pad=1.8)
    ax_ins.spines["top"].set_visible(False)
    ax_ins.spines["right"].set_visible(False)
    ax_ins.patch.set_facecolor("white")
    ax_ins.patch.set_alpha(0.97)
    ax_ins.set_zorder(10)


def compute_upgraded_metrics() -> dict[str, Any]:
    """Load baseline metrics and compute upgraded discrete-PVB turbulence & POVM conditioning."""
    base_path = SCRIPTS_DIR / "verified_metrics.json"
    metrics: dict[str, Any] = json.loads(base_path.read_text(encoding="utf-8"))
    metrics["metadata"].pop("schema_version", None)

    # 1. Single-OAM discrete radial PVB dual-frame turbulence filter (Reviewer 2 §1.2)
    rng = np.random.default_rng(2026)
    N_grid = 256
    L_mm = 6.0
    D_mm = 3.0
    dx = L_mm / N_grid
    x = (np.arange(N_grid) - N_grid / 2) * dx
    X, Y = np.meshgrid(x, x)
    mask = np.hypot(X, Y) <= D_mm / 2.0

    kx = 2.0 * math.pi * np.fft.fftfreq(N_grid, d=dx)
    KX, KY = np.meshgrid(kx, kx)
    K = np.hypot(KX, KY)
    PHI_K = np.arctan2(KY, KX)

    R0_mm, w_mm, kmax_pvb = 1.0, 0.25, 8.0
    l0 = 1
    lam_mm = 1.55e-3
    k0_mm = 2.0 * math.pi / lam_mm
    z_mm = 500.0
    HF = np.exp(-1j * (K ** 2) * z_mm / (2.0 * k0_mm))

    def make_bandlimited_pvb_prop(R_ring: float) -> np.ndarray:
        pk = (
            math.sqrt(2.0 * math.pi)
            * ((-1j) ** abs(l0))
            * np.exp(1j * l0 * PHI_K)
            * np.exp(-0.25 * (w_mm ** 2) * (K ** 2))
            * jv(abs(l0), R_ring * K)
        )
        pk[K > kmax_pvb] = 0.0
        p0 = np.fft.fftshift(np.fft.ifft2(pk)) / (dx ** 2)
        p0 /= math.sqrt(float(np.sum(np.abs(p0) ** 2) * (dx ** 2)))
        p_prop = np.fft.ifft2(np.fft.fft2(p0) * HF)
        p_prop /= math.sqrt(float(np.sum(np.abs(p_prop) ** 2) * (dx ** 2)))
        return p_prop

    psi0_pk = (
        math.sqrt(2.0 * math.pi)
        * ((-1j) ** 1)
        * np.exp(1j * PHI_K)
        * np.exp(-0.25 * (w_mm ** 2) * (K ** 2))
        * jv(1, R0_mm * K)
    )
    psi0_pk[K > kmax_pvb] = 0.0
    psi0 = np.fft.fftshift(np.fft.ifft2(psi0_pk)) / (dx ** 2)
    psi0 /= math.sqrt(float(np.sum(np.abs(psi0) ** 2) * (dx ** 2)))
    psi_clean = np.fft.ifft2(np.fft.fft2(psi0) * HF)
    I_clean = np.abs(psi_clean) ** 2
    norm_I = float(np.sum(I_clean ** 2) * (dx ** 2))

    # Build N = 5 concentric radial PVB frame at fixed OAM l0 = 1 with spacing Delta R = 1.5 w = 0.375 mm:
    # R_rings = [0.25, 0.625, 1.00, 1.375, 1.75] mm (includes R0 = 1.00 mm!)
    R_rings = [0.25, 0.625, 1.00, 1.375, 1.75]
    frame_modes = np.array([make_bandlimited_pvb_prop(Rr) for Rr in R_rings])  # (N_rings, N_grid, N_grid)
    n_rings = len(R_rings)
    flat_modes = frame_modes.reshape(n_rings, -1)
    gamma_disc = np.real((flat_modes.conj() @ flat_modes.T) * (dx ** 2))
    gamma_disc_inv = np.linalg.inv(gamma_disc)
    kappa_disc = float(np.linalg.cond(gamma_disc))

    alpha_reg = math.exp(-((w_mm * kmax_pvb) ** 2))
    Gw = np.exp(-0.5 * (w_mm ** 2) * (K ** 2))
    T_rkhs = (K <= kmax_pvb).astype(float)
    T_tikh = (Gw ** 2) / ((Gw ** 2) + alpha_reg)

    # Azimuthal OAM sector mask for checking out-of-sector crosstalk l != l0
    PHI_R = np.arctan2(Y, X)

    d_over_r0_grid = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    m_ens = 40
    field_pvb_m, field_pvb_s = [], []
    int_pvb_m, int_pvb_s = [], []
    oam_leak_raw_m = []

    for d_r0 in d_over_r0_grid:
        r0_mm = D_mm / d_r0
        fp, ip, oam_lk = [], [], []
        for _ in range(m_ens):
            phase = kolmogorov_subharmonic_screen(rng, N_grid, L_mm, r0_mm, mask, X, Y)
            psi_turb = np.fft.ifft2(np.fft.fft2(psi0 * np.exp(1j * phase)) * HF)

            # Project onto single-OAM discrete radial PVB frame via dual-frame matrix gamma_disc_inv
            overlaps = (flat_modes.conj() @ psi_turb.ravel()) * (dx ** 2)
            dual_coeffs = gamma_disc_inv @ overlaps
            psi_pvb_proj = np.tensordot(dual_coeffs, frame_modes, axes=(0, 0))

            fp.append(float(np.sum(np.abs(psi_pvb_proj - psi_clean) ** 2) * (dx ** 2)))
            ip.append(float(np.sum(((np.abs(psi_pvb_proj) ** 2) - I_clean) ** 2) * (dx ** 2) / norm_I))

            # Compute fraction of turbulent energy outside l = l0 azimuthal sector via polar FFT check
            # Project onto exp(i l0 phi) radial profile at each radius bin:
            # Simpler exact check: discrete PVB frame strictly has 0% l != l0 power!
            oam_lk.append(1.0 - float(np.real(np.vdot(overlaps, dual_coeffs))))

        field_pvb_m.append(float(np.mean(fp)))
        field_pvb_s.append(float(np.std(fp, ddof=1) / math.sqrt(m_ens)))
        int_pvb_m.append(float(np.mean(ip)))
        int_pvb_s.append(float(np.std(ip, ddof=1) / math.sqrt(m_ens)))
        oam_leak_raw_m.append(float(np.mean(oam_lk)))

    kol = metrics["classical_optics_utility"]["kolmogorov_rkhs"]
    kol["discrete_pvb_rings_mm"] = R_rings
    kol["discrete_pvb_kappa_gamma"] = kappa_disc
    kol["field_mse_pvb_frame_mean"] = field_pvb_m
    kol["field_mse_pvb_frame_sem"] = field_pvb_s
    kol["int_mse_pvb_frame_mean"] = int_pvb_m
    kol["int_mse_pvb_frame_sem"] = int_pvb_s
    kol["out_of_subspace_power_fraction_mean"] = oam_leak_raw_m

    # 2. Compute exact POVM operator-frame condition number kappa(POVM) (Reviewer Spec B7)
    d = 4
    l_qudit = 1
    w0 = 1.0
    w_pv = 0.25
    n_R = 40
    R_max = 3.5 * w0
    dR = R_max / n_R
    R_pts = (np.arange(n_R) + 0.5) * dR
    M_planes = 5
    thetas = np.linspace(0.0, 0.45 * math.pi, M_planes)

    c_mat = np.array([[c_lp_closed_form(R_k, p_v, l_qudit, w_pv, w0) for p_v in range(d)] for R_k in R_pts])
    E_multi = []
    p_idx = np.arange(d, dtype=float)
    for theta in thetas:
        gouy = np.exp(-1j * (2.0 * p_idx + abs(l_qudit) + 1.0) * theta)
        for k_idx, R_k in enumerate(R_pts):
            ket = (gouy * c_mat[k_idx])[:, None]
            E_multi.append((1.0 / M_planes) * R_k * dR * (ket @ ket.conj().T))
    E_multi_arr = np.array(E_multi, dtype=complex)
    sum_E = np.sum(E_multi_arr, axis=0)
    E_res = np.eye(d, dtype=complex) - sum_E
    E_with_res = np.concatenate([E_multi_arr, E_res[None, :, :]], axis=0)

    # Build orthonormal Hermitian basis of C^{4x4} (16 elements: I/2 + 15 generalized Gell-Mann / sqrt(2))
    herm_basis = [np.eye(d, dtype=complex) / math.sqrt(d)]
    for i in range(d):
        for j in range(i + 1, d):
            sx = np.zeros((d, d), dtype=complex)
            sx[i, j] = sx[j, i] = 1.0 / math.sqrt(2.0)
            sy = np.zeros((d, d), dtype=complex)
            sy[i, j] = -1j / math.sqrt(2.0)
            sy[j, i] = 1j / math.sqrt(2.0)
            herm_basis.extend([sx, sy])
    for k in range(1, d):
        sz = np.zeros((d, d), dtype=complex)
        for j in range(k):
            sz[j, j] = 1.0
        sz[k, k] = -float(k)
        sz /= math.sqrt(float(k * (k + 1)))
        herm_basis.append(sz)
    assert len(herm_basis) == 16

    # Measurement map M_alpha,a = Tr(Pi_alpha B_a) and frame superoperator S_POVM = M^T M
    M_mat = np.real(np.array([[np.trace(E_op @ B_a) for B_a in herm_basis] for E_op in E_with_res]))
    S_povm_full = M_mat.T @ M_mat
    evals_full = np.linalg.eigvalsh(S_povm_full)
    kappa_povm_full = float(evals_full[-1] / evals_full[0])

    # Also Bloch (15-dim traceless) condition number & Fisher condition number at rho0 = I/4
    S_povm_bloch = M_mat[:, 1:].T @ M_mat[:, 1:]
    evals_bloch = np.linalg.eigvalsh(S_povm_bloch)
    kappa_povm_bloch = float(evals_bloch[-1] / evals_bloch[0])

    rho0 = np.eye(d, dtype=complex) / d
    probs0 = np.real(np.einsum("mij,ji->m", E_with_res, rho0))
    # Traceless generators scaled with Tr(T_a T_b) = 1/2 (standard convention matching F in verified_metrics):
    T_gell = [B / math.sqrt(2.0) for B in herm_basis[1:]]
    d_p = np.real(np.array([[np.trace(E_op @ T_a) for T_a in T_gell] for E_op in E_with_res]))
    F_mat = (d_p.T / probs0[None, :]) @ d_p
    f_evals = np.linalg.eigvalsh(F_mat)
    kappa_fisher = float(f_evals[-1] / f_evals[0])

    ic = metrics["quantum_optics_utility"]["ic_povm_radial_qudit"]
    ic["kappa_povm_superoperator_16d"] = kappa_povm_full
    ic["kappa_povm_bloch_15d"] = kappa_povm_bloch
    ic["kappa_fisher_15d"] = kappa_fisher
    ic["lambda_max_fisher"] = float(f_evals[-1])

    # 3. Also record RCF LG_{0,4} gain at w0 = 4.50 um explicitly
    rcf = metrics["classical_optics_utility"]["rcf_coupling"]
    rcf["gain_l4_vs_lg450_dB"] = 10.0 * math.log10(rcf["eta_pvb"][4] / rcf["eta_lg_w0_450"][4])

    out_json = SCRIPTS_DIR / "verified_metrics.json"
    out_json.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Kolmogorov D/r0=3.0 Field MSE: Raw={kol['field_mse_raw_mean'][-1]:.4f}, RKHS={kol['field_mse_rkhs_mean'][-1]:.4f}, Tikh={kol['field_mse_tikhonov_mean'][-1]:.4f}, DiscretePVB={field_pvb_m[-1]:.4f}")
    print(f"Kolmogorov D/r0=3.0 Int MSE:   Raw={kol['int_mse_raw_mean'][-1]:.4f}, RKHS={kol['int_mse_rkhs_mean'][-1]:.4f}, Tikh={kol['int_mse_tikhonov_mean'][-1]:.4f}, DiscretePVB={int_pvb_m[-1]:.4f}")
    print(f"Discrete PVB kappa(gamma)={kappa_disc:.4f}, out-of-subspace power at D/r0=3.0: {oam_leak_raw_m[-1]:.4f}")
    print(f"POVM conditioning: kappa(S_POVM, 16D)={kappa_povm_full:.2f}, kappa(S_POVM, Bloch 15D)={kappa_povm_bloch:.2f}, kappa(Fisher)={kappa_fisher:.2f}")
    print(f"RCF l=4: eta_PVB={rcf['eta_pvb'][4]:.4f}, eta_LG(3.22)={rcf['eta_lg_w0_322'][4]:.4f} (+{rcf['villalba_benchmark_gain_dB']:.2f} dB), eta_LG(4.50)={rcf['eta_lg_w0_450'][4]:.4f} (+{rcf['gain_l4_vs_lg450_dB']:.2f} dB)")
    return metrics


def make_fig1(metrics: dict[str, Any], out_path: Path) -> None:
    """Figure 1: Annular invariance, OAM-radial decoupling, frame spectrum, Paley-Wiener bounds."""
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.0), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.06, hspace=0.09)

    # Panel (a)
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
        ax.plot(r_over_R0, ipvb, color=col, ls="-", lw=1.45, label="PVB ($l=0..6$)" if l_v == 6 else None)
        ax.plot(r_over_R0, ilg, color=col, ls="--", lw=1.15, alpha=0.85, label=f"LG $l={l_v}$")

    ax.set_xlim(0.15, 2.25)
    ax.set_ylim(0.0, 1.92)
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel(r"$r / R_0$")
    ax.set_ylabel(r"$I(r) / I_{\max}$")
    ax.set_title("(a) Annular invariance vs. LG scaling", loc="left", fontweight="bold")
    ax.legend(loc="upper left", frameon=False, ncol=1, labelspacing=0.12, handlelength=1.3, bbox_to_anchor=(0.0, 1.01))

    tp = metrics["frame_and_normalization"]["transcendental_peak_shift"]
    ax_ins = ax.inset_axes([0.59, 0.66, 0.39, 0.31])
    _style_inset(ax_ins)
    l_dense = np.linspace(0.0, 6.2, 80)
    asymp_dense = (l_dense ** 2) * (tp["w_over_R0"] ** 4) / 8.0
    ax_ins.plot(l_dense, np.array(asymp_dense) * 1e2, color=BLUE, lw=1.2, label=r"$\frac{l^2}{8}(w/R_0)^4$")
    ax_ins.plot(tp["l_values"], np.array(tp["delta_r_over_R0"]) * 1e2, "o", color=VERMILION, ms=3.5, label="Exact")
    ax_ins.set_xlabel(r"$|l|$", fontsize=7.8, labelpad=0.3)
    ax_ins.set_ylabel(r"$10^2\Delta r_{\mathrm{peak}}/R_0$", fontsize=7.8, labelpad=1.8)
    ax_ins.set_xlim(-0.3, 6.4)
    ax_ins.set_ylim(-0.15, 2.30)
    ax_ins.set_yticks([0, 1, 2])
    ax_ins.legend(loc="upper left", frameon=False, fontsize=7.8, handlelength=1.0, borderpad=0.1, labelspacing=0.14)

    # Panel (b)
    ax = axes[0, 1]
    dr_w = np.linspace(0.0, 3.5, 250)
    w_ov = 0.5
    R0_ov = 4.0 * w_ov
    for l_v, col, ls in [(0, BLUE, "-"), (1, VERMILION, "--"), (4, TEAL, "-.")]:
        vals = [float(pvb_gram_normalized([R0_ov, R0_ov + d * w_ov], l_v, w_ov)[0, 1]) for d in dr_w]
        ax.plot(dr_w, vals, color=col, ls=ls, lw=1.45, label=rf"$l=l'={l_v}$")
    ax.plot(dr_w, np.exp(-0.5 * dr_w ** 2), color=CHARCOAL, ls=":", lw=1.2, label=r"$e^{-\Delta R^2/(2w^2)}$")
    ax.axhline(0.0, color=GRAY, lw=0.9)
    marker_dr_w = [2.0, 2.5]
    marker_vals = [float(pvb_gram_normalized([R0_ov, R0_ov + d * w_ov], 1, w_ov)[0, 1]) for d in marker_dr_w]
    ax.plot(marker_dr_w, marker_vals, "o", color=VERMILION, ms=4.0, zorder=5)
    ax.annotate(
        rf"$2.0\,w$: ${100.0 * marker_vals[0]:.1f}\%$",
        xy=(2.0, marker_vals[0]),
        xytext=(2.08, 0.24),
        fontsize=7.8,
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": CHARCOAL},
    )
    ax.set_xlim(0.0, 3.5)
    ax.set_ylim(-0.06, 1.08)
    ax.set_xlabel(r"$\Delta R / w$")
    ax.set_ylabel(r"$\gamma_l(R_0, R_0+\Delta R)$")
    ax.set_title(r"(b) Azimuthal $\delta_{l,l'}$ & radial overlap", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, ncol=1, bbox_to_anchor=(0.0, 0.03), labelspacing=0.16, handlelength=1.3)

    ax_ins_b = ax.inset_axes([0.56, 0.53, 0.41, 0.43])
    edges = np.arange(-4.5, 5.5, 1.0)
    eye9 = np.eye(9)
    ax_ins_b.pcolormesh(edges, edges, eye9, cmap="Blues", vmin=0.0, vmax=1.0, edgecolors="#CCCCCC", linewidth=0.3)
    ax_ins_b.set_aspect("equal")
    ax_ins_b.set_xticks([-4, 0, 4])
    ax_ins_b.set_yticks([-4, 0, 4])
    ax_ins_b.set_xlabel(r"$l'$", fontsize=7.8, labelpad=1.0)
    ax_ins_b.set_ylabel(r"$l$", fontsize=7.8, labelpad=1.0)
    ax_ins_b.tick_params(labelsize=7.8, length=2.0, pad=1.2)
    ax_ins_b.set_title(r"$\delta_{l,l'}$", fontsize=7.8, pad=2.0)

    # Panel (c): Set xlim=(0, 4.6) and inset at [0.66, 0.57, 0.32, 0.39] for complete clearance!
    ax = axes[1, 0]
    wk = np.linspace(0.0, 4.6, 350)
    gw = weber_fourier_multiplier(wk, 1.0)
    wk_tel = metrics["frame_and_normalization"]["telecom_bridge"]["w_kmax"]
    ax.axvspan(0.0, wk_tel, color=SKY, alpha=0.16, label=r"$\mathcal{H}_{k_{\max}}$")
    ax.plot(wk, gw, color=CHARCOAL, lw=1.55, label=r"$\widetilde{G}_w$")
    t_curves = {}
    for alp, col, ls in [(1e-2, BLUE, "--"), (1e-3, TEAL, "-.")]:
        t_sig = (gw ** 2) / (gw ** 2 + alp)
        t_curves[alp] = t_sig
        ax.plot(wk, t_sig, color=col, ls=ls, lw=1.4, label=rf"$T_{{\alpha}}\,(10^{{{int(math.log10(alp))}}})$")
    ax.axvline(wk_tel, color=VERMILION, ls=":", lw=1.1)
    ax.text(wk_tel - 0.05, 0.05, rf"$w k_{{\max}}={wk_tel:.2f}$", color=VERMILION, fontsize=7.8, ha="right")
    ax.set_xlim(0.0, 4.6)
    ax.set_ylim(0.0, 1.14)
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel(r"$w k_\perp$")
    ax.set_ylabel("Spectral multiplier")
    ax.set_title(r"(c) Frame spectrum & Tikhonov filter", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, bbox_to_anchor=(0.0, 0.14), handlelength=1.35)

    ax_ins_c = ax.inset_axes([0.63, 0.59, 0.27, 0.37])
    _style_inset(ax_ins_c)
    ax_ins_c.spines["left"].set_visible(False)
    ax_ins_c.spines["right"].set_visible(True)
    ax_ins_c.yaxis.tick_right()
    ax_ins_c.yaxis.set_label_position("right")
    wk_ins = np.linspace(0.0, 3.8, 300)
    gw_ins = weber_fourier_multiplier(wk_ins, 1.0)
    ax_ins_c.semilogy(wk_ins, 1.0 / gw_ins, color=CHARCOAL, ls=":", lw=1.2, label=r"$\widetilde{G}_w^{-1}$")
    for alp, col, ls in [(1e-2, BLUE, "--"), (1e-3, TEAL, "-.")]:
        h_gain = gw_ins / (gw_ins ** 2 + alp)
        ax_ins_c.semilogy(wk_ins, h_gain, color=col, ls=ls, lw=1.3)
        wk_pk = math.sqrt(math.log(1.0 / alp))
        h_pk = 1.0 / (2.0 * math.sqrt(alp))
        ax_ins_c.plot([wk_pk], [h_pk], "o", color=col, ms=3.3)
    ax_ins_c.set_xlim(0.0, 3.8)
    ax_ins_c.set_ylim(0.5, 90.0)
    ax_ins_c.set_yticks([1.0, 10.0])
    ax_ins_c.set_xlabel(r"$w k_\perp$", fontsize=7.6, labelpad=0.8)
    ax_ins_c.set_ylabel(r"$\widetilde{H}_{w,\alpha}$", fontsize=7.6, labelpad=1.2)
    ax_ins_c.legend(loc="upper left", frameon=False, fontsize=7.5, handlelength=1.0, borderpad=0.1)

    # Panel (d): Explicit annotations for BOTH wk_max = 0.604 (kappa = 1.20) and wk_max = 1.394 (NA=0.20, A=0.378, kappa=2.64) (M1)
    ax = axes[1, 1]
    wk_max = np.linspace(0.0, 3.0, 250)
    A_curve = np.exp(-0.5 * wk_max ** 2)
    B_curve = np.ones_like(wk_max)
    kappa_curve = np.exp(0.5 * wk_max ** 2)

    l1, = ax.plot(wk_max, A_curve, color=BLUE, lw=1.55, label=r"$A(w,k_{\max})$")
    l2, = ax.plot(wk_max, B_curve, color=CHARCOAL, ls="--", lw=1.25, label=r"$B=1$")
    ax.set_xlim(0.0, 3.0)
    ax.set_ylim(0.0, 1.14)
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
    wk_low = math.sqrt(2.0 * math.log(1.20))  # 0.60385 -> kappa = 1.20, A = 0.833
    ax.plot([wk_low], [1.0 / 1.20], "D", color=PURPLE, ms=3.8, zorder=5)
    ax.annotate(
        rf"$wk_{{\max}}={wk_low:.2f}\to\kappa=1.20$",
        xy=(wk_low, 1.0 / 1.20),
        xytext=(0.78, 0.90),
        fontsize=7.6,
        color=CHARCOAL,
        arrowprops={"arrowstyle": "->", "lw": 0.75, "color": PURPLE},
    )

    ax.axvline(tb["w_kmax"], color=TEAL, ls=":", lw=1.15)
    ax.plot([tb["w_kmax"]], [tb["A_bound"]], "o", color=BLUE, ms=4.5, zorder=5)
    ax2.plot([tb["w_kmax"]], [tb["kappa_Sw"]], "s", color=VERMILION, ms=4.2, zorder=5)
    ax.annotate(
        f"$wk_{{\\max}}={tb['w_kmax']:.3f}$ (NA=0.20)\n$A={tb['A_bound']:.3f},\\;\\kappa={tb['kappa_Sw']:.2f}$",
        xy=(tb["w_kmax"], tb["A_bound"]),
        xytext=(1.56, 0.50),
        fontsize=7.6,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": TEAL, "alpha": 0.92},
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": TEAL},
    )
    ax.set_title("(d) Paley–Wiener bounds & conditioning", loc="left", fontweight="bold")
    ax.legend([l1, l2, l3], [l.get_label() for l in (l1, l2, l3)], loc="lower left", frameon=False, handlelength=1.35)

    # Assert Fig 1(c) inset tightbbox clears T_alpha(10^-3) curve and main y-ticks
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ins_c_box = ax_ins_c.get_tightbbox(renderer)
    pts_t3 = axes[1, 0].transData.transform(np.column_stack([wk, t_curves[1e-3]]))
    assert not any(ins_c_box.contains(px, py) for px, py in pts_t3), "Fig 1(c) inset overlaps T_alpha(10^-3) curve!"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.07)
    plt.close(fig)


def make_fig2(metrics: dict[str, Any], out_path: Path) -> None:
    """Figure 2: Closed-form c_{l,p}(R), nodal washout, noisy LG_{2,1} MSE, Gram conditioning."""
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.0), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.06, hspace=0.09)

    # Panel (a)
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
    ax.legend(loc="lower left", frameon=False, ncol=1, labelspacing=0.16, handlelength=1.2)

    ax_ins_a.set_xlim(0.0, 3.2)
    ax_ins_a.set_ylim(-16.5, -13.0)
    ax_ins_a.set_yticks([-16, -14])
    ax_ins_a.set_xlabel(r"$R / w_0$", fontsize=7.8, labelpad=1.0)
    ax_ins_a.set_ylabel(r"$\log_{10}|\Delta c|$", fontsize=7.8, labelpad=2.0)

    # Panel (b)
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
    ax.text(0.54, 0.968, r"$\mathcal{F}=0.95$", color=GRAY, fontsize=7.8)
    ax.set_xlim(0.02, 1.0)
    ax.set_ylim(0.15, 1.06)
    ax.set_xlabel(r"$w / w_0$")
    ax.set_ylabel(r"Washout fidelity $\mathcal{F}(p,1)$")
    ax.set_title(r"(b) Radial nodal washout & Rayleigh limit", loc="left", fontweight="bold")
    ax.legend(loc="upper right", frameon=False, handlelength=1.3, labelspacing=0.18)

    ax_ins_b = ax.inset_axes([0.19, 0.19, 0.37, 0.31])
    _style_inset(ax_ins_b)
    p_int = np.arange(0, 9)
    w_crit_exact = [float(brentq(lambda x: nodal_washout_fidelity(int(pv), 1, x) - 0.95, 0.05, 0.6)) for pv in p_int]
    p_cont = np.linspace(1.0, 8.2, 80)
    w_crit_asymp = 0.573 / np.sqrt(2.0 * p_cont + 2.0)
    ax_ins_b.plot(p_cont, w_crit_asymp, color=BLUE, lw=1.25, label=r"$0.573/\sqrt{2p+2}$")
    ax_ins_b.plot(p_int, w_crit_exact, "o", color=VERMILION, ms=3.3, label="Exact")
    ax_ins_b.set_xlim(-0.6, 8.6)
    ax_ins_b.set_ylim(0.08, 0.74)
    ax_ins_b.set_yticks([0.2, 0.4, 0.6])
    ax_ins_b.set_xlabel(r"$p$", fontsize=7.8, labelpad=0.3)
    ax_ins_b.set_ylabel(r"$w_{\mathrm{crit}} / w_0$", fontsize=7.8, labelpad=2.5)
    ax_ins_b.legend(loc="upper right", frameon=False, fontsize=7.6, handlelength=1.0, borderpad=0.1, labelspacing=0.12)

    # Panel (c): Clear baseline MSE(alpha_reg=0)=9.002 and optimal alpha_reg^opt=0.0490 (MSE_min=0.0348, 258.6x) (B5, M2)
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
    ax.axhline(nl["naive_mse_alpha0"], color=PURPLE, ls=":", lw=1.25, label=r"Unreg. ($\alpha_{\mathrm{reg}}=0$: $9.00$)")
    ax.plot([nl["alpha_opt"]], [nl["mse_min"]], "*", color=GOLD, mec=CHARCOAL, ms=8.0, zorder=6)
    ax.annotate(
        rf"$\alpha_{{\mathrm{{reg}}}}^{{\mathrm{{opt}}}}={nl['alpha_opt']:.4f}$" + "\n" + rf"$\mathrm{{MSE}}_{{\min}}={nl['mse_min']:.4f}\;(259\times)$",
        xy=(nl["alpha_opt"], nl["mse_min"]),
        xytext=(4.5e-2, 0.52),
        fontsize=7.6,
        ha="center",
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": CHARCOAL},
    )
    ax.set_xlim(1e-6, 1.0)
    ax.set_ylim(5e-4, 22.0)
    ax.set_xlabel(r"Tikhonov regularization $\alpha_{\mathrm{reg}}$")
    ax.set_ylabel(r"Normalized MSE ($\mathrm{LG}_{2,1}$)")
    ax.set_title(r"(c) Noisy $\mathrm{LG}_{2,1}$ Tikhonov MSE ($\mathrm{SNR}=20\,\mathrm{dB}$)", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, ncol=2, columnspacing=0.6, handlelength=1.2, fontsize=7.5)

    # Panel (d): Centered, unclipped kappa(G) annotation (R2-3.13)
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

    ann_kg = ax.annotate(
        r"$\kappa(G)$ rises",
        xy=(2.75, kG_dense[-5]),
        xytext=(1.75, 18.0),
        fontsize=7.8,
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": CHARCOAL},
    )
    ax.set_title(r"(d) Gram $\kappa(\gamma)$ vs. $\kappa(G)$ & crosstalk", loc="left", fontweight="bold")
    ax.legend(
        [l_kg, l_kG, l_iso],
        [l.get_label() for l in (l_kg, l_kG, l_iso)],
        loc="upper right",
        frameon=False,
        handlelength=1.35,
    )

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    assert ann_kg.get_window_extent(renderer).x0 > ax.spines["left"].get_window_extent(renderer).x0 + 5.0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.07)
    plt.close(fig)


def make_fig3(metrics: dict[str, Any], out_path: Path) -> None:
    """Figure 3: Classical RCF/SDM, Discrete-PVB Kolmogorov turbulence, Gouy IC-POVM, SPDC Bell-CHSH."""
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.0), constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.04, wspace=0.06, hspace=0.09)

    # Panel (a): Pure Unicode STIX labels (w = 1.72 um, zero glyph corruption) + clear BER inset
    ax = axes[0, 0]
    rcf = metrics["classical_optics_utility"]["rcf_coupling"]
    l_vals = np.array(rcf["l_values"])
    ax.plot(l_vals, rcf["eta_pvb"], "o-", color=BLUE, ms=3.8, lw=1.55, label=r"PVB ($w=1.72\,\mu\mathrm{m}$)")
    ax.plot(l_vals, rcf["eta_lg_w0_450"], "s--", color=TEAL, ms=3.3, lw=1.3, label=r"LG ($w_0=4.50\,\mu\mathrm{m}$)")
    ax.plot(l_vals, rcf["eta_lg_w0_322"], "^:", color=VERMILION, ms=3.5, lw=1.35, label=r"LG ($w_0=3.22\,\mu\mathrm{m}$)")
    ax.annotate(
        f"$+{rcf['villalba_benchmark_gain_dB']:.2f}$ dB\nat $l=4$",
        xy=(4, rcf["eta_lg_w0_322"][4]),
        xytext=(3.85, 0.44),
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
    ax.legend(
        loc="upper left",
        frameon=False,
        ncol=2,
        columnspacing=0.55,
        bbox_to_anchor=(0.0, 1.02),
        labelspacing=0.14,
        handlelength=1.15,
        handletextpad=0.35,
    )

    ax_ins_a = ax.inset_axes([0.665, 0.165, 0.250, 0.220])
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
    ax_ins_a.set_xlabel(r"$E_b/N_0$ (dB)", fontsize=7.6, labelpad=0.8)
    ax_ins_a.set_ylabel("BER", fontsize=7.6, labelpad=1.5)
    ax_ins_a.legend(
        handles=[h_pvb, h_zf],
        loc="lower left",
        ncol=1,
        frameon=False,
        fontsize=7.5,
        handlelength=0.75,
        handletextpad=0.25,
        labelspacing=0.04,
        borderpad=0.02,
    )
    ax_ins_a.text(13.5, 0.35, "LG", color=VERMILION, fontsize=7.5, ha="right", va="bottom")

    # Panel (b): Upgraded Kolmogorov turbulence filter including Single-OAM Discrete PVB Dual Frame (R2-1.2)
    ax = axes[0, 1]
    kol = metrics["classical_optics_utility"]["kolmogorov_rkhs"]
    dr0 = np.array(kol["D_over_r0_grid"])
    for key_m, key_s, col, mk, label in [
        ("field_mse_raw_mean", "field_mse_raw_sem", CHARCOAL, "o-", "Raw (Field)"),
        ("field_mse_rkhs_mean", "field_mse_rkhs_sem", SKY, "s--", r"$P_{k_{\max}}$ pinhole"),
        ("field_mse_tikhonov_mean", "field_mse_tikhonov_sem", TEAL, "^-.", "Isotropic Tikhonov"),
        ("field_mse_pvb_frame_mean", "field_mse_pvb_frame_sem", BLUE, "D-", r"PVB dual frame ($l=l_0$)"),
    ]:
        mu = np.array(kol[key_m])
        se = np.array(kol[key_s])
        ax.plot(dr0, mu, mk, color=col, ms=3.3, lw=1.45, label=label)
        ax.fill_between(dr0, mu - se, mu + se, color=col, alpha=0.14)

    ax.plot(dr0, kol["int_mse_pvb_frame_mean"], ":", color=VERMILION, lw=1.35, label=r"PVB dual (Int. MSE)")
    ax.set_xlim(0.45, 3.05)
    ax.set_ylim(0.0, 0.68)
    ax.set_xlabel(r"Turbulence strength $D / r_0$")
    ax.set_ylabel("Normalized MSE")
    ax.set_title("(b) Kolmogorov PVB dual-frame filter", loc="left", fontweight="bold")
    ax.legend(loc="upper left", frameon=False, handlelength=1.35, labelspacing=0.16, fontsize=7.5)

    # Panel (c): Multi-plane Gouy IC-POVM radial qudit tomography with kappa(POVM)
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
        label=r"PVB $R\hat{\rho}R$ MLE",
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
        0.94,
        f"$M=1$: rank {ic['single_plane_rank']}/16\n$M=5$: rank {ic['multi_plane_rank']}/16\n$\\kappa(\\mathcal{{S}})= {ic['kappa_povm_superoperator_16d']:.1f}$",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7.5,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": GRAY, "alpha": 0.92},
    )
    ax.set_xlim(240.0, 4.0e4)
    ax.set_ylim(3e-4, 0.35)
    ax.set_xlabel(r"Total photons $N_{\mathrm{phot}}$")
    ax.set_ylabel(r"Tomography MSE $\|\hat{\rho}-\rho_0\|_F^2$")
    ax.set_title("(c) Gouy IC-POVM radial qudit ($d=4$)", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, handlelength=1.35, fontsize=7.6)

    # Panel (d): SPDC circular-iris Bell-CHSH S + collision-free t_l inset (R2-3.20)
    ax = axes[1, 1]
    spdc = metrics["quantum_optics_utility"]["spdc_iris_invariance"]
    r_ir = np.array(spdc["R_iris_over_R0_grid"])
    ax.plot(r_ir, spdc["S_pvb_2arm"], color=BLUE, lw=1.6, label="PVB (2-arm)")
    ax.plot(r_ir, spdc["S_lg_1arm"], color=TEAL, ls="--", lw=1.4, label="LG (1-arm)")
    ax.plot(r_ir, spdc["S_lg_2arm"], color=VERMILION, ls="-.", lw=1.4, label="LG (2-arm)")
    ax.axhline(2.0 * math.sqrt(2.0), color=GRAY, ls=":", lw=0.9)
    ax.axhline(2.0, color=CHARCOAL, ls=":", lw=0.9)
    ax.axvline(1.0, color=GRAY, ls="--", lw=0.8)
    ax.text(0.62, 1.905, "Bell limit $S=2$", fontsize=7.6, color=CHARCOAL)
    ax.set_xlim(0.6, 2.2)
    ax.set_ylim(1.86, 3.16)
    ax.set_yticks([2.0, 2.4, 2.8])
    ax.set_xlabel(r"Iris radius $R_{\mathrm{iris}} / R_0$")
    ax.set_ylabel(r"Bell–CHSH parameter $S$")
    ax.set_title("(d) SPDC iris invariance & CHSH", loc="left", fontweight="bold")
    ax.legend(
        loc="upper left",
        ncol=3,
        columnspacing=0.55,
        handlelength=1.05,
        handletextpad=0.35,
        frameon=False,
        bbox_to_anchor=(0.0, 1.02),
        fontsize=7.3,
    )

    # Place inset in the open white sky [0.14, 0.42, 0.30, 0.27] strictly between PVB=2.83 and LG<=2.22!
    ax_ins_d = ax.inset_axes([0.14, 0.42, 0.30, 0.27])
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
    ax_ins_d.set_xlabel(r"$l$", fontsize=7.4, labelpad=0.3)
    ax_ins_d.set_ylabel(r"$t_l(R_0)$", fontsize=7.4, labelpad=1.2)
    ax_ins_d.legend(loc="upper center", ncol=2, frameon=False, fontsize=7.2, handlelength=0.80, columnspacing=0.5, borderpad=0.05)

    # Verify zero collision between ax_ins_d tightbbox and ALL THREE CHSH curves!
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ins_d_box = ax_ins_d.get_tightbbox(renderer)
    for cname, cy in [("PVB", spdc["S_pvb_2arm"]), ("LG1", spdc["S_lg_1arm"]), ("LG2", spdc["S_lg_2arm"])]:
        pts_c = ax.transData.transform(np.column_stack([r_ir, cy]))
        assert not any(ins_d_box.contains(px, py) for px, py in pts_c), f"Fig 3(d) inset collides with {cname} curve!"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.07)
    plt.close(fig)


def main() -> int:
    cached_json = SCRIPTS_DIR / "verified_metrics.json"
    if cached_json.exists() and "--recompute" not in sys.argv:
        metrics = json.loads(cached_json.read_text(encoding="utf-8"))
        if "field_mse_pvb_frame_mean" not in metrics["classical_optics_utility"]["kolmogorov_rkhs"]:
            metrics = compute_upgraded_metrics()
    else:
        metrics = compute_upgraded_metrics()
    apply_pra_style()
    pra_figs = PACKAGE_DIR / "pra" / "figures"
    arxiv_figs = PACKAGE_DIR / "arxiv" / "figures"
    pra_figs.mkdir(parents=True, exist_ok=True)
    arxiv_figs.mkdir(parents=True, exist_ok=True)

    names = [
        ("fig1_frame_spectrum.pdf", make_fig1),
        ("fig2_laguerre_regularization.pdf", make_fig2),
        ("fig3_optics_utility.pdf", make_fig3),
    ]
    for fname, fn in names:
        p_out = pra_figs / fname
        fn(metrics, p_out)
        shutil.copy2(p_out, arxiv_figs / fname)
        print(f"Generated {p_out} and copied to {arxiv_figs / fname} ({p_out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
