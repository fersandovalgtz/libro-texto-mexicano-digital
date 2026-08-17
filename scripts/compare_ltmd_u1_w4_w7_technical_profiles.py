#!/usr/bin/env python3
"""Compare finalized LTMD-U1 W4 and source-admitted W7 technical profiles.

This comparison is deliberately nonsemantic. It compares processing outputs
created with shared technical contracts: PAGESTRUCT, frozen FRAGSEG mechanics,
and exact-text reuse. It does not assert curricular, pedagogical, historical, or
bibliographic equivalence between W4 Social Sciences and W7 Civics/Ethics.
"""
from __future__ import annotations

import csv
from pathlib import Path

W4_STRUCT = Path('data/catalog/ltmd_u1_w4_social_sciences_page_structure_summary.csv')
W7_STRUCT = Path('data/catalog/ltmd_u1_w7_civics_ethics_page_structure_summary.csv')
W4_FRAG = Path('data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest_summary.csv')
W7_FRAG = Path('data/catalog/ltmd_u1_w7_civics_ethics_fragment_manifest_summary.csv')
W4_UNITS = Path('data/catalog/ltmd_u1_w4_social_sciences_exact_content_units.csv')
W7_UNITS = Path('data/catalog/ltmd_u1_w7_civics_ethics_exact_content_units.csv')
W4_OVERLAP = Path('data/catalog/ltmd_u1_w4_social_sciences_exact_viewer_overlap.csv')
W7_OVERLAP = Path('data/catalog/ltmd_u1_w7_civics_ethics_exact_viewer_overlap.csv')
W7_COMPLETION = Path('docs/LTMD_U1_W7_COMPLETION.md')
OUT = Path('data/derived/ltmd_u1_w4_w7_technical_comparison.csv')
REPORT = Path('docs/LTMD_U1_W4_W7_TECHNICAL_COMPARISON.md')
VERSION = 'LTMD_U1_W4_W7_TECHNICAL_COMPARISON_0.1'

STRUCT_CLASSES = ['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown']
CANDIDATES = ['activity_candidate','assessment_candidate','experiment_candidate','expository_candidate','instruction_candidate','project_candidate','question_candidate','short_residual_candidate']


def read(path):
    if not path.exists():
        raise SystemExit(f'missing finalized comparison input: {path}')
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def all_row(rows, label):
    rr = [r for r in rows if r['viewer_key'] == 'ALL']
    if len(rr) != 1:
        raise SystemExit(f'{label}: expected exactly one ALL row')
    return rr[0]


def profile(name, struct_path, frag_path, units_path, overlap_path, expected_pages, expected_viewers, expected_struct_version, expected_frag_version, withheld):
    srows = read(struct_path); frows = read(frag_path); units = read(units_path); overlap = read(overlap_path)
    s = all_row(srows, name); f = all_row(frows, name)
    if int(s['n_pages']) != expected_pages:
        raise SystemExit(f'{name}: page count drift')
    if len([r for r in srows if r['viewer_key'] != 'ALL']) != expected_viewers:
        raise SystemExit(f'{name}: viewer count drift')
    if name == 'W7' and {r['classifier_version'] for r in read(Path('data/catalog/ltmd_u1_w7_civics_ethics_page_structure.csv'))} != {expected_struct_version}:
        raise SystemExit('W7 PAGESTRUCT version drift')
    if {r['segmenter_version'] for r in frows} != {expected_frag_version}:
        raise SystemExit(f'{name}: FRAGSEG version drift')
    pages = int(s['n_pages']); eligible = int(s['textual']) + int(s['mixed_text_image'])
    fragments = int(f['fragment_count']); segmented = int(f['segmented_page_count'])
    if segmented > eligible:
        raise SystemExit(f'{name}: segmented pages exceed eligible pages')
    unique_units = len(units)
    repeated = sum(int(r['occurrence_count']) > 1 for r in units)
    cross_viewer = sum(int(r['viewer_count']) > 1 for r in units)
    cross_generation = sum(int(r['catalog_generation_count']) > 1 for r in units)
    return {
        'corpus': name,
        'processed_viewers': expected_viewers,
        'source_withheld_viewers': withheld,
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


def pct(x): return f'{100*x:.2f}%'
def ratio(x): return f'{x:.3f}'


def main():
    if not W7_COMPLETION.exists():
        raise SystemExit('W7 technical completion report is required before cross-wave comparison')
    w4 = profile('W4', W4_STRUCT, W4_FRAG, W4_UNITS, W4_OVERLAP, 2414, 14,
                 'PAGESTRUCT_LTMD_U1_W4_SOCIAL_SCIENCES_0.1', 'FRAGSEG_LTMD_U1_W4_SOCIAL_SCIENCES_0.1', 0)
    w7 = profile('W7', W7_STRUCT, W7_FRAG, W7_UNITS, W7_OVERLAP, 3261, 25,
                 'PAGESTRUCT_LTMD_U1_W7_CIVICS_ETHICS_0.1', 'FRAGSEG_LTMD_U1_W7_CIVICS_ETHICS_0.1', 5)

    fields = list(w4)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows([w4, w7])

    lines = [
        '# LTMD-U1 — comparación técnica W4 Ciencias Sociales ↔ W7 Cívica/Ética',
        '', f'Versión: `{VERSION}`.', '',
        'Esta comparación usa únicamente capas técnicas producidas con contratos compatibles. **No compara validez curricular ni demuestra cambios históricos o pedagógicos por sí sola.** W7 además representa una cohorte técnicamente admisible de 25 identidades: cinco identidades históricas siguen retenidas por limitaciones de fuente.', '',
        '## Escala y estructura', '',
        '| métrica | W4 Ciencias Sociales | W7 Cívica/Ética |',
        '|---|---:|---:|',
        f"| objetos procesados | {w4['processed_viewers']} | {w7['processed_viewers']} |",
        f"| identidades retenidas por fuente | {w4['source_withheld_viewers']} | {w7['source_withheld_viewers']} |",
        f"| páginas | {w4['pages']:,} | {w7['pages']:,} |",
        f"| páginas PAGESTRUCT elegibles | {w4['eligible_pages']:,} ({pct(w4['eligible_page_rate'])}) | {w7['eligible_pages']:,} ({pct(w7['eligible_page_rate'])}) |",
        f"| fragmentos | {w4['fragments']:,} | {w7['fragments']:,} |",
        f"| fragmentos / página elegible | {ratio(w4['fragments_per_eligible_page'])} | {ratio(w7['fragments_per_eligible_page'])} |",
        '', '### Distribución PAGESTRUCT', '',
        '| clase | W4 | W7 |', '|---|---:|---:|',
    ]
    for c in STRUCT_CLASSES:
        lines.append(f"| `{c}` | {w4[f'struct_{c}_count']:,} ({pct(w4[f'struct_{c}_rate'])}) | {w7[f'struct_{c}_count']:,} ({pct(w7[f'struct_{c}_rate'])}) |")
    lines += ['', '## Tipos candidatos FRAGSEG', '', '| tipo | W4 | W7 |', '|---|---:|---:|']
    for c in CANDIDATES:
        lines.append(f"| `{c}` | {w4[f'candidate_{c}_count']:,} ({pct(w4[f'candidate_{c}_share'])}) | {w7[f'candidate_{c}_count']:,} ({pct(w7[f'candidate_{c}_share'])}) |")
    lines += [
        '', '## Reutilización textual exacta', '',
        '| métrica | W4 | W7 |', '|---|---:|---:|',
        f"| unidades exactas únicas | {w4['unique_exact_units']:,} | {w7['unique_exact_units']:,} |",
        f"| unidades repetidas | {w4['repeated_exact_units']:,} ({pct(w4['repeated_unit_rate'])}) | {w7['repeated_exact_units']:,} ({pct(w7['repeated_unit_rate'])}) |",
        f"| unidades en ≥2 visores | {w4['cross_viewer_exact_units']:,} ({pct(w4['cross_viewer_unit_rate'])}) | {w7['cross_viewer_exact_units']:,} ({pct(w7['cross_viewer_unit_rate'])}) |",
        f"| unidades en ≥2 generaciones | {w4['cross_generation_exact_units']:,} ({pct(w4['cross_generation_unit_rate'])}) | {w7['cross_generation_exact_units']:,} ({pct(w7['cross_generation_unit_rate'])}) |",
        f"| pares de visores con reuso exacto | {w4['viewer_pairs_with_exact_reuse']:,} | {w7['viewer_pairs_with_exact_reuse']:,} |",
        '', '## Límite inferencial', '',
        'Las diferencias de tasas son descriptivas de estos dos conjuntos procesados. W4 y W7 cubren dominios, generaciones e inventarios distintos; W7 además excluye cinco identidades por fuente no admisible. Por tanto, este producto sirve para formular hipótesis y controlar el comportamiento del pipeline, no para atribuir causalmente diferencias a reformas, asignaturas o periodos históricos sin un diseño analítico posterior y validación humana.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
