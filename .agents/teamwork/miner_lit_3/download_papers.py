import urllib.request
import os
import fitz

codex_dir = r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\Codex Máxima"

papers_to_download = [
    {
        "url": "https://arxiv.org/pdf/2209.01723.pdf",
        "filename": "2022-arxiv-Customizable Laguerre-Gaussian Perfect Vortex Beams.pdf"
    },
    {
        "url": "https://arxiv.org/pdf/2209.00481.pdf",
        "filename": "2022-arxiv-Versatile Non-diffracting Perfect Vortex Beams.pdf"
    },
    {
        "url": "https://arxiv.org/pdf/2608.20688.pdf",
        "filename": "2026-arxiv-VortexChat An agentic framework for autonomous multi-objective integrated photonic design.pdf"
    }
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for p in papers_to_download:
    target_path = os.path.join(codex_dir, p["filename"])
    if os.path.exists(target_path):
        print(f"Already exists: {p['filename']}")
        continue
    print(f"Downloading: {p['filename']} from {p['url']}...")
    try:
        req = urllib.request.Request(p["url"], headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        with open(target_path, "wb") as f:
            f.write(content)
        # Verify with fitz
        doc = fitz.open(target_path)
        print(f"SUCCESS: {p['filename']} downloaded, valid PDF with {len(doc)} pages.")
    except Exception as e:
        print(f"FAILED to download {p['filename']}: {e}")
