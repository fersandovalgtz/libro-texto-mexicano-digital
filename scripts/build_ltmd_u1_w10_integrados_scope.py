#!/usr/bin/env python3
"""Freeze the authoritative LTMD-U1 W10 integrated/multiarea cohort from the master queue."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path

QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_w10_scope.csv')
REPORT=Path('docs/LTMD_U1_W10_FREEZE.md')
VERSION='LTMD_U1_W10_INTEGRADOS_SCOPE_0.1'
DOMAIN='integrados_multiarea'
WAVE='U1-W10-integrados_multiarea'
EXPECTED=69
FIELDS=['scope_version','viewer_key','catalog_generation','grade_code','title_core','source_url','operational_domain']

def fail(message:str)->None:
    raise SystemExit(f'W10 scope failed: {message}')

def main()->None:
    queue=list(csv.DictReader(QUEUE.open(encoding='utf-8',newline='')))
    rows=[r for r in queue if r['wave_label']==WAVE and r['operational_domain']==DOMAIN]
    keys=[r['viewer_key'] for r in rows]
    if len(rows)!=EXPECTED:fail(f'expected {EXPECTED} rows, got {len(rows)}')
    if len(set(keys))!=EXPECTED:fail('duplicate viewer keys')
    if any(not r['source_url'] for r in rows):fail('missing source URL in master queue')
    out=[{'scope_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'source_url':r['source_url'],'operational_domain':DOMAIN} for r in rows]
    out.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    canonical='\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')) for r in out)+'\n'
    digest=hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
    generations=Counter(r['catalog_generation'] for r in out)
    grades=Counter(r['grade_code'] for r in out)
    lines=['# LTMD-U1 W10 — alcance congelado Integrados/Multiarea','',f'Versión: `{VERSION}`.','',f'- Identidades congeladas: **{EXPECTED}/{EXPECTED}**.',f'- SHA-256 del snapshot normalizado: `{digest}`.','- Autoridad de origen: `data/catalog/ltmd_u1_wave_queue.csv`.','- Dominio operacional: `integrados_multiarea`.','- Estado semántico: `WAITING_HUMAN_REFERENCE`.','','## Distribución por generación de catálogo']
    for g,n in sorted(generations.items(),key=lambda x:int(x[0])):lines.append(f'- {g}: **{n}** identidades.')
    lines+=['','## Distribución por grado']
    for g,n in sorted(grades.items(),key=lambda x:int(x[0])):lines.append(f'- grado {g}: **{n}** identidades.')
    lines+=['','## Identidades congeladas']
    for r in out:lines.append(f"- `{r['viewer_key']}` — catálogo {r['catalog_generation']}, grado {r['grade_code']} — {r['title_core']}.")
    lines+=['','## Reglas de apertura','','1. La pertenencia a W10 procede exclusivamente de la cola maestra; no se reconstruye a partir del prefijo del identificador ni del título.','2. Ninguna coincidencia de título, grado, generación, cardinalidad, OCR o apariencia visual autoriza un alias.','3. La siguiente fase es estrictamente `source-first`: arquitectura del visor → inventario declarado → auditoría de activos → admisibilidad → topología canónica.','4. No se autoriza OCR, PAGESTRUCT ni FRAGSEG para una identidad hasta que su fuente haya superado la compuerta de admisibilidad correspondiente.','5. Las ausencias, huecos o rutas no servidas se conservan como resultados; no se imputan.','6. W10 no modifica la cobertura técnica efectiva de U1 por el solo hecho de congelar el alcance.','','Este documento fija G0. Cualquier cambio posterior del universo W10 requiere una nueva versión explícita del alcance y justificación documental.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':
    main()
