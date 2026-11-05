## 2026-11-05T15:54:44Z
You are worker_package_m4, the Packaging and Verification Worker.
Your working directory is: c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_package_m4\
Your parent orchestrator is: 0e3cebcb-1a99-4033-8616-01b2ec6f9ad7

CRITICAL: Read the authoritative user request at:
c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\ORIGINAL_REQUEST.md
And the project architecture at:
c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\PROJECT.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Primary Resources:
1. `v3/Paper_arxiv_v3.tex` and `v3/Paper_arxiv_v3.pdf`
2. `v3/Paper_revista_v3.tex` and `v3/Paper_revista_v3.pdf`
3. `v3/references.bib`
4. `v3/optica-article.cls`, `v3/opticajnl.bst`, `v3/jabbrv.*`, `v3/styles/opticajournal.sty`
5. `v3/figures/` (all 5 vector PDFs)
6. `v3/scripts/` (all 6 python scripts)
7. E2E test suite: `tests/test_v3_suite.py`

Target File Owned Exclusively:
c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v3\overleaf_bundle_v3.zip

Task Objectives:
1. Initialize your BRIEFING.md and progress.md in your working directory.
2. Package the standalone Overleaf bundle `v3/overleaf_bundle_v3.zip`:
   - Must include:
     * `Paper_arxiv_v3.tex`
     * `Paper_revista_v3.tex`
     * `references.bib`
     * `optica-article.cls`
     * `opticajnl.bst`
     * `jabbrv.sty`
     * `jabbrv-ltwa-en.ldf`
     * `jabbrv-ltwa-all.ldf`
     * `styles/opticajournal.sty`
     * `figures/` (fig1 to fig5)
     * `scripts/` (all simulation scripts)
     * `README_OVERLEAF.txt` (clear instructions on how to select either arXiv or Optica journal manuscript as main document in Overleaf)
3. Validate the zip package:
   - Verify zip integrity and file list.
   - Test unzipping to a temporary test directory and verify that `pdflatex Paper_arxiv_v3.tex` and `pdflatex Paper_revista_v3.tex` compile cleanly from the unzipped bundle.
4. Execute the comprehensive E2E test suite:
   Run:
   `python tests/test_v3_suite.py`
   Run in strict verification mode:
   `$env:FAIL_ON_PENDING="1"; python tests/test_v3_suite.py`
   Ensure all 33 tests pass (100% pass, 0 failures, 0 errors).
5. Write your comprehensive handoff report to:
   c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\.agents\teamwork\worker_package_m4\handoff.md
6. When finished, send a brief message to parent orchestrator (0e3cebcb-1a99-4033-8616-01b2ec6f9ad7) using send_message with the handoff path.
