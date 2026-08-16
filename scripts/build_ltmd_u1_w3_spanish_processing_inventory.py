#!/usr/bin/env python3
"""Build the W3 Spanish/Language processing inventory after source reconciliation.

This step is intentionally downstream from the anomaly audits. It turns evidence
into an operational processing topology without collapsing catalog identities:
- full direct objects remain canonical unless they are proven exact-byte aliases;
- 2018 routing anomalies may point to paired 2019 canonical processing objects only
  when complete route resolution was proven;
- localized persistent source gaps remain explicit while the rest of the viewer is
  eligible for OCR without page renumbering;
- any inconclusive source state blocks only that viewer.
"""
from __future__ import annotations

import csv
from pathlib import Path

STATES = Path('data/catalog/ltmd_u1_w3_spanish_asset_states.csv')
EXACT = Path('data/catalog/ltmd_u1_w3_spanish_exact_aliases.csv')
ROUTES = Path('data/catalog/ltmd_u1_w3_spanish_2018_2019_route_relationships.csv')
GAPS = Path('data/catalog/ltmd_u1_w3_spanish_internal_unserved_audit.csv')
OUT = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
REPORT = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.md')
VERSION = 'LTMD_U1_W3_SPANISH_PROCESSING_INVENTORY_0.1'
EXPECTED = 130


def main():
    states = list(csv.DictReader(STATES.open(encoding='utf-8')))
    exact = list(csv.DictReader(EXACT.open(encoding='utf-8')))
    routes = list(csv.DictReader(ROUTES.open(encoding='utf-8')))
    gaps = list(csv.DictReader(GAPS.open(encoding='utf-8')))
    if len(states) != EXPECTED or len({r['viewer_key'] for r in states}) != EXPECTED:
        raise SystemExit('W3 state cardinality drift')

    exact_map = {r['viewer_key']: r['canonical_viewer_key'] for r in exact}
    if len(exact_map) != 8:
        raise SystemExit(f'expected 8 exact byte aliases, got {len(exact_map)}')

    route_map = {}
    for r in routes:
        if r['complete_route_resolution'] == '1':
            route_map[r['viewer_key_2018']] = r['canonical_processing_viewer_key']
    if len(route_map) != 8:
        raise SystemExit(f'expected 8 complete 2018 route resolutions, got {len(route_map)}')

    gaps_by_viewer = {}
    for r in gaps:
        gaps_by_viewer.setdefault(r['viewer_key'], []).append(r)
    if len(gaps_by_viewer) != 7 or len(gaps) != 8:
        raise SystemExit('W3 localized-gap audit cardinality drift')

    rows = []
    for s in states:
        key = s['viewer_key']
        state = s['asset_state']
        mode = ''
        canonical = ''
        eligible = 0
        persistent_gaps = 0
        recovered_gaps = 0
        block_reason = ''
        evidence = ''

        if state == 'full_direct':
            if key in exact_map:
                mode = 'exact_byte_alias'
                canonical = exact_map[key]
                eligible = 1
                evidence = 'complete_aligned_viewer_page_byte_size_sha256_identity'
            else:
                mode = 'direct_canonical'
                canonical = key
                eligible = 1
                evidence = 'direct_source_jpeg_manifest'
        elif state == 'routing_anomaly_all_or_near_all':
            if key in route_map:
                mode = 'paired_route_alias_2018_to_2019'
                canonical = route_map[key]
                eligible = 1
                evidence = 'complete_paired_route_rehash_against_2019_reference'
            else:
                mode = 'blocked_unresolved_route'
                block_reason = 'routing anomaly not completely resolved'
        elif state == 'partial_internal_unserved':
            audits = gaps_by_viewer.get(key, [])
            expected_gaps = int(s['internal_unserved'])
            if len(audits) != expected_gaps:
                mode = 'blocked_gap_audit_cardinality_mismatch'
                block_reason = f'expected {expected_gaps} audited gaps, got {len(audits)}'
            elif any(r['target_state'] == 'audit_inconclusive' for r in audits):
                mode = 'blocked_inconclusive_source_gap'
                block_reason = 'one or more localized source gaps remain inconclusive'
            else:
                persistent_gaps = sum(r['target_state'] == 'internal_unserved_position_observed' for r in audits)
                recovered_gaps = sum(r['target_state'] == 'unexpectedly_recovered' for r in audits)
                mode = (
                    'partial_canonical_explicit_gap'
                    if persistent_gaps
                    else 'partial_canonical_recovered'
                )
                canonical = key
                eligible = 1
                evidence = 'target_retry_plus_neighbour_sha_controls'
        else:
            mode = 'blocked_unknown_state'
            block_reason = f'unhandled asset state {state}'

        rows.append({
            'processing_version': VERSION,
            'viewer_key': key,
            'catalog_generation': s['catalog_generation'],
            'grade_code': s['grade_code'],
            'title_core': s['title_core'],
            'original_asset_state': state,
            'processing_mode': mode,
            'canonical_processing_viewer_key': canonical,
            'ocr_identity_eligible': eligible,
            'is_canonical_processing_object': int(bool(canonical) and canonical == key),
            'declared_positions': s['declared_positions'],
            'direct_source_jpegs': s['source_jpegs'],
            'persistent_internal_source_gaps': persistent_gaps,
            'recovered_internal_source_gaps': recovered_gaps,
            'evidence_basis': evidence,
            'block_reason': block_reason,
            'interpretive_limit': (
                'Operational processing topology only. Catalog identities remain separate; aliases '
                'do not establish bibliographic identity or edition year.'
            ),
        })

    # Every canonical target must exist and itself be OCR-eligible.
    by_key = {r['viewer_key']: r for r in rows}
    for row in rows:
        if not int(row['ocr_identity_eligible']):
            continue
        target = row['canonical_processing_viewer_key']
        if target not in by_key:
            raise SystemExit(f"{row['viewer_key']}: canonical target missing: {target}")
    for row in rows:
        if row['processing_mode'] in ('exact_byte_alias', 'paired_route_alias_2018_to_2019'):
            target = by_key[row['canonical_processing_viewer_key']]
            if not int(target['ocr_identity_eligible']) or target['canonical_processing_viewer_key'] != target['viewer_key']:
                raise SystemExit(f"{row['viewer_key']}: alias target is not canonical/eligible")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    eligible = sum(int(r['ocr_identity_eligible']) for r in rows)
    canonical = sum(int(r['is_canonical_processing_object']) for r in rows)
    exact_aliases = sum(r['processing_mode'] == 'exact_byte_alias' for r in rows)
    route_aliases = sum(r['processing_mode'] == 'paired_route_alias_2018_to_2019' for r in rows)
    partial = sum(r['processing_mode'].startswith('partial_canonical_') for r in rows)
    blocked = [r for r in rows if not int(r['ocr_identity_eligible'])]
    persistent = sum(int(r['persistent_internal_source_gaps']) for r in rows)
    recovered = sum(int(r['recovered_internal_source_gaps']) for r in rows)

    lines = [
        '# LTMD-U1 W3 — inventario reconciliado de procesamiento Español/Lengua',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Identidades W3: **{len(rows)}**.',
        f'- Identidades con cobertura operacional OCR: **{eligible}/{len(rows)}**.',
        f'- Objetos canónicos que requieren procesamiento único: **{canonical}**.',
        f'- Aliases byte-exactos directos: **{exact_aliases}**.',
        f'- Aliases de ruta 2018→2019 reconciliados: **{route_aliases}**.',
        f'- Canónicos parciales con auditoría de huecos: **{partial}**.',
        f'- Huecos internos persistentes conservados: **{persistent}**.',
        f'- Huecos internos recuperados: **{recovered}**.',
        f'- Identidades bloqueadas: **{len(blocked)}**.',
        '',
        '## Regla de procesamiento',
        'OCR debe ejecutarse una sola vez por `canonical_processing_viewer_key`. Las identidades alias heredan los productos técnicos del canónico mediante provenance explícita. Los canónicos parciales procesan todas las páginas fuente disponibles y conservan el hueco digital sin renumeración.',
    ]
    if blocked:
        lines += ['', '## Bloqueos']
        for row in blocked:
            lines.append(f"- `{row['viewer_key']}`: {row['processing_mode']} — {row['block_reason']}")
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

    if eligible != EXPECTED:
        raise SystemExit(f'W3 not fully reconciled: {eligible}/{EXPECTED} identities OCR-eligible')


if __name__ == '__main__':
    main()
