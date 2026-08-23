#!/usr/bin/env python3
"""Audit official CONALITEG viewer configuration for isolated U1 holes.

The audit extracts only configuration metadata from official JS and reconciles
it with already-published W11 asset manifests. It does not download/persist
source images and does not assert identity between editions.
"""
from __future__ import annotations
import csv,hashlib,re
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen

OUT=Path('data/catalog/ltmd_u1_official_representation_config.csv')
REPORT=Path('docs/LTMD_U1_OFFICIAL_REPRESENTATION_CONFIG.md')
VERSION='LTMD_U1_OFFICIAL_REPRESENTATION_CONFIG_0.1'
UA='LibroTextoMexicanoDigital/U1 official-config audit 0.1'
CASES=[
 {'wave':'W11','viewer_key':'H2014P3COL','hole_page':'130','official_code':'P3COL','config_url':'https://libros.conaliteg.gob.mx/2022/x.js'},
 {'wave':'W11','viewer_key':'H2014P3MOR','hole_page':'15','official_code':'P3MOR','config_url':'https://libros.conaliteg.gob.mx/x.js'},
]
MANIFESTS=[
 Path('data/catalog/ltmd_u1_w11_standard_asset_manifest.csv'),
 Path('data/catalog/ltmd_u1_w11_nonstandard_asset_manifest.csv'),
]
ASSIGN_RE=re.compile(r'''(?m)\b([A-Za-z_$][A-Za-z0-9_$]{0,60})\s*=\s*(?:["']([^"']{0,300})["']|([0-9]{1,7}))\s*;?''')
PATH_RE=re.compile(r'''(?i)(?:["'])([^"']*(?:\.jpg|\.jpeg|/c/|pages?|clave|book)[^"']*)(?:["'])''')

def fetch(url:str)->bytes:
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:
        return r.read(2_000_001)

def load_manifest_rows(viewer:str):
    rows=[]
    for p in MANIFESTS:
        if not p.exists():continue
        with p.open(encoding='utf-8',newline='') as f:
            for r in csv.DictReader(f):
                if r.get('viewer_key')==viewer:
                    rr=dict(r);rr['_manifest']=p.name;rows.append(rr)
    return rows

def first_int(rows,keys):
    for r in rows:
        for k in keys:
            v=(r.get(k) or '').strip()
            if v.isdigit():return int(v)
    return None

def main():
    out=[];lines=['# LTMD-U1 — configuración de representaciones oficiales candidatas','',f'Versión: `{VERSION}`.','',
        'Se extraen metadatos de configuración desde JavaScript oficial de CONALITEG y se contrastan con los manifiestos W11 ya publicados. No se declara equivalencia documental ni se persisten imágenes.','']
    for case in CASES:
        mrows=load_manifest_rows(case['viewer_key'])
        manifest_names=sorted({r['_manifest'] for r in mrows})
        statuses=Counter((r.get('asset_status') or r.get('status') or '').strip() for r in mrows)
        indexes=[]
        for r in mrows:
            v=(r.get('source_image_index') or r.get('source_index') or '').strip()
            if v.isdigit():indexes.append(int(v))
        try:
            data=fetch(case['config_url'])
            if len(data)>2_000_000:raise RuntimeError('config exceeds 2 MB')
            text=data.decode('utf-8','replace')
            assignments=[]
            for name,sval,nval in ASSIGN_RE.findall(text):
                val=sval or nval
                lname=name.lower()
                if any(tok in lname for tok in ('clave','page','pag','book','libro','folder','carp','path','ruta','dir','total','max')) or case['official_code'].lower() in val.lower():
                    assignments.append((name,val))
            paths=sorted(set(x.strip() for x in PATH_RE.findall(text) if x.strip()))
            sha=hashlib.sha256(data).hexdigest();error=''
        except Exception as exc:
            assignments=[];paths=[];sha='';error=f'{type(exc).__name__}: {exc}'
        seen=set()
        for name,val in assignments:
            key=(name,val)
            if key in seen:continue
            seen.add(key)
            out.append({**case,'config_sha256':sha,'config_key':name,'config_value':val,'historical_manifest':';'.join(manifest_names),'historical_rows':len(mrows),'historical_index_min':min(indexes) if indexes else '','historical_index_max':max(indexes) if indexes else '','error':error})
        if not assignments:
            out.append({**case,'config_sha256':sha,'config_key':'','config_value':'','historical_manifest':';'.join(manifest_names),'historical_rows':len(mrows),'historical_index_min':min(indexes) if indexes else '','historical_index_max':max(indexes) if indexes else '','error':error})
        lines += [f"## `{case['viewer_key']}` / `{case['official_code']}`",'',
                  f"- Configuración oficial: `{case['config_url']}`.",
                  f"- SHA-256 del JS: `{sha or '—'}`.",
                  f"- Filas históricas W11 localizadas: **{len(mrows)}**.",
                  f"- Manifiestos: `{', '.join(manifest_names) if manifest_names else 'ninguno'}`.",
                  f"- Rango de índices históricos observado: **{min(indexes) if indexes else '—'}–{max(indexes) if indexes else '—'}**.",
                  f"- Asignaciones técnicas relevantes: **{len(seen)}**.",
                  f"- Strings de ruta/configuración detectados: **{len(paths)}**.",'']
        if seen:
            lines.append('Asignaciones relevantes:')
            for name,val in sorted(seen)[:40]:lines.append(f'- `{name} = {val}`')
            lines.append('')
        if paths:
            lines.append('Patrones/string de arquitectura:')
            for p in paths[:30]:lines.append(f'- `{p}`')
            lines.append('')
        if statuses:
            lines.append('Estados históricos observados:')
            for k,n in sorted(statuses.items()):lines.append(f'- `{k or "(vacío)"}`: **{n}**.')
            lines.append('')
        if error:lines += [f'Error: `{error}`','']
    fields=['wave','viewer_key','hole_page','official_code','config_url','config_sha256','config_key','config_value','historical_manifest','historical_rows','historical_index_min','historical_index_max','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    lines += ['## Criterio para la siguiente compuerta','',
      'Sólo si la configuración oficial permite construir una secuencia de activos con cardinalidad compatible se habilitará una comparación criptográfica temporal. Esa comparación deberá demostrar correspondencia posicional en todas las posiciones históricas servidas; una coincidencia parcial o nominal no recupera el hueco.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
