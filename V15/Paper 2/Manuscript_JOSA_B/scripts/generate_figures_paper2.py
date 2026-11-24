"""
Generate all four Optica-accessible publication figures for V15 Paper 2 (JOSA B).
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
import numpy as np
from scipy.special import erfc

SCRIPT_DIR = Path(__file__).resolve().parent
MANUSCRIPT_DIR = SCRIPT_DIR.parent
FIG_DIR = MANUSCRIPT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SCRIPT_DIR))
import pvb_physics as pvb  # noqa: E402

RESULTS = json.loads(
    (MANUSCRIPT_DIR.parent / "Step_by_Step_Derivations" / "Verification_Scripts" / "verify_paper2_v15_results.json").read_text(encoding="utf-8")
)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9.0,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9.0,
    "legend.fontsize": 7.3,
    "xtick.labelsize": 8.2,
    "ytick.labelsize": 8.2,
    "axes.linewidth": 0.8,
})


def make_fig1() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.65), dpi=300)
    p1 = RESULTS["protocol1_rcf_grin_sdm"]
    ls_step = [r["l"] for r in p1["step_rows"]]
    ls_grin = [r["l"] for r in p1["grin_rows"] if r["l"] <= 6]

    # Panel (a): Step-Index & Guided GRIN RCF coupling vs LG
    ax1.plot(ls_step, [r["eta_pvb"] for r in p1["step_rows"]], "o-", color="#145A32", lw=1.8, ms=4.5, label=r"PVB (Step-index, $w=1.72\,\mu$m)")
    ax1.plot(ls_grin, [r["eta_pvb_opt"] for r in p1["grin_rows"][:7]], "D--", color="#1B4F72", lw=1.7, ms=4.2, label=r"PVB (GRIN $l\leq 6$, $w=1.96\,\mu$m)")
    ax1.plot(ls_step, [r["eta_lg_450"] for r in p1["step_rows"]], "s-.", color="#B7950B", lw=1.4, ms=4.0, label=r"$\mathrm{LG}_{0,l}$ ($w_0=4.50\,\mu$m)")
    ax1.plot(ls_step, [r["eta_lg_322"] for r in p1["step_rows"]], "^:", color="#922B21", lw=1.5, ms=4.2, label=r"$\mathrm{LG}_{0,l}$ ($w_0=3.22\,\mu$m)")
    ax1.axvline(6.5, color="#7F8C8D", ls=":", lw=1.0)
    ax1.text(6.62, 0.25, "GRIN\ncutoff\n($l>6$)", fontsize=6.9, color="#555")
    ax1.set_xlabel(r"Azimuthal OAM order $l$")
    ax1.set_ylabel(r"Modal coupling efficiency $\eta_l$")
    ax1.set_title("(a) Step-Index & Parabolic GRIN RCF Coupling")
    ax1.set_ylim(-0.02, 1.07)
    ax1.legend(frameon=True, facecolor="white", loc="lower right", fontsize=6.8)
    ax1.grid(alpha=0.22, ls="--")

    # Inset: OOK BER at l=4 with N=6 AWGN ZF penalty (0.41 dB)
    ax1_in = ax1.inset_axes([0.13, 0.16, 0.36, 0.35])
    eb_db = np.linspace(4, 16, 60)
    eb_lin = 10.0 ** (eb_db / 10.0)
    ber_pvb_zf = 0.5 * erfc(np.sqrt(0.9916 * eb_lin / (2.0 * 1.0994)))
    ber_lg_fix = 0.5 * erfc(np.sqrt(0.2026 * eb_lin / 2.0))
    ax1_in.semilogy(eb_db, ber_pvb_zf, "-", color="#145A32", lw=1.3, label="PVB+ZF")
    ax1_in.semilogy(eb_db, ber_lg_fix, ":", color="#922B21", lw=1.3, label="LG fix")
    ax1_in.set_ylim(1e-7, 0.5)
    ax1_in.set_xlabel(r"$E_b/N_0$ (dB)", fontsize=6.3, labelpad=1)
    ax1_in.set_ylabel("BER", fontsize=6.3, labelpad=1)
    ax1_in.tick_params(labelsize=6.0)
    ax1_in.legend(fontsize=5.8, loc="lower left", frameon=False)
    ax1_in.grid(alpha=0.25, ls=":")

    # Panel (b): Launch misalignment tolerances (l=4)
    dx_vals = [r["dx_um"] for r in p1["tolerance_dx_lateral"]]
    dR_pos = [r["dR_um"] for r in p1["tolerance_dR"] if r["dR_um"] >= 0]
    ax2.plot(dx_vals, [r["eta_step_l4"] for r in p1["tolerance_dx_lateral"]], "o-", color="#145A32", lw=1.7, ms=4.5, label=r"Lateral $\delta x$ (Step-index)")
    ax2.plot(dx_vals, [r["eta_grin_l4"] for r in p1["tolerance_dx_lateral"]], "D--", color="#1B4F72", lw=1.7, ms=4.2, label=r"Lateral $\delta x$ (GRIN)")
    ax2.plot([abs(r["dR_um"]) for r in p1["tolerance_dR"] if r["dR_um"] >= 0],
             [r["eta_grin_l4"] for r in p1["tolerance_dR"] if r["dR_um"] >= 0], "s-.", color="#B7950B", lw=1.5, ms=4.2, label=r"Radius $+\delta R$ (GRIN)")
    ax2.plot([abs(r["dR_um"]) for r in p1["tolerance_dR"] if r["dR_um"] <= 0][::-1],
             [r["eta_grin_l4"] for r in p1["tolerance_dR"] if r["dR_um"] <= 0][::-1], "^:", color="#922B21", lw=1.5, ms=4.2, label=r"Radius $-\delta R$ (GRIN)")
    ax2.axhline(0.90, color="gray", ls="--", lw=0.9)
    ax2.text(0.82, 0.915, "90% threshold", fontsize=7.2, color="#555")
    ax2.set_xlabel(r"Launch misalignment magnitude $|\delta x|$ or $|\delta R|$ ($\mu$m)")
    ax2.set_ylabel(r"Coupling efficiency $\eta_{\mathrm{PVB}}(l=4)$")
    ax2.set_title("(b) Launch Alignment Tolerance (Step vs. GRIN)")
    ax2.set_ylim(0.45, 1.03)
    ax2.legend(frameon=True, facecolor="white", loc="lower left", fontsize=7.0)
    ax2.grid(alpha=0.22, ls="--")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig1_rcf_step_grin_tolerances.pdf", bbox_inches="tight")
    plt.close(fig)


def make_fig2() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.6), dpi=300)
    p2 = RESULTS["protocol2_turbulence"]
    ss = p2["single_screen"]
    dr0 = [r["D_over_r0"] for r in ss]

    ax1.plot(dr0, [r["raw_mse"] for r in ss], "o-", color="#7F8C8D", lw=1.4, ms=4.2, label="Raw turbulent field")
    ax1.plot(dr0, [r["pk_mse"] for r in ss], "v:", color="#8E44AD", lw=1.3, ms=4.0, label=r"Circular pinhole $P_{k_{\max}}$")
    ax1.plot(dr0, [r["tik_mse"] for r in ss], "s--", color="#B7950B", lw=1.4, ms=4.0, label="Isotropic Tikhonov")
    ax1.errorbar(dr0, [r["lg5_mse"] for r in ss], yerr=[r["lg5_sem"] for r in ss],
                 fmt="^--", color="#2E86C1", lw=1.6, ms=4.5, capsize=2.5, label=r"Matched $N=5$ $\mathrm{LG}_{p,1}$ ($w_0^{\mathrm{opt}}$)")
    ax1.errorbar(dr0, [r["pvb5_mse"] for r in ss], yerr=[r["pvb5_sem"] for r in ss],
                 fmt="D-", color="#145A32", lw=1.9, ms=4.5, capsize=2.5, label=r"$N=5$ PVB dual-frame $P_{\mathrm{PVB},1}$")
    ax1.set_xlabel(r"Turbulence strength $D / r_0$")
    ax1.set_ylabel("Normalized field MSE")
    ax1.set_title("(a) Single-Screen Kolmogorov Turbulence ($30$ Trials)")
    ax1.legend(frameon=True, facecolor="white", loc="upper left", fontsize=6.9)
    ax1.grid(alpha=0.22, ls="--")

    # Panel (b): 5-screen split-step volume turbulence
    ms = p2["multi_screen_5"]
    labels = [rf"$D/r_0={r['D_over_r0_eff']:g}$" for r in ms]
    x = np.arange(len(ms))
    bw = 0.25
    b1 = ax2.bar(x - bw, [r["raw_mse"] for r in ms], bw, color="#7F8C8D", hatch="///", edgecolor="black", lw=0.6, label="Raw (5-screen)")
    b2 = ax2.bar(x, [r["lg5_mse"] for r in ms], bw, color="#2E86C1", hatch="...", edgecolor="black", lw=0.6, label=r"Optimal $N=5$ $\mathrm{LG}_{p,1}$")
    b3 = ax2.bar(x + bw, [r["pvb5_mse"] for r in ms], bw, color="#145A32", edgecolor="black", lw=0.6, label=r"$N=5$ PVB dual-frame")
    for i, r in enumerate(ms):
        ax2.text(i + bw, r["pvb5_mse"] + 0.018, rf"{r['pvb_over_raw_gain']:.1f}$\times$", ha="center", va="bottom",
                 fontsize=7.3, fontweight="bold", color="#145A32")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_ylabel("Normalized field MSE")
    ax2.set_title("(b) Extended 5-Screen Split-Step Volume Turbulence")
    ax2.set_ylim(0, 0.84)
    ax2.legend(frameon=True, facecolor="white", loc="upper left", fontsize=7.2)
    ax2.grid(axis="y", alpha=0.22, ls="--")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig2_turbulence_pvb_vs_lg.pdf", bbox_inches="tight")
    plt.close(fig)


def make_fig3() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.6), dpi=300)
    p3 = RESULTS["protocol3_ic_povm"]
    sw = p3["coherent_superposition_sweep"]
    nph = np.array([r["N_phot"] for r in sw], dtype=float)

    # Panel (a): Coherent superposition MSE & Fidelity vs N_phot + Asymptotic CRB lines
    ax1.loglog(nph, 41.7953 / nph, "--", color="#1B4F72", lw=1.5, label=r"Mixed $\rho_0$ PVB CRB ($41.80/N$)")
    ax1.loglog(nph, 18.75 / nph, ":", color="#7F8C8D", lw=1.4, label=r"Sequential 5-MUB CRB ($18.75/N$)")
    ax1.loglog(nph, [r["mean_frob_mse"] for r in sw], "D-", color="#145A32", lw=1.8, ms=5.0, label=r"Coherent $|\psi_{\mathrm{coh}}\rangle$ MLE MSE")
    ax1.loglog(nph, [1.0 - r["mean_fidelity"] for r in sw], "s-.", color="#922B21", lw=1.5, ms=4.5, label=r"Infidelity $1 - F(\hat{\rho},\psi_{\mathrm{coh}})$")
    ax1.plot([10000], [1.0 - p3["haar_20_pure_10k_mean_fid"]], "*", color="#B7950B", ms=9.0, zorder=6,
             label=rf"20 Haar pure states ($1-\bar{{F}}={1-p3['haar_20_pure_10k_mean_fid']:.4f}$)")
    ax1.set_xlabel(r"Detected photon budget $N_{\mathrm{phot}}$")
    ax1.set_ylabel("Frobenius MSE / Infidelity")
    ax1.set_title(r"(a) Passive $M=5$ Gouy IC-POVM Tomography ($d=4$)")
    ax1.legend(frameon=True, facecolor="white", loc="lower left", fontsize=6.7)
    ax1.grid(True, which="both", alpha=0.2, ls="--")

    # Panel (b): Axial Gouy-plane misalignment robustness
    ma = p3["gouy_misalignment_robustness"]
    dz = [r["dz_over_zR_rms"] * 100.0 for r in ma]
    fid = [r["uncalibrated_coh_fidelity_10k"] for r in ma]
    crb = [r["mean_crb_perturbed"] for r in ma]
    ax2.plot(dz, fid, "o-", color="#145A32", lw=1.9, ms=5.2, label=r"Uncalibrated $F(\hat{\rho},\psi_{\mathrm{coh}})$ ($10^4$ ph.)")
    ax2.set_xlabel(r"RMS axial Gouy-plane jitter $\delta z_{\mathrm{rms}} / z_R$ (\%)")
    ax2.set_ylabel(r"Reconstruction fidelity $F$", color="#145A32")
    ax2.tick_params(axis="y", labelcolor="#145A32")
    ax2.set_ylim(0.95, 1.00)
    ax2.grid(alpha=0.22, ls="--")
    ax2_r = ax2.twinx()
    ax2_r.plot(dz, crb, "s--", color="#922B21", lw=1.6, ms=4.8, label=r"Perturbed CRB $\mathrm{Tr}(\mathbf{F}^{-1})$")
    ax2_r.set_ylabel(r"Single-photon CRB $\mathrm{Tr}(\mathbf{F}^{-1})$", color="#922B21")
    ax2_r.tick_params(axis="y", labelcolor="#922B21")
    ax2_r.set_ylim(41.0, 43.2)
    ax2.set_title("(b) Robustness to Uncalibrated Axial Plane Misalignment")
    lines1, labs1 = ax2.get_legend_handles_labels()
    lines2, labs2 = ax2_r.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labs1 + labs2, frameon=True, facecolor="white", loc="lower left", fontsize=6.9)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig3_gouy_icpovm_extended.pdf", bbox_inches="tight")
    plt.close(fig)


def make_fig4() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.6), dpi=300)
    p4 = RESULTS["protocol4_chsh_loophole"]
    sw = p4["sweep"]
    ri = [r["R_iris_over_R0"] for r in sw]

    # Panel (a): Worst-case single-photon transmission & 82.84% detection-loophole threshold
    ax1.plot(ri, [min(r["t1_pvb"], r["t4_pvb"]) for r in sw], "D-", color="#145A32", lw=2.0, ms=4.8,
             label=r"PVB ($w/R_0=0.1$, clears at $1.048\,R_0$)")
    ax1.plot(ri, [r["t4_lg_w0_l4"] for r in sw], "s--", color="#2E86C1", lw=1.5, ms=4.3,
             label=r"LG ($w_0=R_0/\sqrt{2}$, clears at $1.324\,R_0$)")
    ax1.plot(ri, [r["t4_lg_w0_mid"] for r in sw], "^-.", color="#B7950B", lw=1.5, ms=4.3,
             label=r"LG ($w_0=R_0$, clears at $1.873\,R_0$)")
    ax1.plot(ri, [pvb.lg0l_iris_transmission(r, math.sqrt(2.0), 4) for r in ri], "v:", color="#922B21", lw=1.4, ms=4.0,
             label=r"LG ($w_0=\sqrt{2}R_0$, clears at $2.649\,R_0$)")
    ax1.axhline(p4["eta_chsh_crit"], color="black", ls=":", lw=1.3, label=r"CHSH loophole $\eta_{\mathrm{crit}} = 82.84\%$")
    ax1.set_xlabel(r"Circular iris radius $R_{\mathrm{iris}} / R_0$")
    ax1.set_ylabel(r"Worst-case transmission $\min(t_1, t_4)$")
    ax1.set_title("(a) Pupil Efficiency & Detection-Loophole Threshold")
    ax1.set_ylim(-0.03, 1.07)
    ax1.legend(frameon=True, facecolor="white", loc="center right", fontsize=6.7)
    ax1.grid(alpha=0.22, ls="--")

    # Panel (b): Two-arm Bell-CHSH parameter S^(2) vs R_iris/R0
    ax2.plot(ri, [2.0 * math.sqrt(2.0) - r["dev_S2_pvb"] for r in sw], "D-", color="#145A32", lw=2.0, ms=4.8, label="PVB $S^{(2)}$")
    ax2.plot(ri, [r["S2_lg_w0_l4"] for r in sw], "s--", color="#2E86C1", lw=1.5, ms=4.3, label=r"LG $S^{(2)}$ ($w_0=R_0/\sqrt{2}$)")
    ax2.plot(ri, [r["S2_lg_w0_mid"] for r in sw], "^-.", color="#B7950B", lw=1.5, ms=4.3, label=r"LG $S^{(2)}$ ($w_0=R_0$)")
    ax2.plot(ri, [r["S2_lg_w0_l1"] for r in sw], "v:", color="#922B21", lw=1.4, ms=4.0, label=r"LG $S^{(2)}$ ($w_0=\sqrt{2}R_0$)")
    ax2.axhline(2.0 * math.sqrt(2.0), color="gray", ls="--", lw=0.9, label=r"Tsirelson $2\sqrt{2}$")
    ax2.axhline(2.0, color="black", ls=":", lw=1.0, label="Local-realism bound $S=2$")
    ax2.set_xlabel(r"Circular iris radius $R_{\mathrm{iris}} / R_0$")
    ax2.set_ylabel(r"Two-arm CHSH parameter $S^{(2)}(R_{\mathrm{iris}})$")
    ax2.set_title(r"(b) Bell--CHSH Preservation for $(|1,-1\rangle+|4,-4\rangle)/\sqrt{2}$")
    ax2.set_ylim(1.94, 2.90)
    ax2.legend(frameon=True, facecolor="white", loc="lower right", fontsize=6.7)
    ax2.grid(alpha=0.22, ls="--")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig4_iris_chsh_loophole.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    print("Generated all 4 publication figures for V15 Paper 2 (JOSA B).")
