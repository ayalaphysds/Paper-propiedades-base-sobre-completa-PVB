# Plan — Orchestrator

## Overview
Decompose the work per the Project Pattern into survey, formal theory, numerical simulation, manuscript drafting (arXiv and Q1/Q2 journal), and end-to-end verification.

## Phase 0: Survey (Parallel 3 Explorers)
- **Explorer 1 (Codex Máxima & Scientific Literature Explorer)**:
  Examine `Codex Máxima/`, especially the TGSM/OAM paper and related reference documents, extracting key mathematical notation, operator formalism, beam definitions, and citations.
- **Explorer 2 (LaTeX Templates & Journal Editorial Standards Explorer)**:
  Examine available LaTeX templates (`latex-length-check/`, `latex-universal-template/`, `latex-supplemental-document/`), assess journals (e.g., Physical Review A vs Optics Express / Optica), requirements, compilation toolchains (`pdflatex`/`xelatex`).
- **Explorer 3 (Mathematical & Quantum Foundations Explorer)**:
  Analyze the physical and mathematical formulation: PVB field expression, Bessel-Gauss approximations, Fourier transform of ring aperture, orthogonality relations, completeness condition $\sum_l |PVB_l\rangle\langle PVB_l| = \mathbb{I}$, frame theory/coherent states, conditions under which it fails to be a minimal basis and forms an overcomplete frame, quantum state tomography, classical noise robustness.

## Phase 1: PROJECT.md & Dual-Track Setup
- Synthesize the 3 Explorer reports into `PROJECT.md` at project root.
- Define Architecture, Feature Inventory, Milestones, Interface Contracts, and Code Layout.
- Setup directories under `.agents/teamwork/` for subagents.

## Phase 2: Dual Track Execution
- **Track A: E2E Testing Track**
  - E2E Testing Orchestrator designs `TEST_INFRA.md`
  - Automated validation harness for:
    - Compilation of both LaTeX files without fatal errors
    - PDF page counts (<= 100 pages)
    - Python simulation reproducibility and figure generation
    - First author, affiliation, email, ORCID verification
    - Formal AI declaration presence and ethical compliance
    - Educational appendices presence (PVB, completeness, overcompleteness)
    - Formal physical-mathematical proof completeness
  - Issues `TEST_READY.md`.
- **Track B: Implementation Track**
  - Milestone 1: Mathematical derivations & theory proofs.
  - Milestone 2: Python simulation scripts & high-resolution figures.
  - Milestone 3: Drafting `Paper_arxiv_v1.tex` & `Paper_revista_v1.tex`.
  - Milestone 4: LaTeX compilation & PDF generation in `v1/`.
  - Milestone 5: Pass 100% of E2E tests + Adversarial Coverage Hardening (Tier 5) + Forensic Audit.

## Phase 3: Forensic Audit & Sentinel Delivery
- Review all criteria, run Forensic Auditor.
- Report completion to Sentinel.
