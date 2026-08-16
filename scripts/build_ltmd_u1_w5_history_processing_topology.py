#!/usr/bin/env python3
"""Build reconciled W5 History processing inventory and canonical page manifest.

The topology is published only if all 15 direct-source identities remain complete,
the three anomalous 2018 identities are fully resolved through their paired 2019
routes by live SHA-256/byte-size verification, and no complete direct-source books
are byte-identical. Catalog identities remain distinct from processing objects.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

READINESS = Path('data/catalog/ltmd_u1_w5_history_source_readiness.csv')
EXACT = Path('data/catalog/ltmd_u1_w5_history_exact_asset_relationships.csv')
ROUTES = Path('data/catalog/ltmd_u1_w5_history_2018_2019_route_relationships.csv')
ASSETS = Path('data/catalog/ltmd_u1_w5_history_asset_manifest.csv')
PROCESSING = Path('data/catalog/ltmd_u1_w5_history_processing_inventory.csv')
PAGES = Path('data/catalog/ltmd_u1_w5_history_canonical_page_manifest.csv')
REPORT = Path('data/catalog/ltmd_u1_w5_history_processing_topology.md')
VERSION = 'LTMD_U1_W5_HISTORY_PROCESSING_0.1'
PAGE_VERSION = 'LTMD_U1_W5_HISTORY_CANONICAL_PAGE_MANIFEST_0.1'
EXPECTED_IDENTITIES = 18
EXPECTED_DIRECT = 15
EXPECTED_ROUTE_ALIASES = 3
EXPECTED_SOURCE_PAGES = 2653
EXPECTED_CANONICAL_TERMINALS = 15


def main():
    readiness = list(csv.DictReader(READINESS.open(encoding='utf-8', newline='')))
    exact = list(csv.DictReader(EXACT.open(encoding='utf-8', newline='')))
    routes = list(csv.DictReader(ROUTES.open(encoding='utf-8', newline='')))
    assets = list(csv.DictReader(ASSETS.open(encoding='utf-8', newline='')))

    if len(readiness) != EXPECTED_IDENTITIES or len({r['viewer_key'] for r in readiness}) != EXPECTED_IDENTITIES:
        raise SystemExit(f'W5 readiness cardinality drift: {len(readiness)}')
    direct = [r for r in readiness if r['source_state'] == 'full_direct_source']
    anomalous = [r for r in readiness if r['source_state'] == 'no_source_jpegs']
    if len(direct) != EXPECTED_DIRECT or len(anomalous) != EXPECTED_ROUTE_ALIASES:
        raise SystemExit(f'W5 direct/anomalous state drift: {len(direct)}/{len(anomalous)}')
    if exact:
        raise SystemExit(f'W5 topology requires explicit decision for direct byte-exact pairs: {len(exact)}')
    if len(routes) != EXPECTED_ROUTE_ALIASES:
        raise SystemExit(f'W5 route relationship cardinality drift: {len(routes)}')
    if any(int(r['complete_route_resolution']) != 1 for r in routes):
        raise SystemExit('W5 topology blocked: one or more 2018 route resolutions incomplete')
    if any(int(r['sha256_matches']) != int(r['compared_source_assets']) or int(r['byte_size_matches']) != int(r['compared_source_assets']) for r in routes):
        raise SystemExit('W5 topology blocked: incomplete route hash/size match')

    ready_by_key = {r['viewer_key']: r for r in readiness}
    route_by_18 = {r['viewer_key_2018']: r for r in routes}
    expected_anomalous = {r['viewer_key'] for r in anomalous}
    if set(route_by_18) != expected_anomalous:
        raise SystemExit('W5 route relationships do not cover exactly the anomalous 2018 identities')

    by_key = defaultdict(list)
    for row in assets:
        by_key[row['viewer_key']].append(row)
    if set(by_key) != set(ready_by_key):
        raise SystemExit('W5 source manifest/readiness viewer mismatch')
    if any(r['asset_status'] == 'probe_error' for r in assets):
        raise SystemExit('W5 source manifest contains probe errors')

    processing = []
    for r in sorted(readiness, key=lambda x: (int(x['catalog_generation']), int(x['grade_code']), x['viewer_key'])):
        key = r['viewer_key']
        if r['source_state'] == 'full_direct_source':
            mode = 'direct_canonical'
            canonical = key
            is_canonical = 1
            basis = 'full_direct_asset_audit_no_internal_gaps_no_complete_byte_exact_alias'
            persistent = 0
        else:
            rel = route_by_18[key]
            canonical = rel['canonical_processing_viewer_key']
            if canonical not in ready_by_key or ready_by_key[canonical]['source_state'] != 'full_direct_source':
                raise SystemExit(f'{key}: invalid canonical route target {canonical}')
            mode = 'route_alias_to_2019'
            is_canonical = 0
            basis = 'paired_2019_route_live_sha256_and_byte_size_full_match'
            persistent = 0
        processing.append({
            'processing_version': VERSION,
            'viewer_key': key,
            'catalog_generation': r['catalog_generation'],
            'grade_code': r['grade_code'],
            'title_core': r['title_core'],
            'original_source_state': r['source_state'],
            'processing_mode': mode,
            'canonical_processing_viewer_key': canonical,
            'technical_identity_covered': 1,
            'is_canonical_processing_object': is_canonical,
            'declared_positions': r['declared_positions'],
            'direct_source_jpegs': r['source_jpegs'],
            'terminal_synthetic_candidates_original_route': r['terminal_synthetic_candidates'],
            'persistent_unresolved_source_gaps': persistent,
            'evidence_basis': basis,
            'interpretive_limit': 'Operational processing topology only; route alias status does not establish bibliographic identity, edition year, or curricular equivalence.',
        })

    with PROCESSING.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(processing[0])); w.writeheader(); w.writerows(processing)

    proc = {r['viewer_key']: r for r in processing}
    canonical_keys = {r['viewer_key'] for r in processing if int(r['is_canonical_processing_object']) == 1}
    pages = []
    canonical_terminal = 0
    for key in sorted(canonical_keys, key=lambda k: (int(proc[k]['catalog_generation']), int(proc[k]['grade_code']), k)):
        rr = sorted(by_key[key], key=lambda r: int(r['viewer_page']))
        declared = int(proc[key]['declared_positions'])
        if len(rr) != declared:
            raise SystemExit(f'{key}: source audit cardinality {len(rr)} != declared {declared}')
        served = [r for r in rr if r['asset_status'] == 'source_jpeg']
        terminals = [r for r in rr if r['asset_status'] == 'terminal_synthetic_candidate']
        internal = [r for r in rr if r['asset_status'] == 'internal_unserved']
        if internal:
            raise SystemExit(f'{key}: internal source gap leaked into canonical topology')
        canonical_terminal += len(terminals)
        for r in served:
            if not r['sha256'] or not r['byte_size'] or not r['source_asset_url']:
                raise SystemExit(f"{key} VP{r['viewer_page']}: missing source evidence")
            pages.append({
                'manifest_version': PAGE_VERSION,
                'viewer_key': key,
                'catalog_generation': proc[key]['catalog_generation'],
                'grade_code': proc[key]['grade_code'],
                'title_core': proc[key]['title_core'],
                'processing_mode': 'direct_canonical',
                'viewer_page': r['viewer_page'],
                'source_image_index': r['source_image_index'],
                'source_asset_url': r['source_asset_url'],
                'byte_size': r['byte_size'],
                'sha256': r['sha256'],
                'asset_status': 'source_jpeg',
                'page_numbering_policy': 'preserve_original_viewer_page_no_renumbering',
                'source_provenance': 'W5_history_asset_manifest_source_jpeg',
            })

    if len(pages) != EXPECTED_SOURCE_PAGES:
        raise SystemExit(f'W5 canonical page count drift: {len(pages)} != {EXPECTED_SOURCE_PAGES}')
    if canonical_terminal != EXPECTED_CANONICAL_TERMINALS:
        raise SystemExit(f'W5 canonical terminal count drift: {canonical_terminal} != {EXPECTED_CANONICAL_TERMINALS}')
    pairs = [(r['viewer_key'], int(r['viewer_page'])) for r in pages]
    if len(pairs) != len(set(pairs)):
        raise SystemExit('duplicate W5 canonical viewer/page rows')

    with PAGES.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(pages[0])); w.writeheader(); w.writerows(pages)

    by_gen = defaultdict(lambda: {'identities': 0, 'canonicals': 0, 'aliases': 0, 'canonical_pages': 0})
    for r in processing:
        g = by_gen[r['catalog_generation']]
        g['identities'] += 1
        g['canonicals'] += int(r['is_canonical_processing_object'])
        g['aliases'] += int(r['processing_mode'] == 'route_alias_to_2019')
    for r in pages:
        by_gen[r['catalog_generation']]['canonical_pages'] += 1

    lines = [
        '# LTMD-U1 W5 — topología reconciliada de procesamiento Historia', '',
        f'Versión de procesamiento: `{VERSION}`.',
        f'Versión del manifiesto de páginas: `{PAGE_VERSION}`.', '',
        f'- Identidades W5 técnicamente cubiertas: **{sum(int(r["technical_identity_covered"]) for r in processing)}/{EXPECTED_IDENTITIES}**.',
        f'- Objetos canónicos de procesamiento: **{len(canonical_keys)}**.',
        f'- Aliases operacionales de ruta 2018→2019: **{sum(r["processing_mode"] == "route_alias_to_2019" for r in processing)}**.',
        '- Aliases de libro completo byte-exacto entre fuentes directas: **0**.',
        '- Huecos de fuente persistentes después de reconciliación: **0**.',
        f'- Páginas fuente canónicas autorizables para OCR: **{len(pages):,}**.',
        f'- Terminales sintéticos de objetos canónicos excluidos del OCR: **{canonical_terminal}**.',
        '- Renumeración de páginas: **0**.', '',
        '## Por generación', '',
        '| generación | identidades | canónicos | aliases de ruta | páginas OCR canónicas |',
        '|---:|---:|---:|---:|---:|'
    ]
    for gen in sorted(by_gen, key=int):
        d = by_gen[gen]
        lines.append(f"| {gen} | {d['identities']} | {d['canonicals']} | {d['aliases']} | {d['canonical_pages']:,} |")
    lines += ['', '## Contrato downstream', '',
        'OCR W5 sólo puede consumir `ltmd_u1_w5_history_canonical_page_manifest.csv`. Cada JPEG debe revalidarse en vivo contra SHA-256 y tamaño antes del OCR. Los tres visores 2018 no generan OCR duplicado: heredan cobertura técnica mediante su relación de ruta 2019, conservando sus viewer_key y provenance independientes.', '',
        'Este contrato autoriza exclusivamente procesamiento técnico OCR/PAGESTRUCT/FRAGSEG. No autoriza inferencias históricas o semánticas ni convierte la etiqueta operacional `historia` en una ontología curricular validada.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
