# E2E Test Infra: Paper PVB Sobrecompletos Version 2 (v2)

## Test Philosophy
- Opaque-box, requirement-driven. Derives from ORIGINAL_REQUEST.md and the 7 author revision comments.
- Independent verification: checks compilation, figure layouts, abstract formatting, bibliographic entries, script reproducibility, and overcompleteness mathematics.

## Feature Inventory & Test Mapping
| # | Feature | Scope | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Cross) | Tier 4 (Scenario) |
|---|---------|-------|:-----------------:|:-----------------:|:--------------:|:-----------------:|
| 1 | Directory & Asset Setup | `v2/` exists, independent layout | 5 | 5 | ✓ | ✓ |
| 2 | Bibliographic Expansion | 3 AI ethics citations in `v2/references.bib` | 5 | 5 | ✓ | ✓ |
| 3 | Author Defense Report | `v2/RESPUESTAS_REVISION_V2.md` points 1-7 | 5 | 5 | ✓ | ✓ |
| 4 | Redesigned Python Scripts | 2x2 grid, clean labels, run with exit 0 | 5 | 5 | ✓ | ✓ |
| 5 | Publication Figures | 5 vector PDFs, no raw LaTeX markup | 5 | 5 | ✓ | ✓ |
| 6 | Q1 Abstract & Style | No raw equations, no bracketed citations | 5 | 5 | ✓ | ✓ |
| 7 | Technical Spelling | "radii" vs "radius" strictly applied | 5 | 5 | ✓ | ✓ |
| 8 | Condensed Sections 1-2 | Background < 1.5 pages, overcompleteness core | 5 | 5 | ✓ | ✓ |
| 9 | Autonomous Math Core | Theorems 1, 2, 3, frame bounds, inner product | 5 | 5 | ✓ | ✓ |
| 10 | Classical/Quantum Assets | SDM, RCF advantage, RKHS, IC-POVM | 5 | 5 | ✓ | ✓ |
| 11 | AI Ethics Declaration | Formal declaration citing Codex Máxima papers | 5 | 5 | ✓ | ✓ |
| 12 | Pedagogical Appendices | Appendices A, B, C, D complete | 5 | 5 | ✓ | ✓ |
| 13 | Author Affiliation | Sebastián Ayala metadata verified | 5 | 5 | ✓ | ✓ |
| 14 | arXiv LaTeX & PDF | `Paper_arxiv_v2.pdf` compiles, < 100 pages | 5 | 5 | ✓ | ✓ |
| 15 | Revista LaTeX & PDF | `Paper_revista_v2.pdf` compiles, < 100 pages | 5 | 5 | ✓ | ✓ |
| 16 | Overleaf Zip Bundle | `overleaf_bundle_v2.zip` self-contained | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test runner: Python `unittest` / custom runner `tests/test_e2e_runner_v2.py`.
- Automated checks:
  - File existence and non-emptiness.
  - PDF page count extraction via `pypdf`/`fitz`.
  - LaTeX AST / regex parsing for abstract clean compliance.
  - Figure matplotlib layout parsing for 2-row multi-panel grids.
  - Mathematical simulation assertions (reproducing kernel positivity, frame bounds).
