import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
try:
    import pypdf
except ImportError:
    pypdf = None

def inspect():
    figures_dir = Path("v2/figures")
    figs = sorted(figures_dir.glob("*.pdf"))
    
    print(f"Found {len(figs)} PDF files in {figures_dir}:")
    for fig in figs:
        size = fig.stat().st_size
        raw = fig.read_bytes()
        header = raw[:5].decode("latin-1", errors="ignore")
        eof = raw[-100:].decode("latin-1", errors="ignore")
        
        has_subfigures = []
        for panel in ["(a)", "(b)", "(c)", "(d)"]:
            if panel.encode("utf-8") in raw or (panel in raw.decode("latin-1", errors="ignore")):
                has_subfigures.append(panel)
        
        # Check raw latex textbf
        has_raw_textbf = b"\\textbf" in raw or b"\\mathrm" in raw
        
        # PDF page info if pypdf is available
        page_info = "pypdf unavailable"
        if pypdf:
            try:
                reader = pypdf.PdfReader(str(fig))
                p = reader.pages[0]
                box = p.mediabox
                extracted = p.extract_text() or ""
                page_info = f"Pages: {len(reader.pages)}, MediaBox: [{float(box.width):.1f} x {float(box.height):.1f} pt], Extracted chars: {len(extracted)}"
            except Exception as e:
                page_info = f"Error: {e}"
                
        print(f"\n--- {fig.name} ---")
        print(f"  Size: {size:,} bytes | Header: {header}")
        print(f"  {page_info}")
        if pypdf:
            reader = pypdf.PdfReader(str(fig))
            text = reader.pages[0].extract_text() or ""
            print("  Sample extracted lines:")
            for line in text.splitlines()[:6]:
                print(f"    | {line}")
        print(f"  Contains raw \\textbf: {b'\\textbf' in raw}")


if __name__ == "__main__":
    inspect()
