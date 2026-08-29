#!/usr/bin/env python3
"""Authorize W10 technical reuse only after byte-exact current-source revalidation.

This gate compares the newly re-probed official source topology against the
previously processed W10 canonical page manifest. It also reruns the existing
strict technical completion validator. Any identity, page-index, byte-size or
SHA-256 drift fails closed. It never promotes archival or semantic state.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

CURRENT_EVIDENCE = Path('data/research/ltmd_u1_w10_source_probe_evidence.json')
CURRENT_ADMISS = Path('data/catalog/ltmd_u1_w10_source_admissibility.csv')
CURRENT_MANIFEST = Path('data/catalog/ltmd_u1_w10_source_asset_manifest.csv')
PRIOR_PROC = Path('data/catalog/ltmd_u1_w10_processing_inventory.csv')
PRIOR_MANIFEST = Path('data/catalog/ltmd_u1_w10_canonical_page_manifest.csv')
STRICT_VALIDATOR = Path('scripts/build_ltmd_u1_w10_completion_report.py')
OUT_JSON = Path('data/research/ltmd_u1_w10_technical_reuse_audit.json')
OUT_MD = Path('docs/LTMD_U1_W10_TECHNICAL_REUSE_AUDIT.md')
VERSION = 'LTMD_U1_W10_TECHNICAL_REUSE_AUDIT_0.1'
EXPECTED_HISTORICAL = 69
EXPECTED_REQUIRED = 68
FINAL_EXCEPTION = 'H2014P1ENA'


def fail(message: str) -> None:
    raise SystemExit(f'W10 technical reuse audit failed: {message}')


def rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        fail(f'missing {path}')
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def page_key(row: dict[str, str]) -> tuple[str, int]:
    return row['viewer_key'], int(row['source_image_index'])


def digest_pages(index: dict[tuple[str, int], dict[str, str]]) -> str:
    h = hashlib.sha256()
    for (viewer, source_index), row in sorted(index.items()):
        record = {
            'viewer_key': viewer,
            'source_image_index': source_index,
            'byte_size': int(row['byte_size']),
            'sha256': row['sha256'],
        }
        h.update(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))
        h.update(b'\n')
    return h.hexdigest()


def main() -> None:
    evidence = json.loads(CURRENT_EVIDENCE.read_text(encoding='utf-8'))
    required_contract = {
        'historical_identities': EXPECTED_HISTORICAL,
        'required_ftrl_processing': EXPECTED_REQUIRED,
        'final_exception': 1,
        'final_exception_viewer_keys': [FINAL_EXCEPTION],
        'active_retention_at_g0': 0,
        'aliases_introduced': 0,
        'source_admissible': EXPECTED_REQUIRED,
        'source_retained': 0,
        'probe_errors_sum': 0,
    }
    for key, expected in required_contract.items():
        if evidence.get(key) != expected:
            fail(f'current source evidence {key}={evidence.get(key)!r}, expected {expected!r}')
    if evidence.get('status') != 'source_probe_complete':
        fail(f"current source status={evidence.get('status')!r}")
    if evidence.get('ocr_authorized_for_source_admitted_only') is not True:
        fail('current source gate did not authorize admitted-only OCR')
    if evidence.get('text_verified') is not False or evidence.get('semantic_ready') is not False:
        fail('source evidence improperly promoted semantic state')

    admiss = rows(CURRENT_ADMISS)
    if len(admiss) != EXPECTED_REQUIRED or len({r['viewer_key'] for r in admiss}) != EXPECTED_REQUIRED:
        fail(f'current admissibility cardinality={len(admiss)}')
    current_admitted = {r['viewer_key'] for r in admiss if r['source_status'] == 'SOURCE_ADMISSIBLE' and r['source_admissible'] == '1'}
    current_retained = {r['viewer_key'] for r in admiss if r['source_status'] == 'SOURCE_RETAINED'}
    if len(current_admitted) != EXPECTED_REQUIRED or current_retained:
        fail(f'current admitted/retained split={len(current_admitted)}/{sorted(current_retained)}')
    if FINAL_EXCEPTION in current_admitted:
        fail('final exception leaked into productive current cohort')

    proc = rows(PRIOR_PROC)
    if len(proc) != EXPECTED_HISTORICAL or len({r['viewer_key'] for r in proc}) != EXPECTED_HISTORICAL:
        fail(f'prior processing inventory cardinality={len(proc)}')
    prior_admitted = {
        r['viewer_key'] for r in proc
        if r['source_admitted'] == '1' and r['is_canonical_processing_object'] == '1' and r['processing_mode'] == 'direct_canonical'
    }
    prior_withheld = {r['viewer_key'] for r in proc if r['source_admitted'] == '0'}
    if prior_withheld != {FINAL_EXCEPTION}:
        fail(f'prior withheld set={sorted(prior_withheld)}')
    if prior_admitted != current_admitted:
        fail(f'admitted-set drift current_only={sorted(current_admitted-prior_admitted)} prior_only={sorted(prior_admitted-current_admitted)}')
    if any(r['processing_mode'] == 'exact_source_alias' for r in proc):
        fail('prior processing topology unexpectedly contains aliases')

    prior_expected_pages = sum(int(r['source_pages']) for r in proc if r['viewer_key'] in prior_admitted)
    prior_pages_by_viewer = {r['viewer_key']: int(r['source_pages']) for r in proc if r['viewer_key'] in prior_admitted}

    current_all = rows(CURRENT_MANIFEST)
    if not current_all:
        fail('current source manifest is empty')
    bad_states = Counter(r['asset_status'] for r in current_all if r['asset_status'] not in {'source_jpeg', 'terminal_synthetic_candidate'})
    if bad_states:
        fail(f'current source manifest contains non-reusable states: {dict(bad_states)}')
    current_source = [r for r in current_all if r['asset_status'] == 'source_jpeg']
    terminal = [r for r in current_all if r['asset_status'] == 'terminal_synthetic_candidate']
    if len(current_source) != prior_expected_pages:
        fail(f'current source JPEG pages={len(current_source)}, prior expected={prior_expected_pages}')
    if len(terminal) != EXPECTED_REQUIRED:
        fail(f'expected one terminal synthetic candidate per admitted viewer ({EXPECTED_REQUIRED}), got {len(terminal)}')
    if {r['viewer_key'] for r in terminal} != current_admitted:
        fail('terminal synthetic candidate viewer set drift')

    prior_source = rows(PRIOR_MANIFEST)
    if len(prior_source) != prior_expected_pages:
        fail(f'prior canonical manifest pages={len(prior_source)}, expected={prior_expected_pages}')
    if any(r['asset_status'] != 'source_jpeg' or r['processing_mode'] != 'direct_canonical' for r in prior_source):
        fail('prior canonical manifest contains non-source/non-direct rows')

    current_index: dict[tuple[str, int], dict[str, str]] = {}
    for row in current_source:
        key = page_key(row)
        if key in current_index:
            fail(f'duplicate current page key {key}')
        current_index[key] = row
    prior_index: dict[tuple[str, int], dict[str, str]] = {}
    for row in prior_source:
        key = page_key(row)
        if key in prior_index:
            fail(f'duplicate prior page key {key}')
        prior_index[key] = row

    if set(current_index) != set(prior_index):
        current_only = sorted(set(current_index) - set(prior_index))[:20]
        prior_only = sorted(set(prior_index) - set(current_index))[:20]
        fail(f'page-key drift current_only={current_only} prior_only={prior_only}')

    mismatches: list[dict[str, object]] = []
    for key in sorted(current_index):
        cur = current_index[key]
        old = prior_index[key]
        fields = []
        if cur['source_asset_url'] != old['source_asset_url']:
            fields.append('source_asset_url')
        if int(cur['byte_size']) != int(old['byte_size']):
            fields.append('byte_size')
        if cur['sha256'] != old['sha256']:
            fields.append('sha256')
        if fields:
            mismatches.append({'viewer_key': key[0], 'source_image_index': key[1], 'fields': fields})
            if len(mismatches) >= 20:
                break
    if mismatches:
        fail(f'byte/provenance drift examples={mismatches}')

    current_counts = Counter(r['viewer_key'] for r in current_source)
    if dict(current_counts) != prior_pages_by_viewer:
        drift = {
            k: {'current': current_counts.get(k, 0), 'prior': prior_pages_by_viewer.get(k, 0)}
            for k in sorted(current_admitted)
            if current_counts.get(k, 0) != prior_pages_by_viewer.get(k, 0)
        }
        fail(f'per-viewer source-page count drift={drift}')

    current_digest = digest_pages(current_index)
    prior_digest = digest_pages(prior_index)
    if current_digest != prior_digest:
        fail('global deterministic source digest mismatch despite row checks')

    validator = subprocess.run(
        [sys.executable, str(STRICT_VALIDATOR)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if validator.returncode != 0:
        fail('existing strict W10 technical completion validator failed:\n' + validator.stdout[-5000:])

    audit = {
        'schema': VERSION,
        'wave': 'W10',
        'domain': 'integrados_multiarea',
        'historical_identities': EXPECTED_HISTORICAL,
        'current_source_probe_identities': EXPECTED_REQUIRED,
        'current_source_admitted': EXPECTED_REQUIRED,
        'prior_canonical_processing_objects': EXPECTED_REQUIRED,
        'final_exception_viewer_keys': [FINAL_EXCEPTION],
        'aliases_introduced': 0,
        'exact_matched_source_viewers': EXPECTED_REQUIRED,
        'exact_matched_source_pages': prior_expected_pages,
        'current_terminal_synthetic_candidates': len(terminal),
        'page_identity_index_exact': True,
        'source_asset_url_exact': True,
        'byte_size_exact': True,
        'sha256_exact': True,
        'current_source_global_digest_sha256': current_digest,
        'prior_source_global_digest_sha256': prior_digest,
        'current_source_identical_to_prior_topology': True,
        'existing_strict_technical_completion_validator_passed': True,
        'technical_reuse_validated': True,
        'recompute_ocr_required': False,
        'computationally_validated': True,
        'archival_complete': False,
        'text_verified': False,
        'semantic_ready': False,
        'interpretive_limit': (
            'Byte-exact source identity plus a passing strict technical validator authorizes reuse of the existing '
            'W10 computational outputs. It does not establish private archival closure, human text verification, '
            'semantic readiness, curricular equivalence, or historical interpretation.'
        ),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# LTMD-U1 W10 — auditoría de reutilización técnica byte-exacta', '',
        f'Versión: `{VERSION}`.', '',
        '## Resultado', '',
        f'- Identidades históricas: **{EXPECTED_HISTORICAL}**.',
        f'- Cohorte productiva re-sondeada: **{EXPECTED_REQUIRED}/{EXPECTED_REQUIRED}**.',
        f'- Excepción final conservada fuera de procesamiento: **`{FINAL_EXCEPTION}`**.',
        f'- Objetos canónicos previos auditados: **{EXPECTED_REQUIRED}**.',
        f'- Páginas fuente actuales comparadas 1:1: **{prior_expected_pages:,}/{prior_expected_pages:,}**.',
        '- Identidad `(viewer_key, source_image_index)`: **exacta**.',
        '- URL oficial de activo: **exacta**.',
        '- Tamaño en bytes: **exacto**.',
        '- SHA-256: **exacto**.',
        f'- Digest global determinista de fuente: `{current_digest}`.',
        '- Validador estricto del cierre técnico existente: **PASS**.',
        '- Recalcular OCR por deriva de fuente: **no requerido**.', '',
        '## Alcance científico', '',
        'La coincidencia byte-exacta de toda la cohorte productiva permite reutilizar los productos técnicos W10 ya calculados sin recomputar OCR, PAGESTRUCT, FRAGSEG y reutilización textual exacta. La autorización es estrictamente computacional: cualquier diferencia de índice, URL, tamaño o SHA-256 habría detenido el proceso.', '',
        '`computationally_validated=true` no equivale a `archival_complete=true`. La preservación privada verificable sigue pendiente. Asimismo, `text_verified=false` y `semantic_ready=false`; permanece vigente `WAITING_HUMAN_REFERENCE`.',
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
