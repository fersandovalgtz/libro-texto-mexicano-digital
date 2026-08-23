#!/usr/bin/env python3
"""Profile documentary heterogeneity in frozen LTMD-U1 W11 without semantic reclassification."""
from __future__ import annotations
import csv, re, unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

SCOPE=Path('data/catalog/ltmd_u1_w11_scope.csv')
OUT=Path('data/catalog/ltmd_u1_w11_heterogeneity.csv')
REPORT=Path('docs/LTMD_U1_W11_HETEROGENEITY.md')
SCOPE_VERSION='LTMD_U1_W11_OTROS_SCOPE_0.1'
VERSION='LTMD_U1_W11_HETEROGENEITY_0.2'
EXPECTED=111
SIGNALS=[
    'generic_grade_book','recortable','libro_integrado','monografia_estatal',
    'constitucion_literal','educacion_fisica_literal','entidad_donde_vivo',
    'material_alfabetizacion','fichero_didactico','conocimiento_medio',
    'matematicas_literal'
]
FIELDS=['profile_version','scope_version','viewer_key','catalog_generation','grade_code','title_core','source_host','source_path_shape',*SIGNALS,'signal_signature']

def norm(s:str)->str:
    s=unicodedata.normalize('NFKD',s)
    s=''.join(c for c in s if not unicodedata.combining(c)).upper()
    return re.sub(r'\s+',' ',s).strip()

def flags(title:str)->dict[str,int]:
    t=norm(title)
    return {
        'generic_grade_book': int(bool(re.search(r'^MI (?:CUADERNO DE TRABAJO|LIBRO).*?(?:ANO|1ER|1°|2°|PARTE|SEGUNDO)',t))),
        'recortable': int('RECORTABLE' in t),
        'libro_integrado': int('LIBRO INTEGRADO' in t),
        'monografia_estatal': int(t.startswith('MONOGRAFIA ESTATAL')),
        'constitucion_literal': int('CONSTITU' in t),
        'educacion_fisica_literal': int('EDUCACION FIS' in t),
        'entidad_donde_vivo': int('ENTIDAD DONDE VIVO' in t),
        'material_alfabetizacion': int('MATERIAL DE APOYO A LA ALFABETIZACION' in t),
        'fichero_didactico': int('FICHERO DIDACT' in t),
        'conocimiento_medio': int('CONOCIMIENTO DEL MEDIO' in t),
        # Stemming is intentionally literal/orthographic: it captures catalog spellings such as MATEMAÁTICAS without correcting the source title.
        'matematicas_literal': int('MATEMA' in t),
    }

def path_shape(url:str)->str:
    p=urlparse(url)
    path=p.path
    if re.fullmatch(r'/H[^/]+\.htm',path,re.I):return 'historico_root_viewer_htm'
    if re.fullmatch(r'/[^/]+\.htm',path,re.I):return 'root_htm_other'
    return 'other'

def main()->None:
    if not SCOPE.exists():raise SystemExit(f'missing frozen W11 scope: {SCOPE}')
    rows=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')))
    if len(rows)!=EXPECTED or len({r['viewer_key'] for r in rows})!=EXPECTED:raise SystemExit('W11 heterogeneity scope cardinality failure')
    if {r['scope_version'] for r in rows}!={SCOPE_VERSION}:raise SystemExit('W11 scope version drift')
    out=[]
    for r in rows:
        f=flags(r['title_core']);sig='+'.join(k for k in SIGNALS if f[k]) or 'no_declared_signal'
        u=urlparse(r['source_url'])
        out.append({
            'profile_version':VERSION,'scope_version':r['scope_version'],'viewer_key':r['viewer_key'],
            'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],
            'source_host':u.netloc.lower(),'source_path_shape':path_shape(r['source_url']),**f,'signal_signature':sig
        })
    out.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
    gens=Counter(r['catalog_generation'] for r in out);grades=Counter(r['grade_code'] for r in out)
    hosts=Counter(r['source_host'] for r in out);shapes=Counter(r['source_path_shape'] for r in out)
    signal_counts={s:sum(int(r[s]) for r in out) for s in SIGNALS};sigs=Counter(r['signal_signature'] for r in out)
    no_signal=sum(r['signal_signature']=='no_declared_signal' for r in out)
    multi=sum('+' in r['signal_signature'] for r in out)
    prefix=Counter(re.match(r'^(H\d{4}P\d+)([A-Z]+)',r['viewer_key']).group(2) if re.match(r'^(H\d{4}P\d+)([A-Z]+)',r['viewer_key']) else 'OTHER' for r in out)
    lines=['# LTMD-U1 W11 — perfil de heterogeneidad documental','',f'Versión: `{VERSION}`.','',
           f'- Identidades perfiladas: **{len(out)}/{EXPECTED}**.','- Base: alcance W11 congelado; ninguna fila se agrega ni se elimina.','- Propósito: QA operacional y diseño de ejecución, no reclasificación semántica.','',
           '## Distribución por generación']
    for k,v in sorted(gens.items(),key=lambda x:int(x[0])):lines.append(f'- {k}: **{v}**.')
    lines+=['','## Distribución por grado']
    for k,v in sorted(grades.items(),key=lambda x:int(x[0])):lines.append(f'- grado {k}: **{v}**.')
    lines+=['','## Señales documentales literales/deterministas']
    for s in SIGNALS:lines.append(f'- `{s}`: **{signal_counts[s]}**.')
    lines += ['',f'- Sin ninguna señal declarada: **{no_signal}**.',f'- Con ≥2 señales simultáneas: **{multi}**.','',
              '## Firmas de señales']
    for k,v in sigs.most_common():lines.append(f'- `{k}`: **{v}**.')
    lines+=['','## Patrones técnicos de identificador']
    for k,v in sorted(prefix.items(),key=lambda x:(-x[1],x[0])):lines.append(f'- `{k}`: **{v}**.')
    lines+=['','## Fuente declarada']
    for k,v in hosts.items():lines.append(f'- host `{k}`: **{v}**.')
    for k,v in shapes.items():lines.append(f'- forma de ruta `{k}`: **{v}**.')
    lines+=['','## Interpretación permitida','',
            'Las señales anteriores son coincidencias literales reproducibles en títulos ya congelados o patrones técnicos de identificador/URL. Sirven para medir heterogeneidad y diseñar auditorías. No autorizan a mover identidades entre dominios, inferir asignaturas, fusionar ediciones, crear aliases ni atribuir continuidad curricular.','',
            '`WAITING_HUMAN_REFERENCE` continúa vigente. Cualquier subcohorte posterior deberá justificarse por arquitectura/configuración observada y conservar el universo W11 completo.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
