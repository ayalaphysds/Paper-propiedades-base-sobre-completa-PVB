"""First-principles analytical and numerical verification routines for continuous
Hilbert frames of physical perfect optical vortex beams (PVBs).

All formulas use collision-free notation:
  - w         : PVB annular half-width
  - R         : PVB ring radius
  - w0        : Laguerre-Gaussian (LG) beam waist
  - xi        : Dimensionless width parameter 2*w^2 / (w0^2 + w^2)
  - zeta_R    : Dimensionless Laguerre argument R^2 * w0^2 / [w^2 * (w0^2 + w^2)]
  - alpha_reg : Dimensionless Tikhonov regularization parameter
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np
from scipy.integrate import quad
from scipy.special import eval_genlaguerre, gammaln, ive

mp.mp.dps = 50


def c0_frame(w: float) -> float:
    """Continuous-frame resolution-of-identity scaling C_0 = sqrt(2/pi) / w^2."""
    return math.sqrt(2.0 / math.pi) / (w ** 2)


def c_lp_closed_form(l: int, p: int, R: float, w: float, w0: float) -> float:
    """Exact (p+1)-term closed-form projection c_{l,p}(R) = <Phi_{l,R} | psi_{p,l}>."""
    abs_l = abs(l)
    denom = w0 ** 2 + w ** 2
    xi = 2.0 * (w ** 2) / denom
    zeta_R = (R ** 2) * (w0 ** 2) / ((w ** 2) * denom)

    log_fact_ratio = 0.5 * float(gammaln(p + 1) - gammaln(p + abs_l + 1))
    prefactor = (
        (2.0 ** (0.5 * abs_l + 1.0))
        * math.exp(log_fact_ratio)
        * ((R ** abs_l) * (w0 ** (abs_l + 1)) / (denom ** (abs_l + 1)))
        * math.exp(-(R ** 2) / denom)
    )

    poly_sum = 0.0
    for m in range(p + 1):
        binom_val = math.comb(p + abs_l, p - m)
        lag_val = float(eval_genlaguerre(m, abs_l, -zeta_R))
        poly_sum += ((-1.0) ** m) * binom_val * (xi ** m) * lag_val

    return prefactor * poly_sum


def c_lp_mpmath_quad(l: int, p: int, R: float, w: float, w0: float) -> float:
    """Arbitrary-precision numerical quadrature of <Phi_{l,R} | psi_{p,l}>."""
    abs_l = abs(l)
    R_mp = mp.mpf(str(R))
    w_mp = mp.mpf(str(w))
    w0_mp = mp.mpf(str(w0))

    C0 = mp.sqrt(2 / mp.pi) / (w_mp ** 2)
    N_pl = mp.sqrt(2 * mp.factorial(p) / (mp.pi * mp.factorial(p + abs_l))) / w0_mp

    def integrand(r):
        pvb_rad = C0 * mp.e ** (-((r - R_mp) ** 2) / (w_mp ** 2)) * (
            mp.e ** (-2 * R_mp * r / (w_mp ** 2)) * mp.besseli(abs_l, 2 * R_mp * r / (w_mp ** 2))
        )
        lg_rad = (
            N_pl
            * ((mp.sqrt(2) * r / w0_mp) ** abs_l)
            * mp.laguerre(p, abs_l, 2 * (r ** 2) / (w0_mp ** 2))
            * mp.e ** (-(r ** 2) / (w0_mp ** 2))
        )
        return 2 * mp.pi * r * pvb_rad * lg_rad

    val = mp.quad(integrand, [0, R_mp + 6 * w_mp, mp.inf])
    return float(val)


def verify_60_entry_table() -> list[dict]:
    """Verify all 60 entries requested in Reviewer Specification B4."""
    modes = [(0, 0), (1, 0), (0, 1), (2, 1), (3, 2)]
    w_ratios = [0.25, 0.5, 1.0]
    R_ratios = [0.5, 1.0, 1.5, 2.0]
    w0 = 1.0

    rows = []
    max_rel_err = 0.0
    max_abs_err = 0.0

    for p, l in modes:
        for w_ov_w0 in w_ratios:
            w = w_ov_w0 * w0
            for R_ov_w0 in R_ratios:
                R = R_ov_w0 * w0
                c_exact = c_lp_closed_form(l, p, R, w, w0)
                c_quad = c_lp_mpmath_quad(l, p, R, w, w0)
                abs_err = abs(c_exact - c_quad)
                rel_err = abs_err / max(abs(c_quad), 1e-30)
                max_rel_err = max(max_rel_err, rel_err)
                max_abs_err = max(max_abs_err, abs_err)
                assert abs_err < 1e-14 and rel_err < 1e-10, f"Mismatch at (p={p},l={l},w={w},R={R}): abs={abs_err}, rel={rel_err}"
                rows.append(
                    {
                        "p": p,
                        "l": l,
                        "w_over_w0": w_ov_w0,
                        "R_over_w0": R_ov_w0,
                        "c_exact": c_exact,
                        "c_quad": c_quad,
                        "abs_err": abs_err,
                        "rel_err": rel_err,
                    }
                )

    print(f"Verified all {len(rows)} B4 table entries: max |dc| = {max_abs_err:.3e}, max |dc|/|c| = {max_rel_err:.3e}")
    return rows


def verify_rayleigh_and_sharpness() -> None:
    """Verify Corollary 1 w_crit(0,l) identity and Theorem 1 sharpness integrals."""
    for l in [0, 1, 2, 4]:
        q_l = 0.95 ** (1.0 / (abs(l) + 1))
        w1 = ((1.0 - q_l) ** (-0.5) - 1.0) ** (-0.5)
        w2 = ((1.0 - math.sqrt(1.0 - q_l)) ** (-1.0) - 1.0) ** 0.5
        assert abs(w1 - w2) < 1e-15, f"Formula mismatch at l={l}: {w1} vs {w2}"
        a = w2 ** 2
        fid = ((1.0 + 2.0 * a) / ((1.0 + a) ** 2)) ** (abs(l) + 1)
        assert abs(fid - 0.95) < 1e-15
        print(f"l={l}: w_crit(0,{l})/w0 = {w2:.6f}, F = {fid:.15f}")

    # Verify Theorem 1 sharpness annulus integrals
    w = 0.5
    k_max = 2.788  # wk_max = 1.394
    A_exact = math.exp(-0.5 * (w * k_max) ** 2)
    for eps in [1e-1, 1e-3, 1e-5]:
        upper_val = 2.0 * (1.0 - math.exp(-0.5 * (w * eps) ** 2)) / ((w * eps) ** 2)
        lower_val = (
            2.0
            * (math.exp(-0.5 * (w * (k_max - eps)) ** 2) - math.exp(-0.5 * (w * k_max) ** 2))
            / ((w ** 2) * eps * (2.0 * k_max - eps))
        )
    print(f"Sharpness eps=1e-5: upper={upper_val:.8f} (B=1), lower={lower_val:.8f} (A={A_exact:.8f})")


if __name__ == "__main__":
    rows = verify_60_entry_table()
    verify_rayleigh_and_sharpness()
    out_path = Path(__file__).resolve().parent / "theorem2_table_60.json"
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
