# Paper 2 (`JOSA B`) — Step-by-Step Derivations & Verification Archive

This directory is organized into five separate subfolders so each progressive learning edition (V1, V2, V3), the earlier pre-drafting derivations, and the verification scripts stay completely separated.

## Folder Structure

```text
Step_by_Step_Derivations/
├── README.md
├── JOSA_B_Exact_Walkthrough/                         # Version 1: concise 1-to-1 pen-and-paper workbook (Eqs. (1)–(10))
│   ├── JOSA_B_Paper2_Step_by_Step_Derivations.pdf
│   └── JOSA_B_Paper2_Step_by_Step_Derivations.tex
├── V2_Annotated_Learning_Walkthrough/                # Version 2: explicit exact-vs-approx tags, provenance & tool proofs
│   ├── JOSA_B_Paper2_V2_Annotated_Learning_Walkthrough.pdf
│   └── JOSA_B_Paper2_V2_Annotated_Learning_Walkthrough.tex
├── V3_First_Principles_Course/                       # Version 3: bottom-up course from 1D wells, coin-flip Fisher & qubits to Eqs. (1)–(10)
│   ├── JOSA_B_Paper2_V3_First_Principles_Course.pdf
│   └── JOSA_B_Paper2_V3_First_Principles_Course.tex
├── Pre_Drafting_Archive/                             # Earlier pre-drafting conceptual derivation manual (archived)
│   ├── V15_Paper2_Step_by_Step_Derivations.pdf
│   └── V15_Paper2_Step_by_Step_Derivations.tex
└── Verification_Scripts/                             # Machine-audited photonic-protocol verification suite
    ├── verify_paper2_v15.py
    └── verify_paper2_v15_results.json
```

## Which Version Should I Open?

- **Version 3 (`V3_First_Principles_Course/`):** Best if you are **learning the four photonic protocols from scratch with pencil and paper** — starts from 1D quantum-well analogy, $2\times 2$ linear systems, Kolmogorov dimensional analysis, coin-flip Fisher information, and two-qubit Pauli algebra, clearly tagging `[BACKGROUND]` vs. `[ALREADY IN JOSA B: Eq. (#)]`.
- **Version 2 (`V2_Annotated_Learning_Walkthrough/`):** Best for **auditing every physical/asymptotic approximation and literature provenance** in the exact order of the JOSA B paper.
- **Version 1 (`JOSA_B_Exact_Walkthrough/`):** Best as a **compact 1-to-1 algebraic companion** while reading `Manuscript_JOSA_B/main_paper2_josab.pdf`.
- **Verification (`Verification_Scripts/`):** Run `python Verification_Scripts/verify_paper2_v15.py` to re-verify all 4 photonic-protocol suites.
