#!/usr/bin/env python3
"""Build exact-text reuse and document-dependence views for LTMD-U1 W3 Español/Lengua.

No full text is required. Equality is defined only by FRAGSEG text_sha256 and
must not be interpreted as bibliographic, curricular, pedagogical, or semantic
equivalence.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

FRAGS = Path('data/catalog/ltmd_u1_w3_spanish_fragment_manifest.csv')
PROC = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
UNITS = Path('data/catalog/ltmd_u1_w3_spanish_exact_content_units.csv')
IDENTITIES = Path('data/catalog/ltmd_u1_w3_spanish_identity_content_projection.csv')
OVERLAP = Path('data/catalog/ltmd_u1_w3_spanish_exact_viewer_overlap.csv')
REPORT = Path('data/catalog/ltmd_u1_w3_spanish_exact_reuse.md')
VERSION = 'LTMD_U1_W3_SPANISH_EXACT_REUSE_0.1'
EXPECTED_IDENTITIES = 130
EXPECTED_CANONICAL = 114
EXPECTED_ALIASES = 16


def fmt(x):
    return f'{x:.6f}'


def main():
    frags = list(csv.DictReader(FRAGS.open(encoding='utf-8', newline='')))
    proc_rows = list(csv.DictReader(PROC.open(encoding='utf-8', newline='')))
    if not frags:
        raise SystemExit('no W3 fragment manifest')
    if len(proc_rows) != EXPECTED_IDENTITIES:
        raise SystemExit(f'expected {EXPECTED_IDENTITIES} W3 identities, got {len(proc_rows)}')
    proc = {r['viewer_key']: r for r in proc_rows}
    if len(proc) != EXPECTED_IDENTITIES:
        raise SystemExit('duplicate W3 identity')
    canonical = {r['viewer_key'] for r in proc_rows if r['is_canonical_processing_object'] == '1'}
    eligible = {r['viewer_key'] for r in proc_rows if r['ocr_identity_eligible'] == '1'}
    aliases = eligible - canonical
    if len(canonical) != EXPECTED_CANONICAL or len(aliases) != EXPECTED_ALIASES or len(eligible) != EXPECTED_IDENTITIES:
        raise SystemExit('W3 processing topology mismatch')
    exact_aliases = {k for k in aliases if proc[k]['processing_mode'] == 'exact_byte_alias'}
    route_aliases = {k for k in aliases if proc[k]['processing_mode'] == 'paired_route_alias_2018_to_2019'}
    if len(exact_aliases) != 8 or len(route_aliases) != 8 or exact_aliases | route_aliases != aliases:
        raise SystemExit(f'W3 alias vocabulary/topology mismatch exact={len(exact_aliases)} route={len(route_aliases)}')
    if {r['viewer_key'] for r in frags} != canonical:
        raise SystemExit('FRAGSEG canonical viewer coverage mismatch')
    versions = {r['segmenter_version'] for r in frags}
    if versions != {'FRAGSEG_LTMD_U1_W3_SPANISH_0.1'}:
        raise SystemExit(f'unexpected FRAGSEG version(s): {versions}')
    ids = [r['fragment_id'] for r in frags]
    if len(ids) != len(set(ids)):
        raise SystemExit('duplicate fragment IDs')

    represented = defaultdict(set)
    for identity, row in proc.items():
        represented[row['canonical_processing_viewer_key']].add(identity)
    if set(represented) != canonical or sum(len(v) for v in represented.values()) != EXPECTED_IDENTITIES:
        raise SystemExit('identity→canonical projection mismatch')

    by_hash = defaultdict(list)
    by_viewer_hashes = defaultdict(set)
    by_viewer_count = Counter()
    for row in frags:
        h = row['text_sha256']
        if not h:
            raise SystemExit(f'missing text_sha256 for {row["fragment_id"]}')
        by_hash[h].append(row)
        by_viewer_hashes[row['viewer_key']].add(h)
        by_viewer_count[row['viewer_key']] += 1

    unit_rows = []
    for h, rows in by_hash.items():
        viewers = {r['viewer_key'] for r in rows}
        identity_set = set()
        for key in viewers:
            identity_set |= represented[key]
        generations = {proc[i]['catalog_generation'] for i in identity_set}
        grades = {proc[i]['grade_code'] for i in identity_set}
        token_counts = {r['token_count'] for r in rows}
        char_counts = {r['char_count'] for r in rows}
        if len(token_counts) != 1 or len(char_counts) != 1:
            raise SystemExit(f'exact hash has inconsistent length metrics: {h}')
        unit_rows.append({
            'analysis_version': VERSION,
            'text_sha256': h,
            'token_count': next(iter(token_counts)),
            'char_count': next(iter(char_counts)),
            'canonical_occurrence_count': len(rows),
            'canonical_viewer_count': len(viewers),
            'represented_catalog_identity_count': len(identity_set),
            'represented_catalog_generation_count': len(generations),
            'represented_grade_count': len(grades),
            'first_fragment_id': min(r['fragment_id'] for r in rows),
        })
    unit_rows.sort(key=lambda r: (-int(r['canonical_occurrence_count']), r['text_sha256']))
    with UNITS.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(unit_rows[0]))
        writer.writeheader()
        writer.writerows(unit_rows)

    identity_rows = []
    for identity in sorted(proc, key=lambda k: (int(proc[k]['catalog_generation']), int(proc[k]['grade_code']), k)):
        row = proc[identity]
        canon = row['canonical_processing_viewer_key']
        identity_rows.append({
            'analysis_version': VERSION,
            'viewer_key': identity,
            'catalog_generation': row['catalog_generation'],
            'grade_code': row['grade_code'],
            'title_core': row['title_core'],
            'processing_mode': row['processing_mode'],
            'canonical_processing_viewer_key': canon,
            'inherited_from_canonical': int(identity != canon),
            'canonical_fragment_occurrences': by_viewer_count[canon],
            'canonical_unique_text_units': len(by_viewer_hashes[canon]),
            'persistent_internal_source_gaps': row['persistent_internal_source_gaps'],
        })
    with IDENTITIES.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(identity_rows[0]))
        writer.writeheader()
        writer.writerows(identity_rows)

    overlap_rows = []
    viewer_order = sorted(canonical, key=lambda k: (int(proc[k]['catalog_generation']), int(proc[k]['grade_code']), k))
    for a, b in combinations(viewer_order, 2):
        sa, sb = by_viewer_hashes[a], by_viewer_hashes[b]
        shared = len(sa & sb)
        if not shared:
            continue
        union = len(sa | sb)
        overlap_rows.append({
            'analysis_version': VERSION,
            'viewer_a': a,
            'viewer_b': b,
            'generation_a': proc[a]['catalog_generation'],
            'generation_b': proc[b]['catalog_generation'],
            'grade_a': proc[a]['grade_code'],
            'grade_b': proc[b]['grade_code'],
            'same_generation': int(proc[a]['catalog_generation'] == proc[b]['catalog_generation']),
            'same_grade': int(proc[a]['grade_code'] == proc[b]['grade_code']),
            'unique_units_a': len(sa),
            'unique_units_b': len(sb),
            'shared_unique_units': shared,
            'jaccard': fmt(shared / union),
            'containment_a_in_b': fmt(shared / len(sa)),
            'containment_b_in_a': fmt(shared / len(sb)),
        })
    overlap_rows.sort(key=lambda r: (-int(r['shared_unique_units']), -float(r['jaccard']), r['viewer_a'], r['viewer_b']))
    if overlap_rows:
        with OVERLAP.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(overlap_rows[0]))
            writer.writeheader()
            writer.writerows(overlap_rows)
    else:
        OVERLAP.write_text('analysis_version,viewer_a,viewer_b,generation_a,generation_b,grade_a,grade_b,same_generation,same_grade,unique_units_a,unique_units_b,shared_unique_units,jaccard,containment_a_in_b,containment_b_in_a\n', encoding='utf-8')

    repeated = sum(int(r['canonical_occurrence_count']) > 1 for r in unit_rows)
    cross_viewer = sum(int(r['canonical_viewer_count']) > 1 for r in unit_rows)
    cross_generation = sum(int(r['represented_catalog_generation_count']) > 1 for r in unit_rows)
    top = overlap_rows[:20]
    lines = [
        '# LTMD-U1 W3 Español/Lengua — reutilización textual exacta y dependencia documental',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Fragmentos canónicos (ocurrencias): **{len(frags):,}**.',
        f'- Unidades textuales exactas únicas (`text_sha256`): **{len(unit_rows):,}**.',
        f'- Unidades repetidas en ≥2 ocurrencias canónicas: **{repeated:,}**.',
        f'- Unidades presentes en ≥2 visores canónicos: **{cross_viewer:,}**.',
        f'- Unidades representadas en ≥2 generaciones de catálogo, incluyendo proyección de aliases: **{cross_generation:,}**.',
        f'- Visores canónicos: **{EXPECTED_CANONICAL}**; identidades de catálogo proyectadas: **{EXPECTED_IDENTITIES}**.',
        f'- Aliases proyectados: **{len(aliases)}** (byte-exactos: **{len(exact_aliases)}**; ruta pareada 2018→2019: **{len(route_aliases)}**).',
        f'- Pares canónicos con ≥1 unidad exacta compartida: **{len(overlap_rows):,}**.',
        '',
        '## Pares con mayor número de unidades exactas compartidas',
        '',
        '| Visor A | Visor B | Compartidas | Jaccard | Contención A→B | Contención B→A |',
        '|---|---|---:|---:|---:|---:|',
    ]
    for row in top:
        lines.append(f"| `{row['viewer_a']}` | `{row['viewer_b']}` | {row['shared_unique_units']} | {row['jaccard']} | {row['containment_a_in_b']} | {row['containment_b_in_a']} |")
    lines += [
        '',
        '## Interpretación permitida',
        '',
        'La igualdad de `text_sha256` documenta reutilización textual exacta dentro de la representación OCR+FRAGSEG fijada. No demuestra por sí sola identidad bibliográfica, equivalencia curricular, equivalencia pedagógica ni equivalencia semántica. Los aliases de catálogo permanecen como identidades separadas y sólo heredan productos técnicos de su canónico mediante provenance.',
        '',
        'Este análisis es compatible con el modo operativo sin referencia humana porque no evalúa verdad terreno semántica ni desempeño de un clasificador pedagógico.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
