import fitz  # PyMuPDF
import re
import os

pdf_dir = r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\Codex Máxima"

papers = [
    "2023-Transmission of optical communication signals through ring core fiber using perfect vortex beams.pdf",
    "2021-Evaluating the coupling efficiency of OAM beams into ring-core optical fibers.pdf",
    "2021-Engineering Entangled Photons for Transmission in Ring-Core Optical Fibers.pdf",
    "2026-Second-order moment equivalence of twisted Gaussian Schell model beams and orbital angular momentum eigenmodes.pdf"
]

print("=== STARTING PDF EXTRACTION ===")
for p in papers:
    full_path = os.path.join(pdf_dir, p)
    if not os.path.exists(full_path):
        print(f"File not found: {p}")
        continue
    doc = fitz.open(full_path)
    print(f"\n==================================================")
    print(f"PAPER: {p} (Pages: {len(doc)})")
    print(f"==================================================")
    full_text = ""
    for page_num in range(len(doc)):
        full_text += f"\n--- Page {page_num+1} ---\n" + doc[page_num].get_text()
    
    # Search for key parameters
    keywords = ["8.6", "dB", "coupling", "efficiency", "ring", "core", "radius", "radii", "width", "wavelength", "numerical aperture", "NA", "BER", "threshold", "purity", "loss", "graded-index", "GRIN", "OAM", "PVB", "Laguerre", "LG"]
    
    # Specifically search for "8.6"
    matches_86 = [m.start() for m in re.finditer(r"8\.6", full_text)]
    print(f"Matches for '8.6': {len(matches_86)}")
    for idx in matches_86:
        snippet = full_text[max(0, idx-200):min(len(full_text), idx+200)]
        print(f"SNIPPET for 8.6:\n{snippet}\n")
        
    # Search for fiber specs: core radius, RI, etc.
    fiber_matches = re.findall(r"([^.\n]*?(?:ring[- ]core|graded[- ]index|inner radius|outer radius|cladding|numerical aperture|fiber length|300\s*m|core diameter|\bNA\b)[^.\n]*?\.)", full_text, re.IGNORECASE)
    print(f"Found {len(fiber_matches)} fiber-related sentences. Showing top 10:")
    for s in fiber_matches[:10]:
        print(f" - {s.strip()}")
