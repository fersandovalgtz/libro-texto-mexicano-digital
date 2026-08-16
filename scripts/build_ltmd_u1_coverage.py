#!/usr/bin/env python3
"""Build the LTMD-U1 (542-viewer) coverage matrix and operational wave queue.

This is an operational planning layer, not a semantic or historical classifier.
It derives coverage conservatively from already-materialized LTMD artifacts.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "LTMD_U1_COVERAGE_0.1"
EXPECTED_U1 = 542
EXPECTED_TITLE_FAMILIES = 191

TITLE_INVENTORY = Path("data/catalog/conaliteg_historical_title_inventory.csv")
TITLE_CORES = Path("data/catalog/conaliteg_title_cores.csv")
CN_READINESS = Path("data/catalog/ciencias_naturales_family_asset_readiness.csv")
BOOK_INVENTORY = Path("data/book_inventory.csv")
CN46_INVENTORY = Path("data/expansion/cn46_inventory_preliminary.csv")
CN46_SUMMARY = Path("data/expansion/cn46_fragment_manifest_summary.csv")
WAVE2_QUEUE = Path("data/expansion/cn_wave2_ingestion_queue.csv")
WAVE2_SUMMARY = Path("data/expansion/cn_wave2_fragment_manifest_summary.csv")
PILOT_SUMMARY = Path("data/derived/fragment_segmentation_summary.csv")
PILOT_MANIFEST = Path("data/derived/fragment_manifest.csv")
DOC_REL = Path("data/expansion/document_relationships_0_1.csv")
ALIAS_REL = Path("data/catalog/cn2018_2019_catalog_alias_relationships.csv")

OUT_COVERAGE = Path("data/catalog/ltmd_u1_coverage.csv")
OUT_SUMMARY = Path("data/catalog/ltmd_u1_coverage_summary.csv")
OUT_DOMAIN = Path("data/catalog/ltmd_u1_domain_summary.csv")
OUT_QUEUE = Path("data/catalog/ltmd_u1_wave_queue.csv")
OUT_REPORT = Path("data/catalog/ltmd_u1_coverage.md")


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode().casefold()
    return re.sub(r"\s+", " ", text).strip()


def viewer_from_url(url: str) -> str:
    m = re.search(r"/([^/]+)\.htm(?:\?.*)?$", url or "")
    return m.group(1) if m else ""


def signals_for_title(title_core_normalized: str):
    t = norm(title_core_normalized)
    signals = []
    rules = [
        ("ciencias_naturales", ("ciencias naturales", "ciencia natural", "estudio de la naturaleza", "exploracion de la naturaleza")),
        ("matematicas", ("matematic", "aritmet", "geometr", "algebra")),
        ("espanol_lengua", ("espanol", "lengua nacional", "lectura", "lecturas", "escritura", "gramatica", "lenguaje")),
        ("historia", ("historia",)),
        ("geografia_atlas", ("geografia", "atlas")),
        ("civica_etica", ("civismo", "civica", "civico", "etica", "formacion civica")),
        ("artes", ("educacion artistica", "artes", "artistica")),
        ("educacion_fisica", ("educacion fisica",)),
    ]
    for label, needles in rules:
        if any(n in t for n in needles):
            signals.append(label)
    return signals


def operational_domain(title_core_normalized: str):
    sig = signals_for_title(title_core_normalized)
    if len(sig) > 1:
        return "integrados_multiarea", ";".join(sig)
    if len(sig) == 1:
        return sig[0], sig[0]
    return "otros_no_clasificados", ""


WAVES = {
    "ciencias_naturales": (1, "U1-W1-ciencias_naturales"),
    "matematicas": (2, "U1-W2-matematicas"),
    "espanol_lengua": (3, "U1-W3-espanol_lengua"),
    "historia": (4, "U1-W4-historia"),
    "geografia_atlas": (5, "U1-W5-geografia_atlas"),
    "civica_etica": (6, "U1-W6-civica_etica"),
    "artes": (7, "U1-W7-artes"),
    "educacion_fisica": (8, "U1-W8-educacion_fisica"),
    "integrados_multiarea": (9, "U1-W9-integrados_multiarea"),
    "otros_no_clasificados": (10, "U1-W10-otros_revision"),
}


def main():
    inventory = rows(TITLE_INVENTORY)
    cores = rows(TITLE_CORES)
    assert len(inventory) == EXPECTED_U1, (len(inventory), EXPECTED_U1)
    viewers = [r["viewer_key"] for r in inventory]
    assert len(set(viewers)) == EXPECTED_U1

    core_by_viewer = {r["viewer_key"]: r for r in cores}
    assert set(core_by_viewer) == set(viewers)
    family_count = len({r["title_core_normalized"] for r in cores})
    assert family_count == EXPECTED_TITLE_FAMILIES, (family_count, EXPECTED_TITLE_FAMILIES)

    book_to_viewer = {}
    viewer_to_book = {}

    for r in rows(BOOK_INVENTORY):
        v = viewer_from_url(r.get("source_url", ""))
        if v:
            book_to_viewer[r["book_id"]] = v
            viewer_to_book[v] = r["book_id"]

    for p in (CN46_INVENTORY, WAVE2_QUEUE):
        for r in rows(p):
            b, v = r.get("book_id", ""), r.get("viewer_key", "")
            if b and v:
                book_to_viewer[b] = v
                viewer_to_book[v] = b

    # Directly materialized FRAGSEG objects. A completed FRAGSEG implies the
    # prerequisite page manifest, OCR and PAGESTRUCT stages existed.
    frag_books = set()
    fragment_counts = {}

    if PILOT_MANIFEST.exists() and PILOT_SUMMARY.exists():
        for r in rows(BOOK_INVENTORY):
            frag_books.add(r["book_id"])
        total = next(r for r in rows(PILOT_SUMMARY) if r["catalog_generation"] == "ALL")
        # Per-pilot counts live by generation; map through the four book inventory rows.
        by_gen = {r["catalog_generation"]: int(r["fragment_count"]) for r in rows(PILOT_SUMMARY) if r["catalog_generation"] != "ALL"}
        for r in rows(BOOK_INVENTORY):
            fragment_counts[r["book_id"]] = by_gen.get(r["catalog_generation"], 0)
        assert int(total["fragment_count"]) == sum(fragment_counts[b] for b in frag_books if b in fragment_counts)

    for p in (CN46_SUMMARY, WAVE2_SUMMARY):
        for r in rows(p):
            if r["book_id"] == "ALL":
                continue
            frag_books.add(r["book_id"])
            fragment_counts[r["book_id"]] = int(r["fragment_count"])

    frag_viewers = {book_to_viewer[b] for b in frag_books if b in book_to_viewer}
    assert len(frag_viewers) >= 32, len(frag_viewers)

    readiness = {r["viewer_key"]: r for r in rows(CN_READINESS)}
    asset_full = set()
    asset_partial = set()
    alias_to_viewer = {}
    for v, r in readiness.items():
        s = r["asset_readiness"]
        if s in {"full_direct", "full_alias_same_bytes"}:
            asset_full.add(v)
        elif s == "partial_internal_unserved":
            asset_partial.add(v)
        alias_book = r.get("alias_to_book_id", "")
        if alias_book and alias_book in book_to_viewer:
            alias_to_viewer[v] = book_to_viewer[alias_book]

    # Any directly FRAGSEG-materialized viewer is necessarily fully resolved at
    # the source level for the materialized object, including related CN titles
    # outside the strict title-core readiness table.
    asset_full |= frag_viewers

    dependence_viewers = set()
    if DOC_REL.exists():
        for r in rows(DOC_REL):
            for k in ("book_a", "book_b"):
                b = r.get(k, "")
                if b in book_to_viewer:
                    dependence_viewers.add(book_to_viewer[b])
    if ALIAS_REL.exists():
        for r in rows(ALIAS_REL):
            for k in ("viewer_key_a", "viewer_key_b"):
                if r.get(k):
                    dependence_viewers.add(r[k])
                    if k == "viewer_key_a":
                        alias_to_viewer[r[k]] = r.get("viewer_key_b", "")

    effective_frag = set(frag_viewers)
    changed = True
    while changed:
        changed = False
        for alias_v, target_v in alias_to_viewer.items():
            if target_v in effective_frag and alias_v not in effective_frag:
                effective_frag.add(alias_v)
                changed = True

    coverage = []
    for inv in inventory:
        v = inv["viewer_key"]
        c = core_by_viewer[v]
        domain, sig = operational_domain(c["title_core_normalized"])
        book_id = viewer_to_book.get(v, "")
        direct = v in frag_viewers
        effective = v in effective_frag
        alias_target = alias_to_viewer.get(v, "")

        if direct:
            wave_no, wave_label, queue_status = 0, "U1-W0-materializado", "materialized_direct"
        elif effective and alias_target:
            wave_no, wave_label, queue_status = 0, "U1-W0-cubierto_alias", "covered_by_verified_alias"
        else:
            wave_no, wave_label = WAVES[domain]
            queue_status = "queued"

        if v in readiness:
            asset_status = readiness[v]["asset_readiness"]
        elif direct:
            asset_status = "full_direct_processed"
        else:
            asset_status = "not_yet_audited"

        coverage.append({
            "coverage_version": VERSION,
            "viewer_key": v,
            "catalog_generation": inv["catalog_generation"],
            "grade_code": inv["grade_code"],
            "tail_code": inv["tail_code"],
            "source_url": inv["source_url"],
            "viewer_title": inv["viewer_title"],
            "title_core": c["title_core"],
            "title_core_normalized": c["title_core_normalized"],
            "operational_domain": domain,
            "domain_signals": sig,
            "book_id": book_id,
            "cataloged": 1,
            "title_normalized": 1,
            "asset_status": asset_status,
            "asset_resolved_full": int(v in asset_full),
            "asset_resolved_partial": int(v in asset_partial),
            "page_manifest_ready": int(direct),
            "ocr_ready": int(direct),
            "pagestruct_ready": int(direct),
            "fragseg_materialized": int(direct),
            "effective_fragseg_coverage": int(effective),
            "coverage_inherited_from_viewer": alias_target if effective and not direct else "",
            "fragment_count_materialized": fragment_counts.get(book_id, 0),
            "dependence_audited": int(v in dependence_viewers),
            "semantic_ready": 0,
            "wave_priority": wave_no,
            "wave_label": wave_label,
            "queue_status": queue_status,
        })

    OUT_COVERAGE.parent.mkdir(parents=True, exist_ok=True)
    fields = list(coverage[0].keys())
    with OUT_COVERAGE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(coverage)

    def n(pred): return sum(1 for r in coverage if pred(r))
    stages = [
        ("cataloged", n(lambda r: r["cataloged"] == 1), "All viewers in frozen U1 catalog snapshot."),
        ("title_normalized", n(lambda r: r["title_normalized"] == 1), f"Normalized into {family_count} title-core families."),
        ("asset_resolved_full", n(lambda r: r["asset_resolved_full"] == 1), "Full source-asset resolution demonstrated; unaudited viewers are not counted."),
        ("asset_resolved_partial", n(lambda r: r["asset_resolved_partial"] == 1), "Known partial source resolution; reported separately, not added to full coverage."),
        ("page_manifest_ready_direct", n(lambda r: r["page_manifest_ready"] == 1), "Conservative count from completed direct corpus objects."),
        ("ocr_ready_direct", n(lambda r: r["ocr_ready"] == 1), "Directly materialized OCR technical layer."),
        ("pagestruct_ready_direct", n(lambda r: r["pagestruct_ready"] == 1), "Directly materialized PAGESTRUCT layer."),
        ("fragseg_materialized_direct", n(lambda r: r["fragseg_materialized"] == 1), "Direct viewer objects with completed FRAGSEG."),
        ("effective_fragseg_coverage", n(lambda r: r["effective_fragseg_coverage"] == 1), "Direct FRAGSEG plus verified aliases inheriting byte-identical processed assets."),
        ("dependence_audited", n(lambda r: r["dependence_audited"] == 1), "Viewer participates in a currently registered document-dependence relationship."),
        ("semantic_ready_validated", 0, "SEMB 0.3 remains WAITING_HUMAN_REFERENCE; no viewer is counted as validated semantic coverage."),
    ]
    with OUT_SUMMARY.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["coverage_version","stage","viewer_count","universe_viewers","percent","notes"])
        w.writeheader()
        for stage, count, notes in stages:
            w.writerow({"coverage_version":VERSION,"stage":stage,"viewer_count":count,"universe_viewers":EXPECTED_U1,"percent":f"{100*count/EXPECTED_U1:.2f}","notes":notes})

    domain_rows = []
    grouped = defaultdict(list)
    for r in coverage: grouped[r["operational_domain"]].append(r)
    for domain, rs in sorted(grouped.items(), key=lambda kv:(WAVES[kv[0]][0], kv[0])):
        total = len(rs)
        direct = sum(int(r["fragseg_materialized"]) for r in rs)
        effective = sum(int(r["effective_fragseg_coverage"]) for r in rs)
        full = sum(int(r["asset_resolved_full"]) for r in rs)
        domain_rows.append({
            "coverage_version": VERSION,
            "operational_domain": domain,
            "viewer_count": total,
            "percent_of_u1": f"{100*total/EXPECTED_U1:.2f}",
            "asset_resolved_full": full,
            "fragseg_materialized_direct": direct,
            "effective_fragseg_coverage": effective,
            "remaining_effective": total-effective,
            "next_wave_priority": WAVES[domain][0],
            "next_wave_label": WAVES[domain][1],
        })
    with OUT_DOMAIN.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(domain_rows[0].keys())); w.writeheader(); w.writerows(domain_rows)

    queued = sorted(coverage, key=lambda r:(int(r["wave_priority"]), int(r["catalog_generation"]), int(r["grade_code"]), r["viewer_key"]))
    q_fields = ["coverage_version","wave_priority","wave_label","queue_status","operational_domain","viewer_key","catalog_generation","grade_code","title_core","asset_status","effective_fragseg_coverage","coverage_inherited_from_viewer","source_url"]
    with OUT_QUEUE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=q_fields); w.writeheader()
        for r in queued: w.writerow({k:r[k] for k in q_fields})

    stage_lookup = {stage:(count, notes) for stage,count,notes in stages}
    direct_count = stage_lookup["fragseg_materialized_direct"][0]
    effective_count = stage_lookup["effective_fragseg_coverage"][0]
    full_assets = stage_lookup["asset_resolved_full"][0]
    partial_assets = stage_lookup["asset_resolved_partial"][0]
    dep_count = stage_lookup["dependence_audited"][0]

    wave_counts = Counter((r["wave_priority"], r["wave_label"], r["queue_status"]) for r in coverage)
    lines = [
        "# LTMD-U1 — tablero maestro de cobertura",
        "",
        f"Versión: **{VERSION}**  ",
        f"Universo operativo U1: **{EXPECTED_U1} visores** del snapshot vigente del Catálogo Histórico de CONALITEG.  ",
        f"Familias normalizadas de título: **{family_count}**.",
        "",
        "## Estado ejecutivo",
        "",
        f"- Catálogo censado: **{EXPECTED_U1}/{EXPECTED_U1} (100.00%)**.",
        f"- Títulos normalizados: **{EXPECTED_U1}/{EXPECTED_U1} (100.00%)**.",
        f"- Activos completamente resueltos y demostrados: **{full_assets}/{EXPECTED_U1} ({100*full_assets/EXPECTED_U1:.2f}%)**; además **{partial_assets}** visores tienen resolución parcial documentada.",
        f"- FRAGSEG directamente materializado: **{direct_count}/{EXPECTED_U1} ({100*direct_count/EXPECTED_U1:.2f}%)**.",
        f"- Cobertura FRAGSEG efectiva, contando aliases byte-idénticos ya representados: **{effective_count}/{EXPECTED_U1} ({100*effective_count/EXPECTED_U1:.2f}%)**.",
        f"- Visores participantes en relaciones de dependencia ya registradas: **{dep_count}/{EXPECTED_U1} ({100*dep_count/EXPECTED_U1:.2f}%)**.",
        "- Cobertura semántica validada: **0/542 (0.00%)**; SEMB 0.3 continúa bloqueado por referencia humana.",
        "",
        "La cobertura efectiva no elimina ni fusiona visores: los aliases conservan su identidad de catálogo y simplemente evitan reprocesar bytes ya demostrados como idénticos.",
        "",
        "## Cobertura por dominio operativo",
        "",
        "| dominio | visores | % U1 | activos full | FRAGSEG directo | cobertura efectiva | restantes | próxima ola |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in domain_rows:
        lines.append(f"| {r['operational_domain']} | {r['viewer_count']} | {r['percent_of_u1']}% | {r['asset_resolved_full']} | {r['fragseg_materialized_direct']} | {r['effective_fragseg_coverage']} | {r['remaining_effective']} | {r['next_wave_label']} |")
    lines += [
        "",
        "## Regla de olas",
        "",
        "La taxonomía anterior es **operativa**, derivada sólo de palabras fuertes del título normalizado; no es una ontología curricular ni una clasificación semántica del contenido. Los títulos con señales de más de un dominio pasan a `integrados_multiarea`; los títulos sin señal suficientemente fuerte permanecen en `otros_no_clasificados` para revisión controlada.",
        "",
        "El orden de olas prioriza terminar Ciencias Naturales y después escalar a Matemáticas, Español/Lengua, Historia, Geografía/Atlas, Cívica/Ética, Artes, Educación Física, materiales integrados y finalmente títulos que requieren revisión operacional. Un alias verificado se considera cubierto efectivamente sin duplicar OCR/FRAGSEG.",
        "",
        "## Límites de lectura",
        "",
        "- `cataloged` no significa `asset_resolved`.",
        "- `asset_resolved` no significa `ocr_ready`.",
        "- `fragseg_materialized` no significa `semantic_ready`.",
        "- Una ocurrencia técnica no equivale a una observación histórica independiente.",
        "- Los estados se derivan conservadoramente de artefactos finales ya materializados; trabajo intermedio no terminado no se cuenta como cobertura de etapa.",
        "",
        "## Archivos",
        "",
        "- `data/catalog/ltmd_u1_coverage.csv` — matriz por visor.",
        "- `data/catalog/ltmd_u1_coverage_summary.csv` — KPIs por etapa.",
        "- `data/catalog/ltmd_u1_domain_summary.csv` — cobertura por dominio operativo.",
        "- `data/catalog/ltmd_u1_wave_queue.csv` — cola ordenada para industrialización.",
    ]
    OUT_REPORT.write_text("\n".join(lines)+"\n", encoding="utf-8")

    print(f"{VERSION}: U1={EXPECTED_U1}; direct_fragseg={direct_count}; effective_fragseg={effective_count}; full_assets={full_assets}; partial_assets={partial_assets}; families={family_count}")


if __name__ == "__main__":
    main()
