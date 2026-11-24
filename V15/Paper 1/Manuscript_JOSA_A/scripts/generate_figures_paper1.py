"""
Generate all four Optica-accessible publication figures for V15 Paper 1 (JOSA A).
Uses distinct colors, linestyles, and markers per Optica accessibility guidelines.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np
from scipy.optimize import brentq

SCRIPT_DIR = Path(__file__).resolve().parent
MANUSCRIPT_DIR = SCRIPT_DIR.parent
FIG_DIR = MANUSCRIPT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SCRIPT_DIR))
import pvb_physics as pvb  # noqa: E402

RESULTS = json.loads(
    (MANUSCRIPT_DIR.parent / "Step_by_Step_Derivations" / "Verification_Scripts" / "verify_paper1_v15_results.json").read_text(encoding="utf-8")
)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9.0,
    "axes.titlesize": 9.6,
    "axes.labelsize": 9.0,
    "legend.fontsize": 7.4,
    "xtick.labelsize": 8.2,
    "ytick.labelsize": 8.2,
    "axes.linewidth": 0.8,
})


def make_fig1() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.65), dpi=300)

    # Panel (a): Peak-normalized intensity PVB vs LG
    R0, w = 1.0, 0.15
    r = np.linspace(0.0, 2.3, 400)
    styles = [
        (0, "#1B4F72", "-", "none"),
        (2, "#145A32", "--", "none"),
        (4, "#B7950B", "-.", "none"),
        (6, "#922B21", ":", "none"),
    ]
    for lv, col, ls, _ in styles:
        ip = np.abs(pvb.pvb_radial(r, lv, R0, w)) ** 2
        ax1.plot(r / R0, ip / np.max(ip), color=col, ls=ls, lw=1.7, label=rf"PVB $l={lv}$")
    for lv, col in [(2, "#5DADE2"), (6, "#E6B0AA")]:
        il = np.abs(pvb.lg_radial(r, 0, lv, R0)) ** 2
        ax1.plot(r / R0, il / np.max(il), color=col, ls="-", lw=1.0, alpha=0.75, label=rf"$\mathrm{{LG}}_{{0,{lv}}}$")
    ax1.set_xlabel(r"Radial coordinate $r / R_0$")
    ax1.set_ylabel(r"Normalized intensity $I(r)/I_{\max}$")
    ax1.set_title(r"(a) Annular Invariance ($w/R_0 = 0.15$) & Peak Shift")
    ax1.legend(ncol=2, frameon=True, facecolor="white", loc="upper right", fontsize=6.9)
    ax1.grid(alpha=0.22, ls="--")

    # Inset: differential peak shift at w/R0 = 0.25
    ax1_in = ax1.inset_axes([0.52, 0.34, 0.44, 0.34])
    ps_rows = [row for row in RESULTS["peak_shift"]["peak_shifts"] if abs(row["w_over_R"] - 0.25) < 1e-6]
    ls_arr = np.array([row["l"] for row in ps_rows], dtype=float)
    ex_arr = np.array([row["exact_diff_over_R"] * 1e3 for row in ps_rows])
    l_cont = np.linspace(0, 6.3, 80)
    ax1_in.plot(l_cont, (l_cont**2 / 8.0) * (0.25**4) * 1e3, "-", color="#1B4F72", lw=1.2, label=r"$(l^2/8)(w/R)^4$")
    ax1_in.plot(ls_arr, ex_arr, "o", color="#922B21", ms=3.8, label="Exact")
    ax1_in.set_xlabel(r"$l$", fontsize=7, labelpad=1)
    ax1_in.set_ylabel(r"$\Delta r_{\mathrm{peak}}/R_0\;(10^{-3})$", fontsize=6.5, labelpad=1)
    ax1_in.tick_params(labelsize=6.5)
    ax1_in.set_title(r"$w/R_0=0.25$", fontsize=7, pad=2)
    ax1_in.grid(alpha=0.25, ls=":")

    # Panel (b): Normalized radial overlap gamma_l vs universal Gaussian
    dR = np.linspace(0.0, 3.5, 200)
    R_base = 4.0
    for lv, col, ls, mk in [(0, "#1B4F72", "-", "o"), (1, "#145A32", "--", "s"), (4, "#922B21", "-.", "^")]:
        ov = [float(pvb.pvb_gram_normalized([R_base, R_base + d], lv, 1.0)[0, 1]) for d in dR]
        ax2.plot(dR, ov, color=col, ls=ls, lw=1.7, marker=mk, markevery=28, ms=4.2, label=rf"Exact $\gamma_{{{lv}}}$")
    ax2.plot(dR, np.exp(-0.5 * dR**2), ":", color="black", lw=1.6, label=r"$e^{-\Delta R^2/(2w^2)}$")
    ax2.axvline(2.0, color="#7F8C8D", ls="--", lw=0.9)
    ax2.axvline(2.5, color="#7F8C8D", ls=":", lw=0.9)
    ax2.annotate(r"$13.6\%$ ($\Delta R=2w$)", xy=(2.0, 0.1355), xytext=(2.12, 0.34),
                 arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=7.5)
    ax2.annotate(r"$4.40\%$ ($2.5w$)", xy=(2.5, 0.044), xytext=(2.55, 0.19),
                 arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=7.5)
    ax2.set_xlabel(r"Ring separation $\Delta R / w$")
    ax2.set_ylabel(r"Normalized radial overlap $\gamma_l(R_0, R_0+\Delta R)$")
    ax2.set_title(r"(b) Topologically Universal Radial Overlap ($R_0 = 4w$)")
    ax2.legend(frameon=True, facecolor="white", loc="upper right")
    ax2.grid(alpha=0.22, ls="--")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig1_pvb_overlap_shift.pdf", bbox_inches="tight")
    plt.close(fig)


def make_fig2() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.65), dpi=300)

    # Panel (a): NEW V15 Fresnel Propagation Invariance (analytic vs 2D FFT)
    R0, w = 1.0, 0.25
    N = 512
    L = 14.0
    dx = L / N
    x = (np.arange(N) - N // 2) * dx
    X, Y = np.meshgrid(x, x)
    RR = np.hypot(X, Y)
    PHI = np.arctan2(Y, X)
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, kx)
    K2 = KX**2 + KY**2
    k0 = 2.0 * math.pi / 0.00155
    zR_ring = 0.5 * k0 * w**2
    phi0 = pvb.pvb_radial(RR, 1, R0, w) * np.exp(1j * PHI)
    phi0_hat = np.fft.fft2(phi0)
    r_slice = x[N // 2 :]
    sel = r_slice <= 2.3
    r_plot = r_slice[sel]

    cfgs = [
        (0.0, "#1B4F72", "-", "o"),
        (0.5, "#145A32", "--", "s"),
        (1.0, "#B7950B", "-.", "^"),
        (2.5, "#922B21", ":", "D"),
    ]
    for zr, col, ls, mk in cfgs:
        z_ax = zr * zR_ring
        fft_z = np.fft.ifft2(phi0_hat * np.exp(-1j * z_ax * K2 / (2.0 * k0)))
        int_fft = np.abs(fft_z[N // 2, N // 2 :][sel]) ** 2
        int_ana = np.zeros_like(r_plot)
        with mp.workdps(25):
            wc2 = mp.mpc(w**2, w**2 * zr)
            for idx, rv in enumerate(r_plot):
                val = mp.sqrt(2 / mp.pi) / wc2 * mp.exp(-(mp.mpf(rv) ** 2 + mp.mpf(R0) ** 2) / wc2) * mp.besseli(1, 2 * mp.mpf(R0) * mp.mpf(rv) / wc2)
                int_ana[idx] = float(abs(val) ** 2)
        pk = np.max(int_ana)
        ax1.plot(r_plot / R0, int_ana / pk, color=col, ls=ls, lw=1.7, label=rf"$z/z_R^{{\mathrm{{ring}}}}={zr:g}$")
        ax1.plot(r_plot[::9] / R0, int_fft[::9] / pk, linestyle="none", marker=mk, color=col, ms=3.5, mfc="white", mew=0.9)

    ax1.set_xlabel(r"Radial coordinate $r / R$")
    ax1.set_ylabel(r"Peak-normalized $|\Phi_{1,R}^{(z)}(r)|^2$")
    ax1.set_title(r"(a) Exact Fresnel Evolution (Lines: Theory, Markers: 2D FFT)")
    ax1.legend(frameon=True, facecolor="white", loc="upper right")
    ax1.grid(alpha=0.22, ls="--")
    ax1.text(0.03, 0.06, r"$[S_w,\mathcal{U}_z]=0 \Rightarrow S_w^{(z)} = S_w$" + "\n" + r"2D-FFT $L^2$ err $= 4.7\times 10^{-16}$",
             transform=ax1.transAxes, fontsize=7.2, bbox=dict(boxstyle="round,pad=0.28", fc="#EBF5FB", ec="#1B4F72", lw=0.7))

    # Panel (b): Continuous-frame spectrum & Tikhonov multiplier
    wk = np.linspace(0.0, 4.0, 300)
    gw = np.exp(-0.5 * wk**2)
    ax2.axvspan(0.0, 1.394, color="#EAFAF1", alpha=0.8, label=r"$\mathcal{H}_{k_{\max}}$ ($w k_{\max}=1.394$)")
    ax2.plot(wk, gw, "-", color="#1B4F72", lw=1.9, label=r"$\widetilde{G}_w(k_\perp)=e^{-w^2 k_\perp^2/2}$")
    for alp, col, ls in [(1e-2, "#145A32", "--"), (1e-3, "#922B21", "-.")]:
        T_a = (gw**2) / (gw**2 + alp)
        ax2.plot(wk, T_a, color=col, ls=ls, lw=1.6, label=rf"$T_{{\alpha}}$ ($\alpha={alp:g}$)")
    ax2.axvline(1.394, color="#145A32", ls=":", lw=1.0)
    ax2.set_xlabel(r"Dimensionless spatial frequency $w k_\perp$")
    ax2.set_ylabel("Spectral transfer amplitude")
    ax2.set_title(r"(b) Frame Multiplier, Paley--Wiener Passband \& Tikhonov")
    ax2.legend(frameon=True, facecolor="white", loc="upper right", fontsize=7.0)
    ax2.grid(alpha=0.22, ls="--")

    # Inset: noise gain peak
    ax2_in = ax2.inset_axes([0.51, 0.14, 0.45, 0.36])
    for alp, col, ls in [(1e-2, "#145A32", "--"), (1e-3, "#922B21", "-.")]:
        H_a = gw / (gw**2 + alp)
        ax2_in.plot(wk, H_a, color=col, ls=ls, lw=1.3)
    ax2_in.set_xlabel(r"$w k_\perp$", fontsize=6.8, labelpad=1)
    ax2_in.set_ylabel(r"$\widetilde{H}_{w,\alpha}$", fontsize=6.8, labelpad=1)
    ax2_in.set_title(r"Noise gain peak $(2\sqrt{\alpha})^{-1}$", fontsize=6.8, pad=2)
    ax2_in.tick_params(labelsize=6.5)
    ax2_in.grid(alpha=0.25, ls=":")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig2_fresnel_frame_bounds.pdf", bbox_inches="tight")
    plt.close(fig)


def make_fig3() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.6), dpi=300)

    # Panel (a): Bias^2, Variance, Total MSE vs alpha_reg for noisy LG_{2,1}
    alphas = np.logspace(-4, 0, 120)
    b2, var, mse = pvb.tikhonov_mse_analytic(alphas, p=2, l=1, w_over_w0=0.25, w_kmax=3.0, noise_power=0.01)
    tk = RESULTS["tikhonov_lg21"]
    ax1.loglog(alphas, b2, "--", color="#2E86C1", lw=1.5, label=r"$\mathrm{Bias}^2(\alpha_{\mathrm{reg}})$")
    ax1.loglog(alphas, var, "-.", color="#B7950B", lw=1.5, label=r"$\mathrm{Var}(\alpha_{\mathrm{reg}})$")
    ax1.loglog(alphas, mse, "-", color="#1B4F72", lw=2.0, label="Total Parseval MSE")
    ax1.plot(tk["alpha_opt"], tk["mse_opt"], "D", color="#922B21", ms=6.0, zorder=5,
             label=rf"Optimum ($\alpha={tk['alpha_opt']:.4f}$, $\mathrm{{MSE}}={tk['mse_opt']:.4f}$)")
    ax1.errorbar([tk["alpha_opt"]], [tk["mc_tik_mean"]], yerr=[tk["mc_tik_sem"]],
                 fmt="o", color="#145A32", ms=4.5, capsize=3, zorder=6, label="2D-FFT MC (40 trials)")
    ax1.axhline(tk["mse_unreg"], color="#7F8C8D", ls=":", lw=1.1)
    ax1.text(1.5e-4, 5.2, rf"Unregularized $\mathrm{{MSE}}(0)={tk['mse_unreg']:.2f}$ ($258.6\times$ worse)", fontsize=7.2, color="#555")
    ax1.set_xlabel(r"Tikhonov regularization weight $\alpha_{\mathrm{reg}}$")
    ax1.set_ylabel("Normalized field MSE")
    ax1.set_title(r"(a) Parseval Bias--Variance Tradeoff ($\mathrm{LG}_{2,1}$, $\mathrm{SNR}=20\,$dB)")
    ax1.legend(frameon=True, facecolor="white", loc="lower left", fontsize=7.0)
    ax1.grid(True, which="both", alpha=0.2, ls="--")

    # Panel (b): Single-realization radial slice restoration of LG_{2,1}
    rng = np.random.default_rng(42)
    N = 256
    L = 12.0
    dx = L / N
    x = (np.arange(N) - N // 2) * dx
    X, Y = np.meshgrid(x, x)
    RR = np.hypot(X, Y)
    PHI = np.arctan2(Y, X)
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, kx)
    K = np.hypot(KX, KY)
    mask_k = K <= 12.0
    G_hat = np.exp(-0.5 * (0.25 * K) ** 2)
    H_tik = G_hat / (G_hat**2 + tk["alpha_opt"])
    psi_true = pvb.lg_radial(RR, 2, 1, 1.0) * np.exp(1j * PHI)
    psi_true /= math.sqrt(float(np.sum(np.abs(psi_true) ** 2) * dx * dx))
    psi_hat = np.fft.fft2(psi_true)
    n_modes = int(np.sum(mask_k))
    sigma_mode = math.sqrt(0.01 / (n_modes * (dx * dx) / (N * N)))
    noise_hat = np.zeros((N, N), dtype=complex)
    noise_hat[mask_k] = (rng.standard_normal(n_modes) + 1j * rng.standard_normal(n_modes)) * (sigma_mode / math.sqrt(2.0))
    meas_hat = G_hat * psi_hat + noise_hat
    meas_sp = np.fft.ifft2(meas_hat)
    rec_tik = np.fft.ifft2(H_tik * meas_hat * mask_k)
    rec_unreg = np.fft.ifft2((meas_hat / np.where(mask_k, G_hat, 1.0)) * mask_k)

    r_s = x[N // 2 :]
    sel = r_s <= 3.2
    ax2.plot(r_s[sel], np.abs(psi_true[N // 2, N // 2 :][sel]), "-", color="black", lw=1.9, label=r"Exact $\mathrm{LG}_{2,1}$")
    ax2.plot(r_s[sel], np.abs(meas_sp[N // 2, N // 2 :][sel]), ":", color="#B7950B", lw=1.5, label=r"Blurred noisy $S_w\psi+\varepsilon$")
    ax2.plot(r_s[sel], np.abs(rec_tik[N // 2, N // 2 :][sel]), "--", color="#145A32", lw=1.8, label=r"Tikhonov dual $\hat{\psi}_{\alpha_{\mathrm{opt}}}$")
    ax2.plot(r_s[sel], 0.12 * np.abs(rec_unreg[N // 2, N // 2 :][sel]), "-.", color="#922B21", lw=1.1, alpha=0.8, label=r"$0.12\,|\hat{\psi}_{0}|$ (unregularized)")
    ax2.set_xlabel(r"Radial coordinate $r / w_0$")
    ax2.set_ylabel(r"Field modulus $|\psi(r,0)|\,w_0$")
    ax2.set_title(r"(b) Radial Phase-Flip Node Restoration ($\alpha_{\mathrm{reg}}^{\mathrm{opt}} = 0.0490$)")
    ax2.legend(frameon=True, facecolor="white", loc="upper right", fontsize=7.0)
    ax2.grid(alpha=0.22, ls="--")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig3_tikhonov_lg21_deconv.pdf", bbox_inches="tight")
    plt.close(fig)


def make_fig4() -> None:
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10.2, 3.35), dpi=300)

    # Panel (a): c_{1,p}(R) closed form vs quadrature
    R_arr = np.linspace(0.0, 3.0, 180)
    R_q = np.linspace(0.2, 2.7, 11)
    cfgs = [(0, "#1B4F72", "-", "o"), (1, "#145A32", "--", "s"), (2, "#B7950B", "-.", "^"), (3, "#922B21", ":", "D")]
    for pv, col, ls, mk in cfgs:
        ax1.plot(R_arr, pvb.c_lp_closed_form(R_arr, pv, 1, 0.25, 1.0), color=col, ls=ls, lw=1.6, label=rf"$p={pv}$")
        cq = [pvb.c_lp_quad(float(rv), pv, 1, 0.25, 1.0) for rv in R_q]
        ax1.plot(R_q, cq, linestyle="none", marker=mk, color=col, ms=3.5, mfc="white", mew=0.9)
    ax1.axhline(0.0, color="gray", lw=0.7)
    ax1.set_xlabel(r"Ring radius $R / w_0$")
    ax1.set_ylabel(r"$c_{1,p}(R)\,w_0$")
    ax1.set_title(r"(a) Exact $c_{1,p}(R)$ ($w/w_0=0.25$)")
    ax1.legend(frameon=True, facecolor="white", ncol=2, loc="upper right", fontsize=7.0)
    ax1.grid(alpha=0.22, ls="--")

    # Panel (b): Washout fidelity & WKB arcsine convergence
    ww = np.linspace(0.02, 1.0, 80)
    for pv, col, ls, mk in cfgs:
        ff = [pvb.nodal_washout_fidelity(pv, 1, float(x)) for x in ww]
        ax2.plot(ww, ff, color=col, ls=ls, lw=1.6, marker=mk, markevery=14, ms=3.6, label=rf"$p={pv}$")
    ax2.axhline(0.95, color="black", ls=":", lw=1.0)
    ax2.set_xlabel(r"Relative half-width $w / w_0$")
    ax2.set_ylabel(r"Washout fidelity $\mathcal{F}(p,1,w/w_0)$")
    ax2.set_title("(b) Radial Nodal Washout")
    ax2.legend(frameon=True, facecolor="white", loc="lower left", fontsize=7.0)
    ax2.grid(alpha=0.22, ls="--")

    ax2_in = ax2.inset_axes([0.46, 0.50, 0.50, 0.42])
    p_list = [row["p"] for row in RESULTS["rayleigh_arcsine"]["p_ge_1_roots"]]
    sc_list = [row["scaled_prefactor"] for row in RESULTS["rayleigh_arcsine"]["p_ge_1_roots"]]
    ax2_in.plot(p_list, sc_list, "o-", color="#1B4F72", ms=3.5, lw=1.2)
    ax2_in.axhline(RESULTS["rayleigh_arcsine"]["arcsine_sqrt_c"], color="#922B21", ls="--", lw=1.0)
    ax2_in.set_xlabel(r"$p$", fontsize=6.5, labelpad=1)
    ax2_in.set_ylabel(r"$w_{\mathrm{crit}}\sqrt{2p+2}/w_0$", fontsize=6.2, labelpad=1)
    ax2_in.set_title("Arcsine: 0.5724", fontsize=6.5, pad=1)
    ax2_in.tick_params(labelsize=6.2)
    ax2_in.grid(alpha=0.25, ls=":")

    # Panel (c): Unit-normalized Gram conditioning vs unnormalized & Toeplitz bound
    gt = RESULTS["gram_toeplitz"]["gram_table"]
    dr_w = [r["dR_over_w"] for r in gt]
    ax3.semilogy(dr_w, [r["kappa_G_N6"] for r in gt], "s--", color="#922B21", lw=1.5, ms=4.5, label=r"Unnorm. $\kappa(G)$")
    ax3.semilogy(dr_w, [r["kappa_toeplitz_inf"] for r in gt], "^:", color="#B7950B", lw=1.5, ms=4.5, label=r"$\vartheta_3/\vartheta_4$ ($N\to\infty$)")
    ax3.semilogy(dr_w, [r["kappa_gamma_N6"] for r in gt], "o-", color="#145A32", lw=1.8, ms=4.5, label=r"Norm. $\kappa(\gamma)$ ($N{=}6$)")
    ax3.axvline(2.0, color="gray", ls="--", lw=0.9)
    ax3.set_xlabel(r"Ring spacing $\Delta R / w$")
    ax3.set_ylabel("Gram condition number")
    ax3.set_title("(c) Discrete Gram Spectrum")
    ax3.legend(frameon=True, facecolor="white", loc="upper right", fontsize=6.8)
    ax3.grid(True, which="both", alpha=0.2, ls="--")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig4_lg_washout_gram.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    print("Generated all 4 publication figures for V15 Paper 1 (JOSA A).")
