#!/usr/bin/env python3
"""Capture routing evidence for unresolved LTMD-U1 W7 viewers.

Only HTML and same-origin JavaScript are retrieved. Image assets are never
fetched by this diagnostic. The output records hashes, sizes, script URLs and
small route-relevant snippets so routing changes can be audited over time.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

INVENTORY = Path('data/catalog/ltmd_u1_w7_declared_inventory.csv')
SUMMARY = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_summary.csv')
OUT_JSON = Path('data/catalog/ltmd_u1_w7_routing_diagnostics.json')
OUT_MD = Path('data/catalog/ltmd_u1_w7_routing_diagnostics.md')
VERSION = 'LTMD_U1_W7_ROUTING_DIAGNOSTICS_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W7 routing diagnostics'
KEYWORDS = ('.jpg', '.jpeg', '/c/', 'ag_clave', 'clave', 'pagina', 'page', 'image', 'imagen')


class ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != 'script':
            return
        attr_map = dict(attrs)
        src = attr_map.get('src')
        if src:
            self.scripts.append(src)


def fetch_text(url: str, attempts: int = 3) -> dict[str, object]:
    last_error = ''
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/javascript,text/javascript,*/*;q=0.1'})
            with urlopen(req, timeout=45) as response:
                body = response.read()
                status = int(getattr(response, 'status', 200))
                content_type = response.headers.get('Content-Type', '')
                charset = response.headers.get_content_charset()
            encoding_candidates = [charset, 'utf-8', 'latin-1']
            text = None
            used_encoding = ''
            for encoding in encoding_candidates:
                if not encoding:
                    continue
                try:
                    text = body.decode(encoding)
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            if text is None:
                text = body.decode('utf-8', errors='replace')
                used_encoding = 'utf-8-replace'
            return {
                'url': url,
                'status': status,
                'content_type': content_type,
                'byte_size': len(body),
                'sha256': hashlib.sha256(body).hexdigest(),
                'encoding': used_encoding,
                'attempts': attempt,
                'error': '',
                'text': text,
            }
        except HTTPError as exc:
            last_error = f'HTTPError {exc.code}'
        except (URLError, TimeoutError, OSError) as exc:
            last_error = f'{type(exc).__name__}: {exc}'
        if attempt < attempts:
            time.sleep(attempt)
    return {
        'url': url,
        'status': None,
        'content_type': '',
        'byte_size': 0,
        'sha256': '',
        'encoding': '',
        'attempts': attempts,
        'error': last_error,
        'text': '',
    }


def compact_snippet(line: str, limit: int = 420) -> str:
    cleaned = re.sub(r'\s+', ' ', line).strip()
    return cleaned[:limit]


def evidence_from_text(source_url: str, text: str) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for line_no, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        hits = [keyword for keyword in KEYWORDS if keyword in lower]
        if not hits:
            continue
        snippet = compact_snippet(line)
        if not snippet:
            continue
        key = hashlib.sha256(snippet.encode('utf-8')).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        evidence.append({
            'source_url': source_url,
            'line': str(line_no),
            'keywords': ','.join(hits),
            'snippet_sha256': key,
            'snippet': snippet,
        })
        if len(evidence) >= 120:
            break
    return evidence


def serializable_fetch(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key != 'text'}


def main() -> None:
    inventory_rows = list(csv.DictReader(INVENTORY.open(encoding='utf-8', newline='')))
    summary_rows = list(csv.DictReader(SUMMARY.open(encoding='utf-8', newline='')))
    inventory = {row['viewer_key']: row for row in inventory_rows}
    unresolved = [row for row in summary_rows if row['direct_asset_ready'] != '1']
    if not unresolved:
        raise SystemExit('W7 routing diagnostics expected at least one unresolved viewer')

    results: list[dict[str, object]] = []
    for summary in unresolved:
        key = summary['viewer_key']
        inv = inventory[key]
        page = fetch_text(inv['source_url'])
        page_text = str(page.get('text', ''))
        parser = ScriptParser()
        try:
            parser.feed(page_text)
        except Exception as exc:
            parser.scripts = []
            parse_error = f'{type(exc).__name__}: {exc}'
        else:
            parse_error = ''

        origin = urlparse(inv['source_url']).netloc.lower()
        script_urls: list[str] = []
        for src in parser.scripts:
            resolved = urljoin(inv['source_url'], src)
            if urlparse(resolved).netloc.lower() == origin and resolved not in script_urls:
                script_urls.append(resolved)

        evidence = evidence_from_text(inv['source_url'], page_text)
        scripts: list[dict[str, object]] = []
        for script_url in script_urls[:40]:
            script = fetch_text(script_url)
            script_text = str(script.get('text', ''))
            evidence.extend(evidence_from_text(script_url, script_text))
            scripts.append(serializable_fetch(script))

        results.append({
            'diagnostic_version': VERSION,
            'viewer_key': key,
            'catalog_generation': inv['catalog_generation'],
            'grade_code': inv['grade_code'],
            'title_core': inv['title_core'],
            'source_url': inv['source_url'],
            'declared_positions': int(inv['declared_positions']),
            'asset_audit_internal_unserved': int(summary['internal_unserved']),
            'asset_audit_source_jpegs': int(summary['source_jpegs']),
            'html': serializable_fetch(page),
            'html_parse_error': parse_error,
            'same_origin_scripts_declared': len(script_urls),
            'scripts': scripts,
            'route_evidence': evidence[:250],
        })

    payload = {
        'diagnostic_version': VERSION,
        'scope': 'LTMD-U1 W7 unresolved Civics/Ethics viewers only',
        'policy': 'HTML and same-origin JavaScript only; no image bytes fetched or persisted.',
        'viewer_count': len(results),
        'viewers': results,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# LTMD-U1 W7 — diagnóstico de routing de visores no resueltos',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Este diagnóstico inspecciona únicamente HTML y JavaScript del mismo origen. No descarga ni conserva imágenes del libro.',
        '',
        f'- Visores no resueltos inspeccionados: **{len(results)}**.',
        '',
        '| visor | generación | grado | HTML | scripts mismo origen | evidencias de ruta | huecos internos previos |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for item in results:
        html_status = item['html']['status'] if isinstance(item['html'], dict) else ''
        lines.append(
            f"| `{item['viewer_key']}` | {item['catalog_generation']} | {item['grade_code']} | "
            f"{html_status} | {len(item['scripts'])} | {len(item['route_evidence'])} | {item['asset_audit_internal_unserved']} |"
        )
    lines += [
        '',
        '## Interpretación',
        '',
        'El archivo JSON conserva hashes y tamaños del HTML/JavaScript consultado junto con fragmentos mínimos que contienen indicadores de routing. Cualquier ruta alternativa deberá derivarse de esa evidencia antes de volver a sondear activos; no se autoriza inferir aliases por coincidencia de año, grado, título o cardinalidad.',
    ]
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
