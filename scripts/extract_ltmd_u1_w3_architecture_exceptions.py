#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path
SRC=Path('data/catalog/ltmd_u1_w3_viewer_architecture.csv');OUT=Path('data/catalog/ltmd_u1_w3_architecture_exceptions.csv');REPORT=Path('data/catalog/ltmd_u1_w3_architecture_exceptions.md');VERSION='LTMD_U1_W3_ARCH_EXCEPTIONS_0.1';EXPECTED=4

def main():
 rows=list(csv.DictReader(SRC.open(encoding='utf-8',newline='')));bad=[r for r in rows if r['standard_dynamic_architecture']!='1']
 if len(bad)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} W3 architecture exceptions, got {len(bad)}')
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(bad[0]));w.writeheader();w.writerows(bad)
 lines=['# LTMD-U1 W3 — excepciones de arquitectura','',f'Versión: `{VERSION}`.','',f'- Excepciones: **{len(bad)}**.','']
 for r in bad:lines.append(f"- `{r['viewer_key']}` — generación {r['catalog_generation']}, grado {r['grade_code']}, `{r['title_core']}`; HTML={r['html_status']}, x.js={r['x_js_status']}, ag_pages={r['ag_pages_signal']}.")
 lines+=['','Estas excepciones se aíslan antes de la auditoría de activos. No se infiere ausencia de libro, página ni contenido a partir de una arquitectura no estándar.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
