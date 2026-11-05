import fitz
import os

pdf_dir = r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\Codex Máxima"

def extract_details(filename, output_name):
    doc = fitz.open(os.path.join(pdf_dir, filename))
    with open(output_name, "w", encoding="utf-8") as f:
        f.write(f"=== {filename} ===\n\n")
        for i, page in enumerate(doc):
            f.write(f"\n--- PAGE {i+1} ---\n")
            f.write(page.get_text())

extract_details("2023-Transmission of optical communication signals through ring core fiber using perfect vortex beams.pdf", "text_villalba2023.txt")
extract_details("2021-Evaluating the coupling efficiency of OAM beams into ring-core optical fibers.pdf", "text_coupling2021.txt")
extract_details("2021-Engineering Entangled Photons for Transmission in Ring-Core Optical Fibers.pdf", "text_entangled2021.txt")
extract_details("2026-Second-order moment equivalence of twisted Gaussian Schell model beams and orbital angular momentum eigenmodes.pdf", "text_ferreira2026.txt")

print("Detailed text files written successfully.")
