# Test Infrastructure Specification: Overcomplete Perfect Vortex Beams (PVB)

**Author:** E2E Test Writer Subagent (`e2e_tester_1`)  
**Project:** Overcomplete Perfect Vortex Beams (PVB) — Theory, Simulation & Publication  
**Lead Author & Principal Investigator:** Sebastián Ayala (Independent Researcher, Cauquenes, Región del Maule, Chile; `ayala.phys.ds@gmail.com`; ORCID: `https://orcid.org/0009-0003-7348-3883`)  
**Date:** 2026-11-04  
**Status:** ACTIVE / OPERATIONAL  

---

## 1. Test Philosophy & Principles

The E2E Test Infrastructure for the PVB research project is built upon rigorous mathematical verification, physical constraint enforcement, and opaque-box validation against the formal requirements stated in `ORIGINAL_REQUEST.md` and `PROJECT.md`.

### 1.1 Core Principles
1. **Opaque-Box Requirement-Driven Testing:** Tests validate functional and physical behaviors against requirements rather than matching internal implementation shortcuts.
2. **Mathematical & Physical Rigor:** Equations, integrals, Bessel identities, frame bounds, and asymptotic behaviors are verified with analytical proofs, symbolic algebraic verification (`sympy`), and high-precision numerical quadrature (`scipy.integrate.quad`).
3. **Progressive Testability:** The test suite evaluates foundational mathematics, physical proofs, and structural assets immediately, while providing clear, structured progress tracking ("PENDING DELIVERABLE") for milestones currently undergoing active authoring by worker subagents (e.g., M2 simulation scripts, M3 LaTeX manuscripts, M4 compiled PDFs).
4. **Zero Tolerance for Facade Tests:** Every test performs non-trivial assertions. Cheating, dummy assertions (`assert True`), or fabricated data are strictly prohibited and subject to independent audit.
5. **Portability and Zero External Friction:** The test suite operates using the native Python 3.12 standard library (`unittest`, `math`, `re`, `pathlib`, `zipfile`) combined with standard scientific libraries (`numpy`, `scipy`, `sympy`).

---

## 2. Four-Tier Testing Methodology

The test suite is structured across four distinct verification tiers:

```
           +-----------------------------------------------------------+
           | Tier 4: Real-World Workloads & E2E Packaging             |
           | (Overleaf ZIP, Readability Flow, Resource Verification)   |
           +-----------------------------------------------------------+
                                        ^
                                        |
           +-----------------------------------------------------------+
           | Tier 3: Cross-Feature Pairwise Consistency               |
           | (LaTeX Formulas == Python Code, Figures, BibTeX Keys)     |
           +-----------------------------------------------------------+
                                        ^
                                        |
           +-----------------------------------------------------------+
           | Tier 2: Boundary, Corner & Limit Stress Cases             |
           | (w0 -> 0, r0 >> w0, l >> 1, Malformed/Corrupted Inputs)   |
           +-----------------------------------------------------------+
                                        ^
                                        |
           +-----------------------------------------------------------+
           | Tier 1: Core Feature Coverage (>=5 tests per feature)    |
           | (Author, Ethics, Appendices, Math, Bounds, Scripts, etc.) |
           +-----------------------------------------------------------+
```

### 2.1 Tier 1: Feature Coverage (>= 5 Test Cases per Feature Group)
Validates primary requirements across 9 key functional domains:
- **Group 1: Author Metadata Verification:** Verifies Sebastián Ayala as first author, independent researcher affiliation, Cauquenes, Maule, Chile, contact email `ayala.phys.ds@gmail.com`, and ORCID link `https://orcid.org/0009-0003-7348-3883`.
- **Group 2: AI Ethics Declaration Compliance:** Verifies formal disclosure of AI collaborative assistance under author supervision, COPE/Optica/APS compliance, full author responsibility clause, and explicit description of assistance scope.
- **Group 3: Educational Appendices (A, B, C, D):** Verifies dedicated educational appendices: Appendix A (PVB Primer), Appendix B (Complete Hilbert Bases & Gel'fand Triplets), Appendix C (Overcomplete Frames & RKHS), and Appendix D (Mathematical Integrals & Asymptotics).
- **Group 4: Exact Closed-Form Inner Product & Bessel Identities:** Verifies Gradshteyn-Ryzhik formula 6.633.2, modified Bessel ratio $\gamma_l(r_1, r_2; w_0) = \frac{I_l(r_1 r_2 / w_0^2)}{\sqrt{I_l(r_1^2/w_0^2) I_l(r_2^2/w_0^2)}}$, numerical quadrature equivalence to machine precision ($< 10^{-12}$), and asymptotic Gaussian match.
- **Group 5: Continuous Frame Bounds on Paraxial Subspace:** Verifies Duffin-Schaeffer continuous frame condition $0 < A \le B < \infty$, strictly positive spectrum $\sigma(k_r) = e^{-\frac{1}{2} k_r^2 w_0^2}$, condition number $\kappa = B/A \approx 3$, and frame operator invertibility on $\mathcal{H}_{\text{band}}$.
- **Group 6: Physical Unfeasibility Proofs ($w_0 \to 0$ Divergence):** Verifies proof of divergence of peak intensity $I_{\max} \propto 1/w_0$, vanishing transmitted power under material breakdown field clamping, non-$L^2$ Dirac delta distribution, and diffraction lower bound $w_0 \ge \lambda f / (\pi D)$.
- **Group 7: Simulation Scripts Execution & Figure Generation:** Verifies presence and execution of `generate_fig1` to `generate_fig5` and `run_all_simulations.py`, validating output figures `fig1_...pdf` to `fig5_...pdf`.
- **Group 8: Compilation & Overleaf Asset Packaging:** Verifies LaTeX package integrity, class files (`optica-article.cls`), bibliography style (`opticajnl.bst`), journal style package (`styles/opticajournal.sty`), abbreviation databases (`jabbrv*.ldf`), absence of duplicate packages, and compilation tests.
- **Group 9: Page Count & Layout Enforcement:** Verifies that both arXiv and journal papers adhere to the strict limit of $\le 100$ pages (target ~26–34 pages) and maintain required structural document environments.

### 2.2 Tier 2: Boundary, Corner & Limit Stress Cases (>= 5 Tests per Feature Category)
Stress-tests extreme regimes and failure conditions:
- **Category 1: Singular Limit $w_0 \to 0$:** Evaluates asymptotic divergence behavior of intensity, exponential expansion of spatial bandwidth $K_{\max}$, overlap vanishing for $r_1 \neq r_2$, and numerical stability of modified Bessel quotients as $w_0 \to 0$.
- **Category 2: Thin-Ring / Large Radius Limit $r_0 \gg w_0$:** Tests asymptotic Gaussian annular approximation fidelity, quadratic error scaling $\mathcal{O}(w_0^2 / r_0^2)$, and topological radial shift $\Delta r_l \approx \frac{(4l^2-1)w_0^2}{32 r_0}$.
- **Category 3: High Topological Charge $l \gg 1$:** Tests stability of Bessel evaluations for high charges ($l = 10, 50, 100$), invariance of geometric ring radius $r_0$ across charge $l$, azimuthal phase periodicity $e^{i l (\phi + 2\pi)} = e^{i l \phi}$, and modal orthogonality $\langle \psi_{l_1} | \psi_{l_2} \rangle = 0$ for $l_1 \neq l_2$.
- **Category 4: Malformed, Missing & Negative Inputs:** Asserts that mathematical functions and simulation scripts reject non-physical inputs (negative ring width $w_0 \le 0$, negative radius $r_0 < 0$, non-positive wavelength $\lambda \le 0$, and invalid numerical apertures $\text{NA} > 1.0$).
- **Category 5: File Corruption & Structural Resilience:** Tests detection of corrupted LaTeX environments, unclosed math blocks, broken BibTeX syntax, missing figure dependencies, and incomplete packaging.

### 2.3 Tier 3: Cross-Feature Pairwise Consistency
Validates seamless synchronization between distinct project artifacts:
- **LaTeX Math $\leftrightarrow$ Python Simulations:** Ensures that mathematical expressions written in LaTeX in `Paper_arxiv_v1.tex` and `Paper_revista_v1.tex` strictly match the numerical expressions implemented in `v1/scripts/`.
- **LaTeX Figures $\leftrightarrow$ Script Output Files:** Verifies that every `\includegraphics` target in LaTeX exists and matches the exact filenames generated by `generate_figX_...py`.
- **Bibliography $\leftrightarrow$ In-Text Citations:** Verifies that every `\cite{...}` in both manuscripts has a corresponding `@article`/`@book` key in `v1/references.bib` with complete metadata (author, title, journal, volume, year, DOI), and flags orphaned references.
- **Metadata Consistency:** Verifies that author names, affiliations, emails, and ORCIDs are 100% identical across arXiv, journal, and project documentation.
- **Appendices $\leftrightarrow$ Main Text Referencing:** Validates that all appendices (A through D) are cross-referenced in the main body text.

### 2.4 Tier 4: Real-World Application Workloads
Simulates real-world academic publication and user deployment:
- **Standalone Overleaf ZIP Readiness:** Assembles and validates an in-memory or physical ZIP archive containing the complete paper package, ensuring relative file paths are self-contained without referencing parent directories or external tools.
- **Full Paper Readability & Flow:** Verifies the logical document hierarchy from title, abstract, introduction, physical theory, numerical simulations, classical/quantum advantages, conclusions, AI ethics declaration, appendices, to bibliography.
- **Verification Resources Continuity:** Verifies that historical literature citations (`Codex Máxima/`) are cited and integrated into the manuscript bibliography and derivations.

---

## 3. Comprehensive Feature Inventory Test Mapping

Every feature defined in `PROJECT.md` is mapped directly to corresponding test implementations:

| Feature # | Feature Name | Milestone | Test Module | Test Class & Methods | Pass Criteria |
|---|---|---|---|---|---|
| **F1** | Editorial Viability & Journal Selection | M1 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f01_journal_selection_scope` | Explicit justification of Optics Express (Q1) and Physical Review A (Q1/Q2) documented |
| **F2** | Exact Analytical PVB Inner Product | M1 | `test_tier1_feature_coverage.py`, `test_tier2_boundary_corner_cases.py` | `TestFeatureCoverage.test_f02_exact_inner_product_formula`, `test_f02_numerical_quadrature_equivalence` | Analytical formula matches Gradshteyn-Ryzhik 6.633.2 within machine precision ($< 10^{-12}$) |
| **F3** | Impossibility of Strict Orthonormal Basis | M1 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f03_strictly_positive_overlap` | Overlap $\gamma_l(r_1, r_2; w_0) > 0$ strictly for all finite $r_1, r_2 \in (0, \infty)$ |
| **F4** | Physical Unfeasibility of Singular Limit $w_0 \to 0$ | M1 | `test_tier1_feature_coverage.py`, `test_tier2_boundary_corner_cases.py` | `TestFeatureCoverage.test_f04_divergence_peak_intensity`, `test_f04_power_vanishing_field_clamping`, `test_f04_diffraction_lower_bound` | Proof demonstrated: $I_{\max} \propto 1/w_0 \to \infty$, $P \propto w_0 \to 0$, $w_0 \ge \frac{2\lambda f}{\pi D}$ |
| **F5** | Continuous Frame Formalism on Paraxial Subspace | M1 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f05_continuous_frame_bounds_positive`, `test_f05_condition_number_well_behaved` | Bounds $0 < A \le B < \infty$ with condition number $\kappa \approx 3$ on $\mathcal{H}_{\text{band}}$ |
| **F6** | Classical Advantages of Overcompleteness | M1 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f06_classical_advantages_presence` | Multi-ring SDM, RKHS noise projection, and clipping self-healing documented and proved |
| **F7** | Quantum Advantages of Overcompleteness | M1 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f07_quantum_advantages_presence` | POVM quantum tomography, aperture preservation in HD-QKD, and SPDC entanglement robustness proved |
| **F8** | Literature Continuity with Codex Máxima | M1 | `test_tier4_real_world_scenarios.py` | `TestRealWorldScenarios.test_f08_codex_maxima_citations` | Citation and mathematical unification with Ferreira et al. (2026) and Vaity & Rusch (2015) |
| **F9** | Python Simulation Fig 1: Profiles & Divergence | M2 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f09_fig1_script_and_output` | `generate_fig1_profiles.py` exists, executes, and outputs vector PDF `fig1_...pdf` |
| **F10** | Python Simulation Fig 2: Radial Overlap Matrix | M2 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f10_fig2_script_and_output` | `generate_fig2_overlap.py` exists, executes, and outputs vector PDF `fig2_...pdf` |
| **F11** | Python Simulation Fig 3: Frame Bounds | M2 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f11_fig3_script_and_output` | `generate_fig3_frame_bounds.py` exists, executes, and outputs vector PDF `fig3_...pdf` |
| **F12** | Python Simulation Fig 4: Turbulence & RKHS Recovery | M2 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f12_fig4_script_and_output` | `generate_fig4_turbulence.py` exists, executes, and outputs vector PDF `fig4_...pdf` |
| **F13** | Python Simulation Fig 5: Quantum POVM & Entanglement | M2 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f13_fig5_script_and_output` | `generate_fig5_quantum.py` exists, executes, and outputs vector PDF `fig5_...pdf` |
| **F14** | Master Simulation Runner | M2 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f14_master_runner_execution` | `run_all_simulations.py` executes all five figure generations sequentially without errors |
| **F15** | Primary Journal Manuscript (`Paper_revista_v1.tex`) | M3 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f15_journal_manuscript_structure` | `v1/Paper_revista_v1.tex` exists, uses `optica-article.cls`, contains complete scientific sections |
| **F16** | arXiv Preprint Manuscript (`Paper_arxiv_v1.tex`) | M3 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f16_arxiv_manuscript_structure` | `v1/Paper_arxiv_v1.tex` exists, contains self-contained preamble and bbl compatibility |
| **F17** | Author Information & Affiliation | M3 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f17_author_metadata_complete` (5 sub-checks) | Sebastián Ayala, Cauquenes, Chile, email, and ORCID present across both manuscripts |
| **F18** | Formal AI Ethics Declaration | M3 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f18_ai_ethics_declaration_compliance` (5 sub-checks) | Formal COPE/Optica/APS compliant AI declaration present with author responsibility clause |
| **F19** | Appendix A: Pedagogical Primer on PVBs | M3 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f19_appendix_a_pvb_primer` | Comprehensive tutorial explaining Helmholtz equation, axicon, SPP, and Fourier transformation |
| **F20** | Appendix B: Complete Bases in Hilbert Spaces | M3 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f20_appendix_b_hilbert_bases` | Rigorous exposition of Schauder bases, Parseval identity, and Gel'fand triplets ($\Phi \subset \mathcal{H} \subset \Phi^\times$) |
| **F21** | Appendix C: Overcomplete Bases & Frame Theory | M3 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f21_appendix_c_frame_theory` | Complete exposition of Duffin-Schaeffer frames, continuous frames, dual frames, and RKHS |
| **F22** | Appendix D: Mathematical Derivations | M3 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f22_appendix_d_derivations` | Step-by-step derivations of Gradshteyn-Ryzhik integral and asymptotic expansions |
| **F23** | Comprehensive Bibliography Database | M3 | `test_tier1_feature_coverage.py`, `test_tier3_cross_feature_combinations.py` | `TestFeatureCoverage.test_f23_bib_database_integrity`, `TestCrossFeatureConsistency.test_f23_all_citations_defined` | Complete `references.bib` with zero missing citations and valid BibTeX syntax |
| **F24** | Overleaf & Directory Asset Packaging | M4 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f24_overleaf_asset_packaging` | Class, style, and BST files present in `v1/` (`optica-article.cls`, `styles/`, etc.) |
| **F25** | LaTeX & PDF Compilation | M4 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f25_compilation_readiness` | Clean compilation to `Paper_arxiv_v1.pdf` and `Paper_revista_v1.pdf` without fatal errors |
| **F26** | Length Verification (<= 100 pages) | M4 | `test_tier1_feature_coverage.py` | `TestFeatureCoverage.test_f26_page_count_enforcement` | Both PDFs verified strictly $\le 100$ pages (target ~26–34 pages) |
| **F27** | E2E Test Suite Creation | E2E Track | `test_e2e_runner.py` | `test_e2e_runner.py` self-execution | All 4 test tiers execute cleanly with unified reporting and metrics |
| **F28** | 100% E2E Test Pass & Hardening (Tier 5) | M5 | `test_e2e_runner.py` | Runner terminal execution | 100% pass on completed features, zero regressions |
| **F29** | Forensic Integrity Audit | M5 | `teamwork_auditor` | Audit report | Zero fabrications, zero mock passes, zero integrity violations |

---

## 4. Test Directory Architecture

```
tests/
├── __init__.py                                 # Test package initialization
├── test_e2e_runner.py                          # Master test runner and aggregator
├── test_tier1_feature_coverage.py              # Tier 1: Functional feature coverage
├── test_tier2_boundary_corner_cases.py         # Tier 2: Boundary, corner & limit stress cases
├── test_tier3_cross_feature_combinations.py    # Tier 3: Pairwise cross-feature consistency
└── test_tier4_real_world_scenarios.py          # Tier 4: Real-world workloads & packaging
```

---

## 5. Execution Instructions & CLI Specification

### 5.1 Primary Test Runner (Recommended)
To execute the complete E2E test suite with formatted console reporting, progress tracking, and tier aggregation:

```bash
python tests/test_e2e_runner.py
```

### 5.2 Standard Unittest Runner
To run via Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### 5.3 Individual Tier Execution
To execute individual tiers independently:

```bash
# Tier 1: Feature Coverage
python -m unittest tests/test_tier1_feature_coverage.py -v

# Tier 2: Boundary & Corner Cases
python -m unittest tests/test_tier2_boundary_corner_cases.py -v

# Tier 3: Cross-Feature Combinations
python -m unittest tests/test_tier3_cross_feature_combinations.py -v

# Tier 4: Real-World Scenarios
python -m unittest tests/test_tier4_real_world_scenarios.py -v
```

### 5.4 Exit Codes & Interpretation
- **Exit Code 0:** All active tests passed cleanly. Any pending deliverables are reported with transparent milestone dependencies.
- **Exit Code 1:** One or more regression test failures or integrity violations detected.
