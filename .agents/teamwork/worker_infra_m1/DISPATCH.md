## 2026-11-05T15:16:43Z
You are worker_infra_m1, an Infrastructure, Simulation & Assets Worker.
Your working directory is: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_infra_m1\
Your parent orchestrator is: 0e3cebcb-1a99-4033-8616-01b2ec6f9ad7

CRITICAL: Read the authoritative user request at:
c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\ORIGINAL_REQUEST.md
And the project scope at:
c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\PROJECT.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Task Objectives:
1. Initialize your BRIEFING.md and progress.md in your working directory.
2. Set up the `v3/` directory structure in the repository root:
   - Create `v3/`, `v3/scripts/`, `v3/figures/`, `v3/styles/`.
   - Copy Optica template styling files into `v3/`:
     * `latex-universal-template/optica-article.cls` -> `v3/optica-article.cls`
     * `latex-universal-template/opticajnl.bst` -> `v3/opticajnl.bst`
     * `latex-universal-template/jabbrv.sty` -> `v3/jabbrv.sty`
     * `latex-universal-template/jabbrv-ltwa-en.ldf` -> `v3/jabbrv-ltwa-en.ldf`
     * `latex-universal-template/jabbrv-ltwa-all.ldf` -> `v3/jabbrv-ltwa-all.ldf`
     * `latex-universal-template/styles/opticajournal.sty` -> `v3/styles/opticajournal.sty`
   - Copy the validated 70-entry BibTeX database:
     * `.agents/teamwork/miner_lit_3/references_v3.bib` -> `v3/references.bib`
   - Copy and configure the Python simulation scripts from `v2/scripts/` into `v3/scripts/`:
     * `generate_fig1_profiles.py`
     * `generate_fig2_overlap.py`
     * `generate_fig3_frame_bounds.py`
     * `generate_fig4_turbulence.py`
     * `generate_fig5_quantum.py`
     * `run_all_simulations.py`
     Ensure their output paths target `../figures/` (i.e. `v3/figures/`).
3. Run the Python simulations in `v3/scripts/run_all_simulations.py` using run_command:
   - Verify that all 5 scripts execute cleanly and generate valid vector PDF figures:
     * `v3/figures/fig1_pvb_profiles_divergence.pdf`
     * `v3/figures/fig2_radial_overlap_matrix.pdf`
     * `v3/figures/fig3_frame_spectrum_bounds.pdf`
     * `v3/figures/fig4_turbulence_rkhs_recovery.pdf`
     * `v3/figures/fig5_quantum_povm_entanglement.pdf`
4. Update the root `PROJECT.md` by synchronizing its content with `c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\PROJECT.md`.
5. Write your comprehensive, self-contained handoff report to:
   c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_infra_m1\handoff.md
6. When finished, send a brief message to parent orchestrator (0e3cebcb-1a99-4033-8616-01b2ec6f9ad7) using send_message with the handoff path.
