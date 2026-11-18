"""
Independent, Opaque-Box 5-Tier E2E Test Suite (141 Tests) for V6 Overcomplete PVB Manuscripts.

Covers:
  - Tier 1 (60 tests): Feature Coverage across Features #1-#12 (5 tests/feature).
  - Tier 2 (60 tests): Boundary, Corner Cases & Regression Guards (5 tests/feature).
  - Tier 3 (10 tests): Cross-Feature Pairwise Interactions & Traceability.
  - Tier 4 ( 6 tests): Real-World End-to-End Acceptance Scenarios (S1-S6).
  - Tier 5 ( 5 tests): White-Box Adversarial Coverage Hardening (T5_01-T5_05).

Dual-Runner Support:
  - pytest:  python -m pytest tests/test_v6_e2e.py -m tier1  (.. tier5, or -v)
  - CLI:     python tests/test_v6_e2e.py --tier 1             (.. 5, or full suite)
  - stdlib:  python -m unittest tests/test_v6_e2e.py

Design Guarantees:
  - Zero sys.argv mutation and zero V6/ file I/O at import time.
  - Zero imports from V6/ or V6/scripts/ (all math/physics oracles are first-principles).
  - Zero silent skips: missing V6/ deliverables fail via AssertionError with
    "[M1/M2/M3 Deliverable Missing] Expected <desc> at: <path>".
  - Strict read-only preservation (R4) on p3_3/main.tex, v1/-v5/, and tests/test_v5_e2e.py.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import warnings
from io import StringIO
from pathlib import Path
from typing import Any, Callable

import mpmath as mp
import numpy as np
from scipy import integrate, optimize, special

try:
    import pytest
except ImportError:  # pragma: no cover - fallback when pytest is not installed
    class _NoOpMark:
        def __getattr__(self, _name: str) -> Callable[[Any], Any]:
            def _decorator(obj: Any) -> Any:
                return obj
            return _decorator

    class _NoOpPytest:
        mark = _NoOpMark()

    pytest = _NoOpPytest()  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Authoritative Paths & R4 Baseline Constants (No file I/O at import time)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
V6_DIR = REPO_ROOT / "V6"
V6_FIGURES_DIR = V6_DIR / "figures"
V6_SCRIPTS_DIR = V6_DIR / "scripts"

P33_DIR = Path(r"c:\Users\sayal\OneDrive\Desktop\Papers\p3_3")
P33_MAIN_TEX = P33_DIR / "main.tex"
P33_EXPECTED_SHA256 = (
    "B73835B83672921DF445ADA2EAEC2757F37A19B0CD9A024B65F3AF2441B180A6"
)
P33_EXPECTED_BYTES = 39419
P33_EXPECTED_LINES = 596

PRIOR_VERSION_BASELINE: dict[str, tuple[int, int]] = {
    "v1": (39, 3248719),
    "v2": (39, 4260308),
    "v3": (40, 4762645),
    "v4": (37, 4748443),
    "v5": (43, 5788619),
}

TEST_V5_PATH = TESTS_DIR / "test_v5_e2e.py"
TEST_V5_EXPECTED_BYTES = 80050

TEAMWORK_ROOT = Path(
    r"C:\Users\sayal\.gemini\antigravity\scratch\teamwork"
    r"\d11e9fd1-5289-4f2e-b6f9-93a0f2b4d305\.agents\teamwork"
)

V6_REFEREE_1 = V6_DIR / "REFEREE_1_REPORT.md"
V6_REFEREE_2 = V6_DIR / "REFEREE_2_REPORT.md"
V6_MAPPING = V6_DIR / "RESOLUTION_MAPPING.md"
V6_BIB = V6_DIR / "references.bib"
V6_PRA_TEX = V6_DIR / "main_pra.tex"
V6_PRA_PDF = V6_DIR / "main_pra.pdf"
V6_PRA_LOG = V6_DIR / "main_pra.log"
V6_PRA_BBL = V6_DIR / "main_pra.bbl"
V6_PRA_BLG = V6_DIR / "main_pra.blg"
V6_ARXIV_TEX = V6_DIR / "main_arxiv.tex"
V6_ARXIV_PDF = V6_DIR / "main_arxiv.pdf"
V6_ARXIV_LOG = V6_DIR / "main_arxiv.log"
V6_ARXIV_BBL = V6_DIR / "main_arxiv.bbl"
V6_ARXIV_BLG = V6_DIR / "main_arxiv.blg"

V6_FIG_NAMES = (
    "fig1_frame_spectrum.pdf",
    "fig2_laguerre_regularization.pdf",
    "fig3_optics_utility.pdf",
)
V6_FIG_PATHS = [V6_FIGURES_DIR / name for name in V6_FIG_NAMES]

V6_SCRIPT_NAMES = (
    "verify_math_and_tables.py",
    "generate_figures.py",
    "run_all.py",
)

PROHIBITED_CODENAME_REGEXES = [
    r"(?i)codex[- ]?m(?:[áa´\u0301]|\\'\{?a\}?)*xima",
    r"\bexplorer_[a-z0-9_]+\b",
    r"\bworker_[a-z0-9_]+\b",
    r"\bcritic_[a-z0-9_]+\b",
    r"\bchallenger_[a-z0-9_]+\b",
    r"\breviewer_[a-z0-9_]+\b",
    r"\bauditor_[a-z0-9_]+\b",
    r"\bsub_orch[a-z0-9_]*\b",
    r"\bspec_miner[a-z0-9_]*\b",
    r"\bvictory_auditor\b",
    r"\be2e_testing_orch\b",
    r"\bteamwork_auditor\b",
    r"\bteamwork_[a-z0-9_]+\b",
    r"\bsentinel_[a-z0-9_]+\b",
]

PROHIBITED_VERSION_REGEXES = [
    r"\bp3_3\b",
    r"\btest_v[0-9]+_e2e\b",
    r"\bPaper_(?:arxiv|revista)_v[1-5]\b",
    r"\bv[1-5]/",
    r"\bV6/",
    r"\bV6\b",
    r"v1\s*(?:->|\\to|to)\s*v2",
]

PROHIBITED_INTERNAL_REGEXES = PROHIBITED_CODENAME_REGEXES + PROHIBITED_VERSION_REGEXES

PDF_UNRESOLVED_MARK_RE = re.compile(
    r"\[[^\[\]\n]{0,120}\?[^\[\]\n]{0,120}\]"
    r"|\([^()\n]{0,120}\?[^()\n]{0,120}\)"
    r"|\?\?"
    r"|(?:\s|^)\?(?=\s|[.,;:\)\]]|$)"
)


# ---------------------------------------------------------------------------
# Strict Deliverable Gate (ZERO silent skips)
# ---------------------------------------------------------------------------

def assert_v6_deliverable(
    test_case: unittest.TestCase,
    path: Path,
    milestone: str,
    description: str,
) -> Path:
    """Assert that a required V6 deliverable exists; never silently skip."""
    if not path.exists():
        test_case.fail(
            f"[{milestone} Deliverable Missing] Expected {description} at: {path}"
        )
    return path


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def strip_tex_comments(text: str) -> str:
    """Remove unescaped TeX % comments line-by-line."""
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        out: list[str] = []
        escaped = False
        for ch in line:
            if escaped:
                out.append(ch)
                escaped = False
            elif ch == "\\":
                out.append(ch)
                escaped = True
            elif ch == "%":
                break
            else:
                out.append(ch)
        cleaned_lines.append("".join(out))
    return "\n".join(cleaned_lines)


def strip_tex_math(text: str) -> str:
    """Strip display and inline math environments so prose checks avoid factorials."""
    s = strip_tex_comments(text)
    env_pattern = (
        r"\\begin\{(?:equation|align|eqnarray|multline|gather|flalign|alignat)\*?\}"
        r".*?"
        r"\\end\{(?:equation|align|eqnarray|multline|gather|flalign|alignat)\*?\}"
    )
    s = re.sub(env_pattern, " ", s, flags=re.DOTALL)
    s = re.sub(r"\$\$.*?\$\$", " ", s, flags=re.DOTALL)
    s = re.sub(r"\\\[.*?\\\]", " ", s, flags=re.DOTALL)
    s = re.sub(r"\\\(.*?\\\)", " ", s, flags=re.DOTALL)
    s = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", " ", s, flags=re.DOTALL)
    s = re.sub(r"\\(?:url|href|label|cite|ref|eqref)\{[^}]*\}", " ", s)
    return s


def extract_citations(tex_text: str) -> set[str]:
    clean = strip_tex_comments(tex_text)
    keys: set[str] = set()
    for match in re.finditer(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", clean):
        for raw_key in match.group(1).split(","):
            k = raw_key.strip()
            if k:
                keys.add(k)
    return keys


def extract_labels(tex_text: str) -> set[str]:
    clean = strip_tex_comments(tex_text)
    return set(re.findall(r"\\label\{([^}]+)\}", clean))


def extract_includegraphics_paths(tex_text: str) -> list[str]:
    clean = strip_tex_comments(tex_text)
    return re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", clean)


def extract_abstract_text(tex_text: str) -> str:
    clean = strip_tex_comments(tex_text)
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", clean, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_author_block(tex_text: str) -> str:
    clean = strip_tex_comments(tex_text)
    authors = re.findall(r"\\author(?:\[[^\]]*\])?\{([^}]*)\}", clean)
    return " ".join(authors)


def parse_bibtex_entries(bib_text: str) -> list[dict[str, Any]]:
    """Parse BibTeX entries with brace-depth awareness."""
    entries: list[dict[str, Any]] = []
    n = len(bib_text)
    i = 0
    while i < n:
        at_idx = bib_text.find("@", i)
        if at_idx == -1:
            break
        m = re.match(r"@([A-Za-z]+)\s*([{(])", bib_text[at_idx:])
        if not m:
            i = at_idx + 1
            continue
        entry_type = m.group(1).lower()
        open_ch = m.group(2)
        close_ch = "}" if open_ch == "{" else ")"
        start = at_idx + m.end()
        depth = 1
        pos = start
        while pos < n and depth > 0:
            ch = bib_text[pos]
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
            pos += 1
        body = bib_text[start : pos - 1].strip()
        i = pos
        if entry_type in {"comment", "preamble", "string"}:
            continue
        comma_idx = body.find(",")
        if comma_idx == -1:
            continue
        key = body[:comma_idx].strip()
        fields_raw = body[comma_idx + 1 :]
        fields: dict[str, str] = {}
        f_idx = 0
        fn = len(fields_raw)
        while f_idx < fn:
            while f_idx < fn and fields_raw[f_idx] in " \t\r\n,":
                f_idx += 1
            if f_idx >= fn:
                break
            fm = re.match(r"([A-Za-z0-9_-]+)\s*=\s*", fields_raw[f_idx:])
            if not fm:
                f_idx += 1
                continue
            fname = fm.group(1).lower()
            f_idx += fm.end()
            if f_idx >= fn:
                break
            if fields_raw[f_idx] == "{":
                d = 1
                v_start = f_idx + 1
                f_idx += 1
                while f_idx < fn and d > 0:
                    if fields_raw[f_idx] == "{":
                        d += 1
                    elif fields_raw[f_idx] == "}":
                        d -= 1
                    f_idx += 1
                val = fields_raw[v_start : f_idx - 1].strip()
            elif fields_raw[f_idx] == '"':
                v_start = f_idx + 1
                f_idx += 1
                while f_idx < fn:
                    if fields_raw[f_idx] == '"' and fields_raw[f_idx - 1] != "\\":
                        break
                    f_idx += 1
                val = fields_raw[v_start:f_idx].strip()
                f_idx += 1
            else:
                v_start = f_idx
                while f_idx < fn and fields_raw[f_idx] not in ",\r\n":
                    f_idx += 1
                val = fields_raw[v_start:f_idx].strip()
            fields[fname] = re.sub(r"\s+", " ", val)
        entries.append({"type": entry_type, "key": key, "fields": fields})
    return entries


def parse_bbl_keys(bbl_text: str) -> set[str]:
    return set(re.findall(r"\\bibitem\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", bbl_text))


def extract_pdf_text_pymupdf(pdf_path: Path) -> tuple[int, str, list[str]]:
    import pymupdf

    doc = pymupdf.open(str(pdf_path))
    try:
        pages_text = [page.get_text("text") or "" for page in doc]
        return len(doc), "\n".join(pages_text), pages_text
    finally:
        doc.close()


def run_pdftotext(pdf_path: Path) -> str:
    proc = subprocess.run(
        ["pdftotext", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"pdftotext failed ({proc.returncode}): {proc.stderr}")
    return proc.stdout


def run_pdfinfo(pdf_path: Path) -> dict[str, str]:
    proc = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"pdfinfo failed ({proc.returncode}): {proc.stderr}")
    info: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            info[k.strip()] = v.strip()
    return info


def parse_latex_number(cell: str) -> float | None:
    """Parse a pure LaTeX numeric cell (rejecting mixed prose/symbols like w_0 or p=0)."""
    s = cell.strip()
    if not s:
        return None
    # Iteratively unwrap common text/math formatting wrappers
    for _ in range(3):
        next_s = re.sub(
            r"\\(?:textbf|mathbf|mathrm|text|textrm|emph|num)\{([^{}]*)\}",
            r"\1",
            s,
        )
        if next_s == s:
            break
        s = next_s
    s = s.replace("$", "").replace("\\%", "").replace("%", "")
    s = re.sub(r"\\[,;!:\s]", "", s).replace("~", "").strip()
    # Strip balanced outer braces if present
    while len(s) >= 2 and s[0] == "{" and s[-1] == "}":
        s = s[1:-1].strip()
    # Remove thousands-separator commas between digits (never tuple commas)
    s = re.sub(r"(?<=\d)(?:\{,\}|,)(?=\d)", "", s).strip()
    if not s:
        return None
    sci = re.fullmatch(
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*(?:\\times|x|\*)\s*10\^\{?\s*([-+]?\d+)\s*\}?",
        s,
    )
    if sci:
        return float(sci.group(1)) * (10.0 ** int(sci.group(2)))
    plain = re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", s)
    return float(plain.group(0)) if plain else None


def _strip_tabular_header_args(block: str, env_name: str) -> str:
    """Strip \\begin{tabular[*]} plus its balanced {...} / [...] spec arguments."""
    prefix = f"\\begin{{{env_name}}}"
    pos = block.find(prefix)
    if pos == -1:
        return block
    idx = pos + len(prefix)
    n = len(block)
    req_braces = 2 if env_name == "tabular*" else 1
    seen_braces = 0
    while idx < n and seen_braces < req_braces:
        while idx < n and block[idx].isspace():
            idx += 1
        if idx >= n:
            break
        if block[idx] == "[":
            depth = 1
            idx += 1
            while idx < n and depth > 0:
                if block[idx] == "[":
                    depth += 1
                elif block[idx] == "]":
                    depth -= 1
                idx += 1
        elif block[idx] == "{":
            depth = 1
            idx += 1
            while idx < n and depth > 0:
                if block[idx] == "{":
                    depth += 1
                elif block[idx] == "}":
                    depth -= 1
                idx += 1
            seen_braces += 1
        else:
            break
    end_tok = f"\\end{{{env_name}}}"
    end_idx = block.rfind(end_tok)
    return block[idx:end_idx] if end_idx != -1 else block[idx:]


_TABULAR_ROW_SPLIT_RE = re.compile(r"\\\\\*?(?:\[[^\]]*\])?")
_TABULAR_RULE_STRIP_RE = re.compile(
    r"\\(?:hline|(?:toprule|midrule|bottomrule)(?:\[[^\]]*\])?|colrule|botrule|addlinespace(?:\[[^\]]*\])?|cline\{[^}]*\}|cmidrule(?:\[[^\]]*\])?(?:\([^)]*\))?(?:\[[^\]]*\])?\{[^}]*\})"
)


def _is_header_table_row(cleaned_row: str) -> bool:
    """Detect non-data LaTeX table header rows."""
    return bool(
        re.search(r"w\s*/\s*w_0|p\s*=\s*0|\\Delta\s*R|\\mathcal\{F\}|\\kappa\(", cleaned_row)
    )


def extract_tabular_rows_matching(
    tex_text: str, marker_predicate: Callable[[str], bool]
) -> list[list[str]]:
    clean = strip_tex_comments(tex_text)
    for m in re.finditer(
        r"\\begin\{(tabular\*?)\}.*?\\end\{\1\}", clean, flags=re.DOTALL
    ):
        block = m.group(0)
        if marker_predicate(block):
            inner = _strip_tabular_header_args(block, m.group(1))
            rows: list[list[str]] = []
            for raw_row in _TABULAR_ROW_SPLIT_RE.split(inner):
                if "&" not in raw_row:
                    continue
                cleaned_row = _TABULAR_RULE_STRIP_RE.sub("", raw_row).strip()
                if _is_header_table_row(cleaned_row):
                    continue
                cells = [c.strip() for c in cleaned_row.split("&")]
                if any(parse_latex_number(c) is not None for c in cells):
                    rows.append(cells)
            return rows
    return []


def _is_table2_block(block: str) -> bool:
    return bool(
        re.search(r"1\.64[45]", block)
        and re.search(r"\b2\.50?\b", block)
        and re.search(r"\b3\.00?\b", block)
    )


def classify_pdf_layout(pdf_path: Path) -> tuple[int, int, int]:
    """Return (paired_twocol_pages, wide_body_pages, total_pages) across all PDF pages."""
    import pymupdf

    def _is_col_prose(blk: tuple[Any, ...]) -> bool:
        txt = str(blk[4]).strip()
        if len(txt) < 40:
            return False
        lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        alpha_words = sum(1 for w in txt.split() if sum(c.isalpha() for c in w) >= 2)
        return len(lines) >= 2 and alpha_words >= 8

    doc = pymupdf.open(str(pdf_path))
    try:
        paired_pages = 0
        wide_body_pages = 0
        body_start = 1 if len(doc) > 1 else 0
        for idx, page in enumerate(doc):
            pw = page.rect.width
            blocks = [b for b in page.get_text("blocks") if b[6] == 0]
            if idx >= body_start and any(
                (b[2] - b[0]) > 0.55 * pw and len(str(b[4]).strip()) >= 60
                for b in blocks
            ):
                wide_body_pages += 1
            lefts = [
                b for b in blocks
                if (b[2] - b[0]) < 0.48 * pw and b[2] < 0.52 * pw and _is_col_prose(b)
            ]
            rights = [
                b for b in blocks
                if (b[2] - b[0]) < 0.48 * pw and b[0] > 0.48 * pw and _is_col_prose(b)
            ]
            if any(
                min(lb[3], rb[3]) - max(lb[1], rb[1]) > 10.0
                for lb in lefts
                for rb in rights
            ):
                paired_pages += 1
        return paired_pages, wide_body_pages, len(doc)
    finally:
        doc.close()


def extract_referee_ids(report_text: str, prefix: str) -> set[str]:
    if prefix == "R1":
        return set(re.findall(r"\bR1-[A-Za-z0-9_]+\b", report_text))
    return set(re.findall(r"\bR2-[A-Za-z0-9_]+\b", report_text))


def _split_markdown_row(line: str) -> list[str]:
    """Split a Markdown table row on '|' outside inline $...$, `...`, and escaped \\|."""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    cells: list[str] = []
    cur: list[str] = []
    in_math = False
    in_code = False
    i = 0
    n = len(inner)
    while i < n:
        ch = inner[i]
        if ch == "\\" and i + 1 < n:
            cur.append(ch)
            cur.append(inner[i + 1])
            i += 2
            continue
        if ch == "`" and not in_math:
            in_code = not in_code
            cur.append(ch)
        elif ch == "$" and not in_code:
            in_math = not in_math
            cur.append(ch)
        elif ch == "|" and not in_math and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def _verify_scripts_numerical_outputs(
    test_case: unittest.TestCase,
    scripts_dir: Path,
    tmp_v6: Path,
    stdout: str,
) -> None:
    """Validate V6/scripts source formulas and run_all.py stdout/JSON against oracles."""
    for pyf in sorted(scripts_dir.glob("*.py")):
        src_no_comments = re.sub(r"#[^\n]*", "", read_utf8(pyf))
        test_case.assertNotRegex(
            src_no_comments,
            r"0\.2\s*/\s*(?:np\.|math\.)?sqrt\s*\(",
            f"Erroneous 0.2/sqrt(p) Rayleigh formula in {pyf.name}",
        )
        if pyf.name == "generate_figures.py":
            test_case.assertRegex(
                src_no_comments,
                r"\b(?:ive|eval_genlaguerre|eigvalsh|eigh|quad)\b",
                "generate_figures.py must compute curves from first-principles functions",
            )
            test_case.assertNotRegex(
                src_no_comments,
                r"0\.57033\s*\*",
                "Surrogate 0.57033 curve detected in generate_figures.py",
            )

    test_case.assertGreater(len(stdout.strip()), 50, "run_all.py produced empty stdout")
    for line in stdout.splitlines():
        if "0.57033" in line and not re.search(
            r"0\.5625|p3_3|old|err|bug|legacy|wrong|contrast|delta|diff|\bvs\b", line, re.I
        ):
            test_case.fail(f"run_all.py stdout reported erroneous 0.57033: {line}")
        if re.search(r"\b4\.10\b|\b4\.65\b", line) and not re.search(
            r"1\.17|1\.04|kappa\(G\)|kappa_G|unnorm|p3_3|contrast|\bvs\b", line, re.I
        ):
            test_case.fail(f"run_all.py stdout reported unnormalized Table II kappa: {line}")

    metrics_candidates = [
        tmp_v6 / "scripts" / "verified_metrics.json",
        tmp_v6 / "verified_metrics.json",
    ]
    combined_report = stdout
    for mp in metrics_candidates:
        if mp.exists():
            raw_json = read_utf8(mp)
            json.loads(raw_json)
            combined_report += "\n" + raw_json
    test_case.assertRegex(
        combined_report,
        r"0\.5625|9/16",
        "run_all.py / verified_metrics.json must report exact 0.5625 Table I fidelity",
    )
    test_case.assertRegex(
        combined_report,
        r"1\.64[45]",
        "run_all.py / verified_metrics.json must report normalized Table II kappa(gamma)~1.645",
    )


def _assert_no_positive_distortionless_alpha(
    test_case: unittest.TestCase, tex_text: str, label: str
) -> None:
    """Ban positive 'distortion-free' / 'distortionless' / 'without distortion' claims for alpha > 0 or dual modes."""
    alpha_sym = r"\\alpha(?:_\{?(?:\\text|\\mathrm|\\textrm|\\operatorname)\{reg\}\}?)?"
    alpha_zero_re = rf"{alpha_sym}\s*=\s*0(?!(?:\.\d|\d))"
    alpha_pos_re = (
        rf"{alpha_sym}\s*>\s*0|0\s*<\s*{alpha_sym}"
        r"|\\(?:wide)?tilde\{\\Phi\}_\{?l,\s*R\}?\^\{\(?\\alpha"
    )
    reg_ctx_re = (
        r"(?i)\\alpha|tikhonov|(?<!un-)(?<!non-)\bregulariz"
        r"|dual\s+frame|S_\{?w,\s*\\alpha\}?|\\(?:wide)?tilde\{\\Phi\}"
    )
    unreg_dual_re = re.compile(r"(?i)\b(?:un-?|non-?)regularized\s+dual\s+frames?\b")
    comma_pad = r"(?:(?<!\\)\$|\\[,!;:\s]|\s){0,8},(?:(?<!\\)\$|\\[,!;:\s]|\s){0,8}"
    sent_sep = (
        r"(?:\n\s*\n|;"
        r"|(?<!\bEq)(?<!\bEqs)(?<!\bFig)(?<!\bFigs)(?<!\bSec)(?<!\bSecs)"
        r"(?<!\bRef)(?<!\bRefs)(?<!\bTab)(?<!\bApp)(?<!\bal)(?<!\bi\.e)(?<!\be\.g)"
        r"(?<!\bcf)(?<!\bvs)\.(?=\s|$|[)\]\"'$]))"
    )
    right_contrast_sep = (
        rf"(?:{comma_pad}(?:unlike|rather\s+than|instead\s+of|as\s+opposed\s+to|in\s+contrast\s+to"
        rf"|whereas|while|although|though|but|however|yet|not)\b"
        rf"|\b(?:unlike|rather\s+than|instead\s+of|as\s+opposed\s+to|in\s+contrast\s+to"
        rf"|whereas|while|although|though|but|however)\b)"
    )
    left_contrast_sep = (
        rf"(?:{comma_pad}(?:whereas|while|although|though|however|but|yet|conversely|in\s+contrast\b(?!\s+to\b))\b"
        rf"|\b(?:however|but|yet|conversely|in\s+contrast\b(?!\s+to\b))\b)"
    )
    brace_atom = r"\{(?:[^{}]|\{[^{}]*\})*\}"
    opening_concessive_re = re.compile(
        rf"^\s*(?:whereas|while|although|though|unlike|in\s+contrast\s+to"
        rf"|as\s+opposed\s+to|rather\s+than|instead\s+of)\b(?:{brace_atom}|[^,{{}}])*?{comma_pad}(.*)$",
        flags=re.I | re.DOTALL,
    )
    paren_atom = r"\((?:[^()\n]|\([^()\n]*\))*\)"
    mid_contrast_re = re.compile(
        rf"{comma_pad}(?:unlike|as\s+opposed\s+to|rather\s+than|instead\s+of|in\s+contrast\s+to)\b"
        rf"(?:{brace_atom}|{paren_atom}|[^,.;{{}}()])+?(?={comma_pad})",
        flags=re.I | re.DOTALL,
    )
    which_paren_adv = (
        r"(?:,\s*(?:in\s+turn|however|therefore|moreover|indeed|consequently"
        r"|by\s+contrast|in\s+fact|of\s+course|as\s+a\s+result)\s*,)?"
    )
    mid_contrast_which_re = re.compile(
        rf"{comma_pad}(?:unlike|as\s+opposed\s+to|rather\s+than|instead\s+of|in\s+contrast\s+to)\b"
        rf"((?:{brace_atom}|{paren_atom}|[^,.;{{}}()])+?){comma_pad}"
        rf"(which\b{which_paren_adv}(?:{brace_atom}|{paren_atom}|[^,.;{{}}()])*)$",
        flags=re.I | re.DOTALL,
    )
    left_math_alpha = (
        rf"(?:{alpha_sym}[^$\n]{{0,60}}?\$\s*\)?"
        rf"|{alpha_sym}(?:[^$\n\\]|\\(?!\))){{0,60}}?\\\)\s*\)?)"
    )
    right_math_alpha = (
        r"(?:\$[^$\n]{0,60}?\\alpha[^$\n]{0,60}?\$"
        r"|\\\((?:[^$\n\\]|\\(?!\))){0,60}?\\alpha(?:[^$\n\\]|\\(?!\))){0,60}?\\\))"
    )
    uncommad_alpha_contrast_re = re.compile(
        rf"({left_math_alpha})\s+(?:rather\s+than|instead\s+of)\s+"
        rf"(?:(?:(?:at|for|with|when|in)\s+)?\(?\s*{right_math_alpha}\s*\)?"
        rf"|(?:(?:at|for|with|when|in)\s+)?the\s+\(?\s*{right_math_alpha}\s*\)?\s+(?:case|limit|regime|setting)\b)",
        flags=re.I,
    )
    paren_contrast_re = re.compile(
        r"\((?:unlike|as\s+opposed\s+to|rather\s+than|instead\s+of|in\s+contrast\s+to)\b(?:[^()]|\([^()]*\)){1,240}\)",
        flags=re.I | re.DOTALL,
    )
    subclause_sep = rf"{comma_pad}(?:which|and|so|not|yielding|giving|providing|whereby|thereby)\b"
    comp_alpha0_prefix_re = re.compile(
        r"(?:unlike|like|as\s+\w+\s+as|not\s+\w+\s+like|compared\s+(?:to|with)|versus|vs\.?|rather\s+than|instead\s+of|than)\b[^,;.]*$",
        flags=re.I,
    )
    neg_re = re.compile(
        r"(?:\b(?:not|never|cannot|neither|nor|rather\s+than|instead\s+of|fails?\s+to|unable\s+to|impossible\s+to)\b"
        r"|(?<!with\s)\bno\b(?:\s*$|\s+(?:exact|distortion|recovery|reconstruction|perfect|complete|accurate|faithful|true|lossless)\b"
        r"|\s+(?:(?:\$[^$\n]{1,64}\$|\\\([^)\n]{1,64}\\\)|[\w-]+)\s+){0,2}(?:operator|frame|filter|dual|scheme|method|inversion)\b)"
        r"|\b(?:prevents?|precludes?|prohibits?)\s+(?:(?:any|all|exact|perfect|complete|full|true|faithful|lossless|field|signal|optical|mode|image|direct)\s*,?\s*){0,3}(?:recovery|reconstruction|inversion|restoration)?\s*$)",
        flags=re.I,
    )
    no_neg_tok = r"(?:(?!(?:not|never|cannot|can|neither|nor|no|hardly|scarcely|seldom|rarely|without)\b)\w+\s+)"
    right_neg_re = re.compile(
        rf"^\s*{no_neg_tok}{{0,3}}(?:is|are|remains?|becomes?)\s+(?:impossible|unattainable|unachievable|infeasible|precluded)\b"
        rf"|^\s*{no_neg_tok}{{0,3}}(?:is|are|remains?|becomes?)\s+(?:not|never)\s+(?:possible|feasible|achievable|attainable|realizable|exact|valid|preserved|maintained|guaranteed|achieved|attained|obtained|recovered|reconstructed)\b"
        rf"|^\s*{no_neg_tok}{{0,2}}(?:fails?\s*(?:$|[,.;]|to\s+(?:hold|occur|apply|exist|obtain|persist|succeed|yield|provide|preserve|reconstruct|recover)\b)"
        r"|(?:cannot|can\s+not)\s+(?:be\s+)?(?:achieved|attained|obtained|realized|preserved|maintained|guaranteed|recovered|reconstructed|hold|occur|apply|exist|succeed)\b"
        r"|(?:does|do)\s+not\s+(?:hold|occur|apply|exist|obtain|persist|succeed|yield|provide|preserve|reconstruct|recover)\b)",
        flags=re.I,
    )
    coord_np_tok = (
        r"(?:(?!(?:not|never|no|neither|nor|none|nothing|cannot|without|hardly|scarcely|seldom|rarely)\b)"
        r"(?:\(?\$[^$\n]{1,64}\$\)?(?:-[\w-]+)?|\(?\\\([^)\n]{1,64}\\\)\)?(?:-[\w-]+)?|[\w-]+)\s+)"
    )
    coord_finite_verb_re = re.compile(
        r"\band\s+(?:(?:thus|therefore|hence|still|then|accordingly|consequently)\s+)?"
        rf"{coord_np_tok}{{0,5}}"
        r"(?=(?:reconstructs|recovers|yields|provides|achieves|restores|gives|produces|delivers"
        r"|ensures|preserves|maintains|reproduces|attains|obtains|retains|offers|remains|is|are)\b)",
        flags=re.I,
    )

    def _has_active_alpha_zero(text: str) -> bool:
        for mz in re.finditer(alpha_zero_re, text):
            pre = text[max(0, mz.start() - 60) : mz.start()]
            pre_seg = re.split(r"[;.]|\$(?:[^$]*)\$,\s*|,\s*", pre)[-1]
            if not comp_alpha0_prefix_re.search(pre_seg):
                return True
        return False

    for m in re.finditer(
        r"(?i)(?:without\s+distortion|free\s+of\s+distortion|\b(?:zero|no)\s+distortion(?!(?:-{1,2}|\u2013|\s+)?(?:free|less)\b)|distortion(?:-{1,2}|\u2013|\s+)?(?:free|less))",
        tex_text,
    ):
        raw_left = tex_text[max(0, m.start() - 320) : m.start()]
        raw_right = tex_text[m.end() : min(len(tex_text), m.end() + 320)]

        sent_left = re.split(sent_sep, raw_left, flags=re.I)[-1]
        sent_right = re.split(sent_sep, raw_right, flags=re.I)[0]
        left_s = re.split(left_contrast_sep, sent_left, flags=re.I)[-1]
        right_s = re.split(right_contrast_sep, sent_right, flags=re.I)[0]

        m_open = opening_concessive_re.match(left_s)
        if m_open:
            main_left = m_open.group(1)
            main_candidate = main_left + m.group(0) + right_s
            if (
                re.search(reg_ctx_re, unreg_dual_re.sub("", main_candidate))
                or _has_active_alpha_zero(main_candidate)
                or unreg_dual_re.search(main_candidate)
            ):
                left_s = main_left

        if "which" in left_s.lower():
            m_mcw = mid_contrast_which_re.search(left_s)
            if m_mcw:
                left_s = m_mcw.group(1) + ", " + m_mcw.group(2)
        left_s = mid_contrast_re.sub("", left_s)
        left_s = paren_contrast_re.sub("", left_s)
        left_s = uncommad_alpha_contrast_re.sub(r"\1", left_s)

        left_parts = re.split(rf"({subclause_sep})", left_s, flags=re.I)
        active_left = coord_finite_verb_re.split(left_parts[-1])[-1]
        if neg_re.search(active_left):
            continue
        right_head = re.split(rf"{subclause_sep}|,|\band\b", right_s, maxsplit=1, flags=re.I)[0]
        if right_neg_re.search(right_head):
            continue

        chosen_left = left_s
        clause = left_s + m.group(0) + right_s
        if len(left_parts) > 1:
            for idx in range(len(left_parts) - 1, -1, -2):
                cand_left = "".join(left_parts[idx:])
                cand_clause = cand_left + m.group(0) + right_s
                if re.search(alpha_pos_re, cand_clause):
                    break
                if _has_active_alpha_zero(cand_clause):
                    chosen_left = cand_left
                    clause = cand_clause
                    break
                if idx >= 2 and re.search(reg_ctx_re, unreg_dual_re.sub("", cand_clause)):
                    if re.search(r"\b(?:and|so|not)\b", left_parts[idx - 1], flags=re.I):
                        chosen_left = cand_left
                        clause = cand_clause
                        break

        right_parts = re.split(rf"({subclause_sep})", right_s, flags=re.I)
        if len(right_parts) > 1:
            tail = "".join(right_parts[2:])
            if not re.match(
                r"^\s*(?:this\s+(?:also\s+)?holds|the\s+same\s+holds|similarly|likewise)\b",
                tail,
                flags=re.I,
            ):
                trimmed = chosen_left + m.group(0) + right_parts[0]
                if _has_active_alpha_zero(trimmed) and not re.search(alpha_pos_re, trimmed):
                    clause = trimmed

        if not re.search(reg_ctx_re, unreg_dual_re.sub("", clause)):
            continue
        has_alpha_zero = _has_active_alpha_zero(clause)
        has_alpha_pos = bool(re.search(alpha_pos_re, clause))
        if has_alpha_pos or not has_alpha_zero:
            test_case.fail(
                f"Forbidden distortion-free claim for regularized/alpha>0 frame in {label}: {clause.strip()[:160]}"
            )


def _extract_comparative_table_rows(tex_text: str) -> list[list[str]]:
    clean = strip_tex_comments(tex_text)
    for m in re.finditer(
        r"\\begin\{(tabular\*?)\}.*?\\end\{\1\}", clean, flags=re.DOTALL
    ):
        block = m.group(0)
        if "dirac" in block.lower() and "coherent" in block.lower():
            inner = _strip_tabular_header_args(block, m.group(1))
            rows: list[list[str]] = []
            for raw_row in _TABULAR_ROW_SPLIT_RE.split(inner):
                if "&" not in raw_row:
                    continue
                cleaned_row = _TABULAR_RULE_STRIP_RE.sub("", raw_row).strip()
                cells = [re.sub(r"\s+", " ", c.strip()) for c in cleaned_row.split("&")]
                if any(cells):
                    rows.append(cells)
            return rows
    return []


def parse_markdown_mapping_rows(mapping_text: str) -> tuple[list[str], list[list[str]]]:
    headers: list[str] = []
    rows: list[list[str]] = []
    for line in mapping_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = _split_markdown_row(stripped)
        if any(bool(c.strip()) for c in cells) and all(
            re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c
        ):
            continue
        if not headers and any("Finding ID" in c for c in cells):
            headers = cells
        elif headers:
            if cells:
                cells[0] = cells[0].strip("`").strip()
            rows.append(cells)
    return headers, rows


def check_r4_baseline_details() -> tuple[str, int, int, int, dict[str, tuple[int, int]]]:
    if not P33_MAIN_TEX.exists():
        raise AssertionError(f"Missing R4 baseline file: {P33_MAIN_TEX}")
    p33_files = list(P33_DIR.iterdir())
    raw = P33_MAIN_TEX.read_bytes()
    sha = hashlib.sha256(raw).hexdigest().upper()
    line_count = len(raw.decode("utf-8").splitlines())

    folder_stats: dict[str, tuple[int, int]] = {}
    for folder in PRIOR_VERSION_BASELINE:
        fpath = REPO_ROOT / folder
        if not fpath.exists():
            raise AssertionError(f"Missing prior version folder: {fpath}")
        files = [p for p in fpath.rglob("*") if p.is_file()]
        folder_stats[folder] = (len(files), sum(p.stat().st_size for p in files))
    return sha, len(raw), line_count, len(p33_files), folder_stats


# ---------------------------------------------------------------------------
# Independent First-Principles Mathematical & Physics Oracles (Zero V6 imports)
# ---------------------------------------------------------------------------

def _oracle_safe_ive(abs_l: int, x: float | np.ndarray) -> float | np.ndarray:
    """Evaluate exp(-x)*I_{|l|}(x), switching to 3-term Hankel asymptotic above 5e8 to avoid SciPy's 2^30 ive NaN cliff."""
    x_arr = np.asarray(x, dtype=float)
    huge = x_arr > 5.0e8
    if not np.any(huge):
        res = special.ive(abs_l, x_arr)
        return float(res) if np.ndim(x) == 0 else res
    out = np.empty_like(x_arr, dtype=float)
    reg = ~huge
    if np.any(reg):
        out[reg] = special.ive(abs_l, x_arr[reg])
    if np.any(huge):
        xh = x_arr[huge]
        inv_x = 1.0 / xh
        mu = 4.0 * (abs_l ** 2)
        t1 = (mu - 1.0) * (0.125 * inv_x)
        t2 = (mu - 1.0) * (mu - 9.0) * ((inv_x * inv_x) / 128.0)
        out[huge] = (1.0 / math.sqrt(2.0 * math.pi)) * np.sqrt(inv_x) * (1.0 - t1 + t2)
    return float(out) if np.ndim(x) == 0 else out


def oracle_pvb_radial(r: float | np.ndarray, R: float, w: float, l: int) -> float | np.ndarray:
    """Physical PVB radial profile Phi_{l,R}(r) using exponentially scaled ive."""
    r_arr = np.asarray(r, dtype=float)
    val = np.zeros_like(r_arr, dtype=float)
    if not (math.isfinite(R) and math.isfinite(w) and w > 0.0):
        return float(val) if np.ndim(r) == 0 else val
    al = abs(l)
    fin = np.isfinite(r_arr)
    half_diff = np.empty_like(r_arr, dtype=float)
    half_diff[fin] = np.abs(0.5 * r_arr[fin] - 0.5 * R)
    active = fin & (half_diff < 14.0 * w)
    if np.any(active):
        ra = r_arr[active]
        d2 = ((ra - R) / w) ** 2
        res_a = np.zeros_like(ra, dtype=float)
        both_pos = (R > 0.0) & (ra > 0.0)
        if np.any(both_pos):
            rp = ra[both_pos]
            log_arg = math.log(2.0) + math.log(R) + np.log(rp) - 2.0 * math.log(w)
            huge_arg = log_arg > 690.0
            sub = np.empty_like(rp, dtype=float)
            if np.any(huge_arg):
                sub[huge_arg] = np.exp(
                    -d2[both_pos][huge_arg]
                    - 0.5 * math.log(2.0)
                    - math.log(math.pi)
                    - math.log(w)
                    - 0.5 * (math.log(R) + np.log(rp[huge_arg]))
                )
            reg_arg = ~huge_arg
            if np.any(reg_arg):
                c0 = (1.0 / (w * w)) * math.sqrt(2.0 / math.pi)
                sub[reg_arg] = (
                    c0
                    * np.exp(-d2[both_pos][reg_arg])
                    * _oracle_safe_ive(al, np.exp(log_arg[reg_arg]))
                )
            res_a[both_pos] = sub
        non_pos = ~both_pos
        if np.any(non_pos):
            rn = ra[non_pos]
            c0 = (1.0 / (w * w)) * math.sqrt(2.0 / math.pi)
            arg_n = np.where((R == 0.0) | (rn == 0.0), 0.0, 2.0 * (R / w) * (rn / w))
            res_a[non_pos] = c0 * np.exp(-d2[non_pos]) * _oracle_safe_ive(al, arg_n)
        val[active] = res_a
    return float(val) if np.ndim(r) == 0 else val


def oracle_pvb_self_overlap(R: float, w: float, l: int) -> float:
    """Unnormalized ||Phi_{l,R}||^2 = G_{RR} = (1/w^2) exp(-R^2/w^2) I_{|l|}(R^2/w^2)."""
    if not (math.isfinite(R) and math.isfinite(w) and w > 0.0):
        return 0.0
    if R == 0.0:
        return (1.0 / (w * w)) if l == 0 else 0.0
    log_x = 2.0 * (math.log(abs(R)) - math.log(w))
    if log_x > 690.0:
        return math.exp(-math.log(w) - 0.5 * math.log(2.0 * math.pi) - math.log(abs(R)))
    x = math.exp(log_x)
    return (1.0 / (w * w)) * float(_oracle_safe_ive(abs(l), x))


def oracle_lg_radial(r: float | np.ndarray, p: int, l: int, w0: float) -> float | np.ndarray:
    """Normalized Laguerre-Gaussian radial mode psi_{p,l}^{rad}(r)."""
    r_arr = np.asarray(r, dtype=float)
    val = np.zeros_like(r_arr, dtype=float)
    if not (math.isfinite(w0) and w0 > 0.0):
        return float(val) if np.ndim(r) == 0 else val
    al = abs(l)
    log_norm = 0.5 * math.log(2.0 / math.pi) - math.log(w0) + 0.5 * float(special.gammaln(p + 1) - special.gammaln(p + al + 1))
    cutoff = max(28.0, math.sqrt(800.0 + 10.0 * (2 * p + al)))
    active = np.isfinite(r_arr) & ((np.abs(r_arr) / w0) < cutoff)
    if np.any(active):
        ra = r_arr[active]
        rw = ra / w0
        u = 2.0 * (rw ** 2)
        lag = special.eval_genlaguerre(p, al, u)
        if al == 0:
            log_env = log_norm - 0.5 * u
            ok = log_env > -745.0
            env = np.zeros_like(rw, dtype=float)
            env[ok] = np.exp(log_env[ok])
        else:
            env = np.zeros_like(rw, dtype=float)
            nz = rw != 0.0
            if np.any(nz):
                rwn = rw[nz]
                sign = np.where((rwn < 0.0) & (al % 2 == 1), -1.0, 1.0)
                log_env = log_norm + al * (0.5 * math.log(2.0) + np.log(np.abs(rwn))) - 0.5 * u[nz]
                ok = log_env > -745.0
                sub = np.zeros_like(rwn, dtype=float)
                sub[ok] = sign[ok] * np.exp(log_env[ok])
                env[nz] = sub
        val[active] = env * lag
    return float(val) if np.ndim(r) == 0 else val


def oracle_c_lp_closed(p: int, l: int, R: float, w: float, w0: float) -> float:
    """Closed-form continuous PVB expansion coefficient c_{l,p}(R) for p >= 0."""
    if not (math.isfinite(R) and math.isfinite(w) and math.isfinite(w0) and w > 0.0 and w0 > 0.0):
        return 0.0
    al = abs(l)
    if R == 0.0 and al > 0:
        return 0.0
    scale = math.hypot(w0, w)
    tail_lim = (40.0 + 4.0 * math.sqrt(float(p + 1))) * scale
    if abs(R) >= tail_lim:
        return 0.0
    if p > 4:
        dps = max(60, 2 * p + 30)
        with mp.workdps(dps):
            R_m = mp.mpf(R)
            w_m = mp.mpf(w)
            w0_m = mp.mpf(w0)
            denom_w = (w0_m ** 2) + (w_m ** 2)
            norm_m = mp.mpf(2) * mp.sqrt(mp.factorial(p) / mp.factorial(p + al)) * mp.power(2, mp.mpf(al) / 2)
            eta_m = (2 * (w_m ** 2)) / denom_w
            pref_m = (
                norm_m
                * (R_m ** al)
                * (w0_m ** (al + 1))
                / (denom_w ** (al + 1))
                * mp.exp(-(R_m ** 2) / denom_w)
            )
            z_m = ((R_m ** 2) * (w0_m ** 2)) / ((w_m ** 2) * denom_w)
            L_prev = mp.mpf(1)
            total_m = mp.binomial(p + al, p) * L_prev
            if p >= 1:
                L_curr = mp.mpf(1 + al) + z_m
                total_m -= mp.binomial(p + al, p - 1) * eta_m * L_curr
                eta_pow = eta_m
                for m in range(2, p + 1):
                    L_next = ((2 * m - 1 + al + z_m) * L_curr - (m - 1 + al) * L_prev) / m
                    L_prev, L_curr = L_curr, L_next
                    eta_pow *= eta_m
                    if m % 2 == 1:
                        total_m -= mp.binomial(p + al, p - m) * eta_pow * L_curr
                    else:
                        total_m += mp.binomial(p + al, p - m) * eta_pow * L_curr
            return float(pref_m * total_m)
    r_s = R / scale
    w0_s = w0 / scale
    w_s = w / scale
    eta = 2.0 * (w_s * w_s)
    xi = 2.0 * ((r_s * w0_s) ** 2)
    log_norm = math.log(2.0) + 0.5 * float(special.gammaln(p + 1) - special.gammaln(p + al + 1)) + math.log(w0_s) - math.log(scale)
    if al == 0:
        log_p = log_norm - (r_s * r_s)
        pref = math.exp(log_p) if log_p > -745.0 else 0.0
    else:
        sign = -1.0 if (R < 0.0 and al % 2 == 1) else 1.0
        log_p = log_norm + al * (0.5 * math.log(2.0) + math.log(w0_s) + math.log(abs(r_s))) - (r_s * r_s)
        pref = sign * math.exp(log_p) if log_p > -745.0 else 0.0
    total = 0.0
    for m in range(p + 1):
        binom_outer = math.comb(p + al, p - m)
        inner = 0.0
        for j in range(m + 1):
            inner += math.comb(m + al, m - j) * (eta ** (m - j)) * (xi ** j) / math.factorial(j)
        total += ((-1) ** m) * binom_outer * inner
    return pref * total


def oracle_c_lp_quad(p: int, l: int, R: float, w: float, w0: float) -> float:
    """Direct 1D radial numerical quadrature of 2*pi * int r Phi_{l,R}(r) psi_{p,l}(r) dr in scale-adaptive coordinates."""
    if not (math.isfinite(R) and math.isfinite(w) and math.isfinite(w0) and w > 0.0 and w0 > 0.0):
        return 0.0
    al = abs(l)
    cutoff_w0 = max(28.0, math.sqrt(800.0 + 10.0 * (2 * p + al)))
    if R >= 0.0 and (R - 30.0 * w) >= cutoff_w0 * w0:
        return 0.0

    def _ive_val(r_val: float) -> float:
        if R > 0.0:
            log_arg = math.log(2.0) + math.log(R) + math.log(r_val) - 2.0 * math.log(w)
            if log_arg > 690.0:
                return math.exp(-0.5 * (math.log(2.0 * math.pi) + log_arg))
            if log_arg < -745.0:
                return 0.0
            return float(_oracle_safe_ive(al, math.exp(log_arg)))
        if R == 0.0:
            return 1.0 if al == 0 else 0.0
        return float(_oracle_safe_ive(al, 2.0 * (R / w) * (r_val / w)))

    if w > 2.0 * w0:
        s_lo = max(0.0, (R - 30.0 * w) / w0)
        s_hi = min(cutoff_w0, (R + 30.0 * w) / w0)
        if s_hi <= s_lo:
            return 0.0
        pref_s = 2.0 * math.pi * (math.sqrt(2.0 / math.pi) / w) * (w0 / w)

        def _integrand_s(s: float) -> float:
            r_val = w0 * s
            if r_val <= 0.0:
                return 0.0
            u = (r_val - R) / w
            return pref_s * r_val * math.exp(-u * u) * _ive_val(r_val) * float(oracle_lg_radial(r_val, p, l, w0))

        lg_scale = math.sqrt(float(2 * p + al + 1))
        cands = (
            0.25,
            0.5,
            1.0,
            2.0,
            4.0,
            8.0,
            14.0,
            22.0,
            0.5 * lg_scale,
            lg_scale,
            1.5 * lg_scale,
            R / w0,
            (R - w) / w0,
            (R + w) / w0,
        )
        pts = sorted({float(pt) for pt in cands if s_lo < pt < s_hi})
        bounds = [s_lo, *pts, s_hi]
        samples = [abs(_integrand_s(pt)) for pt in bounds]
        samples.extend(abs(_integrand_s(0.5 * (a + b))) for a, b in zip(bounds[:-1], bounds[1:]))
        max_s = max(samples) if samples else 0.0
        if max_s == 0.0:
            return 0.0
        eps_a = max(1e-300, 1e-14 * max_s * (s_hi - s_lo))
        total = 0.0
        for s0, s1 in zip(bounds[:-1], bounds[1:]):
            val, _ = integrate.quad(_integrand_s, s0, s1, epsabs=eps_a, epsrel=1e-13, limit=250)
            total += float(val)
        return float(total)

    r_upper = max(R + 14.0 * w, 10.0 * w0 * math.sqrt(2 * p + al + 1))
    u_lo = max(-30.0, -R / w)
    u_hi = min(30.0, (r_upper - R) / w)
    if u_hi <= u_lo:
        return 0.0
    pref = 2.0 * math.pi * (math.sqrt(2.0 / math.pi) / w)

    def _integrand_u(u: float) -> float:
        r_val = R + w * u
        if r_val <= 0.0:
            return 0.0
        return pref * r_val * math.exp(-u * u) * _ive_val(r_val) * float(oracle_lg_radial(r_val, p, l, w0))

    candidates = (-14.0, -4.0, -1.0, 0.0, 1.0, 4.0, 14.0)
    pts = sorted({float(pt) for pt in candidates if u_lo < pt < u_hi})
    bounds = [u_lo, *pts, u_hi]
    samples = [abs(_integrand_u(pt)) for pt in bounds]
    samples.extend(abs(_integrand_u(0.5 * (a + b))) for a, b in zip(bounds[:-1], bounds[1:]))
    max_u = max(samples) if samples else 0.0
    eps_a = max(1e-300, 1e-14 * max_u * (u_hi - u_lo)) if max_u > 0.0 else 1e-14
    total = 0.0
    for u0, u1 in zip(bounds[:-1], bounds[1:]):
        val, _ = integrate.quad(_integrand_u, u0, u1, epsabs=eps_a, epsrel=1e-13, limit=250)
        total += float(val)
    return float(total)


def oracle_frame_synthesis_radial(r: float, p: int, l: int, w: float, w0: float) -> float:
    """Compute (S_w psi_{p,l})^{rad}(r) = int_0^inf R dR c_{l,p}(R) Phi_{l,R}(r)."""
    if not (math.isfinite(r) and math.isfinite(w) and math.isfinite(w0) and w > 0.0 and w0 > 0.0):
        return 0.0
    u_lo = max(-14.0, -r / w)
    u_hi = 14.0
    if u_hi <= u_lo:
        return 0.0

    def _integ_u(u: float) -> float:
        R_val = r + w * u
        if R_val <= 0.0:
            return 0.0
        return w * R_val * oracle_c_lp_closed(p, l, R_val, w, w0) * float(oracle_pvb_radial(r, R_val, w, l))

    pts = sorted({float(pt) for pt in (-4.0, -1.0, 0.0, 1.0, 4.0) if u_lo < pt < u_hi})
    bounds = [u_lo, *pts, u_hi]
    samples = [abs(_integ_u(pt)) for pt in bounds]
    samples.extend(abs(_integ_u(0.5 * (a + b))) for a, b in zip(bounds[:-1], bounds[1:]))
    max_u = max(samples) if samples else 0.0
    eps_a = max(1e-300, 1e-14 * max_u * (u_hi - u_lo)) if max_u > 0.0 else 1e-14
    total = 0.0
    for u0, u1 in zip(bounds[:-1], bounds[1:]):
        val, _ = integrate.quad(_integ_u, u0, u1, epsabs=eps_a, epsrel=1e-13, limit=250)
        total += float(val)
    return float(total)


def oracle_polar_conv_radial(r: float, p: int, l: int, w: float, w0: float) -> float:
    """Direct 2D polar Gaussian convolution (G_w * psi_{p,l})^{rad}(r)."""
    if not (math.isfinite(r) and math.isfinite(w) and math.isfinite(w0) and w > 0.0 and w0 > 0.0):
        return 0.0
    al = abs(l)
    cutoff_w0 = max(28.0, math.sqrt(800.0 + 10.0 * (2 * p + al)))
    if r >= 0.0 and (r - 30.0 * w) >= cutoff_w0 * w0:
        return 0.0

    def _ive_kern(rp_val: float) -> float:
        if r > 0.0 and rp_val > 0.0:
            log_arg = math.log(r) + math.log(rp_val) - 2.0 * math.log(w)
            if log_arg > 690.0:
                return math.exp(-0.5 * (math.log(2.0 * math.pi) + log_arg))
            if log_arg < -745.0:
                return 0.0
            return float(_oracle_safe_ive(al, math.exp(log_arg)))
        if r == 0.0 or rp_val == 0.0:
            return 1.0 if al == 0 else 0.0
        return float(_oracle_safe_ive(al, (r / w) * (rp_val / w)))

    if w > 2.0 * w0:
        s_lo = max(0.0, (r - 30.0 * w) / w0)
        s_hi = min(cutoff_w0, (r + 30.0 * w) / w0)
        if s_hi <= s_lo:
            return 0.0

        def _integ_s(s: float) -> float:
            rp = w0 * s
            if rp <= 0.0:
                return 0.0
            u = (rp - r) / w
            kern = (w0 / w) * (rp / w) * math.exp(-0.5 * u * u) * _ive_kern(rp)
            return kern * float(oracle_lg_radial(rp, p, l, w0))

        lg_scale = math.sqrt(float(2 * p + al + 1))
        cands = (
            0.25,
            0.5,
            1.0,
            2.0,
            4.0,
            8.0,
            14.0,
            22.0,
            0.5 * lg_scale,
            lg_scale,
            1.5 * lg_scale,
            r / w0,
            (r - w) / w0,
            (r + w) / w0,
        )
        pts = sorted({float(pt) for pt in cands if s_lo < pt < s_hi})
        bounds = [s_lo, *pts, s_hi]
        samples = [abs(_integ_s(pt)) for pt in bounds]
        samples.extend(abs(_integ_s(0.5 * (a + b))) for a, b in zip(bounds[:-1], bounds[1:]))
        max_s = max(samples) if samples else 0.0
        if max_s == 0.0:
            return 0.0
        eps_a = max(1e-300, 1e-14 * max_s * (s_hi - s_lo))
        total = 0.0
        for s0, s1 in zip(bounds[:-1], bounds[1:]):
            val, _ = integrate.quad(_integ_s, s0, s1, epsabs=eps_a, epsrel=1e-13, limit=250)
            total += float(val)
        return float(total)

    u_lo = max(-30.0, -r / w)
    u_hi = min(30.0, (cutoff_w0 * w0 - r) / w)
    if u_hi <= u_lo:
        return 0.0

    def _integ_u(u: float) -> float:
        rp = r + w * u
        if rp <= 0.0:
            return 0.0
        kern = (rp / w) * math.exp(-0.5 * u * u) * _ive_kern(rp)
        return kern * float(oracle_lg_radial(rp, p, l, w0))

    pts = sorted({float(pt) for pt in (-14.0, -4.0, -1.0, 0.0, 1.0, 4.0, 14.0) if u_lo < pt < u_hi})
    bounds = [u_lo, *pts, u_hi]
    samples = [abs(_integ_u(pt)) for pt in bounds]
    samples.extend(abs(_integ_u(0.5 * (a + b))) for a, b in zip(bounds[:-1], bounds[1:]))
    max_u = max(samples) if samples else 0.0
    eps_a = max(1e-300, 1e-14 * max_u * (u_hi - u_lo)) if max_u > 0.0 else 1e-14
    total = 0.0
    for u0, u1 in zip(bounds[:-1], bounds[1:]):
        val, _ = integrate.quad(_integ_u, u0, u1, epsabs=eps_a, epsrel=1e-13, limit=250)
        total += float(val)
    return float(total)


def oracle_frame_kernel_sum(
    r: float, phi: float, rp: float, phip: float, w: float, l_max: int = 35
) -> float:
    """Evaluate sum_l int R dR Phi_{l,R}(r,phi) Phi_{l,R}^*(rp,phip) via Weber radial factor."""
    if not (math.isfinite(r) and math.isfinite(rp) and math.isfinite(w) and w > 0.0):
        return 0.0
    diff_w = (r - rp) / w
    if abs(diff_w) > 39.0:
        return 0.0
    base = (1.0 / (2.0 * math.pi)) * math.exp(-0.5 * (diff_w * diff_w) - 2.0 * math.log(w))
    dphi = phi - phip
    if r > 0.0 and rp > 0.0:
        log_arg = math.log(r) + math.log(rp) - 2.0 * math.log(w)
        if log_arg > 690.0:
            iv0 = math.exp(-0.5 * (math.log(2.0 * math.pi) + log_arg))
            total = iv0 * (1.0 + 2.0 * sum(math.cos(l * dphi) for l in range(1, l_max + 1)))
            return base * total
        if log_arg < -745.0:
            arg = 0.0
        else:
            arg = math.exp(log_arg)
    else:
        arg = 0.0 if (r == 0.0 or rp == 0.0) else (r / w) * (rp / w)
    total = float(_oracle_safe_ive(0, arg))
    for l in range(1, l_max + 1):
        total += 2.0 * math.cos(l * dphi) * float(_oracle_safe_ive(l, arg))
    return base * total


def oracle_gaussian_kernel_2d(r: float, phi: float, rp: float, phip: float, w: float) -> float:
    dist_sq = r * r + rp * rp - 2.0 * r * rp * math.cos(phi - phip)
    return (1.0 / (2.0 * math.pi * w * w)) * math.exp(-dist_sq / (2.0 * w * w))


def oracle_frame_bounds(w: float, k_max: float) -> tuple[float, float, float]:
    if math.isnan(w) or math.isnan(k_max):
        return float("nan"), 1.0, float("nan")
    if w == 0.0 or k_max == 0.0:
        return 1.0, 1.0, 1.0
    if not (math.isfinite(w) and math.isfinite(k_max)):
        return 0.0, 1.0, float("inf")
    log_wk = math.log(abs(w)) + math.log(abs(k_max))
    if log_wk > 300.0:
        return 0.0, 1.0, float("inf")
    wk = w * k_max
    x = 0.5 * (wk * wk)
    A = math.exp(-x) if x < 745.0 else 0.0
    B = 1.0
    kappa = math.exp(x) if x < 709.0 else float("inf")
    return A, B, kappa


def oracle_tikhonov_mse(
    p: int, l: int, w: float, w0: float, u_max: float, noise_psd: float, alpha: float
) -> tuple[float, float, float]:
    """Compute (bias^2, noise_var, total_mse) on Paley-Wiener disk u <= u_max."""
    a = (w / w0) ** 2
    al = abs(l)
    log_norm = float(special.gammaln(p + 1) - special.gammaln(p + al + 1))

    if alpha == 0.0:
        if u_max <= 0.0:
            return 0.0, 0.0, 0.0
        if a == 0.0:
            noise_var = float(noise_psd) * float(u_max)
        else:
            x = 2.0 * a * u_max
            noise_var = float(noise_psd) * (math.expm1(x) / (2.0 * a)) if x < 709.0 else float("inf")
        return 0.0, noise_var, noise_var

    def _rho(u: float) -> float:
        if u <= 0.0:
            return math.exp(log_norm) if al == 0 else 0.0
        log_wt = log_norm + al * math.log(u) - u
        if log_wt < -745.0:
            return 0.0
        lag = float(special.eval_genlaguerre(p, al, u))
        return math.exp(log_wt) * (lag * lag)

    def _bias_int(u: float) -> float:
        au = a * u
        g_sq = math.exp(-2.0 * au) if au < 350.0 else 0.0
        return ((alpha / (g_sq + alpha)) ** 2) * _rho(u)

    def _noise_int(u: float) -> float:
        au = a * u
        g = math.exp(-au) if au < 709.0 else 0.0
        return (g / (g * g + alpha)) ** 2

    pts: list[float] = []
    if a > 0.0 and alpha > 0.0:
        u_trans = math.log(max(1.0 / alpha, 1.0)) / (2.0 * a)
        du = 35.0 / (2.0 * a)
        pts = sorted({pt for pt in (u_trans - du, u_trans, u_trans + du) if 0.0 < pt < u_max})
    bounds = [0.0, *pts, u_max]
    bias2 = 0.0
    noise_var = 0.0
    for u0, u1 in zip(bounds[:-1], bounds[1:]):
        b_seg, _ = integrate.quad(_bias_int, u0, u1, epsabs=1e-13, epsrel=1e-12, limit=200)
        n_seg, _ = integrate.quad(_noise_int, u0, u1, epsabs=1e-13, epsrel=1e-12, limit=200)
        bias2 += float(b_seg)
        noise_var += float(n_seg)
    noise_var *= noise_psd
    return float(bias2), float(noise_var), float(bias2 + noise_var)


def oracle_fidelity_exact(p: int, l: int, w_over_w0: float) -> float:
    """Exact Laguerre-Gaussian reconstruction fidelity F(p, l, w/w0) in Fourier space via rescaled v = (1 + k*a)*u."""
    if not math.isfinite(w_over_w0):
        return 0.0
    if w_over_w0 <= 0.0:
        return 1.0
    if w_over_w0 > 1.0e150:
        return 0.0
    al = abs(l)
    a = w_over_w0 * w_over_w0
    s1 = 1.0 + a
    s2 = 1.0 + 2.0 * a
    inv_binom = math.exp(float(special.gammaln(p + 1) + special.gammaln(al + 1) - special.gammaln(p + al + 1)))
    lg_gl = float(special.gammaln(al + 1))

    def _scaled_mom(s: float) -> float:
        def _integrand(v: float) -> float:
            if v <= 0.0:
                wt = 1.0 if al == 0 else 0.0
            else:
                wt = math.exp(al * math.log(v) - v - lg_gl)
            lag = inv_binom * float(special.eval_genlaguerre(p, al, v / s))
            return wt * (lag * lag)

        if al > 0:
            v1, _ = integrate.quad(_integrand, 0.0, float(al), epsabs=0.0, epsrel=1e-13, limit=200)
            v2, _ = integrate.quad(_integrand, float(al), np.inf, epsabs=0.0, epsrel=1e-13, limit=200)
            return float(v1 + v2)
        val, _ = integrate.quad(_integrand, 0.0, np.inf, epsabs=0.0, epsrel=1e-13, limit=200)
        return float(val)

    j1 = _scaled_mom(s1)
    j2 = _scaled_mom(s2)
    log_scale = (al + 1) * (math.log(s2) - 2.0 * math.log(s1)) - math.log(inv_binom)
    scale_fac = math.exp(log_scale) if log_scale > -745.0 else 0.0
    return float(min(1.0, max(0.0, scale_fac * (j1 * j1) / j2)))


def oracle_rayleigh_threshold(p: int, l: int, target_f: float = 0.95) -> float:
    """Solve F(p, l, w/w0) = target_f for critical ratio w_crit / w0."""
    return float(
        optimize.brentq(
            lambda ratio: oracle_fidelity_exact(p, l, ratio) - target_f,
            1e-4,
            2.5,
            xtol=1e-12,
        )
    )


def _oracle_log_0f1_bessel(abs_l: int, r1: float, r2: float, w: float) -> float:
    """Compute log(0F1(; |l|+1; ((r1*r2)/(2*w^2))^2)) cleanly across extreme scales."""
    if r1 <= 0.0 or r2 <= 0.0:
        return 0.0
    log_x = math.log(r1) + math.log(r2) - 2.0 * math.log(w)
    thresh = 2.0 * math.sqrt(500.0 * (abs_l + 1))
    if log_x <= math.log(thresh):
        x = math.exp(log_x)
        z = 0.25 * x * x
        s_tail = 0.0
        term = 1.0
        for k in range(1, 200):
            term *= z / (k * (abs_l + k))
            s_tail += term
            if term <= 1e-16 * (1.0 + s_tail):
                break
        return math.log1p(s_tail)
    x = math.exp(log_x) if log_x < 709.0 else float("inf")
    if math.isfinite(x):
        iv = float(_oracle_safe_ive(abs_l, x))
        if iv > 0.0:
            return x + math.log(iv) - abs_l * (log_x - math.log(2.0)) + float(special.gammaln(abs_l + 1))
    with mp.workdps(80):
        zm = ((mp.mpf(r1) * mp.mpf(r2)) / (mp.mpf(w) ** 2)) ** 2 / 4
        return float(mp.log(mp.hyper([], [abs_l + 1], zm)))


def oracle_gram_matrices(
    R_list: list[float] | np.ndarray, w: float, l: int
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Return (G_unnorm, gamma_norm, kappa_G, kappa_gamma)."""
    radii = np.asarray(R_list, dtype=float)
    if np.any(radii < 0.0):
        raise ValueError("R_list radii must be non-negative.")
    n = len(radii)
    al = abs(l)
    G = np.zeros((n, n), dtype=float)
    if n == 0:
        return G, np.zeros((0, 0), dtype=float), 1.0, 1.0
    w_ok = math.isfinite(w) and w > 0.0
    if w_ok:
        fin = np.isfinite(radii)
        if np.any(fin):
            rf = radii[fin]
            m = rf.size
            gf = np.zeros((m, m), dtype=float)
            half_diff = np.abs(0.5 * rf[:, None] - 0.5 * rf[None, :])
            near = half_diff < 19.5 * w
            if np.any(near):
                r1 = np.broadcast_to(rf[:, None], (m, m))[near]
                r2 = np.broadcast_to(rf[None, :], (m, m))[near]
                d = (r1 - r2) / w
                vals = np.zeros_like(d, dtype=float)
                both_pos = (r1 > 0.0) & (r2 > 0.0)
                if np.any(both_pos):
                    r1p, r2p, dp = r1[both_pos], r2[both_pos], d[both_pos]
                    log_arg = np.log(r1p) + np.log(r2p) - 2.0 * math.log(w)
                    huge_arg = log_arg > 690.0
                    sub = np.empty_like(dp, dtype=float)
                    if np.any(huge_arg):
                        sub[huge_arg] = np.exp(
                            -0.5 * (dp[huge_arg] ** 2)
                            - math.log(w)
                            - 0.5 * (math.log(2.0 * math.pi) + np.log(r1p[huge_arg]) + np.log(r2p[huge_arg]))
                        )
                    reg_arg = ~huge_arg
                    if np.any(reg_arg):
                        sub[reg_arg] = (
                            np.exp(-0.5 * (dp[reg_arg] ** 2) - 2.0 * math.log(w))
                            * _oracle_safe_ive(al, np.exp(log_arg[reg_arg]))
                        )
                    vals[both_pos] = sub
                non_pos = ~both_pos
                if np.any(non_pos):
                    dn = d[non_pos]
                    vals[non_pos] = np.exp(-0.5 * (dn ** 2) - 2.0 * math.log(w)) * _oracle_safe_ive(al, 0.0)
                gf[near] = vals
            G[np.ix_(fin, fin)] = gf

    diag = np.sqrt(np.diag(G))
    gamma = np.zeros_like(G, dtype=float)
    pos = diag > 0.0
    if np.any(pos):
        sub_diag = diag[pos]
        gamma[np.ix_(pos, pos)] = G[np.ix_(pos, pos)] / np.outer(sub_diag, sub_diag)
    if not np.all(pos):
        r_flat = radii.ravel()
        valid_mode = np.array(
            [
                w_ok and math.isfinite(float(rv)) and (float(rv) > 0.0 or al == 0)
                for rv in r_flat
            ],
            dtype=bool,
        )
        for i in np.flatnonzero(~pos):
            if not valid_mode[i]:
                gamma[i, i] = 1.0
                continue
            ri = float(r_flat[i])
            gamma[i, i] = 1.0
            for j in range(n):
                if j == i:
                    continue
                if not valid_mode[j]:
                    gamma[i, j] = 0.0
                    gamma[j, i] = 0.0
                    continue
                rj = float(r_flat[j])
                if ri == rj:
                    val_ij = 1.0
                elif (
                    ri > 0.0
                    and rj > 0.0
                    and (math.log(ri) - math.log(w)) > 21.0
                    and (math.log(rj) - math.log(w)) > 21.0
                ):
                    diff_w = (ri - rj) / w
                    val_ij = math.exp(-0.5 * diff_w * diff_w) if abs(diff_w) < 39.0 else 0.0
                else:
                    lg_ij = _oracle_log_0f1_bessel(al, ri, rj, w)
                    lg_ii = _oracle_log_0f1_bessel(al, ri, ri, w)
                    lg_jj = _oracle_log_0f1_bessel(al, rj, rj, w)
                    log_g = lg_ij - 0.5 * (lg_ii + lg_jj)
                    val_ij = math.exp(log_g) if log_g > -745.0 else 0.0
                gamma[i, j] = val_ij
                gamma[j, i] = val_ij
    ev_G = np.linalg.eigvalsh(G)
    ev_g = np.linalg.eigvalsh(gamma)
    kappa_G = float(ev_G[-1] / ev_G[0]) if ev_G[0] > 0.0 else float("inf")
    kappa_gamma = float(ev_g[-1] / ev_g[0]) if ev_g[0] > 0.0 else float("inf")
    return G, gamma, kappa_G, kappa_gamma


def oracle_sdm_zf_penalty_db(gamma: np.ndarray) -> float:
    """Zero-forcing noise enhancement factor Tr[(gamma^T gamma)^{-1}] / N in dB."""
    n = gamma.shape[0]
    gram_sq = gamma.T @ gamma
    zf_factor = float(np.trace(np.linalg.inv(gram_sq)) / n)
    return 10.0 * math.log10(zf_factor)


def oracle_rcf_coupling_gain_db() -> tuple[float, float, float, float]:
    """GRIN-RCF coupling gain (r1=6, r2=9, wf=1.22 um): fixed-wf LG baseline (w0=sqrt(2)*wf) yields ~57.97 dB mean across l=1..6 (cf. Villalba et al. 2023 experimental 6.83 dB gain at l=4 under waist-matched launch)."""
    r_core = 7.5
    wf = 1.22
    w_pvb = 1.22

    def _rcf_mode(r: float) -> float:
        return math.exp(-((r - r_core) ** 2) / (wf * wf))

    norm_rcf, _ = integrate.quad(
        lambda r: 2.0 * math.pi * r * (_rcf_mode(r) ** 2), 0.0, 20.0
    )
    norm_rcf = math.sqrt(norm_rcf)

    # Optimal PVB mode overlap (l-independent when R=r_core, w=w_pvb)
    def _pvb_norm(r: float) -> float:
        return float(oracle_pvb_radial(r, r_core, w_pvb, 1)) / math.sqrt(
            oracle_pvb_self_overlap(r_core, w_pvb, 1)
        )

    ov_pvb, _ = integrate.quad(
        lambda r: 2.0 * math.pi * r * (_rcf_mode(r) / norm_rcf) * _pvb_norm(r), 0.0, 20.0
    )
    eta_pvb = ov_pvb ** 2

    # Average LG_{0,l} overlap across l=1..6 for fixed waist w0=sqrt(2)*wf
    w0 = math.sqrt(2.0) * wf
    etas_lg = []
    for l in range(1, 7):
        ov_lg, _ = integrate.quad(
            lambda r: 2.0 * math.pi * r * (_rcf_mode(r) / norm_rcf) * float(oracle_lg_radial(r, 0, l, w0)),
            0.0,
            25.0,
        )
        etas_lg.append(ov_lg ** 2)
    mean_eta_lg = float(np.mean(etas_lg))
    gain_db = 10.0 * math.log10(eta_pvb / mean_eta_lg)
    return eta_pvb, mean_eta_lg, gain_db, float(min(etas_lg))


def oracle_ic_povm_subspace(
    d: int = 8, M: int = 80, R_min: float = 0.55, R_max: float = 1.55, w: float = 0.10, l: int = 1
) -> tuple[float, float, int, int]:
    """Build radial-PVB POVM on H_d and return (min_eig, res_err, real_op_rank, d^2)."""
    basis_R = np.linspace(R_min, R_max, d)
    _, gamma_b, _, _ = oracle_gram_matrices(basis_R, w, l)
    vals, vecs = np.linalg.eigh(gamma_b)
    inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

    meas_R = np.linspace(R_min - 0.05, R_max + 0.05, M)
    al = abs(l)
    diag_b = np.array([math.sqrt(oracle_pvb_self_overlap(R, w, l)) for R in basis_R])
    v_vecs = []
    for Rm in meas_R:
        dm = math.sqrt(oracle_pvb_self_overlap(Rm, w, l))
        cross = np.array(
            [
                (
                    (1.0 / (w * w))
                    * math.exp(-((Rm - Rj) ** 2) / (2.0 * w * w))
                    * float(_oracle_safe_ive(al, (Rm * Rj) / (w * w)))
                )
                / (dm * diag_b[j])
                for j, Rj in enumerate(basis_R)
            ]
        )
        v_vecs.append(inv_sqrt @ cross)

    S_d = sum(np.outer(v, v) for v in v_vecs)
    s_vals, s_vecs = np.linalg.eigh(S_d)
    S_inv_sqrt = s_vecs @ np.diag(1.0 / np.sqrt(s_vals)) @ s_vecs.T

    pis = [S_inv_sqrt @ np.outer(v, v) @ S_inv_sqrt for v in v_vecs]
    min_eig = min(float(np.min(np.linalg.eigvalsh(pi))) for pi in pis)
    res_err = float(np.linalg.norm(sum(pis) - np.eye(d), ord="fro"))
    op_vecs = np.array([pi.ravel() for pi in pis])
    op_rank = int(np.linalg.matrix_rank(op_vecs, tol=1e-10))
    return min_eig, res_err, op_rank, d * d


def oracle_spdc_iris_transmission_and_chsh(
    R_iris: float, R0: float = 1.0, w: float = 0.10, l1: int = 1, l2: int = 4
) -> tuple[float, float, float, float]:
    """True radial-integral iris transmission and CHSH S for |1,-1>+|l2,-l2> under symmetric two-arm irises (k_l enters as 2*k1*k2/(k1^2+k2^2) -> S_PVB~2.828 vs S_LG~2.001 at R_iris=R0; single-arm iris uses 2*sqrt(T1*T2)/(T1+T2) -> S_LG~2.053)."""
    def _pvb_trans(l_val: int) -> float:
        if R_iris <= 0.0:
            return 0.0
        if math.isfinite(R0) and R0 <= 0.0 and l_val != 0:
            raise ValueError("oracle_spdc_iris_transmission_and_chsh undefined for R0 <= 0 with l != 0.")
        if not (math.isfinite(R0) and math.isfinite(w) and w > 0.0) or math.isnan(R_iris):
            return 0.0
        if math.isinf(R_iris):
            return 1.0
        al = abs(l_val)
        if (R0 / w) > 1.0e7 * max(1, al):
            return float(0.5 * special.erfc(math.sqrt(2.0) * ((R0 - R_iris) / w)))
        u_lo = max(-20.0, -R0 / w)
        u_iris = min(20.0, (R_iris - R0) / w)
        if u_iris <= u_lo:
            return 0.0
        r_norm = max(R0, w)

        def _integ_u(u: float) -> float:
            r = R0 + w * u
            if r <= 0.0:
                return 0.0
            arg = 2.0 * (R0 / w) * (r / w)
            iv = float(_oracle_safe_ive(al, arg))
            return (r / r_norm) * math.exp(-2.0 * u * u) * (iv * iv)

        def _u_quad(fn: Callable[[float], float], a: float, b: float, extra_pts: tuple[float, ...] = ()) -> float:
            if b <= a:
                return 0.0
            base = (-10.0, -4.0, -1.0, 0.0, 1.0, 4.0, 10.0, *extra_pts)
            pts = sorted({float(pt) for pt in base if a < pt < b})
            bounds = [a, *pts, b]
            tot = 0.0
            for x0, x1 in zip(bounds[:-1], bounds[1:]):
                v, _ = integrate.quad(fn, x0, x1, epsabs=1e-14, epsrel=1e-12, limit=200)
                tot += float(v)
            return float(tot)

        den = _u_quad(_integ_u, u_lo, 20.0)
        if den > 0.0:
            num = _u_quad(_integ_u, u_lo, u_iris)
            return float(min(1.0, max(0.0, num / den)))

        # Underflow fallback when ive(|l|, arg)^2 < 5e-324 (e.g., R0 << w with large |l|):
        r_peak = max(R0, w * math.sqrt((2.0 * al + 1.0) / 4.0))
        u_peak = (r_peak - R0) / w
        u_max = max(20.0, u_peak + 20.0)
        u_ir = min(u_max, (R_iris - R0) / w)
        if u_ir <= u_lo:
            return 0.0
        extra = (u_peak - 4.0, u_peak - 1.0, u_peak, u_peak + 1.0, u_peak + 4.0)

        def _series_0f1(x: float) -> float:
            z = 0.25 * x * x
            s = 1.0
            term = 1.0
            for k in range(1, 100):
                term *= z / (k * (al + k))
                s += term
                if term <= 1e-16 * s:
                    break
            return s

        def _integrand_log(u: float) -> float:
            r = R0 + w * u
            if r <= 0.0:
                return 0.0
            arg = 2.0 * (R0 / w) * (r / w)
            exponent = (2 * al + 1) * math.log(r / r_peak) - 2.0 * u * u - 2.0 * arg
            if exponent < -745.0:
                return 0.0
            s_val = _series_0f1(arg)
            return math.exp(exponent) * (s_val * s_val)

        den_l = _u_quad(_integrand_log, u_lo, u_max, extra)
        if den_l <= 0.0:
            return 0.0
        num_l = _u_quad(_integrand_log, u_lo, u_ir, extra)
        return float(min(1.0, max(0.0, num_l / den_l)))

    def _lg_trans(l_val: int) -> float:
        if R_iris <= 0.0 or not (math.isfinite(R0) and R0 > 0.0) or math.isnan(R_iris):
            return 0.0
        if math.isinf(R_iris):
            return 1.0
        w_L = math.sqrt(2.0) * R0
        ratio = R_iris / w_L
        if ratio >= 1.0e150:
            return 1.0
        return float(1.0 - special.gammaincc(abs(l_val) + 1, 2.0 * (ratio * ratio)))

    k_pvb_1, k_pvb_2 = _pvb_trans(l1), _pvb_trans(l2)
    k_lg_1, k_lg_2 = _lg_trans(l1), _lg_trans(l2)

    den_pvb = (k_pvb_1 ** 2) + (k_pvb_2 ** 2)
    den_lg = (k_lg_1 ** 2) + (k_lg_2 ** 2)
    c_pvb = (2.0 * k_pvb_1 * k_pvb_2) / den_pvb if den_pvb > 0.0 else 0.0
    c_lg = (2.0 * k_lg_1 * k_lg_2) / den_lg if den_lg > 0.0 else 0.0
    s_pvb = 2.0 * math.sqrt(1.0 + c_pvb * c_pvb)
    s_lg = 2.0 * math.sqrt(1.0 + c_lg * c_lg)
    return k_pvb_1, k_lg_1, s_pvb, s_lg


def oracle_gouy_ic_povm_d4() -> tuple[int, int, float, float, float, float]:
    """Multi-plane M=5 Gouy IC-POVM radial qudit (d=4, l=1, w/w0=0.25) -> (rank1, rank5, lam_max, lam_min_F, crb_res, crb_nores)."""
    d, l_q, w0, w_pv, n_R, M = 4, 1, 1.0, 0.25, 40, 5
    dR = 3.5 * w0 / n_R
    R_pts = (np.arange(n_R) + 0.5) * dR
    c_mat = np.array([[oracle_c_lp_closed(p, l_q, float(Rk), w_pv, w0) for p in range(d)] for Rk in R_pts])

    E_single = [Rk * dR * np.outer(c_mat[k], c_mat[k]) for k, Rk in enumerate(R_pts)]
    rank_single = int(np.linalg.matrix_rank(np.array(E_single, dtype=complex).reshape(n_R, d * d), tol=1e-10))

    E_multi = []
    p_idx = np.arange(d, dtype=float)
    for zeta in np.linspace(0.0, 0.45 * math.pi, M):
        gouy = np.exp(-1j * (2.0 * p_idx + abs(l_q) + 1.0) * zeta)
        for k, Rk in enumerate(R_pts):
            ket = gouy * c_mat[k]
            E_multi.append((1.0 / M) * Rk * dR * np.outer(ket, ket.conj()))
    E_multi_arr = np.array(E_multi, dtype=complex)
    rank_multi = int(np.linalg.matrix_rank(E_multi_arr.reshape(M * n_R, d * d), tol=1e-10))

    sum_E = np.sum(E_multi_arr, axis=0)
    lam_max = float(np.max(np.linalg.eigvalsh(0.5 * (sum_E + sum_E.conj().T))))
    E_res = np.eye(d, dtype=complex) - sum_E
    E_with_res = np.concatenate([E_multi_arr, E_res[None, :, :]], axis=0)

    # Gell-Mann Hermitian traceless basis (Tr(T_a T_b) = delta_{ab})
    T_basis: list[np.ndarray] = []
    for j in range(d):
        for k in range(j + 1, d):
            ms = np.zeros((d, d), dtype=complex)
            ms[j, k] = ms[k, j] = 1.0 / math.sqrt(2.0)
            T_basis.append(ms)
            ma = np.zeros((d, d), dtype=complex)
            ma[j, k] = -1j / math.sqrt(2.0)
            ma[k, j] = 1j / math.sqrt(2.0)
            T_basis.append(ma)
    for m in range(1, d):
        md = np.zeros((d, d), dtype=complex)
        for j in range(m):
            md[j, j] = 1.0
        md[m, m] = -float(m)
        md /= math.sqrt(m * (m + 1))
        T_basis.append(md)

    rho0 = np.eye(d, dtype=complex) / d

    def _fisher(ops: np.ndarray) -> np.ndarray:
        F = np.zeros((len(T_basis), len(T_basis)), dtype=float)
        for op in ops:
            p0 = float(np.real(np.trace(op @ rho0)))
            if p0 <= 1e-15:
                continue
            grad = np.array([float(np.real(np.trace(op @ T))) for T in T_basis], dtype=float)
            F += np.outer(grad, grad) / p0
        return F

    F_no = _fisher(E_multi_arr)
    F_res = _fisher(E_with_res)
    lam_min_F = float(np.min(np.linalg.eigvalsh(F_res)))
    crb_res = float(np.trace(np.linalg.inv(F_res)))
    crb_no = float(np.trace(np.linalg.inv(F_no)))
    return rank_single, rank_multi, lam_max, lam_min_F, crb_res, crb_no


def _extract_table2_cell_numbers(row: list[str]) -> list[float]:
    """Extract all numeric values from a Table II row, splitting combined '% (dB)' cells."""
    vals: list[float] = []
    for cell in row:
        direct = parse_latex_number(cell)
        if direct is not None:
            vals.append(direct)
            continue
        if "(" in cell:
            for part in re.split(r"[()]", cell):
                cleaned = re.sub(r"\bdB\b", "", part).strip()
                sub = parse_latex_number(cleaned)
                if sub is not None:
                    vals.append(sub)
    return vals


def _assert_table2_all_columns(
    test_case: unittest.TestCase, tex_text: str, label: str
) -> None:
    """Verify all 6 Table II rows across all 7 columns (11 numeric values/row) against first-principles oracles."""
    rows = extract_tabular_rows_matching(tex_text, _is_table2_block)
    test_case.assertGreaterEqual(len(rows), 6, f"Normalized Table II (all 6 rows) not found in {label}")
    parsed = [_extract_table2_cell_numbers(r) for r in rows]
    for ratio in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        matched = [nums for nums in parsed if nums and abs(nums[0] - ratio) < 1e-6]
        test_case.assertGreaterEqual(len(matched), 1, f"{label} Table II missing row dR/w={ratio}")
        nums = matched[0]
        test_case.assertGreaterEqual(len(nums), 11, f"{label} Table II row dR/w={ratio} missing columns: {nums}")
        dr = 0.5 * ratio
        test_case.assertAlmostEqual(nums[1], dr, places=4)
        radii = [2.0 + i * dr for i in range(6)]
        _, gamma, kG, kg = oracle_gram_matrices(radii, 0.5, 1)
        g12 = abs(float(gamma[0, 1]))
        g12_pow = g12 * g12
        iso_db = -10.0 * math.log10(g12_pow)
        gi = np.linalg.inv(gamma)
        zf_corr = float(np.trace(gi) / 6.0)
        zf_corr_db = 10.0 * math.log10(zf_corr)
        zf_awgn = float(np.trace(gi @ gi) / 6.0)
        zf_awgn_db = 10.0 * math.log10(zf_awgn)
        test_case.assertAlmostEqual(nums[2], 100.0 * g12, delta=0.02, msg=f"{label} |gamma12| at {ratio}")
        test_case.assertAlmostEqual(nums[3], 100.0 * g12_pow, delta=0.02, msg=f"{label} |gamma12|^2 at {ratio}")
        test_case.assertAlmostEqual(nums[4], iso_db, delta=0.02, msg=f"{label} isolation dB at {ratio}")
        test_case.assertAlmostEqual(nums[5], kg, delta=max(0.005 * kg, 0.01), msg=f"{label} kappa(gamma) at {ratio}")
        test_case.assertAlmostEqual(nums[6], kG, delta=max(0.005 * kG, 0.01), msg=f"{label} kappa(G) at {ratio}")
        test_case.assertAlmostEqual(nums[7], zf_corr, delta=max(0.005 * zf_corr, 0.002), msg=f"{label} zf_corr at {ratio}")
        test_case.assertAlmostEqual(nums[8], zf_corr_db, delta=0.02, msg=f"{label} zf_corr dB at {ratio}")
        test_case.assertAlmostEqual(nums[9], zf_awgn, delta=max(0.005 * zf_awgn, 0.002), msg=f"{label} zf_awgn at {ratio}")
        test_case.assertAlmostEqual(nums[10], zf_awgn_db, delta=0.02, msg=f"{label} zf_awgn dB at {ratio}")


# ===========================================================================
# TIER 1: FEATURE COVERAGE (60 TESTS: 5 TESTS PER FEATURE #1-#12)
# ===========================================================================

@pytest.mark.tier1
class TestT1Feature01Referee1Report(unittest.TestCase):
    """Feature #1: Referee 1 Innovation & Completeness Report."""

    def test_t1_f01_01_report_exists_utf8(self) -> None:
        p = assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report")
        txt = read_utf8(p)
        self.assertGreater(len(txt), 1000, "Referee 1 report too short")

    def test_t1_f01_02_cites_p33_lines_and_ids(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        ids = extract_referee_ids(txt, "R1")
        self.assertGreaterEqual(len(ids), 3, "Expected >=3 R1-* finding IDs")
        self.assertTrue(
            re.search(r"(?:\bL\d+|\bline\s+\d+)", txt, re.I),
            "Referee 1 report must cite exact p3_3/main.tex line numbers",
        )
        self.assertRegex(txt, r"(?:Sec\.|Section|Eq\.|\\eqref)")

    def test_t1_f01_03_evaluates_novel_contributions(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        self.assertRegex(txt, r"c_\{?l,\s*p\}?|Laguerre")
        self.assertRegex(txt, r"Tikhonov|S_\{?w,\s*\\alpha\}?|dual frame")
        self.assertRegex(txt, r"Paley[- ]?Wiener|frame bound")
        self.assertRegex(txt, r"nodal|Rayleigh|Gram")

    def test_t1_f01_04_evaluates_optics_utility_gap(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        self.assertRegex(txt, r"(?i)classical")
        self.assertRegex(txt, r"(?i)quantum")
        self.assertRegex(txt, r"(?i)(?:ring[- ]?core|RCF|SDM|tomography|POVM|SPDC)")

    def test_t1_f01_05_evaluates_figures_table_and_pvb_term(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        self.assertRegex(txt, r"(?i)figure")
        self.assertRegex(txt, r"(?i)(?:comparative\s+table|table|page\s+budget|compact)")
        self.assertRegex(txt, r"(?i)perfect\s+(?:optical\s+)?vortex")
        self.assertNotRegex(txt, r"(?i)parabolic\s+vector")


@pytest.mark.tier1
class TestT1Feature02Referee2Report(unittest.TestCase):
    """Feature #2: Referee 2 Exhaustive Technical & Editorial Audit Report."""

    def test_t1_f02_01_report_exists_utf8(self) -> None:
        p = assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report")
        txt = read_utf8(p)
        self.assertGreater(len(txt), 1500, "Referee 2 report too short")
        ids = extract_referee_ids(txt, "R2")
        self.assertGreaterEqual(len(ids), 13, "Expected >=13 R2-* finding IDs")

    def test_t1_f02_02_covers_math_defects_m1_to_m11(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        for pat in [
            r"C_0",
            r"P_\{?k_?\{\\max\}|k_\{\\max\}|projection",
            r"without distortion|bias",
            r"base|wedge",
            r"I_\{?l'\}?",
            r"6\.631\.1",
        ]:
            self.assertRegex(txt, pat)

    def test_t1_f02_03_audits_table1_and_rayleigh(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        self.assertIn("0.57033", txt)
        self.assertRegex(txt, r"0\.5625|9/16")
        self.assertRegex(
            txt,
            r"0\.2[^\n]{0,12}/\s*(?:\\sqrt\{?p\}?|sqrt\(p\))|\\frac\{0\.2[^\n]{0,10}\}\{\\sqrt\{p\}\}",
        )
        self.assertRegex(txt, r"2p\s*\+\s*\|l\|\s*\+\s*1")

    def test_t1_f02_04_audits_table2_and_gram_matrix(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        self.assertRegex(txt, r"G_\{?nm\}?")
        self.assertRegex(txt, r"\\gamma_\{?nm\}?|gamma_\{?nm\}?|normalized Gram")
        self.assertRegex(txt, r"13\.6%|13\.5%")
        self.assertRegex(txt, r"(?i)amplitude.*power|power.*amplitude|crosstalk")

    def test_t1_f02_05_audits_structure_and_citations(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        self.assertIn("aleman2023transmission", txt)
        self.assertRegex(txt, r"(?i)Villalba")
        self.assertRegex(txt, r"(?i)Rojas")
        self.assertIn("reddy2016non", txt)
        self.assertRegex(txt, r"(?i)Appendix\s*A|app:weber")


@pytest.mark.tier1
class TestT1Feature03ResolutionMapping(unittest.TestCase):
    """Feature #3: Structured Resolution Mapping Ledger."""

    def test_t1_f03_01_mapping_exists_utf8(self) -> None:
        p = assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger")
        txt = read_utf8(p)
        self.assertGreater(len(txt), 500)

    def test_t1_f03_02_six_column_schema(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        headers, rows = parse_markdown_mapping_rows(txt)
        self.assertEqual(len(headers), 6, f"Expected 6 columns, got: {headers}")
        expected_tokens = [
            "Finding ID",
            "Source",
            "Issue Summary",
            "Target V6 Resolution",
            "V6 Location",
            "Verification Status",
        ]
        for idx, tok in enumerate(expected_tokens):
            self.assertIn(tok.lower(), headers[idx].lower())
        self.assertGreaterEqual(len(rows), 15)

    def test_t1_f03_03_maps_all_r1_and_r2_ids(self) -> None:
        r1 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        r2 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        _, rows = parse_markdown_mapping_rows(mp)
        mapped_ids = {r[0].strip() for r in rows if r}
        expected_ids = extract_referee_ids(r1, "R1") | extract_referee_ids(r2, "R2")
        self.assertTrue(expected_ids.issubset(mapped_ids), f"Missing IDs: {expected_ids - mapped_ids}")

    def test_t1_f03_04_finalized_when_pdfs_present(self) -> None:
        assert_v6_deliverable(self, V6_PRA_PDF, "M3", "Compiled PRA PDF")
        assert_v6_deliverable(self, V6_ARXIV_PDF, "M3", "Compiled arXiv PDF")
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        _, rows = parse_markdown_mapping_rows(mp)
        for row in rows:
            self.assertNotIn("tbd", row[4].lower())
            self.assertNotIn("planned", row[5].lower())

    def test_t1_f03_05_valid_v6_location_targets(self) -> None:
        pra_txt = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "PRA LaTeX source"))
        arxiv_txt = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "arXiv LaTeX source"))
        bib_txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "Bibliography database"))
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        pra_labels = extract_labels(pra_txt)
        arxiv_labels = extract_labels(arxiv_txt)
        pra_refs = set(re.findall(r"\\(?:eq)?ref\{([^}]+)\}", strip_tex_comments(pra_txt)))
        arxiv_refs = set(re.findall(r"\\(?:eq)?ref\{([^}]+)\}", strip_tex_comments(arxiv_txt)))
        self.assertEqual(pra_labels - pra_refs, set(), f"Unused labels in main_pra.tex: {pra_labels - pra_refs}")
        self.assertEqual(pra_refs - pra_labels, set(), f"Broken refs in main_pra.tex: {pra_refs - pra_labels}")
        self.assertEqual(arxiv_labels - arxiv_refs, set(), f"Unused labels in main_arxiv.tex: {arxiv_labels - arxiv_refs}")
        self.assertEqual(arxiv_refs - arxiv_labels, set(), f"Broken refs in main_arxiv.tex: {arxiv_refs - arxiv_labels}")
        bib_keys = {e["key"] for e in parse_bibtex_entries(bib_txt)}
        _, rows = parse_markdown_mapping_rows(mp)
        checked_targets = 0
        for row in rows:
            loc = row[4]
            for lbl in re.findall(r"\b(?:eq|sec|subsec|tab|fig|app|prop|thm|cor|rem):[A-Za-z0-9_:-]+\b", loc):
                checked_targets += 1
                self.assertIn(lbl, pra_labels, f"Label {lbl} missing in main_pra.tex")
                self.assertIn(lbl, arxiv_labels, f"Label {lbl} missing in main_arxiv.tex")
            for bkey in re.findall(r"\b(?:Villalba2023|RojasRojas2021|Reddy2016|Ferreira2026|Gradshteyn2014)\b", loc):
                checked_targets += 1
                self.assertIn(bkey, bib_keys)
        self.assertGreaterEqual(checked_targets, 1)


@pytest.mark.tier1
class TestT1Feature04MathAndOpticsScripts(unittest.TestCase):
    """Feature #4: First-Principles Math & Optics Verification Suite."""

    def test_t1_f04_01_scripts_present_and_valid_ast(self) -> None:
        assert_v6_deliverable(self, V6_SCRIPTS_DIR, "M2", "V6 scripts directory")
        py_files = sorted(V6_SCRIPTS_DIR.glob("*.py"))
        self.assertGreaterEqual(len(py_files), 2, "Expected >=2 verification/figure scripts")
        for pyf in py_files:
            src = read_utf8(pyf)
            tree = ast.parse(src, filename=str(pyf))
            self.assertGreater(len(tree.body), 0)
        run_all = V6_SCRIPTS_DIR / "run_all.py"
        assert_v6_deliverable(self, run_all, "M2", "run_all.py master verification script")
        self.assertIn("__main__", read_utf8(run_all))

    def test_t1_f04_02_scripts_execute_cleanly(self) -> None:
        run_all = assert_v6_deliverable(self, V6_SCRIPTS_DIR / "run_all.py", "M2", "run_all.py")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_v6 = Path(tmp) / "V6"
            shutil.copytree(V6_SCRIPTS_DIR, tmp_v6 / "scripts")
            (tmp_v6 / "figures").mkdir(parents=True, exist_ok=True)
            proc = subprocess.run(
                [sys.executable, str(tmp_v6 / "scripts" / run_all.name)],
                cwd=str(tmp_v6 / "scripts"),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                check=False,
            )
            self.assertEqual(
                proc.returncode,
                0,
                f"run_all.py failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}",
            )

    def test_t1_f04_03_oracle_c_lp_quadrature_match(self) -> None:
        cases = [
            (0, 1, 1.1, 0.35, 1.0),
            (1, 1, 1.0, 0.25, 1.0),
            (2, -2, 0.8, 0.30, 1.0),
            (3, 1, 1.3, 0.20, 1.0),
            (4, 0, 1.5, 0.30, 1.0),
        ]
        for p, l, R, w, w0 in cases:
            cf = oracle_c_lp_closed(p, l, R, w, w0)
            qd = oracle_c_lp_quad(p, l, R, w, w0)
            self.assertLess(abs(cf - qd), 1e-12, f"Mismatch at {(p, l, R, w, w0)}: {cf} vs {qd}")
        syn = oracle_frame_synthesis_radial(0.75, 2, 1, 0.3, 1.0)
        conv = oracle_polar_conv_radial(0.75, 2, 1, 0.3, 1.0)
        self.assertLess(abs(syn - conv), 1e-12)

    def test_t1_f04_04_oracle_bounds_tikhonov_table1(self) -> None:
        A, B, kappa = oracle_frame_bounds(0.5, 4.0)
        self.assertAlmostEqual(A, math.exp(-2.0), places=14)
        self.assertEqual(B, 1.0)
        self.assertAlmostEqual(kappa, math.exp(2.0), places=13)
        # Weber + Graf kernel check
        k_sum = oracle_frame_kernel_sum(1.2, 0.4, 0.9, 1.1, 0.35, l_max=35)
        k_ref = oracle_gaussian_kernel_2d(1.2, 0.4, 0.9, 1.1, 0.35)
        self.assertLess(abs(k_sum - k_ref), 1e-12)
        # Tikhonov bias vs noise U-curve
        b0, _, mse0 = oracle_tikhonov_mse(2, 1, 0.5, 1.0, 12.0, 1e-3, 0.0)
        b_opt, _, mse_opt = oracle_tikhonov_mse(2, 1, 0.5, 1.0, 12.0, 1e-3, 1e-3)
        self.assertEqual(b0, 0.0)
        self.assertGreater(b_opt, 0.0)
        self.assertLess(mse_opt, mse0)
        # Table I exact values and revised Rayleigh threshold
        self.assertAlmostEqual(oracle_fidelity_exact(0, 1, 1.0), 9.0 / 16.0, places=12)
        for p_val in (1, 2, 3, 4):
            w_crit = oracle_rayleigh_threshold(p_val, 1, 0.95)
            scaled = w_crit * math.sqrt(2 * p_val + 1 + 1)
            self.assertGreater(scaled, 0.55)
            self.assertLess(scaled, 0.60)

    def test_t1_f04_05_oracle_gram_sdm_and_quantum(self) -> None:
        kappas = []
        for ratio in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
            dR = ratio * 0.5
            radii = [2.0 + i * dR for i in range(6)]
            _, gamma, _, kg = oracle_gram_matrices(radii, 0.5, 1)
            kappas.append(kg)
            if abs(ratio - 2.0) < 1e-9:
                self.assertAlmostEqual(gamma[0, 1], 0.1355, places=3)
                self.assertGreater(oracle_sdm_zf_penalty_db(gamma), 0.0)
        self.assertEqual(kappas, sorted(kappas, reverse=True))
        eta_pvb, _, gain_db, _ = oracle_rcf_coupling_gain_db()
        self.assertGreater(eta_pvb, 0.99)
        self.assertAlmostEqual(gain_db, 57.9679, places=2)
        min_eig, res_err, op_rank, d2 = oracle_ic_povm_subspace(d=8, M=80)
        self.assertGreaterEqual(min_eig, -1e-12)
        self.assertLess(res_err, 1e-12)
        self.assertLess(op_rank, d2)
        kpvb, klg, spvb, slg = oracle_spdc_iris_transmission_and_chsh(1.0)
        self.assertAlmostEqual(kpvb, 0.50, places=2)
        self.assertLess(klg, 0.30)
        self.assertGreater(spvb, 2.80)
        self.assertLess(slg, 2.10)


@pytest.mark.tier1
class TestT1Feature05VectorFigures(unittest.TestCase):
    """Feature #5: Compact Multi-Panel Vector Figures."""

    def test_t1_f05_01_three_contract_pdfs_exist(self) -> None:
        for fig in V6_FIG_PATHS:
            assert_v6_deliverable(self, fig, "M2", f"vector figure {fig.name}")
            self.assertGreater(fig.stat().st_size, 10240)
            self.assertTrue(fig.read_bytes()[:5] == b"%PDF-")

    def test_t1_f05_02_pymupdf_render_integrity(self) -> None:
        import pymupdf

        for fig in V6_FIG_PATHS:
            assert_v6_deliverable(self, fig, "M2", f"vector figure {fig.name}")
            doc = pymupdf.open(str(fig))
            try:
                self.assertGreaterEqual(len(doc), 1)
                page = doc[0]
                self.assertGreater(len(page.get_drawings()), 0)
                pix = page.get_pixmap(dpi=150)
                self.assertGreater(pix.width, 100)
                self.assertGreater(pix.height, 100)
            finally:
                doc.close()

    def test_t1_f05_03_two_by_two_panel_labels(self) -> None:
        import pymupdf

        for fig in V6_FIG_PATHS:
            assert_v6_deliverable(self, fig, "M2", f"vector figure {fig.name}")
            doc = pymupdf.open(str(fig))
            try:
                txt = doc[0].get_text("text")
            finally:
                doc.close()
            for lbl in ("(a)", "(b)", "(c)", "(d)"):
                self.assertIn(lbl, txt, f"{fig.name} missing panel label {lbl}")

    def test_t1_f05_04_script_palette_and_no_scatter(self) -> None:
        gen_script = assert_v6_deliverable(
            self, V6_SCRIPTS_DIR / "generate_figures.py", "M2", "generate_figures.py"
        )
        src = read_utf8(gen_script)
        self.assertRegex(src, r"(?i)(?:viridis|cividis|plasma|tab10|okabe|#0072B2|#D55E00)")
        self.assertNotIn("np.random.normal", src)

    def test_t1_f05_05_both_tex_include_all_3_figures(self) -> None:
        pra_txt = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "PRA LaTeX source"))
        arxiv_txt = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "arXiv LaTeX source"))
        for label, txt in (("main_pra.tex", pra_txt), ("main_arxiv.tex", arxiv_txt)):
            incs = extract_includegraphics_paths(txt)
            joined = " ".join(incs)
            for name in V6_FIG_NAMES:
                self.assertIn(name.replace(".pdf", ""), joined, f"{label} missing {name}")
            self.assertGreaterEqual(len(re.findall(r"\\caption\{", strip_tex_comments(txt))), 3)


@pytest.mark.tier1
class TestT1Feature06VerifiedBibliography(unittest.TestCase):
    """Feature #6: Verified Bibliography Database (V6/references.bib)."""

    def test_t1_f06_01_bib_exists_and_well_formed(self) -> None:
        bib = assert_v6_deliverable(self, V6_BIB, "M3", "Bibliography database")
        txt = read_utf8(bib)
        self.assertGreater(len(txt), 1000)
        entries = parse_bibtex_entries(txt)
        self.assertGreaterEqual(len(entries), 20)
        depth = 0
        for ch in txt:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            self.assertGreaterEqual(depth, 0, "Unbalanced closing brace in references.bib")
        self.assertEqual(depth, 0, "Unclosed brace in references.bib")

    def test_t1_f06_02_villalba_rojas_split_fixed(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "Bibliography database"))
        entries = {e["key"]: e for e in parse_bibtex_entries(txt)}
        villalba = [e for e in entries.values() if "40113" in e["fields"].get("pages", "")]
        rojas = [e for e in entries.values() if "23381" in e["fields"].get("pages", "")]
        self.assertEqual(len(villalba), 1)
        self.assertEqual(len(rojas), 1)
        self.assertNotEqual(villalba[0]["key"], rojas[0]["key"])
        self.assertIn("Villalba", villalba[0]["fields"].get("author", "").split(" and ")[0])
        self.assertEqual(villalba[0]["fields"].get("year"), "2023")
        self.assertIn("10.1364/OE.503740", villalba[0]["fields"].get("doi", ""))

    def test_t1_f06_03_reddy2016_corrected(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "Bibliography database"))
        entries = parse_bibtex_entries(txt)
        reddy = [e for e in entries if "055602" in e["fields"].get("pages", "")]
        self.assertEqual(len(reddy), 1)
        fields = reddy[0]["fields"]
        self.assertIn("non-diffracting speckles of a perfect vortex beam", fields.get("title", "").lower())
        self.assertIn("Chithrabhanu", fields.get("author", ""))
        self.assertIn("Aadhi", fields.get("author", ""))

    def test_t1_f06_04_seminal_frame_quantum_refs(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "Bibliography database"))
        low = txt.lower()
        for kw in ("duffin", "ali", "christensen", "ferreira", "gradshteyn", "renes", "law"):
            self.assertIn(kw, low, f"Missing seminal reference matching '{kw}'")
        entries = parse_bibtex_entries(txt)
        chris = [e for e in entries if "christensen" in e["fields"].get("author", "").lower()]
        self.assertGreaterEqual(len(chris), 1)
        self.assertEqual(
            chris[0]["fields"].get("year"),
            "2016",
            "R2-B7: Christensen must be upgraded to 2nd ed. (2016)",
        )

    def test_t1_f06_05_citation_resolution_and_blg(self) -> None:
        bib_txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "Bibliography database"))
        pra_txt = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "PRA LaTeX source"))
        arxiv_txt = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "arXiv LaTeX source"))
        bib_keys = {e["key"] for e in parse_bibtex_entries(bib_txt)}
        for name, txt in (("main_pra.tex", pra_txt), ("main_arxiv.tex", arxiv_txt)):
            cites = extract_citations(txt)
            self.assertEqual(cites - bib_keys, set(), f"Missing bib keys in {name}")
        for blg in (V6_PRA_BLG, V6_ARXIV_BLG):
            if blg.exists():
                btxt = read_utf8(blg)
                self.assertNotIn("I didn't find a database entry", btxt)


@pytest.mark.tier1
class TestT1Feature07MathCorrections(unittest.TestCase):
    """Feature #7: Mathematical & Technical Corrections M1-M13."""

    def test_t1_f07_01_norm_and_kernel_proof_m1_m5_m7(self) -> None:
        norm_tok = r"(?:\\\||\\lVert|\\norm(?:\*|\[[^\]]{1,12}\])?\s*\{)"
        norm_end = r"(?:\\\||\\rVert|\})"
        phi_arg = r"\\Phi_\{?(?:l|\\ell)\s{0,3},\s{0,5}R\s{0,3}\}?"
        norm_expr = (
            rf"(?:\\(?:left|[Bb]igg?l?)\s{{0,5}})?{norm_tok}\s{{0,5}}{phi_arg}\s{{0,5}}"
            rf"(?:\\(?:right|[Bb]igg?r?)\s{{0,5}})?{norm_end}"
            rf"(?:\s{{0,5}}\^\{{?2\}}?)?(?:\s{{0,5}}(?:_\{{(?:[^{{}}]|\{{(?:[^{{}}]|\{{[^{{}}]*\}})*\}})*\}}|_L\^2|_2))?(?:\s{{0,5}}\^\{{?2\}}?)?"
        )
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertRegex(
                txt,
                r"I_\{(?:\|\s*l'\s*\||\\lvert\s*l'\s*\\rvert|\\abs\s*\{?\s*l'\s*\}?)\}(?:\s|\\[,!:; ])*(?:\\(?:left|[Bb]ig{1,2}l?)\s*)?\(\s*\\(?:d|t)?frac\s*\{\s*(?:2\s*R'\s*r|2\s*r\s*R')\s*\}\s*\{\s*w\s*\^\s*2\s*\}",
            )
            self.assertRegex(
                txt,
                rf"(?i)(?:not\s+(?:\$?L\^2(?:\s*\(\\mathbb\{{R\}}\^2\))?\$?[- ]?)?(?:unit[- ]?norm(?:alized)?|normalized)|non[- ]?unit[- ]?norm|unnormalized|resolution[- ]?of[- ]?identity\s+(?:constant|factor|scaling)|G_\{{?RR\}}?\s*(?:\\neq|\\ne)\s*1|{norm_tok}\s*{phi_arg}\s*(?:\\(?:right|[Bb]igg?r?)\s*)?{norm_end}[^.\n]{{0,60}}(?:\\neq|\\ne)\s*1)",
            )
            self.assertNotRegex(
                txt,
                rf"{norm_expr}\s{{0,5}}=\s{{0,5}}1(?:\.0+)?(?!(?:\.\d|\d|(?:\s|\\[,!:; ]|~){{0,3}}/))",
                f"False unit-norm equality on Phi_{{l,R}} in {path.name}",
            )
            self.assertNotRegex(
                txt,
                rf"(?<![\d.])1(?:\.0+)?(?!(?:\.\d|\d))\s{{0,5}}=\s{{0,5}}{norm_expr}",
                f"False reversed unit-norm equality on Phi_{{l,R}} in {path.name}",
            )
            for m in re.finditer(
                r"(?i)(?:ensur|yield|produc|giv|form|defin|provid)[a-z]*\s+(?:\$?L\^2\$?[- ]?)?(?<!non-)(?<!non )unit[- ]?norm|C_0[^.\n]{0,80}(?:(?<!non-)(?<!non )unit[- ]?norm\s+modes?|\bto\s+(?:\$?L\^2\$?[- ]+)?(?<!non-)(?<!non )unit[- ]?norm\b)",
                txt,
            ):
                prefix = txt[max(0, m.start() - 45) : m.start()].lower()
                span_low = m.group(0).lower()
                if not re.search(
                    r"\b(?:not|rather\s+than|instead\s+of|neither|fail|no|unlike|contrast|whereas)\b|non[- ]",
                    prefix + " " + span_low,
                ):
                    self.fail(f"False C_0 unit-norm claim in {path.name}: {m.group(0)}")
            self.assertRegex(
                txt,
                r"(?:e\^\{?-i\s*(?:\\mathbf|\\bm|\\vec)?\{?k\}?\s*\\cdot\s*(?:\\mathbf|\\bm|\\vec)?\{?r\}?\}?|\\exp\s*\(\s*-i\s*(?:\\mathbf|\\bm|\\vec)?\{?k\}?\s*\\cdot\s*(?:\\mathbf|\\bm|\\vec)?\{?r\}?\s*\))",
            )
            self.assertRegex(
                txt,
                r"(?i)(?:Jacobi[- ]+Anger|\bGraf\b|Hankel\s+(?:closure|orthogonality|completeness))|J_\{?(?:\|\s*l\s*\||\\lvert\s*l\s*\\rvert|\\abs\s*\{?\s*l\s*\}?)\}?\s*\(\s*R\s*k(?:_\\perp)?\s*\)",
            )

    def test_t1_f07_02_symbols_axicon_asymptotic_m2_m4_m10(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertRegex(txt, r"(?:2\s*R\s*/\s*w(?![\w\^])|\\(?:d|t)?frac\s*\{\s*2\s*R\s*\}\s*\{\s*w\s*\})")
            self.assertRegex(txt, r"(?i)(?:base|wedge)(?:\s*\((?:or\s+)?(?:base|wedge)\)\s+|\s*/\s*(?:base|wedge)\s+|[-\s]+)angle")
            self.assertRegex(txt, r"(?:\\(?:d|t)?frac\s*\{\s*(?:k_r\s*f|f\s*k_r)\s*\}\s*\{\s*k_0\s*\}|(?:k_r\s*f|f\s*k_r)\s*/\s*k_0)")
            self.assertRegex(txt, r"(?:\\(?:d|t)?frac\s*\{\s*2\s*f\s*\}\s*\{\s*k_0\s*w_g\s*\}|2\s*f\s*/\s*\(?\s*k_0\s*w_g\s*\)?)")
            _sep = r"(?:\s|\\[,!:; ]|~|\\cdot){0,8}"
            _na = r"(?:\\(?:mathrm|text|textrm|operatorname)\{NA\}|NA)"
            _k0_na = rf"(?:k_0{_sep}{_na}|{_na}{_sep}k_0)"
            self.assertRegex(
                txt,
                rf"k_\{{?(?:\\max|\\(?:text|mathrm|textrm|operatorname)\{{max\}})\}}?[^.]{{0,60}}{_k0_na}|{_k0_na}[^.]{{0,60}}k_\{{?(?:\\max|\\(?:text|mathrm|textrm|operatorname)\{{max\}})\}}?",
            )
            # R2-M10: separate Gaussian exponent (a_0 / \alpha_0) or \alpha_{\text{reg}} from collision
            self.assertRegex(txt, r"(?:a_0|\\alpha_0|\\alpha_\{?(?:\\text|\\mathrm|\\textrm|\\operatorname)\{reg\}\}?)")
            # R2-M14: 2f chirp cancellation and Fourier phase
            self.assertRegex(
                txt,
                r"(?i)(?:\b2f\$?(?:\s|-)+(?:Fourier|lens|system|setup|geometry|imaging|plane|configuration)|\bchirp|quadratic\s+phase)",
            )
            self.assertRegex(
                txt,
                r"(?:\\(?:left|[Bb]igg?l?)\s*)?\(\s*-i\s*(?:\\(?:right|[Bb]igg?r?)\s*)?\)\^\{?(?:(?:\||\\lvert\s*)?l(?:\s*\\rvert|\|)?|\\abs\{l\})\s*\+\s*1\}?",
            )

    def test_t1_f07_03_dual_projection_and_bias_m8_m9(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertRegex(
                txt,
                r"(?:\\mathcal\{P\}|P)_\{?(?:\\mathcal\{H\}_\{?)?k_\{?(?:\\max|\\(?:text|mathrm|textrm|operatorname)\{max\})\}?\}?",
            )
            self.assertRegex(txt, r"(?i)(?:bias|attenuat|shrinkage)")
            # R2-M15: peak gain / crossover k_peak = w^{-1} sqrt(ln(1/alpha))
            self.assertRegex(
                txt,
                r"\\ln\s*(?:\\left)?\(\s*1\s*/\s*\\alpha|k_\{?(?:\\text|\\mathrm|\\textrm|\\operatorname)\{peak\}\}?|2(?:\s|\\,)*\\sqrt\s*\{\s*\\alpha",
            )

    def test_t1_f07_04_gr_6631_1_and_table1_m11_m12(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertIn("6.631.1", txt)
            self.assertRegex(txt, r"I_\{\s*(?:\|\s*l\s*\||\\lvert\s*l\s*\\rvert|\\abs\s*\{l\})\s*\}")
            self.assertIn("0.5625", txt)
            self.assertRegex(txt, r"2p\s*\+\s*(?:\|\s*l\s*\||\\lvert\s*l\s*\\rvert|\\abs\{l\})\s*\+\s*1")
            # R2-M16: RMS beam radius r_rms (not r_max)
            self.assertRegex(txt, r"r_\{?(?:\\text|\\mathrm|\\textrm|\\operatorname)\{rms\}\}?")

    def test_t1_f07_05_normalized_table2_m13(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertRegex(txt, r"1\.64[45]")
            self.assertRegex(txt, r"1\.17[12]")
            self.assertRegex(txt, r"1\.04[01]")
            self.assertRegex(txt, r"(?is)(?:power|intensity)[^.]{0,120}dB|27\.1[23]?|17\.3[56]")
            # R2-M17: annular asymptotic qualification R_min >> w
            self.assertRegex(txt, r"R_\{\\?(?:text|mathrm|textrm|operatorname)?\{?min\}?\}\s*\\gg\s*(?:\\max\s*\(\s*\{?|\{)?w")


@pytest.mark.tier1
class TestT1Feature08OpticsUtilityAndTable(unittest.TestCase):
    """Feature #8: Classical & Quantum Optics Utility + Comparative Table."""

    def test_t1_f08_01_classical_noisy_lg_and_rcf_sdm(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertRegex(txt, r"(?i)ring[- ]?core\s+fiber|RCF")
            self.assertRegex(txt, r"(?i)zero[- ]?forcing")
            self.assertRegex(txt, r"(?i)MMSE|minimum\s+mean[- ]?square\s+error")
            self.assertRegex(txt, r"(?:6\.83\s*~?dB|57\.9[67]\s*~?dB|99\.5)")
            # R2-M18: normalized-Gram SDM zero-forcing penalties (1.032 / 0.14 dB and 1.099 / 0.41 dB)
            self.assertRegex(txt, r"(?:0\.14\s*~?dB|1\.032)")
            self.assertRegex(txt, r"(?:0\.41\s*~?dB|1\.099)")
            # Worked noisy LG_{2,1} Tikhonov reconstruction + RKHS Kolmogorov turbulence
            self.assertRegex(txt, r"(?:LG\}?|\\psi)_\{?2,\s*1\}?|p\s*=\s*2,?\s*l\s*=\s*1")
            self.assertRegex(txt, r"(?i)RKHS|P_\{\\?(?:text|mathrm)\{RKHS\}\}")
            self.assertRegex(txt, r"(?i)Kolmogorov|D/r_0")

    def test_t1_f08_02_quantum_icpovm_and_spdc_qkd(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertRegex(txt, r"(?i)POVM")
            self.assertRegex(txt, r"(?i)Gouy")
            self.assertRegex(txt, r"(?:M\s*(?:\\ge|>=|=)\s*d\s*\+\s*1|M\s*=\s*5|2d\s*-\s*1)")
            self.assertRegex(txt, r"(?i)(?:Cram[eé\\']+r|Fisher|d\^2)")
            self.assertRegex(txt, r"(?i)SPDC")
            self.assertRegex(txt, r"(?i)CHSH|Bell")
            self.assertRegex(txt, r"(?:2\.828|2\\sqrt\{2\})")
            self.assertRegex(txt, r"(?i)QKD|iris|side[- ]?channel")

    def test_t1_f08_03_comparative_summary_table(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertRegex(txt, r"(?i)Dirac")
            self.assertRegex(txt, r"(?i)coherent\s+states")
            self.assertGreaterEqual(len(re.findall(r"\\begin\{table\*?\}", txt)), 3)

    def test_t1_f08_04_azimuthal_vs_radial_and_z_prop(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertRegex(txt, r"(?i)azimuthal.*orthonormal|orthonormal.*azimuthal")
            self.assertRegex(txt, r"(?i)(?:propagation|Fresnel|z\s*>\s*0|diffraction)")

    def test_t1_f08_05_pvb_terminology_correct(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            self.assertRegex(txt, r"(?i)perfect\s+(?:optical\s+)?vortex")
            self.assertNotRegex(txt, r"(?i)parabolic\s+vector")


@pytest.mark.tier1
class TestT1Feature09AIAttributionAndHygiene(unittest.TestCase):
    """Feature #9: APS-Compliant Human-AI Attribution & Sanitization Hygiene."""

    def test_t1_f09_01_sole_human_author_and_metadata(self) -> None:
        pra_txt = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "PRA LaTeX source"))
        arxiv_txt = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "arXiv LaTeX source"))
        for txt in (pra_txt, arxiv_txt):
            auth = extract_author_block(txt)
            self.assertRegex(auth, r"Sebasti[áa\\']n\s+Ayala|Sebasti\\'an\s+Ayala")
            self.assertNotRegex(auth, r"(?i)gemini|antigravity|\bAI\b|LLM")
            self.assertIn("ayala.phys.ds@gmail.com", txt)
            self.assertIn("Cauquenes", txt)
            self.assertIn("0009-0003-7348-3883", txt)

    def test_t1_f09_02_aps_compliant_ai_disclosure(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertIn("Gemini", txt)
            self.assertIn("Antigravity", txt)
            self.assertRegex(txt, r"(?i)verif(?:ied|ication)")

    def test_t1_f09_03_zero_internal_codenames(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX, V6_BIB):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            for pat in PROHIBITED_CODENAME_REGEXES:
                self.assertNotRegex(txt, pat, f"Internal pattern '{pat}' leaked into {path.name}")

    def test_t1_f09_04_zero_internal_folders_and_versions(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX, V6_BIB):
            txt = strip_tex_comments(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            for pat in PROHIBITED_VERSION_REGEXES:
                self.assertNotRegex(txt, pat, f"Internal path/version '{pat}' leaked into {path.name}")

    def test_t1_f09_05_prose_tone_and_radii_grammar(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            prose = strip_tex_math(
                read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            )
            self.assertEqual(re.findall(r"[A-Za-z]{2,}\s*!", prose), [])
            self.assertNotRegex(prose, r"(?i)\bradiuses\b")
            self.assertRegex(prose, r"\bradii\b")


@pytest.mark.tier1
class TestT1Feature10PRAAndArxivPDFs(unittest.TestCase):
    """Feature #10: Compact PRA & Differentiated arXiv LaTeX + PDFs."""

    def test_t1_f10_01_distinct_pra_and_arxiv_classes(self) -> None:
        pra_txt = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "PRA LaTeX source"))
        arxiv_txt = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "arXiv LaTeX source"))
        self.assertRegex(pra_txt, r"\\documentclass\[[^\]]*pra[^\]]*reprint[^\]]*\]\{revtex4-2\}")
        self.assertRegex(arxiv_txt, r"\\documentclass\[[^\]]*(?:onecolumn|preprint|11pt|12pt)[^\]]*\]")

    def test_t1_f10_02_both_pdfs_exist_and_valid(self) -> None:
        for pdf in (V6_PRA_PDF, V6_ARXIV_PDF):
            assert_v6_deliverable(self, pdf, "M3", f"Compiled PDF {pdf.name}")
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            pages, full_txt, _ = extract_pdf_text_pymupdf(pdf)
            self.assertGreater(pages, 0)
            self.assertGreater(len(full_txt), 5000)

    def test_t1_f10_03_clean_tex_and_bib_logs(self) -> None:
        for log_path in (V6_PRA_LOG, V6_ARXIV_LOG):
            txt = read_utf8(assert_v6_deliverable(self, log_path, "M3", f"LaTeX log {log_path.name}"))
            self.assertNotIn("! LaTeX Error", txt)
            self.assertNotIn("Emergency stop", txt)
            self.assertNotRegex(txt, r"Citation `[^']+' on page \d+ undefined")
            self.assertNotRegex(txt, r"Reference `[^']+' on page \d+ undefined")

    def test_t1_f10_04_concise_page_count_and_abstract(self) -> None:
        pra_pdf = assert_v6_deliverable(self, V6_PRA_PDF, "M3", "Compiled PRA PDF")
        arxiv_pdf = assert_v6_deliverable(self, V6_ARXIV_PDF, "M3", "Compiled arXiv PDF")
        pra_pages, _, _ = extract_pdf_text_pymupdf(pra_pdf)
        arxiv_pages, _, _ = extract_pdf_text_pymupdf(arxiv_pdf)
        self.assertLessEqual(pra_pages, 10)
        self.assertLessEqual(arxiv_pages, 16)
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            abs_txt = extract_abstract_text(read_utf8(tex))
            self.assertLessEqual(len(abs_txt.split()), 220)
            self.assertNotRegex(abs_txt, r"\\(?:cite|ref|eqref)")

    def test_t1_f10_05_cross_manuscript_sync(self) -> None:
        pra_txt = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "PRA LaTeX source"))
        arxiv_txt = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "arXiv LaTeX source"))
        self.assertEqual(extract_citations(pra_txt), extract_citations(arxiv_txt))
        self.assertEqual(
            [Path(p).stem for p in extract_includegraphics_paths(pra_txt)],
            [Path(p).stem for p in extract_includegraphics_paths(arxiv_txt)],
        )


@pytest.mark.tier1
class TestT1Feature11E2ESuiteAndR4(unittest.TestCase):
    """Feature #11: Independent Opaque-Box E2E Suite & R4 Baseline Preservation."""

    def test_t1_f11_01_suite_and_teamwork_docs_exist(self) -> None:
        this_file = Path(__file__).resolve()
        self.assertTrue(this_file.exists())
        ast.parse(read_utf8(this_file))
        self.assertTrue((TEAMWORK_ROOT / "TEST_INFRA.md").exists(), "Missing TEST_INFRA.md in teamwork root")
        self.assertTrue((TEAMWORK_ROOT / "TEST_READY.md").exists(), "Missing TEST_READY.md in teamwork root")

    def test_t1_f11_02_progressive_mode_strict_gate_works(self) -> None:
        # Verify strict assertion helper fails cleanly with AssertionError and never skips
        fake_tc = unittest.TestCase()
        missing = REPO_ROOT / "__nonexistent_v6_probe_target__.txt"
        with self.assertRaises(AssertionError) as ctx:
            assert_v6_deliverable(fake_tc, missing, "M1", "Probe Deliverable")
        self.assertIn("[M1 Deliverable Missing]", str(ctx.exception))
        # Verify no import-time sys.argv mutation calls inside this file via AST
        tree = ast.parse(read_utf8(Path(__file__).resolve()))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if (
                    node.func.attr in {"remove", "pop"}
                    and isinstance(node.func.value, ast.Attribute)
                    and node.func.value.attr == "argv"
                ):
                    self.fail(f"Forbidden sys.argv.{node.func.attr} mutation found")

    def test_t1_f11_03_r4_p33_sha256_and_clean(self) -> None:
        sha, byte_len, line_count, n_files, _ = check_r4_baseline_details()
        self.assertEqual(n_files, 1)
        self.assertEqual(sha, P33_EXPECTED_SHA256)
        self.assertEqual(byte_len, P33_EXPECTED_BYTES)
        self.assertEqual(line_count, P33_EXPECTED_LINES)

    def test_t1_f11_04_r4_v1_to_v5_counts_and_bytes(self) -> None:
        _, _, _, _, stats = check_r4_baseline_details()
        self.assertEqual(stats, PRIOR_VERSION_BASELINE)

    def test_t1_f11_05_opaque_box_no_v6_imports(self) -> None:
        src = read_utf8(Path(__file__).resolve())
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertFalse(alias.name.startswith("V6"), f"Forbidden import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                self.assertFalse(mod.startswith("V6"), f"Forbidden import from {mod}")
        self.assertTrue(TEST_V5_PATH.exists())
        self.assertEqual(TEST_V5_PATH.stat().st_size, TEST_V5_EXPECTED_BYTES)


@pytest.mark.tier1
class TestT1Feature12FinalGateAndHardening(unittest.TestCase):
    """Feature #12: Final E2E Gate & Deliverable Integrity."""

    def test_t1_f12_01_zero_skipped_deliverables_ready(self) -> None:
        required = [
            (V6_REFEREE_1, "M1", "Referee 1 Report"),
            (V6_REFEREE_2, "M1", "Referee 2 Report"),
            (V6_MAPPING, "M1", "Resolution Mapping Ledger"),
            (V6_SCRIPTS_DIR / "run_all.py", "M2", "Master verification script"),
            (V6_BIB, "M3", "Bibliography database"),
            (V6_PRA_TEX, "M3", "PRA LaTeX source"),
            (V6_ARXIV_TEX, "M3", "arXiv LaTeX source"),
            (V6_PRA_PDF, "M3", "Compiled PRA PDF"),
            (V6_ARXIV_PDF, "M3", "Compiled arXiv PDF"),
        ]
        for path, ms, desc in required:
            assert_v6_deliverable(self, path, ms, desc)

    def test_t1_f12_02_no_path_leakage_in_tex(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name))
            self.assertNotRegex(txt, r"[A-Za-z]:\\")
            self.assertNotRegex(txt, r"/(?:Users|home)/")
            self.assertNotIn("../", txt)

    def test_t1_f12_03_pdf_text_no_unresolved_marks(self) -> None:
        for pdf in (V6_PRA_PDF, V6_ARXIV_PDF):
            assert_v6_deliverable(self, pdf, "M3", pdf.name)
            _, full_txt, _ = extract_pdf_text_pymupdf(pdf)
            self.assertNotRegex(full_txt, PDF_UNRESOLVED_MARK_RE)
            for idx in ("1", "2", "3"):
                self.assertRegex(full_txt, rf"Fig\.\s*{idx}|FIG\.\s*{idx}")
            for rom in ("I", "II", "III"):
                self.assertRegex(full_txt, rf"TABLE\s+{rom}|Table\s+{rom}")

    def test_t1_f12_04_bbl_files_present_and_synced(self) -> None:
        for tex_p, bbl_p in ((V6_PRA_TEX, V6_PRA_BBL), (V6_ARXIV_TEX, V6_ARXIV_BBL)):
            tex_txt = read_utf8(assert_v6_deliverable(self, tex_p, "M3", tex_p.name))
            bbl_txt = read_utf8(assert_v6_deliverable(self, bbl_p, "M3", bbl_p.name))
            cites = extract_citations(tex_txt)
            bbl_keys = parse_bbl_keys(bbl_txt)
            self.assertEqual(cites - bbl_keys, set(), f"Unresolved bbl keys in {bbl_p.name}")

    def test_t1_f12_05_r4_post_suite_idempotency(self) -> None:
        sha, byte_len, line_count, n_files, stats = check_r4_baseline_details()
        self.assertEqual((sha, byte_len, line_count, n_files), (P33_EXPECTED_SHA256, P33_EXPECTED_BYTES, P33_EXPECTED_LINES, 1))
        self.assertEqual(stats, PRIOR_VERSION_BASELINE)


# ===========================================================================
# TIER 2: BOUNDARY, CORNER CASES & REGRESSION GUARDS (60 TESTS: 5 / FEATURE)
# ===========================================================================

@pytest.mark.tier2
class TestT2Feature01Referee1Guards(unittest.TestCase):
    """Tier 2 Guards for Feature #1: Referee 1 Report."""

    def test_t2_f01_01_no_parabolic_vector_leak(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        self.assertNotRegex(txt, r"(?i)parabolic\s+vector")

    def test_t2_f01_02_no_placeholder_markers(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        self.assertNotRegex(txt, r"\b(?:TBD|TODO|FIXME)\b|<placeholder>")

    def test_t2_f01_03_distinguishes_p33_vs_v5_novelty(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        self.assertRegex(txt, r"c_\{?l,\s*p\}?")
        self.assertRegex(txt, r"(?i)novel|original|contribution")

    def test_t2_f01_04_compact_budget_boundary(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        self.assertRegex(txt, r"(?i)(?:compact|fewer\s+pages|page\s+budget|PRA)")

    def test_t2_f01_05_cites_exact_p33_lines_in_range(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        lines = [int(n) for n in re.findall(r"(?:\bL|\bline\s+)(\d+)\b", txt, re.I)]
        self.assertGreater(len(lines), 0)
        for ln in lines:
            self.assertTrue(1 <= ln <= P33_EXPECTED_LINES, f"Out-of-range line L{ln}")


@pytest.mark.tier2
class TestT2Feature02Referee2Guards(unittest.TestCase):
    """Tier 2 Guards for Feature #2: Referee 2 Report."""

    def test_t2_f02_01_flags_aleman2023_author_and_995(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        self.assertIn("aleman2023transmission", txt)
        self.assertRegex(txt, r"(?i)Villalba")
        self.assertRegex(txt, r"99\.5|0\.995")

    def test_t2_f02_02_flags_gr_6643_2_error(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        self.assertIn("6.643.2", txt)
        self.assertIn("6.631.1", txt)

    def test_t2_f02_03_flags_table1_057033_and_rayleigh(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        self.assertIn("0.57033", txt)
        self.assertIn("0.5625", txt)
        self.assertRegex(txt, r"p\s*=\s*0")

    def test_t2_f02_04_flags_table2_unnormalized_gram(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        self.assertRegex(txt, r"4\.10|4\.096|4\.65|4\.646")
        self.assertIn("34.3", txt)
        self.assertRegex(txt, r"1\.64[45]|\\gamma_\{?nm\}?")

    def test_t2_f02_05_flags_reddy_and_c0_norm(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        self.assertIn("reddy2016non", txt)
        self.assertRegex(txt, r"C\.?\s*~?P\.|Chithrabhanu")
        self.assertIn("C_0", txt)
        self.assertNotRegex(txt, r"(?i)parabolic\s+vector")


@pytest.mark.tier2
class TestT2Feature03MappingGuards(unittest.TestCase):
    """Tier 2 Guards for Feature #3: Resolution Mapping Ledger."""

    def test_t2_f03_01_strict_six_cell_rows(self) -> None:
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        for ln_no, line in enumerate(mp.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("|"):
                self.assertTrue(stripped.endswith("|"), f"Mapping table line {ln_no} missing trailing '|': {stripped}")
        _, rows = parse_markdown_mapping_rows(mp)
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertEqual(len(row), 6, f"Malformed mapping row: {row}")
            self.assertTrue(bool(row[0].strip()), f"Blank Finding ID cell in row: {row}")
            for cell in row:
                for math_span in re.findall(r"(?<!\\)\$[^$\n]+(?<!\\)\$", cell):
                    self.assertNotRegex(
                        math_span,
                        r"(?<!\\)\|",
                        f"Unescaped '|' inside math span breaks Markdown table: {math_span}",
                    )

    def test_t2_f03_02_no_duplicate_finding_ids(self) -> None:
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        _, rows = parse_markdown_mapping_rows(mp)
        ids = [r[0].strip() for r in rows]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate Finding IDs in RESOLUTION_MAPPING.md")

    def test_t2_f03_03_exact_r1_r2_set_equality(self) -> None:
        r1 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        r2 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        _, rows = parse_markdown_mapping_rows(mp)
        mapped = {r[0].strip() for r in rows}
        expected = extract_referee_ids(r1, "R1") | extract_referee_ids(r2, "R2")
        self.assertEqual(mapped, expected, f"Sym diff: {mapped ^ expected}")

    def test_t2_f03_04_zero_unresolved_status_at_m3(self) -> None:
        assert_v6_deliverable(self, V6_PRA_PDF, "M3", "Compiled PRA PDF")
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        _, rows = parse_markdown_mapping_rows(mp)
        for row in rows:
            self.assertNotRegex(row[5], r"(?i)\b(?:pending|tbd|planned|unresolved)\b")

    def test_t2_f03_05_source_lines_within_1_to_596(self) -> None:
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        _, rows = parse_markdown_mapping_rows(mp)
        for row in rows:
            for ln in re.findall(r"\bL(\d+)\b", row[1]):
                self.assertTrue(1 <= int(ln) <= P33_EXPECTED_LINES)


@pytest.mark.tier2
class TestT2Feature04MathBoundaryOracles(unittest.TestCase):
    """Tier 2 Boundary & Corner Mathematical Oracles (Unconditional)."""

    def test_t2_f04_01_p0_l0_boundary_collapse(self) -> None:
        w, w0 = 0.4, 1.2
        for R in (0.0, 0.5, 1.8):
            expected = (2.0 * w0 / (w0 * w0 + w * w)) * math.exp(-(R * R) / (w0 * w0 + w * w))
            cf = oracle_c_lp_closed(0, 0, R, w, w0)
            qd = oracle_c_lp_quad(0, 0, R, w, w0)
            self.assertLess(abs(cf - expected), 1e-15)
            self.assertLess(abs(cf - qd), 1e-13)

    def test_t2_f04_02_negative_l_parity_symmetry(self) -> None:
        for l in (1, 2, 3, 5):
            for p in (0, 2):
                c_pos = oracle_c_lp_closed(p, l, 1.1, 0.3, 1.0)
                c_neg = oracle_c_lp_closed(p, -l, 1.1, 0.3, 1.0)
                self.assertLess(abs(c_pos - c_neg), 1e-15)
            _, g_pos, _, _ = oracle_gram_matrices([1.5, 2.5], 0.5, l)
            _, g_neg, _, _ = oracle_gram_matrices([1.5, 2.5], 0.5, -l)
            self.assertLess(np.max(np.abs(g_pos - g_neg)), 1e-15)

    def test_t2_f04_03_r_zero_origin_boundary(self) -> None:
        w = 0.4
        c0 = (1.0 / (w * w)) * math.sqrt(2.0 / math.pi)
        val_l0 = float(oracle_pvb_radial(0.5, 0.0, w, 0))
        self.assertAlmostEqual(val_l0, c0 * math.exp(-(0.5 ** 2) / (w * w)), places=14)
        for l in (1, 2, 3):
            self.assertEqual(float(oracle_pvb_radial(0.5, 0.0, w, l)), 0.0)
            self.assertEqual(oracle_c_lp_closed(2, l, 0.0, w, 1.0), 0.0)

    def test_t2_f04_04_extreme_kmax_and_tikhonov_limits(self) -> None:
        A_small, _, k_small = oracle_frame_bounds(0.5, 1e-6)
        self.assertAlmostEqual(A_small, 1.0, places=10)
        self.assertAlmostEqual(k_small, 1.0, places=10)
        A_large, _, k_large = oracle_frame_bounds(0.5, 20.0)
        self.assertLess(A_large, 1e-20)
        self.assertGreater(k_large, 1e20)
        # For any alpha > 0, Tikhonov filter G^2/(G^2+alpha) < 1 strictly
        for alpha in (1e-6, 1e-3, 1e-1):
            for k in (0.0, 1.0, 3.0):
                g = math.exp(-0.5 * (0.4 * k) ** 2)
                self.assertLess((g * g) / (g * g + alpha), 1.0)

    def test_t2_f04_05_fidelity_rational_and_gram_limits(self) -> None:
        self.assertAlmostEqual(oracle_fidelity_exact(0, 1, 1.0), 9.0 / 16.0, places=14)
        self.assertNotAlmostEqual(oracle_fidelity_exact(0, 1, 1.0), 0.57033, places=3)
        self.assertGreater(oracle_fidelity_exact(2, 1, 1e-3), 0.999999)
        _, _, _, k_far = oracle_gram_matrices([2.0, 10.0, 18.0], 0.5, 1)
        self.assertAlmostEqual(k_far, 1.0, places=10)
        _, _, _, k_close = oracle_gram_matrices([2.0, 2.01], 0.5, 1)
        self.assertGreater(k_close, 1e3)


@pytest.mark.tier2
class TestT2Feature05FigureGuards(unittest.TestCase):
    """Tier 2 Guards for Feature #5: Vector Figures & Generation Scripts."""

    def test_t2_f05_01_single_page_per_figure(self) -> None:
        import pymupdf

        for fig in V6_FIG_PATHS:
            assert_v6_deliverable(self, fig, "M2", fig.name)
            doc = pymupdf.open(str(fig))
            try:
                self.assertEqual(len(doc), 1, f"{fig.name} must be single-page")
            finally:
                doc.close()

    def test_t2_f05_02_aspect_ratio_and_min_dimensions(self) -> None:
        import pymupdf

        for fig in V6_FIG_PATHS:
            assert_v6_deliverable(self, fig, "M2", fig.name)
            doc = pymupdf.open(str(fig))
            try:
                rect = doc[0].rect
                self.assertGreaterEqual(rect.width, 180.0)
                self.assertGreaterEqual(rect.height, 140.0)
                ratio = rect.width / rect.height
                self.assertTrue(0.5 <= ratio <= 2.5, f"{fig.name} aspect ratio {ratio:.2f}")
            finally:
                doc.close()

    def test_t2_f05_03_non_blank_rendered_pixmap(self) -> None:
        import pymupdf

        for fig in V6_FIG_PATHS:
            assert_v6_deliverable(self, fig, "M2", fig.name)
            doc = pymupdf.open(str(fig))
            try:
                pix = doc[0].get_pixmap(dpi=72)
                arr = np.frombuffer(pix.samples, dtype=np.uint8)
                self.assertGreater(float(np.std(arr)), 5.0, f"{fig.name} appears blank")
            finally:
                doc.close()

    def test_t2_f05_04_vector_drawings_present(self) -> None:
        import pymupdf

        for fig in V6_FIG_PATHS:
            assert_v6_deliverable(self, fig, "M2", fig.name)
            doc = pymupdf.open(str(fig))
            try:
                self.assertGreater(len(doc[0].get_drawings()), 20)
            finally:
                doc.close()

    def test_t2_f05_05_scripts_safe_io_and_no_v5_bug(self) -> None:
        assert_v6_deliverable(self, V6_SCRIPTS_DIR, "M2", "V6 scripts directory")
        for pyf in V6_SCRIPTS_DIR.glob("*.py"):
            src = read_utf8(pyf)
            self.assertNotRegex(src, r"p3_3|v[1-5]/")
            self.assertNotIn("2.0 * r / w0", src)


@pytest.mark.tier2
class TestT2Feature06BibliographyGuards(unittest.TestCase):
    """Tier 2 Guards for Feature #6: Verified Bibliography."""

    def test_t2_f06_01_no_duplicate_keys_or_dois(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib"))
        entries = parse_bibtex_entries(txt)
        keys = [e["key"] for e in entries]
        self.assertEqual(len(keys), len(set(keys)), "Duplicate BibTeX keys")
        dois = [e["fields"]["doi"].lower() for e in entries if e["fields"].get("doi")]
        self.assertEqual(len(dois), len(set(dois)), "Duplicate DOIs in references.bib")

    def test_t2_f06_02_regressions_purged(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib"))
        for bad in ("aleman2023transmission", "Divergence of Gaussian vortex beams", "PRX Intell", "C.~P."):
            self.assertNotIn(bad, txt)

    def test_t2_f06_03_required_fields_non_empty(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib"))
        for e in parse_bibtex_entries(txt):
            f = e["fields"]
            if "author" in f:
                self.assertNotRegex(
                    f["author"],
                    r"(?i)\bet\s+al\b|\band\s+others\b",
                    f"R2-B5: Premature author truncation in {e['key']}",
                )
            if e["type"] == "article":
                for req in ("author", "title", "journal", "year"):
                    self.assertTrue(bool(f.get(req)), f"{e['key']} missing {req}")
            elif e["type"] == "book":
                self.assertTrue(bool(f.get("author") or f.get("editor")), f"{e['key']} missing author/editor")
                for req in ("title", "publisher", "year"):
                    self.assertTrue(bool(f.get(req)), f"{e['key']} missing {req}")

    def test_t2_f06_04_villalba_and_reddy_exact_fields(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib"))
        entries = parse_bibtex_entries(txt)
        v_hits = [e for e in entries if "40113" in e["fields"].get("pages", "")]
        self.assertEqual(len(v_hits), 1)
        author = v_hits[0]["fields"].get("author", "")
        self.assertIn("Villalba", author)
        self.assertIn("Ayala", author)
        self.assertLess(author.find("Villalba"), author.find("Ayala"))
        r_hits = [e for e in entries if "055602" in e["fields"].get("pages", "")]
        self.assertEqual(len(r_hits), 1)
        self.assertIn("non-diffracting speckles", r_hits[0]["fields"]["title"].lower())

    def test_t2_f06_05_zero_orphans_and_key_parity(self) -> None:
        bib_keys = {e["key"] for e in parse_bibtex_entries(read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib")))}
        c_pra = extract_citations(read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")))
        c_arx = extract_citations(read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex")))
        self.assertEqual(c_pra, c_arx)
        self.assertEqual(bib_keys - c_pra, set(), f"Unused bib keys: {bib_keys - c_pra}")


@pytest.mark.tier2
class TestT2Feature07MathRegressionGuards(unittest.TestCase):
    """Tier 2 Regression Guards for Feature #7: M1-M13 Math Fixes."""

    def test_t2_f07_01_no_gr_6643_2_regression(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            self.assertNotIn("6.643.2", txt)
            self.assertIn("6.631.1", txt)

    def test_t2_f07_02_no_057033_or_02_sqrt_p(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            self.assertNotIn("0.57033", txt)
            self.assertNotRegex(
                txt,
                r"(?:0\.2\b|\\(?:d|t)?frac\{\s*0\.2\b[^}]*\})[^.]{0,35}(?:\\sqrt\s*\{?\s*p\s*\}?|sqrt\s*\(\s*p\s*\))",
            )
            self.assertIn("0.5625", txt)
            # Verify 2p + |l| + 1 appears in Rayleigh / fidelity / resolution context
            rayleigh_hits = [
                m for m in re.finditer(r"(?i)(?:Rayleigh|w_\{\\?(?:text|mathrm|textrm|operatorname)\{crit\}\}|0\.57[23]|nodal\s+washout)", txt)
                if re.search(r"2p\s*\+\s*(?:\|\s*l\s*\||\\lvert\s*l\s*\\rvert|\\abs\{l\})\s*\+\s*1", txt[max(0, m.start() - 400) : min(len(txt), m.end() + 400)])
            ]
            self.assertGreaterEqual(
                len(rayleigh_hits),
                1,
                f"2p + |l| + 1 missing from Rayleigh/resolution context in {tex.name}",
            )

    def test_t2_f07_03_no_unnormalized_410_465_conflict(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            rows = extract_tabular_rows_matching(txt, _is_table2_block)
            self.assertGreaterEqual(len(rows), 6, f"Normalized Table II (all 6 rows) not found in {tex.name}")
            parsed_rows = [
                [v for v in (parse_latex_number(c) for c in r) if v is not None]
                for r in rows
            ]
            for expected_ratio, expected_pat in ((2.0, r"1\.64[45]"), (2.5, r"1\.17[12]"), (3.0, r"1\.04[01]")):
                matching = [
                    r for r, nums in zip(rows, parsed_rows)
                    if nums and abs(nums[0] - expected_ratio) < 1e-6
                ]
                self.assertGreaterEqual(len(matching), 1, f"{tex.name} Table II missing row dR/w={expected_ratio}")
                row_text = " ".join(matching[0])
                self.assertRegex(
                    row_text,
                    expected_pat,
                    f"{tex.name} Table II row dR/w={expected_ratio} missing normalized kappa(gamma)",
                )

    def test_t2_f07_04_no_distortionless_alpha_gt_zero(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            _assert_no_positive_distortionless_alpha(self, txt, tex.name)

    def test_t2_f07_05_no_apex_angle_or_math_LG_or_appA(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            self.assertNotIn("apex angle", txt.lower())
            self.assertNotRegex(
                txt,
                r"(?<!\\mathrm\{)(?<!\\text\{)(?<!\\textrm\{)(?<!\\mbox\{)(?<!\\operatorname\{)\bLG_(?:\{[^}]+\}|[p0-9a-zA-Z]+\s*,\s*[l0-9a-zA-Z\-]+)",
            )
            self.assertNotIn("app:weber", txt)
            self.assertNotRegex(txt, r"r_\{\\?(?:text|mathrm|textrm|operatorname)?\{?max\}?\}\s*(?:=|\\sim|\\approx)\s*w_0(?:\s|\\,)*\\sqrt\{2p")
            # Additional R2-M2/M3/M4/M10/M13 negative regression guards
            self.assertNotRegex(
                txt,
                r"(?:\|\s*l\s*\||\\lvert\s*l\s*\\rvert|\\abs\{l\})\s*\\ll\s*(?:R\s*/\s*w(?![\w\^])|\\(?:d|t)?frac\s*\{\s*R\s*\}\s*\{\s*w\s*\})",
            )
            self.assertNotRegex(txt, r"\\alpha_\{?(?:\\text|\\mathrm|\\textrm|\\operatorname)?\{?ax\}?\}?")
            self.assertNotRegex(txt, r"k_\{?(?:\\text|\\mathrm|\\textrm|\\operatorname)\{paraxial\}\}?")
            self.assertNotRegex(txt, r"\\(?:d|t)?frac\s*\{\s*(?:k_r\s*f|f\s*k_r)\s*\}\s*\{\s*k\s*\}")
            self.assertNotRegex(txt, r"\\(?:d|t)?frac\s*\{\s*2\s*f\s*\}\s*\{\s*k\s*w_g\s*\}")
            self.assertNotRegex(
                txt,
                r"(?<![A-Za-z\\])\\alpha\s*=\s*(?:1\s*/\s*w\^2|\\(?:d|t)?frac\s*\{\s*1\s*\}\s*\{\s*w\^2\s*\})\s*\+\s*(?:1\s*/\s*w_0\^2|\\(?:d|t)?frac\s*\{\s*1\s*\}\s*\{\s*w_0\^2\s*\})",
            )
            self.assertNotRegex(
                txt,
                r"(?i)isolation(?:\s|\$){0,10}(?:(?:>|\\ge|\\geq|\\gtrsim)(?:\s|\$){0,10})?13\.50?(?:\s|\$|~|\\[,!:; ]){0,20}(?:\\(?:text|mathrm|textrm)\{\s{0,5})?dB",
            )


@pytest.mark.tier2
class TestT2Feature08OpticsUtilityGuards(unittest.TestCase):
    """Tier 2 Guards for Feature #8: Classical & Quantum Optics Utility."""

    def test_t2_f08_01_iris_transmission_limits(self) -> None:
        k_high, _, _, _ = oracle_spdc_iris_transmission_and_chsh(1.0 + 4.0 * 0.10, R0=1.0, w=0.10)
        k_low, _, _, _ = oracle_spdc_iris_transmission_and_chsh(1.0 - 4.0 * 0.10, R0=1.0, w=0.10)
        k_mid, _, _, _ = oracle_spdc_iris_transmission_and_chsh(1.0, R0=1.0, w=0.10)
        self.assertGreater(k_high, 0.999)
        self.assertLess(k_low, 0.001)
        self.assertTrue(0.42 <= k_mid <= 0.58)

    def test_t2_f08_02_no_false_oam_non_ortho_claim(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            self.assertNotRegex(txt, r"(?i)OAM\s+modes\s+(?:are|with\s+different\s+l\s+are)\s+non[- ]?orthogonal")

    def test_t2_f08_03_comparative_table_four_families(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            tables = [
                m.group(0)
                for m in re.finditer(r"\\begin\{(tabular\*?)\}.*?\\end\{\1\}", txt, flags=re.DOTALL)
            ]
            comp = [t for t in tables if "dirac" in t.lower() and "coherent" in t.lower()]
            self.assertGreaterEqual(len(comp), 1, f"Comparative table missing in {tex.name}")
            self.assertGreaterEqual(comp[0].count("\\\\"), 4)

    def test_t2_f08_04_rcf_995_not_misattributed_to_villalba(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            self.assertNotIn("aleman2023transmission", txt)
            body = re.sub(r"\\begin\{abstract\}.*?\\end\{abstract\}", " ", txt, flags=re.DOTALL)
            hits = list(re.finditer(r"(?:99\.5|0\.995)", body))
            rojas_hits = 0
            for m in hits:
                window = body[max(0, m.start() - 120) : min(len(body), m.end() + 250)]
                left = body[max(0, m.start() - 120) : m.start()]
                right = body[m.end() : min(len(body), m.end() + 180)]
                clause = (
                    re.split(r"[.;\n]|\b(?:whereas|while|and)\b", left, flags=re.I)[-1]
                    + m.group(0)
                    + re.split(r"[.;\n]|\b(?:whereas|while|and)\b", right, flags=re.I)[0]
                )
                if "Villalba" in clause and "Rojas" not in clause:
                    self.fail(f"99.5% coupling misattributed to Villalba in {tex.name}: {clause.strip()}")
                if "Rojas" in window:
                    rojas_hits += 1
                if "\\cite" in window:
                    self.assertIn("Rojas", window)
            if hits:
                self.assertGreaterEqual(rojas_hits, 1, f"99.5% coupling in {tex.name} must cite Rojas")

    def test_t2_f08_05_zero_parabolic_vector_anywhere(self) -> None:
        for path in [V6_REFEREE_1, V6_REFEREE_2, V6_MAPPING, V6_PRA_TEX, V6_ARXIV_TEX]:
            txt = read_utf8(assert_v6_deliverable(self, path, "M3", path.name))
            self.assertNotRegex(txt, r"(?i)parabolic\s+vector")


@pytest.mark.tier2
class TestT2Feature09HygieneAndAIGuards(unittest.TestCase):
    """Tier 2 Guards for Feature #9: Hygiene & Human-AI Attribution."""

    def test_t2_f09_01_no_ai_in_author_command(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            auth = extract_author_block(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            self.assertNotRegex(auth, r"(?i)gemini|antigravity|\bAI\b|LLM|GPT|Claude")

    def test_t2_f09_02_ai_disclosure_both_manuscripts(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            self.assertIn("Gemini", txt)
            self.assertIn("Antigravity", txt)
            self.assertIn("Ayala", txt)

    def test_t2_f09_03_prohibited_internal_patterns_zero(self) -> None:
        for path in (V6_PRA_TEX, V6_ARXIV_TEX, V6_BIB):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, path, "M3", path.name)))
            for pat in PROHIBITED_INTERNAL_REGEXES:
                self.assertNotRegex(txt, pat, f"Prohibited pattern '{pat}' found in {path.name}")

    def test_t2_f09_04_no_prose_exclamations_or_radiuses(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            prose = strip_tex_math(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            self.assertEqual(re.findall(r"[A-Za-z]{2,}\s*!", prose), [])
            self.assertNotRegex(prose, r"(?i)\bradiuses\b|\bmultiple\s+radius\b")

    def test_t2_f09_05_metadata_parity_pra_vs_arxiv(self) -> None:
        pra = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex"))
        arx = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex"))
        for token in ("ayala.phys.ds@gmail.com", "Cauquenes", "0009-0003-7348-3883"):
            self.assertIn(token, pra)
            self.assertIn(token, arx)
        self.assertNotIn("sayala@udec.cl", pra)
        self.assertNotIn("sayala@udec.cl", arx)


@pytest.mark.tier2
class TestT2Feature10PDFAndTeXGuards(unittest.TestCase):
    """Tier 2 Guards for Feature #10: PDF Layout, Page Budget & Cleanliness."""

    def test_t2_f10_01_pra_twocol_vs_arxiv_onecol_layout(self) -> None:
        pra_pdf = assert_v6_deliverable(self, V6_PRA_PDF, "M3", "main_pra.pdf")
        arx_pdf = assert_v6_deliverable(self, V6_ARXIV_PDF, "M3", "main_arxiv.pdf")

        pra_paired, _, _ = classify_pdf_layout(pra_pdf)
        arx_paired, arx_wide_body, _ = classify_pdf_layout(arx_pdf)

        self.assertGreaterEqual(pra_paired, 1, "PRA must be two-column")
        self.assertEqual(arx_paired, 0, "arXiv must be single-column (found paired 2-col prose)")
        self.assertGreaterEqual(arx_wide_body, 1, "arXiv must contain wide single-column prose")

    def test_t2_f10_02_page_count_lower_and_upper_bounds(self) -> None:
        pra_pages, _, _ = extract_pdf_text_pymupdf(assert_v6_deliverable(self, V6_PRA_PDF, "M3", "main_pra.pdf"))
        arx_pages, _, _ = extract_pdf_text_pymupdf(assert_v6_deliverable(self, V6_ARXIV_PDF, "M3", "main_arxiv.pdf"))
        self.assertTrue(4 <= pra_pages <= 10, f"PRA page count {pra_pages} outside [4, 10]")
        self.assertTrue(5 <= arx_pages <= 16, f"arXiv page count {arx_pages} outside [5, 16]")

    def test_t2_f10_03_abstract_word_count_and_cleanliness(self) -> None:
        for tex in (V6_PRA_TEX, V6_ARXIV_TEX):
            abs_txt = extract_abstract_text(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            wc = len(abs_txt.split())
            self.assertTrue(100 <= wc <= 220, f"{tex.name} abstract word count {wc}")
            self.assertNotRegex(abs_txt, r"\\(?:cite|ref|eqref)|Eq\.\s*\(\d+\)")

    def test_t2_f10_04_zero_question_marks_in_pdfs(self) -> None:
        for pdf in (V6_PRA_PDF, V6_ARXIV_PDF):
            _, full_txt, _ = extract_pdf_text_pymupdf(assert_v6_deliverable(self, pdf, "M3", pdf.name))
            self.assertNotRegex(full_txt, PDF_UNRESOLVED_MARK_RE)
            self.assertNotIn("Undefined control sequence", full_txt)

    def test_t2_f10_05_flat_arxiv_path_portability(self) -> None:
        txt = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex"))
        self.assertNotRegex(txt, r"[A-Za-z]:\\|/(?:Users|home)/|\.\./")


@pytest.mark.tier2
class TestT2Feature11E2EAndR4Guards(unittest.TestCase):
    """Tier 2 Guards for Feature #11: R4 Baseline & Strict Harness Contract."""

    def test_t2_f11_01_r4_p33_exact_hash_bytes_lines_count(self) -> None:
        sha, byte_len, line_count, n_files, _ = check_r4_baseline_details()
        self.assertEqual(n_files, 1)
        self.assertEqual(sha, P33_EXPECTED_SHA256)
        self.assertEqual(byte_len, P33_EXPECTED_BYTES)
        self.assertEqual(line_count, P33_EXPECTED_LINES)

    def test_t2_f11_02_r4_v1_v5_exact_baseline_vector(self) -> None:
        _, _, _, _, stats = check_r4_baseline_details()
        for folder, expected in PRIOR_VERSION_BASELINE.items():
            self.assertEqual(stats[folder], expected, f"Folder {folder} modified")

    def test_t2_f11_03_test_v5_e2e_unmodified(self) -> None:
        self.assertTrue(TEST_V5_PATH.exists())
        self.assertEqual(TEST_V5_PATH.stat().st_size, TEST_V5_EXPECTED_BYTES)
        self.assertNotIn("test_v5_e2e", read_utf8(Path(__file__).resolve()).split("TEST_V5_EXPECTED_BYTES")[1])

    def test_t2_f11_04_no_teamwork_metadata_in_v6(self) -> None:
        if V6_DIR.exists():
            for forbidden in ("PROJECT.md", "TEST_INFRA.md", "TEST_READY.md", "ORIGINAL_REQUEST.md"):
                self.assertFalse((V6_DIR / forbidden).exists(), f"{forbidden} must not be inside V6/")

    def test_t2_f11_05_require_path_strict_no_silent_skip(self) -> None:
        # Verify assert_v6_deliverable raises AssertionError (never SkipTest) when missing
        fake_tc = unittest.TestCase()
        nonexistent = REPO_ROOT / "__missing_require_path_probe__.md"
        raised = None
        try:
            assert_v6_deliverable(fake_tc, nonexistent, "M2", "Nonexistent Probe")
        except BaseException as exc:  # noqa: BLE001
            raised = exc
        self.assertIsInstance(raised, AssertionError)
        self.assertNotIsInstance(raised, unittest.SkipTest)
        self.assertIn("[M2 Deliverable Missing]", str(raised))
        # And succeeds cleanly on existing file
        self.assertEqual(
            assert_v6_deliverable(fake_tc, Path(__file__).resolve(), "M0", "Self"),
            Path(__file__).resolve(),
        )


@pytest.mark.tier2
class TestT2Feature12HardeningGuards(unittest.TestCase):
    """Tier 2 Guards for Feature #12: Hardening & Build Hygiene."""

    def test_t2_f12_01_no_zero_byte_files_in_v6(self) -> None:
        assert_v6_deliverable(self, V6_DIR, "M1", "V6 directory")
        files = [
            p
            for p in V6_DIR.rglob("*")
            if p.is_file()
            and p.suffix in {".tex", ".bib", ".pdf", ".py", ".md"}
            and not p.name.endswith("Notes.bib")
        ]
        self.assertGreater(len(files), 0)
        for f in files:
            self.assertGreater(f.stat().st_size, 0, f"Zero-byte file: {f}")

    def test_t2_f12_02_all_pdf_pages_have_fonts_and_text(self) -> None:
        import pymupdf

        for pdf in (V6_PRA_PDF, V6_ARXIV_PDF):
            assert_v6_deliverable(self, pdf, "M3", pdf.name)
            doc = pymupdf.open(str(pdf))
            try:
                for idx, page in enumerate(doc):
                    self.assertGreater(len(page.get_fonts()), 0, f"{pdf.name} page {idx+1} has no fonts")
                    self.assertGreater(len(page.get_text("text").strip()), 50, f"{pdf.name} page {idx+1} empty")
            finally:
                doc.close()

    def test_t2_f12_03_bbl_contains_all_cited_bibitems(self) -> None:
        for tex, bbl in ((V6_PRA_TEX, V6_PRA_BBL), (V6_ARXIV_TEX, V6_ARXIV_BBL)):
            cites = extract_citations(read_utf8(assert_v6_deliverable(self, tex, "M3", tex.name)))
            bbl_keys = parse_bbl_keys(read_utf8(assert_v6_deliverable(self, bbl, "M3", bbl.name)))
            self.assertTrue(cites.issubset(bbl_keys))

    def test_t2_f12_04_no_severe_latex_log_errors(self) -> None:
        for log_p in (V6_PRA_LOG, V6_ARXIV_LOG):
            txt = read_utf8(assert_v6_deliverable(self, log_p, "M3", log_p.name))
            self.assertNotRegex(txt, r"Emergency stop|! LaTeX Error|! Undefined control sequence|File .* not found")

    def test_t2_f12_05_r4_idempotency_after_checks(self) -> None:
        sha, byte_len, line_count, n_files, stats = check_r4_baseline_details()
        self.assertEqual((sha, byte_len, line_count, n_files), (P33_EXPECTED_SHA256, P33_EXPECTED_BYTES, P33_EXPECTED_LINES, 1))
        self.assertEqual(stats, PRIOR_VERSION_BASELINE)


# ===========================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS (10 PAIRWISE TESTS)
# ===========================================================================

@pytest.mark.tier3
class TestT3CrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Cross-feature pairwise integration & consistency checks."""

    def test_t3_01_pra_arxiv_math_and_table_sync(self) -> None:
        pra = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")))
        arx = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex")))
        for txt in (pra, arx):
            self.assertIn("0.5625", txt)
            self.assertIn("6.631.1", txt)
            self.assertRegex(txt, r"2p\s*\+\s*(?:\|\s*l\s*\||\\lvert\s*l\s*\\rvert|\\abs\{l\})\s*\+\s*1")
        # Table I sync
        t1_pra = extract_tabular_rows_matching(pra, lambda b: "0.5625" in b)
        t1_arx = extract_tabular_rows_matching(arx, lambda b: "0.5625" in b)
        self.assertGreaterEqual(len(t1_pra), 7)
        self.assertEqual(len(t1_pra), len(t1_arx))
        for rp, ra in zip(t1_pra, t1_arx):
            nums_p = [parse_latex_number(c) for c in rp]
            nums_a = [parse_latex_number(c) for c in ra]
            self.assertEqual(nums_p, nums_a)
        # Table II sync
        t2_pra = extract_tabular_rows_matching(pra, _is_table2_block)
        t2_arx = extract_tabular_rows_matching(arx, _is_table2_block)
        self.assertGreaterEqual(len(t2_pra), 6, "Table II missing in main_pra.tex")
        self.assertEqual(len(t2_pra), len(t2_arx), "Table II row count mismatch between PRA and arXiv")
        for rp, ra in zip(t2_pra, t2_arx):
            nums_p = [parse_latex_number(c) for c in rp]
            nums_a = [parse_latex_number(c) for c in ra]
            self.assertEqual(nums_p, nums_a, f"Table II numeric desync: {rp} vs {ra}")
        # Comparative Table III sync
        t3_pra = _extract_comparative_table_rows(pra)
        t3_arx = _extract_comparative_table_rows(arx)
        self.assertGreaterEqual(len(t3_pra), 4, "Comparative Table III missing in main_pra.tex")
        self.assertEqual(len(t3_pra), len(t3_arx), "Comparative Table III row count mismatch")
        for rp, ra in zip(t3_pra, t3_arx):
            self.assertEqual(rp, ra, f"Comparative Table III desync: {rp} vs {ra}")

    def test_t3_02_pra_arxiv_citations_figures_and_layout_diff(self) -> None:
        pra = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex"))
        arx = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex"))
        self.assertEqual(extract_citations(pra), extract_citations(arx))
        self.assertEqual(
            [Path(p).stem for p in extract_includegraphics_paths(pra)],
            [Path(p).stem for p in extract_includegraphics_paths(arx)],
        )
        pra_pages, _, _ = extract_pdf_text_pymupdf(assert_v6_deliverable(self, V6_PRA_PDF, "M3", "main_pra.pdf"))
        arx_pages, _, _ = extract_pdf_text_pymupdf(assert_v6_deliverable(self, V6_ARXIV_PDF, "M3", "main_arxiv.pdf"))
        self.assertLessEqual(pra_pages, 10)
        self.assertLessEqual(arx_pages, 16)
        self.assertLess(pra_pages, 35)
        self.assertLess(arx_pages, 35)

    def test_t3_03_scripts_metrics_vs_latex_tables(self) -> None:
        run_all = assert_v6_deliverable(self, V6_SCRIPTS_DIR / "run_all.py", "M2", "run_all.py")
        pra = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")))
        arx = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex")))
        with tempfile.TemporaryDirectory() as tmp:
            tmp_v6 = Path(tmp) / "V6"
            shutil.copytree(V6_SCRIPTS_DIR, tmp_v6 / "scripts")
            (tmp_v6 / "figures").mkdir(parents=True, exist_ok=True)
            proc = subprocess.run(
                [sys.executable, str(tmp_v6 / "scripts" / run_all.name)],
                cwd=str(tmp_v6 / "scripts"),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            _verify_scripts_numerical_outputs(self, V6_SCRIPTS_DIR, tmp_v6, proc.stdout)
        # Verify Table I & all 6 Table II rows in both .tex files against independent oracles
        for name, txt in (("main_pra.tex", pra), ("main_arxiv.tex", arx)):
            rows = extract_tabular_rows_matching(txt, lambda b: "0.5625" in b)
            self.assertGreaterEqual(len(rows), 7, f"Table I rows missing in {name}")
            data_rows_t1 = 0
            for row in rows:
                vals = [parse_latex_number(c) for c in row]
                if vals and vals[0] is not None and vals[0] > 0.0 and len(vals) >= 5:
                    data_rows_t1 += 1
                    ratio = vals[0]
                    for p_idx in range(4):
                        self.assertIsNotNone(vals[1 + p_idx], f"{name} Table I non-numeric cell at w/w0={ratio}")
                        expected = oracle_fidelity_exact(p_idx, 1, ratio)
                        self.assertAlmostEqual(
                            vals[1 + p_idx], expected, delta=1e-4,  # type: ignore[arg-type]
                            msg=f"{name} Table I mismatch at w/w0={ratio}, p={p_idx}",
                        )
            self.assertGreaterEqual(data_rows_t1, 7, f"{name} Table I had fewer than 7 valid data rows")
            _assert_table2_all_columns(self, txt, name)

    def test_t3_04_scripts_vs_generated_vector_figures(self) -> None:
        import pymupdf

        pra = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex"))
        arx = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex"))
        gen_src = read_utf8(assert_v6_deliverable(self, V6_SCRIPTS_DIR / "generate_figures.py", "M2", "generate_figures.py"))
        self.assertNotIn("2.0 * np.sqrt(2.0) - 0.04 * np.exp", gen_src)
        for tex_name, txt in (("main_pra.tex", pra), ("main_arxiv.tex", arx)):
            incs = extract_includegraphics_paths(txt)
            self.assertGreaterEqual(len(incs), 3, f"{tex_name} missing 3 figure includes")
            for rel in incs:
                fpath = V6_DIR / rel if (V6_DIR / rel).exists() else V6_FIGURES_DIR / Path(rel).name
                assert_v6_deliverable(self, fpath, "M2", f"Included figure {rel}")
                doc = pymupdf.open(str(fpath))
                try:
                    pix = doc[0].get_pixmap(dpi=72)
                    self.assertGreater(pix.width, 0)
                    self.assertGreater(pix.height, 0)
                finally:
                    doc.close()

    def test_t3_05_referee_reports_to_resolution_mapping(self) -> None:
        r1 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        r2 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        expected_ids = extract_referee_ids(r1, "R1") | extract_referee_ids(r2, "R2")
        _, rows = parse_markdown_mapping_rows(mp)
        mapped = {r[0].strip(): r for r in rows}
        self.assertEqual(set(mapped.keys()), expected_ids)
        for fid, row in mapped.items():
            self.assertNotIn("tbd", row[4].lower(), f"{fid} still has TBD location")
            self.assertNotIn("planned", row[5].lower(), f"{fid} still Planned")

    def test_t3_06_resolution_mapping_to_v6_latex(self) -> None:
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        pra = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex"))
        arx = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex"))
        bib_keys = {e["key"] for e in parse_bibtex_entries(read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib")))}
        pra_lbls = extract_labels(pra)
        arx_lbls = extract_labels(arx)
        pra_refs = set(re.findall(r"\\(?:eq)?ref\{([^}]+)\}", strip_tex_comments(pra)))
        arx_refs = set(re.findall(r"\\(?:eq)?ref\{([^}]+)\}", strip_tex_comments(arx)))
        self.assertEqual(pra_lbls, pra_refs)
        self.assertEqual(arx_lbls, arx_refs)
        _, rows = parse_markdown_mapping_rows(mp)
        pra_cites = extract_citations(pra)
        arx_cites = extract_citations(arx)
        checked_lbls = 0
        checked_keys = 0
        for row in rows:
            loc = row[4]
            for lbl in re.findall(r"\b(?:eq|sec|subsec|tab|fig|app|prop|thm|cor|rem):[A-Za-z0-9_:-]+\b", loc):
                checked_lbls += 1
                self.assertIn(lbl, pra_lbls)
                self.assertIn(lbl, arx_lbls)
            for key in re.findall(r"\b([A-Z][A-Za-z0-9_]+\d{4}[a-z]?)\b", loc):
                checked_keys += 1
                self.assertIn(key, bib_keys, f"Mapping BibTeX key {key} missing from references.bib")
                self.assertIn(key, pra_cites, f"Mapping BibTeX key {key} not cited in main_pra.tex")
                self.assertIn(key, arx_cites, f"Mapping BibTeX key {key} not cited in main_arxiv.tex")
        self.assertGreater(checked_lbls, 0)
        self.assertGreater(checked_keys, 0)
        # Verify numeric metadata claims inside RESOLUTION_MAPPING.md
        pra_wc = len(extract_abstract_text(pra).split())
        arx_wc = len(extract_abstract_text(arx).split())
        self.assertEqual(pra_wc, arx_wc)
        for wc_claim in re.findall(r"Abstract \((\d+) words", mp):
            self.assertEqual(int(wc_claim), pra_wc)
        pra_pages, _, _ = extract_pdf_text_pymupdf(assert_v6_deliverable(self, V6_PRA_PDF, "M3", "main_pra.pdf"))
        arx_pages, _, _ = extract_pdf_text_pymupdf(assert_v6_deliverable(self, V6_ARXIV_PDF, "M3", "main_arxiv.pdf"))
        for pg_claim in re.findall(r"main_pra\.pdf \((\d+) pp\)", mp):
            self.assertEqual(int(pg_claim), pra_pages)
        for pg_claim in re.findall(r"main_arxiv\.pdf \((\d+) pp\)", mp):
            self.assertEqual(int(pg_claim), arx_pages)
        for stem, tex_src in (("pra", pra), ("arxiv", arx)):
            remark_lines = [i for i, ln in enumerate(tex_src.splitlines(), 1) if r"\newtheorem{remark}" in ln]
            self.assertEqual(len(remark_lines), 1)
            for ln_end in re.findall(rf"main_{stem}\.tex L1--(\d+)", mp):
                self.assertEqual(int(ln_end), remark_lines[0])
        for lbl_cnt in re.findall(r"0 unused \\label targets out of (\d+)", mp):
            self.assertEqual(int(lbl_cnt), len(pra_lbls))
            self.assertEqual(int(lbl_cnt), len(arx_lbls))

    def test_t3_07_bib_tex_bbl_pdf_synchronization(self) -> None:
        bib_entries = parse_bibtex_entries(read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib")))
        bib_keys = {e["key"] for e in bib_entries}
        c_pra = extract_citations(read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")))
        c_arx = extract_citations(read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex")))
        self.assertEqual(c_pra, bib_keys)
        self.assertEqual(c_arx, bib_keys)
        for bbl in (V6_PRA_BBL, V6_ARXIV_BBL):
            self.assertEqual(parse_bbl_keys(read_utf8(assert_v6_deliverable(self, bbl, "M3", bbl.name))), bib_keys)
        for pdf in (V6_PRA_PDF, V6_ARXIV_PDF):
            _, full_txt, _ = extract_pdf_text_pymupdf(assert_v6_deliverable(self, pdf, "M3", pdf.name))
            self.assertNotRegex(full_txt, PDF_UNRESOLVED_MARK_RE)

    def test_t3_08_fixed_bibliography_and_optics_claims(self) -> None:
        bib_txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib"))
        pra = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex"))
        arx = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex"))
        for txt in (bib_txt, pra, arx):
            self.assertNotIn("aleman2023transmission", txt)
        for tex in (pra, arx):
            self.assertIn("6.631.1", tex)
            self.assertNotIn("6.643.2", tex)
        entries = parse_bibtex_entries(bib_txt)
        reddy = [e for e in entries if "055602" in e["fields"].get("pages", "")]
        self.assertEqual(len(reddy), 1)
        self.assertIn("non-diffracting speckles of a perfect vortex beam", reddy[0]["fields"]["title"].lower())

    def test_t3_09_c0_norm_and_gamma_matrix_consistency(self) -> None:
        pra = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")))
        arx = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex")))
        denom_sqrt = (
            r"(?:\\sqrt\s*\{\s*G_\{?n\s*,?\s*n\}?\s*(?:\\,|\s|\\cdot)?\s*G_\{?m\s*,?\s*m\}?\s*\}"
            r"|\\sqrt\s*\{\s*G_\{?n\s*,?\s*n\}?\s*\}\s*(?:\\,|\s|\\cdot)?\s*\\sqrt\s*\{\s*G_\{?m\s*,?\s*m\}?\s*\})"
        )
        norm_frac = (
            rf"(?:\\(?:d|t)?frac\s*\{{\s*G_\{{?n\s*,?\s*m\}}?\s*\}}\s*\{{\s*{denom_sqrt}\s*\}}"
            rf"|G_\{{?n\s*,?\s*m\}}?\s*/\s*(?:\(\s*)?{denom_sqrt}(?:\s*\))?)"
        )
        gamma_norm_re = re.compile(
            rf"\\gamma_\{{?n\s*,?\s*m\}}?\s*=\s*(?:[^.\n]{{0,80}}=\s*)?{norm_frac}"
        )
        for txt in (pra, arx):
            self.assertRegex(txt, gamma_norm_re)
            self.assertRegex(txt, r"1\.64[45]")
            self.assertRegex(txt, r"1\.04[01]")

    def test_t3_10_p_kmax_projection_and_tikhonov_bias_consistency(self) -> None:
        pra = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")))
        arx = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex")))
        for name, txt in (("main_pra.tex", pra), ("main_arxiv.tex", arx)):
            self.assertRegex(
                txt,
                r"(?:\\mathcal\{P\}|P)_\{?(?:\\mathcal\{H\}_\{?)?k_\{?(?:\\max|\\(?:text|mathrm|textrm|operatorname)\{max\})\}?\}?",
            )
            self.assertRegex(txt, r"\\(?:wide)?tilde\{G\}_w(?:\^2\s*\(\s*k\s*\)|\(\s*k\s*\)\^2|\^2)\s*\+\s*\\alpha")
            _assert_no_positive_distortionless_alpha(self, txt, name)


# ===========================================================================
# TIER 4: REAL-WORLD END-TO-END ACCEPTANCE SCENARIOS (6 SCENARIOS S1-S6)
# ===========================================================================

@pytest.mark.tier4
class TestT4RealWorldAcceptanceScenarios(unittest.TestCase):
    """Tier 4: Full multi-step production, math, PDF, R4, and traceability scenarios."""

    def test_t4_s1_isolated_pdflatex_bibtex_clean_build_pra_and_arxiv(self) -> None:
        assert_v6_deliverable(self, V6_PRA_TEX, "M3", "PRA LaTeX source")
        assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "arXiv LaTeX source")
        assert_v6_deliverable(self, V6_BIB, "M3", "Bibliography database")
        for fig in V6_FIG_PATHS:
            assert_v6_deliverable(self, fig, "M2", f"Figure {fig.name}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_v6 = Path(tmp) / "V6"
            shutil.copytree(V6_DIR, tmp_v6)
            for ext in (".pdf", ".aux", ".bbl", ".blg", ".log", ".out", ".toc"):
                for artifact in tmp_v6.glob(f"*{ext}"):
                    artifact.unlink()

            for stem in ("main_pra", "main_arxiv"):
                cmds = [
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
                    ["bibtex", stem],
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
                ]
                for cmd in cmds:
                    proc = subprocess.run(
                        cmd,
                        cwd=str(tmp_v6),
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=180,
                        check=False,
                    )
                    self.assertEqual(
                        proc.returncode,
                        0,
                        f"{' '.join(cmd)} failed ({proc.returncode}):\n{proc.stdout[-1500:]}",
                    )

                log_txt = read_utf8(tmp_v6 / f"{stem}.log")
                blg_txt = read_utf8(tmp_v6 / f"{stem}.blg")
                self.assertNotIn("! LaTeX Error", log_txt)
                self.assertNotIn("Emergency stop", log_txt)
                self.assertNotRegex(log_txt, r"Citation `[^']+' on page \d+ undefined")
                self.assertNotRegex(log_txt, r"Reference `[^']+' on page \d+ undefined")
                self.assertNotIn("There were undefined", log_txt)
                self.assertNotIn("I didn't find a database entry", blg_txt)

            pra_pages, _, _ = extract_pdf_text_pymupdf(tmp_v6 / "main_pra.pdf")
            arx_pages, _, _ = extract_pdf_text_pymupdf(tmp_v6 / "main_arxiv.pdf")
            self.assertLessEqual(pra_pages, 10)
            self.assertLessEqual(arx_pages, 16)
            self.assertLess(pra_pages, 35)
            self.assertLess(arx_pages, 35)

    def test_t4_s2_isolated_scripts_execution_and_first_principles_check(self) -> None:
        run_all = assert_v6_deliverable(self, V6_SCRIPTS_DIR / "run_all.py", "M2", "run_all.py")
        pra_txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")))

        with tempfile.TemporaryDirectory() as tmp:
            tmp_v6 = Path(tmp) / "V6"
            shutil.copytree(V6_SCRIPTS_DIR, tmp_v6 / "scripts")
            (tmp_v6 / "figures").mkdir(parents=True, exist_ok=True)
            proc = subprocess.run(
                [sys.executable, str(tmp_v6 / "scripts" / run_all.name)],
                cwd=str(tmp_v6 / "scripts"),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, f"run_all.py failed:\n{proc.stdout}\n{proc.stderr}")
            _verify_scripts_numerical_outputs(self, V6_SCRIPTS_DIR, tmp_v6, proc.stdout)

            import pymupdf

            for fig_name in V6_FIG_NAMES:
                fpath = tmp_v6 / "figures" / fig_name
                self.assertTrue(fpath.exists(), f"run_all.py did not generate {fig_name}")
                self.assertGreater(fpath.stat().st_size, 10240)
                self.assertTrue(fpath.read_bytes().startswith(b"%PDF-"))
                doc = pymupdf.open(str(fpath))
                try:
                    self.assertEqual(len(doc), 1)
                finally:
                    doc.close()

        # First-principles verification against PRA LaTeX Table I and all 6 Table II rows
        for p, l, R, w, w0 in [(0, 1, 1.1, 0.35, 1.0), (1, 1, 1.0, 0.25, 1.0), (2, -2, 0.8, 0.3, 1.0), (3, 1, 1.3, 0.2, 1.0)]:
            self.assertLess(abs(oracle_c_lp_closed(p, l, R, w, w0) - oracle_c_lp_quad(p, l, R, w, w0)), 1e-12)
        t1_rows = extract_tabular_rows_matching(pra_txt, lambda b: "0.5625" in b)
        self.assertGreaterEqual(len(t1_rows), 7)
        data_rows_t1 = 0
        for row in t1_rows:
            vals = [parse_latex_number(c) for c in row]
            if vals and vals[0] is not None and vals[0] > 0.0 and len(vals) >= 5:
                data_rows_t1 += 1
                for p_idx in range(4):
                    self.assertIsNotNone(vals[1 + p_idx])
                    self.assertAlmostEqual(
                        vals[1 + p_idx], oracle_fidelity_exact(p_idx, 1, vals[0]), delta=1e-4  # type: ignore[arg-type]
                    )
        self.assertGreaterEqual(data_rows_t1, 7)
        _assert_table2_all_columns(self, pra_txt, "main_pra.tex")

    def test_t4_s3_full_pdf_audit_pypdf_pymupdf_poppler(self) -> None:
        import pymupdf
        from pypdf import PdfReader

        for pdf, max_pages in ((V6_PRA_PDF, 10), (V6_ARXIV_PDF, 16)):
            assert_v6_deliverable(self, pdf, "M3", f"Compiled PDF {pdf.name}")
            info = run_pdfinfo(pdf)
            self.assertEqual(info.get("Encrypted", "no").lower(), "no")

            reader = PdfReader(str(pdf))
            self.assertLessEqual(len(reader.pages), max_pages)

            doc = pymupdf.open(str(pdf))
            try:
                self.assertLessEqual(len(doc), max_pages)
                xobj_count = 0
                for idx, page in enumerate(doc):
                    self.assertGreater(len(page.get_fonts()), 0, f"{pdf.name} page {idx+1} missing fonts")
                    self.assertGreater(len(page.get_text("text").strip()), 50)
                    pix = page.get_pixmap(dpi=72)
                    self.assertGreater(pix.width, 0)
                    xobj_count += len(page.get_xobjects())
                self.assertGreaterEqual(xobj_count, 3, f"{pdf.name} missing embedded vector figure XObjects")
            finally:
                doc.close()

            poppler_txt = run_pdftotext(pdf)
            for idx in ("1", "2", "3"):
                self.assertRegex(poppler_txt, rf"Fig\.\s*{idx}|FIG\.\s*{idx}")
            self.assertNotRegex(poppler_txt, PDF_UNRESOLVED_MARK_RE)
            self.assertNotRegex(poppler_txt, r"\\cite\{|\\ref\{")
            self.assertIn("Ayala", poppler_txt)
            self.assertIn("Gemini", poppler_txt)
            self.assertIn("Antigravity", poppler_txt)
            for pat in PROHIBITED_INTERNAL_REGEXES:
                self.assertNotRegex(poppler_txt, pat, f"Leaked pattern {pat} in {pdf.name}")
            self.assertRegex(poppler_txt, r"(?i)(?:ring[- ]?core|RCF|SDM)")
            self.assertRegex(poppler_txt, r"(?i)(?:POVM|SPDC|CHSH|tomography)")

    def test_t4_s4_r4_baseline_integrity_audit(self) -> None:
        sha, byte_len, line_count, n_files, stats = check_r4_baseline_details()
        self.assertEqual(n_files, 1, "Extra files created inside p3_3/")
        self.assertEqual(sha, P33_EXPECTED_SHA256)
        self.assertEqual(byte_len, P33_EXPECTED_BYTES)
        self.assertEqual(line_count, P33_EXPECTED_LINES)
        self.assertEqual(stats, PRIOR_VERSION_BASELINE)
        self.assertTrue(TEST_V5_PATH.exists())
        self.assertEqual(TEST_V5_PATH.stat().st_size, TEST_V5_EXPECTED_BYTES)

    def test_t4_s5_referee_to_publication_end_to_end_traceability(self) -> None:
        r1 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_1, "M1", "Referee 1 Report"))
        r2 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        mp = read_utf8(assert_v6_deliverable(self, V6_MAPPING, "M1", "Resolution Mapping Ledger"))
        bib = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib"))
        pra = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex"))
        arx = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex"))
        pra_pdf = assert_v6_deliverable(self, V6_PRA_PDF, "M3", "main_pra.pdf")
        arx_pdf = assert_v6_deliverable(self, V6_ARXIV_PDF, "M3", "main_arxiv.pdf")

        expected_ids = extract_referee_ids(r1, "R1") | extract_referee_ids(r2, "R2")
        _, rows = parse_markdown_mapping_rows(mp)
        mapped = {r[0].strip(): r for r in rows}
        self.assertEqual(set(mapped.keys()), expected_ids)
        for fid, row in mapped.items():
            self.assertNotIn("tbd", row[4].lower(), f"{fid} unresolved V6 location")
            self.assertNotIn("planned", row[5].lower(), f"{fid} still Planned")

        for pdf in (pra_pdf, arx_pdf):
            _, pdf_txt, _ = extract_pdf_text_pymupdf(pdf)
            self.assertIn("6.631.1", pdf_txt)
            self.assertNotIn("6.643.2", pdf_txt)
            self.assertIn("0.5625", pdf_txt)
            self.assertNotIn("0.57033", pdf_txt)
            self.assertRegex(pdf_txt, r"1\.64[45]")
            self.assertRegex(pdf_txt, r"1\.17[12]")
            self.assertRegex(pdf_txt, r"1\.04[01]")
        for name, tex_src in (("main_pra.tex", pra), ("main_arxiv.tex", arx)):
            _assert_no_positive_distortionless_alpha(self, strip_tex_comments(tex_src), name)
        for artifact in (bib, pra, arx):
            self.assertNotIn("aleman2023transmission", artifact)

    def test_t4_s6_cross_manuscript_synchronization_and_arxiv_portability(self) -> None:
        bib = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib"))
        pra = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex"))
        arx = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex"))
        pra_pdf = assert_v6_deliverable(self, V6_PRA_PDF, "M3", "main_pra.pdf")
        arx_pdf = assert_v6_deliverable(self, V6_ARXIV_PDF, "M3", "main_arxiv.pdf")

        bib_keys = {e["key"] for e in parse_bibtex_entries(bib)}
        self.assertEqual(extract_citations(pra), bib_keys)
        self.assertEqual(extract_citations(arx), bib_keys)

        for token in ("ayala.phys.ds@gmail.com", "0009-0003-7348-3883", "Cauquenes"):
            self.assertIn(token, pra)
            self.assertIn(token, arx)
        for pdf in (pra_pdf, arx_pdf):
            _, txt, _ = extract_pdf_text_pymupdf(pdf)
            self.assertIn("0009-0003-7348-3883", txt)
            self.assertIn("Ayala", txt)
        for tex in (pra, arx):
            self.assertNotRegex(tex, r"[A-Za-z]:\\|/(?:Users|home)/|\.\./")


# ===========================================================================
# TIER 5: WHITE-BOX ADVERSARIAL COVERAGE HARDENING (5 TESTS)
# ===========================================================================

@pytest.mark.tier5
class TestT5WhiteBoxHardening(unittest.TestCase):
    """Tier 5: White-box adversarial tests for physics, tables, PDFs, scripts, and guards."""

    def test_t5_01_table2_all_columns_and_worked_prose_values(self) -> None:
        pra = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")))
        arx = strip_tex_comments(read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex")))
        for name, txt in (("main_pra.tex", pra), ("main_arxiv.tex", arx)):
            _assert_table2_all_columns(self, txt, name)

        # Worked LG_{2,1} Tikhonov prose values vs oracle_tikhonov_mse
        u_max = 72.0  # (w*k_max)^2 / (2*(w/w0)^2) = 9 / (2*0.0625)
        b2_opt, var_opt, mse_opt = oracle_tikhonov_mse(2, 1, 0.25, 1.0, u_max, 0.01 / u_max, 0.04902)
        self.assertAlmostEqual(b2_opt, 0.01326, delta=2e-5)
        self.assertAlmostEqual(var_opt, 0.02155, delta=2e-5)
        self.assertAlmostEqual(mse_opt, 0.03481, delta=2e-5)

        # N=120 counterexample & near-core breakdown vs oracle_gram_matrices
        _, _, kG_120, kg_120 = oracle_gram_matrices([2.0 + i * 1.0 for i in range(120)], 0.5, 1)
        self.assertAlmostEqual(kG_120, 80.02, delta=0.05)
        self.assertAlmostEqual(kg_120, 1.741, delta=0.002)
        _, g_core, _, _ = oracle_gram_matrices([0.1, 1.1], 0.5, 1)
        self.assertAlmostEqual(100.0 * abs(float(g_core[0, 1])), 34.76, delta=0.02)

        # Gouy IC-POVM & SPDC oracle values
        r1, r5, lmax, lmin_f, crb_r, crb_nr = oracle_gouy_ic_povm_d4()
        self.assertEqual((r1, r5), (7, 16))
        kpvb, klg, spvb, slg = oracle_spdc_iris_transmission_and_chsh(1.0)
        self.assertAlmostEqual(kpvb, 0.4999, delta=2e-4)
        self.assertAlmostEqual(klg, 0.2642, delta=2e-4)
        self.assertAlmostEqual(spvb, 2.8284, delta=2e-4)
        self.assertAlmostEqual(slg, 2.0008, delta=2e-4)

        for name, txt in (("main_pra.tex", pra), ("main_arxiv.tex", arx)):
            for val_str in (
                "9.002", "0.03481", "0.01326", "0.02155", "0.04902",
                "80.02", "1.741", "34.76",
                f"{lmax:.4f}", f"{lmin_f:.4f}", f"{crb_r:.2f}", f"{crb_nr:.2f}",
                "0.4999", "0.4996", "0.4991", "0.4984",
                "0.2642", "0.0803", "0.0190", "0.0037",
                "2.8284", "2.0532", "2.0008",
            ):
                self.assertIn(val_str, txt, f"Missing verified numeric claim '{val_str}' in {name}")

    def test_t5_02_parseval_2f_power_scaling_and_gouy_icpovm_oracle(self) -> None:
        # Parseval: P_in = ||Phi_{l,R}||^2 scales as w^-1 (not w^-2) for R >> w
        p_w1 = oracle_pvb_self_overlap(1.0, 0.001, 1)
        p_w2 = oracle_pvb_self_overlap(1.0, 0.002, 1)
        self.assertAlmostEqual(p_w1 / p_w2, 2.0, places=3)

        for path in (V6_PRA_TEX, V6_ARXIV_TEX):
            txt = strip_tex_comments(read_utf8(assert_v6_deliverable(self, path, "M3", path.name)))
            self.assertNotRegex(txt, r"input\s+power[^.\n]{0,40}\\propto\s*w\^\{?-2\}?")
            self.assertRegex(txt, r"input\s+power[^.\n]{0,60}\\propto\s*w\^\{?-1\}?")
            self.assertRegex(txt, r"input\s+(?:\$?\\mathrm\{SNR\}\$?|SNR)\s*=\s*20")

        r1, r5, lmax, lmin_f, crb_r, crb_nr = oracle_gouy_ic_povm_d4()
        self.assertEqual(r1, 7)
        self.assertEqual(r5, 16)
        self.assertLess(lmax, 1.0)
        self.assertAlmostEqual(lmax, 0.9050, delta=5e-4)
        self.assertAlmostEqual(lmin_f, 0.1261, delta=5e-4)
        self.assertAlmostEqual(crb_r, 41.80, delta=0.02)
        self.assertAlmostEqual(crb_nr, 42.96, delta=0.02)

    def test_t5_03_pvb_physics_narrow_width_and_edge_guards(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertAlmostEqual(
                oracle_c_lp_quad(2, 1, 2.0, 0.01, 1.0),
                oracle_c_lp_closed(2, 1, 2.0, 0.01, 1.0),
                delta=1e-12,
            )
            self.assertAlmostEqual(
                oracle_c_lp_quad(2, 1, 1.0, 1e-4, 1.0),
                oracle_c_lp_closed(2, 1, 1.0, 1e-4, 1.0),
                delta=1e-12,
            )
            self.assertAlmostEqual(
                oracle_c_lp_quad(0, 0, 1.5, 1e-8, 1.0),
                oracle_c_lp_closed(0, 0, 1.5, 1e-8, 1.0),
                delta=1e-12,
            )
            self.assertEqual(oracle_c_lp_quad(0, 0, np.nan, 1e-8, 1.0), 0.0)
            self.assertTrue(math.isfinite(oracle_pvb_self_overlap(5.0, 1e-4, 1)))

            # Gap 1 oracle checks (rescaled washout fidelity + non-finite/w<=0 guards)
            f_100 = oracle_fidelity_exact(0, 0, 100.0)
            self.assertAlmostEqual(f_100, (1.0 + 2.0 * 1e4) / ((1.0 + 1e4) ** 2), delta=1e-14)
            self.assertTrue(0.0 <= f_100 <= 1.0)
            self.assertLessEqual(oracle_fidelity_exact(2, 1, 100.0), oracle_fidelity_exact(2, 1, 50.0))
            self.assertEqual(oracle_fidelity_exact(0, 0, 0.0), 1.0)
            self.assertEqual(oracle_fidelity_exact(2, 1, np.inf), 0.0)
            self.assertEqual(oracle_fidelity_exact(2, 1, np.nan), 0.0)

            # Gap 2 oracle checks (p > 4 mpmath parity + non-finite / far-tail R)
            for p_t, l_t, R_t, w_t, w0_t in (
                (12, 5, 1.5, 1.0, 1.0),
                (15, 1, 1.5, 1.0, 1.0),
                (20, 20, 5.0, 0.25, 1.0),
                (20, 1, 1.5, 1.0, 1.0),
            ):
                with mp.workdps(80):
                    al_t = abs(l_t)
                    Rm, wm, w0m = mp.mpf(R_t), mp.mpf(w_t), mp.mpf(w0_t)
                    dw = w0m ** 2 + wm ** 2
                    pref_m = 2 * mp.sqrt(mp.factorial(p_t) / mp.factorial(p_t + al_t)) * mp.power(2, mp.mpf(al_t) / 2) * (Rm ** al_t) * (w0m ** (al_t + 1)) / (dw ** (al_t + 1)) * mp.exp(-(Rm ** 2) / dw)
                    eta_m = 2 * wm ** 2 / dw
                    z_m = (Rm ** 2 * w0m ** 2) / (wm ** 2 * dw)
                    ref_m = float(pref_m * sum(((-1) ** m) * mp.binomial(p_t + al_t, p_t - m) * (eta_m ** m) * mp.laguerre(m, al_t, -z_m) for m in range(p_t + 1)))
                got_m = oracle_c_lp_closed(p_t, l_t, R_t, w_t, w0_t)
                self.assertLess(abs(got_m - ref_m) / max(abs(ref_m), 1e-300), 1e-11)
            for bad_r in (1e300, np.inf, -np.inf, np.nan):
                self.assertEqual(oracle_c_lp_closed(0, 1, bad_r, 0.25, 1.0), 0.0)
                self.assertEqual(oracle_c_lp_closed(15, 1, bad_r, 0.25, 1.0), 0.0)

            # Gap 3 & Gap 8 oracle checks (SPDC iris R_iris<=0, oracle_pvb_radial, oracle_lg_radial, oracle_gram_matrices)
            kp0, kl0, sp0, sl0 = oracle_spdc_iris_transmission_and_chsh(0.0)
            self.assertEqual((kp0, kl0, sp0, sl0), (0.0, 0.0, 2.0, 2.0))
            self.assertTrue(math.isfinite(oracle_pvb_radial(1e300, 1e300, 1e-8, 0)))
            self.assertEqual(oracle_pvb_radial(np.inf, np.inf, 1e-8, 0), 0.0)
            self.assertEqual(oracle_lg_radial(1e300, 2, 1, 1.0), 0.0)
            self.assertEqual(oracle_lg_radial(np.inf, 2, 1, 1.0), 0.0)
            G0, g0, kG0, kg0 = oracle_gram_matrices([0.0], 1e-8, 1)
            self.assertTrue(np.all(np.isfinite(G0)) and np.allclose(g0, np.ones((1, 1))) and math.isinf(kG0) and kg0 == 1.0)
            Gh, gh, kGh, kgh = oracle_gram_matrices([1e300, 1e300], 1e-8, 0)
            self.assertTrue(np.all(np.isfinite(Gh)) and np.allclose(gh, np.ones((2, 2))) and math.isinf(kgh))
            Gi, gi, _, _ = oracle_gram_matrices([np.inf, 1.0], 1e-8, 0)
            self.assertTrue(np.all(np.isfinite(Gi)) and np.allclose(gi, np.eye(2)))

            # Iteration 5 oracle regression guards (r5_1 + r5_2 Gaps 1-8)
            _, g_s1, _, _ = oracle_gram_matrices([1e-10, 2e-10], 1.0, 20)
            self.assertTrue(np.allclose(g_s1, np.ones((2, 2)), atol=1e-14))
            _, g_s2, _, _ = oracle_gram_matrices([1e-6, 2e-6], 100.0, 20)
            self.assertTrue(np.allclose(g_s2, np.ones((2, 2)), atol=1e-14))
            _, g_mix, _, _ = oracle_gram_matrices([1e-10, 1.0], 1.0, 20)
            self.assertAlmostEqual(float(g_mix[0, 1]), 0.9940668992020802, delta=1e-12)

            for p_q, l_q, R_q, w_q, w0_q in (
                (2, 1, 1.0, 1.0, 1e-4),
                (2, 1, 1.0, 100.0, 1e-3),
                (0, 0, 1.0, 100.0, 1e-4),
                (0, 0, 1.0, 100.0, 1e-6),
                (2, 1, 1.0, 100.0, 1e-8),
            ):
                oq = oracle_c_lp_quad(p_q, l_q, R_q, w_q, w0_q)
                oc = oracle_c_lp_closed(p_q, l_q, R_q, w_q, w0_q)
                self.assertLess(abs(oq - oc) / max(abs(oc), 1e-300), 1e-11)

            self.assertAlmostEqual(
                oracle_spdc_iris_transmission_and_chsh(3.2e-4, 1e-12, 1e-4, -20, 1)[0],
                0.4834676036074702,
                delta=1e-11,
            )
            self.assertAlmostEqual(
                oracle_spdc_iris_transmission_and_chsh(700.0, 1.0, 100.0, 100, 1)[0],
                0.394245631751,
                delta=1e-11,
            )
            with self.assertRaises(ValueError):
                oracle_spdc_iris_transmission_and_chsh(1.0, 0.0, 0.5, 1, 1)

            for w_nar in (1e-160, 1e-200):
                c_nar = oracle_c_lp_closed(2, 1, 1.5, w_nar, 1.0)
                q_nar = oracle_c_lp_quad(2, 1, 1.5, w_nar, 1.0)
                self.assertAlmostEqual(c_nar, q_nar, delta=1e-12)

            lg_hi = oracle_lg_radial(np.array([0.0, 1.0, 10.0, 30.0]), 200, 200, 1.0)
            self.assertTrue(np.all(np.isfinite(lg_hi)) and lg_hi[0] == 0.0 and lg_hi[2] > 0.0)

            A_fb, B_fb, k_fb = oracle_frame_bounds(1e2, 1e2)
            self.assertEqual((A_fb, B_fb), (0.0, 1.0))
            self.assertTrue(math.isinf(k_fb))
            b_t0, v_t0, m_t0 = oracle_tikhonov_mse(2, 1, 1.0, 1.0, 1000.0, 0.01, 0.0)
            self.assertEqual(b_t0, 0.0)
            self.assertTrue(math.isinf(v_t0) and math.isinf(m_t0))
            b_t1, v_t1, m_t1 = oracle_tikhonov_mse(100, 100, 0.25, 1.0, 72.0, 0.01, 0.01)
            self.assertTrue(math.isfinite(b_t1) and math.isfinite(v_t1) and math.isfinite(m_t1))

            ks_nar = oracle_frame_kernel_sum(1.0, 0.1, 1.0, 0.2, 1e-5)
            self.assertTrue(math.isfinite(ks_nar))
            ks_mod = oracle_frame_kernel_sum(1.0, 0.0, 1.0, 0.1, 0.2, l_max=35)
            gk_mod = oracle_gaussian_kernel_2d(1.0, 0.0, 1.0, 0.1, 0.2)
            self.assertLess(abs(ks_mod - gk_mod) / gk_mod, 1e-8)
            conv_nar = oracle_polar_conv_radial(1.0, 2, 1, 1e-5, 1.0)
            synth_nar = oracle_frame_synthesis_radial(1.0, 2, 1, 1e-5, 1.0)
            self.assertLess(abs(conv_nar - synth_nar) / max(abs(synth_nar), 1e-300), 1e-9)

        code = (
            "import math, sys, warnings; "
            f"sys.path.insert(0, {repr(str(V6_SCRIPTS_DIR))}); "
            "import mpmath as mp, numpy as np, pvb_physics as pp; "
            "warnings.simplefilter('error'); "
            "assert abs(pp.c_lp_quad(2.0, 2, 1, 0.01, 1.0) - pp.c_lp_closed_form(2.0, 2, 1, 0.01, 1.0)) < 1e-10; "
            "assert abs(pp.c_lp_quad(2.0, 2, 1, 0.001, 1.0) - pp.c_lp_closed_form(2.0, 2, 1, 0.001, 1.0)) < 1e-10; "
            "assert abs(pp.c_lp_quad(2.0, 2, 1, 0.0001, 1.0) - pp.c_lp_closed_form(2.0, 2, 1, 0.0001, 1.0)) < 1e-10; "
            "q5 = pp.c_lp_quad(5.0, 2, 1, 1e-4, 1.0); "
            "c5 = pp.c_lp_closed_form(5.0, 2, 1, 1e-4, 1.0); "
            "assert math.isfinite(q5) and q5 > 0.0 and abs(q5 - c5) < 1e-12; "
            # Gap 5: ultra-narrow ring w=1e-8 & non-finite bounds
            "assert abs(pp.c_lp_quad(1.5, 0, 0, 1e-8, 1.0) - pp.c_lp_closed_form(1.5, 0, 0, 1e-8, 1.0)) < 1e-12; "
            "assert pp.c_lp_quad(np.nan, 0, 0, 1e-8, 1.0) == 0.0; "
            "assert pp._split_ring_quad(lambda r: r, 0.0, np.inf, np.nan, 1e-8) == 0.0; "
            # Gap 1: rescaled nodal_washout_fidelity & nodal_washout_p0_closed
            "f100 = pp.nodal_washout_fidelity(0, 0, 100.0); p0_100 = pp.nodal_washout_p0_closed(0, 100.0); "
            "assert 0.0 <= f100 <= 1.0 and abs(f100 - p0_100) < 1e-12; "
            "assert 0.0 <= pp.nodal_washout_fidelity(2, 1, 100.0) <= pp.nodal_washout_fidelity(2, 1, 50.0) <= 1.0; "
            "assert pp.nodal_washout_fidelity(0, 0, 0.0) == 1.0 and pp.nodal_washout_fidelity(2, 1, np.inf) == 0.0 and pp.nodal_washout_fidelity(2, 1, np.nan) == 0.0; "
            # Gap 3: pvb_iris_transmission narrow/underflow/huge/nan
            "assert abs(pp.pvb_iris_transmission(1.0, 1.0, 0.002, 1) - 0.5) < 1e-4; "
            "assert abs(pp.pvb_iris_transmission(1.0, 1.0, 0.0005, 1) - 0.5) < 1e-4; "
            "assert abs(pp.pvb_iris_transmission(5.0, 5.0, 1e-4, 1) - 0.5) < 1e-4; "
            "t_uf = pp.pvb_iris_transmission(1e-12, 1e-12, 1e-4, -20); "
            "assert math.isfinite(t_uf) and 0.0 <= t_uf <= 1.0; "
            "assert abs(pp.pvb_iris_transmission(1e-12, 1e-12, 1e-14, -20) - 0.5) < 1e-3; "
            "assert abs(pp.pvb_iris_transmission(1e300, 1e300, 1.0, 1) - 0.5) < 1e-12; "
            "assert pp.pvb_iris_transmission(1e-12, np.nan, 1e-8, 0) == 0.0; "
            # Gap 6: pvb_radial & pvb_gram_* overflow/non-finite guards
            "g5 = pp.pvb_gram_normalized([5.0, 5.0001], 1, 1e-4); "
            "assert np.all(np.isfinite(g5)) and abs(g5[0, 1] - math.exp(-0.5)) < 1e-7; "
            "assert pp.pvb_radial(1e300, 1, 2.0, 0.001) == 0.0 and pp.pvb_radial(np.inf, 1, 2.0, 0.001) == 0.0; "
            "assert math.isfinite(pp.pvb_radial(1e300, 0, 1e300, 1e-8)) and pp.pvb_radial(np.inf, 0, np.inf, 1e-8) == 0.0; "
            "assert np.allclose(pp.pvb_gram_normalized([1e300, 1e300], 0, 1e-8), np.ones((2, 2))); "
            "assert np.allclose(pp.pvb_gram_normalized([np.inf, 1.0], 0, 1e-8), np.eye(2)); "
            "assert pp.lg_radial(1e300, 2, 1, 1.0) == 0.0 and pp.lg_radial(np.inf, 2, 1, 1.0) == 0.0; "
            # Gap 7: lg0l_iris_transmission, FT helpers, laguerre_spectral_density
            "assert pp.lg0l_iris_transmission(1e300, 100.0, 1) == 1.0 and pp.lg0l_iris_transmission(-np.inf, 100.0, 1) == 0.0; "
            "assert pp.pvb_2d_ft_radial(1e300, 1, 1.0, 0.5) == 0j and pp.pvb_2d_ft_radial(np.inf, 1, 1.0, 0.5) == 0j; "
            "assert pp.lg_2d_ft_radial(1e300, 2, 1, 1.0) == 0j and pp.lg_2d_ft_radial(np.inf, 2, 1, 1.0) == 0j; "
            "assert pp.weber_fourier_multiplier(1e300, 0.5) == 0.0 and pp.weber_fourier_multiplier(np.nan, 0.5) == 0.0; "
            "assert pp.laguerre_spectral_density(1e300, 2, 1) == 0.0 and pp.laguerre_spectral_density(np.inf, 2, 1) == 0.0\n"
            "def mp_clp(R, p, l, w, w0):\n"
            "  with mp.workdps(80):\n"
            "    al = abs(l); Rm, wm, w0m = mp.mpf(R), mp.mpf(w), mp.mpf(w0); dw = w0m**2 + wm**2\n"
            "    pref = 2 * mp.sqrt(mp.factorial(p)/mp.factorial(p+al)) * mp.power(2, mp.mpf(al)/2) * (Rm**al) * (w0m**(al+1)) / (dw**(al+1)) * mp.exp(-(Rm**2)/dw)\n"
            "    eta = 2*wm**2/dw; z = (Rm**2 * w0m**2)/(wm**2 * dw)\n"
            "    tot = sum(((-1)**m)*mp.binomial(p+al, p-m)*(eta**m)*mp.laguerre(m, al, -z) for m in range(p+1))\n"
            "    return float(pref * tot)\n"
            "for R_t, p_t, l_t, w_t, w0_t in ((1.5, 12, 5, 1.0, 1.0), (1.5, 9, 1, 1.0, 1.0)):\n"
            "  got_t = pp.c_lp_closed_form(R_t, p_t, l_t, w_t, w0_t); ref_t = mp_clp(R_t, p_t, l_t, w_t, w0_t)\n"
            "  assert abs(got_t - ref_t) / abs(ref_t) < 1e-12\n"
            "assert pp.c_lp_closed_form(1e300, 2, 1, 0.25, 1.0) == 0.0; "
            "assert pp.c_lp_closed_form(np.inf, 15, 1, 0.25, 1.0) == 0.0; "
            "assert pp.c_lp_closed_form(np.nan, 2, 1, 0.25, 1.0) == 0.0; "
            "assert pp.c_lp_closed_form(np.nan, 15, 1, 0.25, 1.0) == 0.0; "
            "c30 = pp.c_lp_closed_form(1.0, 30, 1, 2.0, 1.0); "
            "assert c30 > 0.0 and abs(c30 - 5.439796203214e-7) < 1e-10; "
            "assert abs(pp.c_lp_closed_form(2.5, 25, 1, 0.1, 1.0) - pp.c_lp_quad(2.5, 25, 1, 0.1, 1.0)) < 1e-12; "
            "g0 = pp.pvb_gram_normalized([0.0, 1.0, 2.0], 1, 0.5); "
            "assert np.all(np.isfinite(g0)) and np.allclose(g0, g0.T) and np.allclose(np.diag(g0), 1.0); "
            "lgr = pp.lg_radial(1.0, 100, 71, 1.0); "
            "assert math.isfinite(lgr) and lgr > 0.0; "
            "b20, v20, m20 = pp.tikhonov_mse_analytic(0.0, w_kmax=20.0); "
            "assert b20 == 0.0 and math.isfinite(v20) and math.isfinite(m20); "
            "b28, v28, m28 = pp.tikhonov_mse_analytic(0.0, w_kmax=28.0); "
            "assert b28 == 0.0 and math.isinf(v28) and math.isinf(m28); "
            # Gap 4: tikhonov_mse_analytic(0.0, p=20, l=-20, w_over_w0=100.0) zero warnings
            "b100, v100, m100 = pp.tikhonov_mse_analytic(0.0, p=20, l=-20, w_over_w0=100.0); "
            "assert b100 == 0.0 and math.isfinite(v100) and math.isfinite(m100); "
            # Iteration 5 pvb_physics regression guards (r5_1 + r5_2 Gaps 1-8)
            "assert np.allclose(pp.pvb_gram_normalized([1e-10, 2e-10], 20, 1.0), np.ones((2, 2)), atol=1e-14); "
            "assert np.allclose(pp.pvb_gram_normalized([1e-6, 2e-6], 20, 100.0), np.ones((2, 2)), atol=1e-14); "
            "assert abs(pp.pvb_gram_normalized([1e-10, 1.0], 20, 1.0)[0, 1] - 0.9940668992020802) < 1e-12\n"
            "for R_q, p_q, l_q, w_q, w0_q in ((1.0,2,1,1.0,1e-4),(1.0,2,1,100.0,1e-3),(1.0,0,0,100.0,1e-4),(1.0,0,0,100.0,1e-6),(1.0,2,1,100.0,1e-8)):\n"
            "  pq = pp.c_lp_quad(R_q, p_q, l_q, w_q, w0_q); pc = pp.c_lp_closed_form(R_q, p_q, l_q, w_q, w0_q)\n"
            "  assert abs(pq - pc) / max(abs(pc), 1e-300) < 1e-11\n"
            "assert abs(pp.pvb_iris_transmission(3.2e-4, 1e-12, 1e-4, -20) - 0.4834676036074702) < 1e-11; "
            "assert abs(pp.pvb_iris_transmission(700.0, 1.0, 100.0, 100) - 0.394245631751) < 1e-11\n"
            "try:\n"
            "  pp.pvb_iris_transmission(1.0, 0.0, 0.5, 1)\n"
            "  raise AssertionError('Expected ValueError')\n"
            "except ValueError:\n"
            "  pass\n"
            "assert abs(pp.c_lp_closed_form(1.5, 2, 1, 1e-160, 1.0) - pp.c_lp_quad(1.5, 2, 1, 1e-160, 1.0)) < 1e-12; "
            "assert abs(pp.c_lp_closed_form(1.5, 2, 1, 1e-200, 1.0) - pp.c_lp_quad(1.5, 2, 1, 1e-200, 1.0)) < 1e-12; "
            "arr_nar = pp.c_lp_closed_form(np.array([0.0, 1.5]), 2, 1, 1e-200, 1.0); "
            "assert arr_nar.shape == (2,) and arr_nar[0] == 0.0 and abs(arr_nar[1] - pp.c_lp_quad(1.5, 2, 1, 1e-200, 1.0)) < 1e-12; "
            "bk0, vk0, mk0 = pp.tikhonov_mse_analytic(1e-3, w_over_w0=0.25, w_kmax=0.0); "
            "assert math.isfinite(bk0) and abs(vk0 - 0.01 / (1.001 ** 2)) < 1e-14 and abs(mk0 - (bk0 + vk0)) < 1e-14; "
            "assert pp.tikhonov_mse_analytic(0.0, w_over_w0=0.25, w_kmax=0.0)[1] == 0.01; "
            "assert abs(pp.tikhonov_mse_analytic(1e-3, w_over_w0=0.25, w_kmax=1e-4)[1] - 0.01 / (1.001 ** 2)) < 1e-10; "
            "b2d, v2d, m2d = pp.tikhonov_mse_analytic(np.array([[0.0, 1e-2], [1e-1, np.inf]])); "
            "assert b2d.shape == (2, 2) and v2d.shape == (2, 2) and m2d.shape == (2, 2) and b2d[1, 1] == 1.0 and v2d[1, 1] == 0.0; "
            "assert abs(pp.tikhonov_mse_analytic(1e-6, p=5, l=1, w_over_w0=100.0)[0] - 0.999998341607245) < 1e-12; "
            "assert abs(pp.tikhonov_mse_analytic(1e-12, p=5, l=1, w_over_w0=100.0)[0] - 0.999993870217040) < 1e-12; "
            "assert abs(pp.nodal_washout_p0_closed(0, 1e100) - 2.0e-200) < 1e-212 and pp.nodal_washout_p0_closed(5, 1e100) == 0.0; "
            "lg_p = pp.lg_radial(np.array([0.0, 1.0, 10.0, 30.0]), 200, 200, 1.0); "
            "assert np.all(np.isfinite(lg_p)) and lg_p[0] == 0.0 and lg_p[2] > 0.0; "
            "ft_p = pp.lg_2d_ft_radial(35.0, 50, 250, 1.0); "
            "assert np.isfinite(ft_p) and abs(ft_p) > 0.04"
        )
        proc = subprocess.run(
            [sys.executable, "-B", "-c", code],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, f"pvb_physics edge guard failed:\n{proc.stdout}\n{proc.stderr}")
        gen_src = read_utf8(assert_v6_deliverable(self, V6_SCRIPTS_DIR / "generate_figures.py", "M2", "generate_figures.py"))
        self.assertNotIn("[0.13553, 0.04402]", gen_src)

    def test_t5_04_pra_arxiv_full_body_sync_and_pdf_fonts_oob(self) -> None:
        import pymupdf

        def _norm(s: str) -> str:
            for a, b in (
                ("figure*}", "figure}"),
                ("table*}", "table}"),
                ("[t]", "[htbp]"),
                ("{figures/", "{"),
                ("0.75\\textwidth", "0.76\\textwidth"),
                ("\\setlength{\\tabcolsep}{2.5pt}", "\\setlength{\\tabcolsep}{1pt}"),
            ):
                s = s.replace(a, b)
            return s

        pra_b = read_utf8(assert_v6_deliverable(self, V6_PRA_TEX, "M3", "main_pra.tex")).split(r"\begin{abstract}", 1)[1]
        arx_b = read_utf8(assert_v6_deliverable(self, V6_ARXIV_TEX, "M3", "main_arxiv.tex")).split(r"\begin{abstract}", 1)[1]
        self.assertEqual(_norm(pra_b).splitlines(), _norm(arx_b).splitlines())

        for log_p in (V6_PRA_LOG, V6_ARXIV_LOG):
            log_txt = read_utf8(assert_v6_deliverable(self, log_p, "M3", log_p.name))
            self.assertNotIn("Overfull \\hbox", log_txt, f"Overfull hbox found in {log_p.name}")

        for pdf in [*V6_FIG_PATHS, V6_PRA_PDF, V6_ARXIV_PDF]:
            assert_v6_deliverable(self, pdf, "M3", pdf.name)
            doc = pymupdf.open(str(pdf))
            try:
                for page in doc:
                    self.assertEqual(len(page.get_images()), 0, f"Raster image in {pdf.name}")
                    for f in page.get_fonts(full=True):
                        self.assertNotIn("Type3", str(f[2]), f"Type 3 font in {pdf.name}")
                    r = page.rect
                    for w in page.get_text("words"):
                        self.assertTrue(
                            w[0] >= r.x0 - 0.5 and w[1] >= r.y0 - 0.5 and w[2] <= r.x1 + 0.5 and w[3] <= r.y1 + 0.5,
                            f"OOB word {w[4]} in {pdf.name}",
                        )
            finally:
                doc.close()

    def test_t5_05_referee2_bib_doi_line_bounds_and_redos_guard(self) -> None:
        ref2 = read_utf8(assert_v6_deliverable(self, V6_REFEREE_2, "M1", "Referee 2 Report"))
        bib_txt = read_utf8(assert_v6_deliverable(self, V6_BIB, "M3", "references.bib")).lower()
        for bad in ("66--148", "10.1126/science.1235141", "Science* **326**, 69", "with structured light"):
            self.assertNotIn(bad, ref2)
        lines = [int(n) for n in re.findall(r"(?:\bL|\bline\s+)(\d+)\b", ref2, re.I)]
        self.assertGreater(len(lines), 0)
        for ln in lines:
            self.assertTrue(1 <= ln <= P33_EXPECTED_LINES, f"Out-of-range line L{ln} in REFEREE_2_REPORT.md")
        superseded_dois = {"10.1007/978-0-8176-8224-8"}
        doi_re = re.compile(r"10\.\d{4,9}/(?:[^\s`'\"),;>(]+|\([^\s`'\");>(]*\))+")
        found_dois = doi_re.findall(ref2)
        self.assertIn("10.1016/0030-4018(87)90276-8", found_dois)
        for doi in found_dois:
            clean_doi = doi.rstrip(".")
            if clean_doi in superseded_dois:
                continue
            self.assertIn(clean_doi.lower(), bib_txt, f"DOI {clean_doi} in REFEREE_2_REPORT.md missing from references.bib")
        t_doi = time.perf_counter()
        self.assertEqual(doi_re.findall("10.1016/" + "a" * 25000 + " "), ["10.1016/" + "a" * 25000])
        self.assertLess(time.perf_counter() - t_doi, 0.05)

        # Verify PDF_UNRESOLVED_MARK_RE catches \onlinecite{missing} bare '?' and runs in linear O(N) time
        self.assertRegex("Here, we resolve all four questions ? .", PDF_UNRESOLVED_MARK_RE)
        self.assertNotRegex("Why does this work? Because frames converge.", PDF_UNRESOLVED_MARK_RE)
        t0 = time.perf_counter()
        self.assertIsNone(PDF_UNRESOLVED_MARK_RE.search("[a" * 25000))
        self.assertLess(time.perf_counter() - t0, 0.05)

        # Verify _assert_no_positive_distortionless_alpha edge probes
        _assert_no_positive_distortionless_alpha(
            self,
            r"Tikhonov fails exact recovery and no $S_{w,\alpha}^{-1}$ operator yields recovery without distortion.",
            "neg_subject_probe",
        )
        _assert_no_positive_distortionless_alpha(
            self,
            r"At $\alpha_{\mathrm{reg}} = 0$, recovery has no distortion; for $\alpha_{\mathrm{reg}} > 0$, it yields no distortion-free recovery.",
            "alpha0_and_neg_distortion_free_probe",
        )
        for bad_probe in (
            r"Using \(\alpha_{\mathrm{reg}} > 0\) yields recovery without distortion.",
            r"For $\alpha_{\mathrm{reg}} > 0$, Tikhonov recovery is free of distortion.",
            r"For $\alpha_{\mathrm{reg}} > 0$, Tikhonov recovery has zero distortion.",
            r"For $\alpha_{\mathrm{reg}} > 0$, Tikhonov recovery proceeds with no distortion.",
        ):
            with self.assertRaises(AssertionError):
                _assert_no_positive_distortionless_alpha(self, bad_probe, "distortion_probe")

        # Verify _assert_table2_all_columns fails with AssertionError (not IndexError) on a 10-number row
        short_table2 = (
            r"\begin{tabular}{ccccccccc} \toprule "
            r"$\Delta R / w$ & $\Delta R$ & $|\gamma_{12}|$ & $|\gamma_{12}|^2$ & Iso & $\kappa(\gamma)$ & $\kappa(G)$ & ZF corr & ZF AWGN \\ \midrule "
            r"0.5 & 0.25 & 88.25 & 77.88 & 1.09 & 10857.55 & 15284.28 & 27.14 (14.34 dB) & 4923.02 \\ "
            r"1.0 & 0.50 & 60.65 & 36.79 & 4.34 & 28.80 & 48.20 & 3.12 (4.94 dB) & 19.86 \\ "
            r"1.5 & 0.75 & 32.47 & 10.54 & 9.77 & 3.723 & 7.365 & 1.24 (0.94 dB) & 1.78 (2.51 dB) \\ "
            r"2.0 & 1.00 & 13.53 & 1.83 & 17.37 & 1.645 & 3.841 & 1.04 (0.16 dB) & 1.10 (0.41 dB) \\ "
            r"2.5 & 1.25 & 4.39 & 0.19 & 27.14 & 1.172 & 3.249 & 1.00 (0.02 dB) & 1.01 (0.04 dB) \\ "
            r"3.0 & 1.50 & 1.11 & 0.01 & 39.09 & 1.041 & 3.192 & 1.00 (0.00 dB) & 1.00 (0.00 dB) \\ "
            r"\bottomrule \end{tabular}"
        )
        with self.assertRaises(AssertionError):
            _assert_table2_all_columns(self, short_table2, "short_table2_probe")


# ---------------------------------------------------------------------------
# Dual CLI Runner & ASCII Dashboard (No side-effect execution on import)
# ---------------------------------------------------------------------------

TIER_MAP: dict[int, list[type[unittest.TestCase]]] = {
    1: [
        TestT1Feature01Referee1Report,
        TestT1Feature02Referee2Report,
        TestT1Feature03ResolutionMapping,
        TestT1Feature04MathAndOpticsScripts,
        TestT1Feature05VectorFigures,
        TestT1Feature06VerifiedBibliography,
        TestT1Feature07MathCorrections,
        TestT1Feature08OpticsUtilityAndTable,
        TestT1Feature09AIAttributionAndHygiene,
        TestT1Feature10PRAAndArxivPDFs,
        TestT1Feature11E2ESuiteAndR4,
        TestT1Feature12FinalGateAndHardening,
    ],
    2: [
        TestT2Feature01Referee1Guards,
        TestT2Feature02Referee2Guards,
        TestT2Feature03MappingGuards,
        TestT2Feature04MathBoundaryOracles,
        TestT2Feature05FigureGuards,
        TestT2Feature06BibliographyGuards,
        TestT2Feature07MathRegressionGuards,
        TestT2Feature08OpticsUtilityGuards,
        TestT2Feature09HygieneAndAIGuards,
        TestT2Feature10PDFAndTeXGuards,
        TestT2Feature11E2EAndR4Guards,
        TestT2Feature12HardeningGuards,
    ],
    3: [TestT3CrossFeatureCombinations],
    4: [TestT4RealWorldAcceptanceScenarios],
    5: [TestT5WhiteBoxHardening],
}


class V6TestResult(unittest.TextTestResult):
    """Custom TestResult counting passes cleanly per tier."""

    def __init__(self, stream: Any, descriptions: bool, verbosity: int) -> None:
        super().__init__(stream, descriptions, verbosity)
        self.passed_count = 0

    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self.passed_count += 1


def run_tiers(
    tier: int | None = None, verbosity: int = 1, fail_fast: bool = False
) -> int:
    selected_tiers = [tier] if tier in TIER_MAP else [1, 2, 3, 4, 5]
    tier_labels = {
        1: "Tier 1: Feature Coverage       ",
        2: "Tier 2: Boundary & Regression  ",
        3: "Tier 3: Cross-Feature Pairwise ",
        4: "Tier 4: Real-World E2E (S1-S6) ",
        5: "Tier 5: White-Box Adversarial  ",
    }

    loader = unittest.TestLoader()
    summary: dict[int, dict[str, Any]] = {}
    t_start = time.time()

    for t in selected_tiers:
        suite = unittest.TestSuite()
        for cls in TIER_MAP[t]:
            suite.addTests(loader.loadTestsFromTestCase(cls))
        buf = StringIO()
        runner = unittest.TextTestRunner(
            stream=buf,
            resultclass=V6TestResult,
            verbosity=verbosity,
            failfast=fail_fast,
        )
        res: V6TestResult = runner.run(suite)  # type: ignore[assignment]
        if verbosity >= 2:
            print(buf.getvalue())
        summary[t] = {
            "total": res.testsRun,
            "passed": res.passed_count,
            "failed": len(res.failures),
            "errors": len(res.errors),
            "skipped": len(res.skipped),
            "details": res.failures + res.errors,
        }
        if fail_fast and (res.failures or res.errors):
            break

    elapsed = time.time() - t_start
    print("=" * 80)
    print("   V6 E2E TEST HARNESS: OVERCOMPLETE PERFECT VORTEX BEAMS (PVB)")
    print("=" * 80)
    print("+-------+--------------------------------+-------+------+------+-----+------+")
    print("| Tier  | Description                    | Total | Pass | Fail | Err | Skip |")
    print("+-------+--------------------------------+-------+------+------+-----+------+")
    tot_n = tot_p = tot_f = tot_e = tot_s = 0
    for t in summary:
        r = summary[t]
        tot_n += r["total"]
        tot_p += r["passed"]
        tot_f += r["failed"]
        tot_e += r["errors"]
        tot_s += r["skipped"]
        print(
            f"| T{t}    | {tier_labels[t]} | {r['total']:5d} | {r['passed']:4d} "
            f"| {r['failed']:4d} | {r['errors']:3d} | {r['skipped']:4d} |"
        )
    print("+-------+--------------------------------+-------+------+------+-----+------+")
    print(
        f"| TOTAL | Selected Tiers                 | {tot_n:5d} | {tot_p:4d} "
        f"| {tot_f:4d} | {tot_e:3d} | {tot_s:4d} |"
    )
    print("+-------+--------------------------------+-------+------+------+-----+------+")
    print(f"Elapsed: {elapsed:.2f}s")

    if tot_f or tot_e:
        print("\nFailure / Error Sample (first 15):")
        shown = 0
        for t in summary:
            for test_obj, tb in summary[t]["details"]:
                if shown >= 15:
                    break
                last_line = tb.strip().splitlines()[-1] if tb.strip() else ""
                print(f"  - [T{t}] {test_obj.id().split('.')[-1]}: {last_line}")
                shown += 1

    return 0 if (tot_f == 0 and tot_e == 0 and tot_s == 0) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dual E2E Test Runner for V6 Overcomplete PVB Project"
    )
    parser.add_argument(
        "--tier", "-t", type=int, choices=[1, 2, 3, 4, 5], default=None,
        help="Run a specific tier (1, 2, 3, 4, or 5); omit for all tiers",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    args = parser.parse_args(argv)
    return run_tiers(
        tier=args.tier,
        verbosity=2 if args.verbose else 1,
        fail_fast=args.fail_fast,
    )


if __name__ == "__main__":
    sys.exit(main())
