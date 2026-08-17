#!/usr/bin/env python3
"""Compare finalized LTMD-U1 W3, W4 and source-admitted W7 technical profiles.

This is a descriptive engineering comparison only. W3 Spanish/Language, W4
Social Sciences and W7 Civics/Ethics have different domains, historical
coverage, source topologies and catalog semantics. Shared PAGESTRUCT, FRAGSEG
and exact-text-reuse representations make technical descriptors comparable;
they do not make the corpora curricular, pedagogical, historical or
bibliographic equivalents.
"""
from __future__ import annotations

import csv
from pathlib import Path

from compare_ltmd_u1_w4_w7_technical_profiles import (
    CANDIDATES,
    STRUCT_CLASSES,
    all_row,
    pct,
    profile,
    ratio,
    read,
)

VERSION = 'LTMD_U1_W3_W4_W7_TECHNICAL_COMPARISON_0.2'
OUT = Path('data/derived/ltmd_u1_w3_w4_w7_technical_comparison.csv')
REPORT = Path('docs/LTMD_U1_W3_W4_W7_TECHNICAL_COMPARISON.md')

W3_STRUCT = Path('data/catalog/ltmd_u1_w3_spanish_page_structure_summary.csv')
W3_FRAG = Path('data/catalog/ltmd_u1_w3_spanish_fragment_manifest_summary.csv')
W3_UNITS = Path('data/catalog/ltmd_u1_w3_spanish_exact_content_units.csv')
W3_OVERLAP = Path('data/catalog/ltmd_u1_w3_spanish_exact_viewer_overlap.csv')
W3_COMPLETION = Path('docs/LTMD_U1_W3_COMPLETION.md')

W4_STRUCT = Path('data/catalog/ltmd_u1_w4_social_sciences_page_structure_summary.csv')
W4_FRAG = Path('data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest_summary.csv')
W4_UNITS = Path('data/catalog/ltmd_u1_w4_social_sciences_exact_content_units.csv')
W4_OVERLAP = Path('data/catalog/ltmd_u1_w4_social_sciences_exact_viewer_overlap.csv')
W4_COMPLETION = Path('docs/LTMD_U1_W4_COMPLETION.md')

W7_STRUCT = Path('data/catalog/ltmd_u1_w7_civics_ethics_page_structure_summary.csv')
W7_FRAG = Path('data/catalog/ltmd_u1_w7_civics_ethics_fragment_manifest_summary.csv')
W7_UNITS = Path('data/catalog/ltmd_u1_w7_civics_ethics_exact_content_units.csv')
W7_OVERLAP = Path('data/catalog/ltmd_u1_w7_civics_ethics_exact_viewer_overlap.csv')
W7_COMPLETION = Path('docs/LTMD_U1_W7_COMPLETION.md')


def profile_w3() -> dict[str, int | float | str]:
    """Normalize W3's provenance-aware exact-reuse schema to the common profile.

    W3 deliberately names its counters `canonical_*` and
    `represented_catalog_generation_count` because 16 catalog identities are
    projected through explicit provenance aliases onto 114 canonical processing
    objects. Those fields are semantically different from W4/W7's simpler
    schema, so the mapping is explicit here rather than hidden in the shared
    W4/W7 helper.
    """
    srows = read(W3_STRUCT)
    frows = read(W3_FRAG)
    units = read(W3_UNITS)
    overlap = read(W3_OVERLAP)
    s = all_row(srows, 'W3')
    f = all_row(frows, 'W3')

    if int(s['n_pages']) != 20765:
        raise SystemExit('W3: page count drift')
    if len([r for r in srows if r['viewer_key'] != 'ALL']) != 114:
        raise SystemExit('W3: canonical viewer count drift')
    if {r['segmenter_version'] for r in frows} != {'FRAGSEG_LTMD_U1_W3_SPANISH_0.1'}:
        raise SystemExit('W3: FRAGSEG version drift')

    required_unit_fields = {
        'canonical_occurrence_count',
        'canonical_viewer_count',
        'represented_catalog_generation_count',
    }
    if units and not required_unit_fields.issubset(units[0]):
        raise SystemExit(f'W3: unexpected exact-unit schema: {sorted(units[0])}')

    pages = int(s['n_pages'])
    eligible = int(s['textual']) + int(s['mixed_text_image'])
    fragments = int(f['fragment_count'])
    segmented = int(f['segmented_page_count'])
    if segmented != eligible:
        raise SystemExit(f'W3: segmented/eligible mismatch {segmented} != {eligible}')

    unique_units = len(units)
    repeated = sum(int(r['canonical_occurrence_count']) > 1 for r in units)
    cross_viewer = sum(int(r['canonical_viewer_count']) > 1 for r in units)
    cross_generation = sum(int(r['represented_catalog_generation_count']) > 1 for r in units)

    return {
        'corpus': 'W3',
        'processed_viewers': 114,
        'source_withheld_viewers': 0,
        'pages': pages,
        'eligible_pages': eligible,
        'eligible_page_rate': eligible / pages,
        'segmented_pages': segmented,
        'fragments': fragments,
        'fragments_per_eligible_page': fragments / eligible,
        'unique_exact_units': unique_units,
        'repeated_exact_units': repeated,
        'repeated_unit_rate': repeated / unique_units,
        'cross_viewer_exact_units': cross_viewer,
        'cross_viewer_unit_rate': cross_viewer / unique_units,
        'cross_generation_exact_units': cross_generation,
        'cross_generation_unit_rate': cross_generation / unique_units,
        'viewer_pairs_with_exact_reuse': len(overlap),
        **{f'struct_{c}_count': int(s[c]) for c in STRUCT_CLASSES},
        **{f'struct_{c}_rate': int(s[c]) / pages for c in STRUCT_CLASSES},
        **{f'candidate_{c}_count': int(f[c]) for c in CANDIDATES},
        **{f'candidate_{c}_share': int(f[c]) / fragments for c in CANDIDATES},
    }


def main() -> None:
    for completion in (W3_COMPLETION, W4_COMPLETION, W7_COMPLETION):
        if not completion.exists():
            raise SystemExit(f'missing technical completion prerequisite: {completion}')

    profiles = [
        profile_w3(),
        profile(
            'W4', W4_STRUCT, W4_FRAG, W4_UNITS, W4_OVERLAP,
            2414, 14,
            'PAGESTRUCT_LTMD_U1_W4_SOCIAL_SCIENCES_0.1',
            'FRAGSEG_LTMD_U1_W4_SOCIAL_SCIENCES_0.1',
            0,
        ),
        profile(
            'W7', W7_STRUCT, W7_FRAG, W7_UNITS, W7_OVERLAP,
            3261, 25,
            'PAGESTRUCT_LTMD_U1_W7_CIVICS_ETHICS_0.1',
            'FRAGSEG_LTMD_U1_W7_CIVICS_ETHICS_0.1',
            5,
        ),
    ]

    expected = {
        'W3': {
            'eligible_pages': 17337,
            'fragments': 222490,
            'unique_exact_units': 147375,
            'repeated_exact_units': 40956,
            'cross_viewer_exact_units': 40118,
            'cross_generation_exact_units': 50144,
            'viewer_pairs_with_exact_reuse': 6387,
        },
        'W4': {'eligible_pages': 2018, 'fragments': 21380, 'unique_exact_units': 17735},
        'W7': {'eligible_pages': 2745, 'fragments': 33451, 'unique_exact_units': 22651},
    }
    for p in profiles:
        for field, value in expected[p['corpus']].items():
            if p[field] != value:
                raise SystemExit(f"{p['corpus']}: {field} drift: {p[field]} != {value}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(profiles[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(profiles)

    by = {p['corpus']: p for p in profiles}
    headers = ['W3 Español/Lengua', 'W4 Ciencias Sociales', 'W7 Cívica/Ética']
    keys = ['W3', 'W4', 'W7']
    lines = [
        '# LTMD-U1 — comparación técnica W3 ↔ W4 ↔ W7',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Comparación **estrictamente técnica y descriptiva** entre productos cerrados de PAGESTRUCT, FRAGSEG y reutilización textual exacta. Las tres cohortes tienen dominios, inventarios y coberturas históricas diferentes. Los porcentajes sirven para caracterizar las representaciones computacionales y formular hipótesis posteriores; **no demuestran diferencias curriculares, pedagógicas ni efectos de reformas**.',
        '',
        'W7 representa sólo su cohorte fuente-admisible (25 objetos) y mantiene cinco identidades históricas retenidas. W3 incluye 16 aliases explícitos de provenance proyectados sobre 114 canónicos; para W3, las métricas entre generaciones incorporan esa proyección tal como la definió su cierre técnico.',
        '',
        '## Escala',
        '',
        '| métrica | ' + ' | '.join(headers) + ' |',
        '|---|' + '|'.join(['---:'] * 3) + '|',
        '| objetos canónicos procesados | ' + ' | '.join(f"{by[k]['processed_viewers']:,}" for k in keys) + ' |',
        '| identidades retenidas por fuente | ' + ' | '.join(f"{by[k]['source_withheld_viewers']:,}" for k in keys) + ' |',
        '| páginas | ' + ' | '.join(f"{by[k]['pages']:,}" for k in keys) + ' |',
        '| páginas elegibles | ' + ' | '.join(f"{by[k]['eligible_pages']:,} ({pct(by[k]['eligible_page_rate'])})" for k in keys) + ' |',
        '| fragmentos | ' + ' | '.join(f"{by[k]['fragments']:,}" for k in keys) + ' |',
        '| fragmentos / página elegible | ' + ' | '.join(ratio(by[k]['fragments_per_eligible_page']) for k in keys) + ' |',
        '',
        '## PAGESTRUCT',
        '',
        '| clase | ' + ' | '.join(headers) + ' |',
        '|---|' + '|'.join(['---:'] * 3) + '|',
    ]
    for c in STRUCT_CLASSES:
        lines.append(
            f"| `{c}` | " + ' | '.join(
                f"{by[k][f'struct_{c}_count']:,} ({pct(by[k][f'struct_{c}_rate'])})" for k in keys
            ) + ' |'
        )

    lines += [
        '',
        '## FRAGSEG — tipos candidatos técnicos',
        '',
        '| tipo | ' + ' | '.join(headers) + ' |',
        '|---|' + '|'.join(['---:'] * 3) + '|',
    ]
    for c in CANDIDATES:
        lines.append(
            f"| `{c}` | " + ' | '.join(
                f"{by[k][f'candidate_{c}_count']:,} ({pct(by[k][f'candidate_{c}_share'])})" for k in keys
            ) + ' |'
        )

    lines += [
        '',
        '## Reutilización textual exacta',
        '',
        '| métrica | ' + ' | '.join(headers) + ' |',
        '|---|' + '|'.join(['---:'] * 3) + '|',
        '| unidades exactas únicas | ' + ' | '.join(f"{by[k]['unique_exact_units']:,}" for k in keys) + ' |',
        '| unidades repetidas | ' + ' | '.join(f"{by[k]['repeated_exact_units']:,} ({pct(by[k]['repeated_unit_rate'])})" for k in keys) + ' |',
        '| unidades en ≥2 visores | ' + ' | '.join(f"{by[k]['cross_viewer_exact_units']:,} ({pct(by[k]['cross_viewer_unit_rate'])})" for k in keys) + ' |',
        '| unidades en ≥2 generaciones | ' + ' | '.join(f"{by[k]['cross_generation_exact_units']:,} ({pct(by[k]['cross_generation_unit_rate'])})" for k in keys) + ' |',
        '| pares de visores con reuso exacto | ' + ' | '.join(f"{by[k]['viewer_pairs_with_exact_reuse']:,}" for k in keys) + ' |',
        '',
        '### Nota de schema W3',
        '',
        'W3 usa `canonical_occurrence_count`, `canonical_viewer_count` y `represented_catalog_generation_count`; W4/W7 usan el schema posterior `occurrence_count`, `viewer_count` y `catalog_generation_count`. La normalización de W3 es explícita en el script y conserva la semántica de su proyección de aliases. No se renombran columnas de origen ni se reescriben sus productos cerrados.',
        '',
        '## Uso permitido',
        '',
        'Este producto permite auditar escala, densidad de segmentación, distribución estructural y dependencia textual dentro del pipeline común. Las diferencias observadas pueden motivar preguntas de investigación, pero cualquier interpretación histórica o curricular requiere modelar bibliografía/temporalidad, composición de la cohorte y validación humana por separado.',
        '',
        '## Uso no permitido',
        '',
        'No se debe interpretar una tasa mayor o menor como evidencia directa de calidad educativa, complejidad pedagógica, efecto de una reforma, continuidad curricular o cambio histórico. Tampoco se deben comparar las generaciones de catálogo como si fueran automáticamente años editoriales.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('version', VERSION)
    for p in profiles:
        print(p['corpus'], p['processed_viewers'], p['pages'], p['eligible_pages'], p['fragments'], p['unique_exact_units'])


if __name__ == '__main__':
    main()
