# Technical & Computational Review Report (Milestone M5)

**Reviewer**: `reviewer_2` (Roles: reviewer, critic)  
**Parent / Dispatcher**: Project Orchestrator (`13cbe3c5-df6c-41a9-8cfd-c1094a82e1c5`)  
**Date**: 2026-11-04  
**Verdict**: **REQUEST_CHANGES**

---

## 1. Executive Summary & Verdict

**Verdict**: **REQUEST_CHANGES**

While the Python simulations and mathematical models in `v1/scripts/` are technically outstanding and numerically rigorous, and the test suite passes all 81 opaque-box tests, an adversarial inspection of the LaTeX compilation artifacts revealed **three critical compilation defects** in `v1/Paper_revista_v1.tex` and `v1/Paper_arxiv_v1.tex`, which are also packaged directly into `v1/overleaf_bundle.zip`. 

Under strict compilation (`pdflatex -halt-on-error` and `bibtex`), both manuscripts **fail with fatal errors**. In non-stop mode, they produce severe typographical anomalies (missing proof environments, unformatted proof blocks, and overfull horizontal boxes exceeding 280 points). These defects directly violate Acceptance Criteria for Requirement R3 (*"Ambos documentos LaTeX compilan limpiamente sin errores fatales y están estructurados para subirse directamente a Overleaf"*).

Drop-in solutions have been independently verified in an isolated environment and confirmed to yield 100% clean compilation with zero warnings, zero undefined citations, and zero undefined references.

---

## 2. Quality Review

### Verified Claims
- **Python Simulations**: All 6 scripts in `v1/scripts/` (`generate_fig1_profiles.py`, `generate_fig2_overlap.py`, `generate_fig3_frame_bounds.py`, `generate_fig4_turbulence.py`, `generate_fig5_quantum.py`, and `run_all_simulations.py`) execute without error via `python v1/scripts/run_all_simulations.py` in **5.29 seconds**.
- **Vector Figures**: All 5 figures in `v1/figures/` exist as valid, uncorrupted, single-page vector PDFs with embedded font subsets (5 to 8 fonts per figure, sizes between 52 KB and 160 KB).
- **Test Suite**: `python tests/test_e2e_runner.py` reports 81/81 passed tests (100% pass rate).
- **Manuscript Length**: Compiled PDFs are well within the $\le 100$ page constraint (`Paper_arxiv_v1.pdf` is 19 pages; `Paper_revista_v1.pdf` is 18 pages).
- **Author Metadata & Ethics**: Sebastián Ayala is accurately designated as first and sole author with affiliation `Investigador Independiente / Independent Researcher, Cauquenes, Región del Maule, Chile`, email `ayala.phys.ds@gmail.com`, and ORCID `0009-0003-7348-3883`. A formal COPE/Optica/APS compliant AI declaration is included in both manuscripts (Section 9 / back matter).
- **Pedagogical Appendices**: All 4 planned appendices (A: PVB Primer, B: Hilbert Bases, C: Frame Theory, D: Derivations) are present in full depth and cross-referenced in the text.

### Coverage Gaps
- **LaTeX Compilation Test Coverage**: `tests/test_tier1_feature_coverage.py` and `test_tier4_real_world_scenarios.py` inspect existing binary PDFs and zip archives, but **never execute the LaTeX compiler (`pdflatex -halt-on-error`) or `bibtex`**. This allowed fatal compilation errors to remain hidden behind the 100% passing test dashboard.

### Findings

#### [Critical] Finding 1: Undefined `proof` Environment in `Paper_revista_v1.tex`
- **Location**: `v1/Paper_revista_v1.tex`, Lines 205, 217, 230, 281, 341, 347.
- **Verbatim Error**:
  ```text
  ! LaTeX Error: Environment proof undefined.
  l.205 \begin{proof}
  ! LaTeX Error: \begin{document} ended by \end{proof}.
  l.217 \end{proof}
  ```
- **Why**: `optica-article.cls` does not define `proof` or load `amsthm`. When `\begin{proof}` is called, LaTeX ignores the command, and `\end{proof}` triggers a document-ending error. Because `newtxmath` (loaded by `optica-article`) defines `\openbox`, simply loading `\usepackage{amsthm}` causes `! LaTeX Error: Command \openbox already defined.`
- **Required Fix**: In the preamble of `v1/Paper_revista_v1.tex`, add:
  ```latex
  \let\openbox\relax
  \usepackage{amsthm}
  ```

#### [Critical] Finding 2: Unescaped Underscores in Markdown Backticks Causing Fatal Math Shifts & Overfull Hboxes
- **Location**: `v1/Paper_arxiv_v1.tex` (Line 428) and `v1/Paper_revista_v1.tex` (Line 421).
- **Verbatim Code**:
  ```latex
  To validate all analytical theorems, frame bounds, and physical advantages, numerical simulations were executed and compiled into five publication-grade figures (`figures/fig1_pvb_profiles_divergence.pdf` through `figures/fig5_quantum_povm_entanglement.pdf`).
  ```
- **Verbatim Error**:
  ```text
  ! Missing $ inserted.
  <inserted text> 
                  $
  l.428 ...publication-grade figures (`figures/fig1_
                                                    pvb_profiles_divergence.pd...
  Overfull \hbox (288.11009pt too wide) in paragraph at lines 428--429
  ```
- **Why**: The filenames contain raw underscores `_` wrapped in backticks (markdown syntax). In TeX, `_` is a math subscript trigger, causing TeX to insert `$` and create an enormous 288 pt overfull line that spills off the page.
- **Required Fix**: Replace the backticked filenames with LaTeX references, e.g.:
  ```latex
  To validate all analytical theorems, frame bounds, and physical advantages, numerical simulations were executed and compiled into five publication-grade figures (Figs.~1--5).
  ```

#### [Major] Finding 3: Duplicate `\bibliographystyle` Command Breaking BibTeX
- **Location**: `v1/Paper_revista_v1.tex`, Lines 655--656.
- **Verbatim Code**:
  ```latex
  \bibliography{references}
  \bibliographystyle{opticajnl}
  ```
- **Verbatim Error in `Paper_revista_v1.blg`**:
  ```text
  Illegal, another \bibstyle command---line 140 of file Paper_revista_v1.aux
   : \bibstyle
   :          {opticajnl}
  I'm skipping whatever remains of this command
  ```
- **Why**: `optica-article.cls` automatically declares `\bibliographystyle{opticajnl}` internally. Calling it again manually causes BibTeX to fail with exit code 1.
- **Required Fix**: Delete line 656 (`\bibliographystyle{opticajnl}`) from `v1/Paper_revista_v1.tex`.

#### [Critical] Finding 4: Defective Files Bundled into `v1/overleaf_bundle.zip`
- **Location**: `v1/overleaf_bundle.zip`.
- **Why**: The zip archive contains the uncorrected versions of `Paper_arxiv_v1.tex` and `Paper_revista_v1.tex`. A user uploading this bundle directly to Overleaf will experience immediate red compilation stops.
- **Required Fix**: Rebuild `v1/overleaf_bundle.zip` after applying the fixes to both `.tex` files.

---

## 3. Adversarial Stress-Testing & Integrity Audit

**Overall Risk Assessment**: **HIGH** (Compilation blocker for end users; zero scientific or computational integrity issues).

### Integrity Check Results
1. **Hardcoded test outputs**: **CLEAN**. Numerical calculations in `test_helpers.py` use real numerical quadrature (`scipy.integrate.quad`) and Bessel series (`ive`). Simulations calculate real SVDs, FFTs, and scalar optimizations.
2. **Facade implementations**: **CLEAN**. Physics code is authentic and mathematically rigorous.
3. **Shortcuts & delegation**: **CLEAN**. Equations, proofs, and scripts are built natively.
4. **Self-certifying test runner**: **VULNERABILITY IDENTIFIED**. The test harness checked that `pdf_path.exists()` and read page numbers from binary PDF headers without compiling the TeX sources under `-halt-on-error`.

### Stress Test Matrix

| Scenario | Tested Against | Result | Finding |
|---|---|---|---|
| Run `v1/scripts/run_all_simulations.py` | Python 3.12, NumPy, SciPy, Matplotlib | **PASS** (5.29s) | All 5 PDFs generated, valid magic header `%PDF-`, size 52–160 KB |
| Vector typography & font embedding | `pypdf.PdfReader` font dictionary inspection | **PASS** | 5 to 8 embedded Type 1 / TrueType fonts per figure |
| Full E2E Test Suite | `tests/test_e2e_runner.py` (Tiers 1–4) | **PASS** (81/81, 0.149s) | 100% passed |
| Strict arXiv LaTeX compilation | `pdflatex -halt-on-error Paper_arxiv_v1.tex` | **FAIL** (RC=1) | Missing `$` on line 428 (unescaped `_`) |
| Strict Journal LaTeX compilation | `pdflatex -halt-on-error Paper_revista_v1.tex` | **FAIL** (RC=1) | Undefined environment `proof` on line 205 |
| BibTeX execution for Journal | `bibtex Paper_revista_v1` | **FAIL** (RC=1) | Duplicate `\bibstyle` on line 656 |
| Overleaf bundle extraction & test build | Unpack `v1/overleaf_bundle.zip` and compile | **FAIL** (RC=1) | Propagates all 3 compilation failures |

---

## 4. 5-Component Handoff Report

### 1. Observation
- `pdflatex -halt-on-error Paper_revista_v1.tex` failed with:
  `! LaTeX Error: Environment proof undefined.` at `l.205 \begin{proof}`.
- `pdflatex -halt-on-error Paper_arxiv_v1.tex` failed with:
  `! Missing $ inserted.` at `l.428 ...(`figures/fig1_pvb_profiles_divergence.pdf`...`.
- `bibtex Paper_revista_v1` exited with code 1 and logged:
  `Illegal, another \bibstyle command---line 140 of file Paper_revista_v1.aux`.
- `v1/overleaf_bundle.zip` contains `Paper_arxiv_v1.tex` and `Paper_revista_v1.tex` with these exact errors.
- Python simulations executed successfully:
  `v1/scripts/run_all_simulations.py` generated all 5 figures in 5.29s.

### 2. Logic Chain
1. Acceptance Criteria state: *"Ambos documentos LaTeX compilan limpiamente sin errores fatales y están estructurados para subirse directamente a Overleaf."*
2. Observation confirms `Paper_revista_v1.tex` and `Paper_arxiv_v1.tex` fail with fatal errors under standard strict LaTeX compilation and produce overfull horizontal boxes and broken proof blocks in non-stop mode.
3. Observation confirms `v1/overleaf_bundle.zip` packages these defective files.
4. An isolated test applying the three minimal fixes demonstrated that both documents compile with exit code 0 on both `pdflatex` and `bibtex`, producing clean 19-page and 18-page PDFs with 0 undefined citations and 0 undefined references.
5. Therefore, the deliverable cannot be approved in its current state, but requires these specific, localized changes.

### 3. Caveats
- No caveats regarding theoretical physics derivations, simulation accuracy, or author attribution: all are verified to be of high scientific quality.

### 4. Conclusion
Milestone M5 deliverables are complete in scientific content and computational execution, but require changes to fix LaTeX compilation defects before publication release. Verdict is **REQUEST_CHANGES**.

### 5. Verification Method
To verify the fixes independently:
1. In `v1/Paper_revista_v1.tex`:
   - Add `\let\openbox\relax \usepackage{amsthm}` in preamble (after `\usepackage{amsfonts}`).
   - Replace line 421 with `(Figs.~1--5).`
   - Remove line 656 `\bibliographystyle{opticajnl}`.
2. In `v1/Paper_arxiv_v1.tex`:
   - Replace line 428 with `(Figs.~1--5).`
3. Re-compile both documents:
   ```powershell
   & "C:\Users\sayal\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe" -halt-on-error v1/Paper_arxiv_v1.tex
   & "C:\Users\sayal\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe" -halt-on-error v1/Paper_revista_v1.tex
   & "C:\Users\sayal\AppData\Local\Programs\MiKTeX\miktex\bin\x64\bibtex.exe" v1/Paper_revista_v1
   ```
   Both commands must exit with code 0.
4. Repackage `v1/overleaf_bundle.zip` and verify archive extraction.
