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
