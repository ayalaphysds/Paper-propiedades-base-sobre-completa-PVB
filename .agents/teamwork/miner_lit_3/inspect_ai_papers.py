import fitz
import os
import re

pdf_dir = r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\Codex Máxima"

ai_papers = [
    "2026-Extending human creativity with AI.pdf",
    "2026-DENARIO Project Deep Knowledge Artificial Intelligence Agents for Scientific Discovery.pdf",
    "2026-generative ai for research and thesis work.pdf",
    "2026-arxiv-PaperBanana  Automating Academic Illustration for AI Scientists.pdf",
    "2026-arxiv-TheoPhysEval Assessing AI agents at autonomous theoretical physics problem solving.pdf",
    "2025-Using AI in Academic Writing and Research_ A Complete Guide to Effective and Ethical Academic A.pdf",
    "2024-The Use of Artificial Intelligence in Writing Scientific Review Articles.pdf"
]

print("=== INSPECTING AI PAPERS ===")
for p in ai_papers:
    full_path = os.path.join(pdf_dir, p)
    if not os.path.exists(full_path):
        print(f"NOT FOUND: {p}")
        continue
    doc = fitz.open(full_path)
    print(f"\n==================================================")
    print(f"FILE: {p} (Pages: {len(doc)})")
    first_page = doc[0].get_text()
    print("--- Page 1 excerpt ---")
    print("\n".join(first_page.splitlines()[:25]))
    
    # Try to extract title, author, doi
    full_text_sample = "\n".join([doc[i].get_text() for i in range(min(3, len(doc)))])
    dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', full_text_sample)
    arxivs = re.findall(r'arXiv:\d{4}\.\d{4,5}', full_text_sample)
    print(f"DOIs found: {set(dois)}")
    print(f"arXiv found: {set(arxivs)}")
