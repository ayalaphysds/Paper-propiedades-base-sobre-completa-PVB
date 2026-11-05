================================================================================
Overcomplete Perfect Vortex Beams (PVB) - Version 3 (v3) Overleaf Bundle
================================================================================

Author: Sebastián Ayala
Affiliation: Investigador Independiente / Independent Researcher,
             Cauquenes, Región del Maule, Chile
Email: ayala.phys.ds@gmail.com
ORCID: https://orcid.org/0009-0003-7348-3883
Title: "Properties of Overcomplete Continuous Frames in Perfect Optical Vortex
        Beams: Classical and Quantum Foundations"

--------------------------------------------------------------------------------
OVERVIEW OF THIS BUNDLE
--------------------------------------------------------------------------------
This archive provides a self-contained LaTeX package ready for upload to
Overleaf (https://www.overleaf.com) or compilation in any modern TeX Live /
MiKTeX environment (pdflatex).

Two standalone manuscript variants are included:

1. Paper_arxiv_v3.tex:
   - Standalone arXiv manuscript using standard LaTeX `article` class.
   - Geometry: 2.5 cm margins, 11pt font.
   - Comprehensive derivations, full 70-entry bibliography, 5 multi-panel vector figures.

2. Paper_revista_v3.tex:
   - Standalone Optica Publishing Group Q1 Journal manuscript.
   - Class: `optica-article` (included: optica-article.cls, opticajnl.bst, jabbrv.sty, etc.).
   - Includes line numbers (\linenumbers), journal styling, and identical mathematical rigor.

--------------------------------------------------------------------------------
HOW TO USE THIS BUNDLE IN OVERLEAF
--------------------------------------------------------------------------------
1. Upload to Overleaf:
   - Log in to your Overleaf account (https://www.overleaf.com).
   - Click "New Project" -> "Upload Project".
   - Select this zip file (`overleaf_bundle_v3.zip`).
   - Overleaf will automatically unpack all files into a new project.

2. Selecting the Main Document:
   By default, Overleaf may compile whichever file it detects first. To choose
   between the arXiv manuscript and the Optica journal manuscript:
   - In the upper left corner of Overleaf, click the "Menu" button (or gear/settings icon).
   - Under the "Settings" section, locate the "Main document" dropdown.
   - To compile the arXiv preprint:
       Select: "Paper_arxiv_v3.tex"
   - To compile the Optica Journal submission:
       Select: "Paper_revista_v3.tex"

3. Compiler Configuration:
   - In the same Overleaf "Menu" / "Settings":
       Compiler: pdfLaTeX (recommended)
       TeX Live version: 2024 or 2025
   - Click the green "Recompile" button in the preview pane.

--------------------------------------------------------------------------------
BUNDLE DIRECTORY STRUCTURE
--------------------------------------------------------------------------------
.
├── Paper_arxiv_v3.tex          # Standalone arXiv manuscript source
├── Paper_revista_v3.tex        # Standalone Optica Journal manuscript source
├── references.bib              # Complete, validated 70-entry BibTeX database
├── README_OVERLEAF.txt         # This instruction guide
├── optica-article.cls          # Optica article document class
├── opticajnl.bst               # Optica BibTeX bibliography style
├── jabbrv.sty                  # Journal abbreviation package
├── jabbrv-ltwa-en.ldf          # Journal abbreviation rules (English)
├── jabbrv-ltwa-all.ldf         # Journal abbreviation rules (all)
├── styles/
│   └── opticajournal.sty       # Journal style sheet
├── figures/                    # Publication-grade vector PDF figures
│   ├── fig1_pvb_profiles_divergence.pdf
│   ├── fig2_radial_overlap_matrix.pdf
│   ├── fig3_frame_spectrum_bounds.pdf
│   ├── fig4_turbulence_rkhs_recovery.pdf
│   └── fig5_quantum_povm_entanglement.pdf
└── scripts/                    # Reproducible Python simulation scripts
    ├── generate_fig1_profiles.py
    ├── generate_fig2_overlap.py
    ├── generate_fig3_frame_bounds.py
    ├── generate_fig4_turbulence.py
    ├── generate_fig5_quantum.py
    └── run_all_simulations.py

--------------------------------------------------------------------------------
LOCAL COMPILATION COMMANDS (OPTIONAL)
--------------------------------------------------------------------------------
To compile locally using pdfLaTeX and BibTeX:

  # For arXiv manuscript:
  pdflatex Paper_arxiv_v3.tex
  bibtex Paper_arxiv_v3
  pdflatex Paper_arxiv_v3.tex
  pdflatex Paper_arxiv_v3.tex

  # For Optica Journal manuscript:
  pdflatex Paper_revista_v3.tex
  bibtex Paper_revista_v3
  pdflatex Paper_revista_v3.tex
  pdflatex Paper_revista_v3.tex

--------------------------------------------------------------------------------
FIGURE REPRODUCIBILITY
--------------------------------------------------------------------------------
All 5 figures are fully reproducible using standard scientific Python (numpy, scipy, matplotlib).
To regenerate all figures from source, run:
  python scripts/run_all_simulations.py
================================================================================
