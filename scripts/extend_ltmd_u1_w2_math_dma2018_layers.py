#!/usr/bin/env python3
"""Extend W2 Mathematics OCR/PAGESTRUCT/FRAGSEG with four DMA 2018 books.

The 57-book historical base is treated as immutable validated evidence. Only
H2018P3DMA/H2018P4DMA/H2018P5DMA/H2018P6DMA shards are newly computed.
All versioned outputs remain text-free; FRAGSEG stores text hashes, not text.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

import classify_ltmd_u1_w2_math_page_structure_v02 as ps

DMA = {"H2018P3DMA": 225, "H2018P4DMA": 257, "H2018P5DMA": 225, "H2018P6DMA": 185}
DMA_KEYS = set(DMA)
BASE_VIEWERS = 57
CURRENT_VIEWERS = 61
BASE_IDENTITIES = 60
CURRENT_IDENTITIES = 64
ALIASES = 3
BASE_PAGES = 11945
CURRENT_PAGES = 12837
OCR_VERSION = "LTMD_U1_W2_MATH_OCR_0.2"
FLAG_VERSION = "LTMD_U1_W2_MATH_STRUCTKW_0.2"
PAGESTRUCT_VERSION = "PAGESTRUCT_LTMD_U1_W2_MATH_0.2"
FRAG_VERSION = "FRAGSEG_LTMD_U1_W2_MATH_0.2"
ELIGIBLE = {"textual", "mixed_text_image"}

ROOT = Path("data/catalog")
SCOPE = ROOT / "ltmd_u1_w2_scope.csv"
OCR = ROOT / "ltmd_u1_w2_math_ocr_metrics.csv"
OCR_SUM = ROOT / "ltmd_u1_w2_math_ocr_summary.csv"
OCR_MD = ROOT / "ltmd_u1_w2_math_ocr.md"
FLAGS = ROOT / "ltmd_u1_w2_math_structural_keyword_flags.csv"
STRUCT = ROOT / "ltmd_u1_w2_math_page_structure.csv"
STRUCT_SUM = ROOT / "ltmd_u1_w2_math_page_structure_summary.csv"
STRUCT_MD = ROOT / "ltmd_u1_w2_math_page_structure.md"
FRAG = ROOT / "ltmd_u1_w2_math_fragment_manifest.csv"
FRAG_SUM = ROOT / "ltmd_u1_w2_math_fragment_manifest_summary.csv"
FRAG_GAPS = ROOT / "ltmd_u1_w2_math_fragment_sequence_gaps.csv"
FRAG_MD = ROOT / "ltmd_u1_w2_math_fragment_manifest.md"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows:
        raise SystemExit(f"refusing empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    names = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=names)
        w.writeheader()
        w.writerows(rows)


def shard_rows(input_dir: Path, prefix: str, version_field: str, version: str) -> list[dict[str, str]]:
    files = sorted(input_dir.rglob(prefix + "*.csv"))
    if len(files) != 4:
        raise SystemExit(f"expected 4 {prefix} shards, got {len(files)}")
    rows: list[dict[str, str]] = []
    viewers: set[str] = set()
    for p in files:
        rr = read(p)
        if not rr:
            raise SystemExit(f"empty shard: {p}")
        keys = {r["viewer_key"] for r in rr}
        if len(keys) != 1 or not keys <= DMA_KEYS:
            raise SystemExit(f"invalid DMA shard identity: {p} {keys}")
        if {r[version_field] for r in rr} != {version}:
            raise SystemExit(f"version drift: {p}")
        viewers |= keys
        rows.extend(rr)
    if viewers != DMA_KEYS:
        raise SystemExit(f"DMA shard coverage mismatch: {viewers}")
    return rows


def merge_ocr(input_dir: Path) -> None:
    base = read(OCR)
    base_viewers = {r["viewer_key"] for r in base}
    if len(base_viewers) != BASE_VIEWERS or DMA_KEYS & base_viewers or len(base) != BASE_PAGES:
        raise SystemExit("historical W2 OCR base drift")
    new = shard_rows(input_dir, "ocr_", "ocr_version", OCR_VERSION)
    counts = Counter(r["viewer_key"] for r in new)
    if counts != Counter(DMA):
        raise SystemExit(f"DMA OCR page counts mismatch: {counts}")
    if any(r["source_sha256_verified"] != "1" or r["ocr_status"] != "ok" or r["ocr_class"] == "unresolved" for r in new):
        raise SystemExit("DMA OCR metrics contain unresolved/provenance failure")
    rows = base + new
    ids = [r["page_id"] for r in rows]
    if len(rows) != CURRENT_PAGES or len(ids) != len(set(ids)):
        raise SystemExit("extended OCR page cardinality/uniqueness drift")
    if len({r["viewer_key"] for r in rows}) != CURRENT_VIEWERS:
        raise SystemExit("extended OCR viewer denominator drift")
    rows.sort(key=lambda r: (int(r["catalog_generation"]), int(r["grade"]), r["viewer_key"], int(r["viewer_page"])))
    write(OCR, rows)

    scope = {r["viewer_key"]: r for r in read(SCOPE)}
    by: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        by[r["viewer_key"]].append(r)
    summaries = []
    for key in sorted(by, key=lambda k: (int(scope[k]["catalog_generation"]), int(scope[k]["grade_code"]), k)):
        rr = by[key]
        summaries.append({
            "ocr_version": OCR_VERSION, "viewer_key": key, "book_id": scope[key]["book_id"],
            "catalog_generation": scope[key]["catalog_generation"], "grade_code": scope[key]["grade_code"],
            "pages": len(rr), "sha_verified": sum(r["source_sha256_verified"] == "1" for r in rr),
            "text_detected": sum(r["ocr_class"] == "text_detected" for r in rr),
            "no_text_detected": sum(r["ocr_class"] == "no_text_detected" for r in rr),
            "unresolved": sum(r["ocr_class"] == "unresolved" for r in rr),
            "recognized_words": sum(int(r["recognized_words"] or 0) for r in rr),
            "ocr_chars": sum(int(r["ocr_chars"] or 0) for r in rr),
        })
    if len(summaries) != CURRENT_VIEWERS:
        raise SystemExit("OCR summary denominator drift")
    write(OCR_SUM, summaries)
    text = sum(r["ocr_class"] == "text_detected" for r in rows)
    no = sum(r["ocr_class"] == "no_text_detected" for r in rows)
    OCR_MD.write_text("\n".join([
        "# LTMD-U1 W2 — OCR técnico de Matemáticas", "", f"Versión: `{OCR_VERSION}`.", "",
        f"- Visores canónicos procesados: **{CURRENT_VIEWERS}/{CURRENT_VIEWERS}**.",
        f"- Identidades de catálogo representadas: **{CURRENT_IDENTITIES}/{CURRENT_IDENTITIES}**.",
        f"- Aliases exactos cubiertos sin recomputar OCR: **{ALIASES}**.",
        "- Excepciones de routing aún no resueltas en W2: **0**.",
        f"- Páginas fuente canónicas procesadas: **{len(rows):,}**.",
        f"- SHA-256 verificados: **{len(rows):,}/{len(rows):,}**.",
        f"- Texto detectado: **{text:,}/{len(rows):,} ({100*text/len(rows):.2f}%)**.",
        f"- `no_text_detected`: **{no:,}**.", "- `unresolved`: **0**.", "",
        "La extensión DMA 2018 añade únicamente cuatro objetos route-resolved y 892 páginas; los 57 canónicos históricos no se recomputan. El OCR íntegro no se persiste. Esta capa técnica no implica `text_verified` ni `semantic_ready`."
    ]) + "\n", encoding="utf-8")
    print(f"extended OCR: viewers={CURRENT_VIEWERS} pages={CURRENT_PAGES}")


def merge_pagestruct(input_dir: Path) -> None:
    metrics = read(OCR)
    if len(metrics) != CURRENT_PAGES or len({r["viewer_key"] for r in metrics}) != CURRENT_VIEWERS:
        raise SystemExit("run merge-ocr first")
    base = read(FLAGS)
    if len({r["viewer_key"] for r in base}) != BASE_VIEWERS or DMA_KEYS & {r["viewer_key"] for r in base}:
        raise SystemExit("historical structural flag base drift")
    new = shard_rows(input_dir, "structkw_", "scanner_version", FLAG_VERSION)
    rows = base + new
    expected = set()
    for viewer in {r["viewer_key"] for r in metrics}:
        rr = [r for r in metrics if r["viewer_key"] == viewer]
        max_page = max(int(r["viewer_page"]) for r in rr)
        expected |= {(viewer, r["page_id"]) for r in rr if int(r["viewer_page"]) <= 16 or int(r["viewer_page"]) > max_page - 16}
    keys = {(r["viewer_key"], r["page_id"]) for r in rows}
    if keys != expected or len(keys) != len(rows):
        raise SystemExit(f"extended structural flag coverage drift missing={len(expected-keys)} extra={len(keys-expected)}")
    if any(r["source_sha256_verified"] != "1" for r in rows):
        raise SystemExit("structural SHA failure")
    rows.sort(key=lambda r: (int(r["catalog_generation"]), int(r["grade"]), r["viewer_key"], int(r["viewer_page"])))
    write(FLAGS, rows)

    flags = {r["page_id"]: r for r in rows}
    out = []
    for r in metrics:
        k = flags.get(r["page_id"], {})
        primary, certainty, rule, evidence = ps.classify(r, k)
        out.append({
            "page_id": r["page_id"], "viewer_key": r["viewer_key"], "book_id": r["book_id"],
            "catalog_generation": r["catalog_generation"], "grade": r["grade"], "viewer_page": r["viewer_page"],
            "selected_psm": r["selected_psm"], "recognized_words": r["recognized_words"],
            "mean_word_confidence": r["mean_word_confidence"], "low_confidence_word_rate": r["low_confidence_word_rate"],
            "ocr_class": r["ocr_class"], "front_matter_score": k.get("front_matter_score", ""),
            "toc_navigation_score": k.get("toc_navigation_score", ""),
            "bibliography_credits_score": k.get("bibliography_credits_score", ""),
            "primary_structure": primary, "classification_certainty": certainty,
            "classification_rule": rule, "evidence_flags": evidence, "classifier_version": PAGESTRUCT_VERSION,
        })
    if len(out) != CURRENT_PAGES or len({r["viewer_key"] for r in out}) != CURRENT_VIEWERS:
        raise SystemExit("PAGESTRUCT output denominator drift")
    write(STRUCT, out)
    classes = ["textual", "mixed_text_image", "visual_only", "front_matter", "toc_or_navigation", "bibliography_or_credits", "unknown"]
    counts: dict[str, Counter] = defaultdict(Counter)
    for r in out:
        counts[r["viewer_key"]][r["primary_structure"]] += 1
        counts["ALL"][r["primary_structure"]] += 1
    summary = []
    for key in sorted(k for k in counts if k != "ALL") + ["ALL"]:
        c = counts[key]
        row: dict[str, object] = {"viewer_key": key, "n_pages": sum(c.values())}
        row.update({cl: c[cl] for cl in classes})
        summary.append(row)
    write(STRUCT_SUM, summary)
    allc = counts["ALL"]
    eligible = allc["textual"] + allc["mixed_text_image"]
    lines = ["# PAGESTRUCT — LTMD-U1 W2 Matemáticas", "", f"Versión: `{PAGESTRUCT_VERSION}`. Páginas clasificadas: **{len(out):,}**.", "", f"Visores canónicos: **{CURRENT_VIEWERS}**; representan {CURRENT_IDENTITIES}/{CURRENT_IDENTITIES} identidades mediante {ALIASES} aliases exactos.", "", "## Total"]
    lines += [f"- `{cl}`: {allc[cl]:,}." for cl in classes]
    lines += ["", f"Páginas elegibles para FRAGSEG (`textual` + `mixed_text_image`): **{eligible:,}**.", "", "## Regla", "Se conserva la lógica PAGESTRUCT 0.2. Los cuatro DMA 2018 se añaden tras resolución de routing sin recomputar los 57 canónicos históricos. Esta clasificación técnica no constituye validación humana, `text_verified` ni `semantic_ready`."]
    STRUCT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"extended PAGESTRUCT: viewers={CURRENT_VIEWERS} pages={CURRENT_PAGES} eligible={eligible}")


def merge_fragments(input_dir: Path) -> None:
    structure = read(STRUCT)
    if len(structure) != CURRENT_PAGES or len({r["viewer_key"] for r in structure}) != CURRENT_VIEWERS:
        raise SystemExit("run merge-pagestruct first")
    base = read(FRAG)
    if DMA_KEYS & {r["viewer_key"] for r in base}:
        raise SystemExit("historical FRAGSEG base unexpectedly contains DMA 2018")
    files = sorted(p for p in input_dir.rglob("fragment_*.csv") if not p.name.endswith("_failures.csv"))
    failfiles = sorted(input_dir.rglob("fragment_*_failures.csv"))
    if len(files) != 4 or len(failfiles) != 4:
        raise SystemExit(f"expected 4 fragment/failure shard pairs, got {len(files)}/{len(failfiles)}")
    new: list[dict[str, str]] = []
    new_viewers: set[str] = set()
    for p in files:
        rr = read(p)
        if rr:
            keys = {r["viewer_key"] for r in rr}
            if len(keys) != 1 or not keys <= DMA_KEYS or {r["segmenter_version"] for r in rr} != {FRAG_VERSION}:
                raise SystemExit(f"invalid fragment shard: {p}")
            new_viewers |= keys
            new.extend(rr)
        else:
            stem = p.stem.removeprefix("fragment_").upper()
            if stem in DMA_KEYS:
                new_viewers.add(stem)
    if new_viewers != DMA_KEYS:
        raise SystemExit(f"DMA FRAGSEG viewer coverage drift: {new_viewers}")
    reported_empty: set[tuple[str, str]] = set()
    for p in failfiles:
        for r in read(p):
            if r["status"] != "ok":
                raise SystemExit(f"fatal DMA FRAGSEG failure: {r}")
            reported_empty.add((r["viewer_key"], r["page_id"]))

    rows = base + new
    ids = [r["fragment_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate fragment IDs after DMA extension")
    eligible = {(r["viewer_key"], r["page_id"]) for r in structure if r["primary_structure"] in ELIGIBLE}
    fragment_pages = {(r["viewer_key"], r["page_id"]) for r in rows}
    if not fragment_pages <= eligible:
        raise SystemExit(f"fragment page outside PAGESTRUCT eligibility: {len(fragment_pages-eligible)}")
    empty_pages = eligible - fragment_pages
    dma_empty = {x for x in empty_pages if x[0] in DMA_KEYS}
    if dma_empty != reported_empty:
        raise SystemExit(f"DMA empty eligible-page accounting drift missing={dma_empty-reported_empty} extra={reported_empty-dma_empty}")

    bypage: dict[tuple[str, str], list[int]] = defaultdict(list)
    for r in rows:
        bypage[(r["viewer_key"], r["page_id"])].append(int(r["fragment_sequence"]))
    gaprows = []
    for (key, pid), vals in sorted(bypage.items()):
        sv = sorted(vals)
        if any(v <= 0 for v in sv) or len(sv) != len(set(sv)):
            raise SystemExit(f"invalid fragment sequence {key} {pid}")
        missing = [x for x in range(1, max(sv) + 1) if x not in set(sv)] if sv else []
        if missing:
            gaprows.append({"viewer_key": key, "page_id": pid, "observed_fragment_count": len(sv), "max_sequence": max(sv), "missing_sequence_slots": " ".join(map(str, missing)), "missing_slot_count": len(missing)})
    rows.sort(key=lambda r: (int(r["catalog_generation"]), int(r["grade"]), r["viewer_key"], int(r["viewer_page"]), int(r["fragment_sequence"])))
    write(FRAG, rows)
    if gaprows:
        write(FRAG_GAPS, gaprows)
    else:
        FRAG_GAPS.write_text("viewer_key,page_id,observed_fragment_count,max_sequence,missing_sequence_slots,missing_slot_count\n", encoding="utf-8")

    types = sorted({r["candidate_type"] for r in rows})
    counts: dict[str, Counter] = defaultdict(Counter)
    pages: dict[str, set[str]] = defaultdict(set)
    viewers = {r["viewer_key"] for r in structure}
    for r in rows:
        counts[r["viewer_key"]][r["candidate_type"]] += 1
        counts["ALL"][r["candidate_type"]] += 1
        pages[r["viewer_key"]].add(r["page_id"])
        pages["ALL"].add(r["page_id"])
    summary = []
    for key in sorted(viewers) + ["ALL"]:
        c = counts[key]
        row: dict[str, object] = {"segmenter_version": FRAG_VERSION, "viewer_key": key, "fragment_count": sum(c.values()), "segmented_page_count": len(pages[key])}
        row.update({t: c[t] for t in types})
        summary.append(row)
    write(FRAG_SUM, summary)
    allc = summary[-1]
    gap_slots = sum(int(r["missing_slot_count"]) for r in gaprows)
    lines = ["# FRAGSEG — LTMD-U1 W2 Matemáticas", "", f"Versión: `{FRAG_VERSION}`.", "", f"- Visores canónicos computados/representados: **{CURRENT_VIEWERS}**.", f"- Identidades de catálogo representadas: **{CURRENT_IDENTITIES}/{CURRENT_IDENTITIES}** mediante {ALIASES} aliases exactos.", f"- Páginas elegibles PAGESTRUCT: **{len(eligible):,}**.", f"- Páginas con ≥1 fragmento: **{allc['segmented_page_count']:,}**.", f"- Páginas elegibles sin fragmentos: **{len(empty_pages)}**.", f"- Fragmentos: **{allc['fragment_count']:,}**.", f"- IDs únicos: **{len(set(ids)):,}**.", f"- Páginas con huecos legítimos de secuencia: **{len(gaprows)}**.", f"- Slots omitidos: **{gap_slots}**.", "", "## Tipos candidatos"]
    lines += [f"- `{t}`: {allc[t]:,}." for t in types]
    lines += ["", "## Regla", "La extensión DMA 2018 reutiliza la lógica FRAGSEG 0.2. El texto completo no se persiste; se conservan hashes, señales y metadatos no sustitutivos. `short_residual_candidate` sigue siendo técnica. La capa no constituye validación humana, `text_verified` ni `semantic_ready`."]
    FRAG_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"extended FRAGSEG: viewers={CURRENT_VIEWERS} fragments={len(rows)} eligible={len(eligible)} empty={len(empty_pages)}")


def validate() -> None:
    metrics = read(OCR)
    structure = read(STRUCT)
    frag = read(FRAG)
    if len(metrics) != CURRENT_PAGES or len(structure) != CURRENT_PAGES:
        raise SystemExit("W2 extended layer page cardinality drift")
    if len({r["viewer_key"] for r in metrics}) != CURRENT_VIEWERS or len({r["viewer_key"] for r in structure}) != CURRENT_VIEWERS:
        raise SystemExit("W2 extended layer viewer denominator drift")
    for viewer, expected in DMA.items():
        if sum(r["viewer_key"] == viewer for r in metrics) != expected:
            raise SystemExit(f"{viewer}: OCR page count drift")
        if sum(r["viewer_key"] == viewer for r in structure) != expected:
            raise SystemExit(f"{viewer}: PAGESTRUCT page count drift")
    if any(r.get("classifier_version") != PAGESTRUCT_VERSION for r in structure):
        raise SystemExit("PAGESTRUCT version drift")
    if any(r.get("segmenter_version") != FRAG_VERSION for r in frag):
        raise SystemExit("FRAGSEG version drift")
    forbidden = {"text", "ocr_text", "ocr_text_raw", "search_text", "snippet", "normalized_text"}
    for path in (OCR, FLAGS, STRUCT, FRAG, FRAG_GAPS):
        rows = read(path)
        if rows and forbidden & set(rows[0]):
            raise SystemExit(f"forbidden text column in public layer: {path}")
    print("W2 DMA 2018 structural extension validated: 61 canonical / 64 identities / 12837 pages; text_verified=false; semantic_ready=false")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["merge-ocr", "merge-pagestruct", "merge-fragments", "validate"])
    ap.add_argument("--input-dir", type=Path, default=Path("data/work"))
    args = ap.parse_args()
    if args.mode == "merge-ocr":
        merge_ocr(args.input_dir)
    elif args.mode == "merge-pagestruct":
        merge_pagestruct(args.input_dir)
    elif args.mode == "merge-fragments":
        merge_fragments(args.input_dir)
    else:
        validate()


if __name__ == "__main__":
    main()
