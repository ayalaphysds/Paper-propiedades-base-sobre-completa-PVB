"""
Adversarial Stress Test Suite for Milestone 3 Deliverables.
Author: Challenger Agent (challenger_m3_2)
"""

import os
import re
import unittest
from pathlib import Path
import fitz  # PyMuPDF
import pypdf

REPO_ROOT = Path(r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB")
V2_DIR = REPO_ROOT / "v2"

class TestMilestone3AdversarialStress(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.arxiv_tex = V2_DIR / "Paper_arxiv_v2.tex"
        cls.revista_tex = V2_DIR / "Paper_revista_v2.tex"
        cls.arxiv_pdf = V2_DIR / "Paper_arxiv_v2.pdf"
        cls.revista_pdf = V2_DIR / "Paper_revista_v2.pdf"
        cls.arxiv_log = V2_DIR / "Paper_arxiv_v2.log"
        cls.revista_log = V2_DIR / "Paper_revista_v2.log"

    def test_01_manuscript_files_exist_and_non_empty(self):
        """Stress check: Ensure TeX and PDF deliverables exist and are substantial (> 30KB source, > 400KB PDF)."""
        self.assertTrue(self.arxiv_tex.exists(), "Paper_arxiv_v2.tex missing")
        self.assertTrue(self.revista_tex.exists(), "Paper_revista_v2.tex missing")
        self.assertTrue(self.arxiv_pdf.exists(), "Paper_arxiv_v2.pdf missing")
        self.assertTrue(self.revista_pdf.exists(), "Paper_revista_v2.pdf missing")

        # Size stress assertions
        self.assertGreater(self.arxiv_tex.stat().st_size, 30000, "arxiv tex too small")
        self.assertGreater(self.revista_tex.stat().st_size, 30000, "revista tex too small")
        self.assertGreater(self.arxiv_pdf.stat().st_size, 500000, "arxiv pdf too small")
        self.assertGreater(self.revista_pdf.stat().st_size, 400000, "revista pdf too small")

    def test_02_pdf_page_limits_and_text_density(self):
        """Stress check: Verify PDF page count < 100 and no blank pages."""
        for pdf_path in [self.arxiv_pdf, self.revista_pdf]:
            doc = fitz.open(str(pdf_path))
            num_pages = len(doc)
            self.assertGreater(num_pages, 5, f"{pdf_path.name} has too few pages: {num_pages}")
            self.assertLess(num_pages, 100, f"{pdf_path.name} exceeds 100 pages: {num_pages}")
            
            for i, page in enumerate(doc):
                text = page.get_text()
                # Check for completely blank pages
                self.assertGreater(len(text.strip()), 20, f"Page {i+1} in {pdf_path.name} appears blank")
            doc.close()

    def test_03_latex_compilation_logs_no_fatal_errors(self):
        """Stress check: Parse compilation logs for fatal errors and missing glyphs."""
        for log_path in [self.arxiv_log, self.revista_log]:
            if not log_path.exists():
                continue
            with open(log_path, 'r', encoding='latin-1') as f:
                content = f.read()
            
            # Check for fatal errors
            self.assertNotIn("! Emergency stop.", content, f"Emergency stop in {log_path.name}")
            self.assertNotIn("Fatal error occurred", content, f"Fatal error in {log_path.name}")
            
            # Check for missing characters
            missing_chars = re.findall(r"Missing character:.*", content)
            self.assertEqual(len(missing_chars), 0, f"Missing characters found in {log_path.name}: {missing_chars}")
            
            # Check for undefined citations and references
            undef_cites = re.findall(r"LaTeX Warning: Citation `(.*?)` on page .*? undefined", content)
            undef_refs = re.findall(r"LaTeX Warning: Reference `(.*?)` on page .*? undefined", content)
            self.assertEqual(len(undef_cites), 0, f"Undefined citations in {log_path.name}: {undef_cites}")
            self.assertEqual(len(undef_refs), 0, f"Undefined references in {log_path.name}: {undef_refs}")

    def test_04_badbox_tolerances(self):
        """Stress check: Verify that no overfull \\hbox exceeds catastrophic threshold (> 50pt)."""
        for log_path in [self.arxiv_log, self.revista_log]:
            if not log_path.exists():
                continue
            with open(log_path, 'r', encoding='latin-1') as f:
                content = f.read()
            
            overfull_matches = re.findall(r"Overfull \\hbox \(([\d\.]+)pt too wide\) in paragraph at lines (\d+)--(\d+)", content)
            for width_str, start_line, end_line in overfull_matches:
                width = float(width_str)
                # Overfull hbox should not catastrophically clip (> 50 pt)
                self.assertLess(width, 50.0, 
                    f"Catastrophic overfull hbox ({width} pt) at lines {start_line}-{end_line} in {log_path.name}")

    def test_05_document_body_font_embedding(self):
        """Adversarial check: Verify document body pages (non-figure pages) have zero Type 3 bitmapped fonts."""
        for pdf_path in [self.arxiv_pdf, self.revista_pdf]:
            doc = fitz.open(str(pdf_path))
            body_type3_fonts = []
            for i, page in enumerate(doc):
                page_num = i + 1
                # Figure pages are 11 to 15; body text pages are 1-10 and 16+
                if page_num < 11 or page_num > 15:
                    for font in page.get_fonts():
                        font_name = font[3]
                        font_type = font[2]
                        if font_type.lower() == "type3":
                            body_type3_fonts.append((page_num, font_name))
            doc.close()
            self.assertEqual(len(body_type3_fonts), 0, 
                f"Type 3 bitmapped fonts detected in body text of {pdf_path.name}: {body_type3_fonts}")

    def test_06_mathematical_core_symbols_in_source(self):
        """Stress check: Verify mathematical symbols and exact theorem statements in both TeX files."""
        for tex_path in [self.arxiv_tex, self.revista_tex]:
            with open(tex_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Bessel function I_\ell
            self.assertIn(r"I_\ell", content, f"I_\\ell missing in {tex_path.name}")
            self.assertIn(r"I_{\ell_1}", content, f"I_{{\\ell_1}} missing in {tex_path.name}")
            
            # Hilbert space L^2 and paraxial subspace
            self.assertIn(r"L^2(\mathbb{R}^2)", content, f"L^2(R^2) missing in {tex_path.name}")
            self.assertIn(r"\mathcal{H}_{\text{band}}", content, f"H_band missing in {tex_path.name}")
            
            # Frame operator S_w and bounds
            self.assertIn(r"S_w", content, f"S_w missing in {tex_path.name}")
            self.assertIn(r"S_w^{-1}", content, f"S_w^{{-1}} missing in {tex_path.name}")
            self.assertIn(r"\kappa \approx 3.08", content, f"kappa condition number missing in {tex_path.name}")
            
            # Reproducing kernel K
            self.assertIn(r"K(\mathbf{r}, \mathbf{r}')", content, f"K(r, r') missing in {tex_path.name}")
            
            # Seven divergence pillars
            for pillar in ["Pillar I", "Pillar II", "Pillar III", "Pillar IV", "Pillar V", "Pillar VI", "Pillar VII"]:
                self.assertIn(pillar, content, f"{pillar} missing in {tex_path.name}")
                
            # Theorems 1, 2, 3
            self.assertIn(r"\begin{theorem}[Strict Non-Orthogonality of Physical PVBs]", content, f"Theorem 1 missing in {tex_path.name}")
            self.assertIn(r"\begin{theorem}[Physical Unfeasibility of the Dirac Basis Limit]", content, f"Theorem 2 missing in {tex_path.name}")
            self.assertIn(r"\begin{theorem}[Continuous Frame on Paraxial Subspace]", content, f"Theorem 3 missing in {tex_path.name}")

    def test_07_mathematical_content_extracted_from_pdf(self):
        """Empirical check: Verify key mathematical concepts are present in rendered text from PDF."""
        for pdf_path in [self.arxiv_pdf, self.revista_pdf]:
            doc = fitz.open(str(pdf_path))
            full_text = "\n".join([page.get_text() for page in doc])
            doc.close()
            
            expected_terms = [
                "Strict Non-Orthogonality",
                "Physical Unfeasibility",
                "Continuous Frame",
                "Resolution of the Identity",
                "Kronecker delta",
                "Weber",
                "Plancherel",
                "Gram matrix",
                "condition number",
                "Reproducing Kernel",
                "Coherent States",
                "Sebastián Ayala",
                "Cauquenes",
                "0009-0003-7348-3883",
                "Pillar I",
                "Pillar II",
                "Pillar III",
                "Pillar IV",
                "Pillar V",
                "Pillar VI",
                "Pillar VII"
            ]
            for term in expected_terms:
                self.assertIn(term.lower(), full_text.lower(), f"Term '{term}' missing in {pdf_path.name} text")

    def test_08_all_five_figures_embedded_and_valid(self):
        """Stress check: Verify all 5 figure PDFs exist, are valid PDFs, and have embedded images/vectors."""
        fig_names = [
            "fig1_pvb_profiles_divergence.pdf",
            "fig2_radial_overlap_matrix.pdf",
            "fig3_frame_spectrum_bounds.pdf",
            "fig4_turbulence_rkhs_recovery.pdf",
            "fig5_quantum_povm_entanglement.pdf"
        ]
        figures_dir = V2_DIR / "figures"
        for fn in fig_names:
            fp = figures_dir / fn
            self.assertTrue(fp.exists(), f"Figure missing: {fn}")
            self.assertGreater(fp.stat().st_size, 10000, f"Figure too small: {fn}")
            doc = fitz.open(str(fp))
            self.assertEqual(len(doc), 1, f"Figure {fn} has unexpected page count: {len(doc)}")
            page = doc[0]
            text = page.get_text()
            self.assertGreater(len(text), 10, f"Figure {fn} lacks text/labels")
            doc.close()

if __name__ == "__main__":
    unittest.main()
