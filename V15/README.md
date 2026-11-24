# Paper PVB — Version 15 (`V15/`) Complete Two-Paper Workspace

Organized, decoupled two-paper architecture targeting **Optica Publishing Group**:
- **Paper 1 → *Journal of the Optical Society of America A* (JOSA A)** (`optica-article.cls`, **\$0 mandatory fee** $\le 10$ composed two-column pages)
- **Paper 2 → *Journal of the Optical Society of America B* (JOSA B)** (`optica-article.cls`, **\$0 mandatory fee** $\le 10$ composed two-column pages)

---

## Directory Structure

```text
Paper PVB/V15/
├── Paper 1/   (Standalone Theory — JOSA A)
│   ├── References/
│   │   ├── README.md                                  # 14 verified open-access arXiv PDFs
│   │   ├── references_v15_paper1.bib                  # 36 clean physics/optics/frame references
│   │   └── *.pdf
│   ├── Feasibility Analysis/
│   │   ├── Feasibility_of_V15_Paper_1.pdf             # 4-page Feasibility Analysis & Format Audit
│   │   └── figures/fig1_p1_feasibility.pdf
│   ├── Step_by_Step_Derivations/
│   │   ├── README.md                                  # Guide to V1, V2, V3 first-principles course, archive, and scripts
│   │   ├── JOSA_A_Exact_Walkthrough/
│   │   │   └── JOSA_A_Paper1_Step_by_Step_Derivations.pdf           # V1: 1-to-1 pen-and-paper workbook (Eqs. (1)–(26))
│   │   ├── V2_Annotated_Learning_Walkthrough/
│   │   │   └── JOSA_A_Paper1_V2_Annotated_Learning_Walkthrough.pdf  # V2: exact-vs-approx tags, provenance & tool proofs
│   │   ├── V3_First_Principles_Course/
│   │   │   └── JOSA_A_Paper1_V3_First_Principles_Course.pdf         # V3: bottom-up first-principles course (Maxwell → Eqs. 1–26)
│   │   ├── Pre_Drafting_Archive/
│   │   │   └── V15_Paper1_Step_by_Step_Derivations.pdf              # Archived pre-drafting derivation manual
│   │   └── Verification_Scripts/
│   │       ├── verify_paper1_v15.py                                 # 7/7 SymPy + 50-digit mpmath + 2D-FFT suite
│   │       └── verify_paper1_v15_results.json
│   └── Manuscript_JOSA_A/
│       ├── main_paper1_josaa.pdf                      # Compiled JOSA A submission PDF
│       ├── main_paper1_josaa.tex                      # Official Optica Universal Template source
│       ├── references.bib                             # Clean JOSA A bibliography (zero AI-meta refs)
│       ├── Cover_Letter_JOSA_A.md                     # Ready-to-send cover letter
│       ├── figures/                                   # 4 Optica-accessible vector PDF figures
│       └── scripts/                                   # Self-contained pvb_physics + verify + figure scripts
│
└── Paper 2/   (Standalone Applications — JOSA B)
    ├── References/
    │   ├── README.md                                  # 17 verified open-access arXiv PDFs
    │   ├── references_v15_paper2.bib                  # 37 clean photonics/quantum references
    │   └── *.pdf
    ├── Feasibility Analysis/
    │   ├── Feasibility_of_V15_Paper_2.pdf             # 4-page Feasibility Analysis & Format Audit
    │   └── figures/fig1_p2_feasibility.pdf
    ├── Step_by_Step_Derivations/
    │   ├── README.md                                  # Guide to V1, V2, V3 first-principles course, archive, and scripts
    │   ├── JOSA_B_Exact_Walkthrough/
    │   │   └── JOSA_B_Paper2_Step_by_Step_Derivations.pdf           # V1: 1-to-1 pen-and-paper workbook (Eqs. (1)–(10))
    │   ├── V2_Annotated_Learning_Walkthrough/
    │   │   └── JOSA_B_Paper2_V2_Annotated_Learning_Walkthrough.pdf  # V2: exact-vs-approx tags, provenance & tool proofs
    │   ├── V3_First_Principles_Course/
    │   │   └── JOSA_B_Paper2_V3_First_Principles_Course.pdf         # V3: bottom-up first-principles course (basics → Eqs. 1–10)
    │   ├── Pre_Drafting_Archive/
    │   │   └── V15_Paper2_Step_by_Step_Derivations.pdf              # Archived pre-drafting derivation manual
    │   └── Verification_Scripts/
    │       ├── verify_paper2_v15.py                                 # 4/4 full photonic-protocol verification suite
    │       └── verify_paper2_v15_results.json
    └── Manuscript_JOSA_B/
        ├── main_paper2_josab.pdf                      # Compiled JOSA B submission PDF
        ├── main_paper2_josab.tex                      # Official Optica Universal Template source
        ├── references.bib                             # Clean JOSA B bibliography (update Paper 1 arXiv ID!)
        ├── Cover_Letter_JOSA_B.md                     # Ready-to-send cover letter
        ├── figures/                                   # 4 Optica-accessible vector PDF figures
        └── scripts/                                   # Self-contained pvb_physics + verify + figure scripts
```

---

## Pre-Submission Checklist (Sequential Release)

1. **Paper 1 (First):**
   - For **arXiv (`physics.optics`)** or **Optica Open**: comment out `\linenumbers` on line 7 of `main_paper1_josaa.tex`, recompile, and upload.
   - For **JOSA A (Optica Prism)**: keep `\linenumbers` active, place `main_paper1_josaa.tex`, `main_paper1_josaa.bbl` (or `references.bib`), `optica-article.cls`, `opticajnl.bst`, `jabbrv*`, `styles/`, and the 4 PDFs from `figures/` at the ZIP root level (the `.tex` already uses bare filenames via `\graphicspath{{figures/}}`!), insert the live arXiv ID into `Cover_Letter_JOSA_A.md`, and submit under the **subscription track (\$0 mandatory fee)**.
2. **Paper 2 (1–3 Weeks Later, After Paper 1 Posts on arXiv):**
   - Update `@misc{AyalaV15Paper1}` in `Manuscript_JOSA_B/references.bib` with Paper 1's live arXiv ID and recompile `main_paper2_josab.tex`.
   - Upload Paper 2 to **arXiv (`physics.optics`)** (without `\linenumbers`), then submit to **JOSA B (Optica Prism)** (with `\linenumbers`) under the **subscription track (\$0 mandatory fee)**.
