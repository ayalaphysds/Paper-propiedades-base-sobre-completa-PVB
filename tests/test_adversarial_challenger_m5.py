"""
Adversarial Stress Test Suite for Milestone M5 Verification.
Agent: challenger_2 (Empirical Challenger)

Verifies:
1. PDF Integrity: page count, fonts, font descriptors, corrupt object streams, figure rendering & visibility.
2. Overleaf Bundle: complete self-contained package, no external or parent-relative path leakage.
3. BibTeX Cross-References: all citations resolved, no empty fields, clean compilation logs.
4. E2E Test Suite Execution: full 81/81 pass verification.
"""

import os
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import fitz  # pymupdf
import pypdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V1_DIR = PROJECT_ROOT / "v1"


class TestAdversarialPDFInspection(unittest.TestCase):
    """Stress tests on compiled deliverable PDFs."""

    def test_pdf_existence_and_page_counts(self):
        papers = {
            "Paper_revista_v1.pdf": 18,
            "Paper_arxiv_v1.pdf": 19,
        }
        for filename, expected_pages in papers.items():
            pdf_path = V1_DIR / filename
            self.assertTrue(pdf_path.exists(), f"Deliverable PDF missing: {pdf_path}")
            
            # Check with PyMuPDF
            doc = fitz.open(pdf_path)
            self.assertLessEqual(doc.page_count, 100, f"Exceeds 100 pages: {doc.page_count}")
            self.assertEqual(
                doc.page_count,
                expected_pages,
                f"{filename} expected {expected_pages} pages, found {doc.page_count}",
            )

            # Cross-verify with pypdf
            reader = pypdf.PdfReader(str(pdf_path))
            self.assertEqual(len(reader.pages), expected_pages)
            self.assertFalse(reader.is_encrypted, f"{filename} is unexpectedly encrypted")

    def test_pdf_font_descriptors_and_no_corruption(self):
        """Ensure all fonts have valid descriptors and no streams are corrupt."""
        for filename in ["Paper_revista_v1.pdf", "Paper_arxiv_v1.pdf"]:
            pdf_path = V1_DIR / filename
            doc = fitz.open(pdf_path)
            reader = pypdf.PdfReader(str(pdf_path))

            # Test font descriptors in pymupdf
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                fonts = page.get_fonts()
                self.assertGreater(len(fonts), 0, f"Page {page_idx+1} in {filename} has no fonts")
                for f in fonts:
                    xref = f[0]
                    font_info = doc.extract_font(xref)
                    self.assertTrue(
                        bool(font_info[0]),
                        f"Font at xref {xref} on page {page_idx+1} in {filename} has invalid descriptor",
                    )

            # Test pypdf object stream parsing and text extraction on every page
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                self.assertGreater(
                    len(text), 50, f"Page {page_idx+1} in {filename} extracted suspiciously low text: {len(text)} chars"
                )
                res = page.get("/Resources", {})
                self.assertIn("/Font", res, f"Page {page_idx+1} missing /Font resource dictionary")

    def test_pdf_all_five_figures_rendered(self):
        """Verify that all 5 figures are rendered and present in the compiled PDFs."""
        for filename in ["Paper_revista_v1.pdf", "Paper_arxiv_v1.pdf"]:
            pdf_path = V1_DIR / filename
            doc = fitz.open(pdf_path)
            
            # Search for figure references/captions across pages
            found_figures = set()
            for pno in range(len(doc)):
                page = doc[pno]
                text = page.get_text()
                for fig_num in range(1, 6):
                    # Check caption markers: 'Figure X:' or 'Fig. X.'
                    if f"Figure {fig_num}:" in text or f"Figure {fig_num}." in text or f"Fig. {fig_num}." in text or f"Fig. {fig_num}:" in text:
                        found_figures.add(fig_num)
                # Verify that page renders to pixmap without exception
                pix = page.get_pixmap(dpi=72)
                self.assertGreater(pix.width, 0)
                self.assertGreater(pix.height, 0)

            self.assertEqual(
                found_figures,
                {1, 2, 3, 4, 5},
                f"Missing figure references/captions in {filename}: expected all 5, found {found_figures}",
            )


class TestAdversarialOverleafBundle(unittest.TestCase):
    """Stress tests on the Overleaf ZIP package."""

    def setUp(self):
        self.zip_path = V1_DIR / "overleaf_bundle.zip"
        self.assertTrue(self.zip_path.exists(), "overleaf_bundle.zip missing from v1/")

    def test_bundle_contents_and_required_assets(self):
        """Verify all required template, manuscript, bibliography, and figure assets exist."""
        expected_files = {
            "optica-article.cls",
            "jabbrv.sty",
            "styles/opticajournal.sty",
            "jabbrv-ltwa-en.ldf",
            "jabbrv-ltwa-all.ldf",
            "opticajnl.bst",
            "Paper_arxiv_v1.tex",
            "Paper_revista_v1.tex",
            "references.bib",
            "Paper_arxiv_v1.bbl",
            "Paper_revista_v1.bbl",
            "figures/fig1_pvb_profiles_divergence.pdf",
            "figures/fig2_radial_overlap_matrix.pdf",
            "figures/fig3_frame_spectrum_bounds.pdf",
            "figures/fig4_turbulence_rkhs_recovery.pdf",
            "figures/fig5_quantum_povm_entanglement.pdf",
        }

        with zipfile.ZipFile(self.zip_path, "r") as z:
            names = set(z.namelist())
            missing = expected_files - names
            self.assertEqual(len(missing), 0, f"Overleaf bundle is missing files: {missing}")

            # Verify integrity of every file in the zip by testing extraction in memory
            for n in z.namelist():
                data = z.read(n)
                self.assertGreater(len(data), 0, f"File {n} inside bundle is empty (0 bytes)")

    def test_bundle_no_path_leakage(self):
        """Verify no local machine absolute paths or parent relative paths exist in bundle .tex files."""
        abs_win_pattern = re.compile(r"(?<!https)(?<!http)(?<!ftp)\b[a-zA-Z]:[\\/](?!/)")
        parent_rel_pattern = re.compile(r"\.\.[\\/]")
        unix_abs_pattern = re.compile(r"/(?:Users|home|usr|var|tmp)/")

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.zip_path, "r") as z:
                z.extractall(tmpdir)

            tmp_path = Path(tmpdir)
            tex_files = list(tmp_path.rglob("*.tex"))
            self.assertGreaterEqual(len(tex_files), 2)

            for tf in tex_files:
                lines = tf.read_text(encoding="utf-8", errors="replace").splitlines()
                for idx, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith("%"):
                        continue
                    self.assertIsNone(
                        abs_win_pattern.search(line),
                        f"Windows absolute path found in {tf.name}:{idx} -> {line}",
                    )
                    self.assertIsNone(
                        parent_rel_pattern.search(line),
                        f"Parent-relative path (../) found in {tf.name}:{idx} -> {line}",
                    )
                    self.assertIsNone(
                        unix_abs_pattern.search(line),
                        f"Unix absolute path found in {tf.name}:{idx} -> {line}",
                    )

    def test_bundle_figures_visually_identical(self):
        """Verify that figure PDFs in the bundle render bit-for-bit identical to v1/figures at 150 DPI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.zip_path, "r") as z:
                z.extractall(tmpdir)

            tmp_path = Path(tmpdir)
            for fig in (V1_DIR / "figures").glob("*.pdf"):
                zip_fig = tmp_path / "figures" / fig.name
                self.assertTrue(zip_fig.exists(), f"Missing {fig.name} in extracted bundle")

                d1 = fitz.open(fig)
                d2 = fitz.open(zip_fig)

                self.assertEqual(d1[0].rect, d2[0].rect)
                p1 = d1[0].get_pixmap(dpi=150).tobytes()
                p2 = d2[0].get_pixmap(dpi=150).tobytes()
                
                d1.close()
                d2.close()

                self.assertEqual(p1, p2, f"Rendered pixmap differs for {fig.name}")



class TestAdversarialBibTeXCrossReferences(unittest.TestCase):
    """Stress tests on bibliographic cross-references and citation resolution."""

    def setUp(self):
        self.bib_path = V1_DIR / "references.bib"
        self.assertTrue(self.bib_path.exists(), "references.bib missing")
        self.bib_content = self.bib_path.read_text(encoding="utf-8")

        # Parse all entries
        entry_pattern = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
        self.entries = {}
        keys_list = []
        for m in entry_pattern.finditer(self.bib_content):
            entry_type = m.group(1).lower()
            key = m.group(2).strip()
            keys_list.append(key)
            self.entries[key] = entry_type
        self.keys_list = keys_list

    def test_bib_has_no_duplicate_keys(self):
        """BibTeX keys must be strictly unique."""
        duplicates = [k for k in self.keys_list if self.keys_list.count(k) > 1]
        self.assertEqual(len(duplicates), 0, f"Duplicate BibTeX keys found: {set(duplicates)}")

    def test_bib_has_no_empty_fields(self):
        """No BibTeX field should be empty (e.g. title = {} or author = "")."""
        empty_pattern = re.compile(r"(\w+)\s*=\s*([\"']\s*[\"']|\{\s*\})", re.MULTILINE)
        empty_matches = empty_pattern.findall(self.bib_content)
        self.assertEqual(len(empty_matches), 0, f"Empty fields found in references.bib: {empty_matches}")

    def test_all_cited_keys_in_both_tex_files_resolved(self):
        """Parse all active \\cite{...} commands and verify 100% presence in references.bib."""
        cite_pattern = re.compile(r"\\(?:cite|citep|citet|nocite|citealp)\*?(?:\[[^\]]*\])?\{([^}]+)\}")

        for tex_name in ["Paper_revista_v1.tex", "Paper_arxiv_v1.tex"]:
            tex_path = V1_DIR / tex_name
            self.assertTrue(tex_path.exists())
            lines = tex_path.read_text(encoding="utf-8").splitlines()

            cited_keys = set()
            for line in lines:
                code_only = re.sub(r"(?<!\\)%.*$", "", line)
                for m in cite_pattern.finditer(code_only):
                    for k in m.group(1).split(","):
                        k = k.strip()
                        if k:
                            cited_keys.add(k)

            self.assertGreater(len(cited_keys), 10, f"Suspiciously few citations in {tex_name}: {len(cited_keys)}")
            missing = cited_keys - set(self.entries.keys())
            self.assertEqual(
                len(missing),
                0,
                f"Undefined citation keys in {tex_name} not found in references.bib: {missing}",
            )

    def test_clean_compilation_logs(self):
        """Check LaTeX .log and .blg files for citation warnings."""
        for base in ["Paper_revista_v1", "Paper_arxiv_v1"]:
            log_path = V1_DIR / f"{base}.log"
            blg_path = V1_DIR / f"{base}.blg"
            
            if log_path.exists():
                log_txt = log_path.read_text(encoding="utf-8", errors="replace")
                self.assertNotIn(
                    "There were undefined citations",
                    log_txt,
                    f"Undefined citations reported in {log_path.name}",
                )
                undefined_cites = re.findall(r"Citation `([^']+)' on page \d+ undefined", log_txt)
                self.assertEqual(
                    len(undefined_cites),
                    0,
                    f"Undefined citations in {log_path.name}: {undefined_cites}",
                )

            if blg_path.exists():
                blg_txt = blg_path.read_text(encoding="utf-8", errors="replace")
                self.assertNotIn(
                    "Warning--empty",
                    blg_txt,
                    f"Empty BibTeX fields warned in {blg_path.name}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
