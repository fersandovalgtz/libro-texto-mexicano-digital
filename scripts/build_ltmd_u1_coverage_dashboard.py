#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from collections import Counter
from pathlib import Path

QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_coverage_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_coverage.md')
VERSION='LTMD_U1_COVERAGE_0.6'
EXPECTED_TOTAL=542

WAVES=[
 ('W1','ciencias_naturales',Path('docs/LTMD_U1_W1_COMPLETION_2026-08-15.md')),
 ('W2','matematicas',Path('docs/LTMD_U1_W2_COMPLETION.md')),
 ('W3','espanol_lengua',Path('docs/LTMD_U1_W3_COMPLETION.md')),
 ('W4','ciencias_sociales',Path('docs/LTMD_U1_W4_COMPLETION.md')),
 ('W5','historia',Path('docs/LTMD_U1_W5_COMPLETION.md')),
 ('W6','geografia_atlas',None),
 ('W7','civica_etica',None),
 ('W8','artes',None),
 ('W9','educacion_fisica',None),
 ('W10','integrados_multiarea',None),
 ('W11','otros_no_clasificados',None),
]

def grab(text,pattern,label):
    m=re.search(pattern,text,re.I|re.S)
    if not m: raise SystemExit(f'coverage parser could not find {label}')
    return tuple(int(x.replace(',','')) for x in m.groups())

def completed_metrics(wave,text,planned):
    if wave=='W1':
        eff,total=grab(text,r'cobertura FRAGSEG efectiva:\s*\*\*([\d,]+)/([\d,]+)\*\*','W1 effective')
        can,total2=grab(text,r'FRAGSEG directamente materializado:\s*\*\*([\d,]+)/([\d,]+)\*\*','W1 canonical/direct')
    elif wave=='W2':
        eff,total=grab(text,r'Identidades con activos efectivamente resueltos:\s*\*\*([\d,]+)/([\d,]+)\*\*','W2 effective')
        (can,)=grab(text,r'Contenidos canónicos computados:\s*\*\*([\d,]+)\*\*','W2 canonical')
        total2=total
    elif wave=='W3':
        eff,total=grab(text,r'Identidades de catálogo cubiertas operacionalmente:\s*\*\*([\d,]+)/([\d,]+)\*\*','W3 effective')
        (can,)=grab(text,r'Contenidos canónicos computados:\s*\*\*([\d,]+)\*\*','W3 canonical')
        total2=total
    elif wave=='W4':
        eff,total=grab(text,r'Identidades/canónicos técnicos:\s*\*\*([\d,]+)/([\d,]+)\*\*','W4 effective/canonical')
        can=eff; total2=total
    elif wave=='W5':
        eff,total=grab(text,r'Identidades históricas técnicamente cubiertas:\s*\*\*([\d,]+)/([\d,]+)\*\*','W5 effective')
        (can,)=grab(text,r'Objetos canónicos de procesamiento:\s*\*\*([\d,]+)\*\*','W5 canonical')
        total2=total
    else: raise AssertionError(wave)
    if total!=planned or total2!=planned: raise SystemExit(f'{wave} completion/queue drift: completion={total}/{total2}, queue-domain={planned}')
    return eff,can

def main():
    queue=list(csv.DictReader(QUEUE.open(encoding='utf-8',newline='')))
    if len(queue)!=EXPECTED_TOTAL or len({r['viewer_key'] for r in queue})!=EXPECTED_TOTAL:
        raise SystemExit(f'U1 queue invariant failed: rows={len(queue)} unique={len({r["viewer_key"] for r in queue})}')
    domain_counts=Counter(r['operational_domain'] for r in queue)
    known_domains={domain for _,domain,_ in WAVES}
    if set(domain_counts)!=known_domains:
        raise SystemExit(f'operational-domain partition drift: queue={sorted(domain_counts)} expected={sorted(known_domains)}')
    rows=[]
    for wave,domain,doc in WAVES:
        planned=domain_counts[domain]
        if planned<=0: raise SystemExit(f'missing operational domain {domain}')
        if doc:
            text=doc.read_text(encoding='utf-8')
            eff,can=completed_metrics(wave,text,planned)
            stage='closed' if eff==planned else 'partial_with_preserved_exceptions'
            evidence=str(doc)
        elif wave=='W6':
            scope=Path('data/catalog/ltmd_u1_w6_scope.csv')
            arch=Path('data/catalog/ltmd_u1_w6_viewer_architecture.csv')
            if not scope.exists() or not arch.exists(): raise SystemExit('W6 source-first artifacts missing')
            sr=list(csv.DictReader(scope.open(encoding='utf-8',newline=''))); ar=list(csv.DictReader(arch.open(encoding='utf-8',newline='')))
            if len(sr)!=planned or len(ar)!=planned: raise SystemExit(f'W6 scope/architecture coverage drift: {len(sr)}/{len(ar)} vs {planned}')
            eff=can=0; stage='source_first_active'; evidence='data/catalog/ltmd_u1_w6_viewer_architecture.csv'
        else:
            eff=can=0; stage='queued'; evidence='data/catalog/ltmd_u1_wave_queue.csv'
        rows.append({'coverage_version':VERSION,'wave':wave,'operational_domain':domain,'planned_identities':planned,'effective_technical_identities':eff,'canonical_processing_objects':can,'remaining_to_effective':planned-eff,'stage':stage,'evidence':evidence})
    if sum(r['planned_identities'] for r in rows)!=EXPECTED_TOTAL: raise SystemExit('operational-domain partition does not sum to 542')
    eff=sum(r['effective_technical_identities'] for r in rows); can=sum(r['canonical_processing_objects'] for r in rows)
    if eff!=262 or can!=236: raise SystemExit(f'post-W5 coverage invariant failed: effective={eff}, canonical={can}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    lines=['# LTMD-U1 — tablero de cobertura técnica','',f'Versión: `{VERSION}`.','','Este tablero se recompone desde la cola maestra por `operational_domain` y desde las actas de cierre W1–W5. **Cobertura técnica no equivale a preparación semántica.**','','## Totales','',f'- Universo U1: **{EXPECTED_TOTAL}/{EXPECTED_TOTAL}** identidades catalogadas.',f'- Cobertura técnica efectiva cerrada o resuelta: **{eff}/{EXPECTED_TOTAL} ({100*eff/EXPECTED_TOTAL:.2f}%)**.',f'- Objetos canónicos de procesamiento: **{can}/{EXPECTED_TOTAL} ({100*can/EXPECTED_TOTAL:.2f}%)**.',f'- Cobertura semántica humana validada incorporada al tablero: **0/{EXPECTED_TOTAL}**.','', '## Por ola','', '| ola | dominio operacional | plan | efectiva | canónicos | restantes | estado |','|---|---|---:|---:|---:|---:|---|']
    for r in rows: lines.append(f"| {r['wave']} | `{r['operational_domain']}` | {r['planned_identities']} | {r['effective_technical_identities']} | {r['canonical_processing_objects']} | {r['remaining_to_effective']} | `{r['stage']}` |")
    lines += ['', '## Lectura correcta', '', 'W1, W3, W4 y W5 están cerradas técnicamente. W2 conserva cuatro excepciones de routing sin imputación. W6 está activo únicamente en source-first y por ello todavía no suma identidades a la cobertura técnica efectiva. W7–W11 permanecen en cola.', '', '`wave_label` no se usa para reconstruir la partición científica porque la cola también codifica estados de ejecución como materialización y aliases; la partición se deriva de `operational_domain`.', '', '`effective_technical_identities` puede incluir identidades documentales cubiertas mediante aliases o rutas demostradas criptográficamente; `canonical_processing_objects` evita duplicar procesamiento de contenido cuando la evidencia de identidad/reutilización lo permite.', '', '`WAITING_HUMAN_REFERENCE` sigue vigente. PAGESTRUCT, FRAGSEG y la igualdad de hashes son infraestructura técnica; no validan por sí mismos categorías semánticas, continuidad curricular ni equivalencia pedagógica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__': main()
