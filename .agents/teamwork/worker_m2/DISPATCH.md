## 2026-11-04T19:29:01Z
You are a Teamwork Worker implementing Milestone 2 (Numerical Simulation Suite and Publication Figures) for Version 2 (v2) of the paper project.

## Working Directory
Your working directory is: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_m2
Write your progress to: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_m2\progress.md
Write your final handoff to: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_m2\handoff.md

## Reference Files to Read
1. ORIGINAL_REQUEST.md at: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\ORIGINAL_REQUEST.md
2. Project specification at: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\PROJECT.md
3. Physics handoff at: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\explorer_survey_physics\handoff.md
4. Existing v1 scripts in `v1/scripts/` to understand numerical models and parameters.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Write Ownership
You own and write exclusively to:
- `v2/scripts/` (generate_fig1_profiles.py, generate_fig2_overlap.py, generate_fig3_frame_bounds.py, generate_fig4_turbulence.py, generate_fig5_quantum.py, run_all_simulations.py)
- `v2/figures/` (output vector PDFs)
Do NOT modify files in `v1/`, `v2/references.bib`, `v2/RESPUESTAS_REVISION_V2.md`, or `tests/`.

## Mission & Tasks
Implement the publication-grade numerical simulation suite in `v2/scripts/` and generate the 5 figures in `v2/figures/`:
1. **Redesign from 1-row to 2x2 multi-panel layout**:
   - Each script must use `plt.subplots(2, 2, figsize=(8.5, 7.0))` (or comparable balanced aspect ratio ~4:3 / 16:10).
   - In titles: use native matplotlib bolding `ax.set_title("(a) ...", fontweight="bold", fontsize=11)` — do NOT use raw `\textbf{}`.
   - In labels: clean formatting, avoid raw LaTeX tokens like `\mathrm` in plain text strings. Use math mode `$...$` appropriately.
2. **Script 1 (`v2/scripts/generate_fig1_profiles.py`)**:
   - (a) Annular intensity profiles $I(r)$ for charges $\ell=1, 2, 3, 4$ showing locked ring radius $R_0 = 1.0$ mm and thickness $w_0 = 0.1$ mm.
   - (b) Topological radial shift $\Delta R_\ell \approx \frac{4\ell^2 - 1}{32 R_0} w_0^2$ showing sub-micron shift ($< 0.01 w_0$) across orders.
   - (c) The 7 physical divergence pillars as $w_0 \to 0$ ($\langle k_r^2 \rangle \sim 1/w_0^2$, $M^2 \sim R_0/w_0$, dielectric breakdown $I_{\max} \propto 1/w_0$).
   - (d) Transverse spatial frequency spectrum $\widetilde{E}(k_r)$ showing bandlimiting under paraxial NA.
3. **Script 2 (`v2/scripts/generate_fig2_overlap.py`)**:
   - (a) Exact radial overlap matrix $\gamma_\ell(R_1, R_2; w_0)$ heatmap for $\ell=1$.
   - (b) Azimuthal Kronecker orthogonality $\delta_{\ell_1, \ell_2}$ cross-talk matrix across topological charges.
   - (c) Normalized overlap vs ring separation $\Delta R / w_0$ showing universal Gaussian cross-talk decay $\exp(-\Delta R^2 / 2w_0^2)$.
   - (d) Numerical comparison between exact Weber integral (formula 6.633.2) and asymptotic thin-ring expansion.
4. **Script 3 (`v2/scripts/generate_fig3_frame_bounds.py`)**:
   - (a) 2D Gaussian convolution smoothing kernel $G_w(\mathbf{r} - \mathbf{r}')$ in physical space.
   - (b) Frame operator Fourier spectrum $\widetilde{G}_w(k) = \exp(-w_0^2 k^2 / 2)$.
   - (c) Lower frame bound $A(K_{\max})$ and condition number $\kappa(K_{\max}) \approx 3.08$ vs numerical aperture $\text{NA} \in [0.05, 0.25]$.
   - (d) Frame reconstruction of arbitrary test beam (e.g., Laguerre-Gaussian or superposition) using canonical dual frame $S_w^{-1} \Phi$.
5. **Script 4 (`v2/scripts/generate_fig4_turbulence.py`)**:
   - (a) Kolmogorov phase screen scintillation distorted phase wavefront.
   - (b) Distorted vs RKHS-reconstructed PVB mode profile.
   - (c) Projection operator $P_{\text{RKHS}} = \mathcal{T} S_w^{-1} \mathcal{T}^*$ rejecting out-of-subspace turbulence noise.
   - (d) Modal crosstalk / BER vs turbulence strength $C_n^2$, showing 8.6 dB power advantage in ring-core fibers.
6. **Script 5 (`v2/scripts/generate_fig5_quantum.py`)**:
   - (a) Informationally Complete POVM (IC-POVM) measurement operator layout in continuous-discrete parameter space.
   - (b) Quantum state tomography density matrix reconstruction error (MSE) comparing overcomplete PVB POVM vs standard orthogonal projective measurement.
   - (c) Circular pupil truncation aperture geometry ($R_{\text{iris}}$).
   - (d) Two-photon SPDC OAM entanglement concurrence and fidelity vs circular pupil radius, proving 100% preservation for PVB due to topological radial decoupling.
7. **Script 6 (`v2/scripts/run_all_simulations.py`)**:
   - Master runner executing all 5 scripts, verifying output files, printing execution time, and returning exit code 0.
8. **Execute and Verify**:
   - Run `python v2/scripts/run_all_simulations.py` using run_command.
   - Confirm all 5 files exist in `v2/figures/*.pdf` and are valid, non-empty vector PDFs.
   - Run `python tests/test_v2_suite.py` to verify passing tests.
   - Write comprehensive report to `handoff.md` and send a message.


## 2026-11-04T23:34:05Z
**Context**: Milestone 2 Simulation Suite & Figure Generation
**Content**: Please provide a quick status update on the implementation of the 5 redesigned simulation scripts in `v2/scripts/` and figure generation in `v2/figures/`.
**Action**: Report your current progress and ETA.
