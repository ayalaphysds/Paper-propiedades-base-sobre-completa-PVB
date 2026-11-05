# Milestone 4 Challenger 2 Handoff Report: Empirical Stress Testing & Audit

- **Agent**: `challenger_m4_2`
- **Role**: Milestone 4 Challenger 2 (critic, specialist)
- **Target Deliverable**: `v2/overleaf_bundle_v2.zip`
- **Verdict**: **REQUEST_CHANGES**
- **Date**: 2026-11-05T00:37:00Z
- **Parent Conversation**: `b896091e-9b49-4cdd-bfee-68e28ef0ca66`

---

## 1. Observation

All tests and empirical verifications were independently executed in clean sessions and isolated environments:

1. **Existing Test Suite Verification**:
   - `python tests/test_e2e_runner.py`:
     - Result: `Ran 81 tests ... 81 passed, 0 failed, 0 skipped` in 0.309s (Tier 1: 46, Tier 2: 25, Tier 3: 5, Tier 4: 5).
   - `python tests/test_v2_suite.py` (under standard and `FAIL_ON_PENDING=1`):
     - Result: `Ran 34 tests ... 34 passed, 0 failed, 0 skipped` in 9.487s.

2. **Multi-Engine LaTeX Compilation in Scratch Temporary Folder**:
   - `v2/overleaf_bundle_v2.zip` was extracted to a clean scratch folder (`C:\Users\sayal\AppData\Local\Temp\tmpew53ngqp`).
   - `pdflatex -interaction=nonstopmode Paper_arxiv_v2.tex`: Exit code 0, generated valid PDF (21 pages, 1,162,387 bytes).
   - `pdflatex -interaction=nonstopmode Paper_revista_v2.tex`: Exit code 0, generated valid PDF (20 pages, 872,411 bytes).
   - `xelatex -interaction=nonstopmode Paper_arxiv_v2.tex`: Exit code 0, generated valid PDF (21 pages, 623,648 bytes).
   - `xelatex -interaction=nonstopmode Paper_revista_v2.tex`: Exit code 0, generated valid PDF (20 pages, 622,706 bytes).
   - All generated PDFs have page counts strictly between 5 and 100 pages, and every single page contains substantive text (>20 characters, no blank pages).

3. **BibTeX Lifecycle & Citation Resolution in Scratch Temporary Folder**:
   - Executed 4-pass compilation (`pdflatex` -> `bibtex` -> `pdflatex` -> `pdflatex`) and (`xelatex` -> `bibtex` -> `xelatex` -> `xelatex`) in clean isolated scratch directory.
   - Return codes: `pdflatex=0`, `bibtex=0`, `pdflatex_final=0`; `xelatex=0`, `bibtex=0`, `xelatex_final=0`.
   - Inspection of `.log` files confirmed 0 undefined references and 0 undefined citations.

4. **Simulation In-Place Reproduction Defect (CRITICAL)**:
   - When extracting `v2/overleaf_bundle_v2.zip` into an isolated folder `T = C:\Users\sayal\AppData\Local\Temp\tmp...` and running:
     ```powershell
     python scripts/run_all_simulations.py
     ```
     with `cwd = T`:
     - Initial mtime of `T/figures/*.pdf` recorded.
     - Execution succeeded with exit code 0.
     - However, **0 out of 5 figures inside `T/figures/` were updated**!
     - Instead, the script created a new directory `T.parent / "v2" / "figures"` (`C:\Users\sayal\AppData\Local\Temp\v2\figures\`) and wrote all 5 regenerated figures there!
   - Root cause analysis in `v2/scripts/run_all_simulations.py` (lines 23–25):
     ```python
     PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
     SCRIPTS_V2_DIR = PROJECT_ROOT / "v2" / "scripts"
     FIGURES_V2_DIR = PROJECT_ROOT / "v2" / "figures"
     ```
     In the unzipped bundle, `Path(__file__).resolve().parent.parent` is the bundle root `T`. Ascending three parent levels (`.parent.parent.parent`) climbs into `T.parent` outside the bundle. It then appends `"v2" / "figures"`, which does not exist in the bundle.
   - Root cause in all 5 individual generators (`v2/scripts/generate_fig1_profiles.py` through `generate_fig5_quantum.py`):
     ```python
     PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
     ...
     if output_path is None:
         output_path = PROJECT_ROOT / "v2" / "figures" / "figX...pdf"
     ```
     When executed standalone inside the unzipped bundle (`python scripts/generate_fig1_profiles.py`), the script similarly leaks to `T.parent / "v2" / "figures"`, failing to update `T/figures/fig1_pvb_profiles_divergence.pdf`.

5. **Empirical Challenger Test Suite Execution**:
   - Test suite written to `tests/test_milestone4_stress_challenger.py` (6 tests).
   - Execution command: `python tests/test_milestone4_stress_challenger.py`
   - Results:
     - `test_01_zip_structure_integrity_and_hygiene`: PASSED
     - `test_02_pdflatex_compilation_in_isolated_scratch`: PASSED
     - `test_03_xelatex_compilation_in_isolated_scratch`: PASSED
     - `test_04_bibtex_clean_resolution_in_scratch_dir`: PASSED
     - `test_05_simulation_in_place_reproduction_in_extracted_bundle`: **FAILED**
       - Verbatim assertion error:
         `AssertionError: 0 != 5 : Defect: run_all_simulations.py inside extracted bundle failed to update figures in-place! Updated 0/5 figures in C:\Users\sayal\AppData\Local\Temp\tmp8r7cntep\figures. Leak detected in C:\Users\sayal\AppData\Local\Temp\v2\figures: True. Root cause: scripts use 'Path(__file__).resolve().parent.parent.parent / "v2" / "figures"' which escapes the extracted bundle root and targets a non-existent sibling v2 directory.`
     - `test_06_individual_generator_script_in_place_output`: **FAILED**
       - Verbatim assertion error:
         `AssertionError: False is not true : Defect: generate_fig1_profiles.py failed to output to C:\Users\sayal\AppData\Local\Temp\tmpw_yyi5i5\figures\fig1_pvb_profiles_divergence.pdf. Output leaked to sibling/parent directory due to hardcoded parent.parent.parent / 'v2' / 'figures'.`

---

## 2. Logic Chain

1. **Premise**: Milestone 4 requires packaging `v2/overleaf_bundle_v2.zip` containing self-contained source assets for publication, compilation, and reproducibility. Dispatch requirement 2 explicitly mandates:
   > "2. Verify that `python scripts/run_all_simulations.py` executes inside the extracted bundle and reproduces all figures identically."
2. **Analysis of Unzipped Environment**:
   - Inside the repository, the directory hierarchy is: `<repo_root>/v2/scripts/run_all_simulations.py` (3 levels down from `<repo_root>`).
   - Inside `v2/overleaf_bundle_v2.zip`, the directory hierarchy is: `<bundle_root>/scripts/run_all_simulations.py` (1 level down from `<bundle_root>`).
   - Hardcoding `parent.parent.parent / "v2" / "figures"` works by accident in the repo, but breaks fundamentally in any unzipped copy because `<bundle_root>.parent` is not the repository root, and does not contain `v2/figures`.
3. **Impact & Blast Radius**:
   - An independent researcher, reviewer, or automated container that unzips `overleaf_bundle_v2.zip` and runs `python scripts/run_all_simulations.py` expects the figures in `figures/` to be regenerated in-place so that subsequent LaTeX compilation picks up the fresh figures.
   - Currently, 0/5 figures in `figures/` are updated.
   - Extraneous files leak into the parent folder (`../v2/figures`).
   - If the parent directory is read-only (standard in many sandbox or container environments), the script crashes with `PermissionError`.
4. **Deduction**: Because `run_all_simulations.py` and the 5 figure generation scripts inside `v2/overleaf_bundle_v2.zip` fail to update figures in-place inside the extracted bundle, Milestone 4 fails Dispatch Requirement 2. Therefore, a verdict of `REQUEST_CHANGES` is required.

---

## 3. Caveats

- LaTeX compilation across both `pdflatex` and `xelatex`, page counts, typography, and citation resolution are robust and fully verified.
- The numerical calculations themselves are 100% deterministic and reproduce the exact binary payload when written to disk; the defect is strictly localized to filesystem path resolution in `run_all_simulations.py` and the 5 `generate_fig*.py` scripts.

---

## 4. Conclusion

**Verdict: REQUEST_CHANGES**

Milestone 4 deliverable `v2/overleaf_bundle_v2.zip` must be remediated to ensure adaptive directory resolution so that scripts execute self-contained both inside the repository and inside any unzipped bundle directory.

### Concrete Action Items for Worker (`worker_m4`):
1. In `v2/scripts/run_all_simulations.py`, replace:
   ```python
   PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
   SCRIPTS_V2_DIR = PROJECT_ROOT / "v2" / "scripts"
   FIGURES_V2_DIR = PROJECT_ROOT / "v2" / "figures"
   ```
   with adaptive directory discovery:
   ```python
   SCRIPTS_DIR = Path(__file__).resolve().parent
   if (SCRIPTS_DIR.parent / "figures").is_dir():
       FIGURES_V2_DIR = SCRIPTS_DIR.parent / "figures"
   elif (SCRIPTS_DIR.parent.parent / "v2" / "figures").is_dir():
       FIGURES_V2_DIR = SCRIPTS_DIR.parent.parent / "v2" / "figures"
   else:
       FIGURES_V2_DIR = SCRIPTS_DIR.parent / "figures"
   ```
2. In all 5 simulation scripts (`v2/scripts/generate_fig1_profiles.py` through `generate_fig5_quantum.py`), apply the same adaptive pattern for `output_path`:
   ```python
   SCRIPTS_DIR = Path(__file__).resolve().parent
   if (SCRIPTS_DIR.parent / "figures").is_dir():
       DEFAULT_FIG_DIR = SCRIPTS_DIR.parent / "figures"
   elif (SCRIPTS_DIR.parent.parent / "v2" / "figures").is_dir():
       DEFAULT_FIG_DIR = SCRIPTS_DIR.parent.parent / "v2" / "figures"
   else:
       DEFAULT_FIG_DIR = SCRIPTS_DIR.parent / "figures"
   ```
   and set `output_path = DEFAULT_FIG_DIR / "figX...pdf"` if `output_path is None`.
3. Repackage `v2/overleaf_bundle_v2.zip`.
4. Run `python tests/test_milestone4_stress_challenger.py` to verify that all 6 tests pass (6/6 passed, 0 failed).

---

## 5. Verification Method

To independently reproduce this finding:

1. **Run the Milestone 4 Challenger Stress Suite**:
   ```powershell
   python tests/test_milestone4_stress_challenger.py
   ```
   *Expected behavior before fix*: Tests 1–4 pass, Tests 5–6 fail with `AssertionError: 0 != 5` and directory leak detection.
   *Expected behavior after worker fix*: All 6 tests pass cleanly.

2. **Manual Reproduction in Isolated Directory**:
   ```powershell
   python -c "import tempfile, zipfile, subprocess; from pathlib import Path; t = Path(tempfile.mkdtemp()); zipfile.ZipFile('v2/overleaf_bundle_v2.zip').extractall(t); orig = {f.name: f.stat().st_mtime for f in (t / 'figures').glob('*.pdf')}; subprocess.run(['python', str(t / 'scripts' / 'run_all_simulations.py')], cwd=str(t)); new_m = {f.name: f.stat().st_mtime for f in (t / 'figures').glob('*.pdf')}; updated = [k for k in orig if new_m[k] > orig[k]]; print('Updated inside bundle:', len(updated), 'Leaked in parent:', (t.parent / 'v2' / 'figures').exists())"
   ```
   *Actual output showing bug*: `Updated inside bundle: 0 Leaked in parent: True`.
