# Paper 1 (`JOSA A`) — Step-by-Step Derivations & Verification Archive

This directory is organized into five separate subfolders so each progressive learning edition (V1, V2, V3), the earlier pre-drafting derivations, and the verification scripts stay completely separated.

## Folder Structure

```text
Step_by_Step_Derivations/
├── README.md
├── JOSA_A_Exact_Walkthrough/                         # Version 1: concise 1-to-1 pen-and-paper workbook (Eqs. (1)–(26))
│   ├── JOSA_A_Paper1_Step_by_Step_Derivations.pdf
│   └── JOSA_A_Paper1_Step_by_Step_Derivations.tex
├── V2_Annotated_Learning_Walkthrough/                # Version 2: explicit exact-vs-approx tags, provenance & tool proofs
│   ├── JOSA_A_Paper1_V2_Annotated_Learning_Walkthrough.pdf
│   └── JOSA_A_Paper1_V2_Annotated_Learning_Walkthrough.tex
├── V3_First_Principles_Course/                       # Version 3: bottom-up course from Maxwell & Gaussian integrals to Eqs. (1)–(26)
│   ├── JOSA_A_Paper1_V3_First_Principles_Course.pdf
│   └── JOSA_A_Paper1_V3_First_Principles_Course.tex
├── Pre_Drafting_Archive/                             # Earlier pre-drafting conceptual derivation manual (archived)
│   ├── V15_Paper1_Step_by_Step_Derivations.pdf
│   └── V15_Paper1_Step_by_Step_Derivations.tex
└── Verification_Scripts/                             # Machine-audited symbolic & numerical suite
    ├── verify_paper1_v15.py
    └── verify_paper1_v15_results.json
```

## Which Version Should I Open?

- **Version 3 (`V3_First_Principles_Course/`):** Best if you are **learning the subject from scratch with pencil and paper** — starts from Maxwell's equations, 1D Gaussian integrals, and a 3-vector toy frame in $\mathbb{R}^2$, clearly tagging `[BACKGROUND]` vs. `[ALREADY IN JOSA A: Eq. (#)]`.
- **Version 2 (`V2_Annotated_Learning_Walkthrough/`):** Best for **auditing every approximation and citation provenance** (NIST DLMF, Gradshteyn–Ryzhik, Watson, Goodman, Christensen, Szegő) in the exact order of the JOSA A paper.
- **Version 1 (`JOSA_A_Exact_Walkthrough/`):** Best as a **compact 1-to-1 algebraic companion** while reading `Manuscript_JOSA_A/main_paper1_josaa.pdf`.
- **Verification (`Verification_Scripts/`):** Run `python Verification_Scripts/verify_paper1_v15.py` to re-verify all 7 symbolic & numerical suites.
