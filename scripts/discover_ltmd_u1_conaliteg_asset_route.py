#!/usr/bin/env python3
"""Derive CONALITEG image-route templates from official viewer JavaScript.

Only short normalized route expressions and hashes are retained. No source
images or full third-party JavaScript bodies are committed.
"""
from __future__ import annotations
import csv,hashlib,re
from pathlib import Path
from urllib.request import Request,urlopen

VERSION='LTMD_U1_CONALITEG_ASSET_ROUTE_0.2'
UA='LibroTextoMexicanoDigital/U1 route discovery 0.2'
RESOURCES=[
 ('root-x','https://libros.conaliteg.gob.mx/x.js'),
 ('root-js','https://libros.conaliteg.gob.mx/js.js'),
 ('2022-x','https://libros.conaliteg.gob.mx/2022/x.js'),
 ('2022-js','https://libros.conaliteg.gob.mx/2022/js.js'),
]
OUT=Path('data/catalog/ltmd_u1_conaliteg_asset_route.csv')
REPORT=Path('docs/LTMD_U1_CONALITEG_ASSET_ROUTE.md')
JPG_CONTEXT=re.compile(r'''(?i)[^\n;]{0,260}(?:\.jpg|\.jpeg)[^\n;]{0,260}''')

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:data=r.read(2_000_001)
    if len(data)>2_000_000:raise RuntimeError('JS exceeds 2 MB cap')
    return data

def normalize(expr):
    return re.sub(r'\s+',' ',expr.strip())[:520]

def infer(expr):
    low=expr.lower()
    if 'ag_clave' not in low or '.jpg' not in low:return ''
    if '/c/' in low:return '{base}/c/{ag_clave}/{page}.jpg'
    if 'c/' in low:return '{base}/c/{ag_clave}/{page}.jpg'
    # Preserve a weaker template only when the expression visibly combines the
    # book key and a page/index variable with a JPEG suffix.
    if any(tok in low for tok in ('page','pagina','ag_page')):
        return '{base}/{ag_clave}/{page}.jpg'
    return ''

def main():
    rows=[];lines=['# LTMD-U1 — descubrimiento del patrón de activos CONALITEG','',f'Versión: `{VERSION}`.','',
      'Se inspeccionan temporalmente los módulos oficiales del visor y se retienen únicamente expresiones normalizadas relacionadas con JPEG. No se persiste el código completo ni imágenes.','']
    for label,url in RESOURCES:
        try:
            data=fetch(url);text=data.decode('utf-8','replace');sha=hashlib.sha256(data).hexdigest();contexts=[];error=''
            for m in JPG_CONTEXT.finditer(text):
                expr=normalize(m.group(0));template=infer(expr);contexts.append((expr,template))
            uniq=[];seen=set()
            for expr,t in contexts:
                k=(expr,t)
                if k not in seen:seen.add(k);uniq.append(k)
        except Exception as exc:
            sha='';uniq=[];error=f'{type(exc).__name__}: {exc}'
        lines += [f'## `{label}`','',f'- URL: `{url}`.',f'- SHA-256: `{sha or "—"}`.',f'- Expresiones JPEG observadas: **{len(uniq)}**.',f'- Error: `{error or "ninguno"}`.','']
        for expr,t in uniq:
            rows.append({'route_version':VERSION,'resource_label':label,'resource_url':url,'resource_sha256':sha,'normalized_expression':expr,'route_template':t,'error':error})
            lines.append(f'- expresión: `{expr}`')
            lines.append(f'  - plantilla: `{t or "no_resuelta"}`')
        if not uniq:
            rows.append({'route_version':VERSION,'resource_label':label,'resource_url':url,'resource_sha256':sha,'normalized_expression':'','route_template':'','error':error})
        lines.append('')
    fields=['route_version','resource_label','resource_url','resource_sha256','normalized_expression','route_template','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    templates=sorted({r['route_template'] for r in rows if r['route_template']})
    lines += ['## Plantillas derivadas','']
    for t in templates:lines.append(f'- `{t}`')
    if not templates:lines.append('- Ninguna plantilla suficientemente determinada.')
    lines += ['','## Regla','',
      'Una plantilla derivada sólo habilita un probe de activos oficiales. No demuestra correspondencia con el visor histórico. La equivalencia exige cotejo criptográfico posicional completo de todas las páginas históricas servidas.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
