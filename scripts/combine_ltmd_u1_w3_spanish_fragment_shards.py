#!/usr/bin/env python3
"""Combine canonical LTMD-U1 W3 Español/Lengua FRAGSEG shards with integrity checks."""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

STRUCT = Path('data/catalog/ltmd_u1_w3_spanish_page_structure.csv')
PROC = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
OUT = Path('data/catalog/ltmd_u1_w3_spanish_fragment_manifest.csv')
SUMMARY = Path('data/catalog/ltmd_u1_w3_spanish_fragment_manifest_summary.csv')
GAPS = Path('data/catalog/ltmd_u1_w3_spanish_fragment_sequence_gaps.csv')
REPORT = Path('data/catalog/ltmd_u1_w3_spanish_fragment_manifest.md')
VERSION = 'FRAGSEG_LTMD_U1_W3_SPANISH_0.1'
ELIGIBLE = {'textual','mixed_text_image'}
EXPECTED_CANONICAL = 114
EXPECTED_IDENTITIES = 130
EXPECTED_ALIASES = 16
EXPECTED_PERSISTENT_GAPS = 8


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', default='data/work/ltmd_u1_w3_spanish_fragments')
    args = parser.parse_args()

    structure = list(csv.DictReader(STRUCT.open(encoding='utf-8', newline='')))
    viewers = {r['viewer_key'] for r in structure}
    eligible = {(r['viewer_key'], r['page_id']) for r in structure if r['primary_structure'] in ELIGIBLE}
    if len(viewers) != EXPECTED_CANONICAL:
        raise SystemExit(f'expected {EXPECTED_CANONICAL} canonical PAGESTRUCT viewers, found {len(viewers)}')

    proc_rows = list(csv.DictReader(PROC.open(encoding='utf-8', newline='')))
    if len(proc_rows) != EXPECTED_IDENTITIES:
        raise SystemExit('W3 processing inventory cardinality mismatch')
    canonical = {r['viewer_key'] for r in proc_rows if r['is_canonical_processing_object'] == '1'}
    aliases = {r['viewer_key'] for r in proc_rows if r['ocr_identity_eligible'] == '1'} - canonical
    persistent_gaps = sum(int(r['persistent_internal_source_gaps'] or 0) for r in proc_rows if r['viewer_key'] in canonical)
    if canonical != viewers or len(aliases) != EXPECTED_ALIASES or persistent_gaps != EXPECTED_PERSISTENT_GAPS:
        raise SystemExit('W3 FRAGSEG processing topology mismatch')

    files = sorted(p for p in Path(args.input_dir).rglob('fragment_*.csv') if not p.name.endswith('_failures.csv'))
    failfiles = sorted(Path(args.input_dir).rglob('fragment_*_failures.csv'))
    if len(files) != EXPECTED_CANONICAL or len(failfiles) != EXPECTED_CANONICAL:
        raise SystemExit(f'expected {EXPECTED_CANONICAL} fragment and failure shards, got {len(files)} / {len(failfiles)}')

    rows = []
    seen = []
    empty_pages = []
    failure_by_stem = {}
    for path in failfiles:
        failrows = list(csv.DictReader(path.open(encoding='utf-8', newline='')))
        failure_by_stem[path.name.replace('_failures.csv', '.csv')] = failrows
        for row in failrows:
            if row['status'] != 'ok':
                raise SystemExit(f'fatal FRAGSEG failure persisted: {row}')
            empty_pages.append((row['viewer_key'], row['page_id']))

    for path in files:
        shard = list(csv.DictReader(path.open(encoding='utf-8', newline='')))
        failrows = failure_by_stem.get(path.name, [])
        keys = {r['viewer_key'] for r in shard} | {r['viewer_key'] for r in failrows}
        if len(keys) != 1:
            raise SystemExit(f'cannot identify exactly one viewer for shard {path}')
        key = next(iter(keys))
        if shard and {r['segmenter_version'] for r in shard} != {VERSION}:
            raise SystemExit(f'invalid segmenter version in {path}')
        seen.append(key)
        rows.extend(shard)

    if set(seen) != viewers or len(seen) != EXPECTED_CANONICAL or len(seen) != len(set(seen)):
        raise SystemExit('canonical viewer coverage mismatch')

    ids = [r['fragment_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit(f'duplicate fragment IDs: {len(ids)-len(set(ids))}')
    pagekeys = {(r['viewer_key'], r['page_id']) for r in rows} | set(empty_pages)
    if pagekeys != eligible:
        raise SystemExit(f'eligible PAGESTRUCT coverage mismatch missing={len(eligible-pagekeys)} extra={len(pagekeys-eligible)}')

    bypage = defaultdict(list)
    for row in rows:
        bypage[(row['viewer_key'], row['page_id'])].append(int(row['fragment_sequence']))
    gaprows = []
    for (key, page_id), vals in sorted(bypage.items()):
        seq = sorted(vals)
        if any(v <= 0 for v in seq) or len(seq) != len(set(seq)):
            raise SystemExit(f'invalid fragment sequence {key} {page_id}: {seq}')
        missing = [x for x in range(1, max(seq) + 1) if x not in set(seq)] if seq else []
        if missing:
            gaprows.append({
                'viewer_key': key,
                'page_id': page_id,
                'observed_fragment_count': len(seq),
                'max_sequence': max(seq),
                'missing_sequence_slots': ' '.join(map(str, missing)),
                'missing_slot_count': len(missing),
            })

    rows.sort(key=lambda r: (int(r['catalog_generation']), int(r['grade']), r['viewer_key'], int(r['viewer_page']), int(r['fragment_sequence'])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with OUT.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    else:
        raise SystemExit('W3 FRAGSEG produced zero fragments globally')

    if gaprows:
        with GAPS.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(gaprows[0]))
            writer.writeheader()
            writer.writerows(gaprows)
    else:
        GAPS.write_text('viewer_key,page_id,observed_fragment_count,max_sequence,missing_sequence_slots,missing_slot_count\n', encoding='utf-8')

    types = sorted({r['candidate_type'] for r in rows})
    counts = defaultdict(Counter)
    pages = defaultdict(set)
    for row in rows:
        counts[row['viewer_key']][row['candidate_type']] += 1
        counts['ALL'][row['candidate_type']] += 1
        pages[row['viewer_key']].add(row['page_id'])
        pages['ALL'].add(row['page_id'])

    summary = []
    for key in sorted(viewers) + ['ALL']:
        c = counts[key]
        rec = {
            'segmenter_version': VERSION,
            'viewer_key': key,
            'fragment_count': sum(c.values()),
            'segmented_page_count': len(pages[key]),
        }
        rec.update({t: c[t] for t in types})
        summary.append(rec)
    with SUMMARY.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    allc = summary[-1]
    gap_slots = sum(int(r['missing_slot_count']) for r in gaprows)
    lines = [
        '# FRAGSEG — LTMD-U1 W3 Español/Lengua',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Objetos canónicos computados: **{EXPECTED_CANONICAL}**.',
        f'- Identidades de catálogo cubiertas operacionalmente: **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}** mediante **{EXPECTED_ALIASES}** aliases de provenance.',
        f'- Huecos internos de fuente persistentes preservados sin renumeración: **{EXPECTED_PERSISTENT_GAPS}**.',
        f'- Páginas elegibles PAGESTRUCT: **{len(eligible):,}**.',
        f'- Páginas con ≥1 fragmento: **{allc["segmented_page_count"]:,}**.',
        f'- Páginas elegibles sin fragmentos: **{len(empty_pages)}**.',
        f'- Fragmentos: **{allc["fragment_count"]:,}**.',
        f'- IDs únicos: **{len(set(ids)):,}**.',
        f'- Páginas con huecos legítimos de secuencia: **{len(gaprows)}**.',
        f'- Slots omitidos: **{gap_slots}**.',
        '',
        '## Tipos candidatos',
    ]
    for typ in types:
        lines.append(f'- `{typ}`: {allc[typ]:,}.')
    lines += [
        '',
        '## Regla',
        '`fragment_sequence` conserva la posición previa al descarte de candidatos de 0 tokens; se admiten huecos positivos auditados sin renumerar IDs. Cualquier fallo de descarga, SHA u OCR de ejecución hace fallar el shard. El texto completo no se persiste. `short_residual_candidate` es una categoría técnica residual, no evidencia tipográfica ni pedagógica. Esta capa no es `semantic_ready`.',
        '',
        '## Límite actual',
        'El proyecto opera temporalmente sin referencia humana. FRAGSEG puede usarse para estructura, conteos técnicos, reutilización exacta y dependencia documental; no valida por sí mismo categorías pedagógicas o semánticas.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
