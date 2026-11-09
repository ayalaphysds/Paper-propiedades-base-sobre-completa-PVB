"""
Adversarial Challenger Verification Suite (v4.2)
Specialist & Critic Adversarial Test Suite for PVB Version 4.

Focus:
1. Hostile Sanitization Scan (TeX, BibTeX, Python scripts, Logs, Overleaf Zip, and PDF rendered text).
2. Baseline Protection & Git Status (v1, v2, v3 100% untouched).
3. Citation Parity & Completeness (70/70 keys exact correspondence, zero unreferenced, zero missing).
4. Compiler Undefined References / Log Grep (0 warnings, 0 undefined references, 0 '?').
"""

import os
import re
import subprocess
import unittest
import zipfile
from pathlib import Path
import fitz  # PyMuPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V4_DIR = PROJECT_ROOT / "v4"

class TestAdversarialSanitization(unittest.TestCase):
    """Hostile Sanitization Scan across all deliverables in v4/."""

    FORBIDDEN_PATTERNS = [
        # Project codenames & internal folders
        (r"Codex[-\s]M[aá]xima", re.compile(r"Codex[-\s]M[aá]xima", re.IGNORECASE)),
        (r"\bCodex\b", re.compile(r"\bCodex\b", re.IGNORECASE)),
        (r"\.agents\b", re.compile(r"\.agents\b", re.IGNORECASE)),
        (r"latex-length-check", re.compile(r"latex-length-check", re.IGNORECASE)),
        (r"latex-supplemental-document", re.compile(r"latex-supplemental-document", re.IGNORECASE)),
        (r"latex-universal-template", re.compile(r"latex-universal-template", re.IGNORECASE)),
        
        # Multi-agent bot handles and codenames
        (r"\bminer_lit(_\d+)?\b", re.compile(r"\bminer_lit(_\d+)?\b", re.IGNORECASE)),
        (r"\bworker_arxiv_m2\b", re.compile(r"\bworker_arxiv_m2\b", re.IGNORECASE)),
        (r"\bworker_revista_m2\b", re.compile(r"\bworker_revista_m2\b", re.IGNORECASE)),
        (r"\bworker_m\d(_v\d+)?\b", re.compile(r"\bworker_m\d(_v\d+)?\b", re.IGNORECASE)),
        (r"\bchallenger_v\d+(_\d+)?\b", re.compile(r"\bchallenger_v\d+(_\d+)?\b", re.IGNORECASE)),
        (r"\bchallenger_\w+\b", re.compile(r"\bchallenger_\w+\b", re.IGNORECASE)),
        (r"\bcritic_referee\b", re.compile(r"\bcritic_referee\b", re.IGNORECASE)),
        (r"\bvictory_auditor\b", re.compile(r"\bvictory_auditor\b", re.IGNORECASE)),
        (r"\bteamwork_\w+\b", re.compile(r"\bteamwork_\w+\b", re.IGNORECASE)),
        (r"\bsentinel\b", re.compile(r"\bsentinel\b", re.IGNORECASE)),
        (r"\btest_writer(_v\d+)?\b", re.compile(r"\btest_writer(_v\d+)?\b", re.IGNORECASE)),
        
        # Internal iteration narratives & triads
        (r"v1\s*->\s*v2\s*->\s*v3", re.compile(r"v1\s*->\s*v2\s*->\s*v3", re.IGNORECASE)),
        (r"Three-Iteration Triad", re.compile(r"Three-Iteration Triad", re.IGNORECASE)),
        (r"Version 1 \(Initial Formulation\)", re.compile(r"Version 1 \(Initial Formulation\)", re.IGNORECASE)),
        (r"Version 2 \(Intermediate Formulation\)", re.compile(r"Version 2 \(Intermediate Formulation\)", re.IGNORECASE)),
        (r"Version 3 \(Final Triad Formulation\)", re.compile(r"Version 3 \(Final Triad Formulation\)", re.IGNORECASE)),
        (r"\btriad formulation\b", re.compile(r"\btriad formulation\b", re.IGNORECASE)),
        (r"\biteration narrative\b", re.compile(r"\biteration narrative\b", re.IGNORECASE)),
        (r"\bsprint \d+\b", re.compile(r"\bsprint \d+\b", re.IGNORECASE)),
    ]

    def test_01_hostile_scan_v4_author_source_files(self):
        """Scan all authored text files in v4/ (tex, bib, py, bbl, aux, out, log, txt).
        Ensure ZERO occurrences of Codex, bot handles, internal directories, or version triads.
        """
        violations = []
        scanned_files = 0
        for root, dirs, files in os.walk(V4_DIR):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                # Check all author files and generated artifacts
                if ext in [".tex", ".bib", ".py", ".bbl", ".aux", ".out", ".log", ".txt"]:
                    filepath = Path(root) / fname
                    scanned_files += 1
                    try:
                        content = filepath.read_text(encoding="utf-8", errors="replace")
                    except Exception as e:
                        violations.append(f"Could not read {filepath}: {e}")
                        continue

                    for line_num, line in enumerate(content.splitlines(), start=1):
                        for raw_pat, regex in self.FORBIDDEN_PATTERNS:
                            matches = regex.findall(line)
                            if matches:
                                violations.append(
                                    f"LEAK FOUND in {filepath.relative_to(PROJECT_ROOT)}:{line_num} "
                                    f"Pattern: '{raw_pat}' Matched: '{matches}' Line: {line.strip()}"
                                )

        self.assertGreater(scanned_files, 8, "Expected to scan at least 8 authored/generated files in v4/.")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} sanitization leaks:\n" + "\n".join(violations))

    def test_02_hostile_scan_inside_overleaf_zip(self):
        """Scan all files inside v4/overleaf_bundle_v4.zip.
        Ensures all authored files (tex, bib) and style files contain zero leaks.
        Third-party CTAN language files (.ldf) are verified for zero internal repo references.
        """
        zip_path = V4_DIR / "overleaf_bundle_v4.zip"
        self.assertTrue(zip_path.exists(), "overleaf_bundle_v4.zip does not exist!")

        violations = []
        scanned_zip_files = 0

        with zipfile.ZipFile(zip_path, "r") as zf:
            for zipinfo in zf.infolist():
                if zipinfo.is_dir():
                    continue
                ext = os.path.splitext(zipinfo.filename)[1].lower()
                if ext in [".tex", ".bib", ".cls", ".sty", ".bst", ".txt", ".ldf"]:
                    scanned_zip_files += 1
                    raw_bytes = zf.read(zipinfo.filename)
                    content = raw_bytes.decode("utf-8", errors="replace")
                    for line_num, line in enumerate(content.splitlines(), start=1):
                        for raw_pat, regex in self.FORBIDDEN_PATTERNS:
                            # jabbrv-ltwa-all.ldf has ISO-4 standard exception: \DefineJournalWordException{Codex}{Codex}
                            # and jabbrv-ltwa-en.ldf has \DefineJournalWordException{Teamwork}{Teamwork}
                            if ext == ".ldf" and "DefineJournalWordException" in line:
                                continue
                            matches = regex.findall(line)
                            if matches:
                                violations.append(
                                    f"ZIP LEAK in {zipinfo.filename}:{line_num} "
                                    f"Pattern: '{raw_pat}' Matched: '{matches}' Line: {line.strip()}"
                                )

        self.assertGreater(scanned_zip_files, 3, "Expected at least 4 text files inside overleaf zip bundle.")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} sanitization leaks in zip bundle:\n" + "\n".join(violations))

    def test_03_hostile_scan_compiled_pdf_text(self):
        """Extract all text from compiled PDFs and scan for leaks and broken references."""
        pdf_files = [V4_DIR / "Paper_arxiv_v4.pdf", V4_DIR / "Paper_revista_v4.pdf"]
        
        leak_violations = []
        broken_ref_violations = []

        # Broken reference indicators in rendered PDF: [?], ??, ?, (??)
        broken_ref_regex = re.compile(r"(\[\?\]|\(\?\?\)|\?\?|\b\?0\b)", re.IGNORECASE)

        for pdf_path in pdf_files:
            self.assertTrue(pdf_path.exists(), f"PDF not found: {pdf_path}")
            doc = fitz.open(pdf_path)
            self.assertGreater(len(doc), 5, f"PDF {pdf_path.name} has suspiciously few pages ({len(doc)})")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # Check for sanitization leaks
                for line in text.splitlines():
                    for raw_pat, regex in self.FORBIDDEN_PATTERNS:
                        matches = regex.findall(line)
                        if matches:
                            leak_violations.append(
                                f"PDF LEAK in {pdf_path.name} page {page_num + 1}: "
                                f"Pattern: '{raw_pat}' Matched: '{matches}' Line: {line.strip()}"
                            )
                    # Check for broken references
                    ref_matches = broken_ref_regex.findall(line)
                    if ref_matches:
                        broken_ref_violations.append(
                            f"BROKEN REF in {pdf_path.name} page {page_num + 1}: "
                            f"Matched: '{ref_matches}' Line: {line.strip()}"
                        )
            doc.close()

        self.assertEqual(len(leak_violations), 0, f"Found {len(leak_violations)} PDF text leaks:\n" + "\n".join(leak_violations))
        self.assertEqual(len(broken_ref_violations), 0, f"Found {len(broken_ref_violations)} broken references in PDF text:\n" + "\n".join(broken_ref_violations))


class TestAdversarialBaselineIsolation(unittest.TestCase):
    """Stress-test baseline folder protection (v1, v2, v3 remain 100% untouched)."""

    def test_01_git_status_porcelain_baseline(self):
        """git status --porcelain -uall v1 v2 v3 must be strictly empty."""
        res = subprocess.run(
            ["git", "status", "--porcelain", "-uall", "v1", "v2", "v3"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"git status failed: {res.stderr}")
        self.assertEqual(res.stdout.strip(), "", f"Baseline folders v1/v2/v3 have modifications or untracked files:\n{res.stdout}")

    def test_02_git_diff_baseline(self):
        """git diff HEAD -- v1 v2 v3 must be strictly empty."""
        res = subprocess.run(
            ["git", "diff", "HEAD", "--", "v1", "v2", "v3"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"git diff failed: {res.stderr}")
        self.assertEqual(res.stdout.strip(), "", f"Baseline folders v1/v2/v3 differ from HEAD:\n{res.stdout}")


class TestAdversarialCitationParity(unittest.TestCase):
    """Verify exact 70/70 citation parity, zero missing, zero unreferenced entries."""

    @classmethod
    def setUpClass(cls):
        bib_file = V4_DIR / "references.bib"
        bib_content = bib_file.read_text(encoding="utf-8")
        cls.bib_keys = set(re.findall(r"@\w+\s*\{\s*([a-zA-Z0-9_\-:]+)\s*,", bib_content))

        arxiv_tex = (V4_DIR / "Paper_arxiv_v4.tex").read_text(encoding="utf-8")
        revista_tex = (V4_DIR / "Paper_revista_v4.tex").read_text(encoding="utf-8")

        def extract_citations(tex):
            clean_lines = []
            for line in tex.splitlines():
                stripped = re.sub(r"(?<!\\)%.*$", "", line)
                clean_lines.append(stripped)
            clean_tex = "\n".join(clean_lines)

            raw_cites = re.findall(r"\\(?:cite[a-z]*|nocite)\*?(?:\[[^\]]*\])?\{([^}]+)\}", clean_tex)
            cites = set()
            for group in raw_cites:
                for key in group.split(","):
                    k = key.strip()
                    if k:
                        cites.add(k)
            return cites

        cls.arxiv_cites = extract_citations(arxiv_tex)
        cls.revista_cites = extract_citations(revista_tex)

    def test_01_bibtex_key_count(self):
        """references.bib must contain exactly 70 unique entries."""
        self.assertEqual(len(self.bib_keys), 70, f"Expected exactly 70 BibTeX keys, found {len(self.bib_keys)}")

    def test_02_arxiv_citation_parity_and_completeness(self):
        """Paper_arxiv_v4.tex must cite exactly all 70 BibTeX keys."""
        missing_in_bib = self.arxiv_cites - self.bib_keys
        unreferenced_in_bib = self.bib_keys - self.arxiv_cites

        self.assertEqual(len(missing_in_bib), 0, f"Keys cited in arXiv but missing from references.bib: {missing_in_bib}")
        self.assertEqual(len(unreferenced_in_bib), 0, f"Keys in references.bib not cited in arXiv: {unreferenced_in_bib}")
        self.assertEqual(len(self.arxiv_cites), 70, f"arXiv cites {len(self.arxiv_cites)} keys, expected 70")

    def test_03_revista_citation_parity_and_completeness(self):
        """Paper_revista_v4.tex must cite exactly all 70 BibTeX keys."""
        missing_in_bib = self.revista_cites - self.bib_keys
        unreferenced_in_bib = self.bib_keys - self.revista_cites

        self.assertEqual(len(missing_in_bib), 0, f"Keys cited in Revista but missing from references.bib: {missing_in_bib}")
        self.assertEqual(len(unreferenced_in_bib), 0, f"Keys in references.bib not cited in Revista: {unreferenced_in_bib}")
        self.assertEqual(len(self.revista_cites), 70, f"Revista cites {len(self.revista_cites)} keys, expected 70")

    def test_04_cross_manuscript_citation_identity(self):
        """Both manuscripts must cite the exact same set of 70 keys."""
        diff = self.arxiv_cites.symmetric_difference(self.revista_cites)
        self.assertEqual(len(diff), 0, f"Discrepancy between arXiv and Revista citations: {diff}")

    def test_05_bbl_generated_references_count(self):
        """Verify that .bbl files for both manuscripts contain all 70 \\bibitem entries."""
        for bbl_name in ["Paper_arxiv_v4.bbl", "Paper_revista_v4.bbl"]:
            bbl_file = V4_DIR / bbl_name
            self.assertTrue(bbl_file.exists(), f"Missing {bbl_name}")
            content = bbl_file.read_text(encoding="utf-8")
            bibitems = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", content)
            self.assertEqual(len(bibitems), 70, f"{bbl_name} contains {len(bibitems)} bibitems, expected 70")


class TestAdversarialCompilerLogs(unittest.TestCase):
    """Stress-test compiler logs for unresolved warnings, undefined references, or '?'."""

    LOG_FILES = ["Paper_arxiv_v4.log", "Paper_revista_v4.log"]

    def test_01_zero_undefined_citations(self):
        """Ensure zero undefined citation warnings in LaTeX logs."""
        violations = []
        for log_name in self.LOG_FILES:
            log_path = V4_DIR / log_name
            self.assertTrue(log_path.exists(), f"Log file not found: {log_name}")
            content = log_path.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                if "citation" in line.lower() and "undefined" in line.lower():
                    violations.append(f"{log_name}: {line.strip()}")
                elif "there were undefined citations" in line.lower():
                    violations.append(f"{log_name}: {line.strip()}")
        self.assertEqual(len(violations), 0, f"Undefined citations found:\n" + "\n".join(violations))

    def test_02_zero_undefined_references(self):
        """Ensure zero undefined reference warnings in LaTeX logs."""
        violations = []
        for log_name in self.LOG_FILES:
            log_path = V4_DIR / log_name
            content = log_path.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                if "reference" in line.lower() and "undefined" in line.lower():
                    violations.append(f"{log_name}: {line.strip()}")
                elif "there were undefined references" in line.lower():
                    violations.append(f"{log_name}: {line.strip()}")
        self.assertEqual(len(violations), 0, f"Undefined references found:\n" + "\n".join(violations))

    def test_03_zero_label_changed_warnings(self):
        """Ensure labels have converged completely (no 'Label(s) may have changed')."""
        violations = []
        for log_name in self.LOG_FILES:
            log_path = V4_DIR / log_name
            content = log_path.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                if "label(s) may have changed" in line.lower():
                    violations.append(f"{log_name}: {line.strip()}")
        self.assertEqual(len(violations), 0, f"Unconverged labels found:\n" + "\n".join(violations))

    def test_04_bibtex_blg_cleanliness(self):
        """Ensure zero error or warning messages in BibTeX .blg logs."""
        blg_files = ["Paper_arxiv_v4.blg", "Paper_revista_v4.blg"]
        violations = []
        for blg_name in blg_files:
            blg_path = V4_DIR / blg_name
            self.assertTrue(blg_path.exists(), f"BLG file not found: {blg_name}")
            content = blg_path.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                if any(w in line.lower() for w in ["error message", "warning--", "undefined"]):
                    violations.append(f"{blg_name}: {line.strip()}")
        self.assertEqual(len(violations), 0, f"BibTeX issues found in .blg files:\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main(verbosity=2)
