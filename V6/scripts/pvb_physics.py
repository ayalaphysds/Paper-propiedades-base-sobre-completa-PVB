"""
First-principles mathematical and physical optics kernel for Physical Perfect Vortex
Beams (PVBs) under V6 notation conventions:
  - w         : PVB annular half-width
  - R         : PVB ring radius
  - w0        : Laguerre-Gaussian (LG) beam waist
  - alpha_reg : Tikhonov regularization parameter (dimensionless)
  - a0        : Combined Gaussian exponent 1/w^2 + 1/w0^2 [length^-2]

All modified Bessel functions use exponentially scaled scipy.special.ive
to eliminate 0 * inf = NaN overflow during adaptive quadrature and matrix evaluation.
"""

from __future__ import annotations

import math
from typing import Callable, Sequence

import mpmath as mp
import numpy as np
from scipy.integrate import quad
from scipy.linalg import eigh_tridiagonal
from scipy.special import erfc, eval_genlaguerre, gammainc, gammaln, ive, jv


def _factorial_ratio_sqrt(p: int, abs_l: int) -> float:
    """Overflow-safe sqrt(p! / (p + |l|)!) using log-gamma for arbitrary p + |l|."""
    return math.exp(0.5 * float(gammaln(p + 1) - gammaln(p + abs_l + 1)))


def _split_ring_quad(
    integrand: Callable[[float], float],
    a: float,
    b: float,
    R0: float,
    w: float,
    epsabs: float = 1e-13,
    epsrel: float = 1e-13,
    limit: int = 200,
) -> float:
    """Peak-bracketed adaptive quadrature over [a, b] resolving narrow rings centered at R0."""
    if (
        not (math.isfinite(R0) and math.isfinite(w) and w > 0.0)
        or math.isnan(a)
        or math.isnan(b)
        or b <= a
    ):
        return 0.0
    # Integrate in shifted dimensionless coordinate u = (r - R0) / w (r = R0 + w * u)
    # so narrow rings (w << R0) resolve without r - R0 roundoff loss.
    u_lo = -30.0 if (math.isinf(a) and a < 0.0) else max(-30.0, (float(a) - R0) / w)
    u_hi = 30.0 if (math.isinf(b) and b > 0.0) else min(30.0, (float(b) - R0) / w)
    if u_hi <= u_lo:
        return 0.0
    candidates = (-14.0, -4.0, -1.0, 0.0, 1.0, 4.0, 14.0)
    pts = sorted({float(pt) for pt in candidates if u_lo < pt < u_hi})
    bounds = [u_lo, *pts, u_hi]
    total = 0.0
    for u0, u1 in zip(bounds[:-1], bounds[1:]):
        val, _ = quad(
            lambda u: w * integrand(R0 + w * u),
            u0,
            u1,
            epsabs=epsabs,
            epsrel=epsrel,
            limit=limit,
        )
        total += float(val)
    return float(total)


def _safe_ive(abs_l: int, x: np.ndarray | float) -> np.ndarray | float:
    """Evaluate exp(-x)*I_{|l|}(x), switching to 3-term Hankel asymptotic above 5e8 to avoid SciPy's 2^30 ive NaN cliff."""
    x_arr = np.asarray(x, dtype=float)
    huge = x_arr > 5.0e8
    if not np.any(huge):
        res = ive(abs_l, x_arr)
        return float(res) if np.ndim(x) == 0 else res
    out = np.empty_like(x_arr, dtype=float)
    reg = ~huge
    if np.any(reg):
        out[reg] = ive(abs_l, x_arr[reg])
    if np.any(huge):
        xh = x_arr[huge]
        inv_x = 1.0 / xh
        mu = 4.0 * (abs_l ** 2)
        t1 = (mu - 1.0) * (0.125 * inv_x)
        t2 = (mu - 1.0) * (mu - 9.0) * ((inv_x * inv_x) / 128.0)
        out[huge] = (1.0 / math.sqrt(2.0 * math.pi)) * np.sqrt(inv_x) * (1.0 - t1 + t2)
    return float(out) if np.ndim(x) == 0 else out


def pvb_c0(w: float) -> float:
    """Resolution-of-identity scaling constant C0 = sqrt(2/pi) / w^2."""
    return math.sqrt(2.0 / math.pi) / (w ** 2)


def pvb_radial(r: np.ndarray | float, l: int, R: float, w: float) -> np.ndarray | float:
    """
    Physical PVB radial profile Phi_{l,R}^{rad}(r) using exponentially scaled ive:
      Phi_{l,R}(r, phi) = C0 * exp(-(r-R)^2/w^2) * ive(|l|, 2*R*r/w^2) * exp(i*l*phi).
    """
    r_arr = np.asarray(r, dtype=float)
    val = np.zeros_like(r_arr, dtype=float)
    if not (math.isfinite(R) and math.isfinite(w) and w > 0.0):
        return float(val) if np.ndim(r) == 0 else val
    abs_l = abs(l)
    fin = np.isfinite(r_arr)
    half_diff = np.empty_like(r_arr, dtype=float)
    half_diff[fin] = np.abs(0.5 * r_arr[fin] - 0.5 * R)
    active = fin & (half_diff < 14.0 * w)
    if np.any(active):
        ra = r_arr[active]
        d2 = ((ra - R) / w) ** 2
        res_a = np.zeros_like(ra, dtype=float)
        both_pos = (R > 0.0) & (ra > 0.0)
        if np.any(both_pos):
            rp = ra[both_pos]
            log_arg = math.log(2.0) + math.log(R) + np.log(rp) - 2.0 * math.log(w)
            huge_arg = log_arg > 690.0
            sub = np.empty_like(rp, dtype=float)
            if np.any(huge_arg):
                # For 2*R*r/w^2 > e^690, C0 * ive(|l|, arg) reduces to 1/(sqrt(2)*pi*w*sqrt(R*r))
                sub[huge_arg] = np.exp(
                    -d2[both_pos][huge_arg]
                    - 0.5 * math.log(2.0)
                    - math.log(math.pi)
                    - math.log(w)
                    - 0.5 * (math.log(R) + np.log(rp[huge_arg]))
                )
            reg_arg = ~huge_arg
            if np.any(reg_arg):
                c0 = pvb_c0(w)
                sub[reg_arg] = (
                    c0
                    * np.exp(-d2[both_pos][reg_arg])
                    * _safe_ive(abs_l, np.exp(log_arg[reg_arg]))
                )
            res_a[both_pos] = sub
        non_pos = ~both_pos
        if np.any(non_pos):
            rn = ra[non_pos]
            arg_n = np.where((R == 0.0) | (rn == 0.0), 0.0, 2.0 * (R / w) * (rn / w))
            res_a[non_pos] = pvb_c0(w) * np.exp(-d2[non_pos]) * _safe_ive(abs_l, arg_n)
        val[active] = res_a
    if np.ndim(r) == 0:
        return float(val)
    return val


def pvb_gram_unnormalized(R_grid: Sequence[float], l: int, w: float) -> np.ndarray:
    """Exact unnormalized Gram matrix G_{nm} = <Phi_{l,R_n} | Phi_{l,R_m}> via Weber 6.633.2."""
    R_arr = np.asarray(R_grid, dtype=float)
    n = R_arr.size
    G = np.zeros((n, n), dtype=float)
    if n == 0 or not (math.isfinite(w) and w > 0.0):
        return G
    fin = np.isfinite(R_arr)
    if not np.any(fin):
        return G
    abs_l = abs(l)
    Rf = R_arr[fin]
    m = Rf.size
    Gf = np.zeros((m, m), dtype=float)
    half_diff = np.abs(0.5 * Rf[:, None] - 0.5 * Rf[None, :])
    near = half_diff < 19.5 * w
    if np.any(near):
        r1 = np.broadcast_to(Rf[:, None], (m, m))[near]
        r2 = np.broadcast_to(Rf[None, :], (m, m))[near]
        d = (r1 - r2) / w
        vals = np.zeros_like(d, dtype=float)
        both_pos = (r1 > 0.0) & (r2 > 0.0)
        if np.any(both_pos):
            r1p, r2p, dp = r1[both_pos], r2[both_pos], d[both_pos]
            log_arg = np.log(r1p) + np.log(r2p) - 2.0 * math.log(w)
            huge_arg = log_arg > 690.0
            sub = np.empty_like(dp, dtype=float)
            if np.any(huge_arg):
                sub[huge_arg] = np.exp(
                    -0.5 * (dp[huge_arg] ** 2)
                    - math.log(w)
                    - 0.5 * (math.log(2.0 * math.pi) + np.log(r1p[huge_arg]) + np.log(r2p[huge_arg]))
                )
            reg_arg = ~huge_arg
            if np.any(reg_arg):
                sub[reg_arg] = (
                    np.exp(-0.5 * (dp[reg_arg] ** 2) - 2.0 * math.log(w))
                    * _safe_ive(abs_l, np.exp(log_arg[reg_arg]))
                )
            vals[both_pos] = sub
        non_pos = ~both_pos
        if np.any(non_pos):
            r1n, r2n, dn = r1[non_pos], r2[non_pos], d[non_pos]
            arg_n = np.where((r1n == 0.0) | (r2n == 0.0), 0.0, (r1n / w) * (r2n / w))
            vals[non_pos] = np.exp(-0.5 * (dn ** 2) - 2.0 * math.log(w)) * _safe_ive(abs_l, arg_n)
        Gf[near] = vals
    G[np.ix_(fin, fin)] = Gf
    return G


def _log_0f1_bessel(abs_l: int, r1: float, r2: float, w: float) -> float:
    """Compute log(0F1(; |l|+1; ((r1*r2)/(2*w^2))^2)) cleanly across extreme scales."""
    if r1 <= 0.0 or r2 <= 0.0:
        return 0.0
    log_x = math.log(r1) + math.log(r2) - 2.0 * math.log(w)
    thresh = 2.0 * math.sqrt(500.0 * (abs_l + 1))
    if log_x <= math.log(thresh):
        x = math.exp(log_x)
        z = 0.25 * x * x
        s_tail = 0.0
        term = 1.0
        for k in range(1, 200):
            term *= z / (k * (abs_l + k))
            s_tail += term
            if term <= 1e-16 * (1.0 + s_tail):
                break
        return math.log1p(s_tail)
    x = math.exp(log_x) if log_x < 709.0 else float("inf")
    if math.isfinite(x):
        iv = float(_safe_ive(abs_l, x))
        if iv > 0.0:
            return x + math.log(iv) - abs_l * (log_x - math.log(2.0)) + float(gammaln(abs_l + 1))
    with mp.workdps(80):
        zm = ((mp.mpf(r1) * mp.mpf(r2)) / (mp.mpf(w) ** 2)) ** 2 / 4
        return float(mp.log(mp.hyper([], [abs_l + 1], zm)))


def pvb_gram_normalized(R_grid: Sequence[float], l: int, w: float) -> np.ndarray:
    """
    Unit-normalized Gram matrix gamma_{nm} = G_{nm} / sqrt(G_{nn} * G_{mm}).
    Guards true zero/non-finite modes (R <= 0 for l != 0 or non-finite R) via
    identity fallback, while recovering scale-free gamma_{nm} via 0F1 when
    positive finite radii underflow float64 ive (e.g., R/w << 1 at large |l|).
    """
    R_arr = np.asarray(R_grid, dtype=float)
    if np.any(R_arr < 0.0):
        raise ValueError("R_grid radii must be non-negative.")
    G = pvb_gram_unnormalized(R_arr, l, w)
    n = R_arr.size
    if n == 0:
        return G
    abs_l = abs(l)
    w_ok = math.isfinite(w) and w > 0.0
    diag = np.sqrt(np.diag(G))
    gamma = np.zeros_like(G, dtype=float)
    pos = diag > 0.0
    if np.any(pos):
        sub_diag = diag[pos]
        gamma[np.ix_(pos, pos)] = G[np.ix_(pos, pos)] / np.outer(sub_diag, sub_diag)
    if not np.all(pos):
        r_flat = R_arr.ravel()
        valid_mode = np.array(
            [
                w_ok and math.isfinite(float(rv)) and (float(rv) > 0.0 or abs_l == 0)
                for rv in r_flat
            ],
            dtype=bool,
        )
        for i in np.flatnonzero(~pos):
            if not valid_mode[i]:
                gamma[i, i] = 1.0
                continue
            ri = float(r_flat[i])
            gamma[i, i] = 1.0
            for j in range(n):
                if j == i:
                    continue
                if not valid_mode[j]:
                    gamma[i, j] = 0.0
                    gamma[j, i] = 0.0
                    continue
                rj = float(r_flat[j])
                if ri == rj:
                    val_ij = 1.0
                elif (
                    ri > 0.0
                    and rj > 0.0
                    and (math.log(ri) - math.log(w)) > 21.0
                    and (math.log(rj) - math.log(w)) > 21.0
                ):
                    diff_w = (ri - rj) / w
                    val_ij = math.exp(-0.5 * diff_w * diff_w) if abs(diff_w) < 39.0 else 0.0
                else:
                    lg_ij = _log_0f1_bessel(abs_l, ri, rj, w)
                    lg_ii = _log_0f1_bessel(abs_l, ri, ri, w)
                    lg_jj = _log_0f1_bessel(abs_l, rj, rj, w)
                    log_g = lg_ij - 0.5 * (lg_ii + lg_jj)
                    val_ij = math.exp(log_g) if log_g > -745.0 else 0.0
                gamma[i, j] = val_ij
                gamma[j, i] = val_ij
    return gamma


def pvb_2d_ft_radial(k: np.ndarray | float, l: int, R: float, w: float) -> complex | np.ndarray:
    """
    Non-unitary 2D FT radial/azimuthal prefactor at phi_k = 0:
      F{Phi_{l,R}}(k, phi_k=0) = sqrt(2*pi) * (-i)^|l| * exp(-w^2 k^2 / 4) * J_|l|(R*k).
    """
    k_arr = np.asarray(k, dtype=float)
    val = np.zeros_like(k_arr, dtype=complex)
    if not (math.isfinite(R) and math.isfinite(w) and w > 0.0):
        return complex(val) if np.ndim(k) == 0 else val
    abs_l = abs(l)
    active = np.isfinite(k_arr) & ((np.abs(k_arr) * w) < 60.0)
    if np.any(active):
        ka = k_arr[active]
        r_lim = 1.0e300 / max(abs(R), 1.0)
        rk_ok = np.abs(ka) <= r_lim
        if np.any(rk_ok):
            k_sub = ka[rk_ok]
            wk = w * k_sub
            res = (
                math.sqrt(2.0 * math.pi)
                * ((-1j) ** abs_l)
                * np.exp(-0.25 * (wk ** 2))
                * jv(abs_l, R * k_sub)
            )
            sub = np.zeros_like(ka, dtype=complex)
            sub[rk_ok] = res
            val[active] = sub
    return complex(val) if np.ndim(k) == 0 else val


def weber_fourier_multiplier(k: np.ndarray | float, w: float) -> np.ndarray | float:
    """Fourier multiplier G_tilde_w(k) = exp(-w^2 k^2 / 2) of frame operator S_w."""
    k_arr = np.asarray(k, dtype=float)
    val = np.zeros_like(k_arr, dtype=float)
    if not (math.isfinite(w) and w >= 0.0):
        return float(val) if np.ndim(k) == 0 else val
    active = np.isfinite(k_arr) & ((np.abs(k_arr) * w) < 40.0)
    if np.any(active):
        wk = w * k_arr[active]
        val[active] = np.exp(-0.5 * (wk ** 2))
    return float(val) if np.ndim(k) == 0 else val


def lg_radial(r: np.ndarray | float, p: int, l: int, w0: float) -> np.ndarray | float:
    """Unit-L2-normalized Laguerre-Gaussian radial mode R_{p,l}(r) at z = 0 (without e^{i l phi}/sqrt(2*pi) or with 1/sqrt(2*pi) included)."""
    r_arr = np.asarray(r, dtype=float)
    val = np.zeros_like(r_arr, dtype=float)
    if not (math.isfinite(w0) and w0 > 0.0):
        return float(val) if np.ndim(r) == 0 else val
    abs_l = abs(l)
    log_norm = 0.5 * math.log(2.0 / math.pi) - math.log(w0) + 0.5 * float(gammaln(p + 1) - gammaln(p + abs_l + 1))
    cutoff = max(28.0, math.sqrt(800.0 + 10.0 * (2 * p + abs_l)))
    active = np.isfinite(r_arr) & ((np.abs(r_arr) / w0) < cutoff)
    if np.any(active):
        ra = r_arr[active]
        rw = ra / w0
        rho = 2.0 * (rw ** 2)
        lag = eval_genlaguerre(p, abs_l, rho)
        if abs_l == 0:
            log_env = log_norm - 0.5 * rho
            ok = log_env > -745.0
            env = np.zeros_like(rw, dtype=float)
            env[ok] = np.exp(log_env[ok])
        else:
            env = np.zeros_like(rw, dtype=float)
            nz = rw != 0.0
            if np.any(nz):
                rwn = rw[nz]
                sign = np.where((rwn < 0.0) & (abs_l % 2 == 1), -1.0, 1.0)
                log_env = log_norm + abs_l * (0.5 * math.log(2.0) + np.log(np.abs(rwn))) - 0.5 * rho[nz]
                ok = log_env > -745.0
                sub = np.zeros_like(rwn, dtype=float)
                sub[ok] = sign[ok] * np.exp(log_env[ok])
                env[nz] = sub
        val[active] = env * lag
    if np.ndim(r) == 0:
        return float(val)
    return val


def lg_2d_ft_radial(k: np.ndarray | float, p: int, l: int, w0: float) -> complex | np.ndarray:
    """
    Exact non-unitary 2D Fourier transform of psi_{p,l}(r, phi) at phi_k = 0:
      psi_tilde_{p,l}(k, 0) = (-1)^p (-i)^|l| sqrt(2*pi*p!/(p+|l|)!) * w0
                              * (w0*k/sqrt(2))^|l| L_p^|l|(w0^2 k^2 / 2) exp(-w0^2 k^2 / 4).
    """
    k_arr = np.asarray(k, dtype=float)
    val = np.zeros_like(k_arr, dtype=complex)
    if not (math.isfinite(w0) and w0 > 0.0):
        return complex(val) if np.ndim(k) == 0 else val
    abs_l = abs(l)
    log_pref = 0.5 * math.log(2.0 * math.pi) + math.log(w0) + 0.5 * float(gammaln(p + 1) - gammaln(p + abs_l + 1))
    phase = ((-1) ** p) * ((-1j) ** abs_l)
    cutoff_wk = max(65.0, math.sqrt(2.0 * (1600.0 + 10.0 * (2 * p + abs_l))))
    active = np.isfinite(k_arr) & ((np.abs(k_arr) * w0) < cutoff_wk)
    if np.any(active):
        wk = w0 * k_arr[active]
        u = 0.5 * (wk ** 2)
        lag = eval_genlaguerre(p, abs_l, u)
        if abs_l == 0:
            log_env = log_pref - 0.5 * u
            ok = log_env > -745.0
            env = np.zeros_like(wk, dtype=float)
            env[ok] = np.exp(log_env[ok])
        else:
            env = np.zeros_like(wk, dtype=float)
            nz = wk != 0.0
            if np.any(nz):
                wkn = wk[nz]
                sign = np.where((wkn < 0.0) & (abs_l % 2 == 1), -1.0, 1.0)
                log_env = log_pref + abs_l * (np.log(np.abs(wkn)) - 0.5 * math.log(2.0)) - 0.5 * u[nz]
                ok = log_env > -745.0
                sub = np.zeros_like(wkn, dtype=float)
                sub[ok] = sign[ok] * np.exp(log_env[ok])
                env[nz] = sub
        val[active] = phase * env * lag
    return complex(val) if np.ndim(k) == 0 else val


def c_lp_closed_form(R: np.ndarray | float, p: int, l: int, w: float, w0: float) -> np.ndarray | float:
    """
    Exact (p+1)-term closed-form expansion coefficient c_{l,p}(R) = <Phi_{l,R} | psi_{p,l}>
    for arbitrary p >= 0 and integer l (including l < 0).
    Uses nonsingular (eta, eta*z) vectorized float64 for p <= 4 and high-precision
    mpmath recurrence for p > 4 to prevent alternating-sum cancellation and w -> 0 singularity.
    """
    R_arr = np.asarray(R, dtype=float)
    abs_l = abs(l)
    if not (math.isfinite(w) and math.isfinite(w0) and w > 0.0 and w0 > 0.0):
        return 0.0 if np.ndim(R) == 0 else np.zeros_like(R_arr, dtype=float)
    scale = math.hypot(w0, w)
    if p > 4:
        dps = max(60, 2 * p + 30)
        flat_R = np.atleast_1d(R_arr).ravel()
        out_vals = np.empty(flat_R.shape[0], dtype=float)
        with mp.workdps(dps):
            w_m = mp.mpf(w)
            w0_m = mp.mpf(w0)
            denom_w = (w0_m ** 2) + (w_m ** 2)
            norm_m = mp.mpf(2) * mp.sqrt(mp.factorial(p) / mp.factorial(p + abs_l)) * mp.power(2, mp.mpf(abs_l) / 2)
            eta_m = (2 * (w_m ** 2)) / denom_w
            for idx, r_val in enumerate(flat_R):
                r_f = float(r_val)
                if not math.isfinite(r_f):
                    out_vals[idx] = 0.0
                    continue
                if r_f == 0.0 and abs_l > 0:
                    out_vals[idx] = 0.0
                    continue
                r_scaled = abs(r_f) / scale
                if (r_scaled * r_scaled) > (800.0 + 10.0 * p):
                    out_vals[idx] = 0.0
                    continue
                R_m = mp.mpf(r_f)
                pref_m = (
                    norm_m
                    * (R_m ** abs_l)
                    * (w0_m ** (abs_l + 1))
                    / (denom_w ** (abs_l + 1))
                    * mp.exp(-(R_m ** 2) / denom_w)
                )
                z_m = ((R_m ** 2) * (w0_m ** 2)) / ((w_m ** 2) * denom_w)
                L_prev = mp.mpf(1)
                total_m = mp.binomial(p + abs_l, p) * L_prev
                if p >= 1:
                    L_curr = mp.mpf(1 + abs_l) + z_m
                    total_m -= mp.binomial(p + abs_l, p - 1) * eta_m * L_curr
                    eta_pow = eta_m
                    for m in range(2, p + 1):
                        L_next = ((2 * m - 1 + abs_l + z_m) * L_curr - (m - 1 + abs_l) * L_prev) / m
                        L_prev, L_curr = L_curr, L_next
                        eta_pow *= eta_m
                        if m % 2 == 1:
                            total_m -= mp.binomial(p + abs_l, p - m) * eta_pow * L_curr
                        else:
                            total_m += mp.binomial(p + abs_l, p - m) * eta_pow * L_curr
                out_vals[idx] = float(pref_m * total_m)
        if np.ndim(R) == 0:
            return float(out_vals[0])
        return out_vals.reshape(R_arr.shape)

    active = np.isfinite(R_arr) & (np.abs(R_arr) < (40.0 + 4.0 * math.sqrt(float(p + 1))) * scale)
    val = np.zeros_like(R_arr, dtype=float)
    if np.any(active):
        ra = R_arr[active]
        r_s = ra / scale
        w0_s = w0 / scale
        w_s = w / scale
        eta = 2.0 * (w_s * w_s)
        xi = 2.0 * ((r_s * w0_s) ** 2)
        log_norm = math.log(2.0) + 0.5 * float(gammaln(p + 1) - gammaln(p + abs_l + 1)) + math.log(w0_s) - math.log(scale)
        if abs_l == 0:
            log_p = log_norm - (r_s * r_s)
            ok = log_p > -745.0
            pref = np.zeros_like(ra, dtype=float)
            pref[ok] = np.exp(log_p[ok])
        else:
            pref = np.zeros_like(ra, dtype=float)
            nz = ra != 0.0
            if np.any(nz):
                rn = ra[nz]
                r_sn = np.abs(r_s[nz])
                sign = np.where((rn < 0.0) & (abs_l % 2 == 1), -1.0, 1.0)
                log_p = log_norm + abs_l * (0.5 * math.log(2.0) + math.log(w0_s) + np.log(r_sn)) - (r_sn * r_sn)
                ok = log_p > -745.0
                sub = np.zeros_like(rn, dtype=float)
                sub[ok] = sign[ok] * np.exp(log_p[ok])
                pref[nz] = sub
        total = np.zeros_like(ra, dtype=float)
        for m in range(p + 1):
            binom_outer = math.comb(p + abs_l, p - m)
            inner = np.zeros_like(ra, dtype=float)
            for j in range(m + 1):
                inner += math.comb(m + abs_l, m - j) * (eta ** (m - j)) * (xi ** j) / math.factorial(j)
            total += ((-1) ** m) * binom_outer * inner
        val[active] = pref * total
    if np.ndim(R) == 0:
        return float(val)
    return val


def c_lp_quad(R: float, p: int, l: int, w: float, w0: float) -> float:
    """Direct 1D numerical quadrature of <Phi_{l,R} | psi_{p,l}> using ive and scale-adaptive coordinates."""
    if not (math.isfinite(R) and math.isfinite(w) and math.isfinite(w0) and w > 0.0 and w0 > 0.0):
        return 0.0
    abs_l = abs(l)
    cutoff_w0 = max(28.0, math.sqrt(800.0 + 10.0 * (2 * p + abs_l)))
    if R >= 0.0 and (R - 30.0 * w) >= cutoff_w0 * w0:
        return 0.0

    def _ive_val(r_val: float) -> float:
        if R > 0.0:
            log_arg = math.log(2.0) + math.log(R) + math.log(r_val) - 2.0 * math.log(w)
            if log_arg > 690.0:
                return math.exp(-0.5 * (math.log(2.0 * math.pi) + log_arg))
            if log_arg < -745.0:
                return 0.0
            return float(_safe_ive(abs_l, math.exp(log_arg)))
        if R == 0.0:
            return 1.0 if abs_l == 0 else 0.0
        return float(_safe_ive(abs_l, 2.0 * (R / w) * (r_val / w)))

    if w > 2.0 * w0:
        s_lo = max(0.0, (R - 30.0 * w) / w0)
        s_hi = min(cutoff_w0, (R + 30.0 * w) / w0)
        if s_hi <= s_lo:
            return 0.0
        pref_s = 2.0 * math.pi * (math.sqrt(2.0 / math.pi) / w) * (w0 / w)

        def _integrand_s(s: float) -> float:
            r = w0 * s
            if r <= 0.0:
                return 0.0
            u = (r - R) / w
            return pref_s * r * math.exp(-u * u) * _ive_val(r) * float(lg_radial(r, p, l, w0))

        lg_scale = math.sqrt(float(2 * p + abs_l + 1))
        cands = (
            0.25,
            0.5,
            1.0,
            2.0,
            4.0,
            8.0,
            14.0,
            22.0,
            0.5 * lg_scale,
            lg_scale,
            1.5 * lg_scale,
            R / w0,
            (R - w) / w0,
            (R + w) / w0,
        )
        pts = sorted({float(pt) for pt in cands if s_lo < pt < s_hi})
        bounds = [s_lo, *pts, s_hi]
        samples = [abs(_integrand_s(pt)) for pt in bounds]
        samples.extend(abs(_integrand_s(0.5 * (a + b))) for a, b in zip(bounds[:-1], bounds[1:]))
        max_s = max(samples) if samples else 0.0
        if max_s == 0.0:
            return 0.0
        eps_a = max(1e-300, 1e-14 * max_s * (s_hi - s_lo))
        total = 0.0
        for s0, s1 in zip(bounds[:-1], bounds[1:]):
            val, _ = quad(_integrand_s, s0, s1, epsabs=eps_a, epsrel=1e-13, limit=250)
            total += float(val)
        return float(total)

    u_lo = max(-30.0, -R / w)
    u_hi = min(30.0, (cutoff_w0 * w0 - R) / w)
    if u_hi <= u_lo:
        return 0.0
    pref = 2.0 * math.pi * (math.sqrt(2.0 / math.pi) / w)

    def _integrand_u(u: float) -> float:
        r = R + w * u
        if r <= 0.0:
            return 0.0
        return pref * r * math.exp(-u * u) * _ive_val(r) * float(lg_radial(r, p, l, w0))

    candidates = (-14.0, -4.0, -1.0, 0.0, 1.0, 4.0, 14.0)
    pts = sorted({float(pt) for pt in candidates if u_lo < pt < u_hi})
    bounds = [u_lo, *pts, u_hi]
    samples = [abs(_integrand_u(pt)) for pt in bounds]
    samples.extend(abs(_integrand_u(0.5 * (a + b))) for a, b in zip(bounds[:-1], bounds[1:]))
    max_u = max(samples) if samples else 0.0
    eps_a = max(1e-300, 1e-14 * max_u * (u_hi - u_lo)) if max_u > 0.0 else 1e-13
    total = 0.0
    for u0, u1 in zip(bounds[:-1], bounds[1:]):
        val, _ = quad(_integrand_u, u0, u1, epsabs=eps_a, epsrel=1e-13, limit=200)
        total += float(val)
    return float(total)


def laguerre_spectral_density(u: np.ndarray | float, p: int, l: int) -> np.ndarray | float:
    """Normalized spectral density rho_{p,l}(u) = (p!/(p+|l|)!) u^|l| e^{-u} [L_p^|l|(u)]^2."""
    abs_l = abs(l)
    u_arr = np.asarray(u, dtype=float)
    val = np.zeros_like(u_arr, dtype=float)
    active = np.isfinite(u_arr) & (u_arr >= 0.0) & (u_arr < 745.0)
    if np.any(active):
        ua = u_arr[active]
        sqrt_pref = math.exp(0.5 * float(gammaln(p + 1) - gammaln(p + abs_l + 1)))
        amp = sqrt_pref * (ua ** (0.5 * abs_l)) * np.exp(-0.5 * ua) * eval_genlaguerre(p, abs_l, ua)
        val[active] = amp * amp
    return float(val) if np.ndim(u) == 0 else val


def nodal_washout_fidelity(p: int, l: int, w_over_w0: float) -> float:
    """
    Exact radial nodal washout fidelity F(p, l, w/w0) = (<psi, S_w psi>)^2 / ||S_w psi||^2
    evaluated via rescaled variable v = (1 + k*a)*u so exp(-v) has O(1) decay across all w/w0 >= 0.
    """
    if not math.isfinite(w_over_w0):
        return 0.0
    if w_over_w0 <= 0.0:
        return 1.0
    if w_over_w0 > 1.0e150:
        return 0.0
    abs_l = abs(l)
    a = w_over_w0 * w_over_w0
    s1 = 1.0 + a
    s2 = 1.0 + 2.0 * a
    inv_binom = math.exp(float(gammaln(p + 1) + gammaln(abs_l + 1) - gammaln(p + abs_l + 1)))
    lg_gl = float(gammaln(abs_l + 1))

    def _scaled_moment(s: float) -> float:
        def _integ(v: float) -> float:
            if v <= 0.0:
                wt = 1.0 if abs_l == 0 else 0.0
            else:
                wt = math.exp(abs_l * math.log(v) - v - lg_gl)
            lag = inv_binom * float(eval_genlaguerre(p, abs_l, v / s))
            return wt * (lag * lag)

        if abs_l > 0:
            v1, _ = quad(_integ, 0.0, float(abs_l), epsabs=0.0, epsrel=1e-13, limit=200)
            v2, _ = quad(_integ, float(abs_l), np.inf, epsabs=0.0, epsrel=1e-13, limit=200)
            return float(v1 + v2)
        val, _ = quad(_integ, 0.0, np.inf, epsabs=0.0, epsrel=1e-13, limit=200)
        return float(val)

    j1 = _scaled_moment(s1)
    j2 = _scaled_moment(s2)
    log_scale = (abs_l + 1) * (math.log(s2) - 2.0 * math.log(s1)) - math.log(inv_binom)
    scale_fac = math.exp(log_scale) if log_scale > -745.0 else 0.0
    res = scale_fac * (j1 * j1) / j2
    return float(min(1.0, max(0.0, res)))


def nodal_washout_p0_closed(l: int, w_over_w0: float) -> float:
    """Closed-form washout fidelity at p = 0: [(1 + 2a) / (1 + a)^2]^(|l| + 1)."""
    if not math.isfinite(w_over_w0):
        return 0.0
    if w_over_w0 <= 0.0:
        return 1.0
    if w_over_w0 > 1.0e75:
        log_res = (abs(l) + 1) * (math.log(2.0) - 2.0 * math.log(w_over_w0))
        return math.exp(log_res) if log_res > -745.0 else 0.0
    a = w_over_w0 ** 2
    return ((1.0 + 2.0 * a) / ((1.0 + a) ** 2)) ** (abs(l) + 1)


def tikhonov_mse_analytic(
    alpha_reg: np.ndarray | float,
    p: int = 2,
    l: int = 1,
    w_over_w0: float = 0.25,
    w_kmax: float = 3.0,
    noise_power: float = 0.01,
) -> tuple[np.ndarray | float, np.ndarray | float, np.ndarray | float]:
    """
    Exact continuous Parseval Bias^2 + Variance + Total MSE for Tikhonov-regularized
    inversion of S_w psi_{p,l} + eta (with white bandlimited noise of total power P_eta).
    """
    arr = np.asarray(alpha_reg, dtype=float)
    scalar = arr.ndim == 0
    alphas = np.atleast_1d(arr).ravel()
    bias2 = np.zeros_like(alphas)
    var = np.zeros_like(alphas)

    if math.isnan(w_over_w0) or math.isnan(w_kmax):
        if scalar:
            return float("nan"), float("nan"), float("nan")
        nan_out = np.full(arr.shape, float("nan"), dtype=float)
        return nan_out, nan_out.copy(), nan_out.copy()

    huge_a = (not math.isfinite(w_over_w0)) or abs(w_over_w0) >= 1.0e150
    a = float("inf") if huge_a else (w_over_w0 ** 2)
    huge_k = (not math.isfinite(w_kmax)) or abs(w_kmax) >= 1.0e150
    x_k = float("inf") if huge_k else (w_kmax ** 2)
    g_min_sq = 0.0 if (huge_k or x_k >= 709.0) else math.exp(-x_k)

    for idx, alp_raw in enumerate(alphas):
        alp = float(alp_raw)
        if math.isnan(alp):
            bias2[idx] = float("nan")
            var[idx] = float("nan")
            continue
        if alp == 0.0:
            bias2[idx] = 0.0
            if x_k <= 0.0:
                var[idx] = float(noise_power)
            elif not huge_k and x_k < 709.0:
                var[idx] = float(noise_power) * (math.expm1(x_k) / x_k)
            else:
                var[idx] = float("inf")
            continue
        if math.isinf(alp) and alp > 0.0:
            bias2[idx] = 1.0
            var[idx] = 0.0
            continue
        if huge_a:
            bias2[idx] = 1.0
        else:
            def _bias_integrand(u: float) -> float:
                exp_val = math.exp(-2.0 * a * u) if (2.0 * a * u) < 709.0 else 0.0
                return ((alp / (exp_val + alp)) ** 2) * float(laguerre_spectral_density(u, p, l))

            if a > 10.0 and alp > 0.0:
                u_trans = math.log(max(1.0 / abs(alp), 1.0)) / (2.0 * a)
                du = 35.0 / (2.0 * a)
                pts = sorted({pt for pt in (u_trans - du, u_trans, u_trans + du) if pt > 0.0})
                bounds = [0.0, *pts, np.inf]
                tot_b = 0.0
                for u0, u1 in zip(bounds[:-1], bounds[1:]):
                    val_b, _ = quad(_bias_integrand, u0, u1, epsabs=1e-14, epsrel=1e-13, limit=200)
                    tot_b += float(val_b)
                bias2[idx] = float(tot_b)
            else:
                b2, _ = quad(_bias_integrand, 0.0, np.inf, epsabs=1e-14, epsrel=1e-13, limit=200)
                bias2[idx] = float(b2)
        if huge_k:
            var[idx] = 0.0
        elif x_k <= 0.0:
            var[idx] = float(noise_power) / ((1.0 + alp) ** 2) if alp >= 0.0 else float("nan")
        elif x_k < 709.0:
            ratio_m_expm1 = (-math.expm1(-x_k)) / x_k
            var[idx] = float(noise_power) * ratio_m_expm1 / ((g_min_sq + alp) * (1.0 + alp))
        else:
            var[idx] = (float(noise_power) / x_k) / ((g_min_sq + alp) * (1.0 + alp))

    mse = bias2 + var
    if scalar:
        return float(bias2[0]), float(var[0]), float(mse[0])
    return bias2.reshape(arr.shape), var.reshape(arr.shape), mse.reshape(arr.shape)


def solve_rcf_eigenmodes(
    l_values: Sequence[int],
    r1_um: float = 6.0,
    r2_um: float = 9.0,
    wavelength_um: float = 1.55,
    n_clad: float = 1.444,
    delta_n: float = 0.033,
    r_min_um: float = 0.01,
    r_max_um: float = 20.0,
    n_r: int = 2500,
) -> tuple[np.ndarray, dict[int, float], dict[int, np.ndarray]]:
    """
    Solve the exact 1D radial scalar Helmholtz Sturm-Liouville eigenvalue problem
    for a step-index ring-core fiber (RCF) using scipy.linalg.eigh_tridiagonal.
    Returns (r_grid, n_eff_by_l, normalized_mode_by_l) where integral r |F_l(r)|^2 dr = 1.
    Note: Default FD grid (n_r=2500, r_max_um=20.0) matches the manuscript's reported
    +6.90 dB gain (6.8963 dB) within ~0.01 dB of exact 3-layer Bessel dispersion (6.9081 dB).
    """
    r_grid = np.linspace(r_min_um, r_max_um, n_r)
    h = r_grid[1] - r_grid[0]
    k0 = 2.0 * math.pi / wavelength_um
    n_core = n_clad + delta_n
    n_prof = np.where((r_grid >= r1_um) & (r_grid <= r2_um), n_core, n_clad)
    off_diag = np.full(n_r - 1, -1.0 / (h ** 2))

    n_eff: dict[int, float] = {}
    modes: dict[int, np.ndarray] = {}
    for l_val in l_values:
        diag = (
            2.0 / (h ** 2)
            + ((l_val ** 2 - 0.25) / (r_grid ** 2))
            - (k0 ** 2) * (n_prof ** 2)
        )
        evals, evecs = eigh_tridiagonal(
            diag, off_diag, select="i", select_range=(0, 0)
        )
        beta_sq = -float(evals[0])
        if beta_sq <= 0:
            raise ValueError(f"Mode l={l_val} is below cutoff (beta^2={beta_sq}).")
        n_eff[l_val] = math.sqrt(beta_sq) / k0
        chi = evecs[:, 0]
        if np.sum(chi) < 0:
            chi = -chi
        field = chi / np.sqrt(r_grid)
        norm = math.sqrt(float(np.trapezoid(r_grid * (field ** 2), r_grid)))
        modes[l_val] = field / norm

    return r_grid, n_eff, modes


def kolmogorov_subharmonic_screen(
    rng: np.random.Generator,
    n_grid: int,
    L_mm: float,
    r0_mm: float,
    mask: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
) -> np.ndarray:
    """
    Generate a 2D Kolmogorov phase screen with 3 octaves of Lane et al. (1992)
    subharmonics and least-squares piston + tip + tilt removal over the pupil mask.
    """
    dx = L_mm / n_grid
    df = 1.0 / L_mm
    fx = np.fft.fftfreq(n_grid, d=dx)
    FX, FY = np.meshgrid(fx, fx)
    F = np.hypot(FX, FY)
    PSD = np.zeros_like(F)
    nz = F > 0.0
    PSD[nz] = 0.023 * (r0_mm ** (-5.0 / 3.0)) * (F[nz] ** (-11.0 / 3.0))

    cn = (
        rng.standard_normal((n_grid, n_grid)) + 1j * rng.standard_normal((n_grid, n_grid))
    ) * np.sqrt(PSD) * df
    phase = np.real(np.fft.ifft2(cn) * (n_grid ** 2))

    # 3-octave Lane subharmonic cascade
    for p_oct in range(1, 4):
        dfp = 1.0 / ((3 ** p_oct) * L_mm)
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                fxp = ix * dfp
                fyp = iy * dfp
                fp = math.hypot(fxp, fyp)
                psdp = 0.023 * (r0_mm ** (-5.0 / 3.0)) * (fp ** (-11.0 / 3.0))
                cp = (rng.standard_normal() + 1j * rng.standard_normal()) * math.sqrt(psdp) * dfp
                phase += np.real(cp * np.exp(1j * 2.0 * math.pi * (fxp * X + fyp * Y)))

    # Remove piston + tip + tilt over pupil aperture
    B_mat = np.column_stack([np.ones_like(X[mask]), X[mask], Y[mask]])
    coeffs = np.linalg.lstsq(B_mat, phase[mask], rcond=None)[0]
    phase = phase - (coeffs[0] + coeffs[1] * X + coeffs[2] * Y)
    return phase


def r_rho_r_mle(
    counts: np.ndarray,
    E_ops: np.ndarray,
    n_iter: int = 80,
) -> np.ndarray:
    """
    Damped R-rho-R iterative maximum-likelihood estimator for quantum state tomography
    given observed outcome counts and POVM elements E_ops of shape (M_out, d, d).
    """
    d = E_ops.shape[1]
    rho = np.eye(d, dtype=complex) / d
    G_op = np.sum(E_ops, axis=0)
    G_inv_sqrt = np.linalg.inv(_hermitian_sqrt(G_op))
    nz = counts > 0
    E_nz = E_ops[nz]
    c_nz = counts[nz]

    for _ in range(n_iter):
        probs = np.real(np.einsum("mij,ji->m", E_nz, rho))
        probs = np.maximum(probs, 1e-15)
        weights = c_nz / probs
        R_op = np.tensordot(weights, E_nz, axes=(0, 0))
        K_op = G_inv_sqrt @ R_op @ G_inv_sqrt
        rho_next = K_op @ rho @ K_op.conj().T
        rho_next = 0.5 * (rho_next + rho_next.conj().T)
        tr = float(np.real(np.trace(rho_next)))
        if tr > 0:
            rho = rho_next / tr
    return rho


def _hermitian_sqrt(A: np.ndarray) -> np.ndarray:
    """Matrix square root of a Hermitian positive-definite matrix."""
    evals, evecs = np.linalg.eigh(0.5 * (A + A.conj().T))
    evals = np.maximum(evals, 1e-15)
    return (evecs * np.sqrt(evals)) @ evecs.conj().T


def pvb_iris_transmission(R_iris: float, R0: float, w: float, l: int) -> float:
    """Exact normalized circular-iris power transmission t_l^{PVB}(R_iris) via shifted peak-bracketed ive quadrature."""
    if R_iris <= 0.0:
        return 0.0
    if math.isfinite(R0) and R0 <= 0.0 and l != 0:
        raise ValueError("pvb_iris_transmission undefined for R0 <= 0 with l != 0.")
    if not (math.isfinite(R0) and math.isfinite(w) and w > 0.0) or math.isnan(R_iris):
        return 0.0
    if math.isinf(R_iris):
        return 1.0
    abs_l = abs(l)
    # Narrow large-radius limit (30*w << R0): Hankel asymptotic reduces transmission to 0.5 * erfc(sqrt(2)*(R0 - R_iris)/w)
    if (R0 / w) > 1.0e7 * max(1, abs_l):
        return float(0.5 * erfc(math.sqrt(2.0) * ((R0 - R_iris) / w)))

    u_lo = max(-20.0, -R0 / w)
    u_iris = min(20.0, (R_iris - R0) / w)
    if u_iris <= u_lo:
        return 0.0

    def _u_quad(fn: Callable[[float], float], a: float, b: float, extra_pts: tuple[float, ...] = ()) -> float:
        if b <= a:
            return 0.0
        base = (-10.0, -4.0, -1.0, 0.0, 1.0, 4.0, 10.0, *extra_pts)
        pts = sorted({float(pt) for pt in base if a < pt < b})
        bounds = [a, *pts, b]
        tot = 0.0
        for x0, x1 in zip(bounds[:-1], bounds[1:]):
            val, _ = quad(fn, x0, x1, epsabs=1e-14, epsrel=1e-12, limit=200)
            tot += float(val)
        return float(tot)

    r_norm = max(R0, w)

    def _integrand_u(u: float) -> float:
        r = R0 + w * u
        if r <= 0.0:
            return 0.0
        arg = 2.0 * (R0 / w) * (r / w)
        iv = float(_safe_ive(abs_l, arg))
        return (r / r_norm) * math.exp(-2.0 * u * u) * (iv * iv)

    den = _u_quad(_integrand_u, u_lo, 20.0)
    if den > 0.0:
        num = _u_quad(_integrand_u, u_lo, u_iris)
        return float(min(1.0, max(0.0, num / den)))

    # Underflow fallback when ive(|l|, arg)^2 < 5e-324 (e.g., R0 << w with large |l|):
    # factor out the constant (R0 / w^2)^{2|l|} via I_{|l|}(x) = (x/2)^|l| / |l|! * 0F1(; |l|+1; x^2/4).
    r_peak = max(R0, w * math.sqrt((2.0 * abs_l + 1.0) / 4.0))
    u_peak = (r_peak - R0) / w
    u_max = max(20.0, u_peak + 20.0)
    u_ir = min(u_max, (R_iris - R0) / w)
    if u_ir <= u_lo:
        return 0.0
    extra = (u_peak - 4.0, u_peak - 1.0, u_peak, u_peak + 1.0, u_peak + 4.0)

    def _series_0f1(x: float) -> float:
        z = 0.25 * x * x
        s = 1.0
        term = 1.0
        for k in range(1, 60):
            term *= z / (k * (abs_l + k))
            s += term
            if term <= 1e-16 * s:
                break
        return s

    def _integrand_log(u: float) -> float:
        r = R0 + w * u
        if r <= 0.0:
            return 0.0
        arg = 2.0 * (R0 / w) * (r / w)
        exponent = (2 * abs_l + 1) * math.log(r / r_peak) - 2.0 * u * u - 2.0 * arg
        if exponent < -745.0:
            return 0.0
        s_val = _series_0f1(arg)
        return math.exp(exponent) * (s_val * s_val)

    den_l = _u_quad(_integrand_log, u_lo, u_max, extra)
    if den_l <= 0.0:
        return 0.0
    num_l = _u_quad(_integrand_log, u_lo, u_ir, extra)
    return float(min(1.0, max(0.0, num_l / den_l)))


def lg0l_iris_transmission(R_iris: float, w0: float, l: int) -> float:
    """Exact closed-form circular-iris power transmission t_l^{LG}(R_iris) = P(|l|+1, 2 R_iris^2 / w0^2)."""
    if R_iris <= 0.0:
        return 0.0
    if not (math.isfinite(w0) and w0 > 0.0) or math.isnan(R_iris):
        return 0.0
    if math.isinf(R_iris):
        return 1.0
    ratio = R_iris / w0
    if ratio >= 1.0e150:
        return 1.0
    return float(gammainc(abs(l) + 1, 2.0 * (ratio * ratio)))
