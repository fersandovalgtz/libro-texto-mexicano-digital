#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_w9_scope.csv')
REPORT=Path('data/catalog/ltmd_u1_w9_scope.md')
VERSION='LTMD_U1_W9_SCOPE_0.1'
DOMAIN='educacion_fisica'
WAVE='U1-W9-educacion_fisica'
EXPECTED=4
EXPECTED_KEYS={'H2008P1ED252','H2008P2ED260','H2008P5ED280','H2008P6ED287'}
FIELDS=['scope_version','viewer_key','catalog_generation','grade_code','title_core','source_url','operational_domain']

def fail(message:str)->None:raise SystemExit(f'W9 scope failed: {message}')

def main()->None:
 rows=[r for r in csv.DictReader(QUEUE.open(encoding='utf-8',newline='')) if r['wave_label']==WAVE and r['queue_status']=='queued' and r['operational_domain']==DOMAIN]
 keys={r['viewer_key'] for r in rows}
 if len(rows)!=EXPECTED:fail(f'expected {EXPECTED} rows, got {len(rows)}')
 if len(keys)!=EXPECTED:fail('duplicate viewer keys')
 if keys!=EXPECTED_KEYS:fail(f'cohort drift: missing={sorted(EXPECTED_KEYS-keys)} unexpected={sorted(keys-EXPECTED_KEYS)}')
 out=[{'scope_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'source_url':r['source_url'],'operational_domain':DOMAIN} for r in rows]
 out.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
 grades=', '.join(str(r['grade_code']) for r in out)
 lines=['# LTMD-U1 W9 — alcance congelado Educación Física','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED}**.',f'- Generación de catálogo: **2008**.','- Grados representados: **'+grades+'**.','- Autoridad: `data/catalog/ltmd_u1_wave_queue.csv`.','- Cohorte protegida además por un conjunto explícito de cuatro `viewer_key` para detectar drift.','','## Identidades']
 for r in out:lines.append(f"- `{r['viewer_key']}` — grado {r['grade_code']} — {r['title_core']}.")
 lines+=['','El dominio `educacion_fisica` es operacional y procede de la cola maestra. El prefijo o forma del identificador no se reinterpreta semánticamente.','','Las cuatro identidades permanecen independientes. No se infiere ningún alias por título, grado, generación, cardinalidad, OCR o similitud visual.','','W9 se abre con estrategia **source-first**. Este alcance no autoriza OCR; primero deben cerrarse arquitectura, inventario declarado, activos fuente y admisibilidad.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
