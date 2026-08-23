#!/usr/bin/env python3
"""Triage preserved U1 technical exceptions by evidence pattern.

The triage does not resolve or reprioritize identities semantically. It groups
exceptions by the technical recovery method their existing evidence supports.
"""
from __future__ import annotations
import csv,re
from collections import Counter,defaultdict
from pathlib import Path

SRC=Path('data/catalog/ltmd_u1_preserved_exceptions.csv')
OUT=Path('data/catalog/ltmd_u1_exception_triage.csv')
REPORT=Path('docs/LTMD_U1_EXCEPTION_TRIAGE.md')
VERSION='LTMD_U1_EXCEPTION_TRIAGE_0.1'
EXPECTED=18

def num(detail:str,key:str):
    m=re.search(rf'\b{re.escape(key)}=(\d+)',detail)
    return int(m.group(1)) if m else None

def classify(r):
    detail=r['detail'];state=r['technical_state'];jpg=num(detail,'source_jpegs');internal=num(detail,'internal_unserved')
    if r['exception_kind']=='routing_unresolved' or (jpg==0 and r['wave'] in {'W7','W8'}):
        return 'routing_or_source_subtree_absent','routing/configuration recovery','Resolve official asset routing, ag_clave/config mapping, or an archival representation of the same full source sequence; do not infer identity from the adjacent generation.'
    if 'isolated_internal_unserved' in state or (internal is not None and internal>0):
        return 'isolated_internal_hole','exact-position recovery','Recover only the exact missing institutional position or a demonstrably equivalent archived body with positional provenance and cryptographic verification.'
    if r['wave']=='W8' and 'withheld_source' in state:
        return 'routing_or_source_subtree_absent','routing/configuration recovery','Resolve the complete source route before processing; a 2019 title of the same grade is only a comparator, not an alias.'
    return 'other_preserved_exception','manual evidence review','Review wave-level evidence; no automatic recovery rule is authorized.'

def main():
    rows=list(csv.DictReader(SRC.open(encoding='utf-8',newline='')))
    if len(rows)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} preserved exceptions, got {len(rows)}')
    out=[]
    for r in rows:
        cls,method,rule=classify(r)
        out.append({**r,'triage_version':VERSION,'recovery_class':cls,'recommended_evidence_path':method,'acceptance_rule':rule})
    counts=Counter(r['recovery_class'] for r in out)
    if counts['other_preserved_exception']:
        raise SystemExit(f'unclassified preserved exceptions remain: {counts["other_preserved_exception"]}')
    order={'isolated_internal_hole':0,'routing_or_source_subtree_absent':1}
    out.sort(key=lambda r:(order.get(r['recovery_class'],9),int(r['wave'][1:]),r['viewer_key']))
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    by=defaultdict(list)
    for r in out:by[r['recovery_class']].append(r)
    lines=['# LTMD-U1 — triage de excepciones técnicas preservadas','',f'Versión: `{VERSION}`.','',
           'El triage agrupa las excepciones por patrón técnico de recuperación. No altera cobertura, no crea aliases y no establece prioridad histórica o semántica.','',
           f'- Excepciones clasificadas: **{len(out)}/{EXPECTED}**.',f'- Huecos internos aislados: **{counts["isolated_internal_hole"]}**.',f'- Routing/subárbol de fuente ausente: **{counts["routing_or_source_subtree_absent"]}**.','','## Estrategias']
    lines+=['','### Hueco interno aislado','Buscar primero la posición institucional exacta y sus capturas archivadas; después, si existe otra representación oficial completa, demostrar correspondencia posicional antes de admitir el cuerpo faltante. Una página vecina o de otro estado/edición no es sustituto.','','### Routing o subárbol de fuente ausente','Resolver la configuración/ruta institucional como problema de conjunto: `ag_clave`, código del visor, mappings archivados o una secuencia alternativa explícitamente relacionada. La igualdad de título, grado, cardinalidad o generación próxima no crea un alias.','','## Casos','','| clase | ola | viewer | estado | issue |','|---|---|---|---|---|']
    for r in out:lines.append(f"| `{r['recovery_class']}` | {r['wave']} | `{r['viewer_key']}` | `{r['technical_state']}` | {r['tracking_issue']} |")
    lines+=['','## Regla de cierre','Una excepción sólo sale de este triage después de que el artefacto técnico autoritativo de su ola cambie y el registro U1 se regenere. La clasificación de recuperación por sí sola no modifica `effective_technical_identities`.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
