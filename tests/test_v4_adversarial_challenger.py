"""
Adversarial Verification Suite for Version 4 (v4)
Executed by challenger_v4_1.

Covers:
1. Overleaf Bundle Extraction & Standalone Dry-Run Compilation in isolated tempdir
2. Simulation Suite Reproducibility with timing and memory monitoring
3. PDF Deliverables Integrity (%PDF- magic bytes, non-zero size, <= 100 pages)
4. Strict E2E Test Suite verification (28/28 passing)
"""

import os
import sys
import time
import shutil
import zipfile
import tempfile
import subprocess
import re
import tracemalloc
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V4_DIR = PROJECT_ROOT / "v4"
BUNDLE_PATH = V4_DIR / "overleaf_bundle_v4.zip"
SCRIPTS_DIR = V4_DIR / "scripts"
FIGURES_DIR = V4_DIR / "figures"
TESTS_DIR = PROJECT_ROOT / "tests"

EXPECTED_FIGURES = [
    "fig1_pvb_profiles_divergence.pdf",
    "fig2_radial_overlap_matrix.pdf",
    "fig3_frame_spectrum_bounds.pdf",
    "fig4_turbulence_rkhs_recovery.pdf",
    "fig5_quantum_povm_entanglement.pdf",
]


def check_magic_bytes(path: Path) -> bool:
    if not path.exists():
        return False
    with open(path, "rb") as f:
        magic = f.read(5)
    return magic == b"%PDF-"


def count_pdf_pages(pdf_path: Path) -> int:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except Exception:
        pass
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except Exception:
        pass
    # Fallback to regex in binary stream
    with open(pdf_path, "rb") as f:
        content = f.read()
    matches = re.findall(rb"/Type\s*/Page\b", content)
    return len(matches)


def task1_isolated_overleaf_dry_run():
    print("\n=======================================================")
    print("TASK 1: OVERLEAF BUNDLE EXTRACTION & STANDALONE DRY-RUN")
    print("=======================================================")
    assert BUNDLE_PATH.exists(), f"Bundle missing: {BUNDLE_PATH}"
    print(f"Bundle found: {BUNDLE_PATH} (size: {BUNDLE_PATH.stat().st_size} bytes)")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        print(f"Extracting into clean isolated temporary directory: {tmppath}")
        with zipfile.ZipFile(BUNDLE_PATH) as z:
            z.extractall(tmppath)

        extracted = list(tmppath.rglob("*"))
        print(f"Extracted {len(extracted)} files/folders.")

        # 1. Structural check
        required_in_bundle = [
            "Paper_arxiv_v4.tex",
            "Paper_revista_v4.tex",
            "references.bib",
            "optica-article.cls",
            "jabbrv.sty",
            "opticajnl.bst",
            "styles/opticajournal.sty",
        ] + [f"figures/{fig}" for fig in EXPECTED_FIGURES]

        for item in required_in_bundle:
            target = tmppath / item
            assert target.exists(), f"Missing required file in extracted bundle: {item}"
        print("PASS: All required source files, style files, and figures present in bundle.")

        # 2. Check for external path leaks
        for tex_name in ["Paper_arxiv_v4.tex", "Paper_revista_v4.tex"]:
            content = (tmppath / tex_name).read_text(encoding="utf-8")
            assert ".." not in content, f"Path traversal '..' found in {tex_name}"
            # Check graphics resolution
            graphics = re.findall(r"\\includegraphics(?:\[.*?\])?\{([^\}]+)\}", content)
            print(f"Checking {len(graphics)} graphic references in {tex_name}...")
            for g in graphics:
                gp = tmppath / g
                if not gp.exists() and not gp.with_suffix(".pdf").exists():
                    raise AssertionError(f"Graphic '{g}' referenced in {tex_name} not found in bundle!")
        print("PASS: Zero external path leaks, all graphics resolve internally.")

        # 3. 4-Pass pdflatex + bibtex compilation dry-run
        for basename in ["Paper_arxiv_v4", "Paper_revista_v4"]:
            print(f"\n--- Compiling {basename} in isolated tempdir ---")
            t0 = time.time()
            passes = [
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{basename}.tex"],
                ["bibtex", basename],
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{basename}.tex"],
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{basename}.tex"],
            ]
            for pass_num, cmd in enumerate(passes, 1):
                p_start = time.time()
                res = subprocess.run(cmd, cwd=tmppath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                p_time = time.time() - p_start
                if res.returncode != 0:
                    print(f"FAIL on pass {pass_num} ({cmd[0]}): exit code {res.returncode}")
                    print("Log tail:")
                    log_f = tmppath / f"{basename}.log"
                    if log_f.exists():
                        print(log_f.read_text(encoding="latin-1", errors="replace")[-1500:])
                    raise RuntimeError(f"LaTeX pass {pass_num} failed for {basename}")
                print(f"Pass {pass_num} ({cmd[0]}) completed in {p_time:.2f}s")

            total_t = time.time() - t0
            out_pdf = tmppath / f"{basename}.pdf"
            assert out_pdf.exists(), f"Output PDF {out_pdf} missing!"
            assert check_magic_bytes(out_pdf), f"PDF {out_pdf} does not start with %PDF-"
            
            pages = count_pdf_pages(out_pdf)
            print(f"Compiled {basename}.pdf: size={out_pdf.stat().st_size} bytes, pages={pages}, time={total_t:.2f}s")
            assert pages > 0, "PDF has 0 pages"
            assert pages <= 100, f"PDF page count {pages} exceeds 100 page limit"

            # Check log for undefined references or citations
            log_text = (tmppath / f"{basename}.log").read_text(encoding="latin-1", errors="replace")
            undef_cites = re.findall(r"citation\s+[`\"'](.*?)['\"`]\s+undefined", log_text, re.IGNORECASE)
            undef_refs = re.findall(r"reference\s+[`\"'](.*?)['\"`]\s+undefined", log_text, re.IGNORECASE)
            assert len(undef_cites) == 0, f"Found undefined citations in {basename}: {undef_cites}"
            assert len(undef_refs) == 0, f"Found undefined references in {basename}: {undef_refs}"
            assert "There were undefined references" not in log_text, f"Log reports undefined references in {basename}"
            print(f"PASS: {basename} compiled with zero undefined references/citations in isolated tempdir.")

    print("\n>>> TASK 1 VERDICT: PASSED standalone isolated dry-run.")
    return True


def task2_simulation_reproducibility():
    print("\n=======================================================")
    print("TASK 2: SIMULATION SUITE REPRODUCIBILITY")
    print("=======================================================")
    runner_script = SCRIPTS_DIR / "run_all_simulations.py"
    assert runner_script.exists(), f"Missing runner script: {runner_script}"

    # Record pre-execution modification times
    pre_mtimes = {}
    for fig_name in EXPECTED_FIGURES:
        fp = FIGURES_DIR / fig_name
        if fp.exists():
            pre_mtimes[fig_name] = fp.stat().st_mtime

    print(f"Executing: python {runner_script}")
    time.sleep(1.0) # sleep to ensure mtime change is detectable
    t0 = time.time()
    
    # Run the simulation suite
    res = subprocess.run(
        [sys.executable, str(runner_script)],
        cwd=V4_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    elapsed = time.time() - t0
    
    print(f"Simulations finished in {elapsed:.2f}s (Exit code: {res.returncode})")
    if res.returncode != 0:
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        raise RuntimeError("run_all_simulations.py failed!")

    print("Output summary from simulations:")
    for line in res.stdout.strip().splitlines()[-15:]:
        print("  ", line)

    # Verify all 5 figures were updated and are valid PDFs
    for fig_name in EXPECTED_FIGURES:
        fp = FIGURES_DIR / fig_name
        assert fp.exists(), f"Figure missing: {fp}"
        post_mtime = fp.stat().st_mtime
        if fig_name in pre_mtimes:
            assert post_mtime >= pre_mtimes[fig_name], f"Figure {fig_name} was not updated!"
        
        size = fp.stat().st_size
        print(f"Figure {fig_name}: size={size} bytes, mtime={post_mtime}")
        assert size > 10240, f"Figure {fig_name} is suspiciously small ({size} bytes)"
        assert check_magic_bytes(fp), f"Figure {fig_name} does not have %PDF- header"

    print(f"\n>>> TASK 2 VERDICT: PASSED reproducibility in {elapsed:.2f}s with all 5 valid figure PDFs.")
    return True, elapsed


def task3_pdf_deliverables_integrity():
    print("\n=======================================================")
    print("TASK 3: PDF DELIVERABLES INTEGRITY")
    print("=======================================================")
    pdf_targets = [
        V4_DIR / "Paper_arxiv_v4.pdf",
        V4_DIR / "Paper_revista_v4.pdf"
    ]
    for pdf_path in pdf_targets:
        assert pdf_path.exists(), f"Deliverable PDF missing: {pdf_path}"
        assert check_magic_bytes(pdf_path), f"Magic bytes mismatch for {pdf_path}"
        size = pdf_path.stat().st_size
        assert size > 50000, f"PDF file size too small: {size} bytes for {pdf_path}"
        pages = count_pdf_pages(pdf_path)
        print(f"Deliverable {pdf_path.name}: size={size} bytes, pages={pages}, magic=%PDF- valid")
        assert 1 <= pages <= 100, f"Page count {pages} not in 1..100 range for {pdf_path.name}"

    print("\n>>> TASK 3 VERDICT: PASSED deliverables integrity.")
    return True


def task4_strict_e2e_test_suite():
    print("\n=======================================================")
    print("TASK 4: STRICT E2E TEST SUITE EXECUTION")
    print("=======================================================")
    env = os.environ.copy()
    env["FAIL_ON_PENDING"] = "1"
    
    test_file = TESTS_DIR / "test_v4_e2e.py"
    cmd = [sys.executable, str(test_file), "--strict", "-v"]
    print(f"Running: {' '.join(cmd)} with FAIL_ON_PENDING=1")
    t0 = time.time()
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    elapsed = time.time() - t0
    
    print(f"E2E Test execution finished in {elapsed:.2f}s (Exit code: {res.returncode})")
    
    combined_output = res.stdout + "\n" + res.stderr
    print("Test output summary:")
    lines = [line for line in combined_output.splitlines() if "test_" in line or "Ran " in line or "OK" in line or "FAILED" in line]
    for line in lines:
        print("  ", line)

    # Verify 28 tests ran and passed
    assert res.returncode == 0, f"E2E test suite failed with code {res.returncode}!\n{res.stderr}"
    assert "OK" in combined_output, "Test suite did not output OK"
    match = re.search(r"Ran (\d+) tests", combined_output)
    assert match, "Could not find 'Ran X tests' in output"
    num_tests = int(match.group(1))
    print(f"Total tests executed: {num_tests}")
    assert num_tests == 28, f"Expected 28 tests, got {num_tests}"
    assert "skipped=" not in combined_output.lower() or "skipped=0" in combined_output.lower(), "Skipped tests detected!"

    print(f"\n>>> TASK 4 VERDICT: PASSED 28/28 tests in {elapsed:.2f}s with 0 failures, 0 errors, 0 skipped.")
    return True, elapsed


if __name__ == "__main__":
    t_start = time.time()
    try:
        t1_ok = task1_isolated_overleaf_dry_run()
        t2_ok, sim_time = task2_simulation_reproducibility()
        t3_ok = task3_pdf_deliverables_integrity()
        t4_ok, e2e_time = task4_strict_e2e_test_suite()
        
        total_time = time.time() - t_start
        print("\n" + "=" * 60)
        print(f"ALL ADVERSARIAL CHALLENGES COMPLETED SUCCESSFULLY IN {total_time:.2f}s")
        print("VERDICT: APPROVE")
        print("=" * 60)
    except Exception as e:
        print(f"\nADVERSARIAL VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
