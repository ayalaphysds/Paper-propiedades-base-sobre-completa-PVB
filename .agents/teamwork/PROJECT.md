# Project: Paper PVB Sobrecompletos Version 2 (v2)

## Architecture
- **Dual-Track Workflow**:
  - Implementation Track: Builds all v2 artifacts in `v2/` (LaTeX manuscripts, PDFs, Python simulation scripts, multi-row figures, Overleaf bundle, and response document `RESPUESTAS_REVISION_V2.md`).
  - E2E Testing Track: Verifies all deliverables against requirements R1–R4, the 7 author revision comments, compilation integrity, and numerical reproducibility.
- **Physical & Mathematical Core**:
  - Hilbert space: Paraxial bandlimited subspace $\mathcal{H}_{\text{band}} \subset L^2(\mathbb{R}^2)$ with cutoff $K_{\max} = k \cdot \text{NA}$.
  - Overcomplete frame: Continuous frame with positive bounds $0 < A = \exp(-w_0^2 K_{\max}^2 / 2) \le S_w \le B = 1 < \infty$ and condition number $\kappa \approx 3.08$.
  - Theorem 1: Strict radial non-orthogonality $0 < \gamma_\ell(R_1, R_2; w_0) < 1$ for all $R_1 \neq R_2$.
  - Theorem 2: Seven divergence pillars proving unfeasibility of the singular Dirac limit $w_0 \to 0$.
  - Theorem 3: Continuous frame resolution of identity and canonical dual frame.
  - Classical assets: Multi-ring SDM, 8.6 dB RCF launch power advantage, RKHS out-of-subspace turbulence filtering.
  - Quantum assets: Single-shot IC-POVM tomography, aperture-invariant two-photon entanglement.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Directory & Asset Setup | Create `v2/`, copy cls/sty/bst assets, setup `v2/scripts/` & `v2/figures/` | M1 | R1 |
| 2 | Bibliographic Expansion | Add Jauhiainen (2026), PaperBanana (2026), Haber et al. (2025) to `references.bib` | M1 | R2 (C5) |
| 3 | Author Review Defense Report | Generate point-by-point defense `v2/RESPUESTAS_REVISION_V2.md` | M1 | R2 (C1-C7) |
| 4 | Redesigned Simulation Scripts | Python scripts in `v2/scripts/` with 2x2 multi-row grid layouts and native bold titles | M2 | R1, R2 (C3), R4 |
| 5 | Publication Figures Generation | Generate 5 publication-grade vector PDFs in `v2/figures/` without raw LaTeX markup | M2 | R1, R2 (C3), R4 |
| 6 | Q1 Abstract & Editorial Tone | Rewrite abstract without raw equation citations or bracketed refs | M3 | R2 (C2) |
| 7 | Technical Spelling & Grammar | Enforce Latin plural "radii" vs singular "radius", rigorous scientific English | M3 | R2 (C1) |
| 8 | Condensed Sections 1–2 | Streamline background review of Ayala (2026) to < 1.5 pages | M3 | R2 (C4) |
| 9 | Autonomous Mathematical Core | Formalize Theorems 1, 2, 3, continuous frame bounds, and reproducing kernel | M3 | R2 (C6) |
| 10 | Classical & Quantum Advantages | Formalize SDM, RCF advantage, RKHS filtering, IC-POVM, entanglement protection | M3 | R2 (C6) |
| 11 | AI Ethics Declaration | Add formal section citing Jauhiainen2026, Zhu2026PaperBanana, Haber2025 | M3 | R2 (C5) |
| 12 | Pedagogical Appendices A–D | Add tutorials on PVB optics, complete bases, overcomplete frames, derivations | M3 | R3 |
| 13 | Author Affiliation | Sebastián Ayala, Independent Researcher, Cauquenes, Maule, Chile, ORCID, email | M3 | R3 |
| 14 | arXiv LaTeX Manuscript | Write and compile `Paper_arxiv_v2.tex` -> `Paper_arxiv_v2.pdf` (< 100 pages) | M3 | R1, R3 |
| 15 | Revista LaTeX Manuscript | Write and compile `Paper_revista_v2.tex` -> `Paper_revista_v2.pdf` (< 100 pages) | M3 | R1, R3 |
| 16 | Overleaf Zip Bundle | Package `v2/overleaf_bundle_v2.zip` containing all self-contained source files | M4 | R1 |
| 17 | E2E Testing & Verification | Validate all deliverables against Tiers 1–5 test suite | M5 | Acceptance Criteria |
| 18 | Multi-Agent Review & Audit | Rigorous Reviewer, Challenger, and Forensic Auditor gate verification | M5 | Audit Enforcement |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Setup & Defense Document | Directory setup, references.bib expansion, `v2/RESPUESTAS_REVISION_V2.md` | none | DONE |
| M2 | Numerical Simulation Suite | 5 Python scripts (2x2 grid, clean labels), generate `v2/figures/*.pdf` | M1 | DONE |
| M3 | Manuscript Drafting & Compilation | `Paper_arxiv_v2.tex/.pdf`, `Paper_revista_v2.tex/.pdf` (< 100 pages) | M1, M2 | DONE |
| M4 | Overleaf Bundle Packaging | Package `v2/overleaf_bundle_v2.zip` with verified self-contained compilation | M3 | DONE |
| M5 | Final E2E Test & Review Gate | 100% test pass, Challenger stress test, Forensic Auditor integrity verdict | M4 | DONE |

## Interface Contracts
### M1 ↔ M2 (Assets & References)
- `v2/references.bib` must be in place before M3 compilation.
- `v2/scripts/` must output directly to `v2/figures/*.pdf`.
- All figure names: `fig1_pvb_profiles_divergence.pdf`, `fig2_radial_overlap_matrix.pdf`, `fig3_frame_spectrum_bounds.pdf`, `fig4_turbulence_rkhs_recovery.pdf`, `fig5_quantum_povm_entanglement.pdf`.

### M2 ↔ M3 (Figures & Text)
- Figure aspect ratio: 2x2 grid, ~8.5x7.0 inches.
- Native bold titles: `set_title("(a) ...", fontweight="bold", fontsize=11)`.
- No raw LaTeX formatting commands in axis labels (`\textbf`, `\mathrm` in plain text strings).
- `Paper_arxiv_v2.tex` and `Paper_revista_v2.tex` include figures via `\includegraphics[width=...]{figures/figX...pdf}`.

### M3 ↔ M4 (Manuscripts & Packaging)
- Both `Paper_arxiv_v2.tex` and `Paper_revista_v2.tex` must compile with 0 fatal errors.
- Both PDFs must be < 100 pages.
- `overleaf_bundle_v2.zip` contains all `.tex`, `.bib`, `.cls`, `.sty`, `.bst`, and `figures/`.

## Code Layout
```
v2/
├── Paper_arxiv_v2.tex          # Clean article-class preprint
├── Paper_arxiv_v2.pdf          # Compiled arXiv PDF
├── Paper_revista_v2.tex        # Optica Publishing Group class manuscript
├── Paper_revista_v2.pdf        # Compiled Revista PDF
├── references.bib              # Complete bibtex database with AI ethics references
├── RESPUESTAS_REVISION_V2.md   # Point-by-point technical defense for 7 comments
├── optica-article.cls          # Optica class
├── opticajnl.bst               # Optica bibtex style
├── jabbrv.sty, jabbrv-*.ldf    # Journal abbreviation styles
├── styles/opticajournal.sty    # Optica journal style
├── figures/                    # 5 publication-grade vector PDFs (2x2 grid)
│   ├── fig1_pvb_profiles_divergence.pdf
│   ├── fig2_radial_overlap_matrix.pdf
│   ├── fig3_frame_spectrum_bounds.pdf
│   ├── fig4_turbulence_rkhs_recovery.pdf
│   └── fig5_quantum_povm_entanglement.pdf
├── scripts/                    # Fully reproducible Python simulation scripts
│   ├── generate_fig1_profiles.py
│   ├── generate_fig2_overlap.py
│   ├── generate_fig3_frame_bounds.py
│   ├── generate_fig4_turbulence.py
│   ├── generate_fig5_quantum.py
│   └── run_all_simulations.py
└── overleaf_bundle_v2.zip      # Self-contained archive for Overleaf upload
```
