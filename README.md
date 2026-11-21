# Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams (Companion Papers I & II)

**Author:** Sebastián Ayala (Independent Researcher, Cauquenes, Chile; `ayala.phys.ds@gmail.com`)  
**ORCID:** [https://orcid.org/0009-0003-7348-3883](https://orcid.org/0009-0003-7348-3883)  
**License:** [MIT License](LICENSE)

---

## 1. Project Overview

This repository provides the complete LaTeX sources, BibTeX databases, first-principles analytical and numerical verification routines, 50-digit benchmark datasets, and reproducible figure-generation scripts for the two companion *Physical Review A* manuscripts:

1. **Paper I (Theory):**  
   *Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. I. Operator Theory and Laguerre–Gaussian Expansion*  
   - **Final manuscript directory:** `v12/part1_theory/` (`pra/` two-column reprint and `arxiv/` single-column preprint)
   - **Scope & verified results:** Establishes physical finite-width perfect optical vortex beams (PVBs) as continuous Bessel systems ($B = 1$) on $L^2(\mathbb{R}^2)$ with isotropic Gaussian convolution frame operator $S_w = G_w * \cdot$; proves sharp Paley–Wiener bandlimited frame bounds $A(w, k_{\max}) = \exp(-w^2 k_{\max}^2/2)$ and the Tikhonov-regularized canonical dual noise-gain peak $(2\sqrt{\alpha_{\mathrm{reg}}})^{-1}$; derives and verifies to 50 decimal digits the exact $(p+1)$-term closed-form expansion $c_{l,p}(R)$ for arbitrary Laguerre–Gaussian ($\mathrm{LG}_{p,l}$) modes ($p \ge 0$); establishes exact $p = 0$ and WKB arcsine-law ($p \ge 1$) radial Rayleigh washout criteria; and proves uniform Jacobi-theta Toeplitz conditioning bounds for unit-normalized discrete radial Gram matrices.
   - **Reproduced figures & tables:**
     - **Figures 1–3:** `fig1_pvb_overlap.pdf`, `fig2_frame_regularization.pdf`, `fig3_lg_washout_gram.pdf`
     - **Tables I–IV:** Structural Hilbert-frame hierarchy (Table I); exact $\mathrm{LG}_{p,1}$ radial washout fidelity $\mathcal{F}(p, 1, w/w_0)$ (Table II); $N = 6$ unit-normalized vs. unnormalized discrete radial Gram conditioning and trace invariants (Table III); and 60-entry 50-digit radial quadrature verification of $c_{l,p}(R)$ with $\max_R |\Delta c|/|c| \le 3.64 \times 10^{-12}$ (Table IV).

2. **Paper II (Applications):**  
   *Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. II. Classical and Quantum Optical Applications*  
   - **Final manuscript directory:** `V12.P2/` (`pra/` two-column reprint and `arxiv/` single-column preprint)
   - **Scope & verified results:** Translates the continuous-frame operator theory of Paper I into five quantitative classical and quantum photonic protocols: (i) Tikhonov-regularized Paley–Wiener deconvolution of noisy $\mathrm{LG}_{2,1}$ fields ($258.6\times$ / $24.13\,\mathrm{dB}$ MSE reduction); (ii) 1D scalar Helmholtz Sturm–Liouville step-index ring-core fiber (RCF) coupling ($98.52\%$ mean efficiency across $l = 0\text{--}8$, $+6.90\,\mathrm{dB}$ over fixed-collimator $\mathrm{LG}_{0,4}$) and $N = 6$ concentric multi-ring SDM zero-forcing equalization; (iii) single-OAM discrete PVB dual-frame spatial filtering across 40 subharmonic Kolmogorov turbulence phase screens ($4.24\times$ field-MSE suppression at $D/r_0 = 3.0$); (iv) passive single-setting $M = 5$ Gouy-diverse informationally complete POVM (IC-POVM) tomography of $d = 4$ radial qudits (lifting single-plane SVD rank $7/16$ to full rank $16/16$, $\operatorname{Tr}(\mathbf{F}^{-1}) = 41.80$ vs. $18.75$ for $5$ sequential MUBs); and (v) circular-iris Bell–CHSH entanglement preservation with $\mathcal{O}((w/R_0)^6)$ Tsirelson-bound deviation.
   - **Reproduced figures & tables:**
     - **Figures 1–3:** `fig1_noisy_deconvolution.pdf`, `fig2_rcf_turbulence.pdf`, `fig3_quantum_tomography_chsh.pdf`
     - **Tables I–III:** Sturm–Liouville RCF coupling efficiency across $l = 0\text{--}8$ (Table I); 40-screen subharmonic Kolmogorov turbulence normalized field MSE (Table II); and 30-trial $R\hat{\rho}R$ maximum-likelihood tomography Frobenius MSE vs. Cramér–Rao bounds (Table III).

---

## 2. Repository Map

Peer reviewers can navigate directly to `v12/` (for **Paper I**) and `V12.P2/` (for **Paper II**). Earlier development folders and legacy files are preserved intact at the root for full research provenance. *(Note: the repository name `Paper-propiedades-base-sobre-completa-PVB` and some legacy draft filenames, archival notes, or historical commit messages are in Spanish; all submission `.tex` manuscripts, `.bib` files, and verification scripts in `v12/` and `V12.P2/` are in English.)*

```text
Paper-propiedades-base-sobre-completa-PVB/
├── v12/                              # Final submission package for Paper I (plus initial v12 Paper II build)
│   ├── part1_theory/
│   │   ├── pra/                      # Paper I — Physical Review A two-column reprint (main_part1_pra.tex/.pdf)
│   │   └── arxiv/                    # Paper I — arXiv single-column preprint (main_part1_arxiv.tex/.pdf)
│   ├── part2_applications/           # Earlier v12 build of Paper II (superseded by V12.P2/ below)
│   ├── scripts/                      # Core verification & figure suite cited in Data Availability:
│   │   ├── pvb_physics.py            #   First-principles PVB/LG optics, RCF Sturm-Liouville, turbulence & MLE library
│   │   ├── verify_analytical_tables.py # 50-digit mpmath quadrature check (Table IV) & frame-bound sharpness verifier
│   │   ├── generate_figures.py       #   Vector-PDF generator for Paper I (Figs. 1-3) & Paper II (Figs. 1-3)
│   │   ├── theorem2_table_60.json    #   50-digit radial quadrature dataset for all 60 entries of Paper I Table IV
│   │   └── verified_metrics.json     #   Deterministic numerical benchmark dataset (seed 2026) for all tables/figures
│   ├── README.md                     # Local reproduction guide for v12/
│   └── v12cp2.txt                    # Archived referee checklist notes
│
├── V12.P2/                           # Final pre-submission package for Paper II (incorporating final referee pass)
│   ├── pra/                          # Paper II — Physical Review A two-column reprint (main_part2_pra.tex/.pdf)
│   ├── arxiv/                        # Paper II — arXiv single-column preprint (main_part2_arxiv.tex/.pdf)
│   ├── scripts/                      # Self-contained Paper II copy of the core scripts & JSON datasets above
│   └── README.md                     # Local reproduction guide for V12.P2/
│
├── v1/, v2/, v3/, v4/, v5/, V6/, V7/ # Historical single-manuscript drafts prior to the two-part split
├── v8/, v9/, v10/, v11/              # Historical two-part revision rounds and peer-review iterations
├── tests/                            # Automated pytest regression and numerical boundary-condition test suites
├── latex-length-check/               # Legacy Optica length-check template files from early drafts (v1-v5)
├── latex-supplemental-document/      # Legacy Optica supplemental-document template files from early drafts
├── latex-universal-template/         # Legacy Optica journal template files from early drafts
├── .agents/                          # Internal workflow and milestone audit logs from early iterations
├── PROJECT.md                        # Historical milestone architecture notes (from v3)
├── TEST_INFRA.md, TEST_READY.md      # Historical automated test-suite documentation
├── .gitignore                        # Excludes local reference cache (Codex Máxima/), __pycache__/, and TeX temp logs
├── LICENSE                           # MIT License
└── README.md                         # This peer-reviewer navigation and reproduction guide
```

---

## 3. Requirements & One-Command Reproduction

### Software Requirements
- **Python `>= 3.10`** with packages:
  - `numpy`
  - `scipy`
  - `mpmath` (used for 50-decimal-digit Bessel–Laguerre radial quadrature)
  - `matplotlib` (used for STIX vector-PDF figure rendering and bounding-box checks)
- **Optional (to recompile `.tex` manuscripts):** TeX Live or MiKTeX with `pdflatex`, `bibtex`, `revtex4-2`, `newtxtext`, and `newtxmath`.

Install the Python dependencies with:

```bash
pip install numpy scipy mpmath matplotlib
```

### Reproduce Analytical Benchmarks & Figures (from Repository Root)

1. **Verify all 60 50-digit entries of Paper I Table IV, $p = 0$ Rayleigh thresholds, and Paley–Wiener sharpness limits, and regenerate all vector PDF figures (`v12/`):**

```bash
python v12/scripts/verify_analytical_tables.py
python v12/scripts/generate_figures.py
```

2. **Run verification and regenerate Figs. 1–3 directly inside the final Paper II package (`V12.P2/`):**

```bash
python V12.P2/scripts/verify_analytical_tables.py
python V12.P2/scripts/generate_figures.py
```

### Optional: Recompile Manuscripts from LaTeX Source

- **Paper I (*Phys. Rev. A* two-column reprint):**

```bash
cd v12/part1_theory/pra
pdflatex main_part1_pra.tex
bibtex main_part1_pra
pdflatex main_part1_pra.tex
pdflatex main_part1_pra.tex
```

- **Paper II (*Phys. Rev. A* two-column reprint):**

```bash
cd V12.P2/pra
pdflatex main_part2_pra.tex
bibtex main_part2_pra
pdflatex main_part2_pra.tex
pdflatex main_part2_pra.tex
```

*(Replace `pra` and `*_pra` with `arxiv` and `*_arxiv` to compile the single-column arXiv preprints.)*

---

## 4. License & Citation

All analytical verification scripts, numerical simulation routines, and benchmark datasets in this repository are released under the **[MIT License](LICENSE)**.

If you use these theoretical results, expansions, or numerical routines in academic work, please cite the companion manuscripts:

```bibtex
@unpublished{Ayala2026PVBPartI,
  author = {Ayala, Sebasti{\'a}n},
  title  = {Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. {I}. {Operator} Theory and {Laguerre--Gaussian} Expansion},
  note   = {Companion paper (Part I), submitted to Phys. Rev. A},
  year   = {2026},
  url    = {https://github.com/ayalaphysds/Paper-propiedades-base-sobre-completa-PVB}
}

@unpublished{Ayala2026PVBPartII,
  author = {Ayala, Sebasti{\'a}n},
  title  = {Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. {II}. {Classical} and Quantum Optical Applications},
  note   = {Companion paper (Part II), submitted to Phys. Rev. A},
  year   = {2026},
  url    = {https://github.com/ayalaphysds/Paper-propiedades-base-sobre-completa-PVB}
}
```
