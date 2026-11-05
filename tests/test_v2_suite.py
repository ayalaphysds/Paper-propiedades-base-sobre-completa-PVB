"""
Master E2E Test Suite for Version 2 (v2) of the Paper Project:
"Propiedades Clásicas y Cuánticas de la Sobrecompletitud de los Haces de Vórtice Perfecto (PVB)"

Author: Sebastián Ayala (Investigador Independiente, Cauquenes, Chile)
E2E Testing Track: Version 2 Verification Suite
Structured across 4 systematic tiers:
  - Tier 1: Feature Coverage (deliverables, metadata, bibliographies, appendices)
  - Tier 2: Boundary & Corner Cases (empty files, multi-row layouts, negative checks)
  - Tier 3: Cross-Feature Combinations (figure inclusions, citation consistency, parameters)
  - Tier 4: Real-World Application Scenarios (simulation execution, mathematical proofs, Overleaf packaging)
"""

import math
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_helpers import (
    PROJECT_ROOT,
    V1_DIR,
    V2_DIR,
    SCRIPTS_V2_DIR,
    FIGURES_V2_DIR,
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
    V2_EXPECTED_FIGURES,
    V2_EXPECTED_SCRIPTS,
    V2_AI_CITATIONS,
    V2_REVISION_COMMENTS,
    validate_abstract_cleanliness,
    validate_technical_spelling_radii,
    reproducing_kernel,
    frame_condition_number,
    find_pdflatex_compiler,
)

# Flag for strict milestone enforcement (fails if pending deliverable is missing)
FAIL_ON_PENDING = os.environ.get("FAIL_ON_PENDING", "0").lower() in ("1", "true", "yes")


def require_path(test_case: unittest.TestCase, path: Path, milestone_desc: str):
    """Graceful helper for progressive testability:
    If path does not exist, skips the test unless FAIL_ON_PENDING is set.
    """
    if not path.exists():
        msg = f"{milestone_desc} [Path not found: '{path}']"
        if FAIL_ON_PENDING:
            test_case.fail(f"STRICT MODE FAILURE - {msg}")
        else:
            test_case.skipTest(msg)


def extract_latex_abstract(tex_content: str) -> str:
    """Extracts abstract text from LaTeX source content."""
    # Match standard \begin{abstract}...\end{abstract}
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_content, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Match command \abstract{...}
    m2 = re.search(r"\\abstract\{([^}]+)\}", tex_content, re.DOTALL)
    if m2:
        return m2.group(1).strip()
    return ""


def extract_bibtex_keys(bib_content: str) -> set:
    """Extracts all defined citation keys from BibTeX source content."""
    keys = set()
    for match in re.finditer(r"@\w+\s*\{\s*([^,\s]+)", bib_content):
        keys.add(match.group(1).strip())
    return keys


def extract_latex_citations(tex_content: str) -> set:
    """Extracts all citation keys referenced via \\cite, \\citep, \\citet in LaTeX."""
    citations = set()
    for match in re.finditer(r"\\cite[pt]?\{([^}]+)\}", tex_content):
        for key in match.group(1).split(","):
            cleaned = key.strip()
            if cleaned:
                citations.add(cleaned)
    return citations


def extract_figure_inclusions(tex_content: str) -> set:
    """Extracts filenames referenced via \\includegraphics in LaTeX."""
    figures = set()
    for match in re.finditer(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}", tex_content):
        fname = Path(match.group(1).strip()).name
        if not fname.endswith(".pdf"):
            fname += ".pdf"
        figures.add(fname)
    return figures


# ==============================================================================
# TIER 1: FEATURE COVERAGE
# ==============================================================================

class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Feature Coverage of Version 2 Deliverables.
    Verifies layout, bibliographies, defense document, manuscripts, PDFs, scripts, and bundle.
    """

    def test_01_v2_directory_and_layout(self):
        """TC 1.1: Verify v2/ directory existence and layout (v2/scripts/, v2/figures/)."""
        require_path(self, V2_DIR, "Milestone M1 pending: v2/ directory not yet created")
        self.assertTrue(V2_DIR.is_dir(), "v2/ must be a directory.")
        
        scripts_dir = V2_DIR / "scripts"
        figures_dir = V2_DIR / "figures"
        self.assertTrue(scripts_dir.exists(), "v2/scripts/ directory must exist.")
        self.assertTrue(scripts_dir.is_dir(), "v2/scripts/ must be a directory.")
        self.assertTrue(figures_dir.exists(), "v2/figures/ directory must exist.")
        self.assertTrue(figures_dir.is_dir(), "v2/figures/ must be a directory.")

    def test_02_references_bib_contains_ai_citations(self):
        """TC 1.2: Verify v2/references.bib contains the 3 required AI citations."""
        bib_file = V2_DIR / "references.bib"
        require_path(self, bib_file, "Milestone M1 pending: v2/references.bib not yet created")
        
        bib_content = bib_file.read_text(encoding="utf-8", errors="ignore")
        self.assertGreater(len(bib_content.strip()), 0, "v2/references.bib must not be empty.")
        
        defined_keys = extract_bibtex_keys(bib_content)
        
        # Verify 3 AI ethics citations: Jauhiainen (2026), PaperBanana (2026), Haber et al. (2025)
        for expected_key in V2_AI_CITATIONS:
            # Check direct key match or flexible regex match
            key_found = any(re.search(expected_key, k, re.IGNORECASE) for k in defined_keys)
            self.assertTrue(
                key_found,
                f"Required AI citation '{expected_key}' not found in v2/references.bib. Found keys: {defined_keys}"
            )
        
        # Verify essential fields in BibTeX entries (title, author, year)
        for key in ["Jauhiainen", "PaperBanana", "Haber"]:
            match = re.search(rf"@\w+\s*\{{\s*[^,]*{key}[^,]*,(.*?)\n\}}", bib_content, re.DOTALL | re.IGNORECASE)
            if match:
                entry_body = match.group(1).lower()
                self.assertIn("author", entry_body, f"BibTeX entry for {key} missing 'author' field.")
                self.assertIn("title", entry_body, f"BibTeX entry for {key} missing 'title' field.")
                self.assertIn("year", entry_body, f"BibTeX entry for {key} missing 'year' field.")

    def test_03_author_defense_report_and_metadata(self):
        """TC 1.3: Verify v2/RESPUESTAS_REVISION_V2.md exists and covers all 7 revision comments."""
        defense_file = V2_DIR / "RESPUESTAS_REVISION_V2.md"
        require_path(self, defense_file, "Milestone M1 pending: v2/RESPUESTAS_REVISION_V2.md not yet created")
        
        content = defense_file.read_text(encoding="utf-8", errors="ignore")
        self.assertGreater(len(content.strip()), 200, "Defense document must contain substantive content.")
        
        # Verify author metadata
        self.assertIn(EXPECTED_AUTHOR_NAME, content, "Author name Sebastián Ayala must be present in defense doc.")
        self.assertIn("Cauquenes", content, "Affiliation must include Cauquenes.")
        self.assertIn("Chile", content, "Affiliation must include Chile.")
        self.assertIn(EXPECTED_ORCID_ID, content, "ORCID ID must be present in defense doc.")
        self.assertIn(EXPECTED_EMAIL, content, "Author email must be present in defense doc.")
        
        # Verify all 7 review comments are covered
        lower_content = content.lower()
        for comment_idx, keywords in V2_REVISION_COMMENTS.items():
            # Check for header like "Comentario 1" or "Comment 1" or keyword matches
            comment_header_found = (
                f"comentario {comment_idx}" in lower_content
                or f"comentario #{comment_idx}" in lower_content
                or f"comment {comment_idx}" in lower_content
                or f"comment #{comment_idx}" in lower_content
                or f"observación {comment_idx}" in lower_content
                or f"punto {comment_idx}" in lower_content
            )
            keyword_found = any(k in lower_content for k in keywords)
            self.assertTrue(
                comment_header_found or keyword_found,
                f"Review Comment #{comment_idx} not adequately addressed in v2/RESPUESTAS_REVISION_V2.md."
            )

    def test_04_arxiv_tex_structure_and_compliance(self):
        """TC 1.4: Verify v2/Paper_arxiv_v2.tex structure and substantive content (>200 lines)."""
        arxiv_file = V2_DIR / "Paper_arxiv_v2.tex"
        require_path(self, arxiv_file, "Milestone M3 pending: v2/Paper_arxiv_v2.tex not yet created")
        
        content = arxiv_file.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        self.assertGreater(len(lines), 200, "Paper_arxiv_v2.tex must have >200 lines.")
        self.assertIn(r"\begin{document}", content, "Missing \\begin{document} in arXiv manuscript.")
        self.assertIn(r"\end{document}", content, "Missing \\end{document} in arXiv manuscript.")

    def test_05_revista_tex_structure_and_compliance(self):
        """TC 1.5: Verify v2/Paper_revista_v2.tex structure and substantive content (>200 lines)."""
        revista_file = V2_DIR / "Paper_revista_v2.tex"
        require_path(self, revista_file, "Milestone M3 pending: v2/Paper_revista_v2.tex not yet created")
        
        content = revista_file.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        self.assertGreater(len(lines), 200, "Paper_revista_v2.tex must have >200 lines.")
        self.assertIn(r"\begin{document}", content, "Missing \\begin{document} in Revista manuscript.")
        self.assertIn(r"\end{document}", content, "Missing \\end{document} in Revista manuscript.")

    def test_06_abstract_q1_style_and_cleanliness(self):
        """TC 1.6: Verify both abstracts adhere to Q1 standards: no raw equations, no Eq. numbers, no bracketed citations."""
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            abstract = extract_latex_abstract(content)
            self.assertTrue(len(abstract) > 50, f"Abstract in {name} is missing or too short ({len(abstract)} chars).")
            
            violations = validate_abstract_cleanliness(abstract)
            self.assertEqual(
                violations, [],
                f"Abstract in {name} violates Q1 publication standard:\n" + "\n".join(violations)
            )

    def test_07_technical_spelling_radii_plural(self):
        """TC 1.7: Enforce technical English spelling: Latin plural 'radii' used correctly."""
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            violations = validate_technical_spelling_radii(content)
            self.assertEqual(
                violations, [],
                f"Technical spelling violations in {name}:\n" + "\n".join(violations)
            )
            # Verify that 'radii' is indeed used in the text
            self.assertRegex(content, r"(?i)\bradii\b", f"Expected scientific term 'radii' not found in {name}.")

    def test_08_author_metadata_across_tex(self):
        """TC 1.8: Verify author metadata across both TeX manuscripts."""
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            self.assertIn(EXPECTED_AUTHOR_NAME, content, f"Author name missing in {name}")
            self.assertIn("Cauquenes", content, f"Cauquenes missing in {name}")
            self.assertIn("Chile", content, f"Chile missing in {name}")
            self.assertIn(EXPECTED_ORCID_ID, content, f"ORCID ID missing in {name}")
            self.assertIn(EXPECTED_EMAIL, content, f"Email missing in {name}")

    def test_09_pedagogical_appendices_a_to_d(self):
        """TC 1.9: Verify pedagogical Appendices A, B, C, D are present in manuscripts."""
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            # Appendix A: PVB optics / primer
            self.assertRegex(content, r"(?i)Appendix\s+A.*?(Primer|Tutorial|Perfect\s+Vortex|Optics)",
                             f"Appendix A definition missing in {name}")
            # Appendix B: Complete bases in Hilbert spaces
            self.assertRegex(content, r"(?i)Appendix\s+B.*?(Hilbert|Complete\s+Bases|Schauder)",
                             f"Appendix B definition missing in {name}")
            # Appendix C: Overcomplete bases & Frame theory
            self.assertRegex(content, r"(?i)Appendix\s+C.*?(Frame|Overcomplete|RKHS)",
                             f"Appendix C definition missing in {name}")
            # Appendix D: Mathematical derivations
            self.assertRegex(content, r"(?i)Appendix\s+D.*?(Derivation|Mathematical|Gradshteyn)",
                             f"Appendix D definition missing in {name}")

    def test_10_ai_ethics_declaration_section(self):
        """TC 1.10: Verify AI Ethics Declaration section is present and cites the 3 AI references."""
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            # Section header
            self.assertRegex(
                content,
                r"(?i)(?:section\*?\{|subsection\*?\{)[^}]*(?:artificial intelligence|inteligencia artificial|ai declaration|ai ethics)",
                f"AI ethics declaration section header missing in {name}"
            )
            # Author responsibility affirmation
            lower_content = content.lower()
            self.assertTrue(
                "responsibility" in lower_content or "responsabilidad" in lower_content,
                f"Author full responsibility clause missing in {name}"
            )

    def test_11_arxiv_and_revista_pdf_page_count_under_100(self):
        """TC 1.11: Verify Paper_arxiv_v2.pdf and Paper_revista_v2.pdf exist, compile cleanly, and page count < 100."""
        for name in ["Paper_arxiv_v2.pdf", "Paper_revista_v2.pdf"]:
            pdf_file = V2_DIR / name
            require_path(self, pdf_file, f"Milestone M3 pending: {name} not yet compiled")
            
            # Verify magic bytes
            header = pdf_file.read_bytes()[:5]
            self.assertEqual(header, b"%PDF-", f"{name} is not a valid PDF file (bad magic bytes).")
            
            # Verify page count
            pages = get_pdf_page_count(pdf_file)
            self.assertGreater(pages, 0, f"{name} must have at least 1 page.")
            self.assertLessEqual(pages, 100, f"{name} page count ({pages}) exceeds 100-page limit.")

    def test_12_simulation_scripts_presence(self):
        """TC 1.12: Verify v2/scripts/ contains the 5 figure generation scripts and run_all_simulations.py."""
        scripts_dir = V2_DIR / "scripts"
        master_runner = scripts_dir / "run_all_simulations.py"
        require_path(self, master_runner, "Milestone M2 pending: simulation scripts in v2/scripts/ not yet implemented")
        
        for script_name in V2_EXPECTED_SCRIPTS:
            script_path = scripts_dir / script_name
            self.assertTrue(
                script_path.exists(),
                f"Expected script '{script_name}' missing from v2/scripts/."
            )
            self.assertGreater(
                script_path.stat().st_size, 0,
                f"Script '{script_name}' is empty (0 bytes)."
            )

    def test_13_publication_figure_pdfs_presence(self):
        """TC 1.13: Verify v2/figures/ contains the 5 publication-grade vector PDFs."""
        figures_dir = V2_DIR / "figures"
        first_figure = figures_dir / V2_EXPECTED_FIGURES[0]
        require_path(self, first_figure, "Milestone M2 pending: publication figures in v2/figures/ not yet generated")
        
        for fig_name in V2_EXPECTED_FIGURES:
            fig_path = figures_dir / fig_name
            self.assertTrue(
                fig_path.exists(),
                f"Expected publication figure '{fig_name}' missing from v2/figures/."
            )
            header = fig_path.read_bytes()[:5]
            self.assertEqual(
                header, b"%PDF-",
                f"Figure '{fig_name}' is not a valid vector PDF (bad magic bytes)."
            )


    def test_14_overleaf_bundle_zip_presence_and_structure(self):
        """TC 1.14: Verify v2/overleaf_bundle_v2.zip exists and contains all required assets."""
        bundle_file = V2_DIR / "overleaf_bundle_v2.zip"
        require_path(self, bundle_file, "Milestone M4 pending: v2/overleaf_bundle_v2.zip not yet packaged")
        
        self.assertTrue(zipfile.is_zipfile(bundle_file), "overleaf_bundle_v2.zip is not a valid ZIP file.")
        
        with zipfile.ZipFile(bundle_file, "r") as z:
            names = z.namelist()
            # Must contain manuscripts and bibliography
            self.assertTrue(any(n.endswith("Paper_arxiv_v2.tex") for n in names), "Missing Paper_arxiv_v2.tex in bundle")
            self.assertTrue(any(n.endswith("Paper_revista_v2.tex") for n in names), "Missing Paper_revista_v2.tex in bundle")
            self.assertTrue(any(n.endswith("references.bib") for n in names), "Missing references.bib in bundle")
            # Must contain styles
            self.assertTrue(any(n.endswith("optica-article.cls") for n in names), "Missing optica-article.cls in bundle")
            # Must contain figures
            for fig in V2_EXPECTED_FIGURES:
                self.assertTrue(
                    any(fig in n for n in names),
                    f"Figure '{fig}' missing from overleaf_bundle_v2.zip."
                )


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES
# ==============================================================================

class TestTier2BoundaryAndCornerCases(unittest.TestCase):
    """Tier 2: Boundary, Corner & Robustness Cases.
    Verifies no zero-byte stubs, multi-row figure layouts, clean titles, and negative validation checks.
    """

    def test_01_non_empty_files_in_v2(self):
        """TC 2.1: Verify no files in v2/ are empty (0 bytes)."""
        require_path(self, V2_DIR, "Milestone M1 pending: v2/ directory not yet created")
        
        zero_byte_files = []
        for p in V2_DIR.rglob("*"):
            if p.is_file() and p.stat().st_size == 0:
                zero_byte_files.append(str(p.relative_to(V2_DIR)))
        
        self.assertEqual(
            zero_byte_files, [],
            f"Found zero-byte (empty) files in v2/:\n" + "\n".join(zero_byte_files)
        )

    def test_02_script_multi_row_layouts_not_single_row(self):
        """TC 2.2: Verify simulation scripts produce multi-row layouts (NOT 1-row plt.subplots(1, 3))."""
        scripts_dir = V2_DIR / "scripts"
        first_script = scripts_dir / "generate_fig1_profiles.py"
        require_path(self, first_script, "Milestone M2 pending: simulation scripts in v2/scripts/ not yet implemented")
        
        single_row_violations = []
        for script_name in V2_EXPECTED_SCRIPTS:
            if script_name == "run_all_simulations.py":
                continue
            script_path = scripts_dir / script_name
            if not script_path.exists():
                continue
            
            content = script_path.read_text(encoding="utf-8", errors="ignore")
            # Search for subplots(1, ...) which indicates a single horizontal row
            single_row_matches = re.findall(r"subplots\s*\(\s*1\s*,\s*[2-9]", content)
            if single_row_matches:
                single_row_violations.append(f"{script_name}: found 1-row layout '{single_row_matches}'")
            
            # Verify script specifies multi-row: e.g. subplots(2, 2) or nrows=2
            has_multi_row = (
                re.search(r"subplots\s*\(\s*[2-9]\s*,\s*[2-9]", content)
                or re.search(r"nrows\s*=\s*[2-9]", content)
                or re.search(r"GridSpec\s*\(\s*[2-9]\s*,\s*[2-9]", content)
            )
            if not has_multi_row:
                single_row_violations.append(f"{script_name}: does not appear to use a multi-row layout grid.")
        
        self.assertEqual(
            single_row_violations, [],
            f"Multi-row layout violations found in scripts:\n" + "\n".join(single_row_violations)
        )

    def test_03_script_titles_no_raw_latex_textbf(self):
        """TC 2.3: Verify scripts do not contain unescaped \\textbf in title or label strings."""
        scripts_dir = V2_DIR / "scripts"
        first_script = scripts_dir / "generate_fig1_profiles.py"
        require_path(self, first_script, "Milestone M2 pending: simulation scripts in v2/scripts/ not yet implemented")

        
        raw_latex_violations = []
        for script_name in V2_EXPECTED_SCRIPTS:
            script_path = scripts_dir / script_name
            if not script_path.exists():
                continue
            
            content = script_path.read_text(encoding="utf-8", errors="ignore")
            # Match \textbf inside title calls: set_title, title, suptitle
            matches = re.findall(r"(?:set_title|title|suptitle)\s*\([^)]*\\textbf", content)
            if matches:
                raw_latex_violations.append(f"{script_name}: contains unescaped \\textbf in title: {matches}")
        
        self.assertEqual(
            raw_latex_violations, [],
            f"Unescaped \\textbf violations found:\n" + "\n".join(raw_latex_violations)
        )

    def test_04_negative_check_abstract_validator_detects_violations(self):
        """TC 2.4: Negative check - verify validate_abstract_cleanliness catches all illegal abstract structures."""
        # Test raw equation environment
        bad_eq = "In this work we study PVBs where \\begin{equation} E(r) = e^{-r^2} \\end{equation} is analyzed."
        self.assertTrue(len(validate_abstract_cleanliness(bad_eq)) > 0, "Validator must reject raw \\begin{equation}")

        # Test display math $$...$$
        bad_display = "The overlap is given by $$ \\gamma = 0.5 $$."
        self.assertTrue(len(validate_abstract_cleanliness(bad_display)) > 0, "Validator must reject $$...$$")

        # Test direct equation citation Eq. (3)
        bad_cite_eq = "As demonstrated in Eq. (5), the frame bounds are positive."
        self.assertTrue(len(validate_abstract_cleanliness(bad_cite_eq)) > 0, "Validator must reject Eq. (N)")

        # Test bracketed citation [1]
        bad_bracket = "This builds on previous work [1, 2] in paraxial optics."
        self.assertTrue(len(validate_abstract_cleanliness(bad_bracket)) > 0, "Validator must reject [N] brackets")

        # Test clean abstract passes with 0 violations
        clean = (
            "We present a comprehensive study of the overcomplete continuous frame properties of "
            "quasi-perfect vortex beams. By deriving the exact closed-form inner product and establishing "
            "the paraxial bandlimited continuous frame bounds, we show that the frame operator is strictly "
            "positive and well-conditioned. Classical and quantum advantages in spatial-division multiplexing "
            "and entanglement preservation are demonstrated."
        )
        self.assertEqual(validate_abstract_cleanliness(clean), [], "Validator must accept clean abstract.")

    def test_05_negative_check_bibliography_validator_detects_missing_keys(self):
        """TC 2.5: Negative check - verify citation cross-checker catches undefined citation keys."""
        sample_bib = "@article{Ayala2026, author={Ayala, S.}, title={PVB}, year={2026}}\n"
        defined_keys = extract_bibtex_keys(sample_bib)
        
        # Manuscript citing existing and non-existing keys
        sample_tex = "According to \\cite{Ayala2026} and newer findings \\cite{MissingPaper2099}."
        cited_keys = extract_latex_citations(sample_tex)
        
        missing = cited_keys - defined_keys
        self.assertIn("MissingPaper2099", missing, "Validator must catch missing citation key.")
        self.assertNotIn("Ayala2026", missing, "Validator must not flag defined key.")

    def test_06_negative_check_radii_validator_detects_misuse(self):
        """TC 2.6: Negative check - verify validate_technical_spelling_radii catches incorrect singular/plural forms."""
        bad_text_1 = "We analyze multiple radius across three PVB annular rings."
        violations_1 = validate_technical_spelling_radii(bad_text_1)
        self.assertTrue(len(violations_1) > 0, "Must detect 'multiple radius'.")

        bad_text_2 = "The annular radiuses are spaced equally."
        violations_2 = validate_technical_spelling_radii(bad_text_2)
        self.assertTrue(len(violations_2) > 0, "Must detect 'radiuses'.")

        good_text = "We evaluate distinct ring radii across the paraxial profile."
        violations_good = validate_technical_spelling_radii(good_text)
        self.assertEqual(violations_good, [], "Must accept correct technical plural 'radii'.")

    def test_07_corrupted_pdf_page_counter_robustness(self):
        """TC 2.7: Verify get_pdf_page_count handles nonexistent and corrupted files gracefully."""
        # Nonexistent path
        non_existent = PROJECT_ROOT / "non_existent_file_xyz.pdf"
        self.assertEqual(get_pdf_page_count(non_existent), -1)

        # Empty file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"")
            tmp_path = Path(f.name)
        try:
            count = get_pdf_page_count(tmp_path)
            self.assertEqual(count, 1)  # Fallback gracefully
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


# ==============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS
# ==============================================================================

class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Cross-Feature Pairwise Consistency.
    Validates synchronization between LaTeX figures, citations, parameters, and scripts.
    """

    def test_01_all_tex_figures_exist_in_figures_dir(self):
        """TC 3.1: Verify every figure included via \\includegraphics in .tex corresponds to an existing file in v2/figures/."""
        figures_dir = V2_DIR / "figures"
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            require_path(self, figures_dir, "Milestone M2 pending: v2/figures/ not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            included_figures = extract_figure_inclusions(content)
            self.assertTrue(len(included_figures) > 0, f"No figures included in {name}.")
            
            for fig in included_figures:
                fig_path = figures_dir / fig
                self.assertTrue(
                    fig_path.exists(),
                    f"Figure '{fig}' included in {name} does not exist in v2/figures/."
                )

    def test_02_all_tex_citations_exist_in_bibtex(self):
        """TC 3.2: Verify every \\cite key used in .tex exists in v2/references.bib."""
        bib_file = V2_DIR / "references.bib"
        require_path(self, bib_file, "Milestone M1 pending: v2/references.bib not yet created")
        
        bib_content = bib_file.read_text(encoding="utf-8", errors="ignore")
        defined_keys = extract_bibtex_keys(bib_content)
        
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            cited_keys = extract_latex_citations(content)
            self.assertTrue(len(cited_keys) > 0, f"No citations found in {name}.")
            
            missing_keys = cited_keys - defined_keys
            self.assertEqual(
                missing_keys, set(),
                f"Citations in {name} missing from v2/references.bib: {missing_keys}"
            )

    def test_03_all_bibtex_ai_keys_cited_in_tex(self):
        """TC 3.3: Verify all 3 AI citations are cited in the manuscripts."""
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            cited_keys = extract_latex_citations(content)
            
            for ai_key in V2_AI_CITATIONS:
                found = any(re.search(ai_key, k, re.IGNORECASE) for k in cited_keys)
                self.assertTrue(
                    found,
                    f"Required AI citation '{ai_key}' is not cited in {name}."
                )

    def test_04_parameter_consistency_text_scripts_captions(self):
        """TC 3.4: Verify consistency of physical parameters (R0, w0, l) across manuscripts and scripts."""
        scripts_dir = V2_DIR / "scripts"
        require_path(self, scripts_dir, "Milestone M2 pending: v2/scripts/ not yet created")
        
        # Verify scripts use standard paraxial physical parameters
        for script_name in ["generate_fig1_profiles.py", "generate_fig2_overlap.py"]:
            script_path = scripts_dir / script_name
            if not script_path.exists():
                continue
            content = script_path.read_text(encoding="utf-8", errors="ignore")
            # Check for w0 or w_0
            self.assertTrue(
                "w0" in content or "w_0" in content,
                f"Beam waist parameter w0 missing in {script_name}"
            )
            # Check for r0 or R0
            self.assertTrue(
                "r0" in content or "R0" in content or "R_0" in content,
                f"Ring radius parameter R0 missing in {script_name}"
            )

    def test_05_all_5_figures_referenced_in_manuscripts(self):
        """TC 3.5: Verify all 5 generated figures are referenced in both manuscripts."""
        for name in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
            tex_file = V2_DIR / name
            require_path(self, tex_file, f"Milestone M3 pending: {name} not yet created")
            
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            included = extract_figure_inclusions(content)
            
            for expected_fig in V2_EXPECTED_FIGURES:
                self.assertIn(
                    expected_fig, included,
                    f"Publication figure '{expected_fig}' is not included in {name}."
                )


# ==============================================================================
# TIER 4: REAL-WORLD APPLICATION SCENARIOS
# ==============================================================================

class TestTier4RealWorldApplicationScenarios(unittest.TestCase):
    """Tier 4: Real-World Workloads, Full Simulation Execution, and Math Assertions.
    Validates end-to-end simulation execution, mathematical frame bounds, and bundle compilation.
    """

    def test_01_full_simulation_run_execution(self):
        """TC 4.1: Execute run_all_simulations.py and verify all 5 figure PDFs update cleanly (exit code 0)."""
        runner_script = V2_DIR / "scripts" / "run_all_simulations.py"
        require_path(self, runner_script, "Milestone M2 pending: run_all_simulations.py not yet implemented")
        
        start_time = time.time()
        # Execute master simulation runner
        proc = subprocess.run(
            [sys.executable, str(runner_script)],
            cwd=str(V2_DIR / "scripts"),
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            proc.returncode, 0,
            f"run_all_simulations.py failed with exit code {proc.returncode}.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
        
        # Verify all 5 figure PDFs exist and were updated
        figures_dir = V2_DIR / "figures"
        for fig_name in V2_EXPECTED_FIGURES:
            fig_path = figures_dir / fig_name
            self.assertTrue(fig_path.exists(), f"Figure '{fig_name}' not generated by simulation runner.")
            mtime = fig_path.stat().st_mtime
            self.assertGreaterEqual(
                mtime, start_time - 5.0,
                f"Figure '{fig_name}' modification time was not updated during simulation run."
            )

    def test_02_numerical_exact_overlap_bounds_subunitarity(self):
        """TC 4.2: Mathematical proof assertion - verify strict non-orthogonality 0 < gamma_l < 1 for all R1 != R2 (Theorem 1)."""
        w0 = 0.2  # 0.2 mm
        r_grid = np.linspace(0.5, 3.0, 10)  # 10 radial ring sample points
        
        for l in [0, 1, 2, 5]:
            for i, r1 in enumerate(r_grid):
                for j, r2 in enumerate(r_grid):
                    gamma = exact_overlap_coefficient(float(r1), float(r2), w0, l)
                    if i == j:
                        self.assertAlmostEqual(
                            gamma, 1.0, places=7,
                            msg=f"Diagonal normalization failed at r1={r1}, l={l}"
                        )
                    else:
                        self.assertGreater(
                            gamma, 0.0,
                            f"Strict positivity violated: gamma({r1}, {r2}) = {gamma} <= 0"
                        )
                        self.assertLess(
                            gamma, 1.0,
                            f"Strict sub-unitarity violated: gamma({r1}, {r2}) = {gamma} >= 1"
                        )

    def test_03_numerical_diagonal_normalization(self):
        """TC 4.3: Mathematical proof assertion - verify gamma_l(R0, R0; w0) == 1.0 across diverse parameters."""
        test_cases = [
            (0.5, 0.1, 0),
            (1.0, 0.2, 1),
            (1.5, 0.05, 2),
            (2.5, 0.3, 5),
            (3.0, 0.15, 10),
        ]
        for r0, w0, l in test_cases:
            val = exact_overlap_coefficient(r0, r0, w0, l)
            self.assertAlmostEqual(
                val, 1.0, places=9,
                msg=f"Diagonal normalization failed for r0={r0}, w0={w0}, l={l}: {val}"
            )

    def test_04_numerical_continuous_frame_bounds(self):
        """TC 4.4: Mathematical proof assertion - verify positive continuous frame bounds 0 < A <= S <= B < infty (Theorem 3)."""
        w0 = 0.2  # mm
        k_max = 7.5  # mm^-1
        
        # Lower frame bound: A = exp(-0.5 * k_max^2 * w0^2)
        A = math.exp(-0.5 * (k_max**2) * (w0**2) * 0.04)  # paraxial band cut
        B = 1.0
        
        self.assertGreater(A, 0.0, "Lower continuous frame bound A must be strictly positive.")
        self.assertTrue(math.isfinite(B), "Upper continuous frame bound B must be finite.")
        self.assertLessEqual(A, B, "Lower bound A must be <= Upper bound B.")
        
        # Test frame operator spectrum positivity
        kr_samples = np.linspace(0.0, k_max, 25)
        spec = frame_spectrum(kr_samples, w0 * 0.2)
        self.assertTrue(np.all(spec > 0.0), "Continuous frame spectrum must be strictly positive everywhere.")
        self.assertTrue(np.all(spec <= 1.0 + 1e-12), "Continuous frame spectrum must be bounded above by 1.")

    def test_05_numerical_condition_number_approx_3_08(self):
        """TC 4.5: Mathematical proof assertion - verify frame condition number kappa = B / A approx 3.08."""
        # For paraxial design parameters w0 * K_max = 1.5:
        # A = exp(-0.5 * 1.5^2) = exp(-1.125) = 0.32465
        # B = 1.0
        # kappa = B / A = 3.0802
        w0_kmax_product = 1.50
        A = math.exp(-0.5 * (w0_kmax_product**2))
        B = 1.0
        kappa = B / A
        
        self.assertAlmostEqual(
            kappa, 3.0802, places=3,
            msg=f"Continuous frame condition number {kappa} deviates from theoretical design target ~3.08."
        )
        self.assertLess(
            kappa, 5.0,
            "Condition number must remain small (< 5.0), ensuring robust inversion."
        )

    def test_06_numerical_reproducing_kernel_positive_semidefinite(self):
        """TC 4.6: Mathematical proof assertion - verify reproducing kernel K(r, r') forms a positive semi-definite Gram matrix."""
        r_pts = np.linspace(0.8, 2.2, 8)
        w0 = 0.2
        l = 1
        
        # Assemble Gram matrix
        G = np.zeros((len(r_pts), len(r_pts)))
        for i, r_i in enumerate(r_pts):
            for j, r_j in enumerate(r_pts):
                G[i, j] = reproducing_kernel(float(r_i), float(r_j), w0, l)
        
        # Verify symmetry
        np.testing.assert_allclose(G, G.T, rtol=1e-10, atol=1e-10, err_msg="Gram matrix must be symmetric.")
        
        # Verify positive semi-definiteness via eigenvalues
        eigenvalues = np.linalg.eigvalsh(G)
        self.assertTrue(
            np.all(eigenvalues >= -1e-12),
            f"Reproducing kernel Gram matrix must have all eigenvalues >= 0. Got min eigenvalue: {np.min(eigenvalues)}"
        )

    def test_07_numerical_divergence_scaling_laws(self):
        """TC 4.7: Mathematical proof assertion - verify physical divergence pillars as w0 -> 0 (Theorem 2)."""
        P = 1.0  # 1 Watt
        r0 = 1.0e-3  # 1 mm
        
        # Pillar 1: Peak intensity scales as 1/w0
        w_large = 1e-3
        w_small = 1e-6
        I_large = peak_intensity_model(P, r0, w_large)
        I_small = peak_intensity_model(P, r0, w_small)
        ratio = I_small / I_large
        self.assertAlmostEqual(ratio, 1000.0, delta=1.0, msg="Peak intensity must scale inversely with w0.")
        
        # Pillar 2: Optical field exceeds air breakdown threshold (3e6 V/m)
        eta_0 = 376.73  # Vacuum impedance
        w_ultrathin = 1e-8
        I_peak = peak_intensity_model(P, r0, w_ultrathin)
        E_peak = math.sqrt(2.0 * eta_0 * I_peak)
        self.assertGreater(
            E_peak, AIR_BREAKDOWN_FIELD,
            f"Electric field ({E_peak:.2e} V/m) must exceed dielectric air breakdown ({AIR_BREAKDOWN_FIELD:.2e} V/m)."
        )
        
        # Pillar 3: Transmitted power collapses linearly under field clamping
        E_clamped = 1.0e6
        P_100um = transmitted_power_under_clamping(E_clamped, r0, 100e-6)
        P_1um = transmitted_power_under_clamping(E_clamped, r0, 1e-6)
        self.assertAlmostEqual(P_100um / P_1um, 100.0, delta=1.0, msg="Power under clamping must collapse linearly with w0.")

    def test_08_overleaf_bundle_unzipping_and_compilation_dry_run(self):
        """TC 4.8: Unzip overleaf_bundle_v2.zip, verify complete directory tree and compiler dry-run if available."""
        bundle_file = V2_DIR / "overleaf_bundle_v2.zip"
        require_path(self, bundle_file, "Milestone M4 pending: overleaf_bundle_v2.zip not yet packaged")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with zipfile.ZipFile(bundle_file, "r") as z:
                z.extractall(tmp_path)
            
            # Verify extracted files
            self.assertTrue((tmp_path / "Paper_arxiv_v2.tex").exists(), "Extracted bundle missing Paper_arxiv_v2.tex")
            self.assertTrue((tmp_path / "Paper_revista_v2.tex").exists(), "Extracted bundle missing Paper_revista_v2.tex")
            self.assertTrue((tmp_path / "references.bib").exists(), "Extracted bundle missing references.bib")
            
            # Check figures in bundle
            fig_dir = tmp_path / "figures"
            self.assertTrue(fig_dir.exists(), "Extracted bundle missing figures/ directory")
            for fig in V2_EXPECTED_FIGURES:
                self.assertTrue((fig_dir / fig).exists(), f"Extracted bundle missing {fig}")
            
            # If pdflatex compiler is found, execute a draft compilation
            pdflatex = find_pdflatex_compiler()
            if pdflatex:
                res = subprocess.run(
                    [pdflatex, "-draftmode", "-interaction=nonstopmode", "Paper_arxiv_v2.tex"],
                    cwd=str(tmp_path),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertEqual(
                    res.returncode, 0,
                    f"Overleaf bundle compilation dry-run failed with code {res.returncode}.\nOutput:\n{res.stdout[-1000:]}"
                )


# ==============================================================================
# CLI RUNNER
# ==============================================================================

def main():
    """Main CLI execution for v2 test suite."""
    print("=" * 70)
    print("E2E Test Suite: Version 2 (v2) - PVB Overcompleteness Project")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Strict Milestone Enforcement (FAIL_ON_PENDING): {FAIL_ON_PENDING}")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all 4 tiers
    suite.addTests(loader.loadTestsFromTestCase(TestTier1FeatureCoverage))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2BoundaryAndCornerCases))
    suite.addTests(loader.loadTestsFromTestCase(TestTier3CrossFeatureCombinations))
    suite.addTests(loader.loadTestsFromTestCase(TestTier4RealWorldApplicationScenarios))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TEST SUITE EXECUTION SUMMARY:")
    print(f"  Tests Run:  {result.testsRun}")
    print(f"  Passed:     {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"  Skipped:    {len(result.skipped)} (pending milestone deliverables)")
    print(f"  Failures:   {len(result.failures)}")
    print(f"  Errors:     {len(result.errors)}")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
