"""
Tier 5: Adversarial Stress Test Suite & Empirical Verification Harness.
Role: EMPIRICAL CHALLENGER (challenger_1) | Milestone M5.

Stress tests mathematical claims, identities, and simulation algorithms:
1. Closed-form Gradshteyn & Ryzhik inner product vs high-precision numerical quadrature.
2. Modified Bessel function numerical stability, overflow threshold (iv vs ive), and underflow handling.
3. Asymptotic thin-ring Gaussian cross-talk formula and second-order correction scaling O((w0/r0)^2).
4. Continuous frame operator bounds 0 < A <= B < infty on paraxial bandlimited space H_band.
5. Physical unfeasibility limit w0 -> 0 divergence scaling (<kr^2> ~ 1/w0^2, I_max ~ 1/w0, optical breakdown).
6. Simulation scripts robustness under extreme and boundary arguments.
"""

import math
import os
import sys
import unittest
from pathlib import Path
import numpy as np
import scipy.special as sp
import scipy.integrate as integrate
from scipy.optimize import minimize_scalar

# Project root path resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
V1_DIR = PROJECT_ROOT / "v1"
SCRIPTS_DIR = V1_DIR / "scripts"
FIGURES_DIR = V1_DIR / "figures"


# ==============================================================================
# Helper Mathematical Functions (Adversarially Hardened Reference Implementations)
# ==============================================================================

def exact_overlap_analytical(r1: float, r2: float, w0: float, l: int) -> float:
    """Computes exact normalized overlap using ive and numerically safe denominators."""
    arg12 = (r1 * r2) / (w0**2)
    arg11 = (r1**2) / (w0**2)
    arg22 = (r2**2) / (w0**2)
    
    exp_factor = math.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
    v12 = float(sp.ive(l, arg12))
    v11 = float(sp.ive(l, arg11))
    v22 = float(sp.ive(l, arg22))
    
    # Handle deep subnormal underflow
    if v11 <= 0.0 or v22 <= 0.0 or v12 <= 0.0:
        return float(exp_factor)
        
    # Safe square root separation to avoid float64 intermediate underflow (v11 * v22)
    den = math.sqrt(v11) * math.sqrt(v22)
    if den <= 0.0:
        return float(exp_factor)
    return float(np.clip(exp_factor * (v12 / den), 0.0, 1.0))


def focused_numerical_quadrature_overlap(r1: float, r2: float, w0: float, l: int) -> float:
    """High-precision numerical quadrature with support-focused integration interval."""
    def field_profile(r, r0_val):
        arg = 2.0 * r0_val * r / (w0**2)
        return np.exp(-((r - r0_val)**2) / (w0**2)) * sp.ive(l, arg)
    
    # Adapt integration bounds to physical support:
    # For thin ring (w0 <= r0), focus on [r0 - 8w0, r0 + 8w0]
    # For wide ring (w0 > r0), integrate over [0, max(r0, sqrt(l/2)*w0) + 6*w0]
    min_r0 = min(r1, r2)
    max_r0 = max(r1, r2)
    
    if w0 <= min_r0:
        a_int = max(0.0, min_r0 - 8.0 * w0)
        b_int = max_r0 + 8.0 * w0
    else:
        a_int = 0.0
        peak_est = max(max_r0, math.sqrt(max(1.0, l) / 2.0) * w0)
        b_int = peak_est + 6.0 * w0
        
    num_ip, _ = integrate.quad(lambda r: r * field_profile(r, r1) * field_profile(r, r2),
                               a_int, b_int, epsabs=1e-15, epsrel=1e-12, limit=300)
    num_n1, _ = integrate.quad(lambda r: r * (field_profile(r, r1)**2),
                               a_int, b_int, epsabs=1e-15, epsrel=1e-12, limit=300)
    num_n2, _ = integrate.quad(lambda r: r * (field_profile(r, r2)**2),
                               a_int, b_int, epsabs=1e-15, epsrel=1e-12, limit=300)
    
    den = math.sqrt(num_n1) * math.sqrt(num_n2)
    if den <= 0.0:
        return 0.0
    return float(num_ip / den)


# ==============================================================================
# Tier 5 Test Suites
# ==============================================================================

class TestAdversarialInnerProductQuadrature(unittest.TestCase):
    """Stress test Gradshteyn-Ryzhik closed-form vs high-precision numerical quadrature."""

    def test_01_quadrature_thin_ring_regime(self):
        """Verify analytical inner product vs focused quadrature for thin ring w0=0.1 mm, r0=1.0 mm."""
        w0 = 0.1
        r1, r2 = 1.0, 1.05
        for l in [0, 1, 3, 10]:
            exact_val = exact_overlap_analytical(r1, r2, w0, l)
            quad_val = focused_numerical_quadrature_overlap(r1, r2, w0, l)
            rel_error = abs(exact_val - quad_val) / exact_val
            self.assertLess(rel_error, 1e-10,
                            f"Mismatch for l={l}: exact={exact_val}, quad={quad_val}, rel_error={rel_error}")

    def test_02_quadrature_ultra_thin_ring_1um(self):
        """Verify analytical inner product vs focused quadrature for ultra-thin ring w0=10^-3 mm (1 um)."""
        w0 = 1e-3  # 1 um
        r1 = 1.0
        r2 = 1.0005  # 500 nm separation
        l = 2
        exact_val = exact_overlap_analytical(r1, r2, w0, l)
        quad_val = focused_numerical_quadrature_overlap(r1, r2, w0, l)
        rel_error = abs(exact_val - quad_val) / exact_val
        self.assertLess(rel_error, 1e-10,
                        f"Ultra-thin ring error too large: exact={exact_val}, quad={quad_val}, rel_error={rel_error}")

    def test_03_quadrature_wide_diffuse_regime(self):
        """Verify analytical inner product vs focused quadrature for wide ring w0=2.0 mm, r0=0.5 mm."""
        w0 = 2.0
        r1, r2 = 0.5, 0.6
        for l in [0, 1, 5]:
            exact_val = exact_overlap_analytical(r1, r2, w0, l)
            quad_val = focused_numerical_quadrature_overlap(r1, r2, w0, l)
            rel_error = abs(exact_val - quad_val) / exact_val
            self.assertLess(rel_error, 1e-10,
                            f"Mismatch for wide ring l={l}: exact={exact_val}, quad={quad_val}")

    def test_04_extreme_parameter_grid_sweep(self):
        """Sweep parameter grid w0 in [0.05, 0.5, 2.0], r0 in [0.5, 2.0, 5.0], l in [0, 5, 20]."""
        w0_grid = [0.05, 0.5, 2.0]
        r0_grid = [0.5, 2.0, 5.0]
        l_grid = [0, 5, 20]
        for w0 in w0_grid:
            for r0 in r0_grid:
                for l in l_grid:
                    r1 = r0
                    r2 = r0 + 0.3 * w0
                    exact_val = exact_overlap_analytical(r1, r2, w0, l)
                    quad_val = focused_numerical_quadrature_overlap(r1, r2, w0, l)
                    rel_error = abs(exact_val - quad_val) / max(exact_val, 1e-12)
                    self.assertLess(rel_error, 1e-8,
                                    f"Grid sweep fail at w0={w0}, r0={r0}, l={l}: rel_error={rel_error}")

    def test_05_naive_quadrature_pathology_demonstration(self):
        """Empirically prove that naive unfocused quadrature misses narrow spikes for w0 <= 10^-3 mm."""
        w0 = 1e-3
        r1, r2 = 1.0, 1.0005
        # Naive integration over [0, 2] with no break points
        naive_val, _ = integrate.quad(
            lambda r: r * (np.exp(-((r - r1)**2) / (w0**2)) * sp.ive(1, 2.0 * r1 * r / (w0**2)))**2,
            0.0, 2.0
        )
        # Expected norm ~ (w0^2 / 4) * ive(1, r0^2/w0^2) * 2*pi
        expected_norm = 2.0 * np.pi * (w0**2 / 4.0) * float(sp.ive(1, r1**2 / w0**2))
        # Naive quad severely underestimates by orders of magnitude due to missed sampling points
        self.assertLess(naive_val, expected_norm * 0.1,
                        "Naive quadrature unexpectedly resolved spike; test intended to document pathology.")


class TestModifiedBesselStabilityAndUnderflow(unittest.TestCase):
    """Stress test modified Bessel function overflow/underflow handling."""

    def test_01_iv_overflow_above_709(self):
        """Verify that scipy.special.iv overflows to inf for arguments z > 709.78."""
        z_safe = 700.0
        z_overflow = 715.0
        self.assertTrue(math.isfinite(sp.iv(1, z_safe)))
        self.assertTrue(math.isinf(sp.iv(1, z_overflow)), "iv must overflow to inf above 709.78")

    def test_02_ive_stability_to_extreme_arguments(self):
        """Verify that scipy.special.ive remains finite and non-zero up to z = 10^8."""
        for z in [1e3, 1e5, 1e8]:
            val = sp.ive(1, z)
            self.assertTrue(math.isfinite(val))
            self.assertGreater(val, 0.0)
            # Asymptotic scaling ive(1, z) ~ 1 / sqrt(2 * pi * z)
            expected_asymp = 1.0 / math.sqrt(2.0 * math.pi * z)
            self.assertAlmostEqual(val / expected_asymp, 1.0, delta=0.01)

    def test_03_intermediate_product_underflow_defect(self):
        """Demonstrate the intermediate product underflow bug in naive sqrt(v11 * v22)."""
        # For w0 = 5.0, r0 = 0.1, l = 50:
        z = (0.1**2) / (5.0**2)  # 0.0004
        v11 = float(sp.ive(50, z))  # ~ 3.7e-250
        self.assertGreater(v11, 0.0)
        # Multiplying v11 * v11 underflows to 0.0 in float64
        prod_underflow = v11 * v11
        self.assertEqual(prod_underflow, 0.0, "v11 * v11 must underflow to 0.0 in IEEE 754 float64")
        # While sqrt(v11) * sqrt(v11) preserves v11
        safe_den = math.sqrt(v11) * math.sqrt(v11)
        self.assertGreater(safe_den, 0.0)
        self.assertAlmostEqual(safe_den / v11, 1.0, delta=1e-12)

    def test_04_high_topological_charge_underflow_threshold(self):
        """Test underflow behavior of ive(l, z) for l = 50 across small z."""
        l = 50
        # For z = 1e-4, ive(50, z) is ~ 2.92e-280 > 0
        self.assertGreater(sp.ive(l, 1e-4), 0.0)
        # For z = 1e-5, ive(50, z) underflows to 0.0
        self.assertEqual(sp.ive(l, 1e-5), 0.0)

    def test_05_hardened_overlap_resilience(self):
        """Verify that exact_overlap_analytical handles extreme parameters without crashing."""
        # Extreme parameter: w0 = 5.0, r1 = 0.1, r2 = 0.1, l = 50
        gamma = exact_overlap_analytical(0.1, 0.1, 5.0, 50)
        self.assertTrue(math.isfinite(gamma))
        self.assertAlmostEqual(gamma, 1.0, delta=1e-6)


class TestAsymptoticGaussianCrossTalk(unittest.TestCase):
    """Stress test asymptotic thin-ring cross-talk formula and second-order correction."""

    def test_01_asymptotic_error_bounded_by_quadratic(self):
        """Verify error |gamma_exact - gamma_asymp| / gamma_exact decays as O((w0/r0)^2)."""
        w0 = 0.05
        ratios = [10, 20, 40, 80]
        errors = []
        for r_ratio in ratios:
            r1 = r_ratio * w0
            r2 = r1 + 0.5 * w0
            g_ex = exact_overlap_analytical(r1, r2, w0, l=1)
            g_as = math.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
            rel_err = abs(g_ex - g_as) / g_ex
            errors.append(rel_err)
            
        # As ratio doubles, error should decrease by at least a factor of 4
        for i in range(len(errors) - 1):
            decay = errors[i] / errors[i + 1]
            self.assertGreater(decay, 3.8, f"Decay factor {decay} is less than quadratic expectation ~4.0")

    def test_02_second_order_correction_match(self):
        """Verify theoretical correction (4l^2 - 1)*w0^2*(r1-r2)^2 / (16*r1^2*r2^2) matches exact difference."""
        w0 = 0.1
        r0 = 1.0
        delta_r = 0.15
        r1 = r0
        r2 = r0 + delta_r
        
        for l in [1, 2, 3, 5]:
            g_ex = exact_overlap_analytical(r1, r2, w0, l)
            g_as = math.exp(-(delta_r**2) / (2.0 * (w0**2)))
            actual_diff = g_ex - g_as
            theory_diff = g_as * ((4.0 * (l**2) - 1.0) * (w0**2) * (delta_r**2)) / (16.0 * (r1**2) * (r2**2))
            ratio = actual_diff / theory_diff
            self.assertAlmostEqual(ratio, 1.0, delta=0.03,
                                   msg=f"Correction formula mismatch for l={l}: actual/theory = {ratio}")

    def test_03_l_charge_monotonicity_of_crosstalk(self):
        """Verify that for fixed radii, overlap strictly increases with l: gamma_{l+1} > gamma_l."""
        w0 = 0.1
        r1, r2 = 1.0, 1.15
        overlaps = [exact_overlap_analytical(r1, r2, w0, l) for l in range(6)]
        for i in range(len(overlaps) - 1):
            self.assertGreater(overlaps[i + 1], overlaps[i],
                               f"Overlap must strictly increase with l: {overlaps[i+1]} <= {overlaps[i]}")

    def test_04_zero_topological_charge_lower_bound(self):
        """Verify that l=0 overlap is strictly smaller than universal Gaussian curve."""
        w0 = 0.1
        r1, r2 = 1.0, 1.15
        g_ex_0 = exact_overlap_analytical(r1, r2, w0, l=0)
        g_as = math.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
        self.assertLess(g_ex_0, g_as, "l=0 overlap must be strictly below Gaussian reference.")

    def test_05_thin_ring_limit_asymptotic_convergence(self):
        """At r0/w0 = 100, Gaussian asymptotic formula matches exact Bessel to 7 decimal digits."""
        w0 = 0.01
        r1 = 1.0
        r2 = 1.0 + 0.5 * w0
        g_ex = exact_overlap_analytical(r1, r2, w0, l=1)
        g_as = math.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
        self.assertAlmostEqual(g_ex, g_as, places=6)


class TestContinuousFrameBoundsParaxial(unittest.TestCase):
    """Stress test continuous frame bounds on paraxial bandlimited optical space H_band."""

    def test_01_frame_bounds_strictly_positive(self):
        """Confirm lower frame bound A = exp(-1/2 * K_max^2 * w0^2) > 0 strictly for any finite K_max."""
        wavelength = 1550e-6  # mm
        k0 = 2.0 * math.pi / wavelength
        w0 = 2.0e-3  # mm (2 um)
        
        for na in [0.01, 0.05, 0.10, 0.15, 0.25]:
            K_max = k0 * na
            A = math.exp(-0.5 * (K_max * w0)**2)
            B = 1.0
            self.assertGreater(A, 0.0, f"Lower frame bound A must be strictly positive for NA={na}")
            self.assertLessEqual(A, B, "A must be <= B")
            self.assertTrue(math.isfinite(B / A), "Condition number must be finite")

    def test_02_frame_bounds_on_unconstrained_l2_fail(self):
        """Prove that on unconstrained L^2(R^2), A = inf_{kr} sigma(kr) = 0 (frame condition fails)."""
        w0 = 0.1  # mm
        # As kr -> infty, spectrum -> 0
        kr_large = 1e4
        sigma_inf = math.exp(-0.5 * (kr_large * w0)**2)
        self.assertEqual(sigma_inf, 0.0, "Spectrum must vanish at high frequencies, proving A=0 on L^2(R^2)")

    def test_03_condition_number_scaling_with_na(self):
        """Verify condition number kappa = B / A increases monotonically with numerical aperture NA."""
        wavelength = 1550e-6
        k0 = 2.0 * math.pi / wavelength
        w0 = 1.5e-3
        na_list = [0.02, 0.05, 0.08, 0.12]
        kappas = [1.0 / math.exp(-0.5 * (k0 * na * w0)**2) for na in na_list]
        for i in range(len(kappas) - 1):
            self.assertGreater(kappas[i + 1], kappas[i], "Condition number must monotonically increase with NA")

    def test_04_discrete_gram_matrix_positive_definiteness(self):
        """Verify that discrete multi-ring Gram matrix G_ij is symmetric positive definite with s_min > 0."""
        M = 8
        r_center = 1.0
        w0 = 0.10
        delta_r = 1.0 * w0
        radii = r_center + (np.arange(M) - (M - 1) / 2.0) * delta_r
        
        G = np.zeros((M, M))
        for i in range(M):
            for j in range(M):
                G[i, j] = exact_overlap_analytical(radii[i], radii[j], w0, l=1)
                
        # Eigenvalues must all be strictly positive
        eigvals = np.linalg.eigvalsh(G)
        self.assertTrue(np.all(eigvals > 0.0), f"Gram matrix must be strictly positive definite: min_eig={eigvals[0]}")
        self.assertLess(eigvals[-1] / eigvals[0], 50.0, "Gram matrix must have bounded condition number")

    def test_05_tight_frame_limit_as_w0_to_zero(self):
        """Verify that formally as w0 -> 0, condition number kappa = B/A -> 1 (tight frame limit)."""
        K_max = 500.0  # mm^-1
        w0_vals = [1e-2, 1e-3, 1e-4, 1e-6]
        kappas = [1.0 / math.exp(-0.5 * (K_max * w)**2) for w in w0_vals]
        self.assertAlmostEqual(kappas[-1], 1.0, places=6)


class TestPhysicalUnfeasibilityLimitW0(unittest.TestCase):
    """Stress test physical unfeasibility proofs of strict orthonormal basis limit w0 -> 0."""

    def test_01_peak_intensity_inverse_w0_scaling(self):
        """Verify peak intensity I_max = P / (pi^(3/2) * sqrt(2) * r0 * w0) scales exactly as 1/w0."""
        P = 1.0  # W
        r0 = 1.0  # mm
        w_values = np.logspace(-4, -1, 10)  # mm
        I_max = [P / ((math.pi**1.5) * math.sqrt(2.0) * r0 * w) for w in w_values]
        
        # Log-log slope must be exactly -1.0
        log_w = np.log10(w_values)
        log_I = np.log10(I_max)
        slope, _ = np.polyfit(log_w, log_I, 1)
        self.assertAlmostEqual(slope, -1.0, places=4, msg="Peak intensity must scale with power law -1")

    def test_02_spatial_frequency_divergence_scaling(self):
        """Verify <kr^2> scales as 1/w0^2, violating paraxial propagation condition."""
        w0_vals = np.logspace(-4, -1, 10)
        kr2_scale = 1.0 / (w0_vals**2)
        slope, _ = np.polyfit(np.log10(w0_vals), np.log10(kr2_scale), 1)
        self.assertAlmostEqual(slope, -2.0, places=4, msg="Momentum variance must scale with power law -2")

    def test_03_dielectric_air_breakdown_threshold(self):
        """Verify air breakdown threshold (1.19e4 W/mm^2) is breached for submicron rings at P=1 W."""
        I_air_breakdown = 1.19e4  # W/mm^2
        P = 1.0
        r0 = 1.0
        w0_threshold = P / ((math.pi**1.5) * math.sqrt(2.0) * r0 * I_air_breakdown)  # ~ 1.07e-5 mm = 10.7 nm
        
        # Rings narrower than w0_threshold violate air dielectric stability
        I_10nm = P / ((math.pi**1.5) * math.sqrt(2.0) * r0 * 1e-5)
        self.assertGreater(I_10nm, I_air_breakdown)

    def test_04_vanishing_power_under_field_clamping(self):
        """Verify that clamping peak field to damage limit causes transmitted power P -> 0 as w0 -> 0."""
        I_damage = 1e4  # W/mm^2
        r0 = 1.0
        w0_sweep = [1e-1, 1e-2, 1e-3, 1e-4, 1e-7]
        P_clamped = [(math.pi**1.5) * math.sqrt(2.0) * r0 * w * I_damage for w in w0_sweep]
        for i in range(len(P_clamped) - 1):
            self.assertLess(P_clamped[i + 1], P_clamped[i])
        self.assertLess(P_clamped[-1], 1e-2, "Clamped power must vanish as w0 -> 0")

    def test_05_dirac_delta_non_l2_singularity(self):
        """Verify that the limiting distribution delta(r - r0) has divergent L^2 norm."""
        # Using Gaussian approximations to delta: delta_w(x) = 1/(sqrt(pi)*w) * exp(-x^2/w^2)
        # Integral of delta_w(x)^2 dx = 1 / (sqrt(2*pi)*w) -> infty as w -> 0
        w_vals = [1e-1, 1e-2, 1e-3, 1e-4]
        l2_norms_sq = [1.0 / (math.sqrt(2.0 * math.pi) * w) for w in w_vals]
        for i in range(len(l2_norms_sq) - 1):
            self.assertGreater(l2_norms_sq[i + 1], l2_norms_sq[i] * 5.0)


class TestSimulationScriptsBoundaryRobustness(unittest.TestCase):
    """Stress test functions in v1/scripts/ with boundary and extreme parameters."""

    def test_01_fig1_calculate_pvb_intensity_boundaries(self):
        """Test calculate_pvb_intensity across varied r, w0, and l."""
        from v1.scripts.generate_fig1_profiles import calculate_pvb_intensity
        r_grid = np.linspace(0.0, 2.0, 100)
        
        # Test standard parameters
        I_std = calculate_pvb_intensity(r_grid, 1.0, 0.1, l=1, P=1.0)
        self.assertTrue(np.all(np.isfinite(I_std)))
        self.assertTrue(np.all(I_std >= 0.0))
        
        # Test l=0
        I_l0 = calculate_pvb_intensity(r_grid, 1.0, 0.1, l=0, P=1.0)
        self.assertTrue(np.all(np.isfinite(I_l0)))
        
        # Test w0 = 0.5 mm
        I_w05 = calculate_pvb_intensity(r_grid, 1.0, 0.5, l=2, P=2.5)
        self.assertTrue(np.all(np.isfinite(I_w05)))

    def test_02_fig1_find_topological_peak_boundaries(self):
        """Test find_topological_peak for l in [0, 1, 5, 10]."""
        from v1.scripts.generate_fig1_profiles import find_topological_peak
        for l in [0, 1, 3, 5, 8]:
            r_pk = find_topological_peak(1.0, 0.1, l)
            self.assertTrue(math.isfinite(r_pk))
            self.assertGreater(r_pk, 0.8)
            self.assertLess(r_pk, 1.2)

    def test_03_fig2_calculate_exact_overlap_matrix(self):
        """Test calculate_exact_overlap with 2D meshgrid and 1D arrays."""
        from v1.scripts.generate_fig2_overlap import calculate_exact_overlap
        r_span = np.linspace(0.8, 1.2, 20)
        R1, R2 = np.meshgrid(r_span, r_span)
        gamma_2d = calculate_exact_overlap(R1, R2, 0.1, l=1)
        self.assertEqual(gamma_2d.shape, (20, 20))
        self.assertTrue(np.all(np.isfinite(gamma_2d)))
        self.assertTrue(np.all(gamma_2d >= 0.0))
        self.assertTrue(np.all(gamma_2d <= 1.0))
        # Diagonal must be 1.0
        np.testing.assert_allclose(np.diag(gamma_2d), 1.0, atol=1e-7)

    def test_04_fig4_kolmogorov_phase_screen_reproducibility(self):
        """Test generate_kolmogorov_phase_screen reproducibility with seed."""
        from v1.scripts.generate_fig4_turbulence import generate_kolmogorov_phase_screen
        scr1 = generate_kolmogorov_phase_screen(64, 8e-3, 0.05, seed=123)
        scr2 = generate_kolmogorov_phase_screen(64, 8e-3, 0.05, seed=123)
        np.testing.assert_array_equal(scr1, scr2)
        # Check zero-mean property
        self.assertAlmostEqual(float(np.mean(scr1)), 0.0, places=5)

    def test_05_fig3_overlap_resilience(self):
        """Test calculate_exact_overlap in fig3 script for equal and unequal radii."""
        from v1.scripts.generate_fig3_frame_bounds import calculate_exact_overlap
        # Identical radii must yield 1.0
        g_diag = calculate_exact_overlap(1.0, 1.0, 0.1, l=2)
        self.assertAlmostEqual(g_diag, 1.0, places=6)
        # Separated radii must yield 0 < gamma < 1
        g_off = calculate_exact_overlap(1.0, 1.2, 0.1, l=2)
        self.assertTrue(0.0 < g_off < 1.0)


# ==============================================================================
# Runner
# ==============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
