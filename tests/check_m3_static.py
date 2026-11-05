"""
Static and adversarial check script for Milestone 3 deliverables.
"""
import re
from pathlib import Path

REPO_ROOT = Path(r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB")
V2_DIR = REPO_ROOT / "v2"
ARXIV_TEX = V2_DIR / "Paper_arxiv_v2.tex"
REVISTA_TEX = V2_DIR / "Paper_revista_v2.tex"
BIB_FILE = V2_DIR / "references.bib"
FIG_DIR = V2_DIR / "figures"

def check_citations(tex_path, bib_path):
    tex_text = tex_path.read_text(encoding="utf-8")
    # match \cite{...}, \citep{...}, \citet{...}
    cites = re.findall(r'\\cite[a-zA-Z]*\{([^}]+)\}', tex_text)
    cited_keys = set()
    for c in cites:
        for k in c.split(','):
            k_clean = k.strip()
            if k_clean:
                cited_keys.add(k_clean)
                
    bib_text = bib_path.read_text(encoding="utf-8")
    bib_keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', bib_text))
    
    missing = cited_keys - bib_keys
    print(f"[{tex_path.name}] Total unique citation keys in tex: {len(cited_keys)}")
    print(f"[{tex_path.name}] Missing keys in bib: {missing}")
    return cited_keys, missing

def check_figures(tex_path, fig_dir):
    tex_text = tex_path.read_text(encoding="utf-8")
    fig_refs = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', tex_text)
    print(f"[{tex_path.name}] Figure includes found: {len(fig_refs)}")
    missing = []
    for f in fig_refs:
        # Normalize path
        f_norm = f.replace('\\', '/')
        if f_norm.startswith('figures/'):
            fname = f_norm[len('figures/'):]
        else:
            fname = Path(f_norm).name
        target = fig_dir / fname
        if not target.exists():
            missing.append(f)
        else:
            print(f"  Found: {f} -> {target.name} ({target.stat().st_size} bytes)")
    print(f"[{tex_path.name}] Missing figures: {missing}")
    return fig_refs, missing

def check_abstract(tex_path):
    tex_text = tex_path.read_text(encoding="utf-8")
    m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex_text, re.DOTALL)
    if not m:
        print(f"[{tex_path.name}] Abstract NOT FOUND!")
        return None
    abstract = m.group(1).strip()
    print(f"[{tex_path.name}] Abstract length: {len(abstract)} chars, {len(abstract.split())} words")
    
    # Check for \ref, \eqref, \cite
    refs = re.findall(r'\\(?:ref|eqref|cite[a-zA-Z]*)\{[^}]*\}', abstract)
    # Check for math $...$
    math_inline = re.findall(r'\$[^$]+\$', abstract)
    # Check for bracketed citations like [1] or [1,2] or (2026)
    bracket_cites = re.findall(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', abstract)
    # Check for limit notation
    limits = re.findall(r'\\lim|\\to|->', abstract)
    # Check for equation numbers like Eq. (1) or (1)
    eq_mentions = re.findall(r'(?:[Ee]q\.|[Ee]quation)\s*\(?\d+\)?|\(\d+\)', abstract)
    
    print(f"  TeX refs in abstract: {refs}")
    print(f"  Inline math in abstract: {math_inline}")
    print(f"  Bracketed cites in abstract: {bracket_cites}")
    print(f"  Limits in abstract: {limits}")
    print(f"  Equation mentions in abstract: {eq_mentions}")
    return {
        "refs": refs,
        "math_inline": math_inline,
        "bracket_cites": bracket_cites,
        "limits": limits,
        "eq_mentions": eq_mentions
    }

def check_radius_usage(tex_path):
    tex_text = tex_path.read_text(encoding="utf-8")
    lines = tex_text.splitlines()
    radius_matches = []
    radii_matches = []
    for idx, line in enumerate(lines, 1):
        if 'radius' in line.lower():
            radius_matches.append((idx, line.strip()))
        if 'radii' in line.lower():
            radii_matches.append((idx, line.strip()))
            
    print(f"[{tex_path.name}] Lines with 'radius': {len(radius_matches)}")
    print(f"[{tex_path.name}] Lines with 'radii': {len(radii_matches)}")
    return radius_matches, radii_matches

if __name__ == "__main__":
    print("=== CHECKING CITATIONS ===")
    check_citations(ARXIV_TEX, BIB_FILE)
    check_citations(REVISTA_TEX, BIB_FILE)
    
    print("\n=== CHECKING FIGURES ===")
    check_figures(ARXIV_TEX, FIG_DIR)
    check_figures(REVISTA_TEX, FIG_DIR)
    
    print("\n=== CHECKING ABSTRACTS ===")
    check_abstract(ARXIV_TEX)
    check_abstract(REVISTA_TEX)
    
    print("\n=== CHECKING RADIUS / RADII ===")
    r_arxiv, ri_arxiv = check_radius_usage(ARXIV_TEX)
    r_rev, ri_rev = check_radius_usage(REVISTA_TEX)
