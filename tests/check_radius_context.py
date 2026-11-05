"""
Examine all occurrences of radius and radii in Paper_arxiv_v2.tex and Paper_revista_v2.tex.
"""
import re
from pathlib import Path

arxiv_tex = Path(r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v2\Paper_arxiv_v2.tex")
lines = arxiv_tex.read_text(encoding="utf-8").splitlines()

print("=== ALL OCCURRENCES OF 'RADIUS' AND 'RADII' IN Paper_arxiv_v2.tex ===")
for i, line in enumerate(lines, 1):
    lower = line.lower()
    if 'radius' in lower or 'radii' in lower:
        # highlight
        highlighted = re.sub(r'\b(radii|radius)\b', r'***\1***', line, flags=re.IGNORECASE)
        print(f"L{i:03d}: {highlighted}")
