#!/usr/bin/env python3
"""Recover narrowly defined OCR confusions in W7 reprint statements.

Scope is intentionally tiny: only W7 objects that already have a strong school
cycle but no strict statement matching its start year are inspected. The only
normalization allowed is the documented OCR confusion in Spanish `reimpresión`:
`i` may be read as lowercase/uppercase `l` or digit `1` immediately after `re`.

A recovered candidate must:
* appear on a SHA-verified fingerprint page;
* be supported by >=2 distinct PSM modes on that same page;
* carry a year equal to the already observed school-cycle start;
* preserve raw token variants and PSM provenance.

No edition years, ordinals, cycles or catalog generations are imputed.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

VERSION = 'LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.1'
FINGERPRINT_VERSION = 'LTMD_U1_W7_ADMITTED_BIBLIOGRAPHIC_FINGERPRINTS_0.1'
CANDIDATE_VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.1'
FINGERPRINT = Path('data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.csv')
CANDIDATES = Path('data/catalog/ltmd_bibliographic_instance_candidates.csv')
OUT = Path('data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.md')

PSM_PREFIX_RE = re.compile(r'^psm(\d+):\s*(.*)$', re.S)
REPRINT_FUZZY_RE = re.compile(
    r'\b(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima)\s+'
    r'(re[iIl1]mpresi[oó]n)\D{0,18}((?:19|20)\d{2})',
    re.I,
)
ORDINAL = {
    'primera': 'first', 'segunda': 'second', 'tercera': 'third', 'cuarta': 'fourth',
    'quinta': 'fifth', 'sexta': 'sixth', 'septima': 'seventh', 'séptima': 'seventh',
    'octava': 'eighth', 'novena': 'ninth', 'decima': 'tenth', 'décima': 'tenth',
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def normalize_ordinal(value: str) -> str:
    low = ''.join(
        ch for ch in unicodedata.normalize('NFKD', value.lower())
        if not unicodedata.combining(ch)
    )
    return ORDINAL.get(low, low)


def cycle_start(value: str) -> int:
    m = re.fullmatch(r'((?:19|20)\d{2})-((?:19|20)\d{2})', value)
    if not m:
        raise SystemExit(f'invalid school cycle: {value}')
    first, second = map(int, m.groups())
    if second != first + 1:
        raise SystemExit(f'nonconsecutive school cycle: {value}')
    return first


def main() -> None:
    candidates = read_csv(CANDIDATES)
    if {r['candidate_version'] for r in candidates} != {CANDIDATE_VERSION}:
        raise SystemExit('instance-candidate version drift')
    targets = {
        r['viewer_key']: r
        for r in candidates
        if r['candidate_status'] == 'no_candidate_no_statement_matches_cycle_start'
    }
    if len(targets) != 5:
        raise SystemExit(f'expected 5 cycle-known/no-statement targets, found {len(targets)}')

    fp_rows = read_csv(FINGERPRINT)
    if {r['fingerprint_version'] for r in fp_rows} != {FINGERPRINT_VERSION}:
        raise SystemExit('fingerprint version drift')
    if any(r.get('sha_verified') != '1' for r in fp_rows):
        raise SystemExit('recovery refuses non-SHA-verified fingerprint rows')

    support: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for row in fp_rows:
        viewer = row['viewer_key']
        if viewer not in targets:
            continue
        expected_year = cycle_start(targets[viewer]['school_cycle'])
        for chunk in (row.get('bibliographic_lines') or '').split(' || '):
            m = PSM_PREFIX_RE.match(chunk.strip())
            if not m:
                continue
            psm = int(m.group(1))
            text = m.group(2)
            for hit in REPRINT_FUZZY_RE.finditer(text):
                ordinal, raw_token, year_text = hit.groups()
                year = int(year_text)
                if year != expected_year:
                    continue
                normalized = f'{normalize_ordinal(ordinal)}_reprint:{year}'
                key = (viewer, row['viewer_page'], row['source_sha256'], normalized)
                item = support.setdefault(key, {
                    'psm_modes': set(),
                    'raw_tokens': set(),
                    'raw_snippets': set(),
                    'source_image_index': row['source_image_index'],
                    'source_byte_size': row['source_byte_size'],
                })
                item['psm_modes'].add(psm)
                item['raw_tokens'].add(raw_token)
                item['raw_snippets'].add(' '.join(hit.group(0).split()))

    records = []
    for (viewer, page, sha, normalized), item in sorted(support.items()):
        modes = sorted(item['psm_modes'])
        if len(modes) < 2:
            continue
        target = targets[viewer]
        records.append({
            'recovery_version': VERSION,
            'viewer_key': viewer,
            'catalog_generation': target['catalog_generation'],
            'school_cycle': target['school_cycle'],
            'school_cycle_start_year': cycle_start(target['school_cycle']),
            'recovered_statement_value': normalized,
            'evidence_viewer_page': page,
            'evidence_image_index': item['source_image_index'],
            'evidence_sha256': sha,
            'evidence_byte_size': item['source_byte_size'],
            'psm_support_count': len(modes),
            'psm_modes': ';'.join(map(str, modes)),
            'raw_reprint_tokens': ';'.join(sorted(item['raw_tokens'])),
            'raw_matched_snippets': ' || '.join(sorted(item['raw_snippets'])),
            'normalization_rule': 'only re[iIl1]mpresion-token OCR confusion normalized to reimpresion',
            'year_matches_school_cycle_start': 1,
            'human_validated': 0,
        })

    # A viewer must not acquire competing recovered statements under this narrow
    # rule. If it does, the recovery is ambiguous and must be reviewed instead.
    by_viewer = defaultdict(list)
    for r in records:
        by_viewer[r['viewer_key']].append(r)
    ambiguous = {k: v for k, v in by_viewer.items() if len(v) > 1}
    if ambiguous:
        raise SystemExit(f'ambiguous recovered statements: {sorted(ambiguous)}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        'recovery_version', 'viewer_key', 'catalog_generation', 'school_cycle',
        'school_cycle_start_year', 'recovered_statement_value',
        'evidence_viewer_page', 'evidence_image_index', 'evidence_sha256',
        'evidence_byte_size', 'psm_support_count', 'psm_modes',
        'raw_reprint_tokens', 'raw_matched_snippets', 'normalization_rule',
        'year_matches_school_cycle_start', 'human_validated',
    ]
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)

    recovered_viewers = sorted(by_viewer)
    unrecovered = sorted(set(targets) - set(recovered_viewers))
    lines = [
        '# LTMD-U1 W7 — recuperación conservadora de confusión OCR en reimpresión',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Objetos objetivo con ciclo pero sin statement coincidente: **{len(targets)}**.',
        f'- Objetos con reimpresión recuperada por regla estrecha: **{len(recovered_viewers)}**.',
        f'- Objetos que permanecen sin statement coincidente: **{len(unrecovered)}**.',
        '',
        'La única normalización permitida es la confusión OCR documentada dentro de la palabra `reimpresión`: `i` puede aparecer como `l`, `I` o `1` inmediatamente después de `re`. Se exige el mismo ordinal+año en ≥2 PSM y que el año coincida con el inicio del ciclo escolar ya observado. No se modifica ningún otro token ni se usa `catalog_generation`.',
        '',
        '## Recuperaciones',
        '',
        '| objeto | ciclo | statement recuperado | página | PSM | tokens OCR |',
        '|---|---|---|---:|---|---|',
    ]
    for r in records:
        lines.append(
            f"| `{r['viewer_key']}` | `{r['school_cycle']}` | `{r['recovered_statement_value']}` | "
            f"{r['evidence_viewer_page']} | `{r['psm_modes']}` | `{r['raw_reprint_tokens']}` |"
        )
    lines += [
        '',
        '## Sin recuperación',
        '',
    ]
    for viewer in unrecovered:
        lines.append(f'- `{viewer}`: permanece sin statement que coincida con `{targets[viewer]["school_cycle"]}`.')
    lines += [
        '',
        '## Límite epistemológico',
        '',
        'Una recuperación aquí sólo repara una confusión de caracteres OCR dentro de un marcador bibliográfico explícito y repetido. Sigue siendo `human_validated=0`. La recuperación puede alimentar una nueva versión de observaciones/candidatos, pero no convierte el año en fecha histórica humana validada ni autoriza imputar los objetos que continúan sin match.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('targets', len(targets))
    print('recovered', len(recovered_viewers))
    print('unrecovered', len(unrecovered))
    for r in records:
        print(r['viewer_key'], r['recovered_statement_value'], r['psm_modes'])


if __name__ == '__main__':
    main()
