#!/usr/bin/env python3
"""Probe logical pages 13-20 for the 12 admitted W7 objects lacking school_cycle.

Target selection is derived from the current source-admitted cohort plus
LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4: a viewer is targeted iff it is source-
admitted and has no `school_cycle_statement` observation.

The probe is deliberately bounded to eight additional pages per target. Every
page is downloaded temporarily and must match SHA-256 + byte size in the frozen
W7 asset manifest before OCR. PSM 3, 6 and 11 are run independently. Images and
full OCR are never persisted.

A school-cycle candidate is `strong_multipsm` only when the same valid
`YYYY-YYYY+1` value is read by >=2 PSM modes on the same source page. This probe
does not itself promote observations or instance candidates.
"""
from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

VERSION = 'LTMD_U1_W7_MISSING_CYCLE_WINDOW_13_20_0.1'
OBS_VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4'
ADMISSIBILITY = Path('data/catalog/ltmd_u1_w7_source_admissibility.csv')
OBS = Path('data/catalog/ltmd_bibliographic_observations.csv')
ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w7_missing_cycle_window_13_20.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_missing_cycle_window_13_20.md')
PAGES = tuple(range(13, 21))
PSMS = (3, 6, 11)
UA = 'LibroTextoMexicanoDigital/U1-W7 missing-cycle bounded probe 0.1'

EXPECTED_TARGETS = {
    'H2008P1CI251', 'H2008P2CI258', 'H2008P3CI264', 'H2008P4CI269',
    'H2011P3CI308',
    'H2014P1FCA', 'H2014P2FCA', 'H2014P3FCA', 'H2014P6FCA',
    'H2019P1FCA', 'H2019P2FCA', 'H2019P3FCA',
}

CYCLE_RE = re.compile(
    r'ciclo\s+escolar\D{0,18}((?:19|20)\d{2})\s*[-–/]\s*((?:19|20)\d{2})',
    re.I,
)
MARKER_RE = re.compile(
    r'(ciclo\s+escolar|edici[oó]n|reimpresi[oó]n|secretar[ií]a\s+de\s+educaci[oó]n|isbn)',
    re.I,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def derive_targets() -> dict[str, dict[str, str]]:
    gate_rows = read_csv(ADMISSIBILITY)
    admitted = {
        r['viewer_key']: r for r in gate_rows
        if r.get('ocr_source_admitted') == '1'
    }
    if len(admitted) != 25:
        raise SystemExit(f'expected 25 admitted W7 viewers, found {len(admitted)}')

    observations = read_csv(OBS)
    if {r['observation_version'] for r in observations} != {OBS_VERSION}:
        raise SystemExit('bibliographic observation version drift')
    cycle_viewers = {
        r['viewer_key'] for r in observations
        if r['field'] == 'school_cycle_statement'
    }
    targets = {k: v for k, v in admitted.items() if k not in cycle_viewers}
    if set(targets) != EXPECTED_TARGETS:
        raise SystemExit(
            'missing-cycle target drift: '
            f'expected={sorted(EXPECTED_TARGETS)} observed={sorted(targets)}'
        )
    return targets


def load_assets(targets: dict[str, dict[str, str]]) -> dict[tuple[str, int], dict[str, str]]:
    selected = {}
    for row in read_csv(ASSETS):
        key = row.get('viewer_key', '')
        if key not in targets:
            continue
        try:
            page = int(row.get('viewer_page', ''))
        except ValueError:
            continue
        if page not in PAGES:
            continue
        if row.get('asset_status') != 'source_jpeg' or not row.get('sha256'):
            raise SystemExit(f'{key} page {page}: not a hashable source_jpeg')
        selected[(key, page)] = row
    expected = {(key, page) for key in targets for page in PAGES}
    missing = sorted(expected - set(selected))
    if missing:
        raise SystemExit(f'missing bounded source pages: {missing[:20]}')
    if len(selected) != len(expected):
        raise SystemExit('duplicate bounded source-page keys')
    return selected


def fetch_verified(row: dict[str, str]) -> bytes:
    with urlopen(Request(row['source_asset_url'], headers={'User-Agent': UA}), timeout=45) as response:
        data = response.read()
    sha = hashlib.sha256(data).hexdigest()
    if sha != row['sha256']:
        raise SystemExit(
            f"{row['viewer_key']} page {row['viewer_page']}: SHA mismatch "
            f"{sha} != {row['sha256']}"
        )
    if len(data) != int(row['byte_size']):
        raise SystemExit(
            f"{row['viewer_key']} page {row['viewer_page']}: byte-size mismatch"
        )
    return data


def ocr(data: bytes, psm: int) -> str:
    if not shutil.which('tesseract'):
        raise SystemExit('tesseract is required')
    with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp:
        tmp.write(data); tmp.flush()
        proc = subprocess.run(
            ['tesseract', tmp.name, 'stdout', '-l', 'spa', '--psm', str(psm)],
            check=True, capture_output=True, text=True,
        )
    return proc.stdout


def cycles(text: str) -> set[str]:
    out = set()
    for m in CYCLE_RE.finditer(text):
        first, second = map(int, m.groups())
        if second == first + 1:
            out.add(f'{first}-{second}')
    return out


def retained_lines(text: str, psm: int) -> list[str]:
    lines = [' '.join(line.split()) for line in text.splitlines() if line.strip()]
    return [f'psm{psm}: {line}' for line in lines if MARKER_RE.search(line)]


def main() -> None:
    targets = derive_targets()
    assets = load_assets(targets)
    rows_out = []
    strong_by_viewer: dict[str, list[dict[str, object]]] = defaultdict(list)

    for viewer in sorted(targets):
        for page in PAGES:
            row = assets[(viewer, page)]
            data = fetch_verified(row)
            mode_cycles: dict[int, set[str]] = {}
            marker_lines = []
            for psm in PSMS:
                text = ocr(data, psm)
                mode_cycles[psm] = cycles(text)
                marker_lines.extend(retained_lines(text, psm))

            candidate_modes: dict[str, list[int]] = defaultdict(list)
            for psm, values in mode_cycles.items():
                for value in values:
                    candidate_modes[value].append(psm)
            strong = {
                value: sorted(modes)
                for value, modes in candidate_modes.items()
                if len(set(modes)) >= 2
            }
            for value, modes in strong.items():
                strong_by_viewer[viewer].append({
                    'page': page,
                    'value': value,
                    'modes': modes,
                    'sha': row['sha256'],
                })

            rows_out.append({
                'probe_version': VERSION,
                'viewer_key': viewer,
                'catalog_generation': targets[viewer]['catalog_generation'],
                'grade_code': targets[viewer]['grade_code'],
                'viewer_page': page,
                'source_image_index': row['source_image_index'],
                'source_sha256': row['sha256'],
                'source_byte_size': row['byte_size'],
                'sha_verified': 1,
                'psm_modes': ';'.join(map(str, PSMS)),
                'cycle_candidates_psm3': ';'.join(sorted(mode_cycles[3])),
                'cycle_candidates_psm6': ';'.join(sorted(mode_cycles[6])),
                'cycle_candidates_psm11': ';'.join(sorted(mode_cycles[11])),
                'strong_cycle_candidates': ';'.join(sorted(strong)),
                'strong_cycle_support': ';'.join(
                    f"{value}=>{','.join(map(str, modes))}" for value, modes in sorted(strong.items())
                ),
                'bibliographic_marker_lines': ' || '.join(dict.fromkeys(marker_lines))[:12000],
            })
        print(viewer, 'strong_cycles', strong_by_viewer.get(viewer, []), flush=True)

    if len(rows_out) != 12 * 8:
        raise SystemExit(f'expected 96 page rows, found {len(rows_out)}')
    if sum(int(r['sha_verified']) for r in rows_out) != 96:
        raise SystemExit('not all bounded pages are SHA verified')

    # A viewer with competing strong cycle values is not promotable; report it
    # but fail so future logic cannot silently choose one.
    for viewer, items in strong_by_viewer.items():
        values = {str(x['value']) for x in items}
        if len(values) > 1:
            raise SystemExit(f'{viewer}: competing strong cycle values in pages 13-20: {sorted(values)}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows_out[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows_out)

    found = sorted(strong_by_viewer)
    missing = sorted(set(targets) - set(found))
    lines = [
        '# LTMD-U1 W7 — probe acotado de ciclos faltantes, páginas 13–20',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '- Targets derivados desde W7 admitido + Observations 0.4 sin `school_cycle_statement`: **12**.',
        '- Ventana adicional: páginas lógicas **13–20**.',
        '- Páginas descargadas temporalmente y verificadas SHA-256+tamaño: **96/96**.',
        '- OCR independiente: PSM **3, 6, 11** por página.',
        f'- Objetos con ≥1 `school_cycle` fuerte multímodo en la ventana: **{len(found)}/12**.',
        f'- Objetos sin ciclo fuerte en la ventana: **{len(missing)}/12**.',
        '',
        'Un ciclo fuerte requiere el mismo `YYYY-YYYY+1` en ≥2 PSM sobre la misma página fuente SHA-verificada. Este probe **no promueve automáticamente observaciones ni candidatos**.',
        '',
        '## Ciclos fuertes encontrados',
        '',
        '| objeto | página | ciclo | PSM | SHA |',
        '|---|---:|---|---|---|',
    ]
    for viewer in found:
        for item in strong_by_viewer[viewer]:
            lines.append(
                f"| `{viewer}` | {item['page']} | `{item['value']}` | "
                f"`{';'.join(map(str, item['modes']))}` | `{str(item['sha'])[:16]}…` |"
            )
    if not found:
        lines.append('| — | — | — | — | — |')

    lines += ['', '## Sin ciclo fuerte en páginas 13–20', '']
    for viewer in missing:
        lines.append(f'- `{viewer}`.')
    lines += [
        '',
        '## Límite epistemológico',
        '',
        'Cero hallazgos en esta ventana significa únicamente que páginas 13–20 no aportaron un ciclo fuerte bajo el contrato OCR 0.1. No demuestra que el ejemplar carezca de ciclo escolar. Si aparecen ciclos fuertes, una promoción posterior deberá preservar página, SHA y soporte PSM y recalcular Observations/Candidates de forma versionada.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('targets', len(targets))
    print('rows', len(rows_out))
    print('strong_cycle_viewers', len(found))
    print('no_strong_cycle_viewers', len(missing))


if __name__ == '__main__':
    main()
