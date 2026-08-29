#!/usr/bin/env python3
"""Normalize byte-revalidated W10 topology for private FTRL preservation.

The 68 current source-admitted canonical identities enter FTRL. H2014P1ENA is
preserved as the sole final exception and is never aliased, imputed, or
silently absorbed. This script emits metadata only; it does not perform OCR.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

VERSION = 'LTMD_U1_W10_FTRL_INPUTS_0.1'
EXPECTED_HISTORICAL = 69
EXPECTED_CANONICAL = 68
EXPECTED_FINAL_EXCEPTION = 1
EXPECTED_PAGES = 11937
FINAL_EXCEPTION = 'H2014P1ENA'
SHA = re.compile(r'^[0-9a-f]{64}$')
SCOPE = Path('data/catalog/ltmd_u1_w10_scope.csv')
SOURCE_GATE = Path('data/catalog/ltmd_u1_w10_source_admissibility.csv')
MANIFEST = Path('data/catalog/ltmd_u1_w10_source_asset_manifest.csv')
REUSE_AUDIT = Path('data/research/ltmd_u1_w10_technical_reuse_audit.json')


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def n(row: dict[str, str], key: str) -> int:
    value = row.get(key, '')
    if value in {'', None}:
        raise AssertionError(f'missing {key}: {row}')
    return int(float(value))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    if not rows:
        raise SystemExit(f'refusing to write empty W10 FTRL input: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--asset-output', default='local/ftrl/ltmd_u1_w10_asset_manifest.csv')
    ap.add_argument('--processing-output', default='local/ftrl/ltmd_u1_w10_processing_inventory.csv')
    args = ap.parse_args()

    scope = read(SCOPE)
    gate = read(SOURCE_GATE)
    manifest = read(MANIFEST)
    audit = json.loads(REUSE_AUDIT.read_text(encoding='utf-8'))

    assert len(scope) == EXPECTED_HISTORICAL
    assert len({r['viewer_key'] for r in scope}) == EXPECTED_HISTORICAL
    required = {r['viewer_key'] for r in scope if r['documentary_disposition'] == 'required_ftrl_processing'}
    final = {r['viewer_key'] for r in scope if r['documentary_disposition'] == 'final_exception'}
    assert len(required) == EXPECTED_CANONICAL
    assert final == {FINAL_EXCEPTION}
    assert not any(r['documentary_disposition'] == 'active_retention' for r in scope)

    assert len(gate) == EXPECTED_CANONICAL
    assert len({r['viewer_key'] for r in gate}) == EXPECTED_CANONICAL
    assert {r['viewer_key'] for r in gate} == required
    admitted = [r for r in gate if n(r, 'source_admissible') == 1]
    assert len(admitted) == EXPECTED_CANONICAL
    assert all(r['source_status'] == 'SOURCE_ADMISSIBLE' for r in admitted)
    assert all(r['identity_reconciliation_state'] == 'exact_1_to_1' for r in admitted)
    assert all(r['relation_type'] == 'direct_canonical' for r in admitted)
    assert all(r['canonical_processing_viewer_key'] == r['viewer_key'] for r in admitted)
    assert all(n(r, 'is_canonical_processing_object') == 1 for r in admitted)
    assert all(n(r, 'persistent_unresolved_source_gaps') == 0 for r in admitted)
    assert all(r['alias_state'] == 'no_alias' for r in admitted)
    assert all(n(r, 'text_verified') == 0 and n(r, 'semantic_ready') == 0 for r in admitted)
    assert sum(n(r, 'canonical_source_pages') for r in admitted) == EXPECTED_PAGES

    assert audit['schema'] == 'LTMD_U1_W10_TECHNICAL_REUSE_AUDIT_0.1'
    assert audit['technical_reuse_validated'] is True
    assert audit['computationally_validated'] is True
    assert audit['current_source_identical_to_prior_topology'] is True
    assert audit['exact_matched_source_viewers'] == EXPECTED_CANONICAL
    assert audit['exact_matched_source_pages'] == EXPECTED_PAGES
    assert audit['final_exception_viewer_keys'] == [FINAL_EXCEPTION]
    assert audit['aliases_introduced'] == 0
    assert audit['archival_complete'] is False
    assert audit['text_verified'] is False and audit['semantic_ready'] is False

    pfields = [
        'processing_version', 'viewer_key', 'catalog_generation', 'grade_code', 'title_core',
        'processing_mode', 'canonical_processing_viewer_key', 'technical_identity_covered',
        'is_canonical_processing_object', 'declared_positions', 'direct_source_jpegs',
        'persistent_internal_source_gaps', 'source_processing_basis', 'interpretive_limit',
    ]
    pout: list[dict[str, object]] = []
    expected_counts: dict[str, int] = {}
    for r in admitted:
        viewer = r['viewer_key']
        pages = n(r, 'canonical_source_pages')
        expected_counts[viewer] = pages
        pout.append({
            'processing_version': VERSION,
            'viewer_key': viewer,
            'catalog_generation': n(r, 'catalog_generation'),
            'grade_code': n(r, 'grade_code'),
            'title_core': r['title_core'],
            'processing_mode': 'direct_canonical',
            'canonical_processing_viewer_key': viewer,
            'technical_identity_covered': 1,
            'is_canonical_processing_object': 1,
            'declared_positions': n(r, 'declared_positions'),
            'direct_source_jpegs': pages,
            'persistent_internal_source_gaps': 0,
            'source_processing_basis': f"{r['admissibility_version']}:{r['source_status']}+LTMD_U1_W10_TECHNICAL_REUSE_AUDIT_0.1:byte_exact",
            'interpretive_limit': 'private FTRL preservation only; H2014P1ENA remains a final exception; OCR availability does not imply human text verification or semantic readiness',
        })

    afields = [
        'audit_version', 'viewer_key', 'catalog_generation', 'grade_code', 'title_core',
        'viewer_page', 'source_image_index', 'source_asset_url', 'asset_status', 'byte_size',
        'sha256', 'processing_mode', 'source_provenance',
    ]
    aout: list[dict[str, object]] = []
    seen: set[tuple[str, int]] = set()
    counts: Counter[str] = Counter()
    terminal_counts: Counter[str] = Counter()

    for r in manifest:
        viewer = r['viewer_key']
        if viewer not in required:
            raise AssertionError(f'productive manifest contains identity outside required cohort: {viewer}')
        status = r['asset_status']
        if status == 'terminal_synthetic_candidate':
            terminal_counts[viewer] += 1
            assert n(r, 'is_final_declared_position') == 1
            assert n(r, 'http_status') == 404
            continue
        assert status == 'source_jpeg', (viewer, r['viewer_page'], status)
        index = n(r, 'source_image_index')
        key = (viewer, index)
        assert key not in seen
        seen.add(key)
        assert n(r, 'byte_size') > 0
        assert SHA.fullmatch(r['sha256'])
        assert n(r, 'http_status') == 200
        assert r['probe_state'] == 'served_jpeg'
        assert r['content_type'].lower().startswith('image/')
        assert n(r, 'jpeg_magic') == 1
        assert not r.get('error')
        assert r['source_asset_url'].startswith(f'https://historico.conaliteg.gob.mx/c/{viewer}/')
        counts[viewer] += 1
        aout.append({
            'audit_version': VERSION,
            'viewer_key': viewer,
            'catalog_generation': n(r, 'catalog_generation'),
            'grade_code': n(r, 'grade_code'),
            'title_core': r['title_core'],
            'viewer_page': n(r, 'viewer_page'),
            'source_image_index': index,
            'source_asset_url': r['source_asset_url'],
            'asset_status': 'source_jpeg',
            'byte_size': n(r, 'byte_size'),
            'sha256': r['sha256'],
            'processing_mode': 'direct_canonical',
            'source_provenance': 'LTMD_U1_W10_SOURCE_PROBE_0.1:historico_conaliteg_direct_jpeg:byte_revalidated_against_prior_topology',
        })

    assert dict(counts) == expected_counts
    assert set(terminal_counts) == required
    assert all(v == 1 for v in terminal_counts.values())
    assert len(aout) == len(seen) == EXPECTED_PAGES
    assert sum(int(r['direct_source_jpegs']) for r in pout) == EXPECTED_PAGES
    assert FINAL_EXCEPTION not in counts

    pout.sort(key=lambda r: (int(r['catalog_generation']), int(r['grade_code']), str(r['viewer_key'])))
    aout.sort(key=lambda r: (int(r['catalog_generation']), int(r['grade_code']), str(r['viewer_key']), int(r['source_image_index'])))
    write(Path(args.processing_output), pout, pfields)
    write(Path(args.asset_output), aout, afields)
    print(f'Built W10 private FTRL inputs: historical={EXPECTED_HISTORICAL}, canonical={len(pout)}, final_exception={EXPECTED_FINAL_EXCEPTION}, pages={len(aout)}')


if __name__ == '__main__':
    main()
