# Forensic Analysis of the APS *Physical Review A* Desk Rejections (`AY13023` & `AY13053`) and Publication Roadmap

**Date:** November 24, 2026  
**Audited Version:** `Paper PVB/V14/` (commit `f921887`, *v14 version for APS*)  
**Manuscripts Audited:**
- **Part I (`AY13023`):** *Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. I. Operator Theory and Laguerre–Gaussian Expansion* (12 pages, 26 cited references)
- **Part II (`AY13053`):** *Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams. II. Classical and Quantum Optical Applications* (8 pages, 48 cited references)

**APS Editorial Decisions (Nov 23, 2026 — 7:55 p.m. and 7:56 p.m., 1 minute apart):**
> *"Thank you for your submission. Regrettably, this manuscript fails to match the minimal threshold for the APS journals. APS will not consider this manuscript further."*  
> — Dr. Thomas Pattard, Chief Editor, *Physical Review A*

---

## 1. What Actually Happened (Reading the APS Decision Correctly)

Both manuscripts received **Chief Editor desk-triage rejections** — **neither paper was sent to external referees**. Three details confirm this unambiguously:
1. **Turnaround under 24 hours** and **identical boilerplate sent 1 minute apart** (7:55 p.m. and 7:56 p.m.) directly from the Chief Editor rather than a topical Associate Editor.
2. **Exact APS phrasing:** *"fails to match the minimal threshold for the APS journals. APS will not consider this manuscript further"* is APS's standard triage-rejection template used when initial screening concludes a submission does not pass basic editorial thresholds (scientific fit/impact, screening flags, or format/scope suitability).
3. **Finality:** APS explicitly closed consideration for `AY13023` and `AY13053`. **Do not appeal these two decisions**; an appeal against a Chief Editor minimal-threshold triage rejection almost never succeeds and only delays publication elsewhere.

Crucially, **the core mathematics in Part I is clean and verified** (Gaussian convolution frame operator $S_w = G_w * \cdot$, Paley–Wiener lower bound $A = e^{-w^2 k_{\max}^2/2}$, exact $(p+1)$-term $c_{l,p}(R)$ via Gradshteyn–Ryzhik 6.631.1, and clean LaTeX compilation with zero errors). The rejection was triggered by a **combination of acute 2026 editorial triage red flags, structural choices, and journal-scope mismatch**, not because the equations are wrong.

---

## 2. Five Root Causes Directly Evidenced in `V14`

### Root Cause 1 (Primary Triage Trigger): Heavy AI / "HITL Protocol" Signaling in the Introduction, Bibliography, and Acknowledgments
In 2025–2026, APS editors are screening an unprecedented surge of AI-assisted solo manuscripts from independent authors. `V14` unintentionally displays **every single marker** that triggers instant triage rejection:

1. **Intrusive HITL defense paragraph in Section I (Introduction) of both papers:**
   - Part I (`main_part1_pra.tex`, line 60) and Part II (`main_part2_pra.tex`, line 52) dedicate a prominent paragraph in the Introduction to defending a *"strict Human-in-the-Loop (HITL) scientific protocol"* and cite **six non-physics AI/ChatGPT meta-papers**: `Krenn2022`, `Birhane2023`, `Messeri2024`, `Chandra2026TheoPhysEval` (`arXiv:2610.16733`), `Thorp2023Science` (*"ChatGPT is fun, but not an author"*), and `COPE2023AI`.
   - In **Part I**, those 6 AI-policy/benchmark papers represent **23.1% of the entire reference list** (6 of 26 references; 1 more is the unpublished companion `AyalaPaperII`, leaving only **19 actual physics/mathematics citations** in a 12-page paper). In **Part II**, they represent **12.5%** (6 of 48 references).
2. **Overly expansive AI disclosure in Acknowledgments:**
   - Part I (line 479) and Part II (line 246) state that *"Gemini 4 Carbon (Google DeepMind) operating within the Antigravity IDE"* was used for *"symbolic calculus, asymptotic expansions, numerical verification/simulation scripting, and LaTeX typesetting."*
   - While transparency is commendable, naming an autonomous IDE agent performing symbolic derivations, expansions, scripts, and typesetting — right after citing *TheoPhysEval* and *"ChatGPT is fun, but not an author"* in the Introduction — signals to a rushed Chief Editor that the paper may be an AI-generated research exercise rather than vetted human-led physics.
3. **LLM stylistic cadence + independent metadata:**
   - Solo author (`Independent Researcher, Cauquenes, Chile`) + personal Gmail (`ayala.phys.ds@gmail.com`) + dense ~260–300-word abstracts packed with 4-significant-digit decimals + repetitive LLM transitions (`Crucially,`, `Building on this structure,`) + heavy `Theorem`/`Lemma`/`Proposition`/`Corollary` math-paper formatting inside REVTeX.

### Root Cause 2: Premature Simultaneous "Part I & Part II" Split
- Submitting a **two-part series simultaneously** as a solo author immediately raises the scrutiny bar at PRA. Companion Part I/II submissions are normally reserved for major multi-group milestones where neither paper can stand alone as a 10–14 page article.
- **Splitting weakened both papers:**
  - **Part I alone** reads as incremental applied mathematics / special-function operator theory (Gaussian convolution frame operator + Gradshteyn–Ryzhik integrals) without a standalone new physical phenomenon for PRA.
  - **Part II alone** depends extensively on an *unpublished* Part I and scatters across **five loosely connected numerical mini-benchmarks** (~1–1.5 pages each: noisy $\mathrm{LG}_{2,1}$ deconvolution, scalar step-index RCF coupling, Kolmogorov phase screen, $d=4$ radial-qudit IC-POVM, circular-iris CHSH), none of which includes new experimental data.
- **Citation & archive defects caused by the split:**
  - Both `references.bib` files cite the unpublished companion (`AyalaPaperI` / `AyalaPaperII`) as `@article` with `journal = {Phys. Rev. A}`, `note = {submitted as a companion paper}`, **and `doi = {10.5281/zenodo.24426770}`** — attaching a Zenodo software archive DOI to an unpublished *Phys. Rev. A* article entry.
  - The `Data Availability` section lists `pvb_physics.py`, `verify_analytical_tables.py`, `generate_figures.py`, `theorem2_table_60.json`, and `verified_metrics.json`, which live in `v13/scripts/` rather than inside `V14/`, and the repo `README.md` still references `v13/`.

### Root Cause 3: Scope & Physical-Significance Mismatch for *Physical Review A*
- PRA prioritizes substantial **new physical insight** in AMO physics, quantum optics, and quantum information.
- Most of `V14`'s strongest contributions — continuous Hilbert frames, Paley–Wiener bandlimited sampling, exact Laguerre–Gaussian projection integrals, telecom RCF coupling, multi-ring SDM zero-forcing penalties, OOK BER, and Kolmogorov turbulence filtering — sit squarely in **mathematical optics, classical wave propagation, and optical fiber photonics**, which are core topics for **Optica (*JOSA A*, *Optics Express*, *JOSA B*)** and **IOP (*Journal of Optics*, *Journal of Physics A*)** rather than PRA.
- Two technical points in Part II are also easy targets for skeptical PRA reviewers:
  1. **RCF benchmark (Sec. II.B):** Uses a 1D scalar weakly-guiding step-index Helmholtz solver to compare against Villalba *et al.*'s graded-index RCF (no full-vector spin–orbit coupling).
  2. **Circular-iris CHSH (Sec. IV.B):** Evaluates post-selected coincidences at $R_{\mathrm{iris}} = R_0$, where 50% of ring power is clipped ($24.92\%$ coincidence survival), compared against an $\mathrm{LG}$ baseline whose $l=4$ ring intentionally lies far outside $R_{\mathrm{iris}} = R_0$.

### Root Cause 4: Audit Under the `paper-orchestra` Autorater Rubrics
Evaluating `V14` strictly against `paper-orchestra/autoraters/agent_review.py`, `sxs_quality_prompts.py`, and `lit_review_quality_prompts.py`:

| Evaluation Dimension | Part I (`AY13023`) | Part II (`AY13053`) | Key Evidence |
| :--- | :---: | :---: | :--- |
| **Technical Soundness / Quality (1–4)** | **3.0 / 4** | **2.8 / 4** | Clean operator math, 50-digit quadrature checks, zero LaTeX errors; Part II relies on simplified scalar/toy models. |
| **Presentation & Style (1–4)** | **2.5 / 4** | **2.3 / 4** | Good figures/typesetting, but dense 4-decimal abstracts, repetitive LLM transitions, and distracting HITL defense. |
| **Originality & Significance for PRA (1–4)** | **2.0 / 4** | **2.0 / 4** | Clean formalization extending `Ferreira2026` App. D + GR integrals; Part II splits across 5 thin topics instead of 1 deep physical result. |
| **Literature Review (`lit_review_quality_prompts`, 0–100)** | **50 / 100** | **58 / 100** | Part I has only 19 physics/math refs (below typical ~40–55 PRA baseline) and 23.1% AI-meta citation pollution; Part II has 41 physics refs but 12.5% AI-meta pollution and fragmented scoping. |
| **Overall PRA Readiness** | **Reject (Desk / Scope + Triage)** | **Reject (Desk / Scope + Fragmentation)** | Strong publishable optics work trapped in the wrong packaging and wrong venue. |

### Root Cause 5: Under-Utilizing Your Real Published Track Record
Your own `references.bib` reveals your strongest asset: you are a published co-author of **both** foundational papers this work directly extends:
- **Villalba, ..., S. Ayala, ..., G. Lima, S. P. Walborn, G. Cañas**, *Optics Express* **31**, 40113 (2023)
- **T. Ferreira, G. Santos, S. Ayala, ..., G. Lima, G. Cañas, S. P. Walborn**, *Journal of Optics* **28**, 095601 (September 2026)

Submitting solo as `Independent Researcher, Cauquenes, Chile` with a Gmail address, no prior arXiv posting, and an AI-protocol defense obscured this legitimate domain lineage completely.

---

## 3. Concrete Recovery Plan (Step-by-Step)

1. **Do NOT appeal `AY13023` or `AY13053` to APS.** Move forward cleanly to a better-matched publisher.
2. **Eliminate the AI-protocol bloat & citation pollution immediately:**
   - Delete the entire HITL paragraph in Section I of both papers.
   - Delete all 6 non-physics AI/ChatGPT citations (`Krenn2022`, `Birhane2023`, `Messeri2024`, `Chandra2026TheoPhysEval`, `Thorp2023Science`, `COPE2023AI`) from `references.bib`.
   - Replace the verbose Acknowledgments block with a sober, policy-compliant 1–2 sentence statement tailored strictly to the target publisher's guidelines (e.g., Optica / IOP require disclosing substantive generative AI use briefly in Acknowledgments/Methods without turning the paper into an AI methodology essay).
3. **Choose the right manuscript architecture (Option A strongly recommended):**
   - **Option A — Merge into ONE focused, high-impact 10-page manuscript (Recommended):**
     - Combine **Core Frame Theory** (continuous frame operator $S_w = G_w * \cdot$, Paley–Wiener sharp bounds, Tikhonov canonical dual, exact $(p+1)$-term $c_{l,p}(R)$, generalized radial Rayleigh limit, discrete radial Gram matrix) with the **2–3 strongest, thematically unified applications** (e.g., **Classical/Structured-Light Track:** RCF coupling + multi-ring SDM + atmospheric turbulence filtering — directly extending your `Villalba2023` and `Ferreira2026` papers).
     - Keep the quantum-optics protocols (Gouy-diverse radial-qudit IC-POVM + circular-iris Bell–CHSH) as a **separate, deeper follow-up paper** (targeting *JOSA B* or *Journal of Optics* once Paper 1 is on arXiv/under review), strengthened with loss/detection-efficiency analysis.
   - **Option B — Keep two papers, but decouple them completely and send each to its native journal:**
     - Post **Paper I** on arXiv first (`physics.optics` / `math-ph`), expand its physics/optics literature review to ~35–45 relevant references, remove all forward references to an unpublished Paper II, and submit Paper I alone to **JOSA A** or **Journal of Physics A**.
     - Submit **Paper II** only *after* Paper I has an arXiv identifier (or is accepted), citing it cleanly by arXiv ID — never as `@article{journal={Phys. Rev. A}, doi={zenodo...}}`.
4. **Polish prose, abstract, and repository hygiene:**
   - Trim the abstract to **180–220 words**, emphasizing physical insight and scaling laws rather than strings of 4-decimal numbers.
   - Replace excessive `Theorem/Lemma/Proposition/Corollary` boxes with concise physics-journal derivations (unless targeting *J. Phys. A*).
   - Fix `AyalaPaperI/II` BibTeX entries (Zenodo DOIs belong in `@software`/`@misc` in Data Availability, never on a journal `@article`).
   - Place the exact reproduction scripts inside the submission version folder (`V15/scripts/`) and update `README.md`.
5. **Establish clear scientific provenance before journal submission:**
   - **Post on arXiv (`physics.optics`) first.** If needed, request endorsement or a quick pre-submission read from a former co-author (e.g., S. P. Walborn, G. Lima, G. Cañas, E. S. Gómez).
   - **Consider inviting a former collaborator as co-author** if they contribute meaningful feedback/refinement — institutional affiliation + co-author vetting virtually eliminates blind triage bias.
   - **Write a sharp, 3-paragraph cover letter** explicitly stating: *"As a co-author of Villalba et al. [Opt. Express 31, 40113 (2023)] and Ferreira et al. [J. Opt. 28, 095601 (2026)], this manuscript resolves the open finite-width PVB frame-inversion and general-$p$ Laguerre–Gaussian projection problem noted in Appendix D of our recent Journal of Optics paper."*

---

## 4. Ranked Target Journals (Best Fit, Cost, and Acceptance Odds)

| Priority | Journal (Publisher) | Quartile | Mandatory Fee (Subscription Track) | Best Manuscript Configuration | Why It Fits |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **#1** | ***Journal of Optics*** (IOP Publishing) | Q1/Q2 | **\$0** (Hybrid; optional Gold OA ~\$3,300+) | **Merged PVB Theory + Classical/RCF/Turbulence** (or full merged paper) | **Home court:** you just published `Ferreira2026` here (literally the paper this extends), and classic PVB work (`Reddy2016`) is here. Strong, fair peer review on structured light. |
| **#2** | ***JOSA A*** (*J. Opt. Soc. Am. A*, Optica) | Q1/Q2 | **\$0** up to **10 published pages** (\$300/page overlength fee >10 pp; online color free; optional OA \$2,300) | **Merged Theory + Classical Optics / Turbulence** (strictly $\le 10$ pp) *or* **Part I standalone** | Premier venue in the world for mathematical optics, paraxial modal expansions, frame/sampling theory, and atmospheric propagation. |
| **#3** | ***Journal of Physics A: Mathematical and Theoretical*** (IOP Publishing) | Q1/Q2 | **\$0** (Hybrid) | **Part I standalone** (Operator theory, continuous frames, coherent states, exact $c_{l,p}(R)$) | Ideal if keeping the formal `Theorem`/`Lemma`/`Proposition` operator-theory structure (`Ali1993` / continuous frames territory). |
| **#4** | ***JOSA B*** (*J. Opt. Soc. Am. B*, Optica) | Q1/Q2 | **\$0** up to **10 published pages** (\$300/page overlength fee >10 pp) | **Quantum Optics spin-off** (Radial-qudit IC-POVM + Bell–CHSH + PVB quantum optics) | Natural home for quantum/nonlinear structured-light protocols once decoupled from classical telecom benchmarks. |
| **#5** | ***Optics Express*** (Optica) | Q1 | **Gold OA APC** (~$2,300+; verify waivers/institutional funding) | **Applied RCF + Multi-Ring SDM + Turbulence** | You already published `Villalba2023` here; highest visibility for RCF/SDM photonics, *only if* APC funding or waiver is secured. |
| **#6** | ***Optics Communications*** (Elsevier) / ***Physica Scripta*** (IOP) | Q2 | **\$0** (Hybrid) | Backup for either merged or split tracks | Respected zero-APC structured-light venues (`Gori1987` Bessel–Gauss classic appeared in *Opt. Commun.*). |

---

## 5. Preventive Warning for `Paper 5` (`Paper 5/V1/`)

Because `Paper 5/V1/main_paper5_pra.tex` also targets *Physical Review A* under `Independent Researcher, Cauquenes, Chile` and `ayala.phys.ds@gmail.com`, apply these same safeguards **before submitting Paper 5 to APS**:
1. Post `Paper 5` on **arXiv** first (`quant-ph` / `gr-qc` / `physics.optics`) and verify that it contains **zero** HITL/AI-ethics references or verbose agent-IDE disclosures.
2. Tighten the abstract (~180–220 words, focused on the 2–3 physical discoveries: $\mathrm{EH}_{11}^\pm$ photoelastic suppression, diffeomorphism boundary cancellation, and waveguide-dispersive redshift sign flip) and tone down repetitive LLM connectors (`Crucially,`).
3. Include a crisp cover letter connecting your background in RCF/PVB photonics (`Villalba2023`, `Ferreira2026`) directly to Mieling's PRA/PRD covariant fiber optics framework — or consider *Classical and Quantum Gravity* (IOP, \$0 subscription) / *Physical Review D* / *New Journal of Physics* as alternatives alongside PRA.
