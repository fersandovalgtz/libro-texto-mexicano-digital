#!/usr/bin/env python3
"""Audit W7 bibliographic candidates across independent OCR segmentation modes.

Input is the bounded, source-verified W7 fingerprint table. For every structured
candidate already detected on a page, this script re-extracts evidence from the
retained PSM-prefixed marker lines and counts distinct OCR segmentation modes
that independently support the same candidate on the same SHA-verified page.

Promotion rule used by this audit:
* edition/reprint/school-cycle: strong iff supported by >=2 distinct PSM modes;
* ISBN-13: strong iff supported by >=2 distinct PSM modes AND checksum-valid;
* candidates found only in combined/cross-line OCR or one mode remain review;
* no candidate is interpreted as the current edition of the object here.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

VERSION = 'LTMD_U1_W7_BIBLIOGRAPHIC_CANDIDATE_SUPPORT_0.1'
INPUT = Path('data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.csv')
OUT = Path('data/catalog/ltmd_u1_w7_bibliographic_candidate_support.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_bibliographic_candidate_support.md')

ISBN_RE = re.compile(r'97[89](?:[-\s]?\d){10}')
CYCLE_RE = re.compile(r'ciclo\s+escolar\D{0,12}((?:19|20)\d{2})\s*[-–/]\s*((?:19|20)\d{2})', re.I)
EDITION_RE = re.compile(
    r'\b(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima)\s+'
    r'edici[oó]n\D{0,18}((?:19|20)\d{2})', re.I,
)
REPRINT_RE = re.compile(
    r'\b(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima)\s+'
    r'reimpresi[oó]n\D{0,18}((?:19|20)\d{2})', re.I,
)
PSM_PREFIX_RE = re.compile(r'^psm(\d+):\s*(.*)$', re.S)

ORDINAL = {
    'primera': 'first', 'segunda': 'second', 'tercera': 'third', 'cuarta': 'fourth',
    'quinta': 'fifth', 'sexta': 'sixth', 'septima': 'seventh', 'séptima': 'seventh',
    'octava': 'eighth', 'novena': 'ninth', 'decima': 'tenth', 'décima': 'tenth',
}


def normalize_ordinal(value: str) -> str:
    low = ''.join(
        ch for ch in unicodedata.normalize('NFKD', value.lower())
        if not unicodedata.combining(ch)
    )
    return ORDINAL.get(low, low)


def canonical_isbn(value: str) -> str:
    digits = re.sub(r'\D', '', value)
    return digits if len(digits) != 13 else f'{digits[:3]}-{digits[3:6]}-{digits[6:9]}-{digits[9:12]}-{digits[12:]}'


def isbn13_valid(value: str) -> bool:
    digits = re.sub(r'\D', '', value)
    if len(digits) != 13 or not digits.isdigit():
        return False
    total = sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(digits[:12]))
    check = (10 - (total % 10)) % 10
    return check == int(digits[12])


def candidates_from_line(text: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for m in ISBN_RE.finditer(text):
        out['isbn'].add(canonical_isbn(m.group(0)))
    for m in CYCLE_RE.finditer(text):
        out['school_cycle'].add(f'{m.group(1)}-{m.group(2)}')
    for m in EDITION_RE.finditer(text):
        out['edition'].add(f'{normalize_ordinal(m.group(1))}_edition:{m.group(2)}')
    for m in REPRINT_RE.finditer(text):
        out['reprint'].add(f'{normalize_ordinal(m.group(1))}_reprint:{m.group(2)}')
    return out


def split_values(value: str) -> list[str]:
    return [v for v in value.split(';') if v]


def main() -> None:
    with INPUT.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 300:
        raise SystemExit(f'expected 300 source-verified fingerprint rows, found {len(rows)}')
    if any(r.get('sha_verified') != '1' for r in rows):
        raise SystemExit('candidate-support audit refuses non-SHA-verified fingerprint rows')

    records: list[dict[str, str | int]] = []
    per_viewer = defaultdict(lambda: defaultdict(list))

    for row in rows:
        evidence_by_mode: dict[int, dict[str, set[str]]] = {}
        for chunk in (row.get('bibliographic_lines') or '').split(' || '):
            m = PSM_PREFIX_RE.match(chunk.strip())
            if not m:
                continue
            psm = int(m.group(1))
            found = candidates_from_line(m.group(2))
            if psm not in evidence_by_mode:
                evidence_by_mode[psm] = defaultdict(set)
            for kind, values in found.items():
                evidence_by_mode[psm][kind].update(values)

        source_candidates = {
            'isbn': split_values(row.get('isbn_candidates', '')),
            'school_cycle': split_values(row.get('school_cycle_candidates', '')),
            'edition': split_values(row.get('edition_candidates', '')),
            'reprint': split_values(row.get('reprint_candidates', '')),
        }
        for kind, values in source_candidates.items():
            for value in values:
                modes = sorted(
                    psm for psm, found in evidence_by_mode.items()
                    if value in found.get(kind, set())
                )
                checksum = ''
                if kind == 'isbn':
                    checksum = '1' if isbn13_valid(value) else '0'
                if len(modes) >= 2 and (kind != 'isbn' or checksum == '1'):
                    support_class = 'strong_multipsm'
                    promotable = 1
                elif kind == 'isbn' and checksum == '0':
                    support_class = 'invalid_isbn13_checksum'
                    promotable = 0
                elif len(modes) == 1:
                    support_class = 'single_psm'
                    promotable = 0
                else:
                    support_class = 'cross_line_or_unretained_only'
                    promotable = 0

                rec = {
                    'audit_version': VERSION,
                    'viewer_key': row['viewer_key'],
                    'catalog_generation': row['catalog_generation'],
                    'grade_code': row['grade_code'],
                    'viewer_page': row['viewer_page'],
                    'source_sha256': row['source_sha256'],
                    'candidate_kind': kind,
                    'candidate_value': value,
                    'psm_support_count': len(modes),
                    'psm_modes': ';'.join(map(str, modes)),
                    'isbn13_checksum_valid': checksum,
                    'support_class': support_class,
                    'promotable_under_0_1_rule': promotable,
                }
                records.append(rec)
                per_viewer[row['viewer_key']][kind].append(rec)

    if not records:
        raise SystemExit('no structured candidates to audit')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)

    classes = Counter(str(r['support_class']) for r in records)
    strong = [r for r in records if int(r['promotable_under_0_1_rule']) == 1]
    strong_viewers = sorted({str(r['viewer_key']) for r in strong})
    invalid_isbns = [r for r in records if r['support_class'] == 'invalid_isbn13_checksum']

    lines = [
        '# LTMD-U1 W7 — auditoría de soporte de candidatos bibliográficos',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Filas fingerprint fuente verificadas: **{len(rows)}/300**.',
        f'- Candidatos estructurados auditados: **{len(records)}**.',
        f'- Candidatos con soporte fuerte multímodo: **{len(strong)}**.',
        f'- Visores con ≥1 candidato fuerte: **{len(strong_viewers)}/25**.',
        f'- ISBN rechazados por checksum ISBN-13: **{len(invalid_isbns)}**.',
        '',
        'Regla 0.1: edición, reimpresión y ciclo escolar requieren el mismo candidato en ≥2 modos PSM sobre la misma página SHA-verificada. ISBN requiere además checksum ISBN-13 válido. La regla identifica **observaciones textuales reproducibles**, no decide cuál edición es la “actual” del objeto.',
        '',
        '## Clases de soporte',
        '',
    ]
    for cls, n in sorted(classes.items()):
        lines.append(f'- `{cls}`: **{n}**.')

    lines += [
        '',
        '## Candidatos fuertes por objeto',
        '',
        '| objeto | edición | reimpresión | ciclo | ISBN válido |',
        '|---|---|---|---|---|',
    ]
    for key in sorted(per_viewer):
        cells = []
        for kind in ('edition', 'reprint', 'school_cycle', 'isbn'):
            values = sorted({
                str(r['candidate_value'])
                for r in per_viewer[key].get(kind, [])
                if int(r['promotable_under_0_1_rule']) == 1
            })
            cells.append(', '.join(values) or '—')
        lines.append(f"| `{key}` | `{cells[0]}` | `{cells[1]}` | `{cells[2]}` | `{cells[3]}` |")

    if invalid_isbns:
        lines += [
            '',
            '## ISBN rechazados',
            '',
            '| objeto | página | candidato OCR | soporte PSM |',
            '|---|---:|---|---|',
        ]
        for r in invalid_isbns:
            lines.append(
                f"| `{r['viewer_key']}` | {r['viewer_page']} | `{r['candidate_value']}` | `{r['psm_modes']}` |"
            )

    lines += [
        '',
        '## Límite epistemológico',
        '',
        'Un candidato `strong_multipsm` demuestra que varios modos de segmentación OCR leen de forma concordante la misma declaración estructurada en una página institucional cuya huella binaria está congelada. No demuestra por sí solo que esa declaración sea la edición vigente del objeto ni reemplaza una futura validación humana de la transcripción. La promoción a observaciones canónicas debe conservar página, SHA y clase de soporte.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('candidates', len(records))
    print('strong', len(strong))
    print('strong_viewers', len(strong_viewers))
    print('invalid_isbn13', len(invalid_isbns))


if __name__ == '__main__':
    main()
