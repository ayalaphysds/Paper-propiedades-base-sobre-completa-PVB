# Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams -- Part II: Classical and Quantum Optical Applications

**Author:** Sebastian Ayala (ORCID: [0009-0003-7348-3883](https://orcid.org/0009-0003-7348-3883))  
**License:** MIT License

This directory contains the complete LaTeX manuscripts (`pra/` two-column reprint and `arxiv/` single-column preprint), BibTeX databases, first-principles optical simulation routines, benchmark datasets, and vector-figure generation scripts for **Paper II**.

## One-Command Reproduction Instructions

From the `scripts/` directory, run all analytical/numerical checks and regenerate Figs. 1-3:

```bash
cd scripts && python verify_analytical_tables.py && python generate_figures.py
```

To compile the Physical Review A reprint or arXiv preprint from source:

```bash
cd pra && pdflatex main_part2_pra.tex && bibtex main_part2_pra && pdflatex main_part2_pra.tex && pdflatex main_part2_pra.tex
```
