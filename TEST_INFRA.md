# Test Infrastructure Specification: Version 4 (v4) Overcomplete Perfect Vortex Beams (PVB)

**Project:** Propiedades Clásicas y Cuánticas de la Sobrecompletitud de los Haces de Vórtice Perfecto (PVB) — Versión 4 (v4)  
**Lead Author & Principal Investigator:** Sebastián Ayala (Investigador Independiente, Cauquenes, Región del Maule, Chile; `ayala.phys.ds@gmail.com`; ORCID: `https://orcid.org/0009-0003-7348-3883`)  
**E2E Test Architecture:** `test_writer_v4`  
**Master Test Suite:** `tests/test_v4_e2e.py`  
**Helper Utilities & Oracles:** `tests/test_helpers.py`  
**Status:** ACTIVE / OPERATIONAL (0 Failures, 0 Errors, Progressive Milestone Gating Active)  

---

## 1. Test Architecture & Verification Philosophy

The E2E Test Infrastructure for Version 4 (v4) provides an exhaustive, opaque-box, requirement-driven verification suite derived directly from `ORIGINAL_REQUEST.md` and `PROJECT.md § Feature Inventory`. It enforces mathematical completeness, physical rigor, total sanitization of internal project artifacts, and adherence to international publication ethics standards for arXiv and Q1 scientific journals (Optica Publishing Group / American Physical Society / Nature).

### 1.1 Core Principles
1. **Opaque-Box Requirement Derivation:** All test assertions evaluate external observables, file structures, and physical behavior directly against authoritative specifications rather than matching internal implementation shortcuts.
2. **First-Principles Mathematical Oracles:** Closed-form Bessel integrals (Gradshteyn-Ryzhik 6.633.2), continuous frame spectral bounds ($0 < A \le B < \infty$, $\kappa \approx 3.08$), the theoretical 8.60 dB decomposition in Ring-Core Fibers (RCF) ($6.83\,\text{dB}$ coupling + $1.77\,\text{dB}$ ISI penalty), and Informationally Complete POVM (IC-POVM) Cramér-Rao advantage ($2.71\times$ lower MSE) serve as authoritative, standalone oracles.
3. **Strict Sanitization & Zero Internal Artifacts:** Enforces complete absence of "Codex-Máxima", internal multi-agent bot codenames (e.g. `miner_lit_3`, `worker_arxiv_m2`, `critic_referee`, `teamwork_*`, `challenger_*`, etc.), and private iteration narratives (e.g. the v1 $\to$ v2 $\to$ v3 triad or internal sprint histories) across all manuscripts, bibliographies, and scripts.
4. **100% Citation Parity:** Enforces exact citation coverage across both manuscripts: all 70 BibTeX entries defined in `v4/references.bib` must be cited in both `Paper_arxiv_v4.tex` and `Paper_revista_v4.tex` with zero orphaned citations.
5. **Progressive Testability:** Mathematical oracles, simulation runners, and physical scaling laws are verified immediately, while deliverables belonging to active/planned implementation milestones (e.g., M2 arXiv/Revista manuscripts, M3 compiled PDFs and Overleaf bundle) are gated via `require_path(...)`. They skip cleanly during early phases and strictly fail when `--strict` or `FAIL_ON_PENDING=1` is asserted during the final audit gate (Milestone M4).
6. **Zero Tolerance for Facade Tests:** Dummy passes (`assert True`) or simulated outputs are strictly forbidden. All mathematical properties, file headers, and cross-feature references are evaluated dynamically.
7. **Adversarial Defensive Checks:** Includes negative test cases verifying that sanitization, abstract cleanliness, and Latin plural validators actively catch deliberate violations.
8. **Universal Portability:** Built on standard Python 3.12 (`unittest`, `math`, `re`, `pathlib`, `zipfile`, `subprocess`) and core scientific packages (`numpy`, `scipy`).

---

## 2. Four-Tier Testing Methodology

The v4 test suite is organized into four complementary verification tiers:

```
+-------------------------------------------------------------------------+
| Tier 4: Scientific Ethics, Epistemology & Human-AI Collaboration        |
| - Dedicated Section 8: "Epistemological Methodology and Human-AI       |
|   Scientific Collaboration" with 5 structured subsections                |
| - Paradigm shift: interactive generative cognitive symbiosis vs passive |
| - Epistemological accountability & human-in-the-loop (HITL) oversight   |
| - Research integrity: prevention and mitigation of hallucinations       |
| - Realistic technical case study: 8.60 dB RCF advantage (human         |
|   intuition directing AI calculation and drafting)                      |
| - Standard backmatter declaration conforming to COPE/Optica/APS/Nature  |
| - Scientific citations of peer-reviewed AI methodology literature (>=3) |
+-------------------------------------------------------------------------+
                                    ^
                                    |
+-------------------------------------------------------------------------+
| Tier 3: Step-by-Step Mathematical & Analytical Completeness             |
| - Theorem 1: Strict non-orthogonality & Bessel ODE linear independence  |
| - Theorem 2: Complete Seven Pillars of divergence as w0 -> 0            |
| - Theorem 3: Continuous frame bounds (0 < A <= S <= B) & kappa ~ 3.08   |
| - First-principles 8.60 dB RCF advantage: 6.83 dB coupling + 1.77 dB ISI|
| - Informationally Complete POVM (IC-POVM) Cramér-Rao advantage (2.71x)  |
| - Pedagogical Appendices A, B, C, D, and E full mathematical rigor      |
| - Reproducing kernel Gram matrix positive semi-definiteness             |
| - Bessel ODE Wronskian non-vanishing independence                       |
+-------------------------------------------------------------------------+
                                    ^
                                    |
+-------------------------------------------------------------------------+
| Tier 2: Sanitization & Cleanliness (Zero Internal Artifacts)            |
| - Zero occurrences of "Codex-Máxima" or internal repository folders     |
| - Zero occurrences of internal multi-agent bot codenames                |
| - Zero occurrences of internal sprint / iteration narratives (v1-v2-v3) |
| - Zero unresolved citations or '?' in LaTeX logs and TeX source         |
| - Exact 100% citation parity: both manuscripts cite all 70 BibTeX keys   |
| - Q1 Abstract cleanliness (no raw equations, no Eq. (N), no brackets)   |
| - Technical English spelling: Latin plural 'radii' strictly enforced    |
| - Exact author metadata string: "Sebastián Ayala", "Cauquenes",         |
|   "Región del Maule, Chile", email, and ORCID in both manuscripts       |
+-------------------------------------------------------------------------+
                                    ^
                                    |
+-------------------------------------------------------------------------+
| Tier 1: Deliverables & Structural Coverage                              |
| - Complete v4/ directory layout (v4/scripts/, v4/figures/, styles)      |
| - Preservation of baseline integrity: v1/, v2/, v3/ intact & unmodified|
| - Validated 70-entry BibTeX database (v4/references.bib)                |
| - Standalone Paper_arxiv_v4.tex (>300 lines, Sections 1 to 10)          |
| - Standalone Paper_revista_v4.tex (optica-article, linenumbers, macros) |
| - 6 reproducible scripts in v4/scripts/ (size > 0)                      |
| - 5 publication vector PDFs in v4/figures/ (magic bytes %PDF-)          |
| - Compiled PDFs existence with valid %PDF- magic bytes (<= 100 pages)   |
| - Complete standalone v4/overleaf_bundle_v4.zip package                 |
+-------------------------------------------------------------------------+
```

---

## 3. Test Execution Guide

### 3.1 Standard Test Execution (Progressive Milestone Mode)
Executes all testable deliverables, mathematical oracles, simulations, and adversarial validators. Pending milestone deliverables skip gracefully:
```powershell
python tests/test_v4_e2e.py
```
or via standard unittest:
```powershell
python -m unittest tests/test_v4_e2e.py
```

### 3.2 Strict Final Milestone Gate Execution (M4 Verification Gate)
In strict mode, any missing deliverable triggers an immediate assertion failure instead of skipping. This mode must be run to pass the Milestone M4 audit gate:
```powershell
python tests/test_v4_e2e.py --strict
```
or via environment variable:
```powershell
$env:FAIL_ON_PENDING="1"
python tests/test_v4_e2e.py
```

---

## 4. Test Inventory and Mapping Matrix

| Test ID | Test Method | Tier | Verified Requirement | Gated Dependency |
|---|---|---|---|---|
| TC 1.1 | `test_01_v4_directory_and_required_files` | Tier 1 | R1 (Deliverables layout, styles, tex, pdf, bib, zip) | Milestone M1, M2, M3 |
| TC 1.2 | `test_02_prior_versions_baseline_integrity` | Tier 1 | R1 (v1, v2, v3 intact & unmodified) | None (Immediate PASS) |
| TC 1.3 | `test_03_python_simulation_scripts_presence` | Tier 1 | R1 (6 scripts in `v4/scripts/`) | Milestone M1 |
| TC 1.4 | `test_04_python_simulation_execution_and_vector_figures` | Tier 1 | R1 (Execution & 5 figures in `v4/figures/`) | Milestone M1 |
| TC 1.5 | `test_05_compiled_pdfs_validity_and_page_budget` | Tier 1 | R1 (PDFs `%PDF-` header, $\le 100$ pages) | Milestone M3 |
| TC 1.6 | `test_06_overleaf_bundle_v4_zip_integrity_and_contents` | Tier 1 | R1 (`overleaf_bundle_v4.zip` packaging) | Milestone M3 |
| TC 2.1 | `test_01_zero_occurrences_of_codex_maxima` | Tier 2 | R4 (Zero "Codex Máxima" across all v4 files) | Milestone M1, M2 |
| TC 2.2 | `test_02_zero_occurrences_of_internal_bot_codenames` | Tier 2 | R4 (Zero bot codenames in TeX, Bib, Py) | Milestone M1, M2 |
| TC 2.3 | `test_03_zero_occurrences_of_internal_iteration_narratives` | Tier 2 | R4 (Zero v1->v2->v3 triad or sprint narratives) | Milestone M1, M2 |
| TC 2.4 | `test_04_zero_unresolved_citations_or_cross_references` | Tier 2 | R1, R4 (0 errors, 0 undefined citations, 0 `?`) | Milestone M3 |
| TC 2.5 | `test_05_exact_citation_parity_seventy_entries` | Tier 2 | R4 (100% citation parity: 70/70 cited in both) | Milestone M1, M2 |
| TC 2.6 | `test_06_abstract_cleanliness_q1_standards` | Tier 2 | R1 (No raw equations, No Eq. numbers, No brackets) | Milestone M2 |
| TC 2.7 | `test_07_technical_spelling_radii_plural` | Tier 2 | R1 (Latin plural 'radii' strictly enforced) | Milestone M2 |
| TC 2.8 | `test_08_exact_author_metadata_across_manuscripts` | Tier 2 | R1 (Exact author metadata string) | Milestone M2 |
| TC 3.1 | `test_01_theorems_coverage_in_tex_manuscripts` | Tier 3 | R2 (Theorems 1, 2, 3 covered in manuscripts) | Milestone M2 |
| TC 3.2 | `test_02_mathematical_oracle_continuous_frame_bounds_and_condition_number` | Tier 3 | R2 (Frame bounds $A, B$, $\kappa \approx 3.08$, Gram PSD) | None (Immediate PASS) |
| TC 3.3 | `test_03_first_principles_rcf_eight_point_six_db_derivation` | Tier 3 | R2 (8.60 dB RCF advantage: 6.83 dB + 1.77 dB) | Milestone M2 |
| TC 3.4 | `test_04_quantum_tomography_and_ic_povm` | Tier 3 | R2 (IC-POVM Cramér-Rao $2.71\times$ lower MSE) | Milestone M2 |
| TC 3.5 | `test_05_appendices_a_to_e_mathematical_rigor` | Tier 3 | R2 (Pedagogical Appendices A to E present) | Milestone M2 |
| TC 3.6 | `test_06_mathematical_oracle_overlap_subunitarity_and_wronskian` | Tier 3 | R2 ($0 < \gamma < 1$, Bessel Wronskian non-zero) | None (Immediate PASS) |
| TC 4.1 | `test_01_section_eight_dedicated_structure` | Tier 4 | R3 (Section 8 structure & 5 subsections) | Milestone M2 |
| TC 4.2 | `test_02_epistemological_principles_and_anti_hallucination` | Tier 4 | R3 (Cognitive symbiosis, HITL, anti-hallucination) | Milestone M2 |
| TC 4.3 | `test_03_realistic_technical_case_study` | Tier 4 | R3 (8.60 dB RCF case study: human intuition + AI) | Milestone M2 |
| TC 4.4 | `test_04_standard_backmatter_ai_declaration` | Tier 4 | R3, R4 (COPE/Optica/APS/Nature AI declaration) | Milestone M2 |
| TC 4.5 | `test_05_scientific_literature_citations_in_section_eight` | Tier 4 | R3 (>=3 peer-reviewed AI methodology citations) | Milestone M1, M2 |
| TC Adv.1 | `test_01_sanitization_validator_catches_all_prohibited_patterns` | Adv | Defensive (Sanitization validator flags violations) | None (Immediate PASS) |
| TC Adv.2 | `test_02_abstract_validator_catches_violations` | Adv | Defensive (Abstract validator flags bad math/cites) | None (Immediate PASS) |
| TC Adv.3 | `test_03_radii_validator_catches_errors` | Adv | Defensive (Radii validator flags non-standard plural) | None (Immediate PASS) |
