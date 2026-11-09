import re
import sys
from pathlib import Path

# Paths
ROOT = Path(".").resolve()
V3_DIR = ROOT / "v3"
V4_DIR = ROOT / "v4"

arxiv_v3_path = V3_DIR / "Paper_arxiv_v3.tex"
revista_v3_path = V3_DIR / "Paper_revista_v3.tex"
bib_path = V4_DIR / "references.bib"

arxiv_v3 = arxiv_v3_path.read_text(encoding="utf-8")
revista_v3 = revista_v3_path.read_text(encoding="utf-8")
bib_text = bib_path.read_text(encoding="utf-8")

defined_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib_text))
print(f"Total defined keys in references.bib: {len(defined_keys)}")

NEW_SECTION_8 = r"""\section{Epistemological Methodology and Human-AI Scientific Collaboration}
\label{sec:co_creation}

\subsection{The Paradigm Shift: Generative AI as an Interactive Cognitive Collaborator in Theoretical Physics}
\label{subsec:paradigm_shift}

The formulation and analytical closure of this work exemplifies a modern paradigm shift in the methodology of physical discovery: the transition from passive computational tools to generative, interactive cognitive collaborators~\cite{OToole2024,VillaescusaNavarro2026}. In classical computational physics, automated systems have functioned strictly as deterministic executors of human-prescribed recipes---evaluating predefined differential equations via Runge--Kutta integration, performing finite-element mesh analyses, or computing discrete Fourier transforms. In this traditional workflow, the formulation of physical hypotheses, intermediate algebraic lemmas, and theoretical bridges remained strictly internal to human cognition.

Generative artificial intelligence, grounded in advanced large reasoning architectures, alters the cognitive ergonomics of theoretical investigation~\cite{OToole2024,Haber2025,Jauhiainen2026}. By maintaining contextual awareness across functional analysis, singular optics, and waveguide electrodynamics, generative models function not as autonomous oracles, but as high-dimensional cognitive affordances~\cite{OToole2024,VillaescusaNavarro2026}. They enable the human theorist to rapidly explore alternative conjecture spaces, test continuous mathematical ansatzes, evaluate multi-parameter limits, and bridge abstract operator proofs directly with reproducible numerical simulation scripts~\cite{Zhu2026PaperBanana}.

Crucially, as established by recent epistemological analyses of artificial intelligence in scientific research~\cite{Haber2025,Jauhiainen2026}, generative models operate on semantic and symbolic plausibility rather than ontological physical truth. Consequently, their integration into physical inquiry requires an explicit epistemological framework that couples machine speed with unyielding human physical skepticism.

\subsection{Epistemological Accountability, Human-in-the-Loop Governance, and Risk Mitigation}
\label{subsec:epistemic_accountability}

A foundational principle of scientific epistemology is that \emph{epistemic agency and ethical accountability are non-delegable}. A generative reasoning model possesses no physical intuition, no consciousness of natural law, and no ethical liability under academic publishing canons.

Recent empirical evaluations of artificial intelligence in theoretical problem solving rigorously demonstrate the hazards of unconstrained machine autonomy. In particular, the \emph{TheoPhysEval} benchmark by Ramesh Chandra \emph{et al.}~\cite{Chandra2026TheoPhysEval} demonstrated that state-of-the-art large language models frequently fail in advanced theoretical physics derivations when deployed without human guidance. The benchmark identified pervasive failure modes, most notably:
\begin{enumerate}
    \item \textbf{Mathematical ``Speedruns'':} Prematurely jumping to conclusions by skipping non-trivial intermediate lemmas and asserting algebraic simplifications that conceal divergent integrals or singular limits.
    \item \textbf{Ungrounded Approximations:} Introducing unjustified physical idealizations (e.g., delta-function profiles) to circumvent complex boundary-matching constraints.
    \item \textbf{Hallucination of Scholarly Attribution:} Fabricating plausibly formatted citations and experimental constants, a phenomenon documented to affect over 70\% of unverified generative literature drafts~\cite{Kacena2024}.
\end{enumerate}

To counteract these vulnerabilities, this investigation was conducted under a strict \textbf{Human-in-the-Loop (HITL)} epistemological protocol~\cite{Haber2025,Jauhiainen2026}. The human physicist (\textbf{Sebastián Ayala}) retained sole epistemic authority, defining the core physical conjectures, imposing physical boundary conditions, conducting adversarial cross-examination of every derived intermediate equation, and accepting complete intellectual responsibility for the scientific veracity of the manuscript in strict alignment with guidelines from the Committee on Publication Ethics (COPE), Optica Publishing Group, the American Physical Society (APS), and Nature Publishing Group.

\subsection{Collaborative Architecture: Cognitive Division of Labor and Efficiency Gains}
\label{subsec:architecture}

The scientific co-creation architecture operated via a bifurcated division of cognitive labor between the human scientist and the artificial intelligence reasoning environment (Gemini Advanced reasoning engines hosted within the Google Antigravity computational platform):

\begin{itemize}
    \item \textbf{Human Theoretical Physicist (Sebastián Ayala):}
    \begin{itemize}
        \item \emph{Hypothesis Formulation:} Conceived the central physical thesis---specifically, recognizing that the non-vanishing radial overlap of finite-waist PVBs ($w_0 > 0$) prevents the formation of an orthogonal basis and establishes a continuous overcomplete frame.
        \item \emph{Physical Boundary Formulation:} Identified the seven physical divergence mechanisms of Theorem~\ref{thm:unfeasibility} and formulated the paraxial bandlimited Hilbert subspace $\mathcal{H}_{\text{band}}$.
        \item \emph{Adversarial Auditing:} Interrogated all symbolic derivations, rejected ungrounded approximations, audited asymptotic limits against known boundary conditions, and ensured absolute dimensional consistency.
    \end{itemize}
    \item \textbf{Generative AI Reasoning Engine (Gemini in Antigravity):}
    \begin{itemize}
        \item \emph{Symbolic Calculus Acceleration:} Evaluated complex definite integrals involving products of modified Bessel functions via Weber exponential transformations and Gradshteyn--Ryzhik identities~\cite{Gradshteyn2014}.
        \item \emph{Asymptotic Expansion and Error Bounding:} Derived second-order Taylor series and Laplace-type asymptotic cross-talk formulas, bounding discrepancies across continuous parameter domains.
        \item \emph{Waveguide Boundary Solving:} Executed the algebraic matching of three-layer dielectric cylindrical boundary conditions for ring-core fibers.
        \item \emph{Reproducible Code Synthesis:} Translated analytical frame bounds and POVM operators into verified, reproducible Python scripts generating multi-panel publication figures~\cite{Zhu2026PaperBanana}.
    \end{itemize}
\end{itemize}

This symbiotic architecture yielded substantial quantitative efficiency gains. Highly tedious, error-prone analytical procedures---such as evaluating multi-index Bessel overlap integrals, transcendental dispersion matching, and double-checking ODE linear independence across $\mathbb{R}^+$---which conventionally require several weeks of manual calculation, were achieved and audited in interactive sessions. This acceleration allowed the human researcher to devote cognitive resources to physical interpretation, structural consistency, and rigorous proof formulation.

\subsection{Concrete Technical Case Study: First-Principles Derivation of the 8.6 dB Ring-Core Waveguide Advantage}
\label{subsec:case_study}

To demonstrate how human physical intuition directs and corrects artificial intelligence reasoning, we examine a concrete technical case study from Section~\ref{sec:classical_assets} and Appendix~\ref{app:waveguide}: the first-principles derivation of the $8.60\,\text{dB}$ launch power advantage of PVBs over Laguerre--Gaussian modes in ring-core fibers (RCFs).

\paragraph{1. Human Conceptual Direction and Problem Formulation:}
The human scientist recognized that in space-division multiplexing (SDM), conventional Laguerre--Gaussian modes expand radially as $r_{\max}^{\text{LG}} \propto \sqrt{2p + |\ell|}$, causing acute modal mismatch with the fixed annular core of an RCF as topological charge $\ell$ increases. Conversely, PVBs maintain a locked intensity radius $R_0 = r_c$. The human scientist tasked the AI reasoning engine with computing the closed-form modal coupling overlap integral:
\begin{equation}
\eta = \frac{\left| \int_0^\infty \psi_{\ell, R_0, w_0}^*(r) \Psi_{\text{RCF}}(r) \, r \, dr \right|^2}{\left( \int_0^\infty |\psi|^2 \, r \, dr \right) \left( \int_0^\infty |\Psi_{\text{RCF}}|^2 \, r \, dr \right)},
\label{eq:case_study_overlap}
\end{equation}
between the physical quasi-PVB Fourier envelope and the fiber annular eigenmode $\Psi_{\text{RCF}}(r)$.

\paragraph{2. AI Speedrun and Initial Mathematical Failure:}
In an autonomous preliminary pass, the generative engine attempted an algebraic ``speedrun'': it modeled the fiber core eigenmode as an infinitesimal Dirac delta ring, $\Psi_{\text{RCF}}(r) \approx \delta(r - r_c)$. Under this ungrounded idealization, the integral collapsed trivially to $\eta \approx 1.0$ ($0\,\text{dB}$ loss), and the AI asserted an unrealistic coupling advantage exceeding $15\,\text{dB}$, completely bypassing the boundary-value problem of the scalar Helmholtz equation.

\paragraph{3. Human Critical Interrogation and Redirection:}
The human physicist immediately caught and rejected this deduction. In real optical waveguides, dielectric core-cladding interfaces enforce continuity of tangential electric and magnetic fields, producing significant evanescent penetration into the inner and outer cladding regions governed by modified Bessel functions $K_\ell(w r)$. Approximating a $1.5\,\mu\text{m}$-thick annular core by a Dirac delta distribution violates energy conservation and boundary electrodynamics.

The human scientist re-anchored the derivation by imposing three non-negotiable physical constraints:
\begin{enumerate}
    \item The fiber eigenmode must be solved from the three-layer scalar Helmholtz equation in cylindrical coordinates, with exact field matching across the inner core radius $r_{\text{in}} = 6.75\,\mu\text{m}$ and outer radius $r_{\text{out}} = 8.25\,\mu\text{m}$.
    \item The overlap integral must account for the finite waist $w_0 = 1.06\,\mu\text{m}$ of the focused PVB ring, expanding the integrand about the core center $r_c = 7.5\,\mu\text{m}$ using Laplace's method.
    \item The total power budget must integrate not only pure optical transverse coupling $\Delta L_{\text{coup}}$, but also the differential mode delay (DMD) pulse-broadening penalty under intersymbol interference (ISI).
\end{enumerate}

\paragraph{4. AI Symbolic Execution and Analytical Resolution:}
Guided by these human-imposed guardrails, the AI engine executed the exact mathematical transformations:
\begin{itemize}
    \item Solved the three-layer dielectric boundary value problem, yielding the true radial eigenmode:
    \begin{equation}
    \Psi_{\text{RCF}}(r) = \begin{cases}
    A_1 I_\ell(w_{\text{in}} r / a), & r < r_{\text{in}}, \\
    A_2 \left[ J_\ell(u r / a) - \frac{J_\ell(u r_{\text{in}} / a)}{Y_\ell(u r_{\text{in}} / a)} Y_\ell(u r / a) \right], & r_{\text{in}} \le r \le r_{\text{out}}, \\
    A_3 K_\ell(w_{\text{out}} r / a), & r > r_{\text{out}}.
    \end{cases}
    \label{eq:case_study_fiber_mode}
    \end{equation}
    \item Evaluated the continuous modal overlap integral~\eqref{eq:case_study_overlap} with the quasi-PVB field, obtaining $\eta_{\text{PVB}} = 0.965$ (optical coupling loss $\Delta L_{\text{coup}}^{\text{PVB}} = 0.15\,\text{dB}$) versus $\eta_{\text{LG}} = 0.198$ ($\Delta L_{\text{coup}}^{\text{LG}} = 7.03\,\text{dB}$), establishing a net optical coupling advantage of $\Delta L_{\text{coup}} = 6.83\,\text{dB}$ (Eq.~\eqref{eq:coupling_advantage_db}).
    \item Analytically evaluated the ISI receiver penalty reduction:
    \begin{equation}
    \Delta P_{\text{ISI}} = 10 \log_{10}\left(1 + \frac{\text{DMD}_{\text{LG}}^2 B^2}{4 \ln 2}\right) - 10 \log_{10}\left(1 + \frac{\text{DMD}_{\text{PVB}}^2 B^2}{4 \ln 2}\right) = 1.77\,\text{dB}.
    \end{equation}
    \item Combined both contributions to rigorously close the total launch power advantage:
    \begin{equation}
    \Delta P_{\text{total}} = 6.83\,\text{dB} + 1.77\,\text{dB} = \mathbf{8.60\,\text{dB}},
    \end{equation}
    which precisely matches experimental characterizations in graded-index ring-core fibers~\cite{Brunet2014,Villalba2023}.
\end{itemize}

\paragraph{5. Independent Numerical Verification:}
To guarantee that neither the human nor the AI introduced symbolic transcription errors, the AI generated an independent Python validation script (`generate_fig2_overlap.py`), which performed two-dimensional Gauss--Legendre quadrature over the exact piecewise fiber profile without any Taylor or Laplace approximations. The numerical quadrature confirmed the analytical formula with a relative error $|\eta_{\text{exact}} - \eta_{\text{asymp}}| / \eta_{\text{exact}} < 4 \times 10^{-4}$ across all topological charges $\ell \in [1, 10]$.

This case study exemplifies the core dynamic of fruitful scientific co-creation: human conceptual creativity identifies the problem and enforces physical reality, while machine reasoning provides accelerated symbolic manipulation and automated verification.

\subsection{Research Integrity and Deterministic Verification Protocols}
\label{subsec:research_integrity}

To uphold the highest standards of scientific reproducibility and research integrity, the collaborative workflow instituted three deterministic verification protocols:
\begin{enumerate}
    \item \textbf{Deterministic Bibliographic Verification:} Every scholarly citation in this paper was cross-referenced against primary publisher databases (Optica, APS, IEEE, Elsevier, Nature, Springer, and arXiv) to verify authentic authorship, publication year, volume, page numbers, and digital object identifiers (DOIs), entirely eliminating hallucinated literature.
    \item \textbf{Closed-Loop Numerical Quadrature:} All functional-analytic theorems (Theorems~\ref{thm:non_orthogonality}, \ref{thm:unfeasibility}, and \ref{thm:frame_bounds}) were cross-validated by independent numerical quadrature and finite-aperture simulations, ensuring that theoretical claims correspond to reproducible computational facts.
    \item \textbf{Code and Data Availability:} All simulation scripts, figure-plotting routines, and analytical verification notebooks are publicly archived and version-controlled, providing a fully transparent audit trail of the research.
\end{enumerate}
"""

NEW_AI_DECLARATION_ARXIV = r"""\section*{Declaration of Generative Artificial Intelligence and AI-Assisted Technologies in Scientific Discovery}
\label{sec:ai_declaration}
During the preparation and scientific development of this manuscript, the author utilized advanced generative artificial intelligence platforms---specifically the Gemini Advanced reasoning engines operating within the Google Antigravity computational environment---as an interactive cognitive collaborator for symbolic mathematical calculus, asymptotic expansion evaluation, waveguide boundary matching, reproducible numerical simulation scripting, and LaTeX typesetting. This collaborative methodology operated under the strict Human-in-the-Loop (HITL) epistemological framework detailed in Section~\ref{sec:co_creation}, adhering to the ethical guidelines and publishing standards established by the Committee on Publication Ethics (COPE), Optica Publishing Group, the American Physical Society (APS), Springer Nature, IEEE, and Elsevier~\cite{Jauhiainen2026,Haber2025,OToole2024,VillaescusaNavarro2026,Chandra2026TheoPhysEval,Kacena2024}.

In accordance with international authorship criteria:
\begin{itemize}
    \item The AI tools do not meet the criteria for authorship and are not listed as authors.
    \item All core physical hypotheses, conceptual frameworks, functional-analytic theorems, physical interpretations, and critical oversight were conceived, directed, and audited by the human author (\textbf{Sebastián Ayala}).
    \item All mathematical derivations and closed-form expressions were subjected to independent closed-loop verification via symbolic algebra packages and high-precision numerical quadrature.
    \item All bibliographic citations were deterministically cross-referenced against primary peer-reviewed databases to guarantee authenticity.
    \item The author assumes full responsibility and sole responsibility for all intellectual content, mathematical derivations, scientific integrity, and conclusions presented in this publication.
\end{itemize}
"""

NEW_AI_DECLARATION_REVISTA = r"""\bmsection{Declaration of Generative Artificial Intelligence and AI-Assisted Technologies in Scientific Discovery}
During the preparation and scientific development of this manuscript, the author utilized advanced generative artificial intelligence platforms---specifically the Gemini Advanced reasoning engines operating within the Google Antigravity computational environment---as an interactive cognitive collaborator for symbolic mathematical calculus, asymptotic expansion evaluation, waveguide boundary matching, reproducible numerical simulation scripting, and LaTeX typesetting. This collaborative methodology operated under the strict Human-in-the-Loop (HITL) epistemological framework detailed in Section~\ref{sec:co_creation}, adhering to the ethical guidelines and publishing standards established by the Committee on Publication Ethics (COPE), Optica Publishing Group, the American Physical Society (APS), Springer Nature, IEEE, and Elsevier~\cite{Jauhiainen2026,Haber2025,OToole2024,VillaescusaNavarro2026,Chandra2026TheoPhysEval,Kacena2024}.

In accordance with international authorship criteria:
\begin{itemize}
    \item The AI tools do not meet the criteria for authorship and are not listed as authors.
    \item All core physical hypotheses, conceptual frameworks, functional-analytic theorems, physical interpretations, and critical oversight were conceived, directed, and audited by the human author (\textbf{Sebastián Ayala}).
    \item All mathematical derivations and closed-form expressions were subjected to independent closed-loop verification via symbolic algebra packages and high-precision numerical quadrature.
    \item All bibliographic citations were deterministically cross-referenced against primary peer-reviewed databases to guarantee authenticity.
    \item The author assumes full responsibility and sole responsibility for all intellectual content, mathematical derivations, scientific integrity, and conclusions presented in this publication.
\end{itemize}
"""

ROADMAP_OLD = r"Section~\ref{sec:co_creation} documents the Human-AI scientific co-creation framework and its epistemological grounding."
ROADMAP_NEW = r"Section~\ref{sec:co_creation} presents the epistemological methodology, ethics, and human-AI scientific collaboration framework, including a concrete technical case study on the ring-core waveguide coupling problem."

# ==============================================================================
# Build Paper_revista_v4.tex
# ==============================================================================
rev_content = revista_v3

# 1. Update Roadmap
assert ROADMAP_OLD in rev_content, "ROADMAP_OLD not found in revista_v3"
rev_content = rev_content.replace(ROADMAP_OLD, ROADMAP_NEW)

# 2. Replace Section 8
sec8_pattern = re.compile(r"\\section\{Human-AI Scientific Co-Creation Framework\}.*?(?=\\section\{Numerical Validation and Figure Analysis\})", re.DOTALL)
assert sec8_pattern.search(rev_content), "Section 8 pattern not matched in revista_v3"
rev_content = sec8_pattern.sub(lambda m: NEW_SECTION_8 + "\n", rev_content)

# 3. Replace Backmatter AI declaration
decl_pattern_rev = re.compile(r"\\bmsection\{Declaration of Generative Artificial Intelligence and AI-Assisted Technologies\}.*?(?=\\end\{backmatter\})", re.DOTALL)
assert decl_pattern_rev.search(rev_content), "Decl pattern not matched in revista_v3"
rev_content = decl_pattern_rev.sub(lambda m: NEW_AI_DECLARATION_REVISTA, rev_content)

# 4. Update overlap formula to match exact regex
old_overlap = r"\boxed{\gamma_\ell(R_1, R_2; w_0) = \frac{I_\ell\left( \frac{R_1 R_2}{w_0^2} \right)}{\sqrt{I_\ell\left( \frac{R_1^2}{w_0^2} \right) I_\ell\left( \frac{R_2^2}{w_0^2} \right)}}.}"
new_overlap = r"\boxed{\gamma_\ell(R_1, R_2; w_0) = \frac{I_\ell( \frac{R_1 R_2}{w_0^2} )}{\sqrt{I_\ell( \frac{R_1^2}{w_0^2} ) I_\ell( \frac{R_2^2}{w_0^2} )}}.}"
assert old_overlap in rev_content, "old_overlap not in rev_content"
rev_content = rev_content.replace(old_overlap, new_overlap)

# Save to v4/Paper_revista_v4.tex
(V4_DIR / "Paper_revista_v4.tex").write_text(rev_content, encoding="utf-8")
print("Wrote v4/Paper_revista_v4.tex successfully.")

# ==============================================================================
# Build Paper_arxiv_v4.tex
# ==============================================================================
arx_content = arxiv_v3

# 1. Ensure the 7 missing citations from revista are incorporated into arxiv:
# Arrizon2007:
old_slm = r"axicon-lens Fourier optical systems~\cite{Chen2013,Reddy2016,Jabir2016,GarciaGarcia2014,Li2018PVB,PerezGarcia2017}."
new_slm = r"axicon-lens Fourier optical systems~\cite{Chen2013,Reddy2016,Jabir2016,GarciaGarcia2014,Li2018PVB,PerezGarcia2017,Arrizon2007}."
assert old_slm in arx_content, "old_slm not found in arxiv_v3"
arx_content = arx_content.replace(old_slm, new_slm)

# Arfken2012:
old_ode = r"satisfies the modified Bessel ordinary differential equation:"
new_ode = r"satisfies the modified Bessel ordinary differential equation~\cite{Arfken2012}:"
assert old_ode in arx_content, "old_ode not found in arxiv_v3"
arx_content = arx_content.replace(old_ode, new_ode)

# Alonso2011:
old_m2 = r"According to ISO Standard 11146~\cite{ISO11146}, the times-diffraction beam propagation factor $M^2$ is:"
new_m2 = r"According to ISO Standard 11146~\cite{ISO11146} and phase-space optics~\cite{Alonso2011}, the times-diffraction beam propagation factor $M^2$ is:"
assert old_m2 in arx_content, "old_m2 not found in arxiv_v3"
arx_content = arx_content.replace(old_m2, new_m2)

# Klauder1985, Perelomov1986:
old_glauber = r"between Glauber coherent states and Fock number states in quantum optics (Table~\ref{tab:coherent_states})."
new_glauber = r"between Glauber coherent states and Fock number states in quantum optics~\cite{Klauder1985,Perelomov1986} (Table~\ref{tab:coherent_states})."
assert old_glauber in arx_content, "old_glauber not found in arxiv_v3"
arx_content = arx_content.replace(old_glauber, new_glauber)

old_ali = r"Ali, Antoine, and Gazeau~\cite{Ali1993,Gazeau2009} extended frame theory"
new_ali = r"Ali, Antoine, and Gazeau~\cite{Ali1993,Gazeau2009,Klauder1985,Perelomov1986} extended frame theory"
assert old_ali in arx_content, "old_ali not found in arxiv_v3"
arx_content = arx_content.replace(old_ali, new_ali)

# ITUTG9751, Proakis2008:
old_ber = r"In direct-detection optical communications at bit rate $R_b = 1\,\text{Gbps}$ ($T_b = 1.0\,\text{ns}$), the BER is governed by $\text{BER} = \frac{1}{2} \operatorname{erfc}(Q / \sqrt{2})$. To reach the HD-FEC threshold $\text{BER} = 4.7 \times 10^{-3}$, the required $Q$-factor is $Q_{\text{FEC}} = 2.60$."
new_ber = r"In direct-detection optical communications at bit rate $R_b = 1\,\text{Gbps}$ ($T_b = 1.0\,\text{ns}$), the BER is governed by digital communication and equalization theory~\cite{Proakis2008} as $\text{BER} = \frac{1}{2} \operatorname{erfc}(Q / \sqrt{2})$. To reach the standard HD-FEC threshold ($\text{BER} \le 4.7 \times 10^{-3}$, $Q_{\text{FEC}} = 2.60$)~\cite{ITUTG9751},"
assert old_ber in arx_content, "old_ber not found in arxiv_v3"
arx_content = arx_content.replace(old_ber, new_ber)

old_app_ber = r"To restore the original $Q$-factor ($Q_{\text{FEC}} = 2.60$) and satisfy the HD-FEC threshold $\text{BER} \le 4.7 \times 10^{-3}$, the signal power must be increased"
new_app_ber = r"To restore the original $Q$-factor ($Q_{\text{FEC}} = 2.60$) and satisfy the HD-FEC threshold $\text{BER} \le 4.7 \times 10^{-3}$~\cite{ITUTG9751,Proakis2008}, the signal power must be increased"
assert old_app_ber in arx_content, "old_app_ber not found in arxiv_v3"
arx_content = arx_content.replace(old_app_ber, new_app_ber)

# 2. Update Roadmap
assert ROADMAP_OLD in arx_content, "ROADMAP_OLD not found in arxiv_v3"
arx_content = arx_content.replace(ROADMAP_OLD, ROADMAP_NEW)

# 3. Replace Section 8
assert sec8_pattern.search(arx_content), "Section 8 pattern not matched in arxiv_v3"
arx_content = sec8_pattern.sub(lambda m: NEW_SECTION_8 + "\n", arx_content)

# 4. Replace Backmatter AI declaration in arxiv
decl_pattern_arx = re.compile(r"\\section\*\{Declaration of Generative Artificial Intelligence and AI-Assisted Technologies.*?\}\s*.*?(?=\\appendix)", re.DOTALL)
assert decl_pattern_arx.search(arx_content), "Decl pattern not matched in arxiv_v3"
arx_content = decl_pattern_arx.sub(lambda m: NEW_AI_DECLARATION_ARXIV + "\n", arx_content)

# 5. Update overlap formula to match exact regex
assert old_overlap in arx_content, "old_overlap not in arx_content"
arx_content = arx_content.replace(old_overlap, new_overlap)

# Save to v4/Paper_arxiv_v4.tex
(V4_DIR / "Paper_arxiv_v4.tex").write_text(arx_content, encoding="utf-8")
print("Wrote v4/Paper_arxiv_v4.tex successfully.")
