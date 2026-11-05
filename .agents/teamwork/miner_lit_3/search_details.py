import re

def search_file(fname, patterns):
    print(f"\n==================== SEARCHING {fname} ====================")
    with open(fname, "r", encoding="utf-8") as f:
        text = f.read()
    for pat in patterns:
        print(f"\n--- PATTERN: {pat} ---")
        matches = [m.start() for m in re.finditer(pat, text, re.IGNORECASE)]
        print(f"Count: {len(matches)}")
        for idx in matches[:5]:
            snippet = text[max(0, idx-250):min(len(text), idx+350)]
            print("----------------- SNIPPET -----------------")
            print(snippet)

search_file("text_villalba2023.txt", ["refractive index", "graded-index", "diameter", "radius", "1550", "NA", "BER", "coupling efficiency", "8.6 dB", "formula", "integral", "overlap", "axicon"])
search_file("text_coupling2021.txt", ["refractive index", "graded-index", "radius", "cladding", "coupling efficiency", "overlap", "formula", "integral", "mode"])
