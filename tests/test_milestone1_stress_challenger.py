"""
Empirical Challenger Adversarial Stress Test Suite for Milestone 1.
Agent: challenger_m1_2 (Role: EMPIRICAL CHALLENGER / critic, specialist)

Verifies:
1. Exact matching of titles, authors, publishers, DOIs, ISBNs, and years between:
   - The 3 AI PDFs in Codex Máxima/
   - The Ferreira et al. (2026) paper in Codex Máxima/
   - v2/references.bib
   - v2/RESPUESTAS_REVISION_V2.md
2. Strict UTF-8 encoding, brace balance, syntax integrity, and field completeness of v2/references.bib.
3. Full execution of master E2E regression test runner: exactly 81/81 pass, 0 skips, 0 failures.
4. Comprehensive point-by-point fidelity of v2/RESPUESTAS_REVISION_V2.md for all 7 author revision comments.
"""

import math
import os
import re
import sys
import unittest
from pathlib import Path

import fitz  # PyMuPDF
import pypdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CODEX_DIR = PROJECT_ROOT / "Codex Máxima"
V2_DIR = PROJECT_ROOT / "v2"
REFERENCES_BIB = V2_DIR / "references.bib"
RESPUESTAS_MD = V2_DIR / "RESPUESTAS_REVISION_V2.md"


class TestCodexMaximaAIReferences(unittest.TestCase):
    """Stress-test AI reference PDFs in Codex Máxima against BibTeX and Defense Report."""

    @classmethod
    def setUpClass(cls):
        cls.pdf_jauhiainen = CODEX_DIR / "2026-generative ai for research and thesis work.pdf"
        cls.pdf_paperbanana = CODEX_DIR / "2026-arxiv-PaperBanana  Automating Academic Illustration for AI Scientists.pdf"
        cls.pdf_haber = CODEX_DIR / "2025-Using AI in Academic Writing and Research_ A Complete Guide to Effective and Ethical Academic A.pdf"
        cls.pdf_ferreira = CODEX_DIR / "2026-Second-order moment equivalence of twisted Gaussian Schell model beams and orbital angular momentum eigenmodes.pdf"

        # Read bib file
        cls.bib_text = REFERENCES_BIB.read_text(encoding="utf-8", errors="strict")
        # Read markdown report
        cls.md_text = RESPUESTAS_MD.read_text(encoding="utf-8", errors="strict")

    def test_01_all_pdf_files_exist(self):
        """TC 1.1: Verify all 4 required reference PDFs exist and are accessible."""
        for path in [self.pdf_jauhiainen, self.pdf_paperbanana, self.pdf_haber, self.pdf_ferreira]:
            self.assertTrue(path.exists(), f"Reference PDF does not exist: {path}")
            self.assertGreater(path.stat().st_size, 10000, f"PDF file suspiciously small: {path}")

    def test_02_jauhiainen_pdf_content_matches_bib_and_report(self):
        """TC 1.2: Stress-test Jauhiainen (2026) title, author, publisher, DOI, ISBN, year."""
        doc = fitz.open(self.pdf_jauhiainen)
        self.assertGreaterEqual(len(doc), 200, "Jauhiainen book should have > 200 pages")
        
        # Verify text on copyright / title pages (pages 0-4)
        extracted = " ".join([doc[p].get_text() for p in range(min(5, len(doc)))])
        self.assertIn("Generative AI", extracted)
        self.assertIn("Jussi S. Jauhiainen", extracted)
        self.assertIn("MDPI", extracted)
        self.assertIn("978-3-7258-7921-2", extracted)
        self.assertIn("10.3390/books978-3-7258-7921-2", extracted)
        self.assertIn("2026", extracted)

        # Cross-test against v2/references.bib
        self.assertIn("@book{Jauhiainen2026", self.bib_text)
        self.assertTrue("J. S. Jauhiainen" in self.bib_text or "Jussi S. Jauhiainen" in self.bib_text)
        self.assertIn("Generative {AI} for Research and Thesis Work", self.bib_text)
        self.assertIn("MDPI", self.bib_text)
        self.assertIn("Basel, Switzerland", self.bib_text)
        self.assertIn("10.3390/books978-3-7258-7921-2", self.bib_text)
        self.assertIn("978-3-7258-7921-2", self.bib_text)
        self.assertIn("2026", self.bib_text)

        # Cross-test against v2/RESPUESTAS_REVISION_V2.md
        self.assertIn("Jauhiainen", self.md_text)
        self.assertIn("10.3390/books978-3-7258-7921-2", self.md_text)
        self.assertIn("MDPI", self.md_text)

    def test_03_paperbanana_pdf_content_matches_bib_and_report(self):
        """TC 1.3: Stress-test PaperBanana (2026) title, authors, arXiv ID, DOI, year."""
        doc = fitz.open(self.pdf_paperbanana)
        self.assertGreaterEqual(len(doc), 30, "PaperBanana preprint should have > 30 pages")
        
        # Verify text on page 0
        p0_text = doc[0].get_text()
        self.assertIn("PaperBanana: Automating Academic", p0_text)
        self.assertIn("Dawei Zhu", p0_text)
        self.assertIn("Rui Meng", p0_text)
        self.assertIn("Yale Song", p0_text)
        self.assertIn("Tomas Pfister", p0_text)
        self.assertIn("Jinsung Yoon", p0_text)
        self.assertIn("arXiv:2601.23265", p0_text)

        # Cross-test against v2/references.bib
        self.assertIn("@misc{Zhu2026PaperBanana", self.bib_text)
        self.assertIn("D. Zhu and R. Meng and Y. Song and X. Wei and S. Li and T. Pfister and J. Yoon", self.bib_text)
        self.assertIn("{PaperBanana}: Automating Academic Illustration for {AI} Scientists", self.bib_text)
        self.assertIn("2601.23265", self.bib_text)
        self.assertIn("10.48550/arXiv.2601.23265", self.bib_text)
        self.assertIn("2026", self.bib_text)

        # Cross-test against v2/RESPUESTAS_REVISION_V2.md
        self.assertIn("Zhu2026PaperBanana", self.md_text)
        self.assertIn("PaperBanana", self.md_text)
        self.assertIn("2601.23265", self.md_text)

    def test_04_haber_pdf_content_matches_bib_and_report(self):
        """TC 1.4: Stress-test Haber et al. (2025) title, authors, publisher, DOI, ISBN, year."""
        doc = fitz.open(self.pdf_haber)
        self.assertGreaterEqual(len(doc), 100, "Haber book should have > 100 pages")
        
        # Verify text on pages 0-3
        extracted = " ".join([doc[p].get_text() for p in range(min(5, len(doc)))])
        self.assertIn("Eldar", extracted)
        self.assertIn("Haber", extracted)
        self.assertIn("Dariusz", extracted)
        self.assertIn("Jemielniak", extracted)
        self.assertIn("Artur", extracted)
        self.assertIn("Kurasiński", extracted)
        self.assertIn("Aleksandra", extracted)
        self.assertIn("Przegalińska", extracted)
        self.assertIn("Using AI in Academic Writing and Research", extracted)
        self.assertIn("978-3-031-91705-9", extracted)
        self.assertIn("10.1007/978-3-031-91705-9", extracted)
        self.assertIn("2025", extracted)

        # Cross-test against v2/references.bib
        self.assertIn("@book{Haber2025", self.bib_text)
        self.assertIn("E. Haber", self.bib_text)
        self.assertIn("Using {AI} in Academic Writing and Research", self.bib_text)
        self.assertIn("Palgrave Macmillan", self.bib_text)
        self.assertIn("10.1007/978-3-031-91705-9", self.bib_text)
        self.assertIn("978-3-031-91705-9", self.bib_text)
        self.assertIn("2025", self.bib_text)

        # Cross-test against v2/RESPUESTAS_REVISION_V2.md
        self.assertIn("Haber", self.md_text)
        self.assertIn("10.1007/978-3-031-91705-9", self.md_text)
        self.assertIn("Palgrave Macmillan", self.md_text)

    def test_05_ferreira2026_pdf_matches_bib(self):
        """TC 1.5: Verify Ferreira et al. (2026) metadata fidelity in v2/references.bib."""
        doc = fitz.open(self.pdf_ferreira)
        meta = doc.metadata
        self.assertIn("Second-order moment equivalence of twisted Gaussian Schell model beams", meta.get("title", ""))
        self.assertIn("S Ayala", meta.get("author", ""))

        # In bib:
        self.assertIn("@article{Ferreira2026", self.bib_text)
        self.assertIn("S. Ayala", self.bib_text)
        self.assertIn("10.1088/2040-8986/ae9b1d", self.bib_text)
        self.assertIn("095601", self.bib_text)
        self.assertIn("2026", self.bib_text)


class TestBibTeXParsingAndEncoding(unittest.TestCase):
    """Stress-test v2/references.bib syntax, brace balance, UTF-8 validity, and completeness."""

    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = REFERENCES_BIB.read_bytes()
        cls.text = REFERENCES_BIB.read_text(encoding="utf-8", errors="strict")

    def test_01_strict_utf8_encoding_no_bom(self):
        """TC 2.1: Verify references.bib is valid strict UTF-8 with no BOM and no null bytes."""
        # Check no UTF-8 BOM (\xef\xbb\xbf)
        self.assertFalse(self.raw_bytes.startswith(b"\xef\xbb\xbf"), "references.bib must not contain UTF-8 BOM")
        # Check no null bytes
        self.assertNotIn(b"\x00", self.raw_bytes, "references.bib contains illegal null bytes")
        # Ensure it decodes cleanly in strict mode
        decoded = self.raw_bytes.decode("utf-8", errors="strict")
        # Normalize CRLF for length comparison
        self.assertEqual(len(decoded.replace("\r\n", "\n")), len(self.text.replace("\r\n", "\n")))

    def test_02_global_brace_balance(self):
        """TC 2.2: Verify total opened and closed curly braces are strictly equal."""
        open_count = self.text.count("{")
        close_count = self.text.count("}")
        self.assertEqual(
            open_count,
            close_count,
            f"Mismatched curly braces in references.bib: {open_count} open vs {close_count} close",
        )

    def test_03_bibtex_entry_parsing(self):
        """TC 2.3: Parse every BibTeX entry and check syntax and uniqueness of cite keys."""
        pattern = r"@([a-zA-Z]+)\s*\{\s*([^,]+),"
        entries = re.findall(pattern, self.text)
        self.assertGreaterEqual(len(entries), 25, "Expected at least 25 BibTeX entries in references.bib")

        keys = [k.strip() for _, k in entries]
        self.assertEqual(len(keys), len(set(keys)), f"Duplicate citation keys detected: {[k for k in keys if keys.count(k) > 1]}")

        # Check required foundational entries
        required_keys = [
            "Ferreira2026",
            "Villalba2023",
            "Vaity2015",
            "Ostrovsky2013",
            "Reddy2016",
            "Allen1992",
            "Durnin1987",
            "Duffin1952",
            "Ali1993",
            "Daubechies1990",
            "Jauhiainen2026",
            "Zhu2026PaperBanana",
            "Haber2025",
        ]
        for rk in required_keys:
            self.assertIn(rk, keys, f"Missing critical citation key in references.bib: {rk}")

    def test_04_individual_entry_brace_balance(self):
        """TC 2.4: Verify each individual BibTeX entry is self-contained and balanced."""
        entry_blocks = re.split(r"\n(?=@\w+\s*\{)", self.text)
        for block in entry_blocks:
            block = block.strip()
            if not block:
                continue
            open_b = block.count("{")
            close_b = block.count("}")
            entry_header = block.split("\n")[0][:40]
            self.assertEqual(
                open_b,
                close_b,
                f"Unbalanced braces in entry '{entry_header}': {open_b} open vs {close_b} close",
            )

    def test_05_critical_fields_presence(self):
        """TC 2.5: Verify every entry has title, author/editor."""
        entry_blocks = re.split(r"\n(?=@\w+\s*\{)", self.text)
        for block in entry_blocks:
            block = block.strip()
            if not block:
                continue
            entry_match = re.match(r"@(\w+)\s*\{\s*([^,]+),", block)
            if not entry_match:
                continue
            etype, key = entry_match.group(1).lower(), entry_match.group(2).strip()
            
            # Check title
            self.assertTrue(
                re.search(r"\btitle\s*=", block, re.IGNORECASE),
                f"Entry '{key}' of type @{etype} is missing 'title' field",
            )
            # Check author or editor
            self.assertTrue(
                re.search(r"\b(?:author|editor)\s*=", block, re.IGNORECASE),
                f"Entry '{key}' of type @{etype} is missing 'author' or 'editor' field",
            )


class TestE2ERegressionPassRate(unittest.TestCase):
    """Stress-test the existing master E2E regression runner."""

    def test_01_e2e_runner_execution_81_passed(self):
        """TC 3.1: Execute test_e2e_runner.py and verify 81/81 tests pass with zero errors/skips."""
        from tests.test_e2e_runner import build_suite, CustomTestResult
        from io import StringIO

        suite = build_suite(tier=None)
        self.assertEqual(suite.countTestCases(), 81, f"Expected 81 test cases, found {suite.countTestCases()}")

        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, resultclass=CustomTestResult, verbosity=1)
        result = runner.run(suite)

        self.assertEqual(result.testsRun, 81, f"Expected 81 tests run, got {result.testsRun}")
        self.assertEqual(result.success_count, 81, f"Expected 81 successes, got {result.success_count}")
        self.assertEqual(len(result.failures), 0, f"Failures detected: {result.failures}")
        self.assertEqual(len(result.errors), 0, f"Errors detected: {result.errors}")
        self.assertEqual(len(result.skipped), 0, f"Skipped tests detected: {result.skipped}")


class TestRespuestasRevisionFidelity(unittest.TestCase):
    """Stress-test v2/RESPUESTAS_REVISION_V2.md structure, author metadata, and comments."""

    @classmethod
    def setUpClass(cls):
        cls.md_text = RESPUESTAS_MD.read_text(encoding="utf-8", errors="strict")

    def test_01_author_metadata_fidelity(self):
        """TC 4.1: Verify first author metadata in RESPUESTAS_REVISION_V2.md."""
        self.assertIn("Sebastián Ayala", self.md_text)
        self.assertIn("Investigador Independiente", self.md_text)
        self.assertIn("Cauquenes", self.md_text)
        self.assertIn("Maule", self.md_text)
        self.assertIn("Chile", self.md_text)
        self.assertIn("ayala.phys.ds@gmail.com", self.md_text)
        self.assertIn("0009-0003-7348-3883", self.md_text)

    def test_02_all_seven_comments_covered(self):
        """TC 4.2: Verify all 7 review comments are explicitly addressed with sections."""
        for c in range(1, 8):
            pattern = rf"(?i)COMENTARIO\s+{c}\b"
            self.assertTrue(
                re.search(pattern, self.md_text),
                f"Review comment C{c} not found in RESPUESTAS_REVISION_V2.md",
            )

    def test_03_technical_substance_of_theorems(self):
        """TC 4.3: Verify explicit discussion of Theorems 1, 2, and 3."""
        self.assertIn("Teorema 1", self.md_text)
        self.assertIn("Teorema 2", self.md_text)
        self.assertIn("Teorema 3", self.md_text)
        self.assertIn("Duffin-Schaeffer", self.md_text)
        self.assertIn("3.08", self.md_text)  # condition number kappa
        self.assertIn("8.6 dB", self.md_text)  # RCF coupling advantage
        self.assertIn("IC-POVM", self.md_text)  # quantum tomography
        self.assertIn("RKHS", self.md_text)  # reproducing kernel Hilbert space

    def test_04_no_unresolved_placeholders(self):
        """TC 4.4: Verify no unfinished placeholder markers (TODO, TBD, FIXME, XXX) in defense report."""
        placeholders = re.findall(r"\b(?:TODO|FIXME|XXX|\[TBD\])\b", self.md_text)
        self.assertEqual(len(placeholders), 0, f"Unresolved placeholders found in RESPUESTAS_REVISION_V2.md: {placeholders}")

    def test_05_substantial_length_and_depth(self):
        """TC 4.5: Verify defense report is exhaustive (> 25,000 chars, > 300 lines)."""
        self.assertGreater(len(self.md_text), 25000, f"Report length too short: {len(self.md_text)} chars")
        lines = self.md_text.splitlines()
        self.assertGreater(len(lines), 300, f"Report line count too low: {len(lines)} lines")


class TestPyPDFCorpusIntegrity(unittest.TestCase):
    """Stress-test that pypdf can open, parse, and extract text from all reference PDFs."""

    def test_01_pypdf_opens_all_ai_and_optics_pdfs(self):
        """TC 5.1: pypdf verifies structural integrity, page tree, and unencrypted status."""
        pdfs = [
            CODEX_DIR / "2026-generative ai for research and thesis work.pdf",
            CODEX_DIR / "2026-arxiv-PaperBanana  Automating Academic Illustration for AI Scientists.pdf",
            CODEX_DIR / "2025-Using AI in Academic Writing and Research_ A Complete Guide to Effective and Ethical Academic A.pdf",
            CODEX_DIR / "2026-Second-order moment equivalence of twisted Gaussian Schell model beams and orbital angular momentum eigenmodes.pdf",
        ]
        for p in pdfs:
            self.assertTrue(p.exists(), f"PDF missing: {p}")
            reader = pypdf.PdfReader(str(p))
            self.assertFalse(reader.is_encrypted, f"PDF is encrypted: {p}")
            self.assertGreater(len(reader.pages), 0, f"PDF has 0 pages: {p}")
            # Stress-test text extraction from first 5 pages
            total_text = ""
            for idx in range(min(5, len(reader.pages))):
                page = reader.pages[idx]
                text = page.extract_text()
                self.assertIsNotNone(text, f"extract_text returned None for {p.name} page {idx}")
                total_text += text
            self.assertGreater(len(total_text.strip()), 100, f"First 5 pages in {p.name} extracted negligible text")


if __name__ == "__main__":
    unittest.main()

