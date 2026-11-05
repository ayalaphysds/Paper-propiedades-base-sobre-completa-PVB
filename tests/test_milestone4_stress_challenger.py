"""
Milestone 4 Challenger 2 Empirical Stress Test Suite.
Author: Milestone 4 Challenger 2 (challenger_m4_2)
Archetype: EMPIRICAL CHALLENGER
Roles: critic, specialist

Stress-tests:
1. v2/overleaf_bundle_v2.zip integrity, structure, and hygiene.
2. Isolated multi-engine compilation (pdflatex and xelatex) in scratch directory.
3. Isolated BibTeX lifecycle and zero-undefined citation resolution.
4. Independent execution of scripts/run_all_simulations.py inside the extracted bundle.
5. In-place figure reproduction test: verifies figures/ inside bundle are updated vs leaking to parent.
"""

import os
import sys
import time
import zipfile
import tempfile
import subprocess
import unittest
from pathlib import Path
import fitz  # PyMuPDF

REPO_ROOT = Path(r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB")
BUNDLE_ZIP = REPO_ROOT / "v2" / "overleaf_bundle_v2.zip"

EXPECTED_BUNDLE_MEMBERS = {
    "Paper_arxiv_v2.tex",
    "Paper_arxiv_v2.bbl",
    "Paper_revista_v2.tex",
    "Paper_revista_v2.bbl",
    "references.bib",
    "optica-article.cls",
    "opticajnl.bst",
    "jabbrv.sty",
    "jabbrv-ltwa-all.ldf",
    "jabbrv-ltwa-en.ldf",
    "RESPUESTAS_REVISION_V2.md",
    "styles/opticajournal.sty",
    "figures/fig1_pvb_profiles_divergence.pdf",
    "figures/fig2_radial_overlap_matrix.pdf",
    "figures/fig3_frame_spectrum_bounds.pdf",
    "figures/fig4_turbulence_rkhs_recovery.pdf",
    "figures/fig5_quantum_povm_entanglement.pdf",
    "scripts/generate_fig1_profiles.py",
    "scripts/generate_fig2_overlap.py",
    "scripts/generate_fig3_frame_bounds.py",
    "scripts/generate_fig4_turbulence.py",
    "scripts/generate_fig5_quantum.py",
    "scripts/run_all_simulations.py",
}

EXPECTED_FIGURES = [
    "fig1_pvb_profiles_divergence.pdf",
    "fig2_radial_overlap_matrix.pdf",
    "fig3_frame_spectrum_bounds.pdf",
    "fig4_turbulence_rkhs_recovery.pdf",
    "fig5_quantum_povm_entanglement.pdf",
]


class TestMilestone4EmpiricalChallenger(unittest.TestCase):

    def setUp(self):
        self.assertTrue(BUNDLE_ZIP.exists(), f"Deliverable missing: {BUNDLE_ZIP}")
        self.assertGreater(BUNDLE_ZIP.stat().st_size, 300_000, "Bundle zip suspiciously small (< 300 KB)")

    def test_01_zip_structure_integrity_and_hygiene(self):
        """Stress Check 1: Validate ZIP CRC-32, exact 23 members, POSIX slashes, and zero temp compiler files."""
        with zipfile.ZipFile(BUNDLE_ZIP, "r") as z:
            # CRC test
            bad_crc = z.testzip()
            self.assertIsNone(bad_crc, f"Corrupted file found in zip: {bad_crc}")

            namelist = z.namelist()
            self.assertEqual(len(namelist), 23, f"Expected 23 members in zip, found {len(namelist)}")
            self.assertEqual(set(namelist), EXPECTED_BUNDLE_MEMBERS, "Bundle member set mismatch")

            # Path hygiene
            for name in namelist:
                self.assertFalse(name.startswith("/"), f"Absolute path detected in zip: {name}")
                self.assertFalse(name.startswith("\\"), f"Leading backslash in zip: {name}")
                self.assertNotIn("\\", name, f"Windows backslash detected in zip entry: {name}")
                self.assertNotIn("..", name, f"Path traversal token detected in zip: {name}")

                # Ensure no forbidden extensions
                ext = Path(name).suffix.lower()
                self.assertNotIn(ext, [".aux", ".log", ".blg", ".out", ".pyc", ".synctex.gz"],
                                 f"Forbidden temporary build artifact in zip: {name}")
                self.assertNotIn("__pycache__", name, f"Python cache in zip: {name}")

    def test_02_pdflatex_compilation_in_isolated_scratch(self):
        """Stress Check 2: pdflatex compilation of both manuscripts in a scratch isolated folder."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with zipfile.ZipFile(BUNDLE_ZIP, "r") as z:
                z.extractall(tmp_path)

            for doc in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
                cmd = ["pdflatex", "-interaction=nonstopmode", doc]
                p = subprocess.run(cmd, cwd=str(tmp_path), capture_output=True)
                self.assertEqual(p.returncode, 0, f"pdflatex failed on {doc} with returncode {p.returncode}")

                pdf_path = tmp_path / doc.replace(".tex", ".pdf")
                self.assertTrue(pdf_path.exists(), f"Expected output PDF missing: {pdf_path}")
                self.assertGreater(pdf_path.stat().st_size, 400_000, f"PDF suspiciously small: {pdf_path}")

                doc_fitz = fitz.open(str(pdf_path))
                page_count = len(doc_fitz)
                self.assertGreaterEqual(page_count, 5, f"{doc} page count too low ({page_count})")
                self.assertLessEqual(page_count, 100, f"{doc} page count exceeds 100 limit ({page_count})")

                # Verify each page contains actual text
                for i, page in enumerate(doc_fitz):
                    txt = page.get_text().strip()
                    self.assertGreater(len(txt), 20, f"Page {i+1} in {doc} appears blank (< 20 chars)")
                doc_fitz.close()

    def test_03_xelatex_compilation_in_isolated_scratch(self):
        """Stress Check 3: xelatex compilation of both manuscripts in a scratch isolated folder."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with zipfile.ZipFile(BUNDLE_ZIP, "r") as z:
                z.extractall(tmp_path)

            for doc in ["Paper_arxiv_v2.tex", "Paper_revista_v2.tex"]:
                cmd = ["xelatex", "-interaction=nonstopmode", doc]
                p = subprocess.run(cmd, cwd=str(tmp_path), capture_output=True)
                self.assertEqual(p.returncode, 0, f"xelatex failed on {doc} with returncode {p.returncode}")

                pdf_path = tmp_path / doc.replace(".tex", ".pdf")
                self.assertTrue(pdf_path.exists(), f"Expected output PDF missing under xelatex: {pdf_path}")
                self.assertGreater(pdf_path.stat().st_size, 400_000, f"PDF suspiciously small under xelatex: {pdf_path}")

                doc_fitz = fitz.open(str(pdf_path))
                page_count = len(doc_fitz)
                self.assertGreaterEqual(page_count, 5, f"{doc} page count too low ({page_count})")
                self.assertLessEqual(page_count, 100, f"{doc} page count exceeds 100 limit ({page_count})")

                for i, page in enumerate(doc_fitz):
                    txt = page.get_text().strip()
                    self.assertGreater(len(txt), 20, f"Page {i+1} in {doc} under xelatex appears blank (< 20 chars)")
                doc_fitz.close()

    def test_04_bibtex_clean_resolution_in_scratch_dir(self):
        """Stress Check 4: Verify full BibTeX cycle in scratch folder produces 0 undefined citations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with zipfile.ZipFile(BUNDLE_ZIP, "r") as z:
                z.extractall(tmp_path)

            for stem in ["Paper_arxiv_v2", "Paper_revista_v2"]:
                # Pass 1: LaTeX
                subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{stem}.tex"], cwd=str(tmp_path), capture_output=True)
                # Pass 2: BibTeX
                pb = subprocess.run(["bibtex", stem], cwd=str(tmp_path), capture_output=True)
                self.assertEqual(pb.returncode, 0, f"BibTeX failed on {stem} with returncode {pb.returncode}")
                # Pass 3 & 4: LaTeX to resolve references
                subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{stem}.tex"], cwd=str(tmp_path), capture_output=True)
                p_final = subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{stem}.tex"], cwd=str(tmp_path), capture_output=True)
                self.assertEqual(p_final.returncode, 0, f"Final pdflatex failed on {stem}")

                log_content = (tmp_path / f"{stem}.log").read_text(encoding="latin-1", errors="replace")
                self.assertNotIn("There were undefined references", log_content,
                                 f"Undefined references detected in {stem}.log")

    def test_05_simulation_in_place_reproduction_in_extracted_bundle(self):
        """
        Stress Check 5 (CRITICAL): Execute scripts/run_all_simulations.py inside extracted bundle
        and verify that the figures in the extracted bundle's figures/ directory are updated in-place.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with zipfile.ZipFile(BUNDLE_ZIP, "r") as z:
                z.extractall(tmp_path)

            figures_dir = tmp_path / "figures"
            self.assertTrue(figures_dir.exists(), "Extracted figures/ directory missing")

            # Record initial modification times of figures inside the extracted bundle
            orig_mtimes = {fig_name: (figures_dir / fig_name).stat().st_mtime for fig_name in EXPECTED_FIGURES}

            # Small delay to ensure timestamp difference
            time.sleep(1.0)
            runner_script = tmp_path / "scripts" / "run_all_simulations.py"
            self.assertTrue(runner_script.exists(), "scripts/run_all_simulations.py missing in bundle")

            proc = subprocess.run([sys.executable, str(runner_script)], cwd=str(tmp_path), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, f"run_all_simulations.py exited with error {proc.returncode}:\n{proc.stderr}")

            # Check if figures inside tmp_path / "figures" were updated
            new_mtimes = {fig_name: (figures_dir / fig_name).stat().st_mtime for fig_name in EXPECTED_FIGURES}
            updated_figures = [f for f in EXPECTED_FIGURES if new_mtimes[f] > orig_mtimes[f]]

            # Detect directory leak: did the script write to tmp_path.parent / "v2" / "figures"?
            leaked_dir = tmp_path.parent / "v2" / "figures"
            leaked = leaked_dir.exists() and any(leaked_dir.glob("*.pdf"))

            self.assertEqual(
                len(updated_figures), 5,
                f"Defect: run_all_simulations.py inside extracted bundle failed to update figures in-place! "
                f"Updated {len(updated_figures)}/5 figures in {figures_dir}. "
                f"Leak detected in {leaked_dir}: {leaked}. "
                f"Root cause: scripts use 'Path(__file__).resolve().parent.parent.parent / \"v2\" / \"figures\"' "
                f"which escapes the extracted bundle root and targets a non-existent sibling v2 directory."
            )

    def test_06_individual_generator_script_in_place_output(self):
        """
        Stress Check 6: Execute individual simulation generator inside extracted bundle
        and verify it saves to the extracted bundle's figures/ directory.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with zipfile.ZipFile(BUNDLE_ZIP, "r") as z:
                z.extractall(tmp_path)

            target_fig = tmp_path / "figures" / "fig1_pvb_profiles_divergence.pdf"
            if target_fig.exists():
                target_fig.unlink()
            self.assertFalse(target_fig.exists())

            script_1 = tmp_path / "scripts" / "generate_fig1_profiles.py"
            proc = subprocess.run([sys.executable, str(script_1)], cwd=str(tmp_path / "scripts"), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, f"generate_fig1_profiles.py failed:\n{proc.stderr}")

            self.assertTrue(
                target_fig.exists(),
                f"Defect: generate_fig1_profiles.py failed to output to {target_fig}. "
                f"Output leaked to sibling/parent directory due to hardcoded parent.parent.parent / 'v2' / 'figures'."
            )


if __name__ == "__main__":
    unittest.main()
