#!/usr/bin/env python3
"""
run_all_simulations.py
Master Simulation Runner & Artifact Validation Suite for Version 3 (v3).

Milestone M1: Executes all 5 modular simulation scripts and verifies that all
publication-quality vector PDF figures in 2x2 multi-panel layout are generated and valid:
1. v3/figures/fig1_pvb_profiles_divergence.pdf
2. v3/figures/fig2_radial_overlap_matrix.pdf
3. v3/figures/fig3_frame_spectrum_bounds.pdf
4. v3/figures/fig4_turbulence_rkhs_recovery.pdf
5. v3/figures/fig5_quantum_povm_entanglement.pdf

Author: Sebastián Ayala (Cauquenes, Chile)
Paper: Overcomplete Perfect Vortex Beams
"""

import sys
import time
from pathlib import Path

# Adaptive directory discovery for repository and extracted bundle environments
SCRIPTS_DIR = Path(__file__).resolve().parent
if (SCRIPTS_DIR.parent / "figures").is_dir():
    FIGURES_V3_DIR = SCRIPTS_DIR.parent / "figures"
elif (SCRIPTS_DIR.parent.parent / "v3" / "figures").is_dir():
    FIGURES_V3_DIR = SCRIPTS_DIR.parent.parent / "v3" / "figures"
else:
    FIGURES_V3_DIR = SCRIPTS_DIR.parent / "figures"
FIGURES_V3_DIR.mkdir(parents=True, exist_ok=True)

# Ensure scripts directory and parent roots are in sys.path
for p in [SCRIPTS_DIR, SCRIPTS_DIR.parent, SCRIPTS_DIR.parent.parent]:
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Import individual simulation generators
from generate_fig1_profiles import generate_figure_1
from generate_fig2_overlap import generate_figure_2
from generate_fig3_frame_bounds import generate_figure_3
from generate_fig4_turbulence import generate_figure_4
from generate_fig5_quantum import generate_figure_5


SIMULATION_JOBS = [
    {
        "id": 1,
        "name": "Figure 1: PVB Intensity Profiles & Physical Divergence (2x2)",
        "output_file": FIGURES_V3_DIR / "fig1_pvb_profiles_divergence.pdf",
        "runner": generate_figure_1,
        "min_size_bytes": 10_000,
    },
    {
        "id": 2,
        "name": "Figure 2: Radial Overlap Matrix & Universal Cross-Talk (2x2)",
        "output_file": FIGURES_V3_DIR / "fig2_radial_overlap_matrix.pdf",
        "runner": generate_figure_2,
        "min_size_bytes": 10_000,
    },
    {
        "id": 3,
        "name": "Figure 3: Continuous Frame Bounds & Dual Reconstruction (2x2)",
        "output_file": FIGURES_V3_DIR / "fig3_frame_spectrum_bounds.pdf",
        "runner": generate_figure_3,
        "min_size_bytes": 10_000,
    },
    {
        "id": 4,
        "name": "Figure 4: Kolmogorov Turbulence & RKHS Noise Projection (2x2)",
        "output_file": FIGURES_V3_DIR / "fig4_turbulence_rkhs_recovery.pdf",
        "runner": generate_figure_4,
        "min_size_bytes": 20_000,
    },
    {
        "id": 5,
        "name": "Figure 5: High-Dimensional POVM & SPDC Entanglement (2x2)",
        "output_file": FIGURES_V3_DIR / "fig5_quantum_povm_entanglement.pdf",
        "runner": generate_figure_5,
        "min_size_bytes": 10_000,
    },
]


def validate_pdf_file(pdf_path: Path, min_bytes: int = 10_000) -> tuple[bool, str]:
    """Validates that a generated PDF exists, has sufficient size, and has valid PDF header."""
    if not pdf_path.exists():
        return False, f"File does not exist: {pdf_path}"

    file_size = pdf_path.stat().st_size
    if file_size < min_bytes:
        return False, f"File size ({file_size} bytes) below minimum threshold ({min_bytes} bytes)"

    header = pdf_path.read_bytes()[:5]
    if header != b"%PDF-":
        return False, f"Invalid PDF magic header: {header}"

    return True, f"Valid vector PDF ({file_size / 1024:.1f} KB)"


def run_all() -> bool:
    """Executes all simulation jobs sequentially and displays dashboard summary."""
    print("=" * 80)
    print("      MASTER SIMULATION RUNNER: OVERCOMPLETE PVB PUBLICATION FIGURES (v3)")
    print("      Author: Sebastián Ayala (Cauquenes, Chile) | Milestone M1")
    print("=" * 80)

    FIGURES_V3_DIR.mkdir(parents=True, exist_ok=True)
    all_success = True
    total_start = time.time()
    results = []

    for job in SIMULATION_JOBS:
        print(f"\n[*] Executing Job {job['id']}: {job['name']}...")
        job_start = time.time()
        try:
            job["runner"](job["output_file"])
            job_time = time.time() - job_start

            valid, msg = validate_pdf_file(job["output_file"], job["min_size_bytes"])
            if valid:
                print(f"    [+] SUCCESS ({job_time:.2f}s) -> {job['output_file'].name} [{msg}]")
                results.append((job["id"], job["name"], "PASSED", job_time, msg))
            else:
                print(f"    [!] VALIDATION FAILED: {msg}")
                results.append((job["id"], job["name"], "INVALID", job_time, msg))
                all_success = False
        except Exception as e:
            job_time = time.time() - job_start
            print(f"    [!] EXECUTION ERROR: {e}")
            results.append((job["id"], job["name"], "FAILED", job_time, str(e)))
            all_success = False

    total_time = time.time() - total_start

    # Summary table
    print("\n" + "=" * 80)
    print(f"{'Job':<5} | {'Description':<42} | {'Status':<8} | {'Time':<7} | {'Details'}")
    print("-" * 80)
    for j_id, j_name, j_status, j_time, j_msg in results:
        print(f"{j_id:<5} | {j_name[:42]:<42} | {j_status:<8} | {j_time:5.2f}s | {j_msg}")
    print("=" * 80)
    print(f"Total Suite Execution Time: {total_time:.2f} seconds")

    if all_success:
        print("\n[+] ALL 5 PUBLICATION-QUALITY VECTOR FIGURES GENERATED & VALIDATED SUCCESSFULLY.")
        return True
    else:
        print("\n[!] SIMULATION SUITE COMPLETED WITH ONE OR MORE FAILURES.")
        return False


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
