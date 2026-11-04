# Project: Overcomplete Perfect Vortex Beams (PVB) — Theory, Simulation & Publication

## Architecture
This project develops a complete, mathematically rigorous, and publication-ready scientific article (for arXiv and a Q1/Q2 journal, Optics Express / Physical Review A) authored by **Sebastián Ayala** (Independent Researcher, Cauquenes, Región del Maule, Chile; `ayala.phys.ds@gmail.com`; ORCID: `https://orcid.org/0009-0003-7348-3883`).

The architecture establishes a dual-track workflow:
1. **Implementation Track**:
   - **Milestone 1 (Mathematical Foundations & Proofs)**: Closed-form inner products via Gradshteyn-Ryzhik, physical proof of the unfeasibility of the $w_0 \to 0$ basis limit (divergence of $\langle k_r^2 \rangle$, $M^2$, $I_{\max}$, optical breakdown, non-$L^2$ distribution), continuous frame formulation on paraxial bandlimited space $\mathcal{H}_{\text{band}}$, classical (RKHS projection, SDM, spatial filtering) and quantum advantages (POVM tomography, HD-QKD, SPDC entanglement preservation).
   - **Milestone 2 (Reproducible Python Simulations & Figure Generation)**: Python 3.12 scripts in `v1/` generating 5 high-resolution publication-quality figures (`fig1` through `fig5`) in PDF format, verifying analytical formulas to machine precision.
   - **Milestone 3 (Manuscripts & Pedagogical Appendices Drafting)**: Creation of `Paper_arxiv_v1.tex` and `Paper_revista_v1.tex` (Optics Express standard via `optica-article.cls`), comprehensive bibliography `references.bib`, 4 dedicated pedagogical appendices (PVB primer, complete Hilbert bases, overcomplete frame theory, mathematical derivations), and formal AI ethics declaration.
   - **Milestone 4 (Compilation & Packaging)**: Compilation into `Paper_arxiv_v1.pdf` and `Paper_revista_v1.pdf`, packaging supporting style and bst files in `v1/` for direct Overleaf and arXiv drag-and-drop upload.
   - **Milestone 5 (Final Verification & Hardening)**: Pass 100% E2E test suite + Tier 5 adversarial coverage hardening + Forensic Audit (`teamwork_auditor`).
2. **E2E Testing Track**:
   - Independent test harness and test suites across 4 Tiers (Feature coverage, Boundary cases, Cross-feature combinations, Real-world application scenarios). Publishes `TEST_READY.md`.

```
Project Root /
├── PROJECT.md                                          # Global architecture and feature index
├── .agents/teamwork/                                   # Agent state, metadata, and logs
└── v1/                                                 # Final deliverable package
    ├── Paper_arxiv_v1.tex & Paper_arxiv_v1.pdf         # arXiv deliverable
    ├── Paper_revista_v1.tex & Paper_revista_v1.pdf     # Optics Express journal deliverable
    ├── references.bib & Paper_arxiv_v1.bbl             # Complete bibliographic database
    ├── optica-article.cls, jabbrv.sty, opticajnl.bst   # Optica template assets
    ├── styles/opticajournal.sty                        # Journal style package
    ├── figures/                                        # Vector PDF figures (fig1–fig5)
    │   ├── fig1_pvb_profiles_divergence.pdf
    │   ├── fig2_radial_overlap_matrix.pdf
    │   ├── fig3_frame_spectrum_bounds.pdf
    │   ├── fig4_turbulence_rkhs_recovery.pdf
    │   └── fig5_quantum_povm_entanglement.pdf
    └── scripts/                                        # Reproducible Python scripts
        ├── generate_fig1_profiles.py
        ├── generate_fig2_overlap.py
        ├── generate_fig3_frame_bounds.py
        ├── generate_fig4_turbulence.py
        ├── generate_fig5_quantum.py
        └── run_all_simulations.py
```

---

## Feature Inventory

Every feature derived from user requirements (`ORIGINAL_REQUEST.md`) and the Survey phase is mapped to an assigned milestone:

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Editorial Viability & Journal Selection | Detailed assessment of Optics Express (Q1, Optica) and Physical Review A (Q1/Q2, APS) | M1 | Survey (Explorer 2 & 1) |
| 2 | Exact Analytical PVB Inner Product | Closed-form formula via Gradshteyn & Ryzhik 6.633.2: $\gamma_l(r_1, r_2; w_0) = \frac{I_l(r_1 r_2 / w_0^2)}{\sqrt{I_l(r_1^2/w_0^2) I_l(r_2^2/w_0^2)}}$ | M1 | Survey (Explorer 3) |
| 3 | Impossibility of Strict Orthonormal Basis | Proof that physical PVBs have strictly positive overlap for any finite $w_0 > 0$ | M1 | Survey (Explorer 3 & 1) |
| 4 | Physical Unfeasibility of Singular Limit $w_0 \to 0$ | Physical proof: divergence of $\langle k_r^2 \rangle$, $M^2 \to \infty$, $I_{\max} \propto 1/w_0$, vanishing power, optical damage, non-$L^2$ Dirac delta | M1 | Survey (Explorer 3 & 1) |
| 5 | Continuous Frame Formalism on Paraxial Subspace | Duffin-Schaeffer continuous frame condition $0 < A \le B < \infty$ on bandlimited optical subspace $\mathcal{H}_{\text{band}}$ | M1 | Survey (Explorer 3 & 1) |
| 6 | Classical Advantages of Overcompleteness | Multi-ring SDM multiplexing, RKHS projective noise filtering, sub-scale spatial filtering ($e^{-w_0^2 k^2 / 2}$), beam clipping recovery | M1 | Survey (Explorer 3 & 1) |
| 7 | Quantum Advantages of Overcompleteness | Informationally Complete POVM quantum tomography, constant aperture footprint across dimension $d$ in HD-QKD, SPDC two-photon entanglement preservation | M1 | Survey (Explorer 3 & 1) |
| 8 | Literature Continuity with Codex Máxima | Explicit citations and mathematical unification with Ferreira et al. (J. Opt. 2026) and Villalba et al. (Opt. Express 2023) | M1 | Survey (Explorer 1) |
| 9 | Python Simulation Fig 1: Profiles & Divergence | Script generating `fig1_pvb_profiles_divergence.pdf` showing intensity profiles and $1/w_0$ scaling | M2 | Survey (Explorer 3) |
| 10 | Python Simulation Fig 2: Radial Overlap Matrix | Script generating `fig2_radial_overlap_matrix.pdf` comparing exact Bessel vs Gaussian asymptotic cross-talk | M2 | Survey (Explorer 3) |
| 11 | Python Simulation Fig 3: Frame Bounds | Script generating `fig3_frame_spectrum_bounds.pdf` showing frame eigenvalues and condition number $\kappa \approx 3$ | M2 | Survey (Explorer 3) |
| 12 | Python Simulation Fig 4: Turbulence & RKHS Recovery | Script generating `fig4_turbulence_rkhs_recovery.pdf` simulating Kolmogorov turbulence and RKHS projection | M2 | Survey (Explorer 3) |
| 13 | Python Simulation Fig 5: Quantum POVM & Entanglement | Script generating `fig5_quantum_povm_entanglement.pdf` showing tomography MSE vs photon count and Bell parameter vs aperture | M2 | Survey (Explorer 3) |
| 14 | Master Simulation Runner | `run_all_simulations.py` executing all 5 simulations and verifying outputs | M2 | Requirement R5 |
| 15 | Primary Journal Manuscript (`Paper_revista_v1.tex`) | Full article formatted for Optics Express using `latex-universal-template/` (`optica-article.cls`) | M3 | Requirement R3 |
| 16 | arXiv Preprint Manuscript (`Paper_arxiv_v1.tex`) | Self-contained manuscript configured for clean arXiv ingestion with pre-compiled `.bbl` | M3 | Requirement R3 |
| 17 | Author Information & Affiliation | Sebastián Ayala, Independent Researcher, Cauquenes, Región del Maule, Chile, email and ORCID in both manuscripts | M3 | Requirement R4 |
| 18 | Formal AI Ethics Declaration | COPE, Optica, and APS compliant disclosure of AI collaborative assistance under author supervision | M3 | Requirement R4 |
| 19 | Appendix A: Pedagogical Primer on PVBs | Dedicated tutorial on PVB physics, Helmholtz equation, Fourier transform generation via axicon + spiral phase plate | M3 | Requirement R4 |
| 20 | Appendix B: Complete Bases in Hilbert Spaces | Pedagogical & rigorous treatise on Schauder bases, orthonormal bases, resolution of identity, and Gel'fand triplets | M3 | Requirement R4 |
| 21 | Appendix C: Overcomplete Bases & Frame Theory | Rigorous treatise on Duffin-Schaeffer frames, continuous frames, dual frames, coherent states, and RKHS | M3 | Requirement R4 |
| 22 | Appendix D: Mathematical Derivations | Detailed derivations of Gradshteyn-Ryzhik integrals and asymptotic expansions | M3 | Requirement R2 |
| 23 | Comprehensive Bibliography Database | `references.bib` containing complete metadata for all cited papers | M3 | Requirement R2 |
| 24 | Overleaf & Directory Asset Packaging | Copying `optica-article.cls`, `styles/opticajournal.sty`, `jabbrv.sty`, `opticajnl.bst` into `v1/` | M4 | Requirement R3 |
| 25 | LaTeX & PDF Compilation | Compilation of both manuscripts to `Paper_arxiv_v1.pdf` and `Paper_revista_v1.pdf` without fatal errors | M4 | Requirement R3 |
| 26 | Length Verification (<= 100 pages) | Verification that both compiled PDFs are strictly <= 100 pages (~26–34 pages expected) | M4 | Requirement R4 |
| 27 | E2E Test Suite Creation | Opaque-box test suite across Tiers 1–4 deriving from `ORIGINAL_REQUEST.md` | E2E Track | Project Pattern |
| 28 | 100% E2E Test Pass & Hardening (Tier 5) | Sequential pass of all E2E test tiers and white-box adversarial stress testing | M5 | Project Pattern |
| 29 | Forensic Integrity Audit | Independent verification by `teamwork_auditor` confirming zero integrity violations | M5 | Integrity Forensics |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Theoretical Foundations & Proofs | Formal mathematical derivations, theorems, frame bounds, and literature integration (Features 1–8) | Survey complete | DONE |
| M2 | Python Simulations & Figures | Reproducible scripts in `v1/scripts/` generating 5 PDF figures in `v1/figures/` (Features 9–14) | M1 interfaces defined | DONE |
| M3 | Manuscript Drafting & Appendices | Full LaTeX drafting of `Paper_revista_v1.tex`, `Paper_arxiv_v1.tex`, `references.bib`, Appendices A–D, AI declaration (Features 15–23) | M1, M2 | DONE |
| M4 | Compilation & Overleaf Packaging | Compiling `Paper_revista_v1.pdf` and `Paper_arxiv_v1.pdf`, packaging `v1/` for direct Overleaf upload, verifying <= 100 pages (Features 24–26) | M3 | DONE |
| M5 | E2E Verification & Forensic Audit | Verification against 100% of E2E tests, Tier 5 adversarial hardening, and `teamwork_auditor` clean audit (Features 28–29) | M4, TEST_READY.md | DONE |
| E2E | E2E Testing Track | Independent design of test harness, test suites Tiers 1–4, and publication of `TEST_READY.md` (Feature 27) | Survey complete | DONE |

---

## Interface Contracts

### M1 (Theory) ↔ M2 (Python Simulations)
- Exact mathematical formulas to be implemented:
  - Exact inner product: $\gamma_l(r_1, r_2; w_0) = \frac{I_l(r_1 r_2 / w_0^2)}{\sqrt{I_l(r_1^2/w_0^2) I_l(r_2^2/w_0^2)}}$.
  - Asymptotic formula: $\gamma_{\text{asymp}}(r_1, r_2; w_0) = \exp\left( - \frac{(r_1 - r_2)^2}{2 w_0^2} \right)$.
  - Frame spectrum: $\sigma(k_r) = \exp\left( - \frac{1}{2} k_r^2 w_0^2 \right)$.
  - Energy divergence: $I_{\max} = \frac{P}{\pi^{3/2} \sqrt{2} r_0 w_0}$.
- Parameters: $\lambda = 1550\,\text{nm}$, $r_0 = 1.0\,\text{mm}$, $w_0 \in [0.02, 1.0]\,\text{mm}$, $K_{\max} = k_0 \text{NA}$.
- Data structures: Python functions must accept NumPy arrays and output vector PDF figures with 300+ DPI equivalent typography.

### M2 (Python Simulations) ↔ M3 (Manuscript Drafting)
- Figure file locations: `v1/figures/fig1_pvb_profiles_divergence.pdf`, `fig2_radial_overlap_matrix.pdf`, `fig3_frame_spectrum_bounds.pdf`, `fig4_turbulence_rkhs_recovery.pdf`, `fig5_quantum_povm_entanglement.pdf`.
- Manuscript figure inclusions: `\includegraphics[width=\linewidth]{figures/figX_...pdf}`.
- All figures must be referenced in the main text and accompanied by informative captions explaining physical implications.

### M3 (Manuscript Drafting) ↔ M4 (Compilation & Packaging)
- Root files in `v1/`:
  - `v1/Paper_revista_v1.tex`
  - `v1/Paper_arxiv_v1.tex`
  - `v1/references.bib`
  - `v1/optica-article.cls`
  - `v1/styles/opticajournal.sty`
  - `v1/jabbrv.sty`
  - `v1/jabbrv-ltwa-en.ldf`
  - `v1/jabbrv-ltwa-all.ldf`
  - `v1/opticajnl.bst`
- Preamble requirements: `\let\Bbbk\relax` before `amssymb`, no duplicate `cite` or `natbib`, UTF-8 encoding.

---

## Code Layout

```
v1/
├── Paper_revista_v1.tex
├── Paper_revista_v1.pdf
├── Paper_arxiv_v1.tex
├── Paper_arxiv_v1.pdf
├── Paper_arxiv_v1.bbl
├── references.bib
├── optica-article.cls
├── jabbrv.sty
├── jabbrv-ltwa-en.ldf
├── jabbrv-ltwa-all.ldf
├── opticajnl.bst
├── styles/
│   └── opticajournal.sty
├── figures/
│   ├── fig1_pvb_profiles_divergence.pdf
│   ├── fig2_radial_overlap_matrix.pdf
│   ├── fig3_frame_spectrum_bounds.pdf
│   ├── fig4_turbulence_rkhs_recovery.pdf
│   └── fig5_quantum_povm_entanglement.pdf
└── scripts/
    ├── generate_fig1_profiles.py
    ├── generate_fig2_overlap.py
    ├── generate_fig3_frame_bounds.py
    ├── generate_fig4_turbulence.py
    ├── generate_fig5_quantum.py
    └── run_all_simulations.py
```
