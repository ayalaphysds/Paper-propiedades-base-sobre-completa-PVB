## 2026-11-04T15:49:21Z
You are a Worker subagent (worker_sim_1) in a Project Orchestration hierarchy.
Your working directory is: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_sim_1
Your parent is the Project Orchestrator (Conversation ID: 13cbe3c5-df6c-41a9-8cfd-c1094a82e1c5).

MANDATORY FIRST STEP:
Read ORIGINAL_REQUEST.md at:
c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\ORIGINAL_REQUEST.md
read PROJECT.md at:
c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\PROJECT.md
and read the complete theoretical foundations at:
c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v1\theory_foundations.md

WRITE OWNERSHIP:
You exclusively own:
- `c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v1\scripts\`
- `c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v1\figures\`
- your working directory `.agents/teamwork/worker_sim_1/`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

YOUR MISSION (Milestone M2: Python Simulations & Publication Figures):
Develop the complete suite of modular, reproducible Python 3.12 simulation scripts in `v1/scripts/` and generate 5 high-resolution publication-quality vector PDF figures in `v1/figures/`:
1. `v1/scripts/generate_fig1_profiles.py` -> `v1/figures/fig1_pvb_profiles_divergence.pdf`
   - Fig 1(a): Radial intensity profiles $I(r)$ for various $w_0 \in [1.0, 0.5, 0.2, 0.1, 0.05, 0.02]\,\text{mm}$ ($r_0=1.0\,\text{mm}, P=1\,\text{W}$).
   - Fig 1(b): Peak intensity divergence $I_{\max}$ vs $1/w_0$ (log-log scale), confirming $1/w_0$ scaling and comparing with air optical breakdown threshold.
   - Fig 1(c): Topological radial shift $\Delta r_l$ vs $l$ for multiple $w_0$.
2. `v1/scripts/generate_fig2_overlap.py` -> `v1/figures/fig2_radial_overlap_matrix.pdf`
   - Fig 2(a): 2D heatmap of exact normalized overlap matrix $\gamma_l(r_1, r_2; w_0) = \frac{I_l(r_1 r_2 / w_0^2)}{\sqrt{I_l(r_1^2/w_0^2) I_l(r_2^2/w_0^2)}}$.
   - Fig 2(b): Universal asymptotic Gaussian cross-talk comparison: $\gamma_l(r_0, r)$ vs $|r - r_0| / w_0$ comparing exact Bessel against $\exp(-(r-r_0)^2 / (2w_0^2))$ for $l \in \{0, 1, 3, 5\}$.
   - Fig 2(c): Relative error of the Gaussian approximation.
3. `v1/scripts/generate_fig3_frame_bounds.py` -> `v1/figures/fig3_frame_spectrum_bounds.pdf`
   - Fig 3(a): Frame operator continuous spectrum $\sigma(k_r) = \exp(-\frac{1}{2} k_r^2 w_0^2)$ vs spatial frequency $k_r$.
   - Fig 3(b): Frame bounds $A = \exp(-\frac{1}{2} K_{\max}^2 w_0^2)$, $B=1.0$, and condition number $\kappa = B/A$ vs $\text{NA} \in [0.01, 0.15]$ ($\lambda = 1550\,\text{nm}$).
   - Fig 3(c): Singular value spectrum of concentric discrete multi-ring Gram matrix.
4. `v1/scripts/generate_fig4_turbulence.py` -> `v1/figures/fig4_turbulence_rkhs_recovery.pdf`
   - Fig 4(a): Kolmogorov turbulence phase screen simulation ($C_n^2 = 10^{-14}\,\text{m}^{-2/3}, z = 1\,\text{km}$).
   - Fig 4(b): Modal crosstalk matrix comparison: Laguerre-Gaussian modes vs PVB modes (demonstrating radius invariance and uniform scintillation in PVBs).
   - Fig 4(c): RKHS projective noise filtering: reconstruction error vs noise level before and after projection $P_{\text{RKHS}} = \mathcal{T} S_w^{-1} \mathcal{T}^*$.
5. `v1/scripts/generate_fig5_quantum.py` -> `v1/figures/fig5_quantum_povm_entanglement.pdf`
   - Fig 5(a): Quantum state tomography MSE vs photon count $N \in [10^2, 10^5]$ for qudit $d=8$, comparing overcomplete POVM against standard MUBs.
   - Fig 5(b): SPDC two-photon entanglement Bell-CHSH parameter $S$ vs iris radius $R_{\text{iris}} / r_0 \in [0.5, 2.5]$, proving that PVB maintains $S = 2\sqrt{2}$ violation while LG decays below classical bound $S \le 2$.
   - Fig 5(c): High-dimensional QKD secret key rate vs fiber distance in ring-core fiber.
6. `v1/scripts/run_all_simulations.py`:
   - Master execution script that runs all 5 generators and validates that all 5 PDF files are produced, non-empty, and valid.
7. Verification:
   - Run `python v1/scripts/run_all_simulations.py` to generate the figures.
   - Run `python tests/test_e2e_runner.py` to verify that Tier 1 simulation tests pass.

DELIVERABLE:
Write all scripts in `v1/scripts/`, generate all 5 figures in `v1/figures/`, write handoff report to:
`.agents/teamwork/worker_sim_1/handoff.md`.
Keep `progress.md` updated.
When finished, send a message to the orchestrator with your results.
