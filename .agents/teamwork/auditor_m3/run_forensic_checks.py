import os
import re
import hashlib
from pathlib import Path
import pypdf

root = Path('.')
v2_dir = root / 'v2'

print('=== FORENSIC CHECK 1: SOURCE CODE ANALYSIS ===')
tex_files = ['Paper_arxiv_v2.tex', 'Paper_revista_v2.tex']
for tf in tex_files:
    p = v2_dir / tf
    content = p.read_text(encoding='utf-8')
    lines = content.splitlines()
    words = len(content.split())
    chars = len(content)
    print(f'{tf}: {len(lines)} lines, {words} words, {chars} chars')
    
    # Check for placeholder / facade patterns
    placeholders = ['TODO', 'LOREM IPSUM', 'TBD', 'PLACEHOLDER', 'DUMMY', 'UNDER CONSTRUCTION']
    found_ph = [ph for ph in placeholders if ph in content.upper()]
    print(f'  Placeholder check: {found_ph if len(found_ph) > 0 else "NONE (CLEAN)"}')
    
    # Core mathematical elements check
    theorems = re.findall(r'\\begin\{theorem\}\[(.*?)\]', content)
    print(f'  Theorems defined: {theorems}')
    
    has_inner_prod = 'Gradshteyn' in content and 'Weber' in content
    has_frame_op = 'S_w' in content and 'Gaussian convolution' in content
    has_rcf = '8.6' in content and 'Villalba2023' in content
    has_povm = 'IC-POVM' in content or 'POVM' in content
    has_ai = 'Declaration of Generative Artificial Intelligence' in content
    print(f'  Core components present: InnerProduct={has_inner_prod}, FrameOp={has_frame_op}, RCF={has_rcf}, POVM={has_povm}, AI_Decl={has_ai}')

print('\n=== FORENSIC CHECK 2: PDF COMPILATION & COMPARISON ===')
v1_arxiv = root / 'v1' / 'Paper_arxiv_v1.pdf'
v2_arxiv = v2_dir / 'Paper_arxiv_v2.pdf'
v1_revista = root / 'v1' / 'Paper_revista_v1.pdf'
v2_revista = v2_dir / 'Paper_revista_v2.pdf'

for label, p1, p2 in [('arXiv', v1_arxiv, v2_arxiv), ('Revista', v1_revista, v2_revista)]:
    r1 = pypdf.PdfReader(str(p1), strict=False)
    r2 = pypdf.PdfReader(str(p2), strict=False)
    h1 = hashlib.md5(p1.read_bytes()).hexdigest()
    h2 = hashlib.md5(p2.read_bytes()).hexdigest()
    print(f'{label} comparison:')
    print(f'  v1: {len(r1.pages)} pages, {p1.stat().st_size} bytes, MD5={h1}')
    print(f'  v2: {len(r2.pages)} pages, {p2.stat().st_size} bytes, MD5={h2}')
    print(f'  Distinct files: {h1 != h2}')
    print(f'  Page count < 100: {len(r2.pages) < 100}')

print('\n=== FORENSIC CHECK 3: CODEX MAXIMA CITATIONS ===')
bib_path = v2_dir / 'references.bib'
bib_text = bib_path.read_text(encoding='utf-8')
keys = ['Jauhiainen2026', 'Zhu2026PaperBanana', 'Haber2025']
for k in keys:
    print(f'  Key {k} in references.bib: {k in bib_text}')

for tf in tex_files:
    content = (v2_dir / tf).read_text(encoding='utf-8')
    cites_ai = all(k in content for k in keys)
    print(f'  All AI keys cited in {tf}: {cites_ai}')

for bbl_name in ['Paper_arxiv_v2.bbl', 'Paper_revista_v2.bbl']:
    bbl_text = (v2_dir / bbl_name).read_text(encoding='utf-8')
    in_bbl = all(k in bbl_text for k in ['Jauhiainen', 'PaperBanana', 'Haber'])
    print(f'  All AI authors resolved in {bbl_name}: {in_bbl}')

print('\n=== FORENSIC CHECK 4: TEST HARNESS INTEGRITY ===')
import subprocess
git_diff = subprocess.check_output(['git', 'diff', 'tests/'], text=True)
print(f'  Git diff on tests/: {len(git_diff)} chars')

print('\n=== FORENSIC CHECK 5: COMPILATION LOG VERIFICATION ===')
for log_name, pdf_name in [('Paper_arxiv_v2.log', 'Paper_arxiv_v2.pdf'), ('Paper_revista_v2.log', 'Paper_revista_v2.pdf')]:
    log_text = (v2_dir / log_name).read_text(encoding='latin1')
    match = re.search(r'Output written on ' + pdf_name + r' \((\d+) pages, (\d+) bytes\)\.', log_text)
    if match:
        pages, bytes_count = int(match.group(1)), int(match.group(2))
        actual_bytes = (v2_dir / pdf_name).stat().st_size
        print(f'{log_name}: Log says {pages} pages, {bytes_count} bytes | Actual PDF is {actual_bytes} bytes | MATCH: {bytes_count == actual_bytes}')
    else:
        print(f'{log_name}: Output pattern NOT found in log!')
