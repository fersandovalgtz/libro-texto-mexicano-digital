#!/usr/bin/env python3
"""Combine W10 per-book source probes and freeze source admissibility denominators."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

SCOPE = Path('data/catalog/ltmd_u1_w10_scope.csv')
ARCH = Path('data/catalog/ltmd_u1_w10_viewer_architecture.csv')
INV = Path('data/catalog/ltmd_u1_w10_declared_inventory.csv')
MANIFEST_OUT = Path('data/catalog/ltmd_u1_w10_source_asset_manifest.csv')
SUMMARY_OUT = Path('data/catalog/ltmd_u1_w10_source_asset_summary.csv')
ADMISS_OUT = Path('data/catalog/ltmd_u1_w10_source_admissibility.csv')
EVIDENCE_OUT = Path('data/research/ltmd_u1_w10_source_probe_evidence.json')
REPORT = Path('docs/LTMD_U1_W10_SOURCE_PROBE.md')
VERSION = 'LTMD_U1_W10_SOURCE_PROBE_0.1'
EXPECTED_HISTORICAL = 69
EXPECTED_REQUIRED = 68
FINAL_EXCEPTION = 'H2014P1ENA'


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def keyed(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row['viewer_key']
        if key in out:
            raise SystemExit(f'W10 combine: duplicate {label} viewer_key {key}')
        out[key] = row
    return out


def as_int(value: str | int | None) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--shard-dir', type=Path, default=Path('data/work/ltmd_u1_w10_source_assets'))
    args = ap.parse_args()

    scope_rows = read_rows(SCOPE)
    if len(scope_rows) != EXPECTED_HISTORICAL or len({r['viewer_key'] for r in scope_rows}) != EXPECTED_HISTORICAL:
        raise SystemExit('W10 combine: historical scope cardinality drift')
    required_scope = [r for r in scope_rows if r['documentary_disposition'] == 'required_ftrl_processing']
    exception_scope = [r for r in scope_rows if r['documentary_disposition'] == 'final_exception']
    if len(required_scope) != EXPECTED_REQUIRED or [r['viewer_key'] for r in exception_scope] != [FINAL_EXCEPTION]:
        raise SystemExit('W10 combine: documentary split drift')
    required_keys = {r['viewer_key'] for r in required_scope}

    arch = keyed(read_rows(ARCH), 'architecture')
    inv = keyed(read_rows(INV), 'inventory')
    if set(arch) != required_keys or set(inv) != required_keys:
        raise SystemExit(
            f'W10 combine: source metadata identity drift arch_missing={sorted(required_keys-set(arch))} '
            f'inv_missing={sorted(required_keys-set(inv))}'
        )

    summary_files = sorted(args.shard_dir.glob('summary_*.csv'))
    summaries: list[dict[str, str]] = []
    for path in summary_files:
        rows = read_rows(path)
        if len(rows) != 1:
            raise SystemExit(f'W10 combine: expected one summary row in {path}, got {len(rows)}')
        summaries.extend(rows)
    summary_by = keyed(summaries, 'shard summary')
    if set(summary_by) != required_keys:
        raise SystemExit(
            f'W10 combine: shard summary identity drift missing={sorted(required_keys-set(summary_by))} '
            f'unexpected={sorted(set(summary_by)-required_keys)}'
        )

    manifest_rows: list[dict[str, str]] = []
    for path in sorted(args.shard_dir.glob('asset_*.csv')):
        manifest_rows.extend(read_rows(path))
    manifest_counts = Counter(r['viewer_key'] for r in manifest_rows)
    if any(k not in required_keys for k in manifest_counts):
        raise SystemExit('W10 combine: manifest contains viewer outside required cohort')

    out_summary: list[dict[str, object]] = []
    admissibility: list[dict[str, object]] = []
    for scope in sorted(required_scope, key=lambda r: (int(r['catalog_generation']), int(r['grade_code']), r['viewer_key'])):
        key = scope['viewer_key']
        s = summary_by[key]
        a = arch[key]
        i = inv[key]
        declared = as_int(s['declared_positions'])
        source_jpegs = as_int(s['source_jpegs'])
        terminal = as_int(s['terminal_synthetic_candidates'])
        internal = as_int(s['internal_unserved'])
        probe_errors = as_int(s['probe_errors'])
        manifest_n = manifest_counts.get(key, 0)
        ready = as_int(s['direct_asset_probe_ready']) == 1

        if ready and manifest_n != declared:
            raise SystemExit(f'W10 combine: {key} ready manifest rows {manifest_n} != declared {declared}')
        if not ready and manifest_n != 0:
            raise SystemExit(f'W10 combine: {key} not-ready viewer unexpectedly has {manifest_n} manifest rows')
        if ready and source_jpegs + terminal + internal + probe_errors != declared:
            raise SystemExit(f'W10 combine: {key} asset partition does not equal declared positions')
        if a['direct_asset_probe_ready'] != i['direct_asset_probe_ready'] or i['direct_asset_probe_ready'] != s['direct_asset_probe_ready']:
            raise SystemExit(f'W10 combine: {key} direct-ready metadata drift')

        admitted = (
            ready
            and source_jpegs > 0
            and internal == 0
            and probe_errors == 0
            and terminal <= 1
        )
        if admitted:
            source_status = 'SOURCE_ADMISSIBLE'
            reason = 'exact_1_to_1; official dynamic architecture/configuration; served JPEG sequence has no internal gaps or probe errors'
            relation_type = 'direct_canonical'
        else:
            source_status = 'SOURCE_RETAINED'
            reason_parts: list[str] = []
            if as_int(s['standard_dynamic_architecture']) != 1:
                reason_parts.append('nonstandard_or_unverified_architecture')
            if as_int(s['config_present']) != 1:
                reason_parts.append('official_config_missing')
            if as_int(s['config_ag_clave_exact']) != 1:
                reason_parts.append('ag_clave_not_exact_1_to_1')
            if not ready:
                reason_parts.append('direct_asset_probe_not_ready')
            if ready and source_jpegs == 0:
                reason_parts.append('no_source_jpegs_served')
            if internal:
                reason_parts.append(f'internal_unserved={internal}')
            if probe_errors:
                reason_parts.append(f'probe_errors={probe_errors}')
            if terminal > 1:
                reason_parts.append(f'terminal_synthetic_candidates={terminal}')
            reason = '; '.join(reason_parts) or 'source gate not satisfied'
            relation_type = 'withheld_source'

        out_summary.append({
            'probe_version': VERSION,
            'viewer_key': key,
            'catalog_generation': scope['catalog_generation'],
            'grade_code': scope['grade_code'],
            'title_core': scope['title_core'],
            'standard_dynamic_architecture': s['standard_dynamic_architecture'],
            'config_present': s['config_present'],
            'config_ag_clave_exact': s['config_ag_clave_exact'],
            'direct_asset_probe_ready': s['direct_asset_probe_ready'],
            'declared_positions': declared,
            'source_jpegs': source_jpegs,
            'terminal_synthetic_candidates': terminal,
            'internal_unserved': internal,
            'probe_errors': probe_errors,
            'manifest_rows': manifest_n,
            'source_probe_state': s['source_probe_state'],
            'architecture_probe_error': s['architecture_probe_error'],
            'source_url': scope['source_url'],
        })
        admissibility.append({
            'admissibility_version': VERSION,
            'viewer_key': key,
            'catalog_generation': scope['catalog_generation'],
            'grade_code': scope['grade_code'],
            'title_core': scope['title_core'],
            'identity_reconciliation_state': 'exact_1_to_1',
            'source_admissible': int(admitted),
            'source_status': source_status,
            'source_reason': reason,
            'source_ready': 'full' if admitted else 'unresolved',
            'relation_type': relation_type,
            'canonical_processing_viewer_key': key if admitted else '',
            'is_canonical_processing_object': int(admitted),
            'declared_positions': declared if declared > 0 else '',
            'canonical_source_pages': source_jpegs if admitted else '',
            'persistent_unresolved_source_gaps': internal if admitted else '',
            'alias_state': 'no_alias',
            'text_verified': 0,
            'semantic_ready': 0,
            'source_url': scope['source_url'],
        })

    if manifest_rows:
        MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
        with MANIFEST_OUT.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
            writer.writeheader(); writer.writerows(manifest_rows)
    else:
        MANIFEST_OUT.write_text('', encoding='utf-8')
    with SUMMARY_OUT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out_summary[0]))
        writer.writeheader(); writer.writerows(out_summary)
    with ADMISS_OUT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(admissibility[0]))
        writer.writeheader(); writer.writerows(admissibility)

    admitted_rows = [r for r in admissibility if r['source_status'] == 'SOURCE_ADMISSIBLE']
    retained_rows = [r for r in admissibility if r['source_status'] == 'SOURCE_RETAINED']
    total_declared = sum(as_int(r['declared_positions']) for r in out_summary)
    total_source_pages = sum(as_int(r['source_jpegs']) for r in out_summary)
    total_internal = sum(as_int(r['internal_unserved']) for r in out_summary)
    total_terminal = sum(as_int(r['terminal_synthetic_candidates']) for r in out_summary)
    total_probe_errors = sum(as_int(r['probe_errors']) for r in out_summary)
    direct_ready = sum(as_int(r['direct_asset_probe_ready']) for r in out_summary)
    by_generation: dict[str, dict[str, int]] = defaultdict(lambda: {'required': 0, 'admitted': 0, 'retained': 0, 'source_pages': 0})
    for r in admissibility:
        bucket = by_generation[str(r['catalog_generation'])]
        bucket['required'] += 1
        bucket['admitted'] += int(r['source_status'] == 'SOURCE_ADMISSIBLE')
        bucket['retained'] += int(r['source_status'] == 'SOURCE_RETAINED')
        bucket['source_pages'] += as_int(r['canonical_source_pages'])

    evidence = {
        'schema': VERSION,
        'wave': 'W10',
        'domain': 'integrados_multiarea',
        'status': 'source_probe_complete' if total_probe_errors == 0 else 'source_probe_operational_errors',
        'historical_identities': EXPECTED_HISTORICAL,
        'required_ftrl_processing': EXPECTED_REQUIRED,
        'final_exception': 1,
        'final_exception_viewer_keys': [FINAL_EXCEPTION],
        'active_retention_at_g0': 0,
        'aliases_introduced': 0,
        'direct_asset_probe_ready': direct_ready,
        'source_admissible': len(admitted_rows),
        'source_retained': len(retained_rows),
        'declared_positions_sum': total_declared,
        'source_jpeg_pages_sum': total_source_pages,
        'terminal_synthetic_candidates_sum': total_terminal,
        'internal_unserved_sum': total_internal,
        'probe_errors_sum': total_probe_errors,
        'admitted_viewer_keys': [r['viewer_key'] for r in admitted_rows],
        'retained_viewer_keys': [r['viewer_key'] for r in retained_rows],
        'generation_summary': dict(sorted(by_generation.items(), key=lambda x: int(x[0]))),
        'ocr_authorized_for_source_admitted_only': total_probe_errors == 0,
        'text_verified': False,
        'semantic_ready': False,
        'interpretive_limit': 'Source admissibility is a technical gate only. It does not establish semantic equivalence, historical continuity, text verification, or archival closure.',
    }
    EVIDENCE_OUT.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_OUT.write_text(json.dumps(evidence, indent=2, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')

    retained_list = ', '.join(f'`{r["viewer_key"]}`' for r in retained_rows) or 'Ninguna.'
    lines = [
        '# LTMD-U1 W10 — probe source-first y admisibilidad', '',
        f'Versión: `{VERSION}`.', '',
        '## Resultado', '',
        f'- Identidades históricas: **{EXPECTED_HISTORICAL}**.',
        f'- Procesables auditadas: **{EXPECTED_REQUIRED}/{EXPECTED_REQUIRED}**.',
        f'- Excepción final fuera del probe: **1** (`{FINAL_EXCEPTION}`).',
        f'- Listas para auditoría directa de activos: **{direct_ready}/{EXPECTED_REQUIRED}**.',
        f'- `SOURCE_ADMISSIBLE`: **{len(admitted_rows)}/{EXPECTED_REQUIRED}**.',
        f'- `SOURCE_RETAINED`: **{len(retained_rows)}/{EXPECTED_REQUIRED}**.',
        f'- Posiciones declaradas observadas: **{total_declared:,}**.',
        f'- JPEG fuente servidos y hasheados: **{total_source_pages:,}**.',
        f'- Candidatos terminales sintéticos: **{total_terminal:,}**.',
        f'- Huecos internos no servidos: **{total_internal:,}**.',
        f'- Errores operacionales de probe: **{total_probe_errors:,}**.',
        '- Alias creados: **0**.',
        '- `text_verified`: **false**.',
        '- `semantic_ready`: **false**.', '',
        '## Retenciones de fuente', '',
        retained_list, '',
        '## Por generación', '',
        '| generación | procesables | admitidas | retenidas | páginas fuente admitidas |',
        '|---:|---:|---:|---:|---:|',
    ]
    for generation, values in sorted(by_generation.items(), key=lambda x: int(x[0])):
        lines.append(
            f"| {generation} | {values['required']} | {values['admitted']} | {values['retained']} | {values['source_pages']:,} |"
        )
    lines += [
        '', '## Regla de admisión', '',
        'Una identidad sólo es `SOURCE_ADMISSIBLE` cuando conserva reconciliación exacta 1:1, arquitectura/configuración oficial verificable, al menos un JPEG fuente servido, cero huecos internos, cero errores operacionales y como máximo un candidato terminal sintético. Los bytes de imagen se transmiten únicamente para computar SHA-256 y tamaño; no se persisten en GitHub.', '',
        'Cualquier ausencia, 404 o arquitectura no verificable permanece como retención de fuente. No se imputa contenido desde títulos, grados, ediciones, cardinalidades, OCR o libros vecinos.', '',
        'Si `probe_errors_sum` es distinto de cero, el gate queda operacionalmente inconcluso y no autoriza OCR. Con cero errores, sólo las identidades `SOURCE_ADMISSIBLE` pueden avanzar al procesamiento distribuido; la admisibilidad no implica verificación humana del texto ni preparación semántica.',
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
