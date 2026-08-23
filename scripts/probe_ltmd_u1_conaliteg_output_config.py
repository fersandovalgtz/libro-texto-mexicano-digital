#!/usr/bin/env python3
"""Extract only P3COL/P3MOR configuration from CONALITEG output.json.

The complete remote configuration is never committed. Only target records,
source hash, structural location, and scalar metadata are retained.
"""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen

URL='https://libros.conaliteg.gob.mx/output.json'
TARGETS={'P3COL','P3MOR'}
VERSION='LTMD_U1_CONALITEG_OUTPUT_CONFIG_0.1'
UA='LibroTextoMexicanoDigital/U1 output-config probe 0.1'
OUT=Path('data/catalog/ltmd_u1_conaliteg_output_config.csv')
REPORT=Path('docs/LTMD_U1_CONALITEG_OUTPUT_CONFIG.md')

def fetch():
    with urlopen(Request(URL,headers={'User-Agent':UA}),timeout=60) as r:
        data=r.read(30_000_001);status=int(getattr(r,'status',200) or 200);ctype=r.headers.get('Content-Type','')
    if len(data)>30_000_000:raise RuntimeError('output.json exceeds 30 MB safety cap')
    return status,ctype,data

def scalars(obj):
    if not isinstance(obj,dict):return {}
    out={}
    for k,v in obj.items():
        if isinstance(v,(str,int,float,bool)) or v is None:out[str(k)]=v
    return out

def walk(obj,path=()):
    if isinstance(obj,dict):
        for k,v in obj.items():
            yield from walk(v,path+(str(k),))
            if str(k).upper() in TARGETS:
                yield ('key',str(k).upper(),path+(str(k),),v)
            if isinstance(v,str) and v.upper() in TARGETS:
                yield ('value',v.upper(),path+(str(k),),obj)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from walk(v,path+(str(i),))

def main():
    status,ctype,data=fetch();sha=hashlib.sha256(data).hexdigest();root=json.loads(data.decode('utf-8'))
    found={t:[] for t in TARGETS}
    for mode,target,path,obj in walk(root):
        found[target].append((mode,path,obj))
    rows=[];lines=['# LTMD-U1 — configuración selectiva desde CONALITEG `output.json`','',f'Versión: `{VERSION}`.','',
        f'- Fuente: `{URL}`.',f'- HTTP: **{status}**.',f'- Content-Type: `{ctype}`.',f'- SHA-256 del objeto remoto: `{sha}`.',f'- Bytes inspeccionados temporalmente: **{len(data):,}**.','- Copia íntegra persistida: **0**.','']
    for target in sorted(TARGETS):
        matches=found[target];lines += [f'## `{target}`','',f'- Coincidencias estructurales: **{len(matches)}**.']
        seen=set()
        for mode,path,obj in matches:
            sv=scalars(obj)
            sig=(mode,'/'.join(path),tuple(sorted((k,str(v)) for k,v in sv.items())))
            if sig in seen:continue
            seen.add(sig)
            lines.append(f"- Ubicación: `{'/'.join(path)}` · modo `{mode}`")
            if sv:
                for k,v in sorted(sv.items()):
                    rows.append({'probe_version':VERSION,'target_code':target,'match_mode':mode,'json_path':'/'.join(path),'field':k,'value':v,'source_url':URL,'source_sha256':sha})
                    lines.append(f'  - `{k}` = `{v}`')
            else:
                rows.append({'probe_version':VERSION,'target_code':target,'match_mode':mode,'json_path':'/'.join(path),'field':'','value':'','source_url':URL,'source_sha256':sha})
        lines.append('')
    fields=['probe_version','target_code','match_mode','json_path','field','value','source_url','source_sha256']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    lines += ['## Regla','',
        'Los registros anteriores son metadatos de configuración del visor oficial. No prueban que la representación actual sea byte-idéntica al visor histórico. La siguiente etapa sólo puede usar campos de ruta/cardinalidad para construir un cotejo temporal posición por posición.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
