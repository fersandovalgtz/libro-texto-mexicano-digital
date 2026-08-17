#!/usr/bin/env python3
"""Recover narrowly defined OCR confusions in W7 reprint statements — v0.2.

Unlike 0.1, target viewers are derived from the *pre-recovery* bibliographic
candidate-support audit rather than from the mutable final instance-candidate
table. This removes a circular dependency.

Target derivation:
* source-verified W7 admitted fingerprint exists;
* candidate-support audit has exactly one strong school-cycle value;
* no strong edition/reprint candidate already matches that cycle's start year.

Recovery normalization remains unchanged and intentionally narrow:
`reimpresión` may have its `i` read as l/I/1 immediately after `re`.
A recovered statement requires >=2 PSM modes on the same SHA-verified page and
a year equal to the strong school-cycle start.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

VERSION = 'LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.2'
SUPPORT_VERSION = 'LTMD_U1_W7_BIBLIOGRAPHIC_CANDIDATE_SUPPORT_0.1'
FINGERPRINT_VERSION = 'LTMD_U1_W7_ADMITTED_BIBLIOGRAPHIC_FINGERPRINTS_0.1'
SUPPORT = Path('data/catalog/ltmd_u1_w7_bibliographic_candidate_support.csv')
FINGERPRINT = Path('data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.csv')
OUT = Path('data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.md')

PSM_PREFIX_RE = re.compile(r'^psm(\d+):\s*(.*)$', re.S)
REPRINT_FUZZY_RE = re.compile(
    r'\b(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima)\s+'
    r'(re[iIl1]mpresi[oó]n)\D{0,18}((?:19|20)\d{2})',
    re.I,
)
HISTORY_VALUE_RE = re.compile(r'^[a-z]+_(?:edition|reprint):((?:19|20)\d{2})$')
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


def derive_targets() -> dict[str, dict[str, str | int]]:
    rows = read_csv(SUPPORT)
    if {r['audit_version'] for r in rows} != {SUPPORT_VERSION}:
        raise SystemExit('candidate-support version drift')
    strong = [r for r in rows if r['promotable_under_0_1_rule'] == '1']
    by_viewer = defaultdict(list)
    for row in strong:
        by_viewer[row['viewer_key']].append(row)

    targets: dict[str, dict[str, str | int]] = {}
    for viewer, items in by_viewer.items():
        cycles = sorted({r['candidate_value'] for r in items if r['candidate_kind'] == 'school_cycle'})
        if not cycles:
            continue
        if len(cycles) != 1:
            # Multiple strong cycles are intrinsically ambiguous and do not
            # enter this recovery path.
            continue
        cycle = cycles[0]
        start = cycle_start(cycle)
        matching_statement = False
        for r in items:
            if r['candidate_kind'] not in {'edition', 'reprint'}:
                continue
            m = HISTORY_VALUE_RE.fullmatch(r['candidate_value'])
            if m and int(m.group(1)) == start:
                matching_statement = True
                break
        if not matching_statement:
            exemplar = items[0]
            targets[viewer] = {
                'catalog_generation': exemplar['catalog_generation'],
                'school_cycle': cycle,
                'school_cycle_start_year': start,
            }

    if len(targets) != 5:
        raise SystemExit(f'expected 5 pre-recovery targets from support audit, found {len(targets)}: {sorted(targets)}')
    return targets


def main() -> None:
    targets = derive_targets()
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
        expected_year = int(targets[viewer]['school_cycle_start_year'])
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
                    'psm_modes': set(), 'raw_tokens': set(), 'raw_snippets': set(),
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
            'school_cycle_start_year': target['school_cycle_start_year'],
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
            'target_derivation_rule': 'strong school_cycle plus no strong exact edition/reprint at cycle start',
            'year_matches_school_cycle_start': 1,
            'human_validated': 0,
        })

    by_viewer = defaultdict(list)
    for r in records:
        by_viewer[r['viewer_key']].append(r)
    if any(len(v) > 1 for v in by_viewer.values()):
        raise SystemExit('ambiguous recovered statements under narrow rule')
    if len(records) != 2:
        raise SystemExit(f'expected two reproducible recoveries, found {len(records)}')
    if set(by_viewer) != {'H2011P5CI326', 'H2014P4FCA'}:
        raise SystemExit(f'unexpected recovered viewer set: {sorted(by_viewer)}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)

    unrecovered = sorted(set(targets) - set(by_viewer))
    lines = [
        '# LTMD-U1 W7 — recuperación conservadora de confusión OCR en reimpresión',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '- Cohorte objetivo derivada reproduciblemente desde el audit pre-recovery: **5** objetos.',
        '- Objetos con reimpresión recuperada por regla estrecha: **2**.',
        '- Objetos que permanecen sin statement coincidente: **3**.',
        '',
        '0.2 elimina la dependencia circular de 0.1: los targets se derivan de `LTMD_U1_W7_BIBLIOGRAPHIC_CANDIDATE_SUPPORT_0.1`, buscando un ciclo escolar fuerte sin edición/reimpresión fuerte que coincida con su año inicial. La tabla final de candidatos no participa en la selección.',
        '',
        'La única normalización permitida sigue siendo `reimpresión` con `i→l/I/1` inmediatamente después de `re`. Se exige ≥2 PSM sobre la misma página SHA-verificada y coincidencia exacta con el inicio del ciclo.',
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
    lines += ['', '## Sin recuperación', '']
    for viewer in unrecovered:
        lines.append(f"- `{viewer}`: permanece sin statement compatible con `{targets[viewer]['school_cycle']}`.")
    lines += [
        '',
        '## Límite epistemológico',
        '',
        'La recuperación repara únicamente una confusión de caracteres OCR repetida y documentada. `human_validated=0` permanece. Los tres objetos no recuperados no reciben ninguna imputación y el proceso no usa `catalog_generation` para derivar fechas.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('targets', len(targets))
    print('recovered', len(records))
    print('unrecovered', len(unrecovered))
    for r in records:
        print(r['viewer_key'], r['recovered_statement_value'], r['psm_modes'])


if __name__ == '__main__':
    main()
