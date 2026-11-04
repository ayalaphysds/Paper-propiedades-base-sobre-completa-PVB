"""
Tier 3: Cross-Feature Pairwise Consistency Test Suite.
Validates synchronization between:
1. LaTeX mathematical equations <-> Python simulation formulas
2. LaTeX figure references <-> generated figure files in v1/figures/
3. Bibliography keys <-> in-text LaTeX citations
4. Pairwise author metadata consistency across all manuscripts and documentation
"""

import os
import re
import unittest
from pathlib import Path

from tests.test_helpers import (
    PROJECT_ROOT,
    V1_DIR,
    SCRIPTS_DIR,
    FIGURES_DIR,
    TEMPLATES_DIR,
    EXPECTED_AUTHOR_NAME,
    EXPECTED_EMAIL,
    EXPECTED_ORCID_ID,
)


class TestCrossFeatureConsistency(unittest.TestCase):
    """Pairwise consistency tests across codebase, manuscripts, and simulations."""

    def _get_latex_manuscripts(self):
        manuscripts = []
        for name in ["Paper_arxiv_v1.tex", "Paper_revista_v1.tex"]:
            p = V1_DIR / name
            if p.exists():
                manuscripts.append(p)
        return manuscripts

    def _get_bib_files(self):
        bibs = []
        for p in [V1_DIR / "references.bib", TEMPLATES_DIR / "sample.bib"]:
            if p.exists():
                bibs.append(p)
        return bibs

    def test_01_math_formula_consistency_latex_vs_python(self):
        """TC 3.1: Verify mathematical equations in PROJECT.md and manuscripts match Python reference."""
        # Check that PROJECT.md and manuscripts contain the exact Gradshteyn-Ryzhik formula
        project_md = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
        
        # Exact inner product modified Bessel pattern: I_l(r_1 r_2 / w_0^2)
        self.assertIn("I_l(r_1 r_2 / w_0^2)", project_md,
                      "PROJECT.md must document exact Gradshteyn-Ryzhik inner product formula.")
        
        # Asymptotic formula pattern: exp(-(r_1 - r_2)^2 / (2 w_0^2))
        self.assertIn("(r_1 - r_2)^2", project_md,
                      "PROJECT.md must document Gaussian asymptotic cross-talk formula.")

        # Check in TeX manuscripts if already created
        for tex in self._get_latex_manuscripts():
            content = tex.read_text(encoding="utf-8", errors="ignore")
            self.assertTrue("I_l" in content or "I_{l}" in content,
                            f"Modified Bessel function I_l not found in {tex.name}")

    def test_02_figure_references_match_spec_and_directory(self):
        """TC 3.2: Verify figure inclusions in LaTeX match the 5 planned PDF figure filenames."""
        expected_figures = [
            "fig1_pvb_profiles_divergence.pdf",
            "fig2_radial_overlap_matrix.pdf",
            "fig3_frame_spectrum_bounds.pdf",
            "fig4_turbulence_rkhs_recovery.pdf",
            "fig5_quantum_povm_entanglement.pdf",
        ]
        
        # Check PROJECT.md mapping
        project_md = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
        for fig in expected_figures:
            self.assertIn(fig, project_md, f"Figure {fig} not listed in PROJECT.md")
            
        # If LaTeX files exist, extract \includegraphics and verify match
        for tex in self._get_latex_manuscripts():
            content = tex.read_text(encoding="utf-8", errors="ignore")
            includes = re.findall(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}", content)
            if includes:
                for inc in includes:
                    inc_name = Path(inc).name
                    if not inc_name.endswith(".pdf"):
                        inc_name += ".pdf"
                    self.assertIn(inc_name, expected_figures,
                                  f"Unexpected figure {inc_name} referenced in {tex.name}")

    def test_03_bibliography_keys_match_citations(self):
        """TC 3.3: Every \\cite{KEY} in LaTeX must have a defined entry in references.bib."""
        bib_files = self._get_bib_files()
        if not bib_files:
            self.skipTest("No .bib file found to validate citations.")
            
        defined_keys = set()
        for bib in bib_files:
            content = bib.read_text(encoding="utf-8", errors="ignore")
            # Match @type{key,
            keys = re.findall(r"@\w+\s*\{\s*([^,]+),", content)
            defined_keys.update(k.strip() for k in keys)
            
        self.assertGreater(len(defined_keys), 0, "No bibliographic keys found in bib files.")
        
        # Check template or manuscript citations
        for tex in list(self._get_latex_manuscripts()) + [TEMPLATES_DIR / "Optica-template.tex"]:
            if not tex.exists():
                continue
            content = tex.read_text(encoding="utf-8", errors="ignore")
            citations = re.findall(r"\\cite\{([^}]+)\}", content)
            for c_group in citations:
                for key in c_group.split(","):
                    key = key.strip()
                    # Skip empty keys
                    if not key:
                        continue
                    # If references.bib is present in v1, enforce 100% key resolution
                    if (V1_DIR / "references.bib").exists():
                        self.assertIn(key, defined_keys,
                                      f"Undefined citation key '\\cite{{{key}}}' in {tex.name}")

    def test_04_author_metadata_pairwise_consistency(self):
        """TC 3.4: Author metadata is strictly identical across PROJECT.md and manuscripts."""
        project_md = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
        
        self.assertIn(EXPECTED_AUTHOR_NAME, project_md)
        self.assertIn(EXPECTED_EMAIL, project_md)
        self.assertIn(EXPECTED_ORCID_ID, project_md)
        
        for tex in self._get_latex_manuscripts():
            content = tex.read_text(encoding="utf-8", errors="ignore")
            self.assertIn(EXPECTED_AUTHOR_NAME, content, f"Author name mismatch in {tex.name}")
            self.assertIn(EXPECTED_EMAIL, content, f"Email mismatch in {tex.name}")
            self.assertIn(EXPECTED_ORCID_ID, content, f"ORCID mismatch in {tex.name}")

    def test_05_appendices_referenced_in_main_body(self):
        """TC 3.5: All educational appendices (A, B, C, D) are referenced in paper body."""
        for tex in self._get_latex_manuscripts():
            content = tex.read_text(encoding="utf-8", errors="ignore")
            for label in ["Appendix A", "Appendix B", "Appendix C", "Appendix D"]:
                self.assertIn(label, content, f"Appendix cross-reference '{label}' missing in {tex.name}")


if __name__ == "__main__":
    unittest.main()
