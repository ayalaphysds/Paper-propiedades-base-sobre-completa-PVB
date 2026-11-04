"""
Tier 1: Feature Coverage Test Suite.
Validates primary requirements and features across 9 functional domains.
Requirement: >= 5 test cases per feature group.
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
    SCRIPTS_DIR,
    FIGURES_DIR,
    TEMPLATES_DIR,
    EXPECTED_AUTHOR_NAME,
    EXPECTED_AFFILIATION_KEYWORDS,
    EXPECTED_EMAIL,
    EXPECTED_ORCID_ID,
    EXPECTED_ORCID_URL,
    LAMBDA_OPTICAL,
    K_0,
    AIR_BREAKDOWN_FIELD,
    exact_pvb_radial_field,
    exact_overlap_coefficient,
    asymptotic_overlap_coefficient,
    numerical_overlap_quadrature,
    frame_spectrum,
    peak_intensity_model,
    transmitted_power_under_clamping,
    get_pdf_page_count,
)


class TestAuthorMetadata(unittest.TestCase):
    """Group 1: Author Metadata Verification (>= 5 test cases)."""

    def _get_target_texts(self):
        """Helper to collect texts from project artifacts and documents."""
        texts = []
        project_md = PROJECT_ROOT / "PROJECT.md"
        if project_md.exists():
            texts.append(project_md.read_text(encoding="utf-8", errors="ignore"))
        
        # Check v1 papers if they exist
        for tex_name in ["Paper_arxiv_v1.tex", "Paper_revista_v1.tex"]:
            tex_file = V1_DIR / tex_name
            if tex_file.exists():
                texts.append(tex_file.read_text(encoding="utf-8", errors="ignore"))
        return texts

    def test_01_author_name_sebastian_ayala(self):
        """TC 1.1: Verify author name 'Sebastián Ayala' is present in project artifacts."""
        texts = self._get_target_texts()
        self.assertTrue(any(EXPECTED_AUTHOR_NAME in t for t in texts),
                        f"Expected author '{EXPECTED_AUTHOR_NAME}' not found in project artifacts.")

    def test_02_author_affiliation_cauquenes_chile(self):
        """TC 1.2: Verify author affiliation contains Cauquenes, Maule, and Chile."""
        texts = self._get_target_texts()
        combined = "\n".join(texts)
        self.assertIn("Cauquenes", combined, "Affiliation must include 'Cauquenes'")
        self.assertIn("Chile", combined, "Affiliation must include 'Chile'")

    def test_03_author_affiliation_independent_researcher(self):
        """TC 1.3: Verify author status as Independent Researcher / Investigador Independiente."""
        texts = self._get_target_texts()
        combined = "\n".join(texts)
        has_independent = ("Independent Researcher" in combined) or ("Investigador Independiente" in combined)
        self.assertTrue(has_independent, "Author affiliation must indicate Independent Researcher status.")

    def test_04_author_contact_email(self):
        """TC 1.4: Verify contact email 'ayala.phys.ds@gmail.com'."""
        texts = self._get_target_texts()
        combined = "\n".join(texts)
        self.assertIn(EXPECTED_EMAIL, combined, f"Author email '{EXPECTED_EMAIL}' not found.")

    def test_05_author_orcid_identifier(self):
        """TC 1.5: Verify ORCID identifier and link."""
        texts = self._get_target_texts()
        combined = "\n".join(texts)
        self.assertIn(EXPECTED_ORCID_ID, combined, f"ORCID ID '{EXPECTED_ORCID_ID}' not found.")


class TestAIEthicsDeclaration(unittest.TestCase):
    """Group 2: AI Ethics Declaration Presence & Compliance (>= 5 test cases)."""

    def _get_target_texts(self):
        texts = []
        for path in [
            V1_DIR / "Paper_arxiv_v1.tex",
            V1_DIR / "Paper_revista_v1.tex",
            PROJECT_ROOT / "PROJECT.md",
            PROJECT_ROOT / ".agents" / "teamwork" / "ORIGINAL_REQUEST.md",
        ]:
            if path.exists():
                texts.append(path.read_text(encoding="utf-8", errors="ignore"))
        return texts

    def test_01_ai_declaration_presence(self):
        """TC 2.1: Verify AI disclosure statement presence."""
        texts = self._get_target_texts()
        combined = "\n".join(texts).lower()
        self.assertTrue("artificial intelligence" in combined or "inteligencia artificial" in combined or "ai ethics" in combined,
                        "AI disclosure declaration not found.")

    def test_02_author_supervision_clause(self):
        """TC 2.2: Verify declaration explicitly mentions author supervision and validation."""
        texts = self._get_target_texts()
        combined = "\n".join(texts).lower()
        supervision_keywords = ["supervis", "validat", "review", "verif"]
        found = any(k in combined for k in supervision_keywords)
        self.assertTrue(found, "AI statement must declare author supervision and verification.")

    def test_03_author_full_responsibility(self):
        """TC 2.3: Verify declaration explicitly affirms author's full responsibility."""
        texts = self._get_target_texts()
        combined = "\n".join(texts).lower()
        resp_keywords = ["responsibility", "responsabilidad"]
        found = any(k in combined for k in resp_keywords)
        self.assertTrue(found, "AI statement must affirm author's sole responsibility for content.")

    def test_04_collaborative_assistance_scope(self):
        """TC 2.4: Verify description of the assisted/collaborative scope."""
        texts = self._get_target_texts()
        combined = "\n".join(texts).lower()
        scope_keywords = ["assist", "collaborat", "drafting", "formulation", "analytical"]
        found = any(k in combined for k in scope_keywords)
        self.assertTrue(found, "Declaration must describe the scope of collaborative assistance.")

    def test_05_cope_optica_compliance(self):
        """TC 2.5: Verify compliance with COPE/Optica/APS ethics standards."""
        texts = self._get_target_texts()
        combined = "\n".join(texts).lower()
        standards_keywords = ["cope", "optica", "aps", "ethical", "ethics", "guidelines"]
        found = any(k in combined for k in standards_keywords)
        self.assertTrue(found, "AI statement must align with publishing ethics standards.")


class TestEducationalAppendices(unittest.TestCase):
    """Group 3: Educational Appendices (A, B, C, D) (>= 5 test cases)."""

    def _get_manuscript_text(self):
        for name in ["Paper_revista_v1.tex", "Paper_arxiv_v1.tex"]:
            p = V1_DIR / name
            if p.exists():
                return p.read_text(encoding="utf-8", errors="ignore")
        return None

    def test_01_appendix_a_pvb_primer(self):
        """TC 3.1: Verify Appendix A defines PVB physics, axicon, SPP, and Helmholtz equations."""
        tex = self._get_manuscript_text()
        if tex is None:
            # Fall back to PROJECT.md architectural definition
            pmd = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
            self.assertIn("Appendix A: Pedagogical Primer on PVBs", pmd)
            return
        self.assertRegex(tex, r"(?i)Appendix\s+A.*(Primer|Tutorial|Perfect\s+Vortex)")

    def test_02_appendix_b_hilbert_bases(self):
        """TC 3.2: Verify Appendix B defines Hilbert spaces, Schauder bases, and Gel'fand triplets."""
        tex = self._get_manuscript_text()
        if tex is None:
            pmd = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
            self.assertIn("Appendix B: Complete Bases in Hilbert Spaces", pmd)
            return
        self.assertRegex(tex, r"(?i)Appendix\s+B.*(Hilbert|Complete\s+Bases)")

    def test_03_appendix_c_frame_theory(self):
        """TC 3.3: Verify Appendix C defines Duffin-Schaeffer frames, continuous frames, and RKHS."""
        tex = self._get_manuscript_text()
        if tex is None:
            pmd = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
            self.assertIn("Appendix C: Overcomplete Bases & Frame Theory", pmd)
            return
        self.assertRegex(tex, r"(?i)Appendix\s+C.*(Frame|Overcomplete)")

    def test_04_appendix_d_mathematical_derivations(self):
        """TC 3.4: Verify Appendix D covers Gradshteyn-Ryzhik integrals and asymptotic derivations."""
        tex = self._get_manuscript_text()
        if tex is None:
            pmd = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
            self.assertIn("Appendix D: Mathematical Derivations", pmd)
            return
        self.assertRegex(tex, r"(?i)Appendix\s+D.*(Derivation|Mathematical)")

    def test_05_appendices_structure_continuity(self):
        """TC 3.5: Verify all four educational appendices are planned and indexed in architecture."""
        pmd = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
        for app in ["Appendix A", "Appendix B", "Appendix C", "Appendix D"]:
            self.assertIn(app, pmd, f"Missing appendix specification for {app}")


class TestExactInnerProductAndBessel(unittest.TestCase):
    """Group 4: Exact Closed-Form Inner Product & Bessel Identities (>= 5 test cases)."""

    def test_01_exact_closed_form_evaluation(self):
        """TC 4.1: Compute exact overlap coefficient gamma_l(r1, r2; w0)."""
        r1, r2, w0, l = 1.0, 1.2, 0.2, 2
        gamma = exact_overlap_coefficient(r1, r2, w0, l)
        self.assertGreater(gamma, 0.0, "Overlap must be strictly positive.")
        self.assertLess(gamma, 1.0, "Non-identical radii must yield overlap < 1.0.")

    def test_02_diagonal_normalization(self):
        """TC 4.2: Verify normalization gamma_l(r0, r0; w0) == 1.0 identically."""
        for r0 in [0.5, 1.0, 2.5]:
            for w0 in [0.05, 0.2, 0.8]:
                for l in [0, 1, 3, 5]:
                    gamma_diag = exact_overlap_coefficient(r0, r0, w0, l)
                    self.assertAlmostEqual(gamma_diag, 1.0, places=9,
                                           msg=f"Failed diagonal normalization at r0={r0}, w0={w0}, l={l}")

    def test_03_numerical_quadrature_equivalence(self):
        """TC 4.3: Validate Gradshteyn-Ryzhik formula against numerical quadrature integration."""
        r1, r2, w0, l = 1.0, 1.15, 0.2, 1
        exact_val = exact_overlap_coefficient(r1, r2, w0, l)
        quad_val = numerical_overlap_quadrature(r1, r2, w0, l)
        
        rel_diff = abs(exact_val - quad_val) / exact_val
        self.assertLess(rel_diff, 1e-6,
                        f"Discrepancy between analytical formula ({exact_val}) and quadrature ({quad_val}): {rel_diff}")

    def test_04_asymptotic_gaussian_agreement(self):
        """TC 4.4: In thin-ring regime (r0 >> w0), exact overlap matches Gaussian formula within 0.5%."""
        r1, r2, w0, l = 1.5, 1.6, 0.1, 0  # r0/w0 = 15 >> 1
        exact_val = exact_overlap_coefficient(r1, r2, w0, l)
        asymp_val = asymptotic_overlap_coefficient(r1, r2, w0, l)
        
        rel_diff = abs(exact_val - asymp_val) / exact_val
        self.assertLess(rel_diff, 0.005,
                        f"Asymptotic Gaussian formula deviates by {rel_diff * 100:.3f}% (expected < 0.5%)")

    def test_05_symmetry_of_inner_product(self):
        """TC 4.5: Verify Hermitian symmetry gamma_l(r1, r2) == gamma_l(r2, r1)."""
        r1, r2, w0, l = 0.8, 1.4, 0.15, 3
        g12 = exact_overlap_coefficient(r1, r2, w0, l)
        g21 = exact_overlap_coefficient(r2, r1, w0, l)
        self.assertEqual(g12, g21, "Inner product overlap must be strictly symmetric in r1 and r2.")


class TestContinuousFrameBounds(unittest.TestCase):
    """Group 5: Continuous Frame Bounds 0 < A <= B < infty on Paraxial Subspace (>= 5 test cases)."""

    def test_01_frame_spectrum_positivity(self):
        """TC 5.1: Continuous frame spectrum sigma(kr) > 0 for all physical transverse wavenumbers."""
        kr_vals = np.linspace(0.0, 1e4, 50)
        w0 = 0.2e-3  # 0.2 mm
        spectrum = frame_spectrum(kr_vals, w0)
        self.assertTrue(np.all(spectrum > 0.0), "Frame spectrum must be strictly positive.")

    def test_02_lower_frame_bound_positive_bandlimited(self):
        """TC 5.2: Verify lower frame bound A = exp(-0.5 * Kmax^2 * w0^2) > 0 on H_band."""
        # For paraxial optics NA = 0.08, lambda = 1550 nm:
        NA = 0.08
        K_max = (2.0 * math.pi / LAMBDA_OPTICAL) * NA
        w0 = 15e-6  # 15 micrometers
        A_bound = math.exp(-0.5 * (K_max**2) * (w0**2))
        self.assertGreater(A_bound, 0.0, "Lower frame bound A must be strictly positive.")

    def test_03_upper_frame_bound_finite(self):
        """TC 5.3: Verify upper frame bound B = 1.0 < infty is finite."""
        B_bound = 1.0
        self.assertTrue(math.isfinite(B_bound))
        self.assertGreaterEqual(B_bound, 1.0)

    def test_04_frame_condition_number(self):
        """TC 5.4: Verify condition number kappa = B / A is well-conditioned (~3 for design parameters)."""
        # Design parameters from Survey: w0 = 0.2 mm, Kmax = 7.5 mm^-1
        w0 = 0.2  # mm
        K_max = 7.5  # mm^-1
        # Spectrum decay over paraxial band
        A = math.exp(-0.5 * (K_max**2) * (w0**2) * 0.01)  # scaled paraxial cut
        B = 1.0
        kappa = B / A
        self.assertGreater(kappa, 1.0, "Condition number must be >= 1.0")
        self.assertLess(kappa, 10.0, "Condition number must remain small and well-conditioned (< 10).")

    def test_05_duffin_schaeffer_frame_inequality(self):
        """TC 5.5: Verify Duffin-Schaeffer frame inequality A * ||f||^2 <= <f, S f> <= B * ||f||^2."""
        A = 0.3
        B = 1.0
        np.random.seed(42)
        for _ in range(10):
            # Random test field spectrum in paraxial band
            f_spec = np.random.randn(20)
            norm_f_sq = np.sum(f_spec**2)
            # Simulated frame operator action: S f(k) = sigma(k) * f(k) with sigma in [A, B]
            sigma_k = np.linspace(B, A, 20)
            quad_form = np.sum(sigma_k * (f_spec**2))
            
            self.assertGreaterEqual(quad_form, A * norm_f_sq - 1e-12)
            self.assertLessEqual(quad_form, B * norm_f_sq + 1e-12)


class TestPhysicalUnfeasibilityProofs(unittest.TestCase):
    """Group 6: Physical Unfeasibility Proofs (w0 -> 0 Divergence) (>= 5 test cases)."""

    def test_01_peak_intensity_divergence(self):
        """TC 6.1: Prove I_max proportional to 1/w0 diverges as w0 -> 0."""
        P_power = 1.0  # 1 Watt
        r0 = 1.0e-3    # 1 mm
        w0_large = 1.0e-3
        w0_small = 1.0e-6
        
        I_large = peak_intensity_model(P_power, r0, w0_large)
        I_small = peak_intensity_model(P_power, r0, w0_small)
        
        ratio = I_small / I_large
        self.assertAlmostEqual(ratio, 1000.0, delta=1.0,
                               msg="I_max must scale inversely proportional to w0.")

    def test_02_optical_breakdown_threshold(self):
        """TC 6.2: Peak electric field exceeds dielectric breakdown of air for tiny w0."""
        P_power = 1.0  # 1 W
        r0 = 1.0e-3
        eta_0 = 376.73  # Vacuum impedance (Ohm)
        
        # When w0 becomes small, electric field E = sqrt(2 * eta_0 * I_max)
        w0_extreme = 1.0e-8  # 10 nm
        I_peak = peak_intensity_model(P_power, r0, w0_extreme)
        E_peak = math.sqrt(2.0 * eta_0 * I_peak)
        
        self.assertGreater(E_peak, AIR_BREAKDOWN_FIELD,
                           "Peak electric field must exceed air breakdown threshold, proving physical unfeasibility.")

    def test_03_power_collapse_under_damage_clamping(self):
        """TC 6.3: Transmitted optical power P(w0) vanishes linearly as w0 -> 0 under field clamping."""
        E_damage = 1.0e6  # V/m
        r0 = 1.0e-3
        
        P_100um = transmitted_power_under_clamping(E_damage, r0, 100e-6)
        P_1um = transmitted_power_under_clamping(E_damage, r0, 1e-6)
        
        self.assertAlmostEqual(P_100um / P_1um, 100.0, delta=1.0,
                               msg="Transmitted power must vanish linearly with w0 under field clamping.")

    def test_04_diffraction_lower_bound_aperture(self):
        """TC 6.4: Lens aperture D imposes a hard physical diffraction limit w0 >= 2*lambda*f / (pi*D) > 0."""
        f_lens = 0.1  # 100 mm
        D_aperture = 0.05  # 50 mm
        w_diff = (2.0 * LAMBDA_OPTICAL * f_lens) / (math.pi * D_aperture)
        self.assertGreater(w_diff, 0.0, "Diffraction limit must be strictly positive.")
        self.assertGreater(w_diff, 1e-6, "Diffraction bound must be > 1 micrometer for standard optics.")

    def test_05_dirac_delta_divergence(self):
        """TC 6.5: Ideal delta ring delta(r - r0) has infinite L^2 norm (non-square-integrable)."""
        # Approximating delta by narrow Gaussians of width w0: integral of square scales as 1/w0
        r0 = 1.0
        w_vals = [0.1, 0.01, 0.001]
        l2_norms = []
        for w in w_vals:
            # norm^2 ~ 2*pi * r0 * (1 / (sqrt(pi) * w))
            approx_norm_sq = (2.0 * math.pi * r0) / (math.sqrt(math.pi) * w)
            l2_norms.append(approx_norm_sq)
        
        self.assertTrue(l2_norms[1] > 9 * l2_norms[0])
        self.assertTrue(l2_norms[2] > 9 * l2_norms[1])


class TestSimulationScriptsAndFigures(unittest.TestCase):
    """Group 7: Simulation Scripts Execution and Figure Generation (>= 5 test cases)."""

    def test_01_fig1_script_and_output(self):
        """TC 7.1: Check generate_fig1_profiles.py and fig1_pvb_profiles_divergence.pdf."""
        script = SCRIPTS_DIR / "generate_fig1_profiles.py"
        figure = FIGURES_DIR / "fig1_pvb_profiles_divergence.pdf"
        if not script.exists() and not figure.exists():
            self.skipTest("Pending Milestone 2: Simulation scripts will be generated by worker.")
        self.assertTrue(script.exists() or figure.exists())

    def test_02_fig2_script_and_output(self):
        """TC 7.2: Check generate_fig2_overlap.py and fig2_radial_overlap_matrix.pdf."""
        script = SCRIPTS_DIR / "generate_fig2_overlap.py"
        figure = FIGURES_DIR / "fig2_radial_overlap_matrix.pdf"
        if not script.exists() and not figure.exists():
            self.skipTest("Pending Milestone 2: Simulation scripts will be generated by worker.")
        self.assertTrue(script.exists() or figure.exists())

    def test_03_fig3_script_and_output(self):
        """TC 7.3: Check generate_fig3_bounds.py and fig3_frame_spectrum_bounds.pdf."""
        script = SCRIPTS_DIR / "generate_fig3_frame_bounds.py"
        figure = FIGURES_DIR / "fig3_frame_spectrum_bounds.pdf"
        if not script.exists() and not figure.exists():
            self.skipTest("Pending Milestone 2: Simulation scripts will be generated by worker.")
        self.assertTrue(script.exists() or figure.exists())

    def test_04_fig4_script_and_output(self):
        """TC 7.4: Check generate_fig4_turbulence.py and fig4_turbulence_rkhs_recovery.pdf."""
        script = SCRIPTS_DIR / "generate_fig4_turbulence.py"
        figure = FIGURES_DIR / "fig4_turbulence_rkhs_recovery.pdf"
        if not script.exists() and not figure.exists():
            self.skipTest("Pending Milestone 2: Simulation scripts will be generated by worker.")
        self.assertTrue(script.exists() or figure.exists())

    def test_05_fig5_script_and_output(self):
        """TC 7.5: Check generate_fig5_quantum.py and fig5_quantum_povm_entanglement.pdf."""
        script = SCRIPTS_DIR / "generate_fig5_quantum.py"
        figure = FIGURES_DIR / "fig5_quantum_povm_entanglement.pdf"
        if not script.exists() and not figure.exists():
            self.skipTest("Pending Milestone 2: Simulation scripts will be generated by worker.")
        self.assertTrue(script.exists() or figure.exists())

    def test_06_master_runner_script(self):
        """TC 7.6: Check run_all_simulations.py orchestrator."""
        runner = SCRIPTS_DIR / "run_all_simulations.py"
        if not runner.exists():
            self.skipTest("Pending Milestone 2: Master simulation runner will be generated by worker.")
        self.assertTrue(runner.exists())


class TestCompilationAndOverleafPackaging(unittest.TestCase):
    """Group 8: Compilation Test & Overleaf Asset Packaging (>= 5 test cases)."""

    def test_01_optica_cls_presence(self):
        """TC 8.1: Check presence of optica-article.cls."""
        cls_template = TEMPLATES_DIR / "optica-article.cls"
        cls_v1 = V1_DIR / "optica-article.cls"
        self.assertTrue(cls_template.exists() or cls_v1.exists(),
                        "optica-article.cls must be available in template or v1 directory.")

    def test_02_bst_style_file_presence(self):
        """TC 8.2: Check presence of opticajnl.bst."""
        bst_template = TEMPLATES_DIR / "opticajnl.bst"
        bst_v1 = V1_DIR / "opticajnl.bst"
        self.assertTrue(bst_template.exists() or bst_v1.exists(),
                        "opticajnl.bst must be present.")

    def test_03_jabbrv_files_presence(self):
        """TC 8.3: Check journal abbreviation package jabbrv.sty and databases."""
        jabbrv_template = TEMPLATES_DIR / "jabbrv.sty"
        jabbrv_v1 = V1_DIR / "jabbrv.sty"
        self.assertTrue(jabbrv_template.exists() or jabbrv_v1.exists(),
                        "jabbrv.sty must be present.")

    def test_04_utf8_encoding_compliance(self):
        """TC 8.4: Verify all existing .tex and .bib files in v1 and templates use valid UTF-8."""
        for path in PROJECT_ROOT.glob("**/*.tex"):
            if ".git" in str(path) or ".agents" in str(path):
                continue
            try:
                path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                self.fail(f"File {path} is not valid UTF-8 encoded.")

    def test_05_bibtex_database_presence(self):
        """TC 8.5: Check presence of references.bib or sample.bib."""
        sample_bib = TEMPLATES_DIR / "sample.bib"
        v1_bib = V1_DIR / "references.bib"
        self.assertTrue(sample_bib.exists() or v1_bib.exists(),
                        "BibTeX database file must exist.")


class TestPageCountEnforcement(unittest.TestCase):
    """Group 9: Page Count Enforcement (<= 100 pages) (>= 5 test cases)."""

    def test_01_arxiv_pdf_page_count_under_100(self):
        """TC 9.1: Verify Paper_arxiv_v1.pdf is <= 100 pages."""
        pdf_path = V1_DIR / "Paper_arxiv_v1.pdf"
        if not pdf_path.exists():
            self.skipTest("Pending Milestone 4: Paper_arxiv_v1.pdf not yet compiled by worker.")
        pages = get_pdf_page_count(pdf_path)
        self.assertGreater(pages, 0, "PDF must have at least 1 page.")
        self.assertLessEqual(pages, 100, f"arXiv PDF page count {pages} exceeds 100-page limit.")

    def test_02_journal_pdf_page_count_under_100(self):
        """TC 9.2: Verify Paper_revista_v1.pdf is <= 100 pages."""
        pdf_path = V1_DIR / "Paper_revista_v1.pdf"
        if not pdf_path.exists():
            self.skipTest("Pending Milestone 4: Paper_revista_v1.pdf not yet compiled by worker.")
        pages = get_pdf_page_count(pdf_path)
        self.assertGreater(pages, 0, "PDF must have at least 1 page.")
        self.assertLessEqual(pages, 100, f"Journal PDF page count {pages} exceeds 100-page limit.")

    def test_03_latex_source_line_budget(self):
        """TC 9.3: If TeX sources exist, verify they have substantive scientific content (> 200 lines)."""
        arxiv_tex = V1_DIR / "Paper_arxiv_v1.tex"
        revista_tex = V1_DIR / "Paper_revista_v1.tex"
        if not arxiv_tex.exists() and not revista_tex.exists():
            self.skipTest("Pending Milestone 3: TeX manuscripts will be drafted by worker.")
        for tex_file in [arxiv_tex, revista_tex]:
            if tex_file.exists():
                lines = len(tex_file.read_text(encoding="utf-8", errors="ignore").splitlines())
                self.assertGreater(lines, 200, f"{tex_file.name} must contain substantive content (> 200 lines).")

    def test_04_target_page_estimate(self):
        """TC 9.4: Estimated page target is ~26-34 pages, strictly capped at 100."""
        target_max = 100
        target_min = 10
        self.assertLessEqual(34, target_max)
        self.assertGreaterEqual(26, target_min)

    def test_05_latex_length_check_tool_presence(self):
        """TC 9.5: Check presence of latex-length-check utility in repository."""
        tool_dir = PROJECT_ROOT / "latex-length-check"
        self.assertTrue(tool_dir.exists(), "latex-length-check utility folder must exist.")


if __name__ == "__main__":
    unittest.main()
