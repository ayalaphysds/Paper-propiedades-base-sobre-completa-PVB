# Project: Overcomplete Perfect Vortex Beams (PVB) — Version 3 (v3)

## Architecture
This project develops Version 3 (v3) of the scientific research paper on classical and quantum properties of overcomplete continuous frames in Perfect Vortex Beams (PVB) for arXiv and Q1 scientific journals (Optics Express / Phys. Rev. A), authored by:
**Sebastián Ayala**, Independent Researcher, Cauquenes, Región del Maule, Chile; Email: `ayala.phys.ds@gmail.com`; ORCID: `https://orcid.org/0009-0003-7348-3883`.

The architecture implements a rigorous, multi-agent development workflow to ensure:
1. Complete step-by-step mathematical proofs without leaps ("speedruns"), with continuous algebraic bridges connecting every numbered equation throughout all sections (1–8 and Appendices A–E).
2. Strictly deductive first-principles derivation of Section 6.2 (The 8.6 dB Power Advantage in Ring-Core Fibers) decomposing into $6.83\,\text{dB}$ modal coupling efficiency gain ($\eta_{\text{PVB}} \approx 0.965-0.996$ vs $\bar{\eta}_{\text{LG}} \approx 0.207-0.250$) and $1.77\,\text{dB}$ intermodal crosstalk / ISI penalty mitigation, connecting continuous frame theory directly to experimental data from Villalba et al. (2023) and Rojas-Rojas et al. (2021).
3. Airtight ODE proof of Theorem 1 linear independence via modified Bessel equations.
4. Comprehensive derivation of the Seven Pillars of Theorem 2 ($w_0 \to 0$ physical unfeasibility).
5. Spectral frame bounds ($A \approx 0.325$, $B = 1.0$, $\kappa \approx 3.08$), canonical dual inversion, and RKHS projective filtering.
6. Quantum Fisher information, IC-POVM tomography ($2.71\times$ lower MSE), qudit security bounds, and SPDC biphoton entanglement preservation ($S = 2\sqrt{2}$).
7. Standalone Section 8: Human-AI Scientific Co-Creation Framework (Sebastián Ayala, Google Antigravity, Gemini reasoning models, Teamwork multi-agent architecture, v1 $\to$ v2 $\to$ v3 iterative audit cycle, Codex Máxima AI literature grounding).
8. 70-entry validated BibTeX database (`v3/references.bib`), 5 reproducible Python scripts in `v3/scripts/` generating 5 vector figures in `v3/figures/`, standalone `Paper_arxiv_v3.tex/pdf` and `Paper_revista_v3.tex/pdf` ($\le 100$ pages), and `v3/overleaf_bundle_v3.zip`.
9. Independent adversarial referee review and forensic integrity audit (`teamwork_auditor`).

```
Project Root /
├── v3/                                                 # Version 3 Complete Deliverable Package
│   ├── Paper_arxiv_v3.tex & Paper_arxiv_v3.pdf         # Standalone arXiv manuscript
│   ├── Paper_revista_v3.tex & Paper_revista_v3.pdf     # Standalone Optica Q1 Journal manuscript
│   ├── references.bib                                  # Validated 70-entry BibTeX database
│   ├── optica-article.cls, jabbrv.sty, opticajnl.bst   # Optica template files
│   ├── styles/opticajournal.sty                        # Journal style package
│   ├── figures/                                        # Vector PDF figures (fig1–fig5)
│   │   ├── fig1_pvb_profiles_divergence.pdf
│   │   ├── fig2_radial_overlap_matrix.pdf
│   │   ├── fig3_frame_spectrum_bounds.pdf
│   │   ├── fig4_turbulence_rkhs_recovery.pdf
│   │   └── fig5_quantum_povm_entanglement.pdf
│   ├── scripts/                                        # Reproducible Python scripts
│   │   ├── generate_fig1_profiles.py
│   │   ├── generate_fig2_overlap.py
│   │   ├── generate_fig3_frame_bounds.py
│   │   ├── generate_fig4_turbulence.py
│   │   ├── generate_fig5_quantum.py
│   │   └── run_all_simulations.py
│   └── overleaf_bundle_v3.zip                          # Complete Overleaf bundle
├── Codex Máxima/                                       # Primary reference library
└── .agents/teamwork/                                   # Multi-agent state and audit logs
```

---

## Feature Inventory

Every requirement from `ORIGINAL_REQUEST.md` and the Survey phase is mapped to an assigned milestone:

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Directory & Infrastructure Setup | Creation of `v3/` root, `v3/scripts/`, `v3/figures/`, copying styles, classes, and `references.bib` | M1 | Requirement R1 |
| 2 | Python Simulation Suite & Vector Figures | Executing and verifying reproducible simulation scripts in `v3/scripts/` to generate `v3/figures/fig1`..`fig5` | M1 | Requirement R1 |
| 3 | Validated 70-entry BibTeX Database | Placement of verified `v3/references.bib` covering physics and AI literature with full DOIs | M1 | Requirement R3, R5 |
| 4 | First-Principles Derivation of 8.6 dB Advantage | Analytical formulation of Helmholtz equation in GRIN-RCF, LP$_{\ell, 1}$ modes, 6.83 dB coupling ratio, 1.77 dB ISI penalty | M2 | Requirement R2 |
| 5 | Elimination of Speedruns & Algebraic Bridges | Step-by-step proofs between all numbered equations across Sections 1 to 7 | M2 | Requirement R2 |
| 6 | Airtight ODE Proof of Theorem 1 | Proof of linear independence via modified Bessel differential equation | M2 | Requirement R2 |
| 7 | Complete Seven Pillars Derivations (Theorem 2) | Step-by-step derivation of $\langle k_\perp^2 \rangle$, $M^2$, far-field divergence, $I_{\max}$, $P \to 0$, $w_{\text{diff}}$, Gel'fand triplet | M2 | Requirement R2 |
| 8 | Continuous Frame Bounds & Dual Inversion | Weber integral, 2D Fourier transform of Gaussian frame kernel, $0 < A \le S_w \le B < \infty$, $\kappa \approx 3.08$ | M2 | Requirement R2 |
| 9 | RKHS Filtering & Classical Assets | Multi-ring SDM, Gram matrix, ZF/MMSE equalization, Kolmogorov turbulence noise rejection, conical self-healing | M2 | Requirement R2 |
| 10 | High-Dimensional Quantum Assets | IC-POVM quantum Fisher information and Cramér-Rao lower bound ($2.71\times$ lower MSE), qudit security, SPDC entanglement invariance | M2 | Requirement R2 |
| 11 | Human-AI Scientific Co-Creation Section | Dedicated Section 8 detailing Sebastián Ayala + Antigravity + Gemini + Teamwork, v1->v2->v3 audits, dual paper purpose | M2 | Requirement R4 |
| 12 | Comprehensive Pedagogical Appendices A–E | Detailed primers on PVB optics, complete Hilbert bases, continuous frames/RKHS, overlap derivations, and RCF waveguide integrals | M2 | Requirement R1, R2 |
| 13 | arXiv Manuscript Authoring (`Paper_arxiv_v3.tex`) | Full standalone arXiv manuscript in `v3/` with complete mathematics, author metadata, and references | M2 | Requirement R1 |
| 14 | Q1 Journal Manuscript Authoring (`Paper_revista_v3.tex`) | Full standalone Optica Journal manuscript in `v3/` with macro clash fixes (`\Bbbk`, `\openbox`), line numbering, identical mathematical exhaustiveness | M3 | Requirement R1 |
| 15 | Automated 4-Pass Compilation Pipeline | 4-pass pdflatex + bibtex compilation of both manuscripts to `Paper_arxiv_v3.pdf` and `Paper_revista_v3.pdf` | M4 | Requirement R1 |
| 16 | Zero Broken References & Page Budget ($\le 100$ pages) | Verification of 0 fatal errors, 0 undefined citations, 0 undefined references, page count between 35 and 60 pages | M4 | Requirement R1 |
| 17 | Overleaf Bundle Creation | Generation of standalone `v3/overleaf_bundle_v3.zip` containing all source files, style files, figures, and scripts | M4 | Requirement R1 |
| 18 | Opaque-Box E2E Test Suite (Tiers 1–4) | Complete test suite validating deliverables, compilation, mathematical content, and citations deriving from user requirements | E2E Track | Requirement R1–R5 |
| 19 | Adversarial Referee Review (Severe Arbitro) | Hostile peer review auditing every equation, proof step, bridge, and 8.6 dB derivation across Sections 1–8 and Appendices | M5 | Requirement R6 |
| 20 | Forensic Integrity Audit (`teamwork_auditor`) | Forensic verification confirming authentic implementation, zero cheating, zero hardcoding | M5 | Integrity Forensics |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Infrastructure, Figures & BibTeX | Set up `v3/`, run Python simulation scripts in `v3/scripts/`, generate `v3/figures/`, place validated `v3/references.bib` | Survey complete | PLANNED |
| M2 | Standalone arXiv Manuscript Authoring | Full drafting of `v3/Paper_arxiv_v3.tex` with all mathematical derivations, algebraic bridges, 8.6 dB RCF proof, Sec 8 Co-Creation, Appendices A–E | M1 | PLANNED |
| M3 | Standalone Journal Manuscript Authoring | Full drafting of `v3/Paper_revista_v3.tex` with `optica-article` class, macro clash fixes, line numbering, identical mathematical exhaustiveness | M2 | PLANNED |
| M4 | Compilation, E2E Testing & Overleaf Packaging | 4-pass pdflatex + bibtex compilation of both PDFs, verification of 0 warnings/errors, $\le 100$ pages, `overleaf_bundle_v3.zip` | M3, TEST_READY.md | PLANNED |
| M5 | Adversarial Referee Review & Forensic Audit | Hostile referee review of all mathematical derivations and forensic integrity audit by `teamwork_auditor` | M4 | PLANNED |
| E2E | E2E Testing Track | Independent design of test harness, test suites Tiers 1–4, and publication of `TEST_READY.md` | Survey complete | PLANNED |

---

## Interface Contracts

### M1 (Infrastructure & Figures) ↔ M2 (arXiv Authoring)
- Output paths: `v3/references.bib`, `v3/figures/fig1_pvb_profiles_divergence.pdf` through `fig5_quantum_povm_entanglement.pdf`.
- Graphics inclusion: `\includegraphics[width=\linewidth]{figures/figX_...pdf}`.
- BibTeX keys: 70 validated keys matching `miner_lit_3/references_v3.bib`.

### M2 (arXiv Authoring) ↔ M3 (Journal Authoring)
- Source parity: Complete mathematical identity between `Paper_arxiv_v3.tex` and `Paper_revista_v3.tex`.
- Preamble adaptation: `\documentclass{optica-article}`, `\let\Bbbk\relax` before `amssymb`, `\let\openbox\relax` before `amsthm`, `\linenumbers`.

### M3 (Journal Authoring) ↔ M4 (Compilation & Packaging)
- Target files: `v3/Paper_arxiv_v3.tex`, `v3/Paper_revista_v3.tex`, `v3/references.bib`.
- Compilation command: 4-pass `pdflatex -> bibtex -> pdflatex -> pdflatex`.
- Packaging command: Zip all necessary files into `v3/overleaf_bundle_v3.zip`.

---

## Code Layout

```
v3/
├── Paper_arxiv_v3.tex
├── Paper_arxiv_v3.pdf
├── Paper_revista_v3.tex
├── Paper_revista_v3.pdf
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
├── scripts/
│   ├── generate_fig1_profiles.py
│   ├── generate_fig2_overlap.py
│   ├── generate_fig3_frame_bounds.py
│   ├── generate_fig4_turbulence.py
│   ├── generate_fig5_quantum.py
│   └── run_all_simulations.py
└── overleaf_bundle_v3.zip
```
