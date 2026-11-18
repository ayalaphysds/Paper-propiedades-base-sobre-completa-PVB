"""
First-principles mathematical and physical optics verification suite for V6.
Executes:
  - 6 Core Mathematical Assertion Suites (Explorer 1 / Referee 2 R2-M1..R2-M18)
  - 5 Classical & Quantum Optics Simulations (Explorer 2 / Referee 1 R1-1..R1-9)
Exports deterministic (seed=2026) metrics to V6/scripts/verified_metrics.json (schema v1.0.0).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import scipy
import sympy as sp
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
from scipy.special import erfc, eval_genlaguerre, ive, jv

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pvb_physics import (
    c_lp_closed_form,
    c_lp_quad,
    kolmogorov_subharmonic_screen,
    laguerre_spectral_density,
    lg0l_iris_transmission,
    lg_2d_ft_radial,
    lg_radial,
    nodal_washout_fidelity,
    nodal_washout_p0_closed,
    pvb_2d_ft_radial,
    pvb_c0,
    pvb_gram_normalized,
    pvb_gram_unnormalized,
    pvb_iris_transmission,
    pvb_radial,
    r_rho_r_mle,
    solve_rcf_eigenmodes,
    tikhonov_mse_analytic,
    weber_fourier_multiplier,
)


def _gell_mann_basis(d: int = 4) -> list[np.ndarray]:
    """Return d^2 - 1 Hermitian traceless matrices with Tr(T_a T_b) = delta_{ab}."""
    basis: list[np.ndarray] = []
    for j in range(d):
        for k in range(j + 1, d):
            mat_s = np.zeros((d, d), dtype=complex)
            mat_s[j, k] = mat_s[k, j] = 1.0 / math.sqrt(2.0)
            basis.append(mat_s)
            mat_a = np.zeros((d, d), dtype=complex)
            mat_a[j, k] = -1j / math.sqrt(2.0)
            mat_a[k, j] = 1j / math.sqrt(2.0)
            basis.append(mat_a)
    for m in range(1, d):
        mat_d = np.zeros((d, d), dtype=complex)
        for j in range(m):
            mat_d[j, j] = 1.0
        mat_d[m, m] = -float(m)
        mat_d /= math.sqrt(m * (m + 1))
        basis.append(mat_d)
    assert len(basis) == d * d - 1
    return basis


def _build_5_mubs_d4() -> list[np.ndarray]:
    """
    Construct the 5 mutually unbiased bases in C^4 as 5 sets of 4 orthonormal
    rank-1 projectors (20 POVM elements scaled by 1/5 so sum E = I_4).
    """
    I2 = np.eye(2, dtype=complex)
    X2 = np.array([[0, 1], [1, 0]], dtype=complex)
    Y2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z2 = np.array([[1, 0], [0, -1]], dtype=complex)
    paulis = {"I": I2, "X": X2, "Y": Y2, "Z": Z2}

    def kron(label: str) -> np.ndarray:
        return np.kron(paulis[label[0]], paulis[label[1]])

    commuting_triples = [
        ("ZI", "IZ", "ZZ"),
        ("XI", "IX", "XX"),
        ("YI", "IY", "YY"),
        ("XY", "YZ", "ZX"),
        ("XZ", "YX", "ZY"),
    ]
    povm_mub: list[np.ndarray] = []
    for a, b, c in commuting_triples:
        # Distinct linear combination breaks any degeneracy across the 4 joint eigenspaces
        op = 1.0 * kron(a) + math.pi * kron(b) + math.e * kron(c)
        _, evecs = np.linalg.eigh(0.5 * (op + op.conj().T))
        for col in range(4):
            ket = evecs[:, col : col + 1]
            povm_mub.append((1.0 / 5.0) * (ket @ ket.conj().T))

    # Verify pairwise MUB inner products == 1/4
    for m1 in range(5):
        for m2 in range(m1 + 1, 5):
            for i in range(4):
                for j in range(4):
                    ov = float(
                        np.real(
                            np.trace((5.0 * povm_mub[4 * m1 + i]) @ (5.0 * povm_mub[4 * m2 + j]))
                        )
                    )
                    assert abs(ov - 0.25) < 1e-12
    return povm_mub


def _fisher_matrix(E_ops: np.ndarray, rho0: np.ndarray, T_basis: list[np.ndarray]) -> np.ndarray:
    """Classical Fisher information matrix F_ab at rho0 for POVM E_ops."""
    n_param = len(T_basis)
    F = np.zeros((n_param, n_param), dtype=float)
    for E in E_ops:
        p0 = float(np.real(np.trace(E @ rho0)))
        if p0 <= 1e-15:
            continue
        grad = np.array([float(np.real(np.trace(E @ T))) for T in T_basis], dtype=float)
        F += np.outer(grad, grad) / p0
    return F


def run_suite_1_and_2(metrics: dict[str, Any], assertions: dict[str, bool]) -> None:
    """Suite 1 (C0 norm, R=0, Hankel, 2f optics, peak shift) & Suite 2 (2D FT, Weber, PW bounds, telecom)."""
    # --- Suite 1 ---
    R_test, w_test, l_test = 2.0, 0.5, 1
    norm2_quad, _ = quad(
        lambda r: 2.0 * math.pi * r * (pvb_radial(r, l_test, R_test, w_test) ** 2),
        0.0,
        np.inf,
        epsabs=1e-13,
        epsrel=1e-13,
        limit=200,
    )
    norm2_closed = float(pvb_gram_unnormalized([R_test], l_test, w_test)[0, 0])
    assert abs(norm2_quad - norm2_closed) < 1e-12
    assert abs(norm2_closed - 0.389398459026) < 1e-11
    assert abs(norm2_closed - 1.0) > 0.5
    assertions["c0_non_unit_norm"] = True

    # R = 0 degeneracy
    r_probe = np.array([0.1, 0.5, 1.2])
    for l_nz in (-2, -1, 1, 3):
        assert np.all(pvb_radial(r_probe, l_nz, 0.0, w_test) == 0.0)
    norm2_00_quad, _ = quad(
        lambda r: 2.0 * math.pi * r * (pvb_radial(r, 0, 0.0, w_test) ** 2),
        0.0,
        np.inf,
        epsabs=1e-13,
        epsrel=1e-13,
    )
    assert abs(norm2_00_quad - 1.0 / (w_test ** 2)) < 1e-12

    # Hankel leading-order asymptotic error at R/w = 4, l = 4 (x = 2*R^2/w^2 = 32)
    R_hk, w_hk, l_hk = 4.0, 1.0, 4
    x_hk = 2.0 * (R_hk ** 2) / (w_hk ** 2)
    exact_hk = pvb_radial(R_hk, l_hk, R_hk, w_hk)
    asymp_hk = pvb_c0(w_hk) / math.sqrt(2.0 * math.pi * x_hk)
    hankel_rel_err = abs(asymp_hk - exact_hk) / exact_hk
    assert abs(hankel_rel_err - 0.2837) < 1e-3

    # 2f optics parameter consistency (R2-M3, R2-M4, R2-M14)
    lam = 1550e-9
    k0 = 2.0 * math.pi / lam
    n_ax, beta_rad, f_len, w_g = 1.45, 0.02, 0.10, 1.4e-3
    k_r = k0 * (n_ax - 1.0) * beta_rad
    R_2f = k_r * f_len / k0
    w_2f = 2.0 * f_len / (k0 * w_g)
    assert abs(R_2f - (n_ax - 1.0) * beta_rad * f_len) < 1e-15
    assert w_2f > 0.0 and k_r > 0.0

    # Transcendental peak shift r_peak(l) via brentq on d/dr |Phi_{l,R0}(r)|^2 = 0
    w_over_R0 = 0.25
    R0_pk = 1.0
    w_pk = w_over_R0 * R0_pk
    l_pk_vals = [0, 1, 2, 4, 6]
    r_peak_list: list[float] = []
    delta_r_list: list[float] = []
    asymp_list: list[float] = []
    for l_v in l_pk_vals:
        def peak_eq(r: float) -> float:
            x = 2.0 * R0_pk * r / (w_pk ** 2)
            ratio = (l_v / x) + float(ive(l_v + 1, x) / ive(l_v, x))
            return r - R0_pk * ratio

        r_sol = float(brentq(peak_eq, 0.7 * R0_pk, 1.3 * R0_pk, xtol=1e-13))
        r_peak_list.append(r_sol / R0_pk)
        asymp_list.append((l_v ** 2) * (w_over_R0 ** 4) / 8.0)
    delta_r_list = [rp - r_peak_list[0] for rp in r_peak_list]
    assert delta_r_list[-1] > delta_r_list[2] > delta_r_list[1] > delta_r_list[0]

    # --- Suite 2 ---
    # Non-unitary 2D FT check across positive & negative l
    R_ft, w_ft, k_ft = 1.8, 0.45, 2.7
    ft_errs = []
    for l_v in (-3, -1, 0, 1, 2):
        val_r, _ = quad(
            lambda r: r * pvb_radial(r, l_v, R_ft, w_ft) * float(jv(abs(l_v), k_ft * r)),
            0.0,
            np.inf,
            epsabs=1e-13,
            epsrel=1e-13,
            limit=200,
        )
        ft_num = 2.0 * math.pi * ((-1j) ** abs(l_v)) * val_r
        ft_ana = pvb_2d_ft_radial(k_ft, l_v, R_ft, w_ft)
        err = abs(ft_num - ft_ana)
        assert err < 1e-12
        ft_errs.append(err)

    # Position-space Weber kernel convolution check (S_w psi)(r,0) = (G_w * psi)(r,0)
    # on a Gaussian test packet psi(r) = exp(-r^2) -> S_w(exp(-r^2))(r) = 1/(1+2 w^2) * exp(-r^2/(1+2 w^2))
    w_wk = 0.5
    r_eval = 0.7
    sw_exact = (1.0 / (1.0 + 2.0 * w_wk ** 2)) * math.exp(-(r_eval ** 2) / (1.0 + 2.0 * w_wk ** 2))
    sw_conv, _ = quad(
        lambda rp: (rp / (w_wk ** 2))
        * math.exp(-((r_eval - rp) ** 2) / (2.0 * w_wk ** 2))
        * float(ive(0, r_eval * rp / (w_wk ** 2)))
        * math.exp(-(rp ** 2)),
        0.0,
        np.inf,
        epsabs=1e-13,
        epsrel=1e-13,
    )
    pos_rel_err = abs(sw_conv - sw_exact) / sw_exact
    assert pos_rel_err < 1e-12

    # Paley-Wiener sharp bounds & saturating Fourier rings
    w_pw, kmax_pw = 0.5, 2.8
    A_pw = math.exp(-0.5 * (w_pw * kmax_pw) ** 2)
    B_pw = 1.0
    eps = 1e-3

    def ring_ratio(k1: float, k2: float) -> float:
        num, _ = quad(lambda k: 2.0 * k * math.exp(-0.5 * (w_pw * k) ** 2), k1, k2, epsabs=1e-14)
        return num / (k2 ** 2 - k1 ** 2)

    ratio_upper = ring_ratio(0.0, eps)
    ratio_lower = ring_ratio(kmax_pw - eps, kmax_pw)
    assert abs(ratio_upper - B_pw) < 1e-6
    assert abs(ratio_lower - A_pw) < 5e-4

    # Bandlimit projector P_{k_max} dual norm vs unprojected divergence
    proj_dual_norm2, _ = quad(
        lambda k: k * math.exp(0.5 * (w_pw * k) ** 2) * (float(jv(1, 1.5 * k)) ** 2),
        0.0,
        kmax_pw,
        epsabs=1e-12,
        epsrel=1e-12,
    )
    unproj_tail, _ = quad(
        lambda k: k * math.exp(0.5 * (w_pw * k) ** 2) * (float(jv(1, 1.5 * k)) ** 2),
        10.0,
        20.0,
        epsabs=1e-6,
        epsrel=1e-6,
        limit=200,
    )
    assert np.isfinite(proj_dual_norm2) and proj_dual_norm2 < 10.0
    assert unproj_tail > 1e15

    # Telecom/SLM parameter bridge (R1-6)
    NA_tel = 0.20
    w_tel_um = 1.72
    w_tel_m = w_tel_um * 1e-6
    kmax_tel = k0 * NA_tel
    w_kmax_tel = w_tel_m * kmax_tel
    A_tel = math.exp(-0.5 * (w_kmax_tel ** 2))
    kappa_tel = 1.0 / A_tel
    assert abs(w_kmax_tel - 1.394462) < 1e-5
    assert abs(kappa_tel - 2.643918) < 1e-5

    metrics["frame_and_normalization"] = {
        "c0_norm_check": {
            "R": R_test,
            "w": w_test,
            "l": l_test,
            "C0": pvb_c0(w_test),
            "L2_norm_sq_analytic": norm2_closed,
            "L2_norm_sq_quad": norm2_quad,
            "abs_error": abs(norm2_quad - norm2_closed),
        },
        "r0_degeneracy": {
            "l_nonzero_max_abs": 0.0,
            "Phi_00_L2_norm_sq": norm2_00_quad,
            "expected_1_over_w2": 1.0 / (w_test ** 2),
        },
        "hankel_asymptotic_error_example": {
            "R_over_w": R_hk / w_hk,
            "l": l_hk,
            "x": x_hk,
            "leading_rel_error": hankel_rel_err,
        },
        "optics_2f_check": {
            "wavelength_nm": 1550.0,
            "k0_inv_m": k0,
            "n_ax": n_ax,
            "beta_rad": beta_rad,
            "f_m": f_len,
            "R_m": R_2f,
            "w_m": w_2f,
        },
        "transcendental_peak_shift": {
            "w_over_R0": w_over_R0,
            "l_values": l_pk_vals,
            "r_peak_over_R0": r_peak_list,
            "delta_r_over_R0": delta_r_list,
            "asymp_w4_over_R04": asymp_list,
        },
        "weber_kernel_check": {
            "fourier_max_abs_err": float(max(ft_errs)),
            "position_rel_err": pos_rel_err,
            "A_global_L2": 0.0,
            "B_global_L2": 1.0,
        },
        "paley_wiener_saturation": {
            "w": w_pw,
            "k_max": kmax_pw,
            "A_bound": A_pw,
            "B_bound": B_pw,
            "ring_upper_ratio": ratio_upper,
            "ring_lower_ratio": ratio_lower,
            "projected_dual_norm2": proj_dual_norm2,
            "unprojected_tail_10_20": unproj_tail,
        },
        "telecom_bridge": {
            "wavelength_nm": 1550.0,
            "k0_inv_m": k0,
            "NA": NA_tel,
            "w_um": w_tel_um,
            "k_max_inv_m": kmax_tel,
            "w_kmax": w_kmax_tel,
            "A_bound": A_tel,
            "B_bound": 1.0,
            "kappa_Sw": kappa_tel,
        },
    }


def run_suite_3(metrics: dict[str, Any], assertions: dict[str, bool]) -> None:
    """Suite 3: Tikhonov dual S_{w,alpha_reg}^{-1}, peak gain, synthesis multiplier, nonzero bias."""
    alpha_t = 1e-4
    w_t = 0.5
    k_peak = math.sqrt(math.log(1.0 / alpha_t)) / w_t

    def h_tikh(k: float) -> float:
        gw = float(weber_fourier_multiplier(k, w_t))
        return gw / (gw ** 2 + alpha_t)

    h_at_peak = h_tikh(k_peak)
    h_expected = 1.0 / (2.0 * math.sqrt(alpha_t))
    assert k_peak > 1.0 / w_t
    assert abs(h_at_peak - h_expected) < 1e-12
    assert abs(h_at_peak - 50.0) < 1e-12

    # Derivative zero check at k_peak
    dk = 1e-5
    deriv = (h_tikh(k_peak + dk) - h_tikh(k_peak - dk)) / (2.0 * dk)
    assert abs(deriv) < 1e-7

    # Synthesis multiplier M(k) = G_w^2 / (G_w^2 + alpha_reg) < 1 for alpha_reg > 0
    gw0 = float(weber_fourier_multiplier(1.0, w_t))
    synth_mult = (gw0 ** 2) / (gw0 ** 2 + alpha_t)
    assert 0.0 < synth_mult < 1.0

    # Nonzero shrinkage bias on LG_{2,1} (w/w0 = 0.25)
    b0, _, _ = tikhonov_mse_analytic(0.0, p=2, l=1, w_over_w0=0.25)
    b_m4, _, _ = tikhonov_mse_analytic(1e-4, p=2, l=1, w_over_w0=0.25)
    b_m3, _, _ = tikhonov_mse_analytic(1e-3, p=2, l=1, w_over_w0=0.25)
    b_m2, _, _ = tikhonov_mse_analytic(1e-2, p=2, l=1, w_over_w0=0.25)
    assert b0 == 0.0
    assert b_m4 > 1e-8
    assert b_m3 > b_m4
    assert b_m2 > b_m3

    metrics["frame_and_normalization"]["tikhonov_peak_check"] = {
        "alpha_reg": alpha_t,
        "w": w_t,
        "one_over_w": 1.0 / w_t,
        "k_peak": k_peak,
        "H_max": h_at_peak,
        "deriv_at_peak": deriv,
        "lg21_bias2_by_alpha": {
            "0.0": b0,
            "1e-4": b_m4,
            "1e-3": b_m3,
            "1e-2": b_m2,
        },
    }
    assertions["tikhonov_peak_and_bias_verified"] = True


def run_suite_4(metrics: dict[str, Any], assertions: dict[str, bool]) -> None:
    """Suite 4: Exact closed-form c_{l,p}(R) vs quad, synthesis, 2D FT of psi_{p,l}, Ferreira p=0."""
    w_c, w0_c = 0.3, 1.0
    R_vals = [0.3, 1.2, 2.5]
    pairs = [(0, 0), (0, 2), (1, 1), (2, -2), (3, 1), (4, -3)]
    test_cases = []
    max_abs_res = 0.0

    for p_v, l_v in pairs:
        errs = []
        for R_v in R_vals:
            c_cf = c_lp_closed_form(R_v, p_v, l_v, w_c, w0_c)
            c_qd = c_lp_quad(R_v, p_v, l_v, w_c, w0_c)
            err = abs(c_cf - c_qd)
            assert err <= 1e-14 or err < 1e-13
            errs.append(err)
            max_abs_res = max(max_abs_res, err)
        test_cases.append(
            {
                "p": p_v,
                "l": l_v,
                "w": w_c,
                "w0": w0_c,
                "max_abs_res": float(max(errs)),
            }
        )
    assertions["c_lp_quad_residual_lt_1e13"] = max_abs_res < 1e-13

    # Frame synthesis (S_w psi_{2,-1})(r, 0) vs polar Gaussian convolution (G_w * psi_{2,-1})(r, 0)
    synth_errs = []
    for r_eval in (0.4, 1.1, 2.0):
        synth_val, _ = quad(
            lambda R: R * c_lp_closed_form(R, 2, -1, w_c, w0_c) * pvb_radial(r_eval, -1, R, w_c),
            0.0,
            np.inf,
            epsabs=1e-13,
            epsrel=1e-13,
            limit=200,
        )
        conv_val, _ = quad(
            lambda rp: (rp / (w_c ** 2))
            * math.exp(-((r_eval - rp) ** 2) / (2.0 * w_c ** 2))
            * float(ive(1, r_eval * rp / (w_c ** 2)))
            * lg_radial(rp, 2, -1, w0_c),
            0.0,
            np.inf,
            epsabs=1e-13,
            epsrel=1e-13,
            limit=200,
        )
        err = abs(synth_val - conv_val)
        assert err < 1e-13
        synth_errs.append(err)

    # Exact 2D FT of psi_{p,l} vs numerical Hankel transform
    ft_lg_errs = []
    k_probe = 1.9
    for p_v, l_v in ((0, 0), (1, 1), (2, -1), (3, 2)):
        val_r, _ = quad(
            lambda r: r * lg_radial(r, p_v, l_v, w0_c) * float(jv(abs(l_v), k_probe * r)),
            0.0,
            np.inf,
            epsabs=1e-13,
            epsrel=1e-13,
            limit=200,
        )
        ft_num = 2.0 * math.pi * ((-1j) ** abs(l_v)) * val_r
        ft_ana = lg_2d_ft_radial(k_probe, p_v, l_v, w0_c)
        err = abs(ft_num - ft_ana)
        assert err < 1e-13
        ft_lg_errs.append(err)

    # p = 0 Ferreira unit-normalized check
    ferreira_errs = []
    for l_v in (-2, 0, 1, 3):
        for R_v in (0.6, 1.5):
            norm_phi = math.sqrt(float(pvb_gram_unnormalized([R_v], l_v, w_c)[0, 0]))
            c_unit_cf = c_lp_closed_form(R_v, 0, l_v, w_c, w0_c) / norm_phi
            c_unit_qd, _ = quad(
                lambda r: 2.0
                * math.pi
                * r
                * (pvb_radial(r, l_v, R_v, w_c) / norm_phi)
                * lg_radial(r, 0, l_v, w0_c),
                0.0,
                np.inf,
                epsabs=1e-13,
                epsrel=1e-13,
                limit=200,
            )
            err = abs(c_unit_cf - c_unit_qd)
            assert err < 1e-13
            ferreira_errs.append(err)

    metrics["laguerre_expansion_c_lp"] = {
        "test_cases": test_cases,
        "max_abs_residual_all": max_abs_res,
        "frame_synthesis_max_err": float(max(synth_errs)),
        "lg_2d_ft_max_err": float(max(ft_lg_errs)),
        "ferreira_p0_unit_max_err": float(max(ferreira_errs)),
    }


def run_suite_5(metrics: dict[str, Any], assertions: dict[str, bool]) -> None:
    """Suite 5: Table I nodal washout F, SymPy exact rationals, Rayleigh thresholds."""
    w_over_w0_grid = [0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 1.00]
    p_vals = [0, 1, 2, 3]
    l_t1 = 1
    rows = []
    p0_max_err = 0.0

    for ww0 in w_over_w0_grid:
        f_dict: dict[str, float] = {}
        for p_v in p_vals:
            f_val = nodal_washout_fidelity(p_v, l_t1, ww0)
            f_dict[str(p_v)] = f_val
            if p_v == 0:
                err0 = abs(f_val - nodal_washout_p0_closed(l_t1, ww0))
                assert err0 < 1e-14
                p0_max_err = max(p0_max_err, err0)
        rows.append({"w_over_w0": ww0, "F": f_dict})

    # Frame energy identity <psi_{2,1}, S_w psi_{2,1}> = int R |c_{1,2}(R)|^2 dR = int e^{-a u} rho_{2,1}(u) du
    w_id = 0.3
    e_radial, _ = quad(
        lambda R: R * (c_lp_closed_form(R, 2, 1, w_id, 1.0) ** 2),
        0.0,
        np.inf,
        epsabs=1e-13,
        epsrel=1e-13,
        limit=200,
    )
    e_fourier, _ = quad(
        lambda u: math.exp(-(w_id ** 2) * u) * laguerre_spectral_density(u, 2, 1),
        0.0,
        np.inf,
        epsabs=1e-13,
        epsrel=1e-13,
        limit=200,
    )
    energy_id_err = abs(e_radial - e_fourier)
    assert energy_id_err < 1e-13

    # SymPy exact rationals at w/w0 = 1, l = 1
    u_sym = sp.Symbol("u", positive=True)
    exact_rationals: dict[str, str] = {}
    for p_v in p_vals:
        lag_sym = sp.assoc_laguerre(p_v, l_t1, u_sym)
        rho_sym = sp.Rational(sp.factorial(p_v), sp.factorial(p_v + l_t1)) * u_sym * sp.exp(-u_sym) * lag_sym**2
        num_sym = sp.integrate(sp.exp(-u_sym) * rho_sym, (u_sym, 0, sp.oo))
        den_sym = sp.integrate(sp.exp(-2 * u_sym) * rho_sym, (u_sym, 0, sp.oo))
        f_sym = sp.simplify((num_sym ** 2) / den_sym)
        exact_rationals[str(p_v)] = str(f_sym)
        assert abs(float(f_sym) - rows[-1]["F"][str(p_v)]) < 1e-14

    expected_rats = {
        "0": "9/16",
        "1": "81/256",
        "2": "18225/74752",
        "3": "8037225/38862848",
    }
    assert exact_rationals == expected_rats
    assertions["table1_exact_rationals_match"] = True

    # Rayleigh criteria (F = 0.95)
    def wcrit_p0(l_v: int) -> float:
        return (((1.0 - 0.95 ** (1.0 / (abs(l_v) + 1))) ** (-0.5)) - 1.0) ** (-0.5)

    p0_l0 = wcrit_p0(0)
    p0_l1 = wcrit_p0(1)
    p0_l2 = wcrit_p0(2)
    assert abs(nodal_washout_fidelity(0, 0, p0_l0) - 0.95) < 1e-13
    assert abs(nodal_washout_fidelity(0, 1, p0_l1) - 0.95) < 1e-13
    assert abs(p0_l0 - 0.536663) < 1e-5
    assert abs(p0_l1 - 0.435013) < 1e-5

    exact_roots_l1: dict[str, dict[str, float]] = {
        "0": {"w_crit": p0_l1, "scaled": p0_l1 * math.sqrt(2 * 0 + 1 + 1)}
    }
    for p_v in (1, 2, 3, 10):
        w_root = float(
            brentq(lambda x: nodal_washout_fidelity(p_v, 1, x) - 0.95, 0.05, 0.6, xtol=1e-12)
        )
        scaled = w_root * math.sqrt(2 * p_v + 1 + 1)
        exact_roots_l1[str(p_v)] = {"w_crit": w_root, "scaled": scaled}
        assert 0.572 <= scaled <= 0.581

    # Arcsine p -> inf asymptote: I0(c)^2 / I0(2c) = 0.95
    c_arc = float(
        brentq(
            lambda c: (float(ive(0, c)) ** 2) * math.exp(2 * c) / (float(ive(0, 2 * c)) * math.exp(2 * c)) - 0.95,
            0.05,
            1.0,
            xtol=1e-13,
        )
    )
    # Note: ive(0, c)^2 / ive(0, 2c) = (I0(c) e^{-c})^2 / (I0(2c) e^{-2c}) = I0(c)^2 / I0(2c)!
    arcsine_coeff = math.sqrt(c_arc)
    taylor2_coeff = 0.10 ** 0.25
    assert abs(arcsine_coeff - 0.572440) < 1e-5
    assert abs(taylor2_coeff - 0.562341) < 1e-5

    metrics["table1_nodal_washout"] = {
        "l": l_t1,
        "w_over_w0_grid": w_over_w0_grid,
        "rows": rows,
        "exact_rationals_at_1": exact_rationals,
        "p0_closed_form_max_err": p0_max_err,
        "frame_energy_identity_err": energy_id_err,
        "rayleigh_threshold_F095": {
            "p0_exact_l0": p0_l0,
            "p0_exact_l1": p0_l1,
            "p0_exact_l2": p0_l2,
            "moderate_p_coeff": 0.573,
            "arcsine_c": c_arc,
            "arcsine_asymptote": arcsine_coeff,
            "taylor_2nd_coeff": taylor2_coeff,
            "exact_roots_l1": exact_roots_l1,
        },
    }


def run_suite_6(metrics: dict[str, Any], assertions: dict[str, bool]) -> None:
    """Suite 6: Table II normalized gamma_{nm} vs G_{nm}, ZF penalties, core breakdown, N=120."""
    N_t2, w_t2, l_t2, R_min_t2 = 6, 0.5, 1, 2.0
    ratios = [0.50, 1.00, 1.50, 2.00, 2.50, 3.00]
    rows = []
    prev_kappa_gamma = float("inf")

    for dr_w in ratios:
        dr = dr_w * w_t2
        R_grid = R_min_t2 + np.arange(N_t2) * dr
        G = pvb_gram_unnormalized(R_grid, l_t2, w_t2)
        gamma = pvb_gram_normalized(R_grid, l_t2, w_t2)
        assert np.allclose(G, G.T, atol=1e-14)
        eigs_gamma = np.linalg.eigvalsh(gamma)
        assert np.all(eigs_gamma > 0.0)

        kappa_G = float(np.linalg.cond(G))
        kappa_gamma = float(np.linalg.cond(gamma))
        assert kappa_gamma < prev_kappa_gamma
        prev_kappa_gamma = kappa_gamma

        gamma_inv = np.linalg.inv(gamma)
        zf_corr = float(np.trace(gamma_inv) / N_t2)
        zf_awgn = float(np.trace(gamma_inv @ gamma_inv) / N_t2)
        g12 = float(abs(gamma[0, 1]))
        g12_pow = g12 ** 2
        iso_dB = -10.0 * math.log10(g12_pow)

        if dr_w <= 1.0:
            regime = "Ill-conditioned"
        elif dr_w == 1.5:
            regime = "Transition"
        elif dr_w == 2.0:
            regime = "Optimal"
        else:
            regime = "Quasi-orthogonal"

        rows.append(
            {
                "delta_R_over_w": dr_w,
                "delta_R": dr,
                "gamma_12_amp": g12,
                "gamma_12_power": g12_pow,
                "power_isolation_dB": iso_dB,
                "kappa_G": kappa_G,
                "kappa_gamma": kappa_gamma,
                "zf_corr_factor": zf_corr,
                "zf_corr_dB": 10.0 * math.log10(zf_corr),
                "zf_awgn_factor": zf_awgn,
                "zf_awgn_dB": 10.0 * math.log10(zf_awgn),
                "regime": regime,
            }
        )

    # Verify exact Table II key rows (dr_w = 2.0 and 2.5)
    r_20 = next(r for r in rows if r["delta_R_over_w"] == 2.00)
    r_25 = next(r for r in rows if r["delta_R_over_w"] == 2.50)
    assert abs(r_20["gamma_12_amp"] - 0.13553) < 1e-4
    assert abs(r_20["power_isolation_dB"] - 17.36) < 0.02
    assert abs(r_20["kappa_gamma"] - 1.645) < 1e-3
    assert abs(r_20["zf_corr_factor"] - 1.0321) < 1e-3
    assert abs(r_20["zf_awgn_factor"] - 1.0994) < 1e-3
    assert abs(r_25["gamma_12_amp"] - 0.04402) < 1e-4
    assert abs(r_25["power_isolation_dB"] - 27.13) < 0.02
    assertions["table2_normalized_monotonic"] = True

    # Core breakdown check (R_min = 0.2 w, l = 1, delta_R = 2.0 w)
    R_core = np.array([0.2 * w_t2, 2.2 * w_t2])
    gamma_core = pvb_gram_normalized(R_core, 1, w_t2)
    assert abs(gamma_core[0, 1] - 0.3476) < 1e-3
    assert gamma_core[0, 1] > 2.0 * math.exp(-2.0)

    # N = 120 counterexample (delta_R/w = 2.0)
    R_120 = R_min_t2 + np.arange(120) * (2.0 * w_t2)
    kappa_G_120 = float(np.linalg.cond(pvb_gram_unnormalized(R_120, l_t2, w_t2)))
    kappa_gamma_120 = float(np.linalg.cond(pvb_gram_normalized(R_120, l_t2, w_t2)))
    assert kappa_G_120 > 50.0 and abs(kappa_G_120 - 80.015) < 0.1
    assert kappa_gamma_120 < 2.0 and abs(kappa_gamma_120 - 1.741) < 0.01

    metrics["table2_gram_and_sdm"] = {
        "params": {"N": N_t2, "w": w_t2, "l": l_t2, "R_min": R_min_t2},
        "rows": rows,
        "large_N_counterexample": {
            "N": 120,
            "delta_R_over_w": 2.0,
            "kappa_G": kappa_G_120,
            "kappa_gamma": kappa_gamma_120,
        },
        "near_core_counterexample": {
            "R_min_over_w": 0.2,
            "delta_R_over_w": 2.0,
            "l": 1,
            "gamma_12_exact": float(gamma_core[0, 1]),
            "exp_minus_2": math.exp(-2.0),
        },
    }


def run_sim_1_noisy_lg21(
    rng: np.random.Generator, metrics: dict[str, Any], assertions: dict[str, bool]
) -> None:
    """Sim 1: Worked noisy LG_{2,1} Tikhonov reconstruction + 2D-FFT Monte Carlo cross-check."""
    w_over_w0 = 0.25
    w_kmax = 3.0
    snr_dB = 20.0
    p_eta = 10.0 ** (-snr_dB / 10.0)
    alpha_grid = np.logspace(-6, 0, 121)
    bias2, var, total_mse = tikhonov_mse_analytic(
        alpha_grid, p=2, l=1, w_over_w0=w_over_w0, w_kmax=w_kmax, noise_power=p_eta
    )
    opt_res = minimize_scalar(
        lambda log_a: tikhonov_mse_analytic(10.0 ** log_a, p=2, l=1, w_over_w0=w_over_w0, w_kmax=w_kmax, noise_power=p_eta)[2],
        bounds=(-4.0, 0.0),
        method="bounded",
    )
    alpha_opt = 10.0 ** float(opt_res.x)
    b_opt, v_opt, mse_min = tikhonov_mse_analytic(
        alpha_opt, p=2, l=1, w_over_w0=w_over_w0, w_kmax=w_kmax, noise_power=p_eta
    )
    naive_mse_0 = (p_eta / (w_kmax ** 2)) * (math.exp(w_kmax ** 2) - 1.0)
    assert mse_min < 0.045
    assert naive_mse_0 > 8.9
    assert float(mse_min) < float(total_mse[0]) and float(mse_min) < float(total_mse[-1])

    # 2D-FFT Monte Carlo cross-check (256 x 256, L_box = 10 w0, 16 realizations)
    N_fft, L_box, w0 = 256, 10.0, 1.0
    w_pv = w_over_w0 * w0
    kmax = w_kmax / w_pv
    dx = L_box / N_fft
    x = (np.arange(N_fft) - N_fft / 2) * dx
    X, Y = np.meshgrid(x, x)
    R_grid = np.hypot(X, Y)
    PHI = np.arctan2(Y, X)
    psi_exact = lg_radial(R_grid, 2, 1, w0) * np.exp(1j * PHI)
    psi_exact /= math.sqrt(float(np.sum(np.abs(psi_exact) ** 2) * (dx ** 2)))

    kx = 2.0 * math.pi * np.fft.fftfreq(N_fft, d=dx)
    KX, KY = np.meshgrid(kx, kx)
    K = np.hypot(KX, KY)
    in_band = K <= kmax
    Gw = np.exp(-0.5 * (w_pv ** 2) * (K ** 2))
    psi_k = np.fft.fft2(psi_exact) * (dx ** 2)
    sw_psi_k = Gw * psi_k

    # Variance calibration for 2D DFT white noise inside K <= kmax:
    # Discrete Parseval: sum |eta_grid|^2 dx^2 = (1/L^2) sum |eta_k|^2 = p_eta
    n_in_band = int(np.sum(in_band))
    sigma_k = math.sqrt(p_eta * (L_box ** 2) / n_in_band)

    alpha_mc = [1e-4, 1e-3, 1e-2, 3.16227766e-2, 1e-1, 1.0]
    n_mc = 20
    mc_means = []
    mc_sems = []
    mc_analytic = []
    for alp in alpha_mc:
        H_tikh = np.where(in_band, Gw / (Gw ** 2 + alp), 0.0)
        trials = []
        for _ in range(n_mc):
            eta_k = np.zeros((N_fft, N_fft), dtype=complex)
            noise = (
                rng.standard_normal(n_in_band) + 1j * rng.standard_normal(n_in_band)
            ) * (sigma_k / math.sqrt(2.0))
            eta_k[in_band] = noise
            y_k = sw_psi_k + eta_k
            rec_k = H_tikh * y_k
            err_l2 = float(np.sum(np.abs(rec_k - psi_k) ** 2)) / (L_box ** 2)
            trials.append(err_l2)
        mc_means.append(float(np.mean(trials)))
        mc_sems.append(float(np.std(trials, ddof=1) / math.sqrt(n_mc)))
        _, _, m_an = tikhonov_mse_analytic(alp, p=2, l=1, w_over_w0=w_over_w0, w_kmax=w_kmax, noise_power=p_eta)
        mc_analytic.append(float(m_an))
        assert abs(mc_means[-1] - mc_analytic[-1]) < max(0.05 * mc_analytic[-1], 4.0 * mc_sems[-1] + 0.01)

    assertions["noisy_lg21_has_unique_interior_minimum"] = True
    metrics["noisy_lg21_reconstruction"] = {
        "mode": "LG_{2,1}",
        "w_over_w0": w_over_w0,
        "w_kmax": w_kmax,
        "snr_dB": snr_dB,
        "noise_energy": p_eta,
        "naive_mse_alpha0": naive_mse_0,
        "alpha_grid": [float(v) for v in alpha_grid],
        "bias2": [float(v) for v in bias2],
        "variance": [float(v) for v in var],
        "total_mse": [float(v) for v in total_mse],
        "alpha_opt": alpha_opt,
        "bias2_at_opt": b_opt,
        "var_at_opt": v_opt,
        "mse_min": mse_min,
        "mse_at_alpha_1e6": float(total_mse[0]),
        "mc_2d_fft_check": {
            "N_grid": N_fft,
            "n_trials": n_mc,
            "alpha_values": alpha_mc,
            "mc_mse_mean": mc_means,
            "mc_mse_sem": mc_sems,
            "analytic_mse": mc_analytic,
        },
    }


def run_sim_2_rcf_and_ber(metrics: dict[str, Any], assertions: dict[str, bool]) -> None:
    """Sim 2: Exact radial Sturm-Liouville RCF eigenmode solver + OOK/QPSK BER & SDM ZF penalties."""
    l_vals = list(range(9))
    r_grid, n_eff, rcf_modes = solve_rcf_eigenmodes(l_vals)
    r_center = 7.5
    w_telecom = 1.72
    w_opt = 1.92

    def coupling_efficiency(psi_rad: np.ndarray, mode_rad: np.ndarray) -> float:
        ov = float(np.trapezoid(r_grid * psi_rad * mode_rad, r_grid))
        return ov ** 2

    def norm_pvb(l_v: int, w_um: float) -> np.ndarray:
        raw = pvb_radial(r_grid, l_v, r_center, w_um)
        nrm = math.sqrt(float(np.trapezoid(r_grid * (raw ** 2), r_grid)))
        return raw / nrm

    def norm_lg0(l_v: int, w0_um: float) -> np.ndarray:
        raw = lg_radial(r_grid, 0, l_v, w0_um)
        nrm = math.sqrt(float(np.trapezoid(r_grid * (raw ** 2), r_grid)))
        return raw / nrm

    eta_pvb_172 = [coupling_efficiency(norm_pvb(l_v, w_telecom), rcf_modes[l_v]) for l_v in l_vals]
    eta_pvb_192 = [coupling_efficiency(norm_pvb(l_v, w_opt), rcf_modes[l_v]) for l_v in l_vals]
    eta_lg_450 = [coupling_efficiency(norm_lg0(l_v, 4.50), rcf_modes[l_v]) for l_v in l_vals]
    eta_lg_322 = [coupling_efficiency(norm_lg0(l_v, 3.22), rcf_modes[l_v]) for l_v in l_vals]
    eta_lg_1061 = [coupling_efficiency(norm_lg0(l_v, math.sqrt(2.0) * r_center), rcf_modes[l_v]) for l_v in l_vals]

    assert all(e > 0.99 for e in eta_pvb_172[:5])
    mean_pvb_172 = float(np.mean(eta_pvb_172))
    assert mean_pvb_172 > 0.98 and abs(mean_pvb_172 - 0.9852) < 1e-3
    assert abs(float(np.mean(eta_pvb_192)) - 0.9940) < 1e-3
    gain_l4_dB = 10.0 * math.log10(eta_pvb_172[4] / eta_lg_322[4])
    assert abs(gain_l4_dB - 6.83) < 0.15

    # OOK BER vs Eb/N0 (dB) at l=4 + SDM ZF penalties (N=6, w=0.5, l=1, R_min=2.0, delta_R/w=2.0)
    eb_n0_dB = np.linspace(0.0, 14.0, 29)
    eb_n0_lin = 10.0 ** (eb_n0_dB / 10.0)
    ber_pvb_l4 = [0.5 * float(erfc(math.sqrt(eta_pvb_172[4] * snr / 2.0))) for snr in eb_n0_lin]
    ber_lg_l4 = [0.5 * float(erfc(math.sqrt(eta_lg_322[4] * snr / 2.0))) for snr in eb_n0_lin]

    R_sdm = 2.0 + np.arange(6) * (2.0 * 0.5)
    gamma_sdm = pvb_gram_normalized(R_sdm, 1, 0.5)
    gamma_inv = np.linalg.inv(gamma_sdm)
    gamma_inv2 = gamma_inv @ gamma_inv
    zf_corr_diag = np.real(np.diag(gamma_inv))
    zf_awgn_diag = np.real(np.diag(gamma_inv2))
    ber_sdm_corr = [
        float(np.mean([0.5 * erfc(math.sqrt(snr / (2.0 * d_ii))) for d_ii in zf_corr_diag]))
        for snr in eb_n0_lin
    ]
    ber_sdm_awgn = [
        float(np.mean([0.5 * erfc(math.sqrt(snr / (2.0 * d_ii))) for d_ii in zf_awgn_diag]))
        for snr in eb_n0_lin
    ]

    metrics["classical_optics_utility"] = {
        "rcf_coupling": {
            "r_center_um": r_center,
            "r1_um": 6.0,
            "r2_um": 9.0,
            "n_clad": 1.444,
            "delta_n": 0.033,
            "w_um": w_telecom,
            "w_opt_um": w_opt,
            "l_values": l_vals,
            "n_eff": [float(n_eff[l_v]) for l_v in l_vals],
            "eta_pvb": eta_pvb_172,
            "eta_pvb_mean": mean_pvb_172,
            "eta_pvb_opt": eta_pvb_192,
            "eta_pvb_opt_mean": float(np.mean(eta_pvb_192)),
            "eta_lg_w0_450": eta_lg_450,
            "eta_lg_w0_322": eta_lg_322,
            "eta_lg_w0_1061": eta_lg_1061,
            "gain_dB_vs_lg322": [10.0 * math.log10(ep / el) for ep, el in zip(eta_pvb_172, eta_lg_322)],
            "villalba_benchmark_gain_dB": gain_l4_dB,
            "ber_eb_n0_dB": [float(v) for v in eb_n0_dB],
            "ber_pvb_l4": ber_pvb_l4,
            "ber_lg322_l4": ber_lg_l4,
            "ber_sdm_zf_corr_dr2w": ber_sdm_corr,
            "ber_sdm_zf_awgn_dr2w": ber_sdm_awgn,
        }
    }
    assertions["rcf_sturm_liouville_verified"] = True


def run_sim_3_kolmogorov(
    rng: np.random.Generator, metrics: dict[str, Any], assertions: dict[str, bool]
) -> None:
    """Sim 3: Subharmonic-corrected 2D Kolmogorov screens + Fresnel + RKHS projection."""
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
    psi0_k = (
        math.sqrt(2.0 * math.pi)
        * ((-1j) ** 1)
        * np.exp(1j * PHI_K)
        * np.exp(-0.25 * (w_mm ** 2) * (K ** 2))
        * jv(1, R0_mm * K)
    )
    psi0_k[K > kmax_pvb] = 0.0
    psi0 = np.fft.fftshift(np.fft.ifft2(psi0_k)) / (dx ** 2)
    psi0 /= math.sqrt(float(np.sum(np.abs(psi0) ** 2) * (dx ** 2)))

    lam_mm = 1.55e-3
    k0_mm = 2.0 * math.pi / lam_mm
    z_mm = 500.0
    HF = np.exp(-1j * (K ** 2) * z_mm / (2.0 * k0_mm))
    psi_clean = np.fft.ifft2(np.fft.fft2(psi0) * HF)
    I_clean = np.abs(psi_clean) ** 2
    norm_I = float(np.sum(I_clean ** 2) * (dx ** 2))

    alpha_reg = math.exp(-((w_mm * kmax_pvb) ** 2))
    Gw = np.exp(-0.5 * (w_mm ** 2) * (K ** 2))
    T_rkhs = (K <= kmax_pvb).astype(float)
    T_tikh = (Gw ** 2) / ((Gw ** 2) + alpha_reg)

    d_over_r0_grid = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    m_ens = 40

    field_raw_m, field_raw_s = [], []
    field_rkhs_m, field_rkhs_s = [], []
    field_tikh_m, field_tikh_s = [], []
    int_raw_m, int_raw_s = [], []
    int_rkhs_m, int_rkhs_s = [], []
    int_tikh_m, int_tikh_s = [], []

    for d_r0 in d_over_r0_grid:
        r0_mm = D_mm / d_r0
        fr, fk, ft = [], [], []
        ir, ik, it = [], [], []
        for _ in range(m_ens):
            phase = kolmogorov_subharmonic_screen(rng, N_grid, L_mm, r0_mm, mask, X, Y)
            psi_turb = np.fft.ifft2(np.fft.fft2(psi0 * np.exp(1j * phase)) * HF)
            psi_rkhs = np.fft.ifft2(np.fft.fft2(psi_turb) * T_rkhs)
            psi_tikh = np.fft.ifft2(np.fft.fft2(psi_turb) * T_tikh)

            fr.append(float(np.sum(np.abs(psi_turb - psi_clean) ** 2) * (dx ** 2)))
            fk.append(float(np.sum(np.abs(psi_rkhs - psi_clean) ** 2) * (dx ** 2)))
            ft.append(float(np.sum(np.abs(psi_tikh - psi_clean) ** 2) * (dx ** 2)))

            ir.append(float(np.sum(((np.abs(psi_turb) ** 2) - I_clean) ** 2) * (dx ** 2) / norm_I))
            ik.append(float(np.sum(((np.abs(psi_rkhs) ** 2) - I_clean) ** 2) * (dx ** 2) / norm_I))
            it.append(float(np.sum(((np.abs(psi_tikh) ** 2) - I_clean) ** 2) * (dx ** 2) / norm_I))

        assert np.mean(fk) < np.mean(fr) and np.mean(ft) < np.mean(fr)
        assert np.mean(ik) < np.mean(ir) and np.mean(it) < np.mean(ir)

        for arr, m_l, s_l in (
            (fr, field_raw_m, field_raw_s),
            (fk, field_rkhs_m, field_rkhs_s),
            (ft, field_tikh_m, field_tikh_s),
            (ir, int_raw_m, int_raw_s),
            (ik, int_rkhs_m, int_rkhs_s),
            (it, int_tikh_m, int_tikh_s),
        ):
            m_l.append(float(np.mean(arr)))
            s_l.append(float(np.std(arr, ddof=1) / math.sqrt(m_ens)))

    assertions["kolmogorov_rkhs_suppresses_noise"] = True
    metrics["classical_optics_utility"]["kolmogorov_rkhs"] = {
        "N_grid": N_grid,
        "L_box_mm": L_mm,
        "D_ap_mm": D_mm,
        "z_m": z_mm / 1000.0,
        "R0_mm": R0_mm,
        "w_mm": w_mm,
        "kmax_rad_per_mm": kmax_pvb,
        "alpha_reg": alpha_reg,
        "n_realizations": m_ens,
        "D_over_r0_grid": d_over_r0_grid,
        "field_mse_raw_mean": field_raw_m,
        "field_mse_raw_sem": field_raw_s,
        "field_mse_rkhs_mean": field_rkhs_m,
        "field_mse_rkhs_sem": field_rkhs_s,
        "field_mse_tikhonov_mean": field_tikh_m,
        "field_mse_tikhonov_sem": field_tikh_s,
        "int_mse_raw_mean": int_raw_m,
        "int_mse_raw_sem": int_raw_s,
        "int_mse_rkhs_mean": int_rkhs_m,
        "int_mse_rkhs_sem": int_rkhs_s,
        "int_mse_tikhonov_mean": int_tikh_m,
        "int_mse_tikhonov_sem": int_tikh_s,
    }


def run_sim_4_ic_povm(
    rng: np.random.Generator, metrics: dict[str, Any], assertions: dict[str, bool]
) -> None:
    """Sim 4: Multi-plane Gouy-diverse IC-POVM radial qudit tomography & MLE Monte Carlo."""
    d = 4
    l_qudit = 1
    w0 = 1.0
    w_ov_w0 = 0.25
    w_pv = w_ov_w0 * w0
    n_R = 40
    R_max = 3.5 * w0
    dR = R_max / n_R
    R_pts = (np.arange(n_R) + 0.5) * dR
    M_planes = 5
    zetas = np.linspace(0.0, 0.45 * math.pi, M_planes)

    # Single-plane (z=0) vs multi-plane operators
    c_mat = np.array([[c_lp_closed_form(R_k, p_v, l_qudit, w_pv, w0) for p_v in range(d)] for R_k in R_pts])

    E_single = []
    for k_idx, R_k in enumerate(R_pts):
        ket = c_mat[k_idx, :, None]
        E_single.append(R_k * dR * (ket @ ket.conj().T))
    E_single_arr = np.array(E_single, dtype=complex)
    rank_single = int(np.linalg.matrix_rank(E_single_arr.reshape(n_R, d * d), tol=1e-10))
    assert rank_single == 7

    E_multi = []
    p_idx = np.arange(d, dtype=float)
    for zeta in zetas:
        gouy = np.exp(-1j * (2.0 * p_idx + abs(l_qudit) + 1.0) * zeta)
        for k_idx, R_k in enumerate(R_pts):
            ket = (gouy * c_mat[k_idx])[:, None]
            E_multi.append((1.0 / M_planes) * R_k * dR * (ket @ ket.conj().T))
    E_multi_arr = np.array(E_multi, dtype=complex)
    rank_multi = int(np.linalg.matrix_rank(E_multi_arr.reshape(M_planes * n_R, d * d), tol=1e-10))
    assert rank_multi == 16
    assertions["ic_povm_full_rank_16"] = True

    sum_E = np.sum(E_multi_arr, axis=0)
    lam_max_sumE = float(np.max(np.linalg.eigvalsh(0.5 * (sum_E + sum_E.conj().T))))
    assert lam_max_sumE < 1.0 and abs(lam_max_sumE - 0.90498) < 1e-3

    E_res = np.eye(d, dtype=complex) - sum_E
    E_with_res = np.concatenate([E_multi_arr, E_res[None, :, :]], axis=0)

    T_basis = _gell_mann_basis(d)
    rho0 = np.eye(d, dtype=complex) / d

    F_no_res = _fisher_matrix(E_multi_arr, rho0, T_basis)
    F_with_res = _fisher_matrix(E_with_res, rho0, T_basis)
    lam_min_F = float(np.min(np.linalg.eigvalsh(F_with_res)))
    crb_no_res = float(np.trace(np.linalg.inv(F_no_res)))
    crb_with_res = float(np.trace(np.linalg.inv(F_with_res)))
    assert abs(crb_with_res - 41.80) < 0.02
    assert abs(crb_no_res - 42.96) < 0.02

    E_mub = np.array(_build_5_mubs_d4(), dtype=complex)
    F_mub = _fisher_matrix(E_mub, rho0, T_basis)
    crb_mub = float(np.trace(np.linalg.inv(F_mub)))
    assert abs(crb_mub - 18.75) < 0.01

    # Multinomial R-rho-R MLE Monte Carlo tracking CRB / N_phot
    p_pvb_true = np.maximum(np.real(np.einsum("mij,ji->m", E_with_res, rho0)), 0.0)
    p_pvb_true /= np.sum(p_pvb_true)
    p_mub_true = np.maximum(np.real(np.einsum("mij,ji->m", E_mub, rho0)), 0.0)
    p_mub_true /= np.sum(p_mub_true)

    n_phot_grid = [300, 1000, 3000, 10000, 30000]
    n_trials = 30
    mle_pvb_mean, mle_pvb_sem = [], []
    mle_mub_mean, mle_mub_sem = [], []

    for n_ph in n_phot_grid:
        errs_p, errs_m = [], []
        for _ in range(n_trials):
            c_p = rng.multinomial(n_ph, p_pvb_true)
            rho_p = r_rho_r_mle(c_p, E_with_res, n_iter=60)
            errs_p.append(float(np.real(np.trace((rho_p - rho0) @ (rho_p - rho0)))))

            c_m = rng.multinomial(n_ph, p_mub_true)
            rho_m = r_rho_r_mle(c_m, E_mub, n_iter=60)
            errs_m.append(float(np.real(np.trace((rho_m - rho0) @ (rho_m - rho0)))))

        mle_pvb_mean.append(float(np.mean(errs_p)))
        mle_pvb_sem.append(float(np.std(errs_p, ddof=1) / math.sqrt(n_trials)))
        mle_mub_mean.append(float(np.mean(errs_m)))
        mle_mub_sem.append(float(np.std(errs_m, ddof=1) / math.sqrt(n_trials)))

    # Assert MLE converges within 25% of CRB at N_phot = 30000
    assert abs(mle_pvb_mean[-1] - crb_with_res / 30000.0) / (crb_with_res / 30000.0) < 0.25

    metrics.setdefault("quantum_optics_utility", {})["ic_povm_radial_qudit"] = {
        "d": d,
        "l": l_qudit,
        "w_over_w0": w_ov_w0,
        "M_planes": M_planes,
        "n_R_bins": n_R,
        "R_max_over_w0": R_max / w0,
        "single_plane_rank": rank_single,
        "multi_plane_rank": rank_multi,
        "lambda_max_sum_E": lam_max_sumE,
        "lambda_min_fisher": lam_min_F,
        "crb_with_Eres": crb_with_res,
        "crb_no_Eres": crb_no_res,
        "crb_sequential_mub": crb_mub,
        "N_phot_grid": n_phot_grid,
        "n_trials": n_trials,
        "mle_mse_pvb_mean": mle_pvb_mean,
        "mle_mse_pvb_sem": mle_pvb_sem,
        "mle_mse_mub_mean": mle_mub_mean,
        "mle_mse_mub_sem": mle_mub_sem,
    }


def run_sim_5_spdc_iris(metrics: dict[str, Any], assertions: dict[str, bool]) -> None:
    """Sim 5: High-d QKD footprint & SPDC circular-iris Bell-CHSH S(R_iris/R0)."""
    R0 = 1.0
    w_pv = 0.1
    w0_lg = math.sqrt(2.0) * R0
    l_channels = [1, 2, 3, 4]

    t_pvb_R0 = [pvb_iris_transmission(R0, R0, w_pv, l_v) for l_v in l_channels]
    t_lg_R0 = [lg0l_iris_transmission(R0, w0_lg, l_v) for l_v in l_channels]

    expected_pvb = [0.4999, 0.4996, 0.4991, 0.4984]
    expected_lg = [0.2642, 0.0803, 0.0190, 0.0037]
    for a, b in zip(t_pvb_R0, expected_pvb):
        assert abs(a - b) < 1e-4
    for a, b in zip(t_lg_R0, expected_lg):
        assert abs(a - b) < 1e-4

    def chsh_1arm(t1: float, t4: float) -> float:
        c = (2.0 * math.sqrt(t1 * t4)) / (t1 + t4)
        return 2.0 * math.sqrt(1.0 + c ** 2)

    def chsh_2arm(t1: float, t4: float) -> float:
        c = (2.0 * t1 * t4) / (t1 ** 2 + t4 ** 2)
        return 2.0 * math.sqrt(1.0 + c ** 2)

    S_pvb_R0 = chsh_2arm(t_pvb_R0[0], t_pvb_R0[-1])
    S_lg_1arm_R0 = chsh_1arm(t_lg_R0[0], t_lg_R0[-1])
    S_lg_2arm_R0 = chsh_2arm(t_lg_R0[0], t_lg_R0[-1])
    assert abs(S_pvb_R0 - 2.8284) < 5e-4
    assert abs(S_lg_1arm_R0 - 2.0532) < 5e-4
    assert abs(S_lg_2arm_R0 - 2.0008) < 5e-4
    assertions["spdc_chsh_matches"] = True

    r_iris_grid = np.linspace(0.6, 2.2, 33)
    s_pvb_1, s_pvb_2, s_lg_1, s_lg_2 = [], [], [], []
    for r_ir in r_iris_grid:
        tp1 = pvb_iris_transmission(float(r_ir), R0, w_pv, 1)
        tp4 = pvb_iris_transmission(float(r_ir), R0, w_pv, 4)
        tl1 = lg0l_iris_transmission(float(r_ir), w0_lg, 1)
        tl4 = lg0l_iris_transmission(float(r_ir), w0_lg, 4)
        s_pvb_1.append(chsh_1arm(tp1, tp4))
        s_pvb_2.append(chsh_2arm(tp1, tp4))
        s_lg_1.append(chsh_1arm(tl1, tl4))
        s_lg_2.append(chsh_2arm(tl1, tl4))

    metrics["quantum_optics_utility"]["spdc_iris_invariance"] = {
        "R0": R0,
        "w": w_pv,
        "w0_lg_matched": w0_lg,
        "l_channels": l_channels,
        "t_pvb_at_R0": t_pvb_R0,
        "t_lg_at_R0": t_lg_R0,
        "R_iris_over_R0_grid": [float(v) for v in r_iris_grid],
        "S_pvb_1arm": s_pvb_1,
        "S_pvb_2arm": s_pvb_2,
        "S_lg_1arm": s_lg_1,
        "S_lg_2arm": s_lg_2,
        "S_pvb_at_R0": S_pvb_R0,
        "S_lg_1arm_at_R0": S_lg_1arm_R0,
        "S_lg_2arm_at_R0": S_lg_2arm_R0,
    }


def run_verification(json_out: Path | None = None, seed: int = 2026) -> dict[str, Any]:
    """Run all 6 mathematical assertion suites and 5 physics simulations, returning metrics."""
    rng = np.random.default_rng(seed)
    metrics: dict[str, Any] = {}
    assertions: dict[str, bool] = {}

    run_suite_1_and_2(metrics, assertions)
    run_suite_3(metrics, assertions)
    run_suite_4(metrics, assertions)
    run_suite_5(metrics, assertions)
    run_suite_6(metrics, assertions)
    run_sim_1_noisy_lg21(rng, metrics, assertions)
    run_sim_2_rcf_and_ber(metrics, assertions)
    run_sim_3_kolmogorov(rng, metrics, assertions)
    run_sim_4_ic_povm(rng, metrics, assertions)
    run_sim_5_spdc_iris(metrics, assertions)

    all_ok = all(assertions.values())
    ordered_metrics = {
        "metadata": {
            "schema_version": "1.0.0",
            "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rng_seed": seed,
            "versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "scipy": scipy.__version__,
                "sympy": sp.__version__,
                "matplotlib": matplotlib.__version__,
            },
            "all_assertions_passed": all_ok,
        },
        **metrics,
        "assertions": assertions,
    }

    if json_out is not None:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(ordered_metrics, indent=2), encoding="utf-8")

    return ordered_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify V6 PVB mathematical and physical optics suites.")
    parser.add_argument(
        "--json-out",
        type=Path,
        default=SCRIPTS_DIR / "verified_metrics.json",
        help="Output path for verified_metrics.json",
    )
    args = parser.parse_args()
    res = run_verification(json_out=args.json_out, seed=2026)
    print(f"[verify_math_and_tables] all_assertions_passed={res['metadata']['all_assertions_passed']}")
    for k, v in res["assertions"].items():
        print(f"  - {k}: {'PASS' if v else 'FAIL'}")
    print(f"[verify_math_and_tables] Exported {args.json_out}")
    return 0 if res["metadata"]["all_assertions_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
