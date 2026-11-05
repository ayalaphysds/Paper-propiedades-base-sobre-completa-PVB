"""
PDF verification harness using pypdf for Paper_arxiv_v2.pdf and Paper_revista_v2.pdf.
"""
from pathlib import Path
import pypdf
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

V2_DIR = Path(r"c:\Users\sayal\OneDrive\Desktop\Repositorios\Paper PVB Sobrecompletos\Paper-propiedades-base-sobre-completa-PVB\v2")

def verify_pdf(pdf_name):
    pdf_path = V2_DIR / pdf_name
    print(f"\n==========================================")
    print(f"VERIFYING PDF: {pdf_name}")
    print(f"==========================================")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
    reader = pypdf.PdfReader(str(pdf_path))
    num_pages = len(reader.pages)
    print(f"Total pages: {num_pages}")
    assert num_pages > 0, "PDF has 0 pages!"
    assert num_pages < 100, f"PDF exceeds 100 pages limit! Pages: {num_pages}"
    
    total_chars = 0
    pages_with_text = 0
    page_dimensions = set()
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        chars = len(text)
        total_chars += chars
        if chars > 50:
            pages_with_text += 1
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        page_dimensions.add((round(width, 1), round(height, 1)))
        
        # Check first and last page preview
        if i == 0 or i == num_pages - 1:
            preview = text[:200].replace('\n', ' ')
            print(f"Page {i+1} preview: {preview}...")
            
    print(f"Pages with substantial text (>50 chars): {pages_with_text} / {num_pages}")
    print(f"Total extracted characters: {total_chars}")
    print(f"Page dimensions (pt): {page_dimensions}")
    assert pages_with_text == num_pages, f"Some pages appear empty or unextractable! ({pages_with_text} vs {num_pages})"
    
    # Check outline / bookmarks
    try:
        outline = reader.outline
        print(f"Document outline elements count: {len(outline) if outline else 0}")
    except Exception as e:
        print(f"Outline read note: {e}")
        
    print(f"PDF {pdf_name} VALIDATION PASSED!")
    return {
        "pdf_name": pdf_name,
        "num_pages": num_pages,
        "total_chars": total_chars,
        "pages_with_text": pages_with_text,
        "page_dimensions": list(page_dimensions)
    }

if __name__ == "__main__":
    r_arxiv = verify_pdf("Paper_arxiv_v2.pdf")
    r_revista = verify_pdf("Paper_revista_v2.pdf")
    print("\n\n=== SUMMARY OF PDF VERIFICATION ===")
    print(f"Paper_arxiv_v2.pdf: {r_arxiv['num_pages']} pages, {r_arxiv['total_chars']} chars, VALID < 100 pages")
    print(f"Paper_revista_v2.pdf: {r_revista['num_pages']} pages, {r_revista['total_chars']} chars, VALID < 100 pages")
