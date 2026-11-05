import hashlib
import os
from pathlib import Path

def inspect_figures():
    v1_dir = Path("v1/figures")
    v2_dir = Path("v2/figures")
    
    figs = [
        "fig1_pvb_profiles_divergence.pdf",
        "fig2_radial_overlap_matrix.pdf",
        "fig3_frame_spectrum_bounds.pdf",
        "fig4_turbulence_rkhs_recovery.pdf",
        "fig5_quantum_povm_entanglement.pdf",
    ]
    
    print(f"{'Figure':<36} | {'v1 Size':<10} | {'v2 Size':<10} | {'v1 SHA256 (first 12)':<20} | {'v2 SHA256 (first 12)':<20} | {'Identical?'}")
    print("-" * 120)
    for fig in figs:
        f1 = v1_dir / fig
        f2 = v2_dir / fig
        
        s1 = f1.stat().st_size if f1.exists() else -1
        s2 = f2.stat().st_size if f2.exists() else -1
        
        h1 = hashlib.sha256(f1.read_bytes()).hexdigest()[:12] if f1.exists() else "N/A"
        h2 = hashlib.sha256(f2.read_bytes()).hexdigest()[:12] if f2.exists() else "N/A"
        
        identical = "IDENTICAL (COPIED!)" if h1 == h2 else "DIFFERENT (FRESH)"
        print(f"{fig:<36} | {s1:<10} | {s2:<10} | {h1:<20} | {h2:<20} | {identical}")

if __name__ == "__main__":
    inspect_figures()
