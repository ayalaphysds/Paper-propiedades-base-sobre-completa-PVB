# DISPATCH: Milestone 4 Remediation Worker

## Task Assignment
- Role: Milestone 4 Remediation Worker
- Goal: Apply adaptive directory discovery to `v2/scripts/run_all_simulations.py` and the 5 figure generation scripts (`generate_fig1_profiles.py` through `generate_fig5_quantum.py`), repackage `v2/overleaf_bundle_v2.zip`, and verify all tests in `tests/test_milestone4_stress_challenger.py` and `tests/test_v2_suite.py` pass.

## Boundaries & Constraints
- Working directory: `.agents/teamwork/worker_m4_remediation/`
- DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
- Authoritative user request: `.agents/teamwork/ORIGINAL_REQUEST.md`
- Scope document: `.agents/teamwork/PROJECT.md`
- Explorer findings: `.agents/teamwork/explorer_m4_remediation/handoff.md`

## Required Actions
1. Read `.agents/teamwork/explorer_m4_remediation/handoff.md`.
2. Update `v2/scripts/run_all_simulations.py` and `v2/scripts/generate_fig1_profiles.py` through `generate_fig5_quantum.py` with adaptive directory discovery so they write to `figures/` whether executed in the repository or inside an extracted Overleaf bundle root.
3. Repackage `v2/overleaf_bundle_v2.zip` containing all updated assets.
4. Run `python tests/test_milestone4_stress_challenger.py` to confirm that all 6/6 tests pass.
5. Run `python tests/test_v2_suite.py` with `FAIL_ON_PENDING=1` to confirm that all 34/34 tests pass.
6. Run `python tests/test_e2e_runner.py` to confirm 81/81 pass.
7. Write your handoff report to `.agents/teamwork/worker_m4_remediation/handoff.md` and message the orchestrator.
