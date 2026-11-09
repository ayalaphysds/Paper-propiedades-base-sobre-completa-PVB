import os, glob, re

patterns = [
    r'codex',
    r'máxima',
    r'worker_',
    r'reviewer_',
    r'challenger_',
    r'orchestrator',
    r'sentinel',
    r'v1\s*->\s*v2',
    r'version\s*1\s*to\s*version\s*2',
    r'iteration\s*history',
    r'multi-agent'
]

v4_files = glob.glob('v4/**/*', recursive=True)
flagged = False

for file_path in v4_files:
    if os.path.isfile(file_path) and not file_path.endswith(('.pdf', '.zip', '.pyc', '.aux', '.log', '.out')):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for p in patterns:
            matches = list(re.finditer(p, content, re.IGNORECASE))
            if matches:
                for m in matches:
                    snippet = content[max(0, m.start()-30):min(len(content), m.end()+30)].replace('\n', ' ')
                    # Allow 'intensity maxima' or 'local maxima'
                    if 'maxima' in snippet.lower() and any(ok in snippet.lower() for ok in ['intensity maxima', 'local maxima', 'radial maxima', 'annular intensity maxima']):
                        continue
                    print(f'Match for pattern "{p}" in {file_path}: ...{snippet}...')
                    flagged = True

if not flagged:
    print('ZERO forbidden artifacts found in v4/! Completely clean.')
