#!/usr/bin/env python3
"""Build current LTMD-U1 coverage from the frozen 0.2 baseline plus finalized W1 evidence.

A viewer is promoted stage-by-stage only when the final artifact for that stage
exists and passes conservative internal checks. In-progress jobs receive no credit.
"""
from __future__ import annotations

import csv
import subprocess
from collections import defaultdict
from pathlib import Path

BASE_SCRIPT = 'scripts/build_ltmd_u1_coverage.py'
COVERAGE = Path('data/catalog/ltmd_u1_coverage.csv')
SUMMARY = Path('data/catalog/ltmd_u1_coverage_summary.csv')
DOMAIN = Path('data/catalog/ltmd_u1_domain_summary.csv')
QUEUE = Path('data/catalog/ltmd_u1_wave_queue.csv')
REPORT = Path('data/catalog/ltmd_u1_coverage.md')
W1_SCOPE = Path('data/catalog/ltmd_u1_w1_scope.csv')

W1_1966_ASSET = Path('data/catalog/ltmd_u1_w1_1966_page_manifest_summary.csv')
W1_1966_OCR = Path('data/catalog/ltmd_u1_w1_1966_ocr_summary.csv')
W1_1966_PS = Path('data/catalog/ltmd_u1_w1_1966_page_structure_summary.csv')
W1_1966_FRAG = Path('data/catalog/ltmd_u1_w1_1966_fragment_manifest_summary.csv')

W1_2008_ASSET = Path('data/catalog/ltmd_u1_w1_2008_page_manifest_summary.csv')
W1_2008_OCR = Path('data/catalog/ltmd_u1_w1_2008_ocr_summary.csv')
W1_2008_PS = Path('data/catalog/ltmd_u1_w1_2008_page_structure_summary.csv')
W1_2008_FRAG = Path('data/catalog/ltmd_u1_w1_2008_fragment_manifest_summary.csv')

VERSION = 'LTMD_U1_COVERAGE_0.4'
U = 542


def rows(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_rows(path, records):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def promote_family(byv, book_to_viewer, asset_path, ocr_path, ps_path, frag_path, asset_label):
    if asset_path.exists():
        for s in rows(asset_path):
            viewer = book_to_viewer.get(s['book_id'])
            if not viewer:
                continue
            ready = int(s.get('asset_layer_ready', 0)) == 1
            unresolved = int(s.get('internal_unserved', s.get('unresolved_effective_positions', 0)) or 0)
            if ready and unresolved == 0:
                r = byv[viewer]
                r['book_id'] = s['book_id']
                r['asset_status'] = asset_label
                r['asset_resolved_full'] = '1'
                r['asset_resolved_partial'] = '0'
                r['page_manifest_ready'] = '1'

    if ocr_path.exists():
        for s in rows(ocr_path):
            viewer = book_to_viewer.get(s['book_id'])
            if not viewer:
                continue
            if int(s['pages']) == int(s['sha_verified']) and int(s['unresolved']) == 0:
                byv[viewer]['ocr_ready'] = '1'

    if ps_path.exists() and ocr_path.exists():
        ocr = {r['book_id']: r for r in rows(ocr_path)}
        for s in rows(ps_path):
            if s['book_id'] == 'ALL':
                continue
            viewer = book_to_viewer.get(s['book_id'])
            if viewer and s['book_id'] in ocr and int(s['n_pages']) == int(ocr[s['book_id']]['pages']):
                byv[viewer]['pagestruct_ready'] = '1'

    if frag_path.exists():
        for s in rows(frag_path):
            if s['book_id'] == 'ALL':
                continue
            viewer = book_to_viewer.get(s['book_id'])
            if not viewer:
                continue
            if int(s['fragment_count']) > 0 and int(s['segmented_page_count']) > 0:
                r = byv[viewer]
                r['fragseg_materialized'] = '1'
                r['effective_fragseg_coverage'] = '1'
                r['fragment_count_materialized'] = s['fragment_count']
                r['wave_priority'] = '0'
                r['wave_label'] = 'U1-W0-materializado'
                r['queue_status'] = 'materialized_direct'


def main():
    subprocess.run(['python3', BASE_SCRIPT], check=True)
    coverage = rows(COVERAGE)
    if len(coverage) != U:
        raise SystemExit(f'baseline coverage rows={len(coverage)} expected={U}')
    byv = {r['viewer_key']: r for r in coverage}

    scope = {r['viewer_key']: r for r in rows(W1_SCOPE)} if W1_SCOPE.exists() else {}
    scope_book_to_viewer = {r['book_id']: r['viewer_key'] for r in scope.values()}

    map_1966 = {
        book: viewer for book, viewer in scope_book_to_viewer.items()
        if viewer in {'H1966P6CI374', 'H1966P6CI375'}
    }
    map_2008 = {
        'LTMD-CN3-G2008': 'H2008P3CI263',
        'LTMD-CN4-G2008': 'H2008P4CI268',
    }

    promote_family(
        byv, map_1966,
        W1_1966_ASSET, W1_1966_OCR, W1_1966_PS, W1_1966_FRAG,
        'full_direct_w1_1966',
    )
    promote_family(
        byv, map_2008,
        W1_2008_ASSET, W1_2008_OCR, W1_2008_PS, W1_2008_FRAG,
        'full_direct_reconciled_w1_2008',
    )

    for r in coverage:
        r['coverage_version'] = VERSION
    write_rows(COVERAGE, coverage)

    def count(field):
        return sum(int(r[field]) for r in coverage)

    stages = [
        ('cataloged', count('cataloged'), 'All viewers in frozen U1 catalog snapshot.'),
        ('title_normalized', count('title_normalized'), 'Normalized title-core families.'),
        ('asset_resolved_full', count('asset_resolved_full'), 'Full source-asset resolution demonstrated.'),
        ('asset_resolved_partial', count('asset_resolved_partial'), 'Known partial source resolution; separate from full coverage.'),
        ('page_manifest_ready_direct', count('page_manifest_ready'), 'Direct page/source manifest materialized.'),
        ('ocr_ready_direct', count('ocr_ready'), 'Direct technical OCR layer materialized.'),
        ('pagestruct_ready_direct', count('pagestruct_ready'), 'Direct PAGESTRUCT layer materialized.'),
        ('fragseg_materialized_direct', count('fragseg_materialized'), 'Direct FRAGSEG materialized.'),
        ('effective_fragseg_coverage', count('effective_fragseg_coverage'), 'Direct FRAGSEG plus verified byte-identical aliases.'),
        ('dependence_audited', count('dependence_audited'), 'Viewer participates in registered documentary dependence.'),
        ('semantic_ready_validated', 0, 'SEMB 0.3 remains WAITING_HUMAN_REFERENCE.'),
    ]
    summary_rows = [
        {
            'coverage_version': VERSION,
            'stage': stage,
            'viewer_count': n,
            'universe_viewers': U,
            'percent': f'{100*n/U:.2f}',
            'notes': note,
        }
        for stage, n, note in stages
    ]
    write_rows(SUMMARY, summary_rows)

    old_domain = {r['operational_domain']: r for r in rows(DOMAIN)} if DOMAIN.exists() else {}
    grouped = defaultdict(list)
    for r in coverage:
        grouped[r['operational_domain']].append(r)
    domain_rows = []
    for domain, rr in grouped.items():
        total = len(rr)
        direct = sum(int(r['fragseg_materialized']) for r in rr)
        effective = sum(int(r['effective_fragseg_coverage']) for r in rr)
        full = sum(int(r['asset_resolved_full']) for r in rr)
        prior = old_domain.get(domain, {})
        queued = [r for r in rr if r['queue_status'] == 'queued']
        if queued:
            wave = prior.get('next_wave_label') or queued[0]['wave_label']
            priority = prior.get('next_wave_priority') or queued[0]['wave_priority']
        else:
            wave = 'completed_domain'
            priority = '0'
        domain_rows.append({
            'coverage_version': VERSION,
            'operational_domain': domain,
            'viewer_count': total,
            'percent_of_u1': f'{100*total/U:.2f}',
            'asset_resolved_full': full,
            'fragseg_materialized_direct': direct,
            'effective_fragseg_coverage': effective,
            'remaining_effective': total-effective,
            'next_wave_priority': priority,
            'next_wave_label': wave,
        })
    domain_rows.sort(key=lambda r: (int(r['next_wave_priority']) if str(r['next_wave_priority']).isdigit() else 999, r['operational_domain']))
    write_rows(DOMAIN, domain_rows)

    queue_fields = [
        'coverage_version','wave_priority','wave_label','queue_status','operational_domain',
        'viewer_key','catalog_generation','grade_code','title_core','asset_status',
        'effective_fragseg_coverage','coverage_inherited_from_viewer','source_url'
    ]
    queue_rows = sorted(coverage, key=lambda r: (int(r['wave_priority']), int(r['catalog_generation']), int(r['grade_code']), r['viewer_key']))
    with QUEUE.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=queue_fields)
        writer.writeheader()
        writer.writerows([{k: r[k] for k in queue_fields} for r in queue_rows])

    stage_map = {stage: n for stage, n, _ in stages}
    lines = [
        '# LTMD-U1 — tablero maestro de cobertura', '',
        f'Versión: **{VERSION}**  ',
        f'Universo operativo U1: **{U} visores**.  ',
        'Familias normalizadas de título: **191**.', '',
        '## Estado ejecutivo', '',
        f"- Catálogo censado: **{stage_map['cataloged']}/{U} ({100*stage_map['cataloged']/U:.2f}%)**.",
        f"- Títulos normalizados: **{stage_map['title_normalized']}/{U} ({100*stage_map['title_normalized']/U:.2f}%)**.",
        f"- Activos completamente resueltos: **{stage_map['asset_resolved_full']}/{U} ({100*stage_map['asset_resolved_full']/U:.2f}%)**; parciales documentados: **{stage_map['asset_resolved_partial']}**.",
        f"- Manifiesto directo: **{stage_map['page_manifest_ready_direct']}/{U} ({100*stage_map['page_manifest_ready_direct']/U:.2f}%)**.",
        f"- OCR directo: **{stage_map['ocr_ready_direct']}/{U} ({100*stage_map['ocr_ready_direct']/U:.2f}%)**.",
        f"- PAGESTRUCT directo: **{stage_map['pagestruct_ready_direct']}/{U} ({100*stage_map['pagestruct_ready_direct']/U:.2f}%)**.",
        f"- FRAGSEG directo: **{stage_map['fragseg_materialized_direct']}/{U} ({100*stage_map['fragseg_materialized_direct']/U:.2f}%)**.",
        f"- Cobertura FRAGSEG efectiva: **{stage_map['effective_fragseg_coverage']}/{U} ({100*stage_map['effective_fragseg_coverage']/U:.2f}%)**.",
        f"- Dependencia documental auditada: **{stage_map['dependence_audited']}/{U} ({100*stage_map['dependence_audited']/U:.2f}%)**.",
        '- Cobertura semántica validada: **0/542 (0.00%)**.', '',
        'Los KPIs se promueven por etapa sólo cuando existe el artefacto final correspondiente. Las tres recuperaciones 2008 conservan la anomalía original y la fuente efectiva en un manifiesto reconciliado.', '',
        '## Cobertura por dominio operativo', '',
        '| dominio | visores | % U1 | activos full | FRAGSEG directo | cobertura efectiva | restantes | próxima ola |',
        '|---|---:|---:|---:|---:|---:|---:|---|',
    ]
    for r in domain_rows:
        lines.append(f"| {r['operational_domain']} | {r['viewer_count']} | {r['percent_of_u1']}% | {r['asset_resolved_full']} | {r['fragseg_materialized_direct']} | {r['effective_fragseg_coverage']} | {r['remaining_effective']} | {r['next_wave_label']} |")
    lines += [
        '', '## Límites de lectura', '',
        '- `cataloged` no significa `asset_resolved`.',
        '- `asset_resolved` no significa `ocr_ready`.',
        '- `fragseg_materialized` no significa `semantic_ready`.',
        '- Cobertura efectiva por alias conserva identidad documental y evita reprocesar bytes demostrados como idénticos.',
        '- Recuperación puntual por continuidad criptográfica no equivale a identidad bibliográfica total entre ediciones.',
        '- La taxonomía de dominios es logística, no una ontología curricular.', '',
        '## Archivos', '',
        '- `data/catalog/ltmd_u1_coverage.csv`',
        '- `data/catalog/ltmd_u1_coverage_summary.csv`',
        '- `data/catalog/ltmd_u1_domain_summary.csv`',
        '- `data/catalog/ltmd_u1_wave_queue.csv`',
    ]
    REPORT.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(
        f"{VERSION}: assets={stage_map['asset_resolved_full']} "
        f"ocr={stage_map['ocr_ready_direct']} pagestruct={stage_map['pagestruct_ready_direct']} "
        f"fragseg={stage_map['fragseg_materialized_direct']} effective={stage_map['effective_fragseg_coverage']}"
    )


if __name__ == '__main__':
    main()
