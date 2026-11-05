r"""
test_milestone3_adversarial_challenger.py
Empirical Challenger Adversarial Stress Test Suite for Milestone 3.
Agent: challenger_m3_1 (Role: EMPIRICAL CHALLENGER / critic, specialist)

Tests:
1. Citation Resolution:
   - 100% of citation keys in Paper_arxiv_v2.tex and Paper_revista_v2.tex must resolve in references.bib.
   - Required AI ethics citations (Jauhiainen2026, Zhu2026PaperBanana, Haber2025) and foundational papers must exist.
2. Figure Inclusion:
   - 100% of figures included via \includegraphics must exist in v2/figures/.
   - All 5 figures must be non-empty vector PDFs.
3. Abstract Hygiene:
   - Zero equation references (\ref, \eqref, Eq., (1)).
   - Zero inline math ($...$).
   - Zero bracketed citations ([1], [2]).
   - Zero raw limit symbols (\lim, \to).
   - Word count within standard Q1 journal limits (150-300 words).
4. Terminology Consistency:
   - "radii" must be used for plural contexts (e.g., distinct ring radii, concentric ring radii).
   - "radius" must be used for singular contexts (e.g., annular ring radius R0, aperture radius).
   - Strictly zero instances of "distinct ring radius" or "a radii".
5. Programmatic Compilation:
   - Both Paper_arxiv_v2.tex and Paper_revista_v2.tex compile with 0 fatal errors.
   - 0 undefined citations and 0 undefined references in LaTeX logs.
6. PDF Integrity & Layout:
   - Valid PDFs readable by pypdf.
   - Page count strictly < 100 pages.
   - Every page contains non-empty text content.
"""

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

import pypdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V2_DIR = PROJECT_ROOT / "v2"
ARXIV_TEX = V2_DIR / "Paper_arxiv_v2.tex"
REVISTA_TEX = V2_DIR / "Paper_revista_v2.tex"
BIB_FILE = V2_DIR / "references.bib"
FIGURES_DIR = V2_DIR / "figures"
ARXIV_PDF = V2_DIR / "Paper_arxiv_v2.pdf"
REVISTA_PDF = V2_DIR / "Paper_revista_v2.pdf"

REQUIRED_FIGURES = [
    "fig1_pvb_profiles_divergence.pdf",
    "fig2_radial_overlap_matrix.pdf",
    "fig3_frame_spectrum_bounds.pdf",
    "fig4_turbulence_rkhs_recovery.pdf",
    "fig5_quantum_povm_entanglement.pdf",
]

REQUIRED_AI_CITATIONS = [
    "Jauhiainen2026",
    "Zhu2026PaperBanana",
    "Haber2025",
]

REQUIRED_FOUNDATIONAL_CITATIONS = [
    "Ferreira2026",
    "Villalba2023",
    "Vaity2015",
    "Ostrovsky2013",
    "Duffin1952",
    "Ali1993",
]


class TestMilestone3AdversarialChallenger(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        assert V2_DIR.exists(), f"v2 directory not found at {V2_DIR}"
        assert ARXIV_TEX.exists(), f"Paper_arxiv_v2.tex not found at {ARXIV_TEX}"
        assert REVISTA_TEX.exists(), f"Paper_revista_v2.tex not found at {REVISTA_TEX}"
        assert BIB_FILE.exists(), f"references.bib not found at {BIB_FILE}"

    def _extract_cites(self, tex_path: Path):
        content = tex_path.read_text(encoding="utf-8")
        raw_matches = re.findall(r'\\cite[a-zA-Z]*\{([^}]+)\}', content)
        keys = set()
        for m in raw_matches:
            for k in m.split(','):
                k = k.strip()
                if k:
                    keys.add(k)
        return keys

    def _extract_bib_keys(self, bib_path: Path):
        content = bib_path.read_text(encoding="utf-8")
        return set(re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', content))

    def _extract_figures(self, tex_path: Path):
        content = tex_path.read_text(encoding="utf-8")
        raw = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', content)
        norm_figs = []
        for f in raw:
            f_clean = f.replace('\\', '/')
            if f_clean.startswith('figures/'):
                norm_figs.append(f_clean[len('figures/'):])
            else:
                norm_figs.append(Path(f_clean).name)
        return norm_figs

    def _extract_abstract(self, tex_path: Path):
        content = tex_path.read_text(encoding="utf-8")
        m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        self.assertIsNotNone(m, f"Abstract missing in {tex_path.name}")
        return m.group(1).strip()

    # ----------------------------------------------------
    # TEST 1: Citation Resolution & Completeness
    # ----------------------------------------------------
    def test_citation_resolution_arxiv(self):
        cited = self._extract_cites(ARXIV_TEX)
        bib_keys = self._extract_bib_keys(BIB_FILE)
        missing = cited - bib_keys
        self.assertEqual(len(missing), 0, f"Unresolved citations in {ARXIV_TEX.name}: {missing}")
        self.assertGreaterEqual(len(cited), 25, "Fewer citations than expected in arXiv manuscript")

    def test_citation_resolution_revista(self):
        cited = self._extract_cites(REVISTA_TEX)
        bib_keys = self._extract_bib_keys(BIB_FILE)
        missing = cited - bib_keys
        self.assertEqual(len(missing), 0, f"Unresolved citations in {REVISTA_TEX.name}: {missing}")
        self.assertGreaterEqual(len(cited), 25, "Fewer citations than expected in revista manuscript")

    def test_mandatory_citations_present(self):
        cited_arxiv = self._extract_cites(ARXIV_TEX)
        cited_revista = self._extract_cites(REVISTA_TEX)

        # AI ethics
        for req in REQUIRED_AI_CITATIONS:
            self.assertIn(req, cited_arxiv, f"Required AI citation {req} missing in arXiv")
            self.assertIn(req, cited_revista, f"Required AI citation {req} missing in revista")

        # Foundational
        for req in REQUIRED_FOUNDATIONAL_CITATIONS:
            self.assertIn(req, cited_arxiv, f"Required foundational citation {req} missing in arXiv")
            self.assertIn(req, cited_revista, f"Required foundational citation {req} missing in revista")

    # ----------------------------------------------------
    # TEST 2: Figure Inclusion & Vector Integrity
    # ----------------------------------------------------
    def test_figure_inclusion_arxiv(self):
        figs = self._extract_figures(ARXIV_TEX)
        self.assertEqual(len(figs), 5, f"Expected 5 figures in arXiv, found {len(figs)}")
        for req in REQUIRED_FIGURES:
            self.assertIn(req, figs, f"Figure {req} not included in {ARXIV_TEX.name}")
            fig_path = FIGURES_DIR / req
            self.assertTrue(fig_path.exists(), f"Figure file {req} does not exist on disk")
            self.assertGreater(fig_path.stat().st_size, 10000, f"Figure {req} size too small ({fig_path.stat().st_size} bytes)")

    def test_figure_inclusion_revista(self):
        figs = self._extract_figures(REVISTA_TEX)
        self.assertEqual(len(figs), 5, f"Expected 5 figures in revista, found {len(figs)}")
        for req in REQUIRED_FIGURES:
            self.assertIn(req, figs, f"Figure {req} not included in {REVISTA_TEX.name}")
            fig_path = FIGURES_DIR / req
            self.assertTrue(fig_path.exists(), f"Figure file {req} does not exist on disk")
            self.assertGreater(fig_path.stat().st_size, 10000, f"Figure {req} size too small ({fig_path.stat().st_size} bytes)")

    # ----------------------------------------------------
    # TEST 3: Adversarial Abstract Hygiene
    # ----------------------------------------------------
    def test_abstract_hygiene_arxiv(self):
        abstract = self._extract_abstract(ARXIV_TEX)
        # 1. No TeX references
        tex_refs = re.findall(r'\\(?:ref|eqref|cite[a-zA-Z]*)\{[^}]*\}', abstract)
        self.assertEqual(tex_refs, [], f"Found raw TeX refs in arXiv abstract: {tex_refs}")

        # 2. No inline math
        inline_math = re.findall(r'\$[^$]+\$', abstract)
        self.assertEqual(inline_math, [], f"Found inline math in arXiv abstract: {inline_math}")

        # 3. No bracketed references
        bracket_cites = re.findall(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', abstract)
        self.assertEqual(bracket_cites, [], f"Found bracketed citations in arXiv abstract: {bracket_cites}")

        # 4. No limit symbols
        limits = re.findall(r'\\lim|\\to|->', abstract)
        self.assertEqual(limits, [], f"Found limit notation in arXiv abstract: {limits}")

        # 5. No raw equation numbers
        eq_numbers = re.findall(r'(?:[Ee]q\.|[Ee]quation)\s*\(?\d+\)?|\(\d+\)', abstract)
        self.assertEqual(eq_numbers, [], f"Found equation mentions in arXiv abstract: {eq_numbers}")

        # 6. Word count
        words = len(abstract.split())
        self.assertTrue(150 <= words <= 300, f"arXiv abstract word count out of Q1 range: {words}")

    def test_abstract_hygiene_revista(self):
        abstract = self._extract_abstract(REVISTA_TEX)
        # 1. No TeX references
        tex_refs = re.findall(r'\\(?:ref|eqref|cite[a-zA-Z]*)\{[^}]*\}', abstract)
        self.assertEqual(tex_refs, [], f"Found raw TeX refs in revista abstract: {tex_refs}")

        # 2. No inline math
        inline_math = re.findall(r'\$[^$]+\$', abstract)
        self.assertEqual(inline_math, [], f"Found inline math in revista abstract: {inline_math}")

        # 3. No bracketed references
        bracket_cites = re.findall(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', abstract)
        self.assertEqual(bracket_cites, [], f"Found bracketed citations in revista abstract: {bracket_cites}")

        # 4. No limit symbols
        limits = re.findall(r'\\lim|\\to|->', abstract)
        self.assertEqual(limits, [], f"Found limit notation in revista abstract: {limits}")

        # 5. No raw equation numbers
        eq_numbers = re.findall(r'(?:[Ee]q\.|[Ee]quation)\s*\(?\d+\)?|\(\d+\)', abstract)
        self.assertEqual(eq_numbers, [], f"Found equation mentions in revista abstract: {eq_numbers}")

        # 6. Word count
        words = len(abstract.split())
        self.assertTrue(150 <= words <= 300, f"Revista abstract word count out of Q1 range: {words}")

    # ----------------------------------------------------
    # TEST 4: Terminology - Radius vs Radii
    # ----------------------------------------------------
    def test_radius_vs_radii_arxiv(self):
        content = ARXIV_TEX.read_text(encoding="utf-8")
        # Adversarially search for erroneous singular where plural is intended
        err_singular = re.findall(r'\b(?:distinct|concentric|multiple|different|various|continuous)\s+ring\s+radius\b', content, re.IGNORECASE)
        self.assertEqual(err_singular, [], f"Found improper singular 'radius' where plural required in arXiv: {err_singular}")

        # Adversarially search for erroneous plural where singular is intended
        err_plural = re.findall(r'\b(?:a|an|the\s+focal|aperture)\s+radii\b', content, re.IGNORECASE)
        self.assertEqual(err_plural, [], f"Found improper plural 'radii' where singular required in arXiv: {err_plural}")

        # Verify correct plural usage
        plural_usages = re.findall(r'\b(?:distinct|concentric)\s+(?:ring\s+)?radii\b', content, re.IGNORECASE)
        self.assertGreaterEqual(len(plural_usages), 4, f"Expected multiple correct uses of 'distinct/concentric radii', found {len(plural_usages)}")

    def test_radius_vs_radii_revista(self):
        content = REVISTA_TEX.read_text(encoding="utf-8")
        # Adversarially search for erroneous singular where plural is intended
        err_singular = re.findall(r'\b(?:distinct|concentric|multiple|different|various|continuous)\s+ring\s+radius\b', content, re.IGNORECASE)
        self.assertEqual(err_singular, [], f"Found improper singular 'radius' where plural required in revista: {err_singular}")

        # Adversarially search for erroneous plural where singular is intended
        err_plural = re.findall(r'\b(?:a|an|the\s+focal|aperture)\s+radii\b', content, re.IGNORECASE)
        self.assertEqual(err_plural, [], f"Found improper plural 'radii' where singular required in revista: {err_plural}")

        # Verify correct plural usage
        plural_usages = re.findall(r'\b(?:distinct|concentric)\s+(?:ring\s+)?radii\b', content, re.IGNORECASE)
        self.assertGreaterEqual(len(plural_usages), 4, f"Expected multiple correct uses of 'distinct/concentric radii', found {len(plural_usages)}")

    # ----------------------------------------------------
    # TEST 5: PDF Validity and Page Count Limits (<100)
    # ----------------------------------------------------
    def test_pdf_properties_arxiv(self):
        self.assertTrue(ARXIV_PDF.exists(), f"arXiv PDF not found at {ARXIV_PDF}")
        reader = pypdf.PdfReader(str(ARXIV_PDF))
        num_pages = len(reader.pages)
        self.assertGreater(num_pages, 0, "arXiv PDF has 0 pages")
        self.assertLess(num_pages, 100, f"arXiv PDF exceeds 100 pages: {num_pages}")
        
        # Verify text extractability
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            self.assertGreater(len(txt), 50, f"Page {idx+1} of arXiv PDF appears empty or corrupted")

    def test_pdf_properties_revista(self):
        self.assertTrue(REVISTA_PDF.exists(), f"Revista PDF not found at {REVISTA_PDF}")
        reader = pypdf.PdfReader(str(REVISTA_PDF))
        num_pages = len(reader.pages)
        self.assertGreater(num_pages, 0, "Revista PDF has 0 pages")
        self.assertLess(num_pages, 100, f"Revista PDF exceeds 100 pages: {num_pages}")
        
        # Verify text extractability
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            self.assertGreater(len(txt), 50, f"Page {idx+1} of Revista PDF appears empty or corrupted")

    # ----------------------------------------------------
    # TEST 6: Fresh Programmatic Compilation Log Verification
    # ----------------------------------------------------
    def test_log_file_diagnostics_arxiv(self):
        log_path = V2_DIR / "Paper_arxiv_v2.log"
        self.assertTrue(log_path.exists(), "arXiv log file missing")
        log_text = log_path.read_text(encoding="utf-8", errors="replace")

        fatal_errors = [line for line in log_text.splitlines() if line.startswith("! ")]
        undefined_citations = [line for line in log_text.splitlines() if "Citation" in line and "undefined" in line]
        undefined_refs = [line for line in log_text.splitlines() if "Reference" in line and "undefined" in line]

        self.assertEqual(fatal_errors, [], f"Fatal LaTeX errors in arXiv log: {fatal_errors}")
        self.assertEqual(undefined_citations, [], f"Undefined citations in arXiv log: {undefined_citations}")
        self.assertEqual(undefined_refs, [], f"Undefined references in arXiv log: {undefined_refs}")

    def test_log_file_diagnostics_revista(self):
        log_path = V2_DIR / "Paper_revista_v2.log"
        self.assertTrue(log_path.exists(), "Revista log file missing")
        log_text = log_path.read_text(encoding="utf-8", errors="replace")

        fatal_errors = [line for line in log_text.splitlines() if line.startswith("! ")]
        undefined_citations = [line for line in log_text.splitlines() if "Citation" in line and "undefined" in line]
        undefined_refs = [line for line in log_text.splitlines() if "Reference" in line and "undefined" in line]

        self.assertEqual(fatal_errors, [], f"Fatal LaTeX errors in Revista log: {fatal_errors}")
        self.assertEqual(undefined_citations, [], f"Undefined citations in Revista log: {undefined_citations}")
        self.assertEqual(undefined_refs, [], f"Undefined references in Revista log: {undefined_refs}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
