#!/usr/bin/env python3
"""Snapshot viewer keys exposed by CONALITEG's public historical-catalog JS.

Does not execute remote JavaScript. It fetches bytes, records SHA-256, extracts
viewer-like identifiers with a conservative regex, and summarizes encoded
generation/grade patterns. No book assets are downloaded.
"""
from __future__ import annotations
import csv,hashlib,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

URL='https://historico.conaliteg.gob.mx/libros_2023.js'
UA='LibroTextoMexicanoDigital/0.1 catalog key snapshot'
OUT=Path('data/catalog/conaliteg_historical_viewer_keys.csv')
REPORT=Path('data/catalog/conaliteg_historical_catalog_snapshot.md')
META=Path('data/catalog/conaliteg_historical_catalog_snapshot.csv')
VERSION='CONALITEG_KEY_SNAPSHOT_0.1'
# Keep tail flexible: e.g. CI084, CNA, other subject codes.
KEY=re.compile(r'\b(H(?P<generation>19\d{2}|20\d{2})P(?P<grade>\d{1,2})(?P<tail>[A-Z][A-Z0-9_-]{1,20}))\b',re.I)

def main():
    with urlopen(Request(URL,headers={'User-Agent':UA}),timeout=45) as r:
        raw=r.read();status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','')
    text=raw.decode('utf-8',errors='replace');sha=hashlib.sha256(raw).hexdigest()
    found={}
    for m in KEY.finditer(text):
        key=m.group(1).upper();found.setdefault(key,{'snapshot_version':VERSION,'viewer_key':key,'catalog_generation':m.group('generation'),'grade_code':m.group('grade'),'tail_code':m.group('tail').upper(),'occurrences':0});found[key]['occurrences']+=1
    rows=sorted(found.values(),key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    if not rows:raise SystemExit('no viewer keys parsed; refusing empty snapshot')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    gens=Counter(r['catalog_generation'] for r in rows);grades=Counter(r['grade_code'] for r in rows)
    generated=datetime.now(timezone.utc).isoformat()
    meta={'snapshot_version':VERSION,'source_url':URL,'fetched_utc':generated,'http_status':status,'content_type':ctype,'source_bytes':len(raw),'source_sha256':sha,'unique_viewer_keys':len(rows),'generation_count':len(gens),'grade_code_count':len(grades)}
    with META.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(meta));w.writeheader();w.writerow(meta)
    lines=['# Snapshot de claves del Catálogo Histórico CONALITEG','',f'Versión: `{VERSION}`.','',f'- Archivo fuente: `libros_2023.js`.\n- Bytes: **{len(raw):,}**.\n- SHA-256: `{sha}`.\n- Claves de visor únicas detectadas: **{len(rows):,}**.\n- Generaciones codificadas: **{len(gens)}**.\n- Códigos de grado detectados: **{len(grades)}**.','', '## Claves por generación']
    for g,n in sorted(gens.items(),key=lambda x:int(x[0])):lines.append(f'- {g}: **{n}**.')
    lines+=['','## Claves por código de grado']
    for g,n in sorted(grades.items(),key=lambda x:int(x[0])):lines.append(f'- grado `{g}`: **{n}**.')
    lines+=['','## Alcance','La extracción registra claves visibles en el JavaScript público sin ejecutar ese código. Una clave no equivale todavía a un objeto bibliográfico validado; título, asignatura, edición y disponibilidad se auditan después a nivel de visor.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
