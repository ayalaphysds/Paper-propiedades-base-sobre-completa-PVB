## 2026-11-09T15:36:12Z
You are worker_m1_v4, an implementation worker.
Working directory: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB
Your state folder: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_m1_v4

Mandatory reference:
Read the original request at: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\ORIGINAL_REQUEST.md
Also read the project plan at: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\PROJECT.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Milestone 1 Scope and Tasks:
1. Initialize the `v4/` directory layout:
   - Create directories: `v4/`, `v4/scripts/`, `v4/figures/`, `v4/styles/`.
   - Copy the required LaTeX class and style files into `v4/`: `optica-article.cls`, `jabbrv.sty`, `jabbrv-ltwa-en.ldf`, `jabbrv-ltwa-all.ldf`, `opticajnl.bst`, and `styles/opticajournal.sty` (from `v3/` or template folders).
2. Setup and Sanitize `v4/references.bib`:
   - Copy or construct `v4/references.bib` with all 70 verified BibTeX entries.
   - Strictly sanitize the file: remove any mention of "Codex-Máxima", internal folders, bot names, or development iteration notes. Ensure standard, clean BibTeX fields with official DOIs and standard journal abbreviations.
3. Setup Python Simulation Scripts in `v4/scripts/`:
   - Implement the reproducible Python simulation suite in `v4/scripts/` (e.g. `generate_fig1_profiles.py`, `generate_fig2_overlap.py`, `generate_fig3_frame_bounds.py`, `generate_fig4_turbulence.py`, `generate_fig5_quantum.py`, and `run_all_simulations.py`).
   - Use adaptive path resolution so scripts run reliably regardless of whether the working directory is the repository root or `v4/scripts/`.
   - Ensure the scripts generate all 5 publication vector figures in `v4/figures/`:
     * `fig1_pvb_profiles_divergence.pdf`
     * `fig2_radial_overlap_matrix.pdf`
     * `fig3_frame_spectrum_bounds.pdf`
     * `fig4_turbulence_rkhs_recovery.pdf`
     * `fig5_quantum_povm_entanglement.pdf`
4. Run the simulations:
   - Execute `run_all_simulations.py` using python and verify that all figures are created with high resolution and zero errors.
5. Verify that prior versions (`v1/`, `v2/`, `v3/`) remain completely unmodified.

Deliverables:
- Write a complete `handoff.md` in your state folder documenting the files created, commands run, verification outputs, and confirmation that v1, v2, v3 are untouched.
- Send a completion message to parent when done.
