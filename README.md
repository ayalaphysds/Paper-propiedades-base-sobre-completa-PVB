# Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams (Companion Papers I & II)

**Author:** Sebastián Ayala (Independent Researcher, Cauquenes, Chile; `ayala.phys.ds@gmail.com`)  
**ORCID:** [https://orcid.org/0009-0003-7348-3883](https://orcid.org/0009-0003-7348-3883)  
**Zenodo Archive DOI:** [10.5281/zenodo.24426770](https://doi.org/10.5281/zenodo.24426770)  
**License:** [MIT License](LICENSE)

---

## 1. Scientific Motivation & Objectives (What We Want to Do)

Structured optical beams carrying orbital angular momentum (OAM) are central to space-division multiplexing (SDM), waveguide communications, and high-dimensional quantum optics, yet standard Laguerre–Gaussian ($\mathrm{LG}_{p,l}$) modes suffer from $l$-dependent radial expansion ($r_{\mathrm{rms}} = w_0\sqrt{2p + |l| + 1}$). Physical perfect optical vortex beams (PVBs) confine all topological charges $l \in \mathbb{Z}$ to a common ring radius $R > 0$ of finite annular half-width $w > 0$, but finite width breaks radial orthogonality and introduces Gaussian spatial smoothing.

The goal of this two-part *Physical Review A* research program is twofold:
1. **Establish a complete, rigorous operator-theoretic foundation (Paper I)** classifying physical finite-width PVBs within continuous Hilbert frame theory, resolving their exact spectral bounds, regularized dual inversion, arbitrary-order $\mathrm{LG}_{p,l}$ expansion ($p \ge 0$), radial resolution limits, and discrete multi-ring Gram conditioning.
2. **Translate those operator properties into quantitatively benchmarked classical and quantum photonic protocols (Paper II)** spanning noisy modal deconvolution, ring-core fiber (RCF) coupling and multi-ring SDM equalization, Kolmogorov atmospheric turbulence filtering, passive multi-plane radial-qudit quantum tomography, and circular-iris Bell–CHSH entanglement preservation.

---

## 2. What We Have Accomplished (Up to Final Submission Version `v13`)

Through an iterative, Human-in-the-Loop (HITL) theoretical and computational audit cycle (`v1`–`v13`), we split the study into two cohesive companion manuscripts, resolved every analytical, dimensional, numerical, and referee-identified issue, minted a permanent Zenodo archival DOI ([10.5281/zenodo.24426770](https://doi.org/10.5281/zenodo.24426770)), and produced zero-warning *Physical Review A* (two-column) and arXiv (single-column) builds in **`v13/`**:

### Paper I — *Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. I. Operator Theory and Laguerre–Gaussian Expansion*
- **Final submission files:** `v13/part1_theory/pra/` (12-page PRA reprint) & `v13/part1_theory/arxiv/` (16-page arXiv preprint)
- **Key accomplishments:**
  - Established azimuthal–radial decoupling ($\mathcal{H} = \bigoplus_{l\in\mathbb{Z}}\mathcal{H}_l$), optimal continuous Bessel upper bound $B = 1$ under polar measure $R\,dR$, and exact isotropic Gaussian convolution frame operator $S_w = G_w * \cdot$ with purely continuous spectrum $\sigma(S_w) = [0, 1]$ (Lemma 1, Proposition 1).
  - Proved sharp Paley–Wiener bandlimited frame bounds $A(w, k_{\max}) = \exp(-w^2 k_{\max}^2/2)$ and $B = 1$ on $\mathcal{H}_{k_{\max}}$ with explicit Fourier-annulus sharpness families (Theorem 1).
  - Constructed the Tikhonov-regularized canonical dual $S_{w,\alpha_{\mathrm{reg}}}^{-1} = (S_w^2 + \alpha_{\mathrm{reg}}\mathbb{I})^{-1}S_w$ and proved its deconvolution noise-gain peak $(2\sqrt{\alpha_{\mathrm{reg}}})^{-1}$ at $k_{\mathrm{peak}} = w^{-1}\sqrt{\ln(1/\alpha_{\mathrm{reg}})}$ (Proposition 2, Appendix B).
  - Proved the exact $(p+1)$-term closed-form expansion $c_{l,p}(R)$ for all $\mathrm{LG}_{p,l}$ modes ($p \ge 0$) via Kummer's transformation and verified all 60 entries of Table IV against 50-decimal-digit radial quadrature ($\max_R |\Delta c|/|c| \le 3.64 \times 10^{-12}$, Theorem 2, Appendix A).
  - Derived both the exact $p = 0$ fidelity threshold and the generalized $p \ge 1$ WKB arcsine-law radial Rayleigh limit $w_{\mathrm{crit}} \approx 0.573\,w_0/\sqrt{2p + |l| + 1}$ (Corollary 1, Table II), and proved uniform $N$-independent Jacobi-theta Toeplitz conditioning bounds for unit-normalized discrete radial Gram matrices ($\kappa(\gamma) = 1.645$ at $\Delta R = 2.0\,w$, Proposition 3, Table III).
- **Reproduced artifacts:** Figs. 1–3 (`fig1_pvb_overlap.pdf`, `fig2_frame_regularization.pdf`, `fig3_lg_washout_gram.pdf`) and Tables I–IV.

### Paper II — *Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. II. Classical and Quantum Optical Applications*
- **Final submission files:** `v13/part2_applications/pra/` (8-page PRA reprint) & `v13/part2_applications/arxiv/` (11-page arXiv preprint)
- **Key accomplishments:**
  - **Noisy $\mathrm{LG}_{2,1}$ Deconvolution:** Achieved $258.6\times$ ($24.13\,\mathrm{dB}$) MSE reduction at $\mathrm{SNR} = 20\,\mathrm{dB}$ ($w/w_0 = 0.25$, $w k_{\max} = 3.0$, $\alpha_{\mathrm{reg}}^{\mathrm{opt}} = 0.04902$), verified against $256 \times 256$ 2D-FFT Monte Carlo ensembles.
  - **Sturm–Liouville RCF Coupling & Multi-Ring SDM:** Solved the 1D scalar Helmholtz radial eigenvalue problem for a telecom step-index RCF ($98.52\%$ mean PVB coupling across $l = 0\text{--}8$, $+6.90\,\mathrm{dB}$ over fixed-collimator $\mathrm{LG}_{0,4}$, closely approximating the $+6.83\,\mathrm{dB}$ benchmark of Villalba *et al.*, Table I) paired with $\le 0.42\,\mathrm{dB}$ zero-forcing equalization penalty for $N = 6$ concentric radial channels at $\Delta R = 2.0\,w$.
  - **Kolmogorov Turbulence Spatial Filtering:** Demonstrated $4.24\times$ normalized field-MSE suppression across 40 subharmonic Kolmogorov screens at $D/r_0 = 3.0$ via single-OAM discrete PVB dual-frame projection (Table II).
  - **Passive Multi-Plane Gouy IC-POVM Tomography:** Lifted single-plane SVD rank $7/16$ (algebraically explained via degree $p + p' \le 2d - 2$ polynomial factorization) to full IC rank $16/16$ for $d = 4$ radial qudits ($M = 5$ planes, $\kappa(\mathcal{S}_{\mathrm{POVM}}) = 442.5$, basis-invariant single-photon Cramér–Rao bound $\operatorname{Tr}(\mathbf{F}^{-1}) = 41.80$ vs. analytically derived $18.75$ for $5$ sequential MUBs, verified by 30-trial $R\hat{\rho}R$ MLE in Table III).
  - **Circular-Iris Bell–CHSH Preservation:** Proved sixth-order $(w/R_0)^6$ Tsirelson-bound deviation ($2\sqrt{2} - S_{\mathrm{PVB}}(R_0) \le 6.5 \times 10^{-6}$ at $w/R_0 = 0.1$ vs. $S_{\mathrm{LG}}(R_0) = 2.0008$).
- **Reproduced artifacts:** Figs. 1–3 (`fig1_noisy_deconvolution.pdf`, `fig2_rcf_turbulence.pdf`, `fig3_quantum_tomography_chsh.pdf`) and Tables I–III.

---

## 3. Repository Map

Peer reviewers and readers should start in **`v13/`** (the final joint-submission package containing the minted Zenodo DOI). All prior development iterations (`v1/`–`v12/`, `V12.P2/`) are preserved intact for complete audit provenance. *(Note: the repository name `Paper-propiedades-base-sobre-completa-PVB` and some legacy draft filenames, archival notes, or commit messages are in Spanish; all submission `.tex` manuscripts, `.bib` files, and verification scripts in `v13/` are in English.)*

```text
Paper-propiedades-base-sobre-completa-PVB/
├── v13/                              # FINAL SUBMISSION PACKAGE (Paper I + Paper II with Zenodo DOI)
│   ├── part1_theory/
│   │   ├── pra/                      # Paper I — Physical Review A two-column reprint (main_part1_pra.tex/.pdf)
│   │   └── arxiv/                    # Paper I — arXiv single-column preprint (main_part1_arxiv.tex/.pdf)
│   ├── part2_applications/
│   │   ├── pra/                      # Paper II — Physical Review A two-column reprint (main_part2_pra.tex/.pdf)
│   │   └── arxiv/                    # Paper II — arXiv single-column preprint (main_part2_arxiv.tex/.pdf)
│   └── scripts/                      # Core verification & figure suite cited in Data Availability:
│       ├── pvb_physics.py            #   First-principles PVB/LG optics, RCF Sturm-Liouville, turbulence & MLE library
│       ├── verify_analytical_tables.py # 50-digit mpmath quadrature check (Table IV) & frame-bound sharpness verifier
│       ├── generate_figures.py       #   Vector-PDF generator for Paper I (Figs. 1-3) & Paper II (Figs. 1-3)
│       ├── theorem2_table_60.json    #   50-digit radial quadrature dataset for all 60 entries of Paper I Table IV
│       └── verified_metrics.json     #   Deterministic numerical benchmark dataset (seed 2026) for all tables/figures
│
├── v12/ & V12.P2/                    # Pre-DOI final peer-review packages (Paper I in v12/, Paper II in V12.P2/)
├── v1/, v2/, v3/, v4/, v5/, V6/, V7/ # Historical single-manuscript drafts prior to the two-part split
├── v8/, v9/, v10/, v11/              # Historical two-part revision rounds and peer-review response iterations
├── tests/                            # Automated pytest regression and numerical boundary-condition test suites
├── latex-length-check/               # Legacy Optica length-check template files from early drafts (v1-v5)
├── latex-supplemental-document/      # Legacy Optica supplemental-document template files from early drafts
├── latex-universal-template/         # Legacy Optica journal template files from early drafts
├── .agents/                          # Internal workflow and milestone audit logs from early iterations
├── PROJECT.md                        # Historical milestone architecture notes (from v3)
├── TEST_INFRA.md, TEST_READY.md      # Historical automated test-suite documentation
├── .gitignore                        # Excludes local reference cache (Codex Máxima/), __pycache__/, and TeX temp logs
├── LICENSE                           # MIT License
└── README.md                         # This project overview, progress summary, and reproduction guide
```

---

## 4. Requirements & One-Command Reproduction

### Software Requirements
- **Python `>= 3.10`** with packages: `numpy`, `scipy`, `mpmath`, `matplotlib`
- **Optional (to recompile `.tex` manuscripts):** TeX Live or MiKTeX with `pdflatex`, `bibtex`, `revtex4-2`, `newtxtext`, and `newtxmath`.

Install Python dependencies:

```bash
pip install numpy scipy mpmath matplotlib
```

### Reproduce Analytical Benchmarks & Vector PDF Figures (from Repository Root)

Verify all 60 50-digit entries of Paper I Table IV, exact $p = 0$ Rayleigh thresholds, and Paley–Wiener sharpness limits, and regenerate all six vector PDF figures for Paper I and Paper II inside `v13/`:

```bash
python v13/scripts/verify_analytical_tables.py
python v13/scripts/generate_figures.py
```

### Optional: Recompile Final Manuscripts from LaTeX Source

- **Paper I (*Phys. Rev. A* two-column reprint):**

```bash
cd v13/part1_theory/pra
pdflatex main_part1_pra.tex && bibtex main_part1_pra && pdflatex main_part1_pra.tex && pdflatex main_part1_pra.tex
```

- **Paper II (*Phys. Rev. A* two-column reprint):**

```bash
cd v13/part2_applications/pra
pdflatex main_part2_pra.tex && bibtex main_part2_pra && pdflatex main_part2_pra.tex && pdflatex main_part2_pra.tex
```

*(Replace `pra` and `*_pra` with `arxiv` and `*_arxiv` to compile the single-column arXiv preprints.)*

---

## 5. License & Citation

All analytical verification scripts, numerical simulation routines, and benchmark datasets in this repository are released under the **[MIT License](LICENSE)** and permanently archived at Zenodo ([DOI: 10.5281/zenodo.24426770](https://doi.org/10.5281/zenodo.24426770)).

If you use these theoretical results, expansions, or numerical routines in academic work, please cite the companion manuscripts:

```bibtex
@unpublished{Ayala2026PVBPartI,
  author = {Ayala, Sebasti{\'a}n},
  title  = {Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. {I}. {Operator} Theory and {Laguerre--Gaussian} Expansion},
  note   = {Companion paper (Part I), submitted to Phys. Rev. A; code/data archived at Zenodo, DOI: 10.5281/zenodo.24426770},
  year   = {2026},
  url    = {https://doi.org/10.5281/zenodo.24426770}
}

@unpublished{Ayala2026PVBPartII,
  author = {Ayala, Sebasti{\'a}n},
  title  = {Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. {II}. {Classical} and Quantum Optical Applications},
  note   = {Companion paper (Part II), submitted to Phys. Rev. A; code/data archived at Zenodo, DOI: 10.5281/zenodo.24426770},
  year   = {2026},
  url    = {https://doi.org/10.5281/zenodo.24426770}
}
```
