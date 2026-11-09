"""
Helper utilities, physical formulas, and constants for E2E tests.
Provides exact mathematical reference implementations for opaque-box testing.
"""

import math
import os
import re
from pathlib import Path
import numpy as np
from scipy.special import iv, ive  # Modified Bessel function of the first kind
from scipy.integrate import quad

# Root repository directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
V1_DIR = PROJECT_ROOT / "v1"
SCRIPTS_DIR = V1_DIR / "scripts"
FIGURES_DIR = V1_DIR / "figures"
V2_DIR = PROJECT_ROOT / "v2"
SCRIPTS_V2_DIR = V2_DIR / "scripts"
FIGURES_V2_DIR = V2_DIR / "figures"
V3_DIR = PROJECT_ROOT / "v3"
SCRIPTS_V3_DIR = V3_DIR / "scripts"
FIGURES_V3_DIR = V3_DIR / "figures"
V4_DIR = PROJECT_ROOT / "v4"
SCRIPTS_V4_DIR = V4_DIR / "scripts"
FIGURES_V4_DIR = V4_DIR / "figures"
TEMPLATES_DIR = PROJECT_ROOT / "latex-universal-template"


# Reference Author Metadata
EXPECTED_AUTHOR_NAME = "Sebastián Ayala"
EXPECTED_AFFILIATION_KEYWORDS = ["Independent Researcher", "Investigador Independiente", "Cauquenes", "Maule", "Chile"]
EXPECTED_EMAIL = "ayala.phys.ds@gmail.com"
EXPECTED_ORCID_ID = "0009-0003-7348-3883"
EXPECTED_ORCID_URL = "https://orcid.org/0009-0003-7348-3883"

# Physical Reference Constants
LAMBDA_OPTICAL = 1550e-9  # 1550 nm paraxial telecom wavelength (m)
K_0 = 2.0 * math.pi / LAMBDA_OPTICAL  # Wavenumber (rad/m)
AIR_BREAKDOWN_FIELD = 3.0e6  # V/m (dielectric breakdown of dry air)


def exact_pvb_radial_field(r: np.ndarray, r0: float, w0: float, l: int) -> np.ndarray:
    """Exact physical quasi-PVB radial field amplitude profile.
    E(r) = exp(-(r^2 + r0^2)/w0^2) * I_l(2 * r0 * r / w0^2)
    Using ive(l, z) = I_l(z) * exp(-z):
    E(r) = exp(-(r - r0)^2 / w0^2) * ive(l, 2 * r0 * r / w0^2)
    """
    arg = 2.0 * r0 * r / (w0**2)
    return np.exp(-((r - r0)**2) / (w0**2)) * ive(l, arg)


def exact_overlap_coefficient(r1: float, r2: float, w0: float, l: int) -> float:
    """Exact closed-form normalized overlap coefficient derived from Gradshteyn & Ryzhik 6.633.2:
    gamma_l(r1, r2; w0) = I_l(r1 * r2 / w0^2) / sqrt(I_l(r1^2 / w0^2) * I_l(r2^2 / w0^2))
    Using exponentially scaled Bessel functions ive(l, z) = iv(l, z) * exp(-z):
    gamma_l = exp(-(r1 - r2)^2 / (2 * w0^2)) * ive(l, r1*r2/w0^2) / sqrt(ive(l, r1^2/w0^2) * ive(l, r2^2/w0^2))
    """
    arg12 = (r1 * r2) / (w0**2)
    arg11 = (r1**2) / (w0**2)
    arg22 = (r2**2) / (w0**2)
    
    exp_factor = math.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
    ive_12 = float(ive(l, arg12))
    ive_11 = float(ive(l, arg11))
    ive_22 = float(ive(l, arg22))
    
    if ive_11 <= 0.0 or ive_22 <= 0.0 or ive_12 <= 0.0:
        return float(exp_factor)
        
    den = math.sqrt(ive_11 * ive_22)
    return float(exp_factor * (ive_12 / den))


def asymptotic_overlap_coefficient(r1: float, r2: float, w0: float, l: int = 0) -> float:
    """Asymptotic Gaussian overlap formula in the thin-ring limit (r0 >> w0):
    gamma_asymp(r1, r2; w0) = exp(-(r1 - r2)^2 / (2 * w0^2)) * [1 + ((4*l^2 - 1)*w0^2*(r1-r2)^2)/(16*r1^2*r2^2)]
    """
    base = math.exp(-((r1 - r2)**2) / (2.0 * (w0**2)))
    correction = 1.0 + ((4.0 * (l**2) - 1.0) * (w0**2) * ((r1 - r2)**2)) / (16.0 * (r1**2) * (r2**2))
    return base * correction


def numerical_overlap_quadrature(r1: float, r2: float, w0: float, l: int) -> float:
    """Numerical quadrature computation of normalized overlap:
    Integrates r * E_l(r, r1) * E_l(r, r2) dr / sqrt(norm1 * norm2)
    """
    # Radial integrand for inner product
    def integrand(r):
        return r * exact_pvb_radial_field(r, r1, w0, l) * exact_pvb_radial_field(r, r2, w0, l)
    
    def norm_integrand1(r):
        return r * (exact_pvb_radial_field(r, r1, w0, l)**2)
    
    def norm_integrand2(r):
        return r * (exact_pvb_radial_field(r, r2, w0, l)**2)
    
    r_max = max(r1, r2) + 10.0 * w0
    val_ip, _ = quad(integrand, 0.0, r_max, limit=200)
    val_n1, _ = quad(norm_integrand1, 0.0, r_max, limit=200)
    val_n2, _ = quad(norm_integrand2, 0.0, r_max, limit=200)
    
    return float(val_ip / math.sqrt(val_n1 * val_n2))


def frame_spectrum(kr: np.ndarray, w0: float) -> np.ndarray:
    """Continuous frame eigenvalue spectrum on paraxial subspace:
    sigma(kr) = exp(-0.5 * kr^2 * w0^2)
    """
    return np.exp(-0.5 * (kr**2) * (w0**2))


def peak_intensity_model(P_power: float, r0: float, w0: float) -> float:
    """Peak optical intensity for a PVB carrying total power P:
    I_max = P / (pi^(3/2) * sqrt(2) * r0 * w0)
    """
    return P_power / ((math.pi**1.5) * math.sqrt(2.0) * r0 * w0)


def transmitted_power_under_clamping(E_damage: float, r0: float, w0: float) -> float:
    """Transmitted power when peak electric field is clamped to dielectric damage threshold:
    P = pi^(3/2) * sqrt(2) * r0 * w0 * E_damage^2
    """
    return (math.pi**1.5) * math.sqrt(2.0) * r0 * w0 * (E_damage**2)


def get_pdf_page_count(pdf_path: Path) -> int:
    """Robust binary parsing of PDF page count without external dependencies."""
    if not pdf_path.exists():
        return -1
    content = pdf_path.read_bytes()
    # Match /Type /Page (excluding /Pages)
    pages = re.findall(rb"/Type\s*/Page\b", content)
    if pages:
        return len(pages)
    # Fallback to /Count <N> in Pages dictionary
    count_matches = re.findall(rb"/Count\s+(\d+)", content)
    if count_matches:
        return max(int(c) for c in count_matches)
    return 1


# V2 Specific Constants and Metadata
V2_EXPECTED_FIGURES = [
    "fig1_pvb_profiles_divergence.pdf",
    "fig2_radial_overlap_matrix.pdf",
    "fig3_frame_spectrum_bounds.pdf",
    "fig4_turbulence_rkhs_recovery.pdf",
    "fig5_quantum_povm_entanglement.pdf",
]

V2_EXPECTED_SCRIPTS = [
    "generate_fig1_profiles.py",
    "generate_fig2_overlap.py",
    "generate_fig3_frame_bounds.py",
    "generate_fig4_turbulence.py",
    "generate_fig5_quantum.py",
    "run_all_simulations.py",
]

V2_AI_CITATIONS = ["Jauhiainen2026", "Zhu2026PaperBanana", "Haber2025"]

V2_REVISION_COMMENTS = {
    1: ["radii", "radius", "plural", "ortografía", "spelling"],
    2: ["abstract", "q1", "equation", "ecuación", "cita", "brackets"],
    3: ["sección 8", "section 8", "multi-fila", "multi-row", "grid", "cuadrícula", "textbf", "etiquetas"],
    4: ["sobrecompletitud", "overcompleteness", "ayala (2026)", "ayala 2026", "secciones 1 a 4", "delimitación"],
    5: ["inteligencia artificial", "artificial intelligence", "codex máxima", "jauhiainen", "paperbanana", "haber", "ética"],
    6: ["autónomo", "autonomous", "premisa", "marco continuo", "frame", "ventajas clásicas", "cuánticas"],
    7: ["justificación", "justified", "fundamentada", "decisiones", "técnica"],
}


def validate_abstract_cleanliness(abstract_text: str) -> list:
    """Validates that an abstract contains no raw equations, direct equation numbers, or bracketed citations.
    Returns list of violation descriptions (empty if valid).
    """
    violations = []
    # Check for raw math environments
    if re.search(r"\\begin\{(?:equation|align|gather|multline)\*?\}", abstract_text):
        violations.append("Contains raw equation environment (\\begin{equation...})")
    if re.search(r"\$\$.*?\$\$", abstract_text, flags=re.DOTALL):
        violations.append("Contains display math ($$...$$)")
    if re.search(r"\\\[.*?\\\]", abstract_text, flags=re.DOTALL):
        violations.append(r"Contains display math (\[...\])")
    # Check for raw equation citations: "Eq. (1)", "equation (2)", etc.
    if re.search(r"(?i)\b(?:eq\.|equation|equations|fórmula)\s*\(\d+\)", abstract_text):
        violations.append("Contains explicit direct equation citation (Eq. (N))")
    if re.search(r"\\eqref\{[^}]+\}", abstract_text):
        violations.append("Contains \\eqref{...}")
    # Check for bracketed citations: \cite{...} or [1], [1, 2]
    if re.search(r"\\cite[pt]?\{[^}]+\}", abstract_text):
        violations.append("Contains \\cite{...} command in abstract")
    if re.search(r"\[\d+(?:[,\s–-]+\d+)*\]", abstract_text):
        violations.append("Contains bracketed numeric citation [N] in abstract")
    return violations


def validate_technical_spelling_radii(text: str) -> list:
    """Validates adherence to technical English standard: 'radii' for plural ring radii.
    Flags improper usages such as 'multiple radius', 'different radius', 'all radius', 'radiuses'.
    """
    violations = []
    if re.search(r"(?i)\bradiuses\b", text):
        violations.append("Found non-standard plural 'radiuses'")
    pattern = r"(?i)\b(?:multiple|different|various|several|two|three|four|both|all|distinct|these|those)\s+radius\b"
    matches = re.findall(pattern, text)
    if matches:
        violations.append(f"Found improper singular with plural quantifier: {matches}")
    return violations


def reproducing_kernel(r: float, r_prime: float, w0: float, l: int = 0) -> float:
    """Exact reproducing kernel K_l(r, r') of the paraxial PVB subspace."""
    return exact_overlap_coefficient(r, r_prime, w0, l)


def frame_condition_number(w0: float, k_max: float) -> float:
    """Condition number kappa = B / A for continuous frame on paraxial band [0, K_max].
    A = exp(-0.5 * K_max^2 * w0^2), B = 1.0.
    """
    a = math.exp(-0.5 * (k_max**2) * (w0**2))
    b = 1.0
    return b / a


def find_pdflatex_compiler() -> str:
    """Finds pdflatex compiler in PATH or known installation locations."""
    import shutil
    found = shutil.which("pdflatex")
    if found:
        return found
    fallback = Path(r"C:\Users\sayal\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe")
    if fallback.exists():
        return str(fallback)
    return ""


# V3 Specific Constants and Metadata
V3_EXPECTED_FIGURES = [
    "fig1_pvb_profiles_divergence.pdf",
    "fig2_radial_overlap_matrix.pdf",
    "fig3_frame_spectrum_bounds.pdf",
    "fig4_turbulence_rkhs_recovery.pdf",
    "fig5_quantum_povm_entanglement.pdf",
]

V3_EXPECTED_SCRIPTS = [
    "generate_fig1_profiles.py",
    "generate_fig2_overlap.py",
    "generate_fig3_frame_bounds.py",
    "generate_fig4_turbulence.py",
    "generate_fig5_quantum.py",
    "run_all_simulations.py",
]

V3_EXPECTED_BIBTEX_COUNT = 70

V3_AUTHOR_METADATA_EXACT = {
    "name": "Sebastián Ayala",
    "affiliation": "Investigador Independiente, Cauquenes, Región del Maule, Chile",
    "email": "ayala.phys.ds@gmail.com",
    "orcid": "0009-0003-7348-3883",
}

V3_KEY_AUTHORS_CITED = [
    "Villalba",
    "Rojas-Rojas",
    "Ayala",
    "Jauhiainen",
    "PaperBanana",
    "Haber",
]


def calculate_rcf_power_advantage(
    eta_pvb: float = 0.98,
    eta_lg: float = 0.203,
    isi_lg: float = 0.50,
    isi_pvb: float = 0.00,
) -> tuple:
    """Theoretical first-principles 8.6 dB decomposition in Ring-Core Fibers (RCF):
    Delta_coupling = 10 * log10(eta_pvb / eta_lg) ~ 6.83 dB
    Delta_isi = 10 * log10((1 + isi_lg) / (1 + isi_pvb)) ~ 1.77 dB
    Total Delta = Delta_coupling + Delta_isi ~ 8.60 dB
    """
    delta_coupling = 10.0 * math.log10(eta_pvb / eta_lg)
    delta_isi = 10.0 * math.log10((1.0 + isi_lg) / (1.0 + isi_pvb))
    return delta_coupling, delta_isi, delta_coupling + delta_isi


def check_latex_log_for_unresolved_references(log_text: str) -> list:
    """Detects unresolved references or citations in LaTeX compiler logs.
    Returns list of violations.
    """
    violations = []
    undef_cites = re.findall(r"Citation [`']([^']+)' on page \d+ undefined", log_text)
    if undef_cites:
        violations.append(f"Undefined citations detected: {set(undef_cites)}")
    
    undef_refs = re.findall(r"Reference [`']([^']+)' on page \d+ undefined", log_text)
    if undef_refs:
        violations.append(f"Undefined references detected: {set(undef_refs)}")
        
    if "There were undefined references" in log_text:
        violations.append("LaTeX log reports 'There were undefined references'")
        
    if re.search(r"citation\s+\?\s+undefined", log_text, re.IGNORECASE):
        violations.append("Citation '?' undefined found in log")
        
    return violations


def validate_algebraic_bridges(text: str) -> dict:
    """Scans text for explicit algebraic bridge phrases connecting numbered equations."""
    patterns = [
        r"(?i)(?:sustituyendo|sustituir|reemplazando|substituting|inserting|combining)\s+(?:la\s+)?(?:ec\.|ecuaci[óo]n|eq\.|equation)\s*(?:\([^\)]+\)|[0-9]+)",
        r"(?i)(?:a\s+partir\s+de|from|using|utilizando)\s+(?:la\s+)?(?:ec\.|ecuaci[óo]n|eq\.|equation)\s*(?:\([^\)]+\)|[0-9]+)",
        r"(?i)(?:obtenemos|se\s+obtiene|we\s+obtain|yields|which\s+gives)\s+(?:la\s+)?(?:ec\.|ecuaci[óo]n|eq\.|equation)\s*(?:\([^\)]+\)|[0-9]+)",
        r"(?i)(?:conduce\s+a|leads\s+to|resulting\s+in)\s+(?:la\s+)?(?:ec\.|ecuaci[óo]n|eq\.|equation)\s*(?:\([^\)]+\)|[0-9]+)",
    ]
    found = {}
    for p in patterns:
        matches = re.findall(p, text)
        if matches:
            found[p] = len(matches)
    return found


# ==============================================================================
# V4 Constants, Prohibited Artifacts, and Sanitization Validators
# ==============================================================================

V4_EXPECTED_FIGURES = [
    "fig1_pvb_profiles_divergence.pdf",
    "fig2_radial_overlap_matrix.pdf",
    "fig3_frame_spectrum_bounds.pdf",
    "fig4_turbulence_rkhs_recovery.pdf",
    "fig5_quantum_povm_entanglement.pdf",
]

V4_EXPECTED_SCRIPTS = [
    "generate_fig1_profiles.py",
    "generate_fig2_overlap.py",
    "generate_fig3_frame_bounds.py",
    "generate_fig4_turbulence.py",
    "generate_fig5_quantum.py",
    "run_all_simulations.py",
]

V4_EXPECTED_BIBTEX_COUNT = 70

V4_AUTHOR_METADATA_EXACT = {
    "name": "Sebastián Ayala",
    "affiliation": "Investigador Independiente, Cauquenes, Región del Maule, Chile",
    "email": "ayala.phys.ds@gmail.com",
    "orcid": "0009-0003-7348-3883",
}

PROHIBITED_INTERNAL_PATTERNS = [
    (r"(?i)\bcodex[-_\s]*m[aá]xima\b", "References to internal repository 'Codex Máxima'"),
    (r"(?i)\bminer_lit(?:_[a-z0-9]+)*\b", "Internal bot handle 'miner_lit*'"),
    (r"(?i)\bexplorer_math(?:_[a-z0-9]+)*\b", "Internal bot handle 'explorer_math*'"),
    (r"(?i)\bexplorer_survey(?:_[a-z0-9]+)*\b", "Internal bot handle 'explorer_survey*'"),
    (r"(?i)\bworker_arxiv(?:_[a-z0-9]+)*\b", "Internal bot handle 'worker_arxiv*'"),
    (r"(?i)\bworker_revista(?:_[a-z0-9]+)*\b", "Internal bot handle 'worker_revista*'"),
    (r"(?i)\bworker_m[0-9](?:_[a-z0-9]+)*\b", "Internal bot handle 'worker_m*'"),
    (r"(?i)\bworker_(?:infra|sim|theory|latex|package|remediation)(?:_[a-z0-9]+)*\b", "Internal worker bot handle"),
    (r"(?i)\bcritic_referee(?:_[a-z0-9]+)*\b", "Internal bot handle 'critic_referee*'"),
    (r"(?i)\bchallenger(?:_[a-z0-9]+)*\b", "Internal bot handle 'challenger*'"),
    (r"(?i)\breviewer(?:_[a-z0-9]+)*\b", "Internal bot handle 'reviewer*'"),
    (r"(?i)\bauditor(?:_[a-z0-9]+)*\b", "Internal bot handle 'auditor*'"),
    (r"(?i)\bvictory_auditor\b", "Internal bot handle 'victory_auditor'"),
    (r"(?i)\bsentinel\b", "Internal bot handle 'sentinel'"),
    (r"(?i)\bsub_orch(?:_[a-z0-9]+)*\b", "Internal bot handle 'sub_orch*'"),
    (r"(?i)\bteamwork\s+multi[-_\s]*agent\b", "Internal 'teamwork multi-agent' architecture narrative"),
    (r"(?i)\bteamwork\s+hierarchy\b", "Internal 'teamwork hierarchy' mention"),
    (r"(?i)\bthree[-_\s]*iteration\s+triad\b", "Internal 'three-iteration triad' narrative"),
    (r"(?i)\bv1\s*(?:to|->|\\to)\s*v2\s*(?:to|->|\\to)\s*v3\b", "Internal 'v1 -> v2 -> v3' triad narrative"),
    (r"(?i)\bversion\s+1\s*\([^)]*initial\s+formulation\)", "Internal iteration description"),
    (r"(?i)\bversion\s+2\s*\([^)]*structural\s+reorganization\)", "Internal iteration description"),
    (r"(?i)\bversion\s+3\s*\([^)]*mathematical\s+exhaustiveness\)", "Internal iteration description"),
]


def validate_text_sanitization(text: str, filename: str = "") -> list:
    """Scans text for prohibited internal artifacts (Codex Máxima, bot codenames, iteration triad).
    Returns list of formatted violation strings.
    """
    violations = []
    lines = text.splitlines()
    for pattern_re, desc in PROHIBITED_INTERNAL_PATTERNS:
        compiled = re.compile(pattern_re)
        for idx, line in enumerate(lines, 1):
            if compiled.search(line):
                # Filter out pure gitignore or self-test references if filename is test/helper
                violations.append(f"[{filename}:{idx}] {desc}: '{line.strip()[:100]}'")
    return violations



