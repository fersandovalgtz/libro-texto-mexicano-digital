#!/usr/bin/env python3
"""Find strict cryptographic recoveries for W2 Mathematics internal gaps.

Uses only hashes already present in the completed W2 asset manifest. No source is
redownloaded. A recovery requires a unique candidate viewer of the same grade and
normalized title core, a fixed offset, >=4 neighbouring source-page SHA matches,
zero compared-anchor mismatches, and a served target page at the mapped position.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

MAN = Path('data/catalog/ltmd_u1_w2_math_asset_manifest.csv')
SCOPE = Path('data/catalog/ltmd_u1_w2_scope.csv')
OUT = Path('data/catalog/ltmd_u1_w2_math_internal_recovery_audit.csv')
REC = Path('data/catalog/ltmd_u1_w2_math_internal_recoveries.csv')
REPORT = Path('data/catalog/ltmd_u1_w2_math_internal_recovery_audit.md')
VERSION = 'LTMD_U1_W2_MATH_INTERNAL_RECOVERY_0.1'
MIN_ANCHORS = 4
RADIUS = 3
OFFSETS = range(-3, 4)


def norm(text):
    text = unicodedata.normalize('NFKD', text or '')
    text = ''.join(c for c in text if not unicodedata.combining(c)).casefold()
    return re.sub(r'\s+', ' ', text).strip()


def main():
    manifest = list(csv.DictReader(MAN.open(encoding='utf-8')))
    scope = {r['viewer_key']: r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))}
    if len(scope) != 64:
        raise SystemExit(f'expected 64 W2 scope viewers, got {len(scope)}')

    by_viewer = defaultdict(dict)
    for r in manifest:
        by_viewer[r['viewer_key']][int(r['viewer_page'])] = r

    gaps = [r for r in manifest if r['asset_status'] == 'internal_unserved']
    audit = []
    recovered = []

    for gap in gaps:
        viewer = gap['viewer_key']
        page = int(gap['viewer_page'])
        meta = scope[viewer]
        anchors = []
        for q in range(max(1, page - RADIUS), page + RADIUS + 1):
            if q == page:
                continue
            r = by_viewer[viewer].get(q)
            if r and r['asset_status'] == 'source_jpeg' and r['sha256']:
                anchors.append((q, r['sha256'], int(r['byte_size'])))

        candidates = [
            v for v, m in scope.items()
            if v != viewer
            and m['grade_code'] == meta['grade_code']
            and norm(m['title_core']) == norm(meta['title_core'])
        ]
        accepted = []
        for cand in candidates:
            cmap = by_viewer.get(cand, {})
            for offset in OFFSETS:
                mapped = [(q, q + offset, sha, size) for q, sha, size in anchors if q + offset >= 1]
                if len(mapped) < MIN_ANCHORS:
                    continue
                compared = 0
                matches = 0
                mismatches = 0
                for source_q, cand_q, sha, size in mapped:
                    cr = cmap.get(cand_q)
                    if not cr or cr['asset_status'] != 'source_jpeg':
                        mismatches += 1
                        compared += 1
                        continue
                    compared += 1
                    if cr['sha256'] == sha and int(cr['byte_size']) == size:
                        matches += 1
                    else:
                        mismatches += 1
                target_page = page + offset
                target = cmap.get(target_page)
                target_ok = bool(target and target['asset_status'] == 'source_jpeg' and target['sha256'])
                if matches >= MIN_ANCHORS and mismatches == 0 and target_ok:
                    accepted.append({
                        'candidate_viewer_key': cand,
                        'candidate_offset': offset,
                        'anchor_count_compared': compared,
                        'anchor_hash_matches': matches,
                        'anchor_hash_mismatches': mismatches,
                        'mapped_target_page': target_page,
                        'target_sha256': target['sha256'],
                        'target_byte_size': target['byte_size'],
                        'target_url': target['source_asset_url'],
                    })

        unique_keys = {(x['candidate_viewer_key'], x['candidate_offset'], x['mapped_target_page']) for x in accepted}
        if len(unique_keys) == 1:
            a = accepted[0]
            decision = 'recovered_unique_cryptographic_alignment'
            recovered.append({
                'recovery_version': VERSION,
                'source_viewer_key': viewer,
                'source_book_id': meta['book_id'],
                'source_generation': meta['catalog_generation'],
                'source_grade_code': meta['grade_code'],
                'source_target_page': page,
                'recovery_viewer_key': a['candidate_viewer_key'],
                'recovery_generation': scope[a['candidate_viewer_key']]['catalog_generation'],
                'fixed_offset': a['candidate_offset'],
                'mapped_target_page': a['mapped_target_page'],
                'recovered_asset_url': a['target_url'],
                'recovered_sha256': a['target_sha256'],
                'recovered_byte_size': a['target_byte_size'],
                'anchor_hash_matches': a['anchor_hash_matches'],
                'anchor_hash_mismatches': a['anchor_hash_mismatches'],
                'interpretive_limit': 'Technical asset recovery only; not full bibliographic identity.',
            })
        elif len(unique_keys) > 1:
            decision = 'ambiguous_multiple_cryptographic_candidates'
        elif len(anchors) < MIN_ANCHORS:
            decision = 'insufficient_source_anchors'
        else:
            decision = 'no_cryptographic_recovery_found'

        audit.append({
            'audit_version': VERSION,
            'source_viewer_key': viewer,
            'source_book_id': meta['book_id'],
            'source_generation': meta['catalog_generation'],
            'source_grade_code': meta['grade_code'],
            'source_target_page': page,
            'source_anchor_count': len(anchors),
            'candidate_viewer_count': len(candidates),
            'accepted_alignment_count': len(unique_keys),
            'decision': decision,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    afields = ['audit_version','source_viewer_key','source_book_id','source_generation','source_grade_code','source_target_page','source_anchor_count','candidate_viewer_count','accepted_alignment_count','decision']
    with OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=afields)
        w.writeheader(); w.writerows(audit)

    rfields = ['recovery_version','source_viewer_key','source_book_id','source_generation','source_grade_code','source_target_page','recovery_viewer_key','recovery_generation','fixed_offset','mapped_target_page','recovered_asset_url','recovered_sha256','recovered_byte_size','anchor_hash_matches','anchor_hash_mismatches','interpretive_limit']
    with REC.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rfields)
        w.writeheader(); w.writerows(recovered)

    decisions = sorted({r['decision'] for r in audit})
    lines = [
        '# LTMD-U1 W2 — recuperación criptográfica de huecos internos de Matemáticas', '',
        f'Versión: `{VERSION}`.', '',
        f'- Huecos internos auditados: **{len(gaps)}**.',
        f'- Recuperaciones unívocas: **{len(recovered)}**.',
    ]
    for d in decisions:
        lines.append(f"- `{d}`: **{sum(r['decision'] == d for r in audit)}**.")
    lines += [
        '', '## Regla',
        'La auditoría reutiliza exclusivamente los hashes del manifiesto de activos ya materializado. No descarga fuentes adicionales. Requiere título nuclear normalizado y grado iguales, un offset fijo, al menos cuatro anchors vecinos byte-idénticos, cero discrepancias y una página objetivo servida. La recuperación no demuestra identidad bibliográfica total.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
