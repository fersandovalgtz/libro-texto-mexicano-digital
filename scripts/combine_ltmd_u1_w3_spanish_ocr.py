#!/usr/bin/env python3
"""Combine LTMD-U1 W3 Español/Lengua OCR shards with strict invariants."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

VERSION = 'LTMD_U1_W3_SPANISH_OCR_0.1'
MAN = Path('data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv')
PROC = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
OUT = Path('data/catalog/ltmd_u1_w3_spanish_ocr_metrics.csv')
SUMMARY = Path('data/catalog/ltmd_u1_w3_spanish_ocr_summary.csv')
REPORT = Path('data/catalog/ltmd_u1_w3_spanish_ocr.md')
EXPECTED_IDENTITIES = 130
EXPECTED_CANONICAL = 114
EXPECTED_ALIASES = 16
EXPECTED_SOURCE_PAGES = 20765
EXPECTED_PERSISTENT_GAPS = 8


def pid(row):
    return f"U1-{row['viewer_key']}-P{int(row['viewer_page']):03d}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', default='data/work/ltmd_u1_w3_spanish_ocr')
    args = parser.parse_args()

    proc_rows = list(csv.DictReader(PROC.open(encoding='utf-8', newline='')))
    if len(proc_rows) != EXPECTED_IDENTITIES:
        raise SystemExit(f'expected {EXPECTED_IDENTITIES} processing identities, got {len(proc_rows)}')
    proc = {r['viewer_key']: r for r in proc_rows}
    if len(proc) != EXPECTED_IDENTITIES:
        raise SystemExit('duplicate viewer_key in processing inventory')

    eligible = {k for k, r in proc.items() if r.get('ocr_identity_eligible') == '1'}
    canonical = {k for k, r in proc.items() if r.get('is_canonical_processing_object') == '1'}
    aliases = eligible - canonical
    if len(eligible) != EXPECTED_IDENTITIES or len(canonical) != EXPECTED_CANONICAL or len(aliases) != EXPECTED_ALIASES:
        raise SystemExit(f'W3 topology mismatch eligible={len(eligible)} canonical={len(canonical)} aliases={len(aliases)}')
    if any(proc[k]['canonical_processing_viewer_key'] not in canonical for k in eligible):
        raise SystemExit('identity points to noncanonical processing object')
    gaps = sum(int(proc[k].get('persistent_internal_source_gaps') or 0) for k in canonical)
    if gaps != EXPECTED_PERSISTENT_GAPS:
        raise SystemExit(f'expected {EXPECTED_PERSISTENT_GAPS} persistent gaps, got {gaps}')

    manifest = list(csv.DictReader(MAN.open(encoding='utf-8', newline='')))
    if len(manifest) != EXPECTED_SOURCE_PAGES:
        raise SystemExit(f'expected {EXPECTED_SOURCE_PAGES} canonical source pages, got {len(manifest)}')
    if {r['viewer_key'] for r in manifest} != canonical:
        raise SystemExit('canonical page manifest viewer coverage mismatch')
    expected_ids = {pid(r) for r in manifest}
    if len(expected_ids) != EXPECTED_SOURCE_PAGES:
        raise SystemExit('duplicate page IDs in canonical page manifest')

    files = sorted(Path(args.input_dir).rglob('ocr_*.csv'))
    if len(files) != EXPECTED_CANONICAL:
        raise SystemExit(f'expected {EXPECTED_CANONICAL} OCR shards, found {len(files)}')

    rows = []
    seen_viewers = []
    for path in files:
        shard = list(csv.DictReader(path.open(encoding='utf-8', newline='')))
        if not shard:
            raise SystemExit(f'empty OCR shard {path}')
        keys = {r['viewer_key'] for r in shard}
        versions = {r['ocr_version'] for r in shard}
        if len(keys) != 1 or versions != {VERSION}:
            raise SystemExit(f'invalid OCR shard {path}')
        seen_viewers.append(next(iter(keys)))
        rows.extend(shard)

    if set(seen_viewers) != canonical or len(seen_viewers) != len(set(seen_viewers)):
        raise SystemExit('OCR canonical viewer coverage/duplicate mismatch')

    got_ids = [r['page_id'] for r in rows]
    if len(rows) != EXPECTED_SOURCE_PAGES or len(set(got_ids)) != len(got_ids) or set(got_ids) != expected_ids:
        raise SystemExit(f'OCR page coverage mismatch rows={len(rows)} expected={EXPECTED_SOURCE_PAGES} unique={len(set(got_ids))}')
    if any(r['source_sha256_verified'] != '1' for r in rows):
        raise SystemExit('one or more W3 SHA checks failed')
    if any(r['ocr_class'] == 'unresolved' or r['ocr_status'] != 'ok' for r in rows):
        raise SystemExit('one or more W3 OCR rows unresolved/error')

    rows.sort(key=lambda r: (int(r['catalog_generation']), int(r['grade']), r['viewer_key'], int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    by_viewer = defaultdict(list)
    for row in rows:
        by_viewer[row['viewer_key']].append(row)

    summaries = []
    for key in sorted(canonical, key=lambda k: (int(proc[k]['catalog_generation']), int(proc[k]['grade_code']), k)):
        rr = by_viewer[key]
        summaries.append({
            'ocr_version': VERSION,
            'viewer_key': key,
            'catalog_generation': proc[key]['catalog_generation'],
            'grade_code': proc[key]['grade_code'],
            'title_core': proc[key]['title_core'],
            'processing_mode': proc[key]['processing_mode'],
            'persistent_internal_source_gaps': proc[key]['persistent_internal_source_gaps'],
            'pages': len(rr),
            'sha_verified': sum(r['source_sha256_verified'] == '1' for r in rr),
            'text_detected': sum(r['ocr_class'] == 'text_detected' for r in rr),
            'no_text_detected': sum(r['ocr_class'] == 'no_text_detected' for r in rr),
            'unresolved': sum(r['ocr_class'] == 'unresolved' for r in rr),
            'recognized_words': sum(int(r['recognized_words'] or 0) for r in rr),
            'ocr_chars': sum(int(r['ocr_chars'] or 0) for r in rr),
        })

    with SUMMARY.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    total = len(rows)
    text = sum(r['ocr_class'] == 'text_detected' for r in rows)
    no_text = sum(r['ocr_class'] == 'no_text_detected' for r in rows)
    exact_aliases = sum(proc[k]['processing_mode'] == 'exact_byte_alias' for k in aliases)
    route_aliases = sum(proc[k]['processing_mode'] == 'route_alias_2018_to_2019' for k in aliases)
    REPORT.write_text('\n'.join([
        '# LTMD-U1 W3 — OCR técnico de Español/Lengua',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Identidades W3 cubiertas operacionalmente: **{len(eligible)}/{EXPECTED_IDENTITIES}**.',
        f'- Objetos canónicos procesados una sola vez: **{len(summaries)}/{EXPECTED_CANONICAL}**.',
        f'- Aliases cubiertos por provenance sin recomputar OCR: **{len(aliases)}** (byte-exactos: **{exact_aliases}**; ruta 2018→2019: **{route_aliases}**).',
        f'- Huecos internos persistentes preservados sin renumeración: **{gaps}**.',
        f'- Páginas fuente canónicas procesadas: **{total:,}**.',
        f'- SHA-256 verificados: **{total:,}/{total:,}**.',
        f'- Texto detectado: **{text:,}/{total:,} ({100*text/total:.2f}%)**.',
        f'- `no_text_detected`: **{no_text:,}**.',
        '- `unresolved` en contenidos procesados: **0**.',
        '',
        'El OCR íntegro no se persiste. Esta capa conserva sólo métricas técnicas y controles de procedencia. La confianza interna de Tesseract se usa para triage técnico y no equivale a exactitud textual validada.',
        '',
        '## Límite epistemológico vigente',
        '',
        'No existe por ahora referencia humana para validación semántica. Por ello este producto autoriza PAGESTRUCT/FRAGSEG y análisis técnicos de estructura, reutilización y dependencia documental, pero no convierte clasificadores semánticos no validados en evidencia histórica primaria.'
    ]) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
