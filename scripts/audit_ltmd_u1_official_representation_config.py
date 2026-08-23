#!/usr/bin/env python3
"""Audit official CONALITEG viewer configuration for isolated U1 holes.

Only configuration metadata are retained. The audit reads official HTML/JS,
reconciles it with published W11 manifests, and derives candidate configuration
endpoints without persisting source images or asserting edition identity.
"""
from __future__ import annotations
import csv,hashlib,re
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen

OUT=Path('data/catalog/ltmd_u1_official_representation_config.csv')
REPORT=Path('docs/LTMD_U1_OFFICIAL_REPRESENTATION_CONFIG.md')
VERSION='LTMD_U1_OFFICIAL_REPRESENTATION_CONFIG_0.2'
UA='LibroTextoMexicanoDigital/U1 official-config audit 0.2'
CASES=[
 {'wave':'W11','viewer_key':'H2014P3COL','hole_page':'130','official_code':'P3COL','entry_url':'https://libros.conaliteg.gob.mx/P3COL.htm','config_url':'https://libros.conaliteg.gob.mx/2022/x.js','hash_url':'https://libros.conaliteg.gob.mx/2022/hash.js'},
 {'wave':'W11','viewer_key':'H2014P3MOR','hole_page':'15','official_code':'P3MOR','entry_url':'https://libros.conaliteg.gob.mx/P3MOR.htm','config_url':'https://libros.conaliteg.gob.mx/x.js','hash_url':'https://libros.conaliteg.gob.mx/hash.js'},
]
MANIFESTS=[Path('data/catalog/ltmd_u1_w11_standard_asset_manifest.csv'),Path('data/catalog/ltmd_u1_w11_nonstandard_asset_manifest.csv')]
ASSIGN_RE=re.compile(r'''(?m)\b([A-Za-z_$][A-Za-z0-9_$]{0,60})\s*=\s*(?:["']([^"']{0,300})["']|([0-9]{1,7}))\s*;?''')
FETCH_RE=re.compile(r'''fetch\s*\(\s*([^\)\n]{1,220})\)''',re.I)
CLAVES_EXPR_RE=re.compile(r'''(?m)\bclavesUrl\s*=\s*([^;\n]{1,300})''',re.I)
STRING_RE=re.compile(r'''["']([^"']{1,240})["']''')

def fetch(url:str,limit:int=2_000_000):
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:
        data=r.read(limit+1);final=r.geturl();status=int(getattr(r,'status',200) or 200);ctype=r.headers.get('Content-Type','')
    if len(data)>limit:raise RuntimeError(f'resource exceeds {limit} bytes: {url}')
    return status,final,ctype,data

def load_manifest_rows(viewer:str):
    rows=[]
    for p in MANIFESTS:
        if not p.exists():continue
        with p.open(encoding='utf-8',newline='') as f:
            for r in csv.DictReader(f):
                if r.get('viewer_key')==viewer:
                    rr=dict(r);rr['_manifest']=p.name;rows.append(rr)
    return rows

def compact(expr:str)->str:
    return re.sub(r'\s+',' ',expr.strip())[:220]

def candidate_strings(text:str):
    vals=set()
    for s in STRING_RE.findall(text):
        low=s.lower()
        if any(tok in low for tok in ('.json','clave','config','catalog','2022/','2019/')) and len(s)<=240:
            vals.add(s.strip())
    return sorted(vals)

def main():
    out=[];lines=['# LTMD-U1 — configuración de representaciones oficiales candidatas','',f'Versión: `{VERSION}`.','',
      'Se extraen únicamente metadatos de configuración desde recursos oficiales CONALITEG y se contrastan con los manifiestos W11. No se declara equivalencia documental ni se persisten imágenes fuente.','']
    for case in CASES:
        mrows=load_manifest_rows(case['viewer_key']);manifest_names=sorted({r['_manifest'] for r in mrows});statuses=Counter((r.get('asset_status') or r.get('status') or '').strip() for r in mrows)
        indexes=[]
        for r in mrows:
            v=(r.get('source_image_index') or r.get('source_index') or '').strip()
            if v.isdigit():indexes.append(int(v))
        resources=[];errors=[]
        for role,url in [('entry_html',case['entry_url']),('x_js',case['config_url']),('hash_js',case['hash_url'])]:
            try:
                status,final,ctype,data=fetch(url);text=data.decode('utf-8','replace')
                resources.append({'role':role,'requested':url,'final':final,'status':status,'ctype':ctype,'sha256':hashlib.sha256(data).hexdigest(),'text':text})
            except Exception as exc:errors.append(f'{role}: {type(exc).__name__}: {exc}')
        assignments=[];fetch_expr=[];claves_expr=[];strings=[]
        for res in resources:
            text=res['text']
            for name,sval,nval in ASSIGN_RE.findall(text):
                val=sval or nval;lname=name.lower()
                if any(tok in lname for tok in ('clave','page','pag','book','libro','folder','carp','path','ruta','dir','total','max')) or case['official_code'].lower() in val.lower():
                    assignments.append((res['role'],name,val))
            fetch_expr += [(res['role'],compact(x)) for x in FETCH_RE.findall(text)]
            claves_expr += [(res['role'],compact(x)) for x in CLAVES_EXPR_RE.findall(text)]
            strings += [(res['role'],s) for s in candidate_strings(text)]
        evidence=[]
        for role,name,val in assignments:evidence.append((role,f'assignment:{name}',val))
        for role,val in fetch_expr:evidence.append((role,'fetch_expression',val))
        for role,val in claves_expr:evidence.append((role,'clavesUrl_expression',val))
        for role,val in strings:evidence.append((role,'candidate_string',val))
        seen=[];seen_keys=set()
        for x in evidence:
            if x not in seen_keys:seen_keys.add(x);seen.append(x)
        primary_sha=next((r['sha256'] for r in resources if r['role']=='x_js'),'')
        if not seen:seen=[('','','')]
        for role,key,val in seen:
            out.append({**case,'config_sha256':primary_sha,'evidence_resource':role,'config_key':key,'config_value':val,'historical_manifest':';'.join(manifest_names),'historical_rows':len(mrows),'historical_index_min':min(indexes) if indexes else '','historical_index_max':max(indexes) if indexes else '','error':' | '.join(errors)})
        lines += [f"## `{case['viewer_key']}` / `{case['official_code']}`",'',
          f"- Filas históricas W11: **{len(mrows)}**; rango índice **{min(indexes) if indexes else '—'}–{max(indexes) if indexes else '—'}**.",
          f"- Recursos oficiales textuales recuperados: **{len(resources)}/3**.",
          f"- Evidencias técnicas extraídas: **{len([x for x in seen if x != ('','','')])}**.",'']
        for res in resources:lines.append(f"- `{res['role']}` → `{res['final']}` · HTTP {res['status']} · SHA-256 `{res['sha256']}`")
        lines.append('')
        if fetch_expr:
            lines.append('Expresiones `fetch` observadas:')
            for role,val in sorted(set(fetch_expr)):lines.append(f'- `{role}`: `{val}`')
            lines.append('')
        if claves_expr:
            lines.append('Construcción de `clavesUrl`:')
            for role,val in sorted(set(claves_expr)):lines.append(f'- `{role}`: `{val}`')
            lines.append('')
        config_strings=sorted(set(strings))
        if config_strings:
            lines.append('Cadenas candidatas de configuración:')
            for role,val in config_strings[:40]:lines.append(f'- `{role}`: `{val}`')
            lines.append('')
        if statuses:
            lines.append('Estados históricos observados:')
            for k,n in sorted(statuses.items()):lines.append(f'- `{k or "(vacío)"}`: **{n}**.')
            lines.append('')
        if errors:
            lines.append('Errores:');lines += [f'- `{e}`' for e in errors];lines.append('')
    fields=['wave','viewer_key','hole_page','official_code','entry_url','config_url','hash_url','config_sha256','evidence_resource','config_key','config_value','historical_manifest','historical_rows','historical_index_min','historical_index_max','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    lines += ['## Criterio para la siguiente compuerta','',
      'Sólo si estos metadatos permiten resolver un endpoint oficial de configuración y una secuencia con cardinalidad compatible se habilita comparación criptográfica temporal. Todas las posiciones históricas servidas deben concordar; coincidencia parcial, título, grado o clave corta no recuperan el hueco.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
