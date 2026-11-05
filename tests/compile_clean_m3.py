"""
Clean compilation harness for Milestone 3.
Compiles Paper_arxiv_v2.tex and Paper_revista_v2.tex from scratch.
"""
import os
import subprocess
import sys
from pathlib import Path

V2_DIR = Path(r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v2")

def clean_intermediates(stem):
    extensions = [".aux", ".bbl", ".blg", ".log", ".out", ".toc", ".lof", ".lot"]
    for ext in extensions:
        f = V2_DIR / (stem + ext)
        if f.exists():
            f.unlink()
            print(f"Cleaned {f.name}")

def compile_manuscript(stem):
    print(f"\n==========================================")
    print(f"COMPILING {stem} FROM SCRATCH IN FRESH SESSION")
    print(f"==========================================")
    clean_intermediates(stem)
    
    tex_file = f"{stem}.tex"
    
    # Step 1: pdflatex pass 1
    print("\n--- Pass 1: pdflatex ---")
    p1 = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_file],
        cwd=str(V2_DIR),
        capture_output=True,
        text=True
    )
    print(f"Pass 1 exit code: {p1.returncode}")
    if p1.returncode != 0:
        print("Pass 1 errors (last 30 lines):")
        print("\n".join(p1.stdout.splitlines()[-30:]))
    
    # Step 2: bibtex
    print("\n--- BibTeX ---")
    pb = subprocess.run(
        ["bibtex", stem],
        cwd=str(V2_DIR),
        capture_output=True,
        text=True
    )
    print(f"BibTeX exit code: {pb.returncode}")
    if pb.returncode != 0:
        print("BibTeX output:")
        print(pb.stdout)
        print(pb.stderr)
    else:
        print(pb.stdout)

    # Step 3: pdflatex pass 2
    print("\n--- Pass 2: pdflatex ---")
    p2 = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_file],
        cwd=str(V2_DIR),
        capture_output=True,
        text=True
    )
    print(f"Pass 2 exit code: {p2.returncode}")

    # Step 4: pdflatex pass 3 (resolve all cross-refs)
    print("\n--- Pass 3: pdflatex ---")
    p3 = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_file],
        cwd=str(V2_DIR),
        capture_output=True,
        text=True
    )
    print(f"Pass 3 exit code: {p3.returncode}")
    
    # Check log for errors and undefined references
    log_file = V2_DIR / f"{stem}.log"
    log_text = log_file.read_text(encoding="utf-8", errors="replace")
    
    fatal_errors = [line for line in log_text.splitlines() if line.startswith("! ")]
    undefined_citations = [line for line in log_text.splitlines() if "Citation" in line and "undefined" in line]
    undefined_refs = [line for line in log_text.splitlines() if "Reference" in line and "undefined" in line]
    
    print(f"\n--- Compilation Diagnostic Summary for {stem} ---")
    print(f"Fatal errors count: {len(fatal_errors)}")
    for err in fatal_errors:
        print(f"  ERROR: {err}")
    print(f"Undefined citations count: {len(undefined_citations)}")
    for c in undefined_citations:
        print(f"  UNDEF CITE: {c}")
    print(f"Undefined references count: {len(undefined_refs)}")
    for r in undefined_refs:
        print(f"  UNDEF REF: {r}")
        
    pdf_file = V2_DIR / f"{stem}.pdf"
    if pdf_file.exists():
        print(f"PDF generated successfully: {pdf_file.name} ({pdf_file.stat().st_size} bytes)")
    else:
        print(f"CRITICAL: PDF {pdf_file.name} NOT FOUND!")
        
    return {
        "stem": stem,
        "pass1_code": p1.returncode,
        "bibtex_code": pb.returncode,
        "pass2_code": p2.returncode,
        "pass3_code": p3.returncode,
        "fatal_errors": fatal_errors,
        "undefined_citations": undefined_citations,
        "undefined_refs": undefined_refs,
        "pdf_exists": pdf_file.exists(),
        "pdf_size": pdf_file.stat().st_size if pdf_file.exists() else 0
    }

if __name__ == "__main__":
    res_arxiv = compile_manuscript("Paper_arxiv_v2")
    res_revista = compile_manuscript("Paper_revista_v2")
    print("\n\n=== FINAL COMPILATION RESULTS ===")
    print(f"arXiv: Fatal Errors = {len(res_arxiv['fatal_errors'])}, Undefined Refs = {len(res_arxiv['undefined_refs'])}, Undefined Cites = {len(res_arxiv['undefined_citations'])}")
    print(f"Revista: Fatal Errors = {len(res_revista['fatal_errors'])}, Undefined Refs = {len(res_revista['undefined_refs'])}, Undefined Cites = {len(res_revista['undefined_citations'])}")
