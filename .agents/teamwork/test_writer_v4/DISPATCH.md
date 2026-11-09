## 2026-11-09T15:35:59Z
You are test_writer_v4, a dedicated test authoring agent.
Working directory: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB
Your state folder: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\test_writer_v4

Mandatory reference:
Read the original request at: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\ORIGINAL_REQUEST.md
Also read the project plan at: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\PROJECT.md

Scope and Tasks:
Design and implement an exhaustive, opaque-box E2E test suite in Python (`tests/test_v4_e2e.py` or executable runner script) covering the 4-tier methodology:
1. Tier 1 - Deliverables & Structural Coverage:
   - Verification that folder `v4/` exists with all required files: `Paper_arxiv_v4.tex`, `Paper_arxiv_v4.pdf`, `Paper_revista_v4.tex`, `Paper_revista_v4.pdf`, `v4/references.bib`, `v4/overleaf_bundle_v4.zip`.
   - Verification that previous versions `v1/`, `v2/`, `v3/` remain intact and unmodified.
   - Verification that Python simulation scripts in `v4/scripts/` execute cleanly and output all required vector figures in `v4/figures/`.
   - Verification that `v4/overleaf_bundle_v4.zip` contains all necessary standalone source files, classes, styles, and figures.
2. Tier 2 - Sanitization & Cleanliness (Zero Internal Artifacts):
   - Regex/string search ensuring ZERO occurrences of "Codex-Máxima" or "Codex" as an internal project folder in `v4/Paper_arxiv_v4.tex`, `v4/Paper_revista_v4.tex`, and `v4/references.bib`.
   - Zero occurrences of internal multi-agent bot codenames (e.g. `miner_lit_3`, `worker_arxiv_m2`, `teamwork_*`, `challenger_*`, etc.).
   - Zero occurrences of internal project iteration narratives (e.g. descriptions of the v1 -> v2 -> v3 triad or internal sprint histories).
   - Zero unresolved citation or cross-reference warnings (no `?` in compiled output logs, no `undefined citations`).
   - Exact citation parity: both `Paper_arxiv_v4.tex` and `Paper_revista_v4.tex` must cite all 70 BibTeX entries in `v4/references.bib`.
3. Tier 3 - Step-by-Step Mathematical & Analytical Completeness:
   - Verification of all key mathematical theorems, definitions, equations, and derivations:
     * Theorems 1, 2, and 3 (linear independence, seven pillars of divergence as $w_0 \to 0$, completeness/continuous frame bounds).
     * Continuous frame bounds $0 < A \le B < \infty$ with condition number $\kappa \approx 3.08$.
     * First-principles derivation of the 8.60 dB ring-core fiber advantage (6.83 dB coupling + 1.77 dB inter-symbol interference from differential mode delay of $LP_{\ell,2}$).
     * High-dimensional quantum state tomography and IC-POVM representation.
     * Full Appendices A, B, C, D, E.
4. Tier 4 - Scientific Ethics, Epistemology & Human-AI Collaboration:
   - Verification of Section 8 dedicated structure ("Epistemological Methodology and Human-AI Scientific Collaboration"):
     * Subsection on paradigm shift towards interactive generative cognitive symbiosis.
     * Epistemological foundations, human-in-the-loop oversight, epistemic responsibility, and prevention of hallucination.
     * Realistic technical case study detailing human scientist direction and AI computational assistance.
     * Standard backmatter declaration conforming to international guidelines (COPE, Optica, APS, Nature) without internal bot/folder artifacts.

Deliverables:
- Write the test script: `c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\tests\test_v4_e2e.py`
- Create `TEST_INFRA.md` and `TEST_READY.md` at project root (or inside `.agents/teamwork/` and workspace root) documenting how to run the test suite and summarizing coverage across all 4 tiers.
- Write a complete `handoff.md` in your state folder.
- Send a completion message to parent when done.
