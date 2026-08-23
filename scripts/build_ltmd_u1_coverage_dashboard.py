#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from collections import Counter
from pathlib import Path

QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_coverage_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_coverage.md')
W9_COMPLETION=Path('docs/LTMD_U1_W9_COMPLETION.md')
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
    elif wave in {'W5','W6','W9'}:
        eff,total=grab(text,r'Identidades históricas técnicamente cubiertas:\s*\*\*([\d,]+)/([\d,]+)\*\*',f'{wave} effective')
        (can,)=grab(text,r'Objetos canónicos de procesamiento:\s*\*\*([\d,]+)\*\*',f'{wave} canonical')
        total2=total
    elif wave in {'W7','W8'}:
        hist,total=grab(text,r'Identidades históricas preservadas:\s*\*\*([\d,]+)/([\d,]+)\*\*',f'{wave} historical scope')
        (can,)=grab(text,r'Canónicos procesados:\s*\*\*([\d,]+)\*\*',f'{wave} canonical')
        (retained,)=grab(text,r'Identidades retenidas por fuente:\s*\*\*([\d,]+)\*\*',f'{wave} retained')
        if hist!=total:
            raise SystemExit(f'{wave} historical identity preservation drift: {hist}/{total}')
        eff=total-retained; total2=total
        if can>eff:
            raise SystemExit(f'{wave} canonical objects exceed effective identities: canonical={can}, effective={eff}')
    else:
        raise AssertionError(wave)
    if total!=planned or total2!=planned:
        raise SystemExit(f'{wave} completion/queue drift: completion={total}/{total2}, queue-domain={planned}')
    return eff,can

def w9_state(planned):
    if W9_COMPLETION.exists():
        eff,can=completed_metrics('W9',W9_COMPLETION.read_text(encoding='utf-8'),planned)
        if eff!=planned or can!=planned:
            raise SystemExit(f'W9 completion must close all four direct canonicals: effective={eff}, canonical={can}, planned={planned}')
        return eff,can,'closed',str(W9_COMPLETION)
    summary=Path('data/catalog/ltmd_u1_w9_educacion_fisica_ocr_summary.csv')
    report=Path('data/catalog/ltmd_u1_w9_educacion_fisica_ocr.md')
    if not summary.exists() or not report.exists():
        return 0,0,'queued','data/catalog/ltmd_u1_wave_queue.csv'
    rows=list(csv.DictReader(summary.open(encoding='utf-8',newline='')))
    if len(rows)!=planned or len({r['viewer_key'] for r in rows})!=planned:
        raise SystemExit(f'W9 OCR/queue drift: rows={len(rows)}, unique={len({r["viewer_key"] for r in rows})}, planned={planned}')
    if any(int(r['unresolved'])!=0 or int(r['sha_verified'])!=int(r['pages']) for r in rows):
        raise SystemExit('W9 OCR state is not fully SHA-verified/resolved')
    return 0,0,'ocr_complete_downstream_pending',str(report)

def main():
    version='LTMD_U1_COVERAGE_0.10' if W9_COMPLETION.exists() else 'LTMD_U1_COVERAGE_0.9'
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
            if eff==planned:
                stage='closed'
            elif wave in {'W7','W8'}:
                stage='source_admitted_cohort_closed_with_retentions'
            else:
                stage='partial_with_preserved_exceptions'
            evidence=str(doc)
        elif wave=='W9':
            eff,can,stage,evidence=w9_state(planned)
        else:
            eff=can=0; stage='queued'; evidence='data/catalog/ltmd_u1_wave_queue.csv'
        rows.append({'coverage_version':version,'wave':wave,'operational_domain':domain,'planned_identities':planned,'effective_technical_identities':eff,'canonical_processing_objects':can,'remaining_to_effective':planned-eff,'stage':stage,'evidence':evidence})
    if sum(r['planned_identities'] for r in rows)!=EXPECTED_TOTAL:
        raise SystemExit('operational-domain partition does not sum to 542')
    eff=sum(r['effective_technical_identities'] for r in rows);can=sum(r['canonical_processing_objects'] for r in rows)
    expected_eff,expected_can=(349,318) if W9_COMPLETION.exists() else (345,314)
    if eff!=expected_eff or can!=expected_can:
        raise SystemExit(f'coverage invariant failed: effective={eff}/{expected_eff}, canonical={can}/{expected_can}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    w9_sentence=('W9 está cerrada técnicamente en 4/4 identidades y cuatro objetos canónicos.' if W9_COMPLETION.exists() else 'W9 conserva 4/4 fuentes canónicas y OCR SHA-verificado, pero permanece fuera del numerador principal hasta completar PAGESTRUCT, FRAGSEG, reutilización exacta y el cierre técnico.')
    lines=['# LTMD-U1 — tablero de cobertura técnica','',f'Versión: `{version}`.','','Este tablero se recompone desde la cola maestra por `operational_domain` y desde las actas/cortes técnicos W1–W9. **Cobertura técnica no equivale a preparación semántica.** La promoción de W9 al numerador sólo ocurre cuando existe y pasa su acta de cierre técnico reproducible.','','## Totales','',f'- Universo U1: **{EXPECTED_TOTAL}/{EXPECTED_TOTAL}** identidades catalogadas.',f'- Cobertura técnica efectiva cerrada o resuelta: **{eff}/{EXPECTED_TOTAL} ({100*eff/EXPECTED_TOTAL:.2f}%)**.',f'- Objetos canónicos de procesamiento cerrados: **{can}/{EXPECTED_TOTAL} ({100*can/EXPECTED_TOTAL:.2f}%)**.',f'- Cobertura semántica humana validada incorporada al tablero: **0/{EXPECTED_TOTAL}**.','', '## Por ola','', '| ola | dominio operacional | plan | efectiva | canónicos | restantes | estado |','|---|---|---:|---:|---:|---:|---|']
    for r in rows:
        lines.append(f"| {r['wave']} | `{r['operational_domain']}` | {r['planned_identities']} | {r['effective_technical_identities']} | {r['canonical_processing_objects']} | {r['remaining_to_effective']} | `{r['stage']}` |")
    lines += ['', '## Lectura correcta', '', f'W1, W3, W4, W5 y W6 están cerradas técnicamente. W2 conserva cuatro excepciones de routing sin imputación. W7 tiene cierre técnico de su cohorte fuente-admitida: 25/30 identidades y cinco retenciones explícitas. W8 tiene cierre técnico de su cohorte fuente-admitida: 16/20 identidades y cuatro retenciones explícitas. {w9_sentence} W10–W11 permanecen en cola.', '', '`wave_label` no se usa para reconstruir la partición científica porque la cola también codifica estados de ejecución; la partición se deriva de `operational_domain`.', '', '`effective_technical_identities` puede incluir identidades documentales cubiertas mediante aliases o rutas demostradas criptográficamente; `canonical_processing_objects` evita duplicar procesamiento de contenido cuando la evidencia de identidad/reutilización lo permite. En W7 y W8 las retenciones de fuente no se sustituyen por aliases heurísticos.', '', '`WAITING_HUMAN_REFERENCE` sigue vigente. OCR, PAGESTRUCT, FRAGSEG y la igualdad de hashes son infraestructura técnica; no validan por sí mismos categorías semánticas, continuidad curricular ni equivalencia pedagógica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':
    main()
