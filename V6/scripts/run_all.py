"""
Master runner for V6 Milestone M2:
  1. Executes verify_math_and_tables.py -> V6/scripts/verified_metrics.json
  2. Executes generate_figures.py -> V6/figures/fig1..3.pdf
  3. Runs automated vector/font/MediaBox/text PDF validation via pymupdf, pypdf, and pdffonts
  4. Prints structured summary dashboard and exits 0 on full pass (1 otherwise).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pymupdf
from pypdf import PdfReader

SCRIPTS_DIR = Path(__file__).resolve().parent
FIGURES_DIR = SCRIPTS_DIR.parent / "figures"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_figures import generate_all_figures
from verify_math_and_tables import run_verification


_DIACRITIC_TEXTS = {"^", "~", "¯", "˙", "¨", "ˇ", "˘", "´", "`"}
_POW10_SINGLE_RE = re.compile(
    r"^10(?:\s*\^\s*(?:\{\s*[-−¡+]?\s*\d+\s*\}|[-−¡+]?\d+)|[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)$"
)
_EXP_PART_RE = re.compile(r"^(?:[-−¡+]?\d+|[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)$")
_SUP_ONLY_RE = re.compile(r"^[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+$")
_MATH_FONT_TAGS = ("Cmr", "Cmmi", "Cmsy", "Cmex", "STIX")
_MATH_SYMBOL_FONT_TAGS = ("Cmsy", "Cmex", "STIX")


def _span_gap_and_perp(a: dict[str, Any], b: dict[str, Any]) -> tuple[float, float, float]:
    """Return (signed_gap, perp_overlap, min_perp) for two same-direction spans."""
    ra, rb = a["rect"], b["rect"]
    if abs(a["dir"][0]) >= abs(a["dir"][1]):
        signed_gap = max(ra.x0, rb.x0) - min(ra.x1, rb.x1)
        perp_ov = max(0.0, min(ra.y1, rb.y1) - max(ra.y0, rb.y0))
        min_perp = min(ra.height, rb.height)
    else:
        signed_gap = max(ra.y0, rb.y0) - min(ra.y1, rb.y1)
        perp_ov = max(0.0, min(ra.x1, rb.x1) - max(ra.x0, rb.x0))
        min_perp = min(ra.width, rb.width)
    return signed_gap, perp_ov, min_perp


def _is_diacritic_pair(a: dict[str, Any], b: dict[str, Any], signed_gap: float) -> bool:
    """Return True iff one span is a genuine mathtext diacritic over a <=2-char symbol."""
    if a.get("line_id") is None or a["line_id"] != b.get("line_id"):
        return False
    if not (-5.0 <= signed_gap <= 2.5):
        return False
    ta, tb = a["text"].strip(), b["text"].strip()
    if ta in _DIACRITIC_TEXTS and tb not in _DIACRITIC_TEXTS:
        diac, base = a, b
    elif tb in _DIACRITIC_TEXTS and ta not in _DIACRITIC_TEXTS:
        diac, base = b, a
    else:
        return False
    if len(base["text"].strip()) > 2:
        return False
    if abs(diac["size"] - base["size"]) > 1.0:
        return False
    if not any(tag in diac["font"] for tag in ("Cmr", "Cmmi", "Cmsy", "STIX")):
        return False
    return True


def _is_opposite_sub_sup(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Return True iff two <7.5 pt spans sit on separated sub/superscript baselines."""
    if a["size"] >= 7.5 or b["size"] >= 7.5:
        return False
    if "origin" not in a or "origin" not in b:
        return False
    horiz = abs(a["dir"][0]) >= abs(a["dir"][1])
    orig_idx = 1 if horiz else 0
    return abs(a["origin"][orig_idx] - b["origin"][orig_idx]) >= 1.5


def _spans_should_cluster(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Return True if two same-direction spans belong to the same text label cluster."""
    if a["dir"] != b["dir"]:
        return False
    signed_gap, perp_ov, min_perp = _span_gap_and_perp(a, b)
    if min_perp <= 0.0 or perp_ov <= 0.35 * min_perp:
        return False
    if -0.15 <= signed_gap <= 2.5:
        return True
    return _is_diacritic_pair(a, b, signed_gap)


def _spans_compatible_in_cluster(comp: list[dict[str, Any]], cand: dict[str, Any]) -> bool:
    """Prevent transitive BFS chaining from merging colliding spans into one cluster."""
    for m in comp:
        if m["dir"] != cand["dir"]:
            return False
        sg, perp_ov, min_perp = _span_gap_and_perp(m, cand)
        if sg >= -0.15:
            continue
        if min_perp <= 0.0 or perp_ov <= 0.35 * min_perp:
            continue
        if _is_diacritic_pair(m, cand, sg):
            continue
        if _is_opposite_sub_sup(m, cand):
            continue
        return False
    return True


def _is_valid_script_or_symbol(sp: dict[str, Any], big_spans: list[dict[str, Any]]) -> bool:
    """Return True iff a <7.5 pt span in a >=7.5 pt cluster is a shifted script or math symbol."""
    st = sp["text"].strip()
    if not st or len(st) > 4:
        return False
    max_big = max(b["size"] for b in big_spans)
    if sp["size"] > 0.75 * max_big:
        return False
    if "origin" not in sp or not all("origin" in b for b in big_spans):
        return False

    horiz = abs(sp["dir"][0]) >= abs(sp["dir"][1])
    orig_idx = 1 if horiz else 0
    is_math_font = any(tag in sp["font"] for tag in _MATH_FONT_TAGS)
    is_symbol_font = any(tag in sp["font"] for tag in _MATH_SYMBOL_FONT_TAGS)

    same_line_big = [
        b for b in big_spans
        if sp.get("line_id") is not None and b.get("line_id") == sp["line_id"]
    ]
    if same_line_big:
        if len(st) <= 1 and is_symbol_font:
            return True
        if not is_math_font:
            has_pow10_base = any(b["text"].strip() == "10" for b in same_line_big)
            if not (has_pow10_base and _EXP_PART_RE.fullmatch(st)):
                return False
        base_orig = statistics.median(b["origin"][orig_idx] for b in same_line_big)
        d_orig = abs(sp["origin"][orig_idx] - base_orig)
        if len(st) > 1 and d_orig > 0.45 * max_big:
            return False
        return d_orig >= 0.9

    if not is_math_font:
        return False
    band_big = [
        b for b in big_spans
        if abs(b["origin"][orig_idx] - sp["origin"][orig_idx]) <= 6.0
    ]
    if not band_big:
        return False
    base_orig = statistics.median(b["origin"][orig_idx] for b in band_big)
    d_orig = abs(sp["origin"][orig_idx] - base_orig)
    if len(st) > 1 and d_orig > 0.45 * max_big:
        return False
    return d_orig >= 0.9


def _effective_vert_bounds(vert: dict[str, Any], horiz: dict[str, Any]) -> tuple[float, float, float, float]:
    """Return (x0, y0, x1, y1) of vertical spans, ignoring Cmsy horizontal metric padding."""
    hy0, hy1 = horiz["rect"].y0, horiz["rect"].y1
    band = [sp for sp in vert["spans"] if sp["rect"].y1 > hy0 and sp["rect"].y0 < hy1]
    if not band:
        band = vert["spans"]
    non_cmsy = [sp for sp in band if "Cmsy" not in sp["font"]]
    chosen = non_cmsy if non_cmsy else band
    return (
        min(sp["rect"].x0 for sp in chosen),
        vert["rect"].y0,
        max(sp["rect"].x1 for sp in chosen),
        vert["rect"].y1,
    )


def _is_pow10_tick(horiz: dict[str, Any]) -> bool:
    """Return True if a horizontal cluster represents a 10^k / 10^-k log tick (single or multi-span)."""
    spans = horiz["spans"]
    if len(spans) >= 2:
        ordered = sorted(
            spans,
            key=lambda sp: (sp["rect"].x0, -sp["size"], sp["rect"].y0),
        )
        base = ordered[0]
        if base["text"].strip() != "10":
            return False
        exp_spans = ordered[1:]
        for sp in exp_spans:
            if sp["size"] > base["size"] + 0.05:
                return False
            is_sup_chars = bool(_SUP_ONLY_RE.fullmatch(sp["text"].strip()))
            is_smaller = sp["size"] <= base["size"] - 0.5
            is_raised = (
                "origin" in sp
                and "origin" in base
                and sp["origin"][1] <= base["origin"][1] - 0.5
            )
            not_lowered = (
                "origin" not in sp
                or "origin" not in base
                or sp["origin"][1] <= base["origin"][1] + 0.5
            )
            if not (is_sup_chars or ((is_smaller or is_raised) and not_lowered)):
                return False
        joined = "".join(sp["text"].strip() for sp in exp_spans)
        return bool(joined) and bool(_EXP_PART_RE.fullmatch(joined))
    return bool(_POW10_SINGLE_RE.fullmatch(horiz["text"].strip()))


def _cluster_text_spans(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Cluster text spans into logical label boxes via bounded connected components."""
    n = len(spans)
    visited = [False] * n
    clusters: list[dict[str, Any]] = []
    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True
        comp = [spans[i]]
        stack = [i]
        while stack:
            cur = stack.pop()
            for j in range(n):
                if (
                    not visited[j]
                    and _spans_should_cluster(spans[cur], spans[j])
                    and _spans_compatible_in_cluster(comp, spans[j])
                ):
                    visited[j] = True
                    comp.append(spans[j])
                    stack.append(j)
        box = pymupdf.Rect(comp[0]["rect"])
        for sp in comp[1:]:
            box |= sp["rect"]
        big_spans = [sp for sp in comp if sp["size"] >= 7.5]
        if not big_spans:
            base_font = max(sp["size"] for sp in comp)
        else:
            unmasked_small = [
                sp["size"]
                for sp in comp
                if sp["size"] < 7.5 and not _is_valid_script_or_symbol(sp, big_spans)
            ]
            base_font = min(unmasked_small) if unmasked_small else max(sp["size"] for sp in comp)
        clusters.append(
            {
                "rect": box,
                "dir": comp[0]["dir"],
                "base_font": base_font,
                "text": " ".join(sp["text"].strip() for sp in comp),
                "spans": comp,
            }
        )
    return clusters


def validate_pdf_artifact(pdf_path: Path) -> dict[str, Any]:
    """Validate single-page 100% vector PDF compliance and geometric integrity."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing PDF artifact: {pdf_path}")

    raw = pdf_path.read_bytes()
    size_bytes = len(raw)
    if size_bytes < 15_000:
        raise AssertionError(f"{pdf_path.name}: size {size_bytes} B < 15000 B")
    if raw[:5] != b"%PDF-":
        raise AssertionError(f"{pdf_path.name}: missing %PDF- header")

    reader = PdfReader(str(pdf_path))
    if len(reader.pages) != 1:
        raise AssertionError(f"{pdf_path.name}: pypdf page count {len(reader.pages)} != 1")

    doc = pymupdf.open(str(pdf_path))
    oob: list[dict[str, Any]] = []
    collisions: list[str] = []
    try:
        if doc.page_count != 1:
            raise AssertionError(f"{pdf_path.name}: pymupdf page_count {doc.page_count} != 1")
        page = doc[0]
        rect = page.rect
        if not (475.0 <= rect.width <= 530.0):
            raise AssertionError(f"{pdf_path.name}: width {rect.width:.2f} pt outside [475, 530]")
        if not (320.0 <= rect.height <= 390.0):
            raise AssertionError(f"{pdf_path.name}: height {rect.height:.2f} pt outside [320, 390]")

        images = page.get_images()
        if images:
            raise AssertionError(f"{pdf_path.name}: found {len(images)} embedded raster image(s)")

        drawings = page.get_drawings()
        if len(drawings) < 20:
            raise AssertionError(f"{pdf_path.name}: too few vector drawings ({len(drawings)})")

        fonts = page.get_fonts(full=True)
        type3_fonts = [f for f in fonts if "Type3" in str(f[2]) or "Type 3" in str(f[2])]
        if type3_fonts:
            raise AssertionError(f"{pdf_path.name}: Type 3 fonts detected via pymupdf: {type3_fonts}")

        text = page.get_text()
        for tag in ("(a)", "(b)", "(c)", "(d)"):
            if tag not in text:
                raise AssertionError(f"{pdf_path.name}: panel label {tag} missing in extracted text")

        # 1. Cmex-aware OOB span check & span collection for clustering
        all_spans: list[dict[str, Any]] = []
        text_dict = page.get_text("dict")
        for block_idx, block in enumerate(text_dict.get("blocks", [])):
            if block.get("type", 0) != 0:
                continue
            for line_idx, line in enumerate(block.get("lines", [])):
                raw_dir = line.get("dir", (1.0, 0.0))
                line_dir = (int(round(raw_dir[0])), int(round(raw_dir[1])))
                kept_in_line: list[dict[str, Any]] = []
                for s in line.get("spans", []):
                    stext = s.get("text", "")
                    sfont = s.get("font", "")
                    if not stext.strip():
                        continue
                    if "Cmex" in sfont and len(stext.strip()) <= 1:
                        continue
                    sp_item = {
                        "text": stext,
                        "font": sfont,
                        "size": float(s.get("size", 0.0)),
                        "rect": pymupdf.Rect(s["bbox"]),
                        "dir": line_dir,
                        "origin": tuple(float(v) for v in s.get("origin", (0.0, 0.0))),
                        "line_id": (block_idx, line_idx),
                    }
                    kept_in_line.append(sp_item)
                    all_spans.append(sp_item)
                if kept_in_line:
                    line_box = pymupdf.Rect(kept_in_line[0]["rect"])
                    for sp in kept_in_line[1:]:
                        line_box |= sp["rect"]
                    if (
                        line_box.x0 < rect.x0 - 0.5
                        or line_box.y0 < rect.y0 - 0.5
                        or line_box.x1 > rect.x1 + 0.5
                        or line_box.y1 > rect.y1 + 0.5
                    ):
                        oob.append(
                            {
                                "text": " ".join(sp["text"].strip() for sp in kept_in_line),
                                "bbox": tuple(round(v, 2) for v in line_box),
                            }
                        )
        if oob:
            raise AssertionError(f"{pdf_path.name}: out-of-bounds text spans detected: {oob}")

        # 2. Clustered pairwise collision & minimum font-size check
        clusters = _cluster_text_spans(all_spans)
        small_clusters = [
            (c["text"], round(c["base_font"], 2))
            for c in clusters
            if c["base_font"] < 7.5
        ]
        if small_clusters:
            raise AssertionError(f"{pdf_path.name}: text clusters below 7.5 pt: {small_clusters}")

        # Intra-cluster raw-span collision guard (defense-in-depth against chained spans)
        for c in clusters:
            sps = c["spans"]
            for a_i in range(len(sps)):
                for b_i in range(a_i + 1, len(sps)):
                    sa, sb = sps[a_i], sps[b_i]
                    if sa["dir"] != sb["dir"]:
                        continue
                    inter = sa["rect"] & sb["rect"]
                    if not inter.is_empty and inter.width > 0.2 and inter.height > 0.2:
                        sg, _, _ = _span_gap_and_perp(sa, sb)
                        if _is_diacritic_pair(sa, sb, sg) or _is_opposite_sub_sup(sa, sb):
                            continue
                        area = inter.width * inter.height
                        min_area = min(sa["rect"].get_area(), sb["rect"].get_area())
                        frac = area / min_area if min_area > 0.0 else 0.0
                        if (
                            area > 30.0
                            or frac > 0.20
                            or (inter.width > 1.8 and inter.height > 1.8)
                        ):
                            collisions.append(
                                f"intra_cluster '{sa['text'].strip()}' vs '{sb['text'].strip()}' "
                                f"(w={inter.width:.2f}, h={inter.height:.2f}, area={area:.1f}pt2, frac={frac:.2f})"
                            )

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                c1, c2 = clusters[i], clusters[j]
                r1, r2 = c1["rect"], c2["rect"]
                is_parallel = (
                    c1["dir"] == c2["dir"]
                    or c1["dir"] == (-c2["dir"][0], -c2["dir"][1])
                )
                inter = r1 & r2
                if not inter.is_empty and inter.width > 0.2 and inter.height > 0.2:
                    area = inter.width * inter.height
                    min_area = min(r1.get_area(), r2.get_area())
                    frac = area / min_area if min_area > 0.0 else 0.0
                    if not is_parallel:
                        if area > 40.0 or frac > 0.35:
                            collisions.append(
                                f"cross_dir '{c1['text']}' vs '{c2['text']}' "
                                f"(area={area:.1f}pt2, frac={frac:.2f})"
                            )
                        non_cmsy_1 = [sp["rect"] for sp in c1["spans"] if "Cmsy" not in sp["font"]]
                        non_cmsy_2 = [sp["rect"] for sp in c2["spans"] if "Cmsy" not in sp["font"]]
                        if non_cmsy_1 and non_cmsy_2:
                            nr1 = pymupdf.Rect(non_cmsy_1[0])
                            for nr in non_cmsy_1[1:]:
                                nr1 |= nr
                            nr2 = pymupdf.Rect(non_cmsy_2[0])
                            for nr in non_cmsy_2[1:]:
                                nr2 |= nr
                            ninter = nr1 & nr2
                            if not ninter.is_empty and ninter.width > 0.2 and ninter.height > 0.2:
                                narea = ninter.width * ninter.height
                                nmin = min(nr1.get_area(), nr2.get_area())
                                nfrac = narea / nmin if nmin > 0.0 else 0.0
                                if (
                                    narea > 12.0
                                    or nfrac > 0.15
                                    or (ninter.width > 1.8 and ninter.height > 1.8)
                                ):
                                    collisions.append(
                                        f"cross_dir_non_cmsy '{c1['text']}' vs '{c2['text']}' "
                                        f"(w={ninter.width:.2f}, h={ninter.height:.2f}, area={narea:.1f}pt2, frac={nfrac:.2f})"
                                    )
                    else:
                        if (
                            area > 30.0
                            or frac > 0.20
                            or (inter.width > 1.8 and inter.height > 1.8)
                        ):
                            collisions.append(
                                f"same_dir '{c1['text']}' vs '{c2['text']}' "
                                f"(w={inter.width:.2f}, h={inter.height:.2f}, area={area:.1f}pt2, frac={frac:.2f})"
                            )
                if not is_parallel:
                    d1_vert = abs(c1["dir"][1]) > abs(c1["dir"][0])
                    d2_vert = abs(c2["dir"][1]) > abs(c2["dir"][0])
                    d1_horiz = abs(c1["dir"][0]) > abs(c1["dir"][1])
                    d2_horiz = abs(c2["dir"][0]) > abs(c2["dir"][1])
                    if d1_vert and d2_horiz:
                        vert, horiz = c1, c2
                    elif d2_vert and d1_horiz:
                        vert, horiz = c2, c1
                    else:
                        continue
                    vx0, vy0, vx1, vy1 = _effective_vert_bounds(vert, horiz)
                    hx0, hy0, hx1, hy1 = horiz["rect"].x0, horiz["rect"].y0, horiz["rect"].x1, horiz["rect"].y1
                    y_ov = min(vy1, hy1) - max(vy0, hy0)
                    x_gap = max(vx0, hx0) - min(vx1, hx1)
                    y_gap = -y_ov
                    if max(x_gap, y_gap) < 0.5:
                        collisions.append(
                            f"cross_dir_touch '{vert['text']}' vs '{horiz['text']}' "
                            f"(x_gap={x_gap:.2f}pt, y_gap={y_gap:.2f}pt < 0.5pt)"
                        )
                    if (
                        y_ov > 0.0
                        and hx0 >= vx0
                        and ("H" in vert["text"] or _is_pow10_tick(horiz))
                        and x_gap < 4.5
                    ):
                        collisions.append(
                            f"inset_gap '{vert['text']}' vs '{horiz['text']}' "
                            f"(gap={x_gap:.2f}pt < 4.5pt)"
                        )
        if collisions:
            raise AssertionError(f"{pdf_path.name}: text collisions detected: {collisions}")
    finally:
        doc.close()

    # Cross-check with pdffonts if installed on PATH
    pdffonts_exe = shutil.which("pdffonts")
    pdffonts_count = None
    if pdffonts_exe:
        proc = subprocess.run(
            [pdffonts_exe, str(pdf_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        font_rows = lines[2:] if len(lines) >= 2 else []
        pdffonts_count = len(font_rows)
        for row in font_rows:
            if "Type 3" in row:
                raise AssertionError(f"{pdf_path.name}: Type 3 font detected via pdffonts: {row}")

    return {
        "file": pdf_path.name,
        "size_bytes": size_bytes,
        "width_pt": round(rect.width, 2),
        "height_pt": round(rect.height, 2),
        "n_drawings": len(drawings),
        "n_fonts_pymupdf": len(fonts),
        "n_fonts_pdffonts": pdffonts_count,
        "oob_spans": len(oob),
        "collisions": len(collisions),
    }


def main() -> int:
    os.environ["PYTHONHASHSEED"] = "0"
    parser = argparse.ArgumentParser(description="Run V6 math verification, figure generation, and PDF validation.")
    parser.add_argument("--verify-only", action="store_true", help="Run mathematical verification only.")
    parser.add_argument("--figures-only", action="store_true", help="Generate and validate figures from existing JSON.")
    parser.add_argument("--json-out", type=Path, default=SCRIPTS_DIR / "verified_metrics.json", help="Metrics JSON path.")
    args = parser.parse_args()

    if args.verify_only and args.figures_only:
        raise ValueError("Cannot specify both --verify-only and --figures-only.")

    stages: list[tuple[str, str, float, str]] = []
    t_total_0 = time.perf_counter()

    if not args.figures_only:
        t0 = time.perf_counter()
        metrics = run_verification(json_out=args.json_out, seed=2026)
        dt_s = time.perf_counter() - t0
        loaded = json.loads(args.json_out.read_text(encoding="utf-8"))
        assert loaded["metadata"]["all_assertions_passed"] is True
        assert all(loaded["assertions"].values())
        n_assert = len(loaded["assertions"])
        stages.append(("Verification", "PASS", dt_s, f"{n_assert}/{n_assert} assertions passed"))
    else:
        loaded = json.loads(args.json_out.read_text(encoding="utf-8"))

    if not args.verify_only:
        t0 = time.perf_counter()
        pdf_paths = generate_all_figures(loaded, FIGURES_DIR)
        dt_s = time.perf_counter() - t0
        stages.append(("Figure Gen", "PASS", dt_s, f"{len(pdf_paths)} PDFs generated"))

        t0 = time.perf_counter()
        val_details = [validate_pdf_artifact(p) for p in pdf_paths]
        dt_s = time.perf_counter() - t0
        summary = "; ".join(
            f"{d['file']}[{d['width_pt']}x{d['height_pt']}pt,{d['size_bytes']//1024}KB,0 Type3,oob={d['oob_spans']},col={d['collisions']}]"
            for d in val_details
        )
        stages.append(("PDF Validate", "PASS", dt_s, summary))

    total_dt = time.perf_counter() - t_total_0
    print("=" * 84)
    print(f"{'Stage':<15} | {'Status':<6} | {'Time (s)':>8} | Details")
    print("-" * 84)
    for st, ok, elapsed, det in stages:
        print(f"{st:<15} | {ok:<6} | {elapsed:>8.2f} | {det}")
    print("-" * 84)
    print(f"Total runtime: {total_dt:.2f} s")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
