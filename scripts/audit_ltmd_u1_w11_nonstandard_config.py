#!/usr/bin/env python3
"""Check whether W11 nonstandard viewers still have official claves.json configuration."""
from __future__ import annotations
import csv,json
from pathlib import Path
from urllib.request import Request,urlopen

ROUTING=Path('data/catalog/ltmd_u1_w11_technical_routing.csv')
OUT=Path('data/catalog/ltmd_u1_w11_nonstandard_config.csv')
REPORT=Path('docs/LTMD_U1_W11_NONSTANDARD_CONFIG.md')
ROUTING_VERSION='LTMD_U1_W11_TECHNICAL_ROUTING_0.1'
VERSION='LTMD_U1_W11_NONSTANDARD_CONFIG_0.1'
EXPECTED_TOTAL=111
EXPECTED_NONSTANDARD=11
UA='LibroTextoMexicanoDigital/U1-W11 nonstandard config audit 0.1'

def main()->None:
    routing=list(csv.DictReader(ROUTING.open(encoding='utf-8',newline='')))
    if len(routing)!=EXPECTED_TOTAL or len({r['viewer_key'] for r in routing})!=EXPECTED_TOTAL:raise SystemExit('W11 nonstandard config routing cardinality drift')
    if {r['routing_version'] for r in routing}!={ROUTING_VERSION}:raise SystemExit('W11 nonstandard config routing version drift')
    cohort=[r for r in routing if r['technical_route']=='nonstandard_html_diagnostics']
    if len(cohort)!=EXPECTED_NONSTANDARD:raise SystemExit(f'expected {EXPECTED_NONSTANDARD} nonstandard viewers, got {len(cohort)}')
    with urlopen(Request('https://historico.conaliteg.gob.mx/claves.json',headers={'User-Agent':UA}),timeout=60) as r:cfg=json.loads(r.read().decode('utf-8-sig'))
    rows=[]
    for r in cohort:
        d=cfg.get(r['viewer_key']);entry=int(isinstance(d,dict));ag='';pages='';ready=0
        if entry:
            ag=str(d.get('ag_clave','')).strip();raw=d.get('ag_pages')
            try:pages=int(raw)
            except Exception:pages=''
            ready=int(bool(ag) and isinstance(pages,int) and pages>0)
        rows.append({'config_audit_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'config_entry_present':entry,'ag_clave':ag,'ag_pages':pages,'official_config_ready':ready,'source_url':r['source_url']})
    rows.sort(key=lambda r:(int(r['catalog_generation']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    present=sum(int(r['config_entry_present']) for r in rows);ready=sum(int(r['official_config_ready']) for r in rows);positions=sum(int(r['ag_pages']) for r in rows if r['official_config_ready']=='1' or r['official_config_ready']==1)
    lines=['# LTMD-U1 W11 — configuración oficial de visores no estándar','',f'Versión: `{VERSION}`.','',f'- Visores auditados: **{len(rows)}/{EXPECTED_NONSTANDARD}**.',f'- Entradas presentes en `claves.json`: **{present}/{EXPECTED_NONSTANDARD}**.',f'- Configuraciones con `ag_clave` + `ag_pages` válidos: **{ready}/{EXPECTED_NONSTANDARD}**.',f'- Posiciones declaradas recuperables por configuración oficial: **{positions:,}**.','','## Por visor','','| viewer | config | ready | ag_pages | ag_clave |','|---|---:|---:|---:|---|']
    for r in rows:lines.append(f"| `{r['viewer_key']}` | {r['config_entry_present']} | {r['official_config_ready']} | {r['ag_pages'] or ''} | `{r['ag_clave']}` |")
    lines+=['','## Regla','La presencia en `claves.json` es evidencia de configuración declarada, no prueba de que los activos estén servidos. Si una configuración resulta válida, se habilita exclusivamente una auditoría de activos posición por posición. Si no existe o es incompleta, el visor permanece en diagnóstico no estándar sin imputación.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
