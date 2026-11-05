import os, re, zipfile, hashlib
from pathlib import Path

v2_path = Path("v2")
zip_path = v2_path / "overleaf_bundle_v2.zip"

print("=== FORENSIC CHECK 1: Facade and Dummy Detection ===")
# Check for trivial or dummy functions in Python scripts
facades = []
for py in (v2_path / "scripts").glob("*.py"):
    code = py.read_text(encoding="utf-8")
    # Search for dummy passes or NotImplementedError
    if re.search(r"def\s+\w+\([^)]*\):\s*(?:pass|\.\.\.|return None|return True|return False)\s*$", code, re.MULTILINE):
        facades.append(f"Facade function found in {py}")
    if "NotImplementedError" in code:
        facades.append(f"NotImplementedError found in {py}")

print(f"Facade functions found: {len(facades)}")
assert len(facades) == 0, f"Facades found: {facades}"

print("\n=== FORENSIC CHECK 2: Hardcoded Test Bypasses ===")
# Check test suite for monkeypatching, mock bypasses, or skipped asserts
test_suite = Path("tests/test_v2_suite.py").read_text(encoding="utf-8")
bypasses = []
if "unittest.mock" in test_suite:
    bypasses.append("unittest.mock imported in test suite")
if "@unittest.skip(" in test_suite:
    bypasses.append("Hardcoded @unittest.skip found in test suite")

print(f"Hardcoded bypasses in test suite: {len(bypasses)}")
assert len(bypasses) == 0, f"Bypasses found: {bypasses}"

print("\n=== FORENSIC CHECK 3: Pre-populated or Fabricated Verification Artifacts ===")
# Check if overleaf_bundle_v2.zip contains pre-compiled binaries or logs
with zipfile.ZipFile(zip_path, "r") as z:
    for name in z.namelist():
        if name.endswith((".log", ".aux", ".out", ".toc", ".synctex.gz", ".pyc")):
            raise AssertionError(f"ZIP contains intermediate compiler or cache artifact: {name}")

print("ZIP contains NO intermediate compiler logs or cached binaries.")

print("\n=== FORENSIC CHECK 4: Member Completeness and Structural Integrity ===")
expected_members = [
    "Paper_arxiv_v2.tex",
    "Paper_arxiv_v2.bbl",
    "Paper_revista_v2.tex",
    "Paper_revista_v2.bbl",
    "references.bib",
    "optica-article.cls",
    "opticajnl.bst",
    "jabbrv.sty",
    "jabbrv-ltwa-all.ldf",
    "jabbrv-ltwa-en.ldf",
    "RESPUESTAS_REVISION_V2.md",
    "styles/opticajournal.sty",
    "figures/fig1_pvb_profiles_divergence.pdf",
    "figures/fig2_radial_overlap_matrix.pdf",
    "figures/fig3_frame_spectrum_bounds.pdf",
    "figures/fig4_turbulence_rkhs_recovery.pdf",
    "figures/fig5_quantum_povm_entanglement.pdf",
    "scripts/generate_fig1_profiles.py",
    "scripts/generate_fig2_overlap.py",
    "scripts/generate_fig3_frame_bounds.py",
    "scripts/generate_fig4_turbulence.py",
    "scripts/generate_fig5_quantum.py",
    "scripts/run_all_simulations.py",
]

with zipfile.ZipFile(zip_path, "r") as z:
    zip_members = z.namelist()
    for exp in expected_members:
        assert exp in zip_members, f"Missing expected member: {exp}"
    print(f"All {len(expected_members)} expected members present in ZIP.")
    assert len(zip_members) == len(expected_members), f"Unexpected extra members: {set(zip_members) - set(expected_members)}"

print("\nALL FORENSIC CHECKS PASSED: CLEAN!")
