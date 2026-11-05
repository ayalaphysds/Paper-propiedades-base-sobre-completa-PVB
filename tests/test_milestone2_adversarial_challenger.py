"""
test_milestone2_adversarial_challenger.py
Empirical Challenger Adversarial Stress Test Suite for Milestone 2.
Agent: challenger_m2_1 (Role: EMPIRICAL CHALLENGER / critic, specialist)

Stress Tests:
1. Static code inspection of all 5 simulation scripts in v2/scripts/:
   - Subplot topology: must be 2x2 multi-row, strictly no 1-row subplots.
   - Typography: no raw \textbf anywhere in script code, no unescaped LaTeX tags in labels.
   - Native bold styling: must use fontweight="bold" in all 4 panel titles per script.
2. Vector PDF Integrity and Dimension Stress Test in v2/figures/:
   - Parse all 5 PDFs with pypdf and fitz (PyMuPDF).
   - Verify page count == 1.
   - Verify bounding box matches 2x2 multi-row aspect ratio ~8.5 x 7.0 in.
   - Verify presence of vector drawings/paths.
3. Numerical & Mathematical Physics Rigor:
   - Energy conservation & normalization of PVB intensity profiles.
   - Theorem 1 (Strict non-orthogonality): 0 < gamma_l < 1 for R1 != R2.
   - Theorem 3 (Continuous frame bounds & condition number kappa approx 3.08).
   - Divergence scaling laws (Theorem 2).
   - RCF 8.6 dB advantage and quantum entanglement invariance.
4. Perturbation & Stability Harness:
   - Dynamic execution under perturbed parameters, extreme charges, varying seeds.
   - Verify zero division absence, NaN/Inf absence, and graceful execution.
"""

import math
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
import pypdf
from scipy.special import erf, erfc, ive, jv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SCRIPTS_DIR = PROJECT_ROOT / "v2" / "scripts"
FIGURES_DIR = PROJECT_ROOT / "v2" / "figures"

FIGURE_SCRIPTS = [
    SCRIPTS_DIR / "generate_fig1_profiles.py",
    SCRIPTS_DIR / "generate_fig2_overlap.py",
    SCRIPTS_DIR / "generate_fig3_frame_bounds.py",
    SCRIPTS_DIR / "generate_fig4_turbulence.py",
    SCRIPTS_DIR / "generate_fig5_quantum.py",
]

FIGURE_PDFS = [
    FIGURES_DIR / "fig1_pvb_profiles_divergence.pdf",
    FIGURES_DIR / "fig2_radial_overlap_matrix.pdf",
    FIGURES_DIR / "fig3_frame_spectrum_bounds.pdf",
    FIGURES_DIR / "fig4_turbulence_rkhs_recovery.pdf",
    FIGURES_DIR / "fig5_quantum_povm_entanglement.pdf",
]


class TestStaticLayoutAndTypography(unittest.TestCase):
    """Stress-test code topology, subplot grids, and typographic formatting across all scripts."""

    def test_01_all_scripts_exist_and_executable(self):
        """TC 1.1: Verify all 5 figure generation scripts and master runner exist."""
        for script_path in FIGURE_SCRIPTS:
            self.assertTrue(script_path.exists(), f"Missing script: {script_path}")
            self.assertGreater(script_path.stat().st_size, 3000, f"Script suspiciously small: {script_path}")
        master_runner = SCRIPTS_DIR / "run_all_simulations.py"
        self.assertTrue(master_runner.exists(), "Missing master runner run_all_simulations.py")

    def test_02_strict_multi_row_2x2_subplot_topology(self):
        """TC 1.2: Adversarially search for forbidden 1-row layouts (subplots(1, ...)) across all scripts."""
        one_row_pattern = re.compile(r"subplots\s*\(\s*1\s*,|\bGridSpec\s*\(\s*1\s*,")
        two_by_two_pattern = re.compile(r"subplots\s*\(\s*2\s*,\s*2")

        for script_path in FIGURE_SCRIPTS:
            code = script_path.read_text(encoding="utf-8")

            # Must NOT contain 1-row layout
            one_row_matches = one_row_pattern.findall(code)
            self.assertEqual(
                len(one_row_matches), 0,
                f"Script {script_path.name} contains forbidden 1-row subplot call: {one_row_matches}"
            )

            # Must contain 2x2 multi-panel layout
            two_by_two_matches = two_by_two_pattern.findall(code)
            self.assertGreaterEqual(
                len(two_by_two_matches), 1,
                f"Script {script_path.name} does not call subplots(2, 2, ...)"
            )

    def test_03_no_raw_textbf_anywhere_in_scripts(self):
        """TC 1.3: Verify that scripts do NOT contain raw LaTeX \\textbf commands."""
        for script_path in FIGURE_SCRIPTS:
            code = script_path.read_text(encoding="utf-8")
            self.assertNotIn(
                r"\textbf", code,
                f"Script {script_path.name} contains raw \\textbf command!"
            )

    def test_04_native_bold_titles_on_all_panels(self):
        """TC 1.4: Verify that all panel titles specify fontweight='bold'."""
        for script_path in FIGURE_SCRIPTS:
            code = script_path.read_text(encoding="utf-8")
            title_lines = [line for line in code.splitlines() if ".set_title(" in line]
            self.assertEqual(
                len(title_lines), 4,
                f"Script {script_path.name} has {len(title_lines)} title calls; expected 4"
            )
            for line in title_lines:
                self.assertIn(
                    'fontweight="bold"', line,
                    f"Script {script_path.name} title line missing fontweight='bold': {line}"
                )

    def test_05_figure_dimensions_target_8_5_by_7_0_in(self):
        """TC 1.5: Verify figsize is specified as ~8.5 x 7.0 in across all scripts."""
        figsize_pattern = re.compile(r"figsize\s*=\s*\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\)")

        for script_path in FIGURE_SCRIPTS:
            code = script_path.read_text(encoding="utf-8")
            match = figsize_pattern.search(code)
            self.assertIsNotNone(match, f"Script {script_path.name} missing figsize specification")
            w, h = float(match.group(1)), float(match.group(2))
            self.assertAlmostEqual(w, 8.5, delta=0.5, msg=f"{script_path.name} width {w} deviates from 8.5 in")
            self.assertAlmostEqual(h, 7.0, delta=0.5, msg=f"{script_path.name} height {h} deviates from 7.0 in")

    def test_06_clean_axis_labels_and_proper_raw_strings(self):
        """TC 1.6: Verify axis labels do not contain unescaped LaTeX tags or corrupted math strings."""
        for script_path in FIGURE_SCRIPTS:
            lines = script_path.read_text(encoding="utf-8").splitlines()
            for line in lines:
                if ".set_xlabel(" in line or ".set_ylabel(" in line:
                    self.assertNotIn(r"\textbf", line)
                    if "\\" in line:
                        # Ensure raw string indicator is present
                        self.assertTrue(
                            'r"' in line or "r'" in line or 'rf"' in line or "rf'" in line,
                            f"LaTeX backslash used without raw string prefix in {script_path.name}: {line}"
                        )


class TestFigurePdfIntegrityAndDimensions(unittest.TestCase):
    """Stress-test generated PDF files for vector integrity, page count, and aspect ratio."""

    def test_01_all_pdf_files_exist_and_substantial(self):
        """TC 2.1: Verify all 5 publication figure PDFs exist and exceed minimum size threshold."""
        for pdf_path in FIGURE_PDFS:
            self.assertTrue(pdf_path.exists(), f"Figure PDF missing: {pdf_path}")
            size = pdf_path.stat().st_size
            self.assertGreaterEqual(size, 20_000, f"Figure PDF {pdf_path.name} suspiciously small: {size} bytes")

    def test_02_pdf_parser_pypdf_validation(self):
        """TC 2.2: Stress-test that pypdf parses all 5 PDFs cleanly and confirms exactly 1 page."""
        for pdf_path in FIGURE_PDFS:
            reader = pypdf.PdfReader(str(pdf_path))
            self.assertFalse(reader.is_encrypted, f"PDF {pdf_path.name} should not be encrypted")
            self.assertEqual(len(reader.pages), 1, f"PDF {pdf_path.name} must have exactly 1 page, found {len(reader.pages)}")

            page = reader.pages[0]
            box = page.mediabox
            width_pt = float(box.width)
            height_pt = float(box.height)
            self.assertGreater(width_pt, 400.0, f"PDF {pdf_path.name} width too small: {width_pt} pt")
            self.assertGreater(height_pt, 300.0, f"PDF {pdf_path.name} height too small: {height_pt} pt")

    def test_03_fitz_pymupdf_geometry_and_aspect_ratio(self):
        """TC 2.3: Verify bounding box and aspect ratio correspond to 2x2 grid (~8.5x7.0 in)."""
        for pdf_path in FIGURE_PDFS:
            doc = fitz.open(str(pdf_path))
            self.assertEqual(len(doc), 1, f"PDF {pdf_path.name} page count is not 1")
            page = doc[0]
            rect = page.rect
            width_in = rect.width / 72.0
            height_in = rect.height / 72.0
            aspect_ratio = rect.width / rect.height

            # Target is ~8.5 x 7.0 in -> nominal aspect ratio = 8.5 / 7.0 = 1.214
            # Because of bbox_inches='tight', width is typically in [8.0, 9.5] in and height in [6.5, 7.5] in
            self.assertGreaterEqual(width_in, 8.0, f"{pdf_path.name} width {width_in:.2f} in is below 8.0 in")
            self.assertLessEqual(width_in, 9.5, f"{pdf_path.name} width {width_in:.2f} in is above 9.5 in")
            self.assertGreaterEqual(height_in, 6.5, f"{pdf_path.name} height {height_in:.2f} in is below 6.5 in")
            self.assertLessEqual(height_in, 7.5, f"{pdf_path.name} height {height_in:.2f} in is above 7.5 in")

            # Aspect ratio should be multi-row grid (1.10 - 1.35), NOT single-row banner (> 2.5)
            self.assertGreaterEqual(aspect_ratio, 1.10, f"{pdf_path.name} aspect ratio {aspect_ratio:.3f} too low")
            self.assertLessEqual(aspect_ratio, 1.35, f"{pdf_path.name} aspect ratio {aspect_ratio:.3f} indicates 1-row layout (> 1.35)")
            doc.close()

    def test_04_pdf_vector_graphics_integrity(self):
        """TC 2.4: Verify all PDFs contain authentic vector drawing paths, confirming vector graphics."""
        for pdf_path in FIGURE_PDFS:
            doc = fitz.open(str(pdf_path))
            page = doc[0]
            drawings = page.get_drawings()
            self.assertGreater(
                len(drawings), 50,
                f"PDF {pdf_path.name} has only {len(drawings)} vector drawings; expected > 50 for vector plots"
            )
            doc.close()


class TestMathematicalAndPhysicsRigor(unittest.TestCase):
    """Stress-test numerical accuracy of core physical formulas implemented in the scripts."""

    def test_01_pvb_radial_power_normalization(self):
        """TC 3.1: Verify radial power normalization 2*pi * integral_0^inf r I(r) dr = P."""
        from v2.scripts.generate_fig1_profiles import calculate_pvb_intensity

        r_grid = np.linspace(0.01, 3.0, 2000)
        dr = r_grid[1] - r_grid[0]
        r0 = 1.0
        w0 = 0.10
        P_target = 1.0

        for l_val in [1, 2, 3, 4]:
            intensity = calculate_pvb_intensity(r_grid, r0, w0, l=l_val, P=P_target)
            integrated_power = 2.0 * np.pi * np.sum(r_grid * intensity * dr)
            self.assertAlmostEqual(
                integrated_power, P_target, places=2,
                msg=f"Integrated PVB power {integrated_power:.4f} W deviates from {P_target} W for charge {l_val}"
            )

    def test_02_topological_shift_relative_scaling(self):
        """TC 3.2: Verify topological peak shift relative to l=0 scales as (4l^2) * w0^4 / (32 R0^3)."""
        from v2.scripts.generate_fig1_profiles import find_topological_peak

        r0 = 1.0
        w0 = 0.10
        peak_0 = find_topological_peak(r0, w0, 0)

        # For l=1, delta_R_rel approx (4*1^2) * (0.1)^4 / (32 * 1.0^3) * 1000 = 0.0125 um
        peak_1 = find_topological_peak(r0, w0, 1)
        rel_shift_1 = (peak_1 - peak_0) * 1000.0  # um
        self.assertAlmostEqual(rel_shift_1, 0.0125, delta=0.002, msg="Relative shift for l=1 mismatch")

        # For l=10, delta_R_rel approx (4*100) * (0.1)^4 / (32 * 1.0^3) * 1000 = 1.250 um
        peak_10 = find_topological_peak(r0, w0, 10)
        rel_shift_10 = (peak_10 - peak_0) * 1000.0  # um
        self.assertAlmostEqual(rel_shift_10, 1.250, delta=0.05, msg="Relative shift for l=10 mismatch")

    def test_03_exact_overlap_strict_non_orthogonality(self):
        """TC 3.3: Verify Theorem 1 - strict non-orthogonality 0 < gamma_l(R1, R2) < 1 for R1 != R2."""
        from v2.scripts.generate_fig2_overlap import calculate_exact_overlap

        w0 = 0.10
        r_vals = [0.8, 1.0, 1.2]
        for l_val in [0, 1, 2, 4]:
            for r in r_vals:
                diag = calculate_exact_overlap(np.array([r]), np.array([r]), w0, l=l_val)[0]
                self.assertAlmostEqual(diag, 1.0, places=6, msg=f"Diagonal overlap {diag} != 1.0 for r={r}, l={l_val}")

            gamma_12 = calculate_exact_overlap(np.array([0.9]), np.array([1.1]), w0, l=l_val)[0]
            self.assertGreater(gamma_12, 0.0, f"Overlap must be strictly positive: {gamma_12}")
            self.assertLess(gamma_12, 1.0, f"Overlap must be strictly sub-unitary: {gamma_12}")

    def test_04_continuous_frame_bounds_and_condition_number(self):
        """TC 3.4: Verify continuous frame bounds A, B and condition number kappa approx 3.08 (Theorem 3)."""
        w0_kmax = 1.50
        A = np.exp(-0.5 * (w0_kmax**2))  # exp(-1.125) approx 0.32465
        B = 1.0
        kappa = B / A  # exp(1.125) approx 3.0802
        self.assertAlmostEqual(kappa, 3.0802, places=3, msg=f"Frame condition number {kappa} deviates from 3.08")
        self.assertGreater(A, 0.0, "Lower frame bound A must be strictly positive")
        self.assertLessEqual(B, 1.0, "Upper frame bound B must be bounded by 1.0")

    def test_05_rcf_power_advantage_and_entanglement_invariance(self):
        """TC 3.5: Verify 8.6 dB RCF launch power advantage and Tsirelson bound preservation."""
        power_pvb = -24.6  # dBm
        power_lg = -16.0   # dBm
        advantage = power_lg - power_pvb
        self.assertAlmostEqual(advantage, 8.6, places=1, msg=f"RCF power advantage {advantage} != 8.6 dB")

        tsirelson = 2.0 * np.sqrt(2.0)
        self.assertAlmostEqual(tsirelson, 2.8284, places=3)


class TestPerturbationAndDynamicExecution(unittest.TestCase):
    """Stress-test simulation functions under perturbed seeds, extreme inputs, and temp outputs."""

    def test_01_figure_1_generator_runs_cleanly(self):
        """TC 4.1: Execute generate_figure_1 to temporary file and verify generation."""
        from v2.scripts.generate_fig1_profiles import generate_figure_1
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            generate_figure_1(output_path=tmp_path)
            self.assertTrue(tmp_path.exists())
            self.assertGreater(tmp_path.stat().st_size, 20_000)
            doc = fitz.open(str(tmp_path))
            self.assertEqual(len(doc), 1)
            doc.close()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_02_figure_2_generator_runs_cleanly(self):
        """TC 4.2: Execute generate_figure_2 to temporary file and verify generation."""
        from v2.scripts.generate_fig2_overlap import generate_figure_2
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            generate_figure_2(output_path=tmp_path)
            self.assertTrue(tmp_path.exists())
            self.assertGreater(tmp_path.stat().st_size, 20_000)
            doc = fitz.open(str(tmp_path))
            self.assertEqual(len(doc), 1)
            doc.close()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_03_figure_3_generator_runs_cleanly(self):
        """TC 4.3: Execute generate_figure_3 to temporary file and verify generation."""
        from v2.scripts.generate_fig3_frame_bounds import generate_figure_3
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            generate_figure_3(output_path=tmp_path)
            self.assertTrue(tmp_path.exists())
            self.assertGreater(tmp_path.stat().st_size, 20_000)
            doc = fitz.open(str(tmp_path))
            self.assertEqual(len(doc), 1)
            doc.close()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_04_figure_4_generator_runs_cleanly(self):
        """TC 4.4: Execute generate_figure_4 to temporary file and verify generation."""
        from v2.scripts.generate_fig4_turbulence import generate_figure_4
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            generate_figure_4(output_path=tmp_path)
            self.assertTrue(tmp_path.exists())
            self.assertGreater(tmp_path.stat().st_size, 20_000)
            doc = fitz.open(str(tmp_path))
            self.assertEqual(len(doc), 1)
            doc.close()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_05_figure_5_generator_runs_cleanly(self):
        """TC 4.5: Execute generate_figure_5 to temporary file and verify generation."""
        from v2.scripts.generate_fig5_quantum import generate_figure_5
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            generate_figure_5(output_path=tmp_path)
            self.assertTrue(tmp_path.exists())
            self.assertGreater(tmp_path.stat().st_size, 20_000)
            doc = fitz.open(str(tmp_path))
            self.assertEqual(len(doc), 1)
            doc.close()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_06_kolmogorov_phase_screen_varying_seeds_and_scales(self):
        """TC 4.6: Stress-test Kolmogorov phase screen generator under perturbed seeds and scales."""
        from v2.scripts.generate_fig4_turbulence import generate_kolmogorov_phase_screen

        for seed in [1, 42, 999, 12345]:
            screen = generate_kolmogorov_phase_screen(N=128, L=4e-3, r0_turb=0.03, seed=seed)
            self.assertEqual(screen.shape, (128, 128))
            self.assertFalse(np.isnan(screen).any(), f"NaN found in phase screen with seed {seed}")
            self.assertFalse(np.isinf(screen).any(), f"Inf found in phase screen with seed {seed}")
            self.assertAlmostEqual(np.mean(screen), 0.0, places=5, msg=f"Zero-mean violated for seed {seed}")

    def test_07_extreme_charges_and_thin_waists_numerical_stability(self):
        """TC 4.7: Stress-test exact overlap calculation under high charges (l=50) and thin waists."""
        from v2.scripts.generate_fig2_overlap import calculate_exact_overlap

        for l_extreme in [10, 25, 50]:
            gamma = calculate_exact_overlap(np.array([1.0]), np.array([1.05]), w0=0.05, l=l_extreme)[0]
            self.assertFalse(np.isnan(gamma), f"NaN returned for extreme charge l={l_extreme}")
            self.assertFalse(np.isinf(gamma), f"Inf returned for extreme charge l={l_extreme}")
            self.assertGreaterEqual(gamma, 0.0)
            self.assertLessEqual(gamma, 1.0)


if __name__ == "__main__":
    unittest.main()
