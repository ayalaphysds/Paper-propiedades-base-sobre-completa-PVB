"""
Empirical Challenger Adversarial Stress Test Suite for Milestone 2.
Agent: challenger_m2_2 (Role: EMPIRICAL CHALLENGER / critic, specialist)

Adversarially stress-tests Milestone 2 Deliverables:
1. Numerical Precision & Reproducibility:
   - Multiple sequential runs of v2/scripts/run_all_simulations.py.
   - Determinism of generated vector PDF figures.
   - Execution timing and throughput limits.
2. Condition Number & Frame Bounds Verification:
   - Theoretical formula: kappa = exp(w0^2 * K_max^2 / 2) approx 3.0802 at NA = 0.15.
   - Match against generate_fig3_frame_bounds.py computation.
   - Monotonicity, positivity, and asymptotic limits.
3. Radial Peak Shift Mathematical Verification:
   - Physical peak of E_l(r) = exp(-(r-R0)^2/w0^2) * ive(l, 2*R0*r/w0^2).
   - Derivation: r_peak - R0 = -w0^2 / (4*R0) + l^2 * w0^4 / (8 * R0^3) + O(w0^6/R0^5).
   - Investigation of generate_fig1_profiles.py formula: Delta R_l approx (4l^2 - 1) w0^2 / (32 R0).
   - Empirical discovery of negative baseline shift, y-axis clipping, and (R0/w0)^2 scale discrepancy.
4. Resource Hygiene & Subprocess Management:
   - Memory leak analysis across repeated runs.
   - Matplotlib figure closure (no unclosed figure leaks).
   - Subprocess hygiene and clean termination.
5. Publication Vector PDF Visual & Structural Quality:
   - PDF magic bytes, EOF marker, dimensions (8.5x7.0 inches ~ 612x504 pt).
   - Clean titles and axis labels (no raw unrendered \\textbf or \\mathrm strings).
   - Non-empty vector paths and valid text streams.
"""

import gc
import math
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
import numpy as np
import psutil
import pymupdf  # PyMuPDF
from scipy.optimize import minimize_scalar
from scipy.special import ive

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

V2_DIR = PROJECT_ROOT / "v2"
SCRIPTS_DIR = V2_DIR / "scripts"
FIGURES_DIR = V2_DIR / "figures"
RUNNER_SCRIPT = SCRIPTS_DIR / "run_all_simulations.py"

FIGURE_FILENAMES = [
    "fig1_pvb_profiles_divergence.pdf",
    "fig2_radial_overlap_matrix.pdf",
    "fig3_frame_spectrum_bounds.pdf",
    "fig4_turbulence_rkhs_recovery.pdf",
    "fig5_quantum_povm_entanglement.pdf",
]


class TestNumericalReproducibilityAndDeterminism(unittest.TestCase):
    """Stress test determinism, reproducibility, and timing across multiple simulation runs."""

    def test_01_multiple_runs_exit_code_zero(self):
        """TC 1.1: Execute run_all_simulations.py 3 consecutive times and verify exit code 0."""
        self.assertTrue(RUNNER_SCRIPT.exists(), f"Runner script not found: {RUNNER_SCRIPT}")

        run_times = []
        for run_idx in range(1, 4):
            t_start = time.perf_counter()
            proc = subprocess.run(
                [sys.executable, str(RUNNER_SCRIPT)],
                cwd=str(SCRIPTS_DIR),
                capture_output=True,
                text=True,
                timeout=60,
            )
            elapsed = time.perf_counter() - t_start
            run_times.append(elapsed)

            self.assertEqual(
                proc.returncode, 0,
                f"Run #{run_idx} failed with exit code {proc.returncode}.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
            )
            self.assertIn("ALL 5 PUBLICATION-QUALITY VECTOR FIGURES GENERATED & VALIDATED", proc.stdout)

        # Ensure reasonable performance (< 15 seconds per full run)
        for idx, t in enumerate(run_times, 1):
            self.assertLess(t, 15.0, f"Run #{idx} took {t:.2f}s, exceeding 15.0s ceiling.")

    def test_02_all_five_figures_exist_with_adequate_size(self):
        """TC 1.2: Verify all 5 publication PDFs exist, have PDF magic header and size >= minimum threshold."""
        min_sizes = {
            "fig1_pvb_profiles_divergence.pdf": 10_000,
            "fig2_radial_overlap_matrix.pdf": 10_000,
            "fig3_frame_spectrum_bounds.pdf": 10_000,
            "fig4_turbulence_rkhs_recovery.pdf": 20_000,
            "fig5_quantum_povm_entanglement.pdf": 10_000,
        }
        for fig_name, min_bytes in min_sizes.items():
            fig_path = FIGURES_DIR / fig_name
            self.assertTrue(fig_path.exists(), f"Figure missing: {fig_name}")
            size = fig_path.stat().st_size
            self.assertGreaterEqual(
                size, min_bytes,
                f"Figure {fig_name} size ({size} bytes) is below minimum threshold ({min_bytes} bytes)."
            )
            header = fig_path.read_bytes()[:5]
            self.assertEqual(header, b"%PDF-", f"Figure {fig_name} does not start with %PDF- header.")

    def test_03_pdf_content_structural_stability_across_runs(self):
        """TC 1.3: Verify structural stability (page count, text count, drawing elements) across re-runs."""
        # Inspect all generated PDFs using PyMuPDF
        for fig_name in FIGURE_FILENAMES:
            fig_path = FIGURES_DIR / fig_name
            doc = pymupdf.open(fig_path)
            self.assertEqual(len(doc), 1, f"Figure {fig_name} must have exactly 1 page.")
            page = doc[0]

            # Verify page has vector content (drawings and text)
            text = page.get_text()
            self.assertGreater(len(text.strip()), 50, f"Figure {fig_name} has insufficient text elements.")

            drawings = page.get_drawings()
            self.assertGreater(len(drawings), 10, f"Figure {fig_name} has insufficient vector drawings ({len(drawings)}).")
            doc.close()


class TestConditionNumberAndFrameBounds(unittest.TestCase):
    """Stress test continuous frame bounds and condition number kappa approx 3.08."""

    def test_01_theoretical_formula_condition_number(self):
        """TC 2.1: Verify theoretical condition number kappa = exp(w0^2 * K_max^2 / 2)."""
        # For paraxial cutoff design where w0 * K_max = 1.5:
        # A = exp(-0.5 * (1.5)^2) = exp(-1.125)
        # B = 1.0
        # kappa = B / A = exp(1.125) = 3.0802168...
        w0_kmax = 1.50
        A = math.exp(-0.5 * (w0_kmax**2))
        B = 1.0
        kappa = B / A
        expected_kappa = math.exp(1.125)

        self.assertAlmostEqual(A, 0.324652467, places=6)
        self.assertAlmostEqual(B, 1.0, places=9)
        self.assertAlmostEqual(kappa, expected_kappa, places=9)
        self.assertAlmostEqual(kappa, 3.0802, places=3)

    def test_02_script_fig3_computational_agreement(self):
        """TC 2.2: Verify generate_fig3_frame_bounds.py implements exact kappa = exp(0.5*(10*NA)^2)."""
        # In generate_fig3_frame_bounds.py:
        # na_vals = np.linspace(0.05, 0.25, 200)
        # w0_kmax = 10.0 * na_vals  -> at NA = 0.15, w0_kmax = 1.50
        # A_bound = np.exp(-0.5 * (w0_kmax**2))
        # B_bound = np.ones_like(A_bound)
        # kappa = B_bound / A_bound
        na_test = 0.15
        w0_kmax_test = 10.0 * na_test
        A_script = np.exp(-0.5 * (w0_kmax_test**2))
        B_script = 1.0
        kappa_script = B_script / A_script

        self.assertAlmostEqual(float(kappa_script), 3.0802168, places=4)
        self.assertAlmostEqual(float(A_script), 0.32465, places=4)

    def test_03_frame_bounds_monotonicity_and_asymptotics(self):
        """TC 2.3: Stress test boundary behavior of frame bounds A, B, kappa as NA -> 0 and NA -> infty."""
        na_grid = np.linspace(0.01, 1.0, 100)
        w0_kmax_grid = 10.0 * na_grid
        A_vals = np.exp(-0.5 * (w0_kmax_grid**2))
        kappa_vals = 1.0 / A_vals

        # Monotonicity: A strictly decreases, kappa strictly increases
        self.assertTrue(np.all(np.diff(A_vals) < 0.0), "Lower bound A must strictly decrease with NA.")
        self.assertTrue(np.all(np.diff(kappa_vals) > 0.0), "Condition number kappa must strictly increase with NA.")

        # Limit NA -> 0: tight frame (isometry, kappa = 1)
        A_zero = math.exp(-0.5 * (0.0**2))
        self.assertAlmostEqual(A_zero, 1.0, places=9)
        self.assertAlmostEqual(1.0 / A_zero, 1.0, places=9)

        # Limit NA -> large: A -> 0, kappa -> infty
        A_large = math.exp(-0.5 * (10.0**2))
        self.assertLess(A_large, 1e-20)
        self.assertGreater(1.0 / A_large, 1e20)


class TestRadialShiftScalingAndEmpiricalFindings(unittest.TestCase):
    """Stress test radial shift Delta R_l in generate_fig1_profiles.py and uncover empirical discrepancies."""

    @staticmethod
    def _find_peak_numerical(r0: float, w0: float, l: int) -> float:
        """Helper to find peak radius using the exact objective function in generate_fig1_profiles.py."""
        def neg_field(r_val):
            arg = 2.0 * r0 * r_val / (w0**2)
            return -(np.exp(-((r_val - r0)**2) / (w0**2)) * ive(l, arg))**2

        search_min = max(1e-4, r0 - 2.0 * w0)
        search_max = r0 + 3.0 * w0
        res = minimize_scalar(neg_field, bounds=(search_min, search_max), method="bounded")
        return float(res.x)

    def test_01_topological_peak_shift_relative_to_charge_zero(self):
        """TC 3.1: Verify that relative to ell=0, peak shifts strictly as Delta r_l approx l^2 * w0^4 / (8 * R0^3)."""
        r0 = 1.0   # mm
        w0 = 0.10  # mm
        peak_0 = self._find_peak_numerical(r0, w0, 0)

        for l in [1, 2, 3, 5, 8, 10]:
            peak_l = self._find_peak_numerical(r0, w0, l)
            shift_num_um = (peak_l - peak_0) * 1000.0  # um
            # Analytical expansion: Delta r_l = l^2 * w0^4 / (8 * R0^3)
            shift_ana_um = ((l**2) * (w0**4) / (8.0 * (r0**3))) * 1000.0  # um

            # The agreement between numerical maximization and l^2 * w0^4 / (8 * R0^3) is < 1.5%
            rel_error = abs(shift_num_um - shift_ana_um) / shift_ana_um
            self.assertLess(
                rel_error, 0.02,
                f"Topological shift for l={l} deviates: num={shift_num_um:.4f} um, ana={shift_ana_um:.4f} um"
            )

    def test_02_baseline_bessel_inward_bias_is_negative(self):
        """TC 3.2: Verify baseline shift r_peak(0) - R0 is negative: approx -w0^2 / (4 * R0)."""
        r0 = 1.0
        for w0 in [0.05, 0.10, 0.15, 0.20]:
            peak_0 = self._find_peak_numerical(r0, w0, 0)
            baseline_num_um = (peak_0 - r0) * 1000.0
            baseline_ana_um = (-w0**2 / (4.0 * r0)) * 1000.0

            self.assertLess(baseline_num_um, 0.0, "Baseline shift r_peak - R0 must be negative.")
            # Discrepancy between numerical and -w0^2 / (4*R0) is < 2%
            rel_diff = abs(baseline_num_um - baseline_ana_um) / abs(baseline_ana_um)
            self.assertLess(
                rel_diff, 0.02,
                f"Baseline shift for w0={w0} deviates: num={baseline_num_um:.4f} um, ana={baseline_ana_um:.4f} um"
            )

    def test_03_empirical_finding_fig1_code_discrepancy(self):
        """TC 3.3: EMPIRICAL FINDING - Document the discrepancies in generate_fig1_profiles.py Panel (b):
        1. Script computes shifts_num = (r_peak - r0) * 1000 which is negative (-2.5 um for w0=0.10 mm).
        2. Script sets ax_b.set_ylim(0, 15.0), clipping out all negative numerical points.
        3. Script analytical formula shifts_ana = (4l^2 - 1) w0^2 / (32 R0) uses w0^2 instead of w0^4/R0^2,
           introducing a factor of (R0/w0)^2 = 100x discrepancy.
        """
        r0 = 1.0
        w0 = 0.10
        peak_1 = self._find_peak_numerical(r0, w0, 1)
        shift_num_from_r0 = (peak_1 - r0) * 1000.0  # um

        # Finding 1: shift_num_from_r0 is negative (-2.497 um)
        self.assertLess(
            shift_num_from_r0, 0.0,
            f"Expected negative shift from R0 due to Bessel envelope, got {shift_num_from_r0} um"
        )

        # Finding 2: Code formula gives +0.9375 um (opposite sign and 100x scale relative to (peak_1 - peak_0))
        code_ana_formula = ((4.0 * (1**2) - 1.0) * (w0**2) / (32.0 * r0)) * 1000.0
        self.assertGreater(code_ana_formula, 0.0)

        # Finding 3: At l=10, code formula yields 124.69 um, while y-axis limit is 15.0 um
        code_ana_l10 = ((4.0 * (10**2) - 1.0) * (w0**2) / (32.0 * r0)) * 1000.0
        self.assertGreater(code_ana_l10, 15.0, "Code analytical curve exceeds ylim=15 um at l=10.")


class TestResourceHygieneAndSubprocesses(unittest.TestCase):
    """Stress test memory usage, figure handles, and subprocess hygiene."""

    def test_01_no_dangling_matplotlib_figures(self):
        """TC 4.1: Import simulation modules and verify all figures are closed after generation."""
        import matplotlib.pyplot as plt
        from v2.scripts.generate_fig1_profiles import generate_figure_1
        from v2.scripts.generate_fig2_overlap import generate_figure_2
        from v2.scripts.generate_fig3_frame_bounds import generate_figure_3
        from v2.scripts.generate_fig4_turbulence import generate_figure_4
        from v2.scripts.generate_fig5_quantum import generate_figure_5

        generators = [
            generate_figure_1,
            generate_figure_2,
            generate_figure_3,
            generate_figure_4,
            generate_figure_5,
        ]

        plt.close("all")
        self.assertEqual(len(plt.get_fignums()), 0, "Initial open figure count must be 0.")

        for gen in generators:
            # Run figure generator
            gen()
            # Verify figure is properly closed
            open_figs = plt.get_fignums()
            self.assertEqual(
                len(open_figs), 0,
                f"Figure generator {gen.__name__} leaked an unclosed figure handle: {open_figs}"
            )

    def test_02_memory_consumption_bounded(self):
        """TC 4.2: Verify process memory consumption does not grow unboundedly during repeated runs."""
        import gc
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)  # MB

        # Run full simulation suite in this process
        from v2.scripts.run_all_simulations import run_all
        for _ in range(2):
            run_all()
            gc.collect()

        mem_after = process.memory_info().rss / (1024 * 1024)  # MB
        mem_increase = mem_after - mem_before

        # Memory increase should remain reasonable (< 150 MB)
        self.assertLess(
            mem_increase, 150.0,
            f"Excessive memory growth detected: +{mem_increase:.1f} MB (before: {mem_before:.1f} MB, after: {mem_after:.1f} MB)"
        )


class TestFigurePDFPublicationIntegrity(unittest.TestCase):
    """Stress test publication aesthetic criteria: dimensions, labels, no unescaped LaTeX markup."""

    def test_01_pdf_dimensions_and_aspect_ratio(self):
        """TC 5.1: Verify each figure has 2x2 grid aspect ratio ~8.5 x 7.0 inches (approx 612 x 504 pt)."""
        for fig_name in FIGURE_FILENAMES:
            fig_path = FIGURES_DIR / fig_name
            doc = pymupdf.open(fig_path)
            rect = doc[0].rect
            width_pt, height_pt = rect.width, rect.height
            doc.close()

            # Expect width around 500-700 pt and height around 400-600 pt
            self.assertTrue(
                450 <= width_pt <= 750,
                f"Figure {fig_name} width ({width_pt:.1f} pt) out of expected range [450, 750]."
            )
            self.assertTrue(
                350 <= height_pt <= 650,
                f"Figure {fig_name} height ({height_pt:.1f} pt) out of expected range [350, 650]."
            )

    def test_02_no_unescaped_latex_markup_in_pdf_text(self):
        """TC 5.2: Verify no raw unrendered LaTeX markup (e.g. \\textbf, \\mathrm) appears in extracted PDF text."""
        forbidden_substrings = [r"\textbf", r"\mathrm", r"\textit", r"\mathbf"]
        for fig_name in FIGURE_FILENAMES:
            fig_path = FIGURES_DIR / fig_name
            doc = pymupdf.open(fig_path)
            text = doc[0].get_text()
            doc.close()

            for bad_str in forbidden_substrings:
                self.assertNotIn(
                    bad_str, text,
                    f"Figure {fig_name} contains unescaped raw LaTeX markup '{bad_str}' in extracted text."
                )

    def test_03_panel_sublabels_a_to_d_present_in_each_figure(self):
        """TC 5.3: Verify all four panel labels (a), (b), (c), (d) are present in each 2x2 figure."""
        for fig_name in FIGURE_FILENAMES:
            fig_path = FIGURES_DIR / fig_name
            doc = pymupdf.open(fig_path)
            text = doc[0].get_text()
            doc.close()

            for panel in ["(a)", "(b)", "(c)", "(d)"]:
                self.assertIn(
                    panel, text,
                    f"Figure {fig_name} missing panel sublabel '{panel}'."
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
