# Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams

**Author:** Sebastian Ayala (ORCID: [0009-0003-7348-3883](https://orcid.org/0009-0003-7348-3883))  
**License:** MIT License

This archive contains the complete LaTeX manuscripts, BibTeX databases, analytical verification routines, 50-digit quadrature benchmark datasets, and vector-figure generation scripts for the two-part study:

- **Paper I (`part1_theory/`):** *Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. I. Operator Theory and Laguerre-Gaussian Expansion* (`pra/` two-column reprint and `arxiv/` single-column preprint).
- **Paper II (`part2_applications/`):** *Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. II. Classical and Quantum Optical Applications* (`pra/` two-column reprint and `arxiv/` single-column preprint).

## Requirements

- Python >= 3.10 with `numpy`, `scipy`, and `matplotlib`
- TeX distribution (`pdflatex` and `bibtex`, e.g., TeX Live or MiKTeX with `revtex4-2` and `newtx`)

## One-Command Reproduction Instructions

From the `scripts/` directory, verify all analytical tables (including all 60 entries of Table IV in Paper I to 50-digit radial quadrature) and regenerate all six vector PDF figures for Paper I (Figs. 1-3) and Paper II (Figs. 1-3):

```bash
cd scripts && python verify_analytical_tables.py && python generate_figures.py
```

To compile any manuscript target from source (`part1_theory/pra`, `part1_theory/arxiv`, `part2_applications/pra`, or `part2_applications/arxiv`):

```bash
pdflatex main_part1_pra.tex && bibtex main_part1_pra && pdflatex main_part1_pra.tex && pdflatex main_part1_pra.tex
```
