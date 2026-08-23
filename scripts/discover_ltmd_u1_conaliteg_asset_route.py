#!/usr/bin/env python3
"""Derive CONALITEG image-route templates from official viewer JavaScript.

Only short normalized route expressions and hashes are retained. No source
images or full third-party JavaScript bodies are committed.
"""
from __future__ import annotations
import csv,hashlib,re
from pathlib import Path
from urllib.request import Request,urlopen

VERSION='LTMD_U1_CONALITEG_ASSET_ROUTE_0.1'
UA='LibroTextoMexicanoDigital/U1 route discovery 0.1'
RESOURCES=[
 ('root','https://libros.conaliteg.gob.mx/x.js'),
 ('2022','https://libros.conaliteg.gob.mx/2022/x.js'),
]
OUT=Path('data/catalog/ltmd_u1_conaliteg_asset_route.csv')
REPORT=Path('docs/LTMD_U1_CONALITEG_ASSET_ROUTE.md')
JPG_CONTEXT=re.compile(r'''(?i)[^\n;]{0,220}(?:\.jpg|\.jpeg)[^\n;]{0,220}''')

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:data=r.read(2_000_001)
    if len(data)>2_000_000:raise RuntimeError('JS exceeds 2 MB cap')
    return data

def normalize(expr):
    x=re.sub(r'\s+',' ',expr.strip())
    # Keep only route-relevant lexical information; remove unrelated function code.
    return x[:440]

def infer(expr):
    low=expr.lower()
    if 'ag_clave' not in low or '.jpg' not in low:return ''
    prefix='/c/' if '/c/' in low else ('c/' if 'c/' in low else '')
    if not prefix:return ''
    # The viewer uses a page/index variable concatenated with ag_clave. Preserve
    # a symbolic template rather than attempting to execute third-party code.
    return '{base}'+('/c/' if '/c/' in low else 'c/')+'{ag_clave}/{page}.jpg'

def main():
    rows=[];lines=['# LTMD-U1 — descubrimiento del patrón de activos CONALITEG','',f'Versión: `{VERSION}`.','',
      'Se inspeccionan temporalmente los JavaScript oficiales y se retienen únicamente expresiones normalizadas relacionadas con JPEG. No se persiste el código completo ni imágenes.','']
    for label,url in RESOURCES:
        data=fetch(url);text=data.decode('utf-8','replace');sha=hashlib.sha256(data).hexdigest();contexts=[]
        for m in JPG_CONTEXT.finditer(text):
            expr=normalize(m.group(0));template=infer(expr)
            if template or 'ag_clave' in expr.lower():contexts.append((expr,template))
        uniq=[];seen=set()
        for expr,t in contexts:
            k=(expr,t)
            if k not in seen:seen.add(k);uniq.append(k)
        lines += [f'## `{label}`','',f'- URL: `{url}`.',f'- SHA-256: `{sha}`.',f'- Expresiones JPEG relevantes: **{len(uniq)}**.','']
        for expr,t in uniq:
            rows.append({'route_version':VERSION,'resource_label':label,'resource_url':url,'resource_sha256':sha,'normalized_expression':expr,'route_template':t})
            lines.append(f'- plantilla: `{t or "no_resuelta"}`')
        lines.append('')
    fields=['route_version','resource_label','resource_url','resource_sha256','normalized_expression','route_template']
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
