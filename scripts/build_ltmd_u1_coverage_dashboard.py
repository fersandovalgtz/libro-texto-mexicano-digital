#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from collections import Counter
from pathlib import Path

QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_coverage_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_coverage.md')
W9_COMPLETION=Path('docs/LTMD_U1_W9_COMPLETION.md')
W10_COMPLETION=Path('docs/LTMD_U1_W10_COMPLETION.md')
W11_COMPLETION=Path('docs/LTMD_U1_W11_COMPLETION.md')
EXPECTED_TOTAL=542

WAVES=[
 ('W1','ciencias_naturales',Path('docs/LTMD_U1_W1_COMPLETION_2026-08-15.md')),
 ('W2','matematicas',Path('docs/LTMD_U1_W2_COMPLETION.md')),
 ('W3','espanol_lengua',Path('docs/LTMD_U1_W3_COMPLETION.md')),
 ('W4','ciencias_sociales',Path('docs/LTMD_U1_W4_COMPLETION.md')),
 ('W5','historia',Path('docs/LTMD_U1_W5_COMPLETION.md')),
 ('W6','geografia_atlas',Path('docs/LTMD_U1_W6_COMPLETION.md')),
 ('W7','civica_etica',Path('docs/LTMD_U1_W7_COMPLETION.md')),
 ('W8','artes',Path('docs/LTMD_U1_W8_COMPLETION.md')),
 ('W9','educacion_fisica',None),
 ('W10','integrados_multiarea',None),
 ('W11','otros_no_clasificados',None),
]

def grab(text,pattern,label):
    m=re.search(pattern,text,re.I|re.S)
    if not m:raise SystemExit(f'coverage parser could not find {label}')
    return tuple(int(x.replace(',','')) for x in m.groups())

def completed_metrics(wave,text,planned):
    if wave=='W1':
        eff,total=grab(text,r'cobertura FRAGSEG efectiva:\s*\*\*([\d,]+)/([\d,]+)\*\*','W1 effective');can,total2=grab(text,r'FRAGSEG directamente materializado:\s*\*\*([\d,]+)/([\d,]+)\*\*','W1 canonical/direct')
    elif wave=='W2':
        eff,total=grab(text,r'Identidades con activos efectivamente resueltos:\s*\*\*([\d,]+)/([\d,]+)\*\*','W2 effective');(can,)=grab(text,r'Contenidos canónicos computados:\s*\*\*([\d,]+)\*\*','W2 canonical');total2=total
    elif wave=='W3':
        eff,total=grab(text,r'Identidades de catálogo cubiertas operacionalmente:\s*\*\*([\d,]+)/([\d,]+)\*\*','W3 effective');(can,)=grab(text,r'Contenidos canónicos computados:\s*\*\*([\d,]+)\*\*','W3 canonical');total2=total
    elif wave=='W4':
        eff,total=grab(text,r'Identidades/canónicos técnicos:\s*\*\*([\d,]+)/([\d,]+)\*\*','W4 effective/canonical');can=eff;total2=total
    elif wave in {'W5','W6','W9'}:
        eff,total=grab(text,r'Identidades históricas técnicamente cubiertas:\s*\*\*([\d,]+)/([\d,]+)\*\*',f'{wave} effective');(can,)=grab(text,r'Objetos canónicos de procesamiento:\s*\*\*([\d,]+)\*\*',f'{wave} canonical');total2=total
    elif wave in {'W7','W8'}:
        hist,total=grab(text,r'Identidades históricas preservadas:\s*\*\*([\d,]+)/([\d,]+)\*\*',f'{wave} historical scope');(can,)=grab(text,r'Canónicos procesados:\s*\*\*([\d,]+)\*\*',f'{wave} canonical');(retained,)=grab(text,r'Identidades retenidas por fuente:\s*\*\*([\d,]+)\*\*',f'{wave} retained')
        if hist!=total:raise SystemExit(f'{wave} historical identity preservation drift: {hist}/{total}')
        eff=total-retained;total2=total
    elif wave in {'W10','W11'}:
        hist,total=grab(text,r'Identidades históricas preservadas:\s*\*\*([\d,]+)/([\d,]+)\*\*',f'{wave} historical scope');eff,total2=grab(text,r'Identidades técnicamente cubiertas por fuente admitida:\s*\*\*([\d,]+)/([\d,]+)\*\*',f'{wave} effective');(can,)=grab(text,r'Objetos canónicos procesados:\s*\*\*([\d,]+)\*\*',f'{wave} canonical')
        if hist!=total:raise SystemExit(f'{wave} historical identity preservation drift: {hist}/{total}')
    else:raise AssertionError(wave)
    if total!=planned or total2!=planned:raise SystemExit(f'{wave} completion/queue drift: completion={total}/{total2}, queue-domain={planned}')
    if can>eff:raise SystemExit(f'{wave} canonical objects exceed effective identities: canonical={can}, effective={eff}')
    return eff,can

def w9_state(planned):
    if W9_COMPLETION.exists():
        eff,can=completed_metrics('W9',W9_COMPLETION.read_text(encoding='utf-8'),planned)
        if eff!=planned or can!=planned:raise SystemExit(f'W9 completion must close all four direct canonicals: effective={eff}, canonical={can}, planned={planned}')
        return eff,can,'closed',str(W9_COMPLETION)
    summary=Path('data/catalog/ltmd_u1_w9_educacion_fisica_ocr_summary.csv');report=Path('data/catalog/ltmd_u1_w9_educacion_fisica_ocr.md')
    if not summary.exists() or not report.exists():return 0,0,'queued','data/catalog/ltmd_u1_wave_queue.csv'
    rows=list(csv.DictReader(summary.open(encoding='utf-8',newline='')))
    if len(rows)!=planned or len({r['viewer_key'] for r in rows})!=planned:raise SystemExit('W9 OCR/queue drift')
    if any(int(r['unresolved'])!=0 or int(r['sha_verified'])!=int(r['pages']) for r in rows):raise SystemExit('W9 OCR state is not fully SHA-verified/resolved')
    return 0,0,'ocr_complete_downstream_pending',str(report)

def w10_state(planned):
    if W10_COMPLETION.exists():
        eff,can=completed_metrics('W10',W10_COMPLETION.read_text(encoding='utf-8'),planned);stage='closed' if eff==planned else 'source_admitted_cohort_closed_with_retentions';return eff,can,stage,str(W10_COMPLETION)
    stages=[('docs/LTMD_U1_W10_EXACT_REUSE.md','exact_reuse_complete_completion_pending'),('docs/LTMD_U1_W10_FRAGSEG.md','fragseg_complete_exact_reuse_pending'),('docs/LTMD_U1_W10_PAGESTRUCT.md','pagestruct_complete_fragseg_pending'),('docs/LTMD_U1_W10_OCR.md','ocr_complete_pagestruct_pending'),('docs/LTMD_U1_W10_PROCESSING_TOPOLOGY.md','source_topology_ready_ocr_pending'),('docs/LTMD_U1_W10_SOURCE_ADMISSIBILITY.md','source_admissibility_complete_topology_pending'),('docs/LTMD_U1_W10_ASSET_AUDIT.md','asset_audit_complete_admissibility_pending'),('docs/LTMD_U1_W10_DECLARED_INVENTORY.md','source_asset_audit_in_progress'),('docs/LTMD_U1_W10_ARCHITECTURE.md','architecture_complete_inventory_pending'),('docs/LTMD_U1_W10_FREEZE.md','scope_frozen_source_audit_pending')]
    for path,stage in stages:
        if Path(path).exists():return 0,0,stage,path
    return 0,0,'queued','data/catalog/ltmd_u1_wave_queue.csv'

def w11_state(planned):
    if planned!=111:raise SystemExit(f'W11 planned cardinality drift: {planned}')
    if W11_COMPLETION.exists():
        eff,can=completed_metrics('W11',W11_COMPLETION.read_text(encoding='utf-8'),planned);stage='closed' if eff==planned else 'source_admitted_cohort_closed_with_retentions';return eff,can,stage,str(W11_COMPLETION)
    stages=[
        ('docs/LTMD_U1_W11_EXACT_REUSE.md','exact_reuse_complete_completion_pending'),
        ('docs/LTMD_U1_W11_FRAGSEG.md','fragseg_complete_exact_reuse_pending'),
        ('docs/LTMD_U1_W11_PAGESTRUCT.md','pagestruct_complete_fragseg_pending'),
        ('docs/LTMD_U1_W11_OCR.md','ocr_complete_pagestruct_pending'),
        ('docs/LTMD_U1_W11_PROCESSING_TOPOLOGY.md','source_topology_ready_ocr_pending'),
        ('docs/LTMD_U1_W11_SOURCE_ADMISSIBILITY.md','source_admissibility_complete_topology_pending'),
    ]
    for path,stage in stages:
        if Path(path).exists():return 0,0,stage,path
    std=Path('docs/LTMD_U1_W11_STANDARD_ASSET_AUDIT.md');non=Path('docs/LTMD_U1_W11_NONSTANDARD_ASSET_AUDIT.md')
    if std.exists() and non.exists():return 0,0,'asset_audit_complete_admissibility_pending',str(std)
    if Path('docs/LTMD_U1_W11_STANDARD_DECLARED_INVENTORY.md').exists() or non.exists():return 0,0,'source_asset_audit_in_progress','docs/LTMD_U1_W11_STANDARD_DECLARED_INVENTORY.md'
    if Path('docs/LTMD_U1_W11_ARCHITECTURE.md').exists():return 0,0,'architecture_complete_inventory_pending','docs/LTMD_U1_W11_ARCHITECTURE.md'
    if Path('docs/LTMD_U1_W11_HETEROGENEITY.md').exists():return 0,0,'heterogeneity_complete_architecture_pending','docs/LTMD_U1_W11_HETEROGENEITY.md'
    if Path('docs/LTMD_U1_W11_FREEZE.md').exists():return 0,0,'scope_frozen_heterogeneity_pending','docs/LTMD_U1_W11_FREEZE.md'
    return 0,0,'queued','data/catalog/ltmd_u1_wave_queue.csv'

def main():
    w11_active=Path('docs/LTMD_U1_W11_FREEZE.md').exists();w10_active=Path('docs/LTMD_U1_W10_FREEZE.md').exists()
    version='LTMD_U1_COVERAGE_0.14' if W11_COMPLETION.exists() else ('LTMD_U1_COVERAGE_0.13' if w11_active else ('LTMD_U1_COVERAGE_0.12' if W10_COMPLETION.exists() else ('LTMD_U1_COVERAGE_0.11' if w10_active else ('LTMD_U1_COVERAGE_0.10' if W9_COMPLETION.exists() else 'LTMD_U1_COVERAGE_0.9'))))
    queue=list(csv.DictReader(QUEUE.open(encoding='utf-8',newline='')))
    if len(queue)!=EXPECTED_TOTAL or len({r['viewer_key'] for r in queue})!=EXPECTED_TOTAL:raise SystemExit(f'U1 queue invariant failed: rows={len(queue)} unique={len({r["viewer_key"] for r in queue})}')
    domain_counts=Counter(r['operational_domain'] for r in queue);known_domains={domain for _,domain,_ in WAVES}
    if set(domain_counts)!=known_domains:raise SystemExit(f'operational-domain partition drift: queue={sorted(domain_counts)} expected={sorted(known_domains)}')
    rows=[]
    for wave,domain,doc in WAVES:
        planned=domain_counts[domain]
        if planned<=0:raise SystemExit(f'missing operational domain {domain}')
        if doc:
            eff,can=completed_metrics(wave,doc.read_text(encoding='utf-8'),planned);stage='closed' if eff==planned else ('source_admitted_cohort_closed_with_retentions' if wave in {'W7','W8'} else 'partial_with_preserved_exceptions');evidence=str(doc)
        elif wave=='W9':eff,can,stage,evidence=w9_state(planned)
        elif wave=='W10':eff,can,stage,evidence=w10_state(planned)
        elif wave=='W11':eff,can,stage,evidence=w11_state(planned)
        rows.append({'coverage_version':version,'wave':wave,'operational_domain':domain,'planned_identities':planned,'effective_technical_identities':eff,'canonical_processing_objects':can,'remaining_to_effective':planned-eff,'stage':stage,'evidence':evidence})
    if sum(r['planned_identities'] for r in rows)!=EXPECTED_TOTAL:raise SystemExit('operational-domain partition does not sum to 542')
    eff=sum(r['effective_technical_identities'] for r in rows);can=sum(r['canonical_processing_objects'] for r in rows);w10=next(r for r in rows if r['wave']=='W10');w11=next(r for r in rows if r['wave']=='W11');base_eff,base_can=((349,318) if W9_COMPLETION.exists() else (345,314));expected_eff=base_eff+w10['effective_technical_identities']+w11['effective_technical_identities'];expected_can=base_can+w10['canonical_processing_objects']+w11['canonical_processing_objects']
    if eff!=expected_eff or can!=expected_can:raise SystemExit(f'coverage invariant failed: effective={eff}/{expected_eff}, canonical={can}/{expected_can}')
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    w9_sentence=('W9 está cerrada técnicamente en 4/4 identidades y cuatro objetos canónicos.' if W9_COMPLETION.exists() else 'W9 conserva 4/4 fuentes canónicas y OCR SHA-verificado, pero permanece fuera del numerador principal hasta completar PAGESTRUCT, FRAGSEG, reutilización exacta y el cierre técnico.')
    if W10_COMPLETION.exists():w10_sentence=f"W10 cerró técnicamente su cohorte fuente-admitida en {w10['effective_technical_identities']}/{w10['planned_identities']} identidades y {w10['canonical_processing_objects']} objetos canónicos; las retenciones permanecen explícitas."
    else:w10_sentence=f"W10 no suma aún al numerador y se encuentra en `{w10['stage']}`; su evidencia vigente es `{w10['evidence']}`."
    if W11_COMPLETION.exists():w11_sentence=f"W11 cerró técnicamente su cohorte fuente-admitida en {w11['effective_technical_identities']}/{w11['planned_identities']} identidades y {w11['canonical_processing_objects']} objetos canónicos; las retenciones permanecen explícitas."
    else:w11_sentence=f"W11 está activa en `{w11['stage']}` con evidencia `{w11['evidence']}`, pero aporta 0/111 al numerador hasta completar una cadena técnica defendible."
    lines=['# LTMD-U1 — tablero de cobertura técnica','',f'Versión: `{version}`.','','Este tablero se recompone desde la cola maestra por `operational_domain` y desde las actas/cortes técnicos W1–W11. **Cobertura técnica no equivale a preparación semántica ni a fase de ejecución.** Una ola puede encontrarse activamente en procesamiento y seguir aportando cero al numerador hasta cumplir su cierre técnico.','','## Totales','',f'- Universo U1: **{EXPECTED_TOTAL}/{EXPECTED_TOTAL}** identidades catalogadas.',f'- Cobertura técnica efectiva cerrada o resuelta: **{eff}/{EXPECTED_TOTAL} ({100*eff/EXPECTED_TOTAL:.2f}%)**.',f'- Objetos canónicos de procesamiento cerrados: **{can}/{EXPECTED_TOTAL} ({100*can/EXPECTED_TOTAL:.2f}%)**.',f'- Cobertura semántica humana validada incorporada al tablero: **0/{EXPECTED_TOTAL}**.','','## Por ola','','| ola | dominio operacional | plan | efectiva | canónicos | restantes | estado |','|---|---|---:|---:|---:|---:|---|']
    for r in rows:lines.append(f"| {r['wave']} | `{r['operational_domain']}` | {r['planned_identities']} | {r['effective_technical_identities']} | {r['canonical_processing_objects']} | {r['remaining_to_effective']} | `{r['stage']}` |")
    lines+=['','## Lectura correcta','',f'W1, W3, W4, W5 y W6 están cerradas técnicamente. W2 conserva cuatro excepciones de routing sin imputación. W7 tiene cierre técnico de su cohorte fuente-admitida: 25/30 identidades y cinco retenciones explícitas. W8 tiene cierre técnico de su cohorte fuente-admitida: 16/20 identidades y cuatro retenciones explícitas. {w9_sentence} {w10_sentence} {w11_sentence}','','`wave_label` no se usa para reconstruir la partición científica porque la cola también codifica estados de ejecución; la partición se deriva de `operational_domain`.','','`effective_technical_identities` puede incluir identidades documentales cubiertas mediante aliases o rutas demostradas criptográficamente; `canonical_processing_objects` evita duplicar procesamiento de contenido cuando la evidencia de identidad/reutilización lo permite. Las retenciones de fuente no se sustituyen por aliases heurísticos.','','`WAITING_HUMAN_REFERENCE` sigue vigente. OCR, PAGESTRUCT, FRAGSEG y la igualdad de hashes son infraestructura técnica; no validan por sí mismos categorías semánticas, continuidad curricular ni equivalencia pedagógica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
