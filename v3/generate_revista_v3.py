import os
import re

arxiv_path = r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v3\Paper_arxiv_v3.tex"
revista_path = r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v3\Paper_revista_v3.tex"

with open(arxiv_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Preamble & Front Matter
preamble = r"""\documentclass{optica-article}

\journal{opticajournal}
\articletype{Research Article}

\usepackage{amsmath}
\let\Bbbk\relax
\usepackage{amssymb,amsfonts}
\let\openbox\relax
\usepackage{amsthm}
\usepackage{bm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage{lineno}
\linenumbers

\newtheorem{theorem}{Theorem}
\newtheorem{corollary}{Corollary}
\newtheorem{definition}{Definition}
\newtheorem{lemma}{Lemma}
\newtheorem{proposition}{Proposition}

\begin{document}

\title{Properties of Overcomplete Continuous Frames in Perfect Optical Vortex Beams: Classical and Quantum Foundations}

\author{Sebastián Ayala\authormark{1,*}}

\address{\authormark{1}Investigador Independiente, Cauquenes, Región del Maule, Chile}

\email{\authormark{*}ayala.phys.ds@gmail.com; ORCID: 0009-0003-7348-3883}
"""

# Extract Abstract
idx_abstract_start = text.find(r"\begin{abstract}")
idx_abstract_end = text.find(r"\end{abstract}") + len(r"\end{abstract}")
abstract = text[idx_abstract_start:idx_abstract_end]

# Extract Main Body (Sections 1 to 10)
idx_intro = text.find(r"\section{Introduction}")
idx_funding = text.find(r"\section*{Funding}")
main_body = text[idx_intro:idx_funding].strip()

# Extract Appendices A to E
idx_appendix = text.find(r"\appendix")
idx_bib = text.find(r"\bibliographystyle{ieeetr}")
appendices = text[idx_appendix:idx_bib].strip()

# Extract Back Matter text items
funding_text = "This research was conducted as an independent theoretical investigation without external grant funding."
ack_text = "The author gratefully acknowledges stimulating discussions with collaborators and colleagues in structured light and quantum optics, in particular colleagues associated with recent investigations in twisted Gaussian Schell-model beams and ring-core fiber optical communications."
disclosures_text = "The author declares no conflicts of interest."
data_text = "All analytical derivations, Python numerical simulation scripts, and figure plotting routines supporting the findings of this study are available within the version control repository and can be reproduced directly using standard scientific Python packages."
ai_text = r"""During the preparation of this manuscript, the author utilized advanced AI-assisted language and reasoning platforms (including the Google Antigravity platform, Gemini reasoning engines, and the Teamwork multi-agent architecture) to assist with LaTeX manuscript drafting, formatting compliance, syntactic validation, and reproducible numerical simulation script structuring, following ethical recommendations and established methodological frameworks~\cite{Jauhiainen2026,Zhu2026PaperBanana,Haber2025,OToole2024,VillaescusaNavarro2026,Chandra2026TheoPhysEval,Kacena2024}. All theoretical concepts, mathematical theorems, functional-analytic proofs, physical interpretations, and analytical derivations were directed, rigorously verified, and validated in full detail by the author. The author assumes complete and sole responsibility for all intellectual content, mathematical derivations, scientific integrity, and conclusions presented in this publication, in full compliance with COPE, Optica Publishing Group, and American Physical Society (APS) ethical publishing guidelines."""

backmatter = f"""\\begin{{backmatter}}
\\bmsection{{Funding}}
{funding_text}

\\bmsection{{Acknowledgment}}
{ack_text}

\\bmsection{{Disclosures}}
{disclosures_text}

\\bmsection{{Data Availability Statement}}
{data_text}

\\bmsection{{Declaration of Generative Artificial Intelligence and AI-Assisted Technologies}}
{ai_text}
\\end{{backmatter}}"""

# Assemble manuscript
manuscript = f"""{preamble}

{abstract}

{main_body}

{appendices}

{backmatter}

\\bibliography{{references}}

\\end{{document}}
"""

# Now incorporate the 7 references cleanly:
# 1. Arrizon2007:
manuscript = manuscript.replace(
    r"\cite{Chen2013,Reddy2016,Jabir2016,GarciaGarcia2014,Li2018PVB,PerezGarcia2017}",
    r"\cite{Chen2013,Reddy2016,Jabir2016,GarciaGarcia2014,Li2018PVB,PerezGarcia2017,Arrizon2007}"
)

# 2. Arfken2012:
manuscript = manuscript.replace(
    r"satisfies the modified Bessel ordinary differential equation:",
    r"satisfies the modified Bessel ordinary differential equation~\cite{Arfken2012}:"
)

# 3. Alonso2011:
manuscript = manuscript.replace(
    r"According to ISO Standard 11146~\cite{ISO11146}, the times-diffraction beam propagation factor $M^2$ is:",
    r"According to ISO Standard 11146~\cite{ISO11146} and phase-space optics~\cite{Alonso2011}, the times-diffraction beam propagation factor $M^2$ is:"
)

# 4. Klauder1985 & Perelomov1986:
manuscript = manuscript.replace(
    r"directly parallels that between Glauber coherent states and Fock number states in quantum optics (Table~\ref{tab:coherent_states}).",
    r"directly parallels that between Glauber coherent states and Fock number states in quantum optics~\cite{Klauder1985,Perelomov1986} (Table~\ref{tab:coherent_states})."
)
manuscript = manuscript.replace(
    r"Ali, Antoine, and Gazeau~\cite{Ali1993,Gazeau2009} extended frame theory",
    r"Ali, Antoine, and Gazeau~\cite{Ali1993,Gazeau2009,Klauder1985,Perelomov1986} extended frame theory"
)

# 5. Proakis2008 & ITUTG9751:
manuscript = manuscript.replace(
    r"In direct-detection optical communications at bit rate $R_b = 1\,\text{Gbps}$ ($T_b = 1.0\,\text{ns}$), the BER is governed by $\text{BER} = \frac{1}{2} \operatorname{erfc}(Q / \sqrt{2})$. To reach the HD-FEC threshold $\text{BER} = 4.7 \times 10^{-3}$, the required $Q$-factor is $Q_{\text{FEC}} = 2.60$.",
    r"In direct-detection optical communications at bit rate $R_b = 1\,\text{Gbps}$ ($T_b = 1.0\,\text{ns}$), the BER is governed by digital communication and equalization theory~\cite{Proakis2008} as $\text{BER} = \frac{1}{2} \operatorname{erfc}(Q / \sqrt{2})$. To reach the standard HD-FEC threshold ($\text{BER} \le 4.7 \times 10^{-3}$, $Q_{\text{FEC}} = 2.60$)~\cite{ITUTG9751},"
)
manuscript = manuscript.replace(
    r"satisfy the HD-FEC threshold $\text{BER} \le 4.7 \times 10^{-3}$, the signal power must be increased",
    r"satisfy the HD-FEC threshold $\text{BER} \le 4.7 \times 10^{-3}$~\cite{ITUTG9751,Proakis2008}, the signal power must be increased"
)

# Fix 3 minor overfull hboxes for perfect 0-warning typesetting
manuscript = manuscript.replace(
    r"Integrating over the azimuthal angle $\theta$ using the identity $\int_0^{2\pi} e^{i \ell \theta} e^{-i z \cos(\theta - \phi)} d\theta = 2\pi (-i)^\ell J_\ell(z) e^{i \ell \phi}$, and evaluating the resulting radial Hankel transform of the product $J_\ell(k_r \rho) J_\ell(\frac{k r}{f} \rho) \exp(-\rho^2 / w_g^2)$ via Weber's second exponential integral~\cite{Gradshteyn2014}, yields the canonical physical quasi-PVB field:",
    r"""Integrating over the azimuthal angle $\theta$ via the Jacobi--Anger identity,
\begin{equation}
\int_0^{2\pi} e^{i \ell \theta} e^{-i z \cos(\theta - \phi)} d\theta = 2\pi (-i)^\ell J_\ell(z) e^{i \ell \phi},
\label{eq:bessel_generating_integral}
\end{equation}
and evaluating the resulting radial Hankel transform of $J_\ell(k_r \rho) J_\ell(\frac{k r}{f} \rho) \exp(-\rho^2 / w_g^2)$ via Weber's second exponential integral~\cite{Gradshteyn2014}, yields the canonical physical quasi-PVB field:"""
)

manuscript = manuscript.replace(
    r"""\begin{align}
\langle \psi_{\ell_1, R_1, w_0} | \psi_{\ell_2, R_2, w_0} \rangle &= \int_0^{2\pi} d\phi \int_0^\infty r \, dr \, \psi_{\ell_1, R_1, w_0}^*(r, \phi) \psi_{\ell_2, R_2, w_0}(r, \phi) \notag \\
&= C_0(R_1) C_0(R_2) \left( \int_0^{2\pi} e^{i(\ell_2 - \ell_1)\phi} d\phi \right) \exp\left( - \frac{R_1^2 + R_2^2}{w_0^2} \right) \mathcal{I}_{\ell_1, \ell_2}(R_1, R_2; w_0),
\label{eq:inner_product_setup}
\end{align}""",
    r"""\begin{align}
\langle \psi_{\ell_1, R_1, w_0} | \psi_{\ell_2, R_2, w_0} \rangle &= \int_0^{2\pi} d\phi \int_0^\infty r \, dr \, \psi_{\ell_1, R_1, w_0}^*(r, \phi) \psi_{\ell_2, R_2, w_0}(r, \phi) \notag \\
&= C_0(R_1) C_0(R_2) \left( \int_0^{2\pi} e^{i(\ell_2 - \ell_1)\phi} d\phi \right) \notag \\
&\quad \times \exp\left( - \frac{R_1^2 + R_2^2}{w_0^2} \right) \mathcal{I}_{\ell_1, \ell_2}(R_1, R_2; w_0),
\label{eq:inner_product_setup}
\end{align}"""
)

manuscript = manuscript.replace(
    r"""    \begin{align}
    - \frac{4\ell^2 - 1}{8} w_0^2 \left[ \frac{1}{R_1 R_2} - \frac{1}{2 R_1^2} - \frac{1}{2 R_2^2} \right] &= \frac{4\ell^2 - 1}{16} w_0^2 \left[ \frac{1}{R_1^2} - \frac{2}{R_1 R_2} + \frac{1}{R_2^2} \right] \notag \\
    &= \frac{4\ell^2 - 1}{16} w_0^2 \left( \frac{1}{R_1} - \frac{1}{R_2} \right)^2 = \frac{4\ell^2 - 1}{16} \frac{w_0^2 (R_1 - R_2)^2}{R_1^2 R_2^2}.
    \label{eq:correction_algebra}
    \end{align}""",
    r"""    \begin{align}
    - \frac{4\ell^2 - 1}{8} w_0^2 \left[ \frac{1}{R_1 R_2} - \frac{1}{2 R_1^2} - \frac{1}{2 R_2^2} \right] &= \frac{4\ell^2 - 1}{16} w_0^2 \left[ \frac{1}{R_1^2} - \frac{2}{R_1 R_2} + \frac{1}{R_2^2} \right] \notag \\
    &= \frac{4\ell^2 - 1}{16} w_0^2 \left( \frac{1}{R_1} - \frac{1}{R_2} \right)^2 \notag \\
    &= \frac{4\ell^2 - 1}{16} \frac{w_0^2 (R_1 - R_2)^2}{R_1^2 R_2^2}.
    \label{eq:correction_algebra}
    \end{align}"""
)


with open(revista_path, "w", encoding="utf-8") as f:
    f.write(manuscript)

print(f"Generated {revista_path} ({len(manuscript)} bytes, {len(manuscript.splitlines())} lines).")
