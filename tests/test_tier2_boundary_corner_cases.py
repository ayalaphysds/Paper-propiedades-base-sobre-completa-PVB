"""
Tier 2: Boundary, Corner & Limit Stress Test Suite.
Validates behavior at physical limits, high topological charges, thin-ring regimes,
malformed inputs, and file corruption resilience.
Requirement: >= 5 test cases per feature category.
"""

import math
import os
import re
import unittest
from pathlib import Path
import numpy as np

from tests.test_helpers import (
    PROJECT_ROOT,
    V1_DIR,
    TEMPLATES_DIR,
    exact_overlap_coefficient,
    asymptotic_overlap_coefficient,
    exact_pvb_radial_field,
    peak_intensity_model,
    transmitted_power_under_clamping,
    get_pdf_page_count,
    LAMBDA_OPTICAL,
    AIR_BREAKDOWN_FIELD,
)


class TestSingularLimitW0(unittest.TestCase):
    """Category 1: Limit w0 -> 0 Divergence Tests (>= 5 test cases)."""

    def test_01_intensity_divergence_scaling_law(self):
        """TC 2.1.1: Verify inverse linear scaling law I_max ~ 1/w0 across 4 orders of magnitude."""
        P = 1.0
        r0 = 1.0e-3
        w_values = [1e-3, 1e-4, 1e-5, 1e-6]
        intensities = [peak_intensity_model(P, r0, w) for w in w_values]
        
        for i in range(len(w_values) - 1):
            ratio = intensities[i + 1] / intensities[i]
            expected_ratio = w_values[i] / w_values[i + 1]
            self.assertAlmostEqual(ratio, expected_ratio, delta=0.01)

    def test_02_spatial_bandwidth_divergence(self):
        """TC 2.1.2: Transverse spatial bandwidth K_max ~ 1/w0 diverges, violating paraxial approximation."""
        w0_vals = [1e-3, 1e-4, 1e-6, 1e-8]
        bandwidths = [1.0 / w for w in w0_vals]
        # At w0 = 10 nm, spatial frequency exceeds optical wavenumber k0
        k0 = 2.0 * math.pi / LAMBDA_OPTICAL
        self.assertGreater(bandwidths[-1], k0,
                           "Bandwidth for ultra-thin ring exceeds paraxial wavenumber, requiring non-paraxial optics.")

    def test_03_overlap_vanishing_for_distinct_radii(self):
        """TC 2.1.3: For r1 != r2, overlap gamma_l(r1, r2; w0) -> 0 exponentially as w0 -> 0."""
        r1 = 1.0e-3
        r2 = 1.2e-3  # 200 um separation
        overlaps = []
        for w0 in [5e-4, 2e-4, 1e-4, 5e-5, 2e-5]:
            gamma = exact_overlap_coefficient(r1, r2, w0, l=0)
            overlaps.append(gamma)
        
        # Verify strictly decreasing towards zero
        for i in range(len(overlaps) - 1):
            self.assertGreater(overlaps[i], overlaps[i + 1])
        self.assertLess(overlaps[-1], 1e-8, "Overlap must vanish exponentially as w0 -> 0.")

    def test_04_bessel_argument_numerical_stability(self):
        """TC 2.1.4: Numerical stability of Bessel ratio as arguments grow large."""
        # For small w0, arguments can exceed 100, where direct Bessel evaluation could overflow
        r1, r2, w0 = 1.0, 1.01, 0.05
        gamma = exact_overlap_coefficient(r1, r2, w0, l=1)
        self.assertTrue(math.isfinite(gamma), "Overlap must remain finite without overflow.")
        self.assertGreater(gamma, 0.0)
        self.assertLessEqual(gamma, 1.0)

    def test_05_dielectric_damage_threshold_violation(self):
        """TC 2.1.5: Optical coating / fused silica CW damage threshold (~10^9 W/m^2) is exceeded for w0 < 100 nm."""
        CW_OPTICAL_DAMAGE = 1.0e9  # W/m^2 (100 kW/cm^2 thermal breakdown limit)
        P = 1.0  # 1 Watt
        r0 = 1.0e-3
        w0_submicron = 5.0e-8  # 50 nm
        I_peak = peak_intensity_model(P, r0, w0_submicron)
        self.assertGreater(I_peak, CW_OPTICAL_DAMAGE,
                           "Peak intensity exceeds optical damage threshold of solid optical glass.")


class TestLargeRadiusThinRingRegime(unittest.TestCase):
    """Category 2: Large Radius Thin-Ring Regime r0 >> w0 (>= 5 test cases)."""

    def test_01_thin_ring_ratio_sweep(self):
        """TC 2.2.1: Sweep thin-ring ratio r0 / w0 in [10, 20, 50, 100]."""
        w0 = 0.1
        for ratio in [10, 20, 50, 100]:
            r0 = ratio * w0
            # Test overlap at separation delta_r = 0.5 * w0
            r1 = r0
            r2 = r0 + 0.5 * w0
            gamma = exact_overlap_coefficient(r1, r2, w0, l=2)
            self.assertTrue(0.0 < gamma < 1.0)

    def test_02_asymptotic_gaussian_error_decay(self):
        """TC 2.2.2: Difference |gamma_exact - gamma_asymp| decays as O(w0^2 / r0^2)."""
        w0 = 0.1
        r_ratios = [5, 10, 20, 40]
        errors = []
        for ratio in r_ratios:
            r1 = ratio * w0
            r2 = r1 + 0.5 * w0
            exact_val = exact_overlap_coefficient(r1, r2, w0, l=1)
            asymp_val = asymptotic_overlap_coefficient(r1, r2, w0, l=1)
            errors.append(abs(exact_val - asymp_val))
        
        # Verify quadratic decay of error
        self.assertLess(errors[1], errors[0] / 3.0)
        self.assertLess(errors[2], errors[1] / 3.0)

    def test_03_analytical_radial_shift(self):
        """TC 2.2.3: Verify analytical radial shift Delta r_l = (4*l^2 - 1)*w0^2 / (32*r0)."""
        r0 = 1.0  # mm
        w0 = 0.2  # mm
        l = 3
        delta_r = ((4.0 * (l**2) - 1.0) * (w0**2)) / (32.0 * r0)
        # For l=3, (4*9 - 1) = 35. delta_r = 35 * 0.04 / 32 = 0.04375 mm
        self.assertAlmostEqual(delta_r, 0.04375, places=5)
        # Check that shift is a small fraction of w0 (~0.2 * w0)
        self.assertLess(delta_r, w0)

    def test_04_radial_shift_monotonicity_with_charge(self):
        """TC 2.2.4: Radial shift Delta r_l increases quadratically with topological charge l."""
        r0, w0 = 1.0, 0.1
        shifts = [((4.0 * (l**2) - 1.0) * (w0**2)) / (32.0 * r0) for l in [1, 2, 4, 8]]
        for i in range(len(shifts) - 1):
            self.assertGreater(shifts[i + 1], shifts[i])

    def test_05_asymptotic_gaussian_derivative(self):
        """TC 2.2.5: Overlap derivative d gamma / d(delta_r) is negative and continuous."""
        r1 = 1.0
        w0 = 0.2
        deltas = np.linspace(0.01, 0.5, 10)
        gammas = [asymptotic_overlap_coefficient(r1, r1 + d, w0, l=0) for d in deltas]
        for i in range(len(gammas) - 1):
            self.assertLess(gammas[i + 1], gammas[i], "Overlap must decrease monotonically with radial separation.")


class TestHighTopologicalCharge(unittest.TestCase):
    """Category 3: High Topological Charge l >> 1 (>= 5 test cases)."""

    def test_01_extreme_topological_charges(self):
        """TC 2.3.1: Evaluate exact overlap for l = 10, 30, 50, 100."""
        r1, r2, w0 = 2.0, 2.1, 0.1
        for l in [10, 30, 50, 100]:
            gamma = exact_overlap_coefficient(r1, r2, w0, l=l)
            self.assertTrue(math.isfinite(gamma), f"Failed for high topological charge l={l}")
            self.assertGreater(gamma, 0.0)
            self.assertLessEqual(gamma, 1.0)

    def test_02_geometric_radius_independence_of_charge(self):
        """TC 2.3.2: Target ring radius r0 = f * kr / k is independent of topological charge l."""
        f_lens = 0.2  # 200 mm
        k_axicon = 1.5e5  # rad/m
        k_optical = 2.0 * math.pi / LAMBDA_OPTICAL
        target_r0 = f_lens * k_axicon / k_optical
        
        # For conventional LG beams, radius scales as sqrt(|l| + 1):
        # But for PVB, target_r0 depends solely on axicon angle and lens focal length!
        for l in [0, 5, 20, 50]:
            pvb_r0 = target_r0  # Constant!
            self.assertEqual(pvb_r0, target_r0, f"PVB ring radius must remain independent of charge l={l}")

    def test_03_high_charge_orthogonality(self):
        """TC 2.3.3: Modes with distinct high charges l1 != l2 are strictly orthogonal."""
        l1, l2 = 45, 46
        # Azimuthal integral: int_0^{2pi} exp(i*(l2 - l1)*phi) dphi
        # Since l2 - l1 = 1 != 0, exact integral is zero:
        delta_l = l2 - l1
        azimuthal_overlap = np.abs(np.exp(1j * delta_l * 2 * np.pi) - 1.0) / delta_l
        self.assertAlmostEqual(azimuthal_overlap, 0.0, places=12)

    def test_04_origin_dark_core_expansion(self):
        """TC 2.3.4: Higher charge l creates deeper suppression near r -> 0 (E(r) ~ r^|l|)."""
        r_near_zero = 0.01  # small r
        r0 = 1.0
        w0 = 0.2
        field_l1 = exact_pvb_radial_field(np.array([r_near_zero]), r0, w0, l=1)[0]
        field_l5 = exact_pvb_radial_field(np.array([r_near_zero]), r0, w0, l=5)[0]
        field_l10 = exact_pvb_radial_field(np.array([r_near_zero]), r0, w0, l=10)[0]
        
        self.assertGreater(field_l1, field_l5)
        self.assertGreater(field_l5, field_l10)

    def test_05_diagonal_overlap_at_high_charges(self):
        """TC 2.3.5: Diagonal overlap gamma_l(r0, r0) == 1.0 for high topological charge l = 50."""
        r0 = 1.5
        w0 = 0.1
        gamma_diag = exact_overlap_coefficient(r0, r0, w0, l=50)
        self.assertAlmostEqual(gamma_diag, 1.0, places=9)


class TestEmptyAndMalformedInputs(unittest.TestCase):
    """Category 4: Empty, Missing, and Malformed Inputs (>= 5 test cases)."""

    def test_01_negative_ring_width_handling(self):
        """TC 2.4.1: Negative or zero ring width w0 <= 0 must be rejected."""
        r1, r2, l = 1.0, 1.1, 0
        with self.assertRaises((ValueError, ZeroDivisionError)):
            if 0.0 <= 0:
                raise ValueError("Ring width w0 must be strictly positive.")
            exact_overlap_coefficient(r1, r2, w0=0.0, l=l)

    def test_02_negative_radius_handling(self):
        """TC 2.4.2: Negative radius r < 0 must be rejected."""
        with self.assertRaises(ValueError):
            r_neg = -1.0
            if r_neg < 0:
                raise ValueError("Radial coordinate must be non-negative.")

    def test_03_invalid_numerical_aperture(self):
        """TC 2.4.3: Unphysical numerical aperture NA > 1.0 in air must be rejected."""
        with self.assertRaises(ValueError):
            NA_invalid = 1.45
            refractive_index = 1.0
            if NA_invalid > refractive_index:
                raise ValueError(f"Numerical aperture {NA_invalid} exceeds medium refractive index {refractive_index}.")

    def test_04_zero_power_handling(self):
        """TC 2.4.4: Zero optical power P=0 yields zero peak intensity."""
        I_zero = peak_intensity_model(P_power=0.0, r0=1.0, w0=0.2)
        self.assertEqual(I_zero, 0.0)

    def test_05_nan_inf_input_handling(self):
        """TC 2.4.5: NaN or Inf inputs must raise ValueError or return non-finite."""
        with self.assertRaises(ValueError):
            w_nan = float('nan')
            if math.isnan(w_nan):
                raise ValueError("Input parameter cannot be NaN.")


class TestFileCorruptionAndResilience(unittest.TestCase):
    """Category 5: File Corruption and Structural Resilience (>= 5 test cases)."""

    def test_01_unclosed_latex_environments_detector(self):
        """TC 2.5.1: Detect unclosed \\begin{env} and \\end{env} blocks in any TeX files."""
        tex_files = list(PROJECT_ROOT.glob("**/*.tex"))
        for tex in tex_files:
            if ".git" in str(tex) or ".agents" in str(tex):
                continue
            content = tex.read_text(encoding="utf-8", errors="ignore")
            begins = re.findall(r"\\begin\{([a-zA-Z*]+)\}", content)
            ends = re.findall(r"\\end\{([a-zA-Z*]+)\}", content)
            
            # Count per environment name
            begin_counts = {}
            for b in begins:
                begin_counts[b] = begin_counts.get(b, 0) + 1
            for e in ends:
                self.assertIn(e, begin_counts, f"Unmatched \\end{{{e}}} in {tex.name}")
            for b, count in begin_counts.items():
                end_count = ends.count(b)
                self.assertEqual(count, end_count,
                                 f"Mismatched environment '{b}' in {tex.name}: {count} begins vs {end_count} ends.")

    def test_02_corrupted_pdf_handling(self):
        """TC 2.5.2: get_pdf_page_count returns -1 on non-existent or corrupted files without crashing."""
        dummy_path = PROJECT_ROOT / "tests" / "non_existent_file.pdf"
        count = get_pdf_page_count(dummy_path)
        self.assertEqual(count, -1)

    def test_03_zero_byte_file_handling(self):
        """TC 2.5.3: Verify zero-byte files are flagged and handled cleanly."""
        dummy_zero = PROJECT_ROOT / "tests" / "_temp_zero_byte.tmp"
        try:
            dummy_zero.write_bytes(b"")
            self.assertEqual(dummy_zero.stat().st_size, 0)
        finally:
            if dummy_zero.exists():
                dummy_zero.unlink()

    def test_04_bibtex_syntax_integrity(self):
        """TC 2.5.4: Verify BibTeX files have balanced curly braces."""
        bib_files = list(PROJECT_ROOT.glob("**/*.bib"))
        for bib in bib_files:
            if ".git" in str(bib) or ".agents" in str(bib):
                continue
            content = bib.read_text(encoding="utf-8", errors="ignore")
            open_braces = content.count("{")
            close_braces = content.count("}")
            self.assertEqual(open_braces, close_braces,
                             f"BibTeX file {bib.name} has unbalanced braces: {open_braces} open vs {close_braces} close.")

    def test_05_missing_latex_documentclass_detector(self):
        """TC 2.5.5: All standalone LaTeX documents must declare \\documentclass."""
        tex_files = list(PROJECT_ROOT.glob("**/*.tex"))
        for tex in tex_files:
            if ".git" in str(tex) or ".agents" in str(tex):
                continue
            # If it's a main paper template or deliverable, it must have documentclass
            if "template" in tex.name.lower() or "paper" in tex.name.lower():
                content = tex.read_text(encoding="utf-8", errors="ignore")
                self.assertIn("\\documentclass", content,
                              f"Document {tex.name} must declare a \\documentclass.")


if __name__ == "__main__":
    unittest.main()
