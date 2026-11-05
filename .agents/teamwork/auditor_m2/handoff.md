# Forensic Audit Report: Milestone 2 — Numerical Simulation Suite and Publication Figures

**Auditor:** Teamwork Forensic Auditor (`auditor_m2`)  
**Target:** Milestone 2 (`v2/scripts/` and `v2/figures/`)  
**Parent / Caller Agent:** `b896091e-9b49-4cdd-bfee-68e28ef0ca66`  
**Integrity Mode:** Development (per `ORIGINAL_REQUEST.md`)  
**Verdict:** **CLEAN**

---

## 1. Observation

1. **Test Harness Tampering Check (`tests/`):**
   - Executed `git status -s tests/` and `git diff tests/`.
   - Result:
     - `tests/test_helpers.py` was last modified on `2026-11-04 16:15:21` (during M1 initialization).
     - `tests/test_v2_suite.py` was created on `2026-11-04 16:19:32` (by `test_writer`).
     - `worker_m2` was dispatched at `2026-11-04 20:34:04` and wrote its handoff at `20:35:00`.
     - Zero files in `tests/` were created or altered by `worker_m2`. The test harness remained 100% untampered.

2. **Pre-Baked Figure Copy Detection (v1 vs v2 Comparison):**
   - Executed comparison script `.agents/teamwork/auditor_m2/compare_figures.py`:
     ```
     Figure                               | v1 Size    | v2 Size    | v1 SHA256 (first 12) | v2 SHA256 (first 12) | Identical?
     ------------------------------------------------------------------------------------------------------------------------
     fig1_pvb_profiles_divergence.pdf     | 52983      | 72411      | f6688525ca09         | 641b382e59d7         | DIFFERENT (FRESH)
     fig2_radial_overlap_matrix.pdf       | 64736      | 76612      | b2dd77fdef1f         | a7cc594a00ae         | DIFFERENT (FRESH)
     fig3_frame_spectrum_bounds.pdf       | 53481      | 108328     | 87151d1c2440         | 4d0484ba1016         | DIFFERENT (FRESH)
     fig4_turbulence_rkhs_recovery.pdf    | 159787     | 169542     | 109499cbe943         | a48096053a0d         | DIFFERENT (FRESH)
     fig5_quantum_povm_entanglement.pdf   | 66449      | 77550      | 4d19207cf762         | d8850de44ec9         | DIFFERENT (FRESH)
     ```
   - Verbatim observation: Every figure in `v2/figures/` has completely distinct file size and SHA256 checksum from `v1/figures/`. None are copied from v1.

3. **Dynamic Rendering Verification from Scratch:**
   - Deleted all files in `v2/figures/*.pdf` using `Remove-Item 'v2\figures\*.pdf' -Force`. Confirmed folder was empty.
   - Executed `python v2/scripts/run_all_simulations.py`:
     ```
     ================================================================================
           MASTER SIMULATION RUNNER: OVERCOMPLETE PVB PUBLICATION FIGURES (v2)
           Author: Sebastián Ayala (Cauquenes, Chile) | Milestone M2
     ================================================================================

     [*] Executing Job 1: Figure 1: PVB Intensity Profiles & Physical Divergence (2x2)...
     [+] Figure 1 successfully generated: ...\v2\figures\fig1_pvb_profiles_divergence.pdf
         [+] SUCCESS (1.05s) -> fig1_pvb_profiles_divergence.pdf [Valid vector PDF (70.7 KB)]

     [*] Executing Job 2: Figure 2: Radial Overlap Matrix & Universal Cross-Talk (2x2)...
     [+] Figure 2 successfully generated: ...\v2\figures\fig2_radial_overlap_matrix.pdf
         [+] SUCCESS (1.07s) -> fig2_radial_overlap_matrix.pdf [Valid vector PDF (74.8 KB)]

     [*] Executing Job 3: Figure 3: Continuous Frame Bounds & Dual Reconstruction (2x2)...
     [+] Figure 3 successfully generated: ...\v2\figures\fig3_frame_spectrum_bounds.pdf
         [+] SUCCESS (1.03s) -> fig3_frame_spectrum_bounds.pdf [Valid vector PDF (105.8 KB)]

     [*] Executing Job 4: Figure 4: Kolmogorov Turbulence & RKHS Noise Projection (2x2)...
     [+] Figure 4 successfully generated: ...\v2\figures\fig4_turbulence_rkhs_recovery.pdf
         [+] SUCCESS (0.84s) -> fig4_turbulence_rkhs_recovery.pdf [Valid vector PDF (165.6 KB)]

     [*] Executing Job 5: Figure 5: High-Dimensional POVM & SPDC Entanglement (2x2)...
     [+] Figure 5 successfully generated: ...\v2\figures\fig5_quantum_povm_entanglement.pdf
         [+] SUCCESS (0.84s) -> fig5_quantum_povm_entanglement.pdf [Valid vector PDF (75.7 KB)]

     ================================================================================
     Total Suite Execution Time: 4.83 seconds
     [+] ALL 5 PUBLICATION-QUALITY VECTOR FIGURES GENERATED & VALIDATED SUCCESSFULLY.
     ```
   - Verbatim observation: All 5 vector PDFs were dynamically created and verified in 4.83 seconds.

4. **Standalone Script Execution:**
   - Executed each simulation script independently:
     - `python v2/scripts/generate_fig1_profiles.py` -> exit code 0, generated valid PDF.
     - `python v2/scripts/generate_fig2_overlap.py` -> exit code 0, generated valid PDF.
     - `python v2/scripts/generate_fig3_frame_bounds.py` -> exit code 0, generated valid PDF.
     - `python v2/scripts/generate_fig4_turbulence.py` -> exit code 0, generated valid PDF.
     - `python v2/scripts/generate_fig5_quantum.py` -> exit code 0, generated valid PDF.

5. **Source Code & Mathematical Authenticity Inspection:**
   - Inspected `v2/scripts/generate_fig1_profiles.py` (209 lines):
     - Line 60: Exact radial norm via Gradshteyn & Ryzhik 6.633.2: `2.0 * np.pi * (w0**2 / 4.0) * float(ive(l, r0**2 / w0**2))`.
     - Line 75: `scipy.optimize.minimize_scalar` bounded optimizer for finding topological peak radius.
     - Line 147: Divergence scaling laws: $\langle k_r^2 \rangle \sim 1/w_0^2$, $M^2 \sim R_0/w_0$, $I_{\max} \propto 1/w_0$.
   - Inspected `v2/scripts/generate_fig2_overlap.py` (178 lines):
     - Line 54: Exact Weber integral overlap $\gamma_\ell(R_1, R_2; w_0)$ evaluated over $200 \times 200$ grid using `ive(l, z)`.
     - Line 70: Asymptotic expansion with 2nd-order curvature correction term.
   - Inspected `v2/scripts/generate_fig3_frame_bounds.py` (180 lines):
     - Line 65: 2D Gaussian smoothing kernel $G_w(\Delta \mathbf{r})$ on $200 \times 200$ spatial grid.
     - Line 89: Frame operator Fourier spectrum $\widetilde{G}_w(k) = \exp(-w_0^2 k^2 / 2)$.
     - Line 112: Frame bounds $A = \exp(-w_0^2 K_{\max}^2 / 2), B = 1.0$ and condition number $\kappa \approx 3.08$ at $\text{NA} = 0.15$.
   - Inspected `v2/scripts/generate_fig4_turbulence.py` (219 lines):
     - Line 47: 2D Kolmogorov phase screen generator using von Kármán power spectral density and 2D IFFT.
     - Line 184: Exact 8.6 dB RCF launch power advantage modeling at HD-FEC threshold ($4.7 \times 10^{-3}$).
   - Inspected `v2/scripts/generate_fig5_quantum.py` (175 lines):
     - Line 62: Continuous-discrete IC-POVM lattice in $(\ell, R)$ space.
     - Line 93: High-dimensional qudit ($d=8$) state tomography MSE showing $2.7\times$ lower variance.
     - Line 148: Two-photon SPDC entanglement Bell-CHSH parameter $S = 2\sqrt{2} \approx 2.828$.
   - Zero facade functions (`return <constant>`), zero mock classes, and zero hardcoded fake returns found.

6. **Layout, Typography, and Author Comment 3 Compliance:**
   - Ran `.agents/teamwork/auditor_m2/inspect_pdf_contents.py`:
     - Every script invokes `plt.subplots(2, 2, figsize=(8.5, 7.0), constrained_layout=True)`.
     - Panel titles use native bold attribute: `ax.set_title("...", fontweight="bold", fontsize=10.5)`.
     - MediaBox dimensions verified: ~620-647 pt wide by 512 pt high (4:3 aspect ratio).
     - Raw LaTeX text command scan: `Contains raw \textbf: False` across all 5 generated PDF files.

7. **Master Test Suite Execution:**
   - Executed `python tests/test_v2_suite.py`:
     - Total tests run: 34.
     - Passed: 20 (including all 6 M2-specific tests: `test_12_simulation_scripts_presence`, `test_13_publication_figure_pdfs_presence`, `test_02_script_multi_row_layouts_not_single_row`, `test_03_script_titles_no_raw_latex_textbf`, `test_04_parameter_consistency_text_scripts_captions`, `test_01_full_simulation_run_execution`).
     - Skipped: 14 (pending M3 LaTeX manuscripts and M4 bundle).
     - Failures: 0, Errors: 0.

---

## 2. Logic Chain

1. **Empirical Independence (Observation 1 & 2):**
   - The test harness files (`tests/test_v2_suite.py` and `tests/test_helpers.py`) were verified via git diff to be untouched by the worker. All assertions remain strictly independent.
   - The generated figures in `v2/figures/` were verified via cryptographic hash to be entirely distinct from `v1/figures/`, demonstrating that no pre-baked files were copied.

2. **Dynamism and Reproducibility (Observation 3 & 4):**
   - Completely wiping `v2/figures/*.pdf` and running `run_all_simulations.py` reproduced all 5 valid vector PDFs in under 5 seconds.
   - Running each individual script standalone verified modular execution without external mocking or artificial prerequisites.

3. **Authenticity of Implementation (Observation 5):**
   - Line-by-line inspection confirmed genuine mathematical models: exponentially scaled modified Bessel functions (`ive`), 2D FFT Kolmogorov phase screens, scalar minimization for peak detection, and numerical integration.
   - No hardcoded test result lookups or facade shortcuts exist in `v2/scripts/`.

4. **Author Comment 3 Resolution (Observation 6):**
   - The layout was refactored from single-row 1x3 into a spacious 2x2 grid (`figsize=(8.5, 7.0)`).
   - Raw `\textbf` formatting was eliminated in favor of native Matplotlib bold titles and math markup.
   - All PDF vector objects show valid font embeddings with zero LaTeX compilation artifacts.

5. **Test Suite Verification (Observation 7):**
   - `python tests/test_v2_suite.py` passed with 0 failures and 0 errors, confirming full contractual compliance with Milestone 2 specifications.

---

## 3. Caveats

- **Challenger Test Regex Artifact:**
  - In `tests/test_milestone2_adversarial_challenger.py` (authored concurrently by challenger agent), a regular expression `\.set_title\s*\(\s*([^\n\)]+)\)` prematurely terminates matching at the closing parenthesis of `(a)` in `"(a) ..."`, failing to see `fontweight="bold"` placed later in the argument list.
  - As observed in Observation 6 and verified by `tests/test_v2_suite.py:test_03_script_titles_no_raw_latex_textbf`, all title calls in `v2/scripts/` strictly contain `fontweight="bold"`. This is an artifact of the challenger test regex, not a defect or integrity violation in the scripts.
- **Milestone Scope:**
  - Milestone 2 covers the simulation scripts and figures only. Manuscript text integration (`Paper_arxiv_v2.tex`, `Paper_revista_v2.tex`) is the scope of Milestone 3.

---

## 4. Conclusion & Verdict

Milestone 2 deliverables are authentic, fully reproducible, mathematically grounded, and strictly free of integrity violations:
- **Verdict:** **CLEAN**
- All 5 simulation scripts genuinely compute physical models and dynamically generate vector PDFs.
- Figures are freshly rendered in 2x2 multi-panel layout, resolving Author Comment 3.
- The test harness was untouched and all master test suite checks passed with 0 failures.

---

## 5. Verification Method

To independently verify this verdict:

1. **Run Master Simulation Runner:**
   ```powershell
   python v2/scripts/run_all_simulations.py
   ```
   *Expected:* Exit code 0, 5/5 jobs report PASSED in ~5 seconds, generating valid vector PDFs.

2. **Wipe and Regenerate Figures (Dynamic Generation Proof):**
   ```powershell
   Remove-Item 'v2\figures\*.pdf' -Force
   python v2/scripts/run_all_simulations.py
   Get-ChildItem 'v2\figures\*.pdf' | Select-Object Name, Length, LastWriteTime
   ```
   *Expected:* 5 fresh PDF files between 70 KB and 170 KB with current timestamps.

3. **Verify Figure Hashes vs v1 (No Blind Copying):**
   ```powershell
   python .agents/teamwork/auditor_m2/compare_figures.py
   ```
   *Expected:* All 5 figures report `DIFFERENT (FRESH)`.

4. **Verify Absence of Raw \textbf and 2x2 Layout:**
   ```powershell
   python .agents/teamwork/auditor_m2/inspect_pdf_contents.py
   ```
   *Expected:* MediaBox ~620-647 x 512 pt, `Contains raw \textbf: False`.

5. **Run Master E2E Test Suite:**
   ```powershell
   python tests/test_v2_suite.py
   ```
   *Expected:* Ran 34 tests, Passed: 20, Skipped: 14, Failures: 0, Errors: 0.
