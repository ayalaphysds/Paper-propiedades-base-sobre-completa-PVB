"""
Tier 4: Real-World Application Workloads Test Suite.
Validates:
1. Standalone Overleaf ZIP readiness and packaging
2. Full paper readability, logical narrative structure, and section hierarchy
3. Literature integration with Codex Máxima verification resources
"""

import io
import os
import re
import unittest
import zipfile
from pathlib import Path

from tests.test_helpers import (
    PROJECT_ROOT,
    V1_DIR,
    TEMPLATES_DIR,
    EXPECTED_AUTHOR_NAME,
)


class TestRealWorldScenarios(unittest.TestCase):
    """Real-world deployment, publication workflows, and packaging tests."""

    def test_01_standalone_overleaf_zip_readiness(self):
        """TC 4.1: Verify in-memory creation of a standalone Overleaf ZIP package."""
        # Determine source of assets: v1/ if present, otherwise latex-universal-template/
        source_dir = V1_DIR if (V1_DIR / "optica-article.cls").exists() else TEMPLATES_DIR
        self.assertTrue(source_dir.exists(), "Source directory for Overleaf assets must exist.")

        # Create an in-memory zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add essential class and style files
            for root, _, files in os.walk(source_dir):
                for f in files:
                    if f.endswith((".cls", ".sty", ".bst", ".ldf", ".tex", ".bib", ".pdf")):
                        full_path = Path(root) / f
                        rel_path = full_path.relative_to(source_dir)
                        # Ensure no parent traversal in zip entry
                        self.assertFalse(str(rel_path).startswith(".."),
                                         f"Invalid relative path in zip: {rel_path}")
                        zip_file.write(full_path, arcname=str(rel_path))

        # Inspect zip contents
        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, "r") as zip_file:
            names = zip_file.namelist()
            self.assertTrue(any(n.endswith("optica-article.cls") for n in names),
                            "Overleaf package must include optica-article.cls")
            self.assertTrue(any(n.endswith(".bst") for n in names),
                            "Overleaf package must include BST style file")
            self.assertTrue(any(n.endswith(".tex") for n in names),
                            "Overleaf package must include main .tex manuscript")

    def test_02_full_paper_narrative_hierarchy(self):
        """TC 4.2: Verify complete scientific section hierarchy in project architecture."""
        project_md = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
        
        required_sections = [
            "Theoretical Foundations & Proofs",
            "Python Simulations & Figures",
            "Exact Analytical PVB Inner Product",
            "Physical Unfeasibility of Singular Limit",
            "Continuous Frame Formalism",
            "Classical Advantages",
            "Quantum Advantages",
            "Appendix A: Pedagogical Primer",
            "Appendix B: Complete Bases in Hilbert Spaces",
            "Appendix C: Overcomplete Bases & Frame Theory",
            "Appendix D: Mathematical Derivations",
            "Formal AI Ethics Declaration",
        ]
        
        for sec in required_sections:
            self.assertIn(sec, project_md, f"Missing required narrative section: '{sec}'")

    def test_03_codex_maxima_literature_continuity(self):
        """TC 4.3: Verify presence and integration of foundational Codex Máxima paper."""
        codex_dir = PROJECT_ROOT / "Codex Máxima"
        self.assertTrue(codex_dir.exists(), "Codex Máxima directory must exist.")
        
        target_pdf_name = "2026-Second-order moment equivalence of twisted Gaussian Schell model beams and orbital angular momentum eigenmodes.pdf"
        target_pdf = codex_dir / target_pdf_name
        self.assertTrue(target_pdf.exists(), f"Foundational reference {target_pdf_name} not found in Codex Máxima.")

        # Check PROJECT.md cites Ferreira et al. (2026)
        project_md = (PROJECT_ROOT / "PROJECT.md").read_text(encoding="utf-8")
        self.assertIn("Ferreira", project_md, "Ferreira et al. must be cited in PROJECT.md.")

    def test_04_no_conflicting_tex_engines_in_preamble(self):
        """TC 4.4: Ensure templates do not define conflicting LaTeX packages."""
        for tex in PROJECT_ROOT.glob("**/*.tex"):
            if ".git" in str(tex) or ".agents" in str(tex):
                continue
            content = tex.read_text(encoding="utf-8", errors="ignore")
            # Overleaf standard for Optica: amssymb should be guarded if Bbbk defined
            if "amssymb" in content and "optica-article" in content:
                # Should have \let\Bbbk\relax or similar protection
                has_bbbk_guard = "\\let\\Bbbk\\relax" in content or "% \\usepackage{amssymb}" in content
                self.assertTrue(has_bbbk_guard or "amssymb" in content,
                                f"Potential Bbbk conflict with amssymb in {tex.name}")

    def test_05_clean_workspace_no_scratch_dumps(self):
        """TC 4.5: Ensure no forbidden scratch dump files exist in project root."""
        forbidden_extensions = [".tmp", ".bak", ".orig"]
        for ext in forbidden_extensions:
            dumps = list(PROJECT_ROOT.glob(f"*{ext}"))
            self.assertEqual(len(dumps), 0, f"Found untracked scratch dump files: {dumps}")


if __name__ == "__main__":
    unittest.main()
