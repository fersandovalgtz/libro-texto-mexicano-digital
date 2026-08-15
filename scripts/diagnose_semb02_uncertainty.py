#!/usr/bin/env python3
"""Diagnose SEMB_0.2 uncertainty without accessing fragment text.

This is a descriptive diagnostic of the already-frozen SEMB_0.2 corpus output.
It MUST NOT tune thresholds from historical contrasts. It joins only persisted
metadata from FRAGSEG and SEMB_0.2 scores/flags and reports which preregistered
uncertainty rule is binding.
"""
from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

LABELS=Path('data/derived/fragment_labels_B.csv')
MANIFEST=Path('data/derived/fragment_manifest.csv')
OUT=Path('data/derived/semb02_uncertainty_diagnostic.csv')
OUT_TYPES=Path('data/derived/semb02_uncertainty_by_candidate_type.csv')
OUT_BINS=Path('data/derived/semb02_uncertainty_by_token_bin.csv')
OUT_Q=Path('data/derived/semb02_uncertainty_quantiles.csv')
OUT_MD=Path('data/derived/semb02_uncertainty_diagnostic.md')
VERSION='SEMB02_UNCERTAINTY_DIAG_0.1'
GATE_THRESHOLD=0.0
GATE_BUFFER=0.02
TOP_MARGIN=0.01


def fnum(x):
    if x is None or x=='': return None
    return float(x)


def pct(n,d):
    return 100.0*n/d if d else float('nan')


def qtile(vals,q):
    vals=sorted(v for v in vals if v is not None and math.isfinite(v))
    if not vals: return None
    if len(vals)==1: return vals[0]
    pos=(len(vals)-1)*q; lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    if lo==hi: return vals[lo]
    return vals[lo]+(vals[hi]-vals[lo])*(pos-lo)


def token_bin(n):
    n=int(n)
    if n<4: return '<4'
    if n<=12: return '4-12'
    if n<=30: return '13-30'
    if n<=60: return '31-60'
    if n<=120: return '61-120'
    return '>120'


def classify(r,m):
    typ=m['candidate_type']; n=int(m['token_count'])
    skipped=(typ=='heading_candidate' or n<4)
    gate=fnum(r['action_gate_margin_B']); am=fnum(r['action_margin_B']); pm=fnum(r['position_margin_B'])
    if skipped:
        action_reason='skipped_heading_or_short'
        position_reason='skipped_heading_or_short'
    else:
        if gate is None:
            action_reason='missing_gate'
        elif gate < GATE_THRESHOLD:
            action_reason='gate_below_threshold'
        elif gate < GATE_THRESHOLD+GATE_BUFFER:
            action_reason='gate_buffer'
        elif am is None:
            action_reason='missing_action_margin'
        elif am < TOP_MARGIN:
            action_reason='action_top_margin'
        else:
            action_reason='action_certain'
        if pm is None:
            position_reason='missing_position_margin'
        elif pm < TOP_MARGIN:
            position_reason='position_top_margin'
        else:
            position_reason='position_certain'
    return skipped,action_reason,position_reason,gate,am,pm


def summarize(rows):
    c=Counter()
    vals=defaultdict(list)
    for x in rows:
        c['n']+=1
        c['uncertain_any']+=x['uncertain_any']
        c['uncertain_action']+=x['uncertain_action']
        c['uncertain_position']+=x['uncertain_position']
        c['skipped']+=x['skipped']
        c['zero_action']+=x['zero_action']
        c['zero_position']+=x['zero_position']
        c['both_certain']+=int(not x['uncertain_any'])
        c['action_certain_flag']+=int(not x['uncertain_action'])
        c['position_certain_flag']+=int(not x['uncertain_position'])
        c['action_reason:'+x['action_reason']]+=1
        c['position_reason:'+x['position_reason']]+=1
        for k in ('gate','action_margin','position_margin','token_count'):
            if x[k] is not None: vals[k].append(float(x[k]))
    return c,vals


def row_summary(group,rows):
    c,_=summarize(rows); n=c['n']
    return {
        'group':group,'n':n,
        'uncertain_any_n':c['uncertain_any'],'uncertain_any_pct':round(pct(c['uncertain_any'],n),4),
        'uncertain_action_n':c['uncertain_action'],'uncertain_action_pct':round(pct(c['uncertain_action'],n),4),
        'uncertain_position_n':c['uncertain_position'],'uncertain_position_pct':round(pct(c['uncertain_position'],n),4),
        'both_certain_n':c['both_certain'],'both_certain_pct':round(pct(c['both_certain'],n),4),
        'skipped_n':c['skipped'],'skipped_pct':round(pct(c['skipped'],n),4),
        'gate_below_threshold_n':c['action_reason:gate_below_threshold'],'gate_below_threshold_pct':round(pct(c['action_reason:gate_below_threshold'],n),4),
        'gate_buffer_n':c['action_reason:gate_buffer'],'gate_buffer_pct':round(pct(c['action_reason:gate_buffer'],n),4),
        'action_top_margin_n':c['action_reason:action_top_margin'],'action_top_margin_pct':round(pct(c['action_reason:action_top_margin'],n),4),
        'action_certain_rule_n':c['action_reason:action_certain'],'action_certain_rule_pct':round(pct(c['action_reason:action_certain'],n),4),
        'position_top_margin_n':c['position_reason:position_top_margin'],'position_top_margin_pct':round(pct(c['position_reason:position_top_margin'],n),4),
        'position_certain_rule_n':c['position_reason:position_certain'],'position_certain_rule_pct':round(pct(c['position_reason:position_certain'],n),4),
        'zero_action_n':c['zero_action'],'zero_action_pct':round(pct(c['zero_action'],n),4),
        'zero_position_n':c['zero_position'],'zero_position_pct':round(pct(c['zero_position'],n),4),
        'diagnostic_version':VERSION,
    }


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def main():
    manifest={r['fragment_id']:r for r in csv.DictReader(MANIFEST.open(encoding='utf-8'))}
    labels=list(csv.DictReader(LABELS.open(encoding='utf-8')))
    assert len(labels)==len(manifest)==9594
    enriched=[]
    for r in labels:
        m=manifest[r['fragment_id']]
        assert r['catalog_generation']==m['catalog_generation']
        skipped,ar,pr,gate,am,pm=classify(r,m)
        enriched.append({
            'generation':r['catalog_generation'],'candidate_type':m['candidate_type'],
            'token_count':int(m['token_count']),'token_bin':token_bin(m['token_count']),
            'skipped':int(skipped),'action_reason':ar,'position_reason':pr,
            'gate':gate,'action_margin':am,'position_margin':pm,
            'uncertain_action':int(r['uncertain_action_B']),'uncertain_position':int(r['uncertain_position_B']),
            'uncertain_any':int(r['uncertain_B']),
            'zero_action':int(r['action_label_count_B'])==0,'zero_position':int(r['position_label_count_B'])==0,
        })
    # Internal consistency: diagnostic rules must reproduce persisted flags.
    for x in enriched:
        pred_a=int(x['action_reason']!='action_certain')
        pred_p=int(x['position_reason']!='position_certain')
        assert pred_a==x['uncertain_action'], (x,pred_a)
        assert pred_p==x['uncertain_position'], (x,pred_p)
        assert int(pred_a or pred_p)==x['uncertain_any']

    groups=[('ALL',enriched)]
    for g in ('1972','1988','1993','2014'):
        groups.append((g,[x for x in enriched if x['generation']==g]))
    write_csv(OUT,[row_summary(k,v) for k,v in groups])

    type_rows=[]
    for typ in sorted({x['candidate_type'] for x in enriched}):
        rr=[x for x in enriched if x['candidate_type']==typ]
        type_rows.append(row_summary(typ,rr))
    write_csv(OUT_TYPES,type_rows)

    bin_order=['<4','4-12','13-30','31-60','61-120','>120']
    bin_rows=[]
    for b in bin_order:
        rr=[x for x in enriched if x['token_bin']==b]
        if rr: bin_rows.append(row_summary(b,rr))
    write_csv(OUT_BINS,bin_rows)

    qrows=[]
    for group,rr in groups:
        eligible=[x for x in rr if not x['skipped']]
        for metric in ('gate','action_margin','position_margin','token_count'):
            vals=[x[metric] for x in eligible if x[metric] is not None]
            qrows.append({'group':group,'metric':metric,'n':len(vals),
                'q01':qtile(vals,.01),'q05':qtile(vals,.05),'q10':qtile(vals,.10),'q25':qtile(vals,.25),
                'q50':qtile(vals,.50),'q75':qtile(vals,.75),'q90':qtile(vals,.90),'q95':qtile(vals,.95),'q99':qtile(vals,.99),
                'diagnostic_version':VERSION})
    write_csv(OUT_Q,qrows)

    overall=row_summary('ALL',enriched)
    eligible=[x for x in enriched if not x['skipped']]
    ec,_=summarize(eligible); ne=ec['n']
    gate_block=ec['action_reason:gate_below_threshold']+ec['action_reason:gate_buffer']
    pos_block=ec['position_reason:position_top_margin']
    action_margin_block=ec['action_reason:action_top_margin']
    both_rule_certain=sum(1 for x in eligible if x['action_reason']=='action_certain' and x['position_reason']=='position_certain')
    qgate=[x['gate'] for x in eligible if x['gate'] is not None]
    qam=[x['action_margin'] for x in eligible if x['action_margin'] is not None]
    qpm=[x['position_margin'] for x in eligible if x['position_margin'] is not None]

    md=f'''# Diagnóstico de incertidumbre SEMB 0.2\n\nVersión: `{VERSION}`. Este diagnóstico usa únicamente metadatos y puntuaciones ya persistidas; no accede al texto OCR ni modifica umbrales.\n\n## Resultado ejecutivo\n\n- Fragmentos totales: **{overall['n']}**.\n- Incertidumbre global persistida: **{overall['uncertain_any_n']} ({overall['uncertain_any_pct']:.2f}%)**.\n- Fragmentos excluidos de clasificación por `heading_candidate` o longitud <4 tokens: **{overall['skipped_n']} ({overall['skipped_pct']:.2f}%)**.\n- Fragmentos elegibles no omitidos: **{ne}**.\n- En elegibles, la regla del gate de acción bloquea **{gate_block} ({pct(gate_block,ne):.2f}%)**: margen <0 o dentro del buffer [0, 0.02).\n- Tras superar el gate+buffer, el margen entre las dos mejores acciones bloquea **{action_margin_block} ({pct(action_margin_block,ne):.2f}%)** adicional.\n- La regla de margen de posición (<0.01) bloquea **{pos_block} ({pct(pos_block,ne):.2f}%)** de los elegibles.\n- Sólo **{both_rule_certain} ({pct(both_rule_certain,ne):.2f}%)** de los elegibles satisfacen simultáneamente las reglas de certeza de acción y posición.\n\n## Distribuciones centrales en fragmentos elegibles\n\n- `action_gate_margin_B`: mediana **{qtile(qgate,.5):.4f}**, p75 **{qtile(qgate,.75):.4f}**, p90 **{qtile(qgate,.90):.4f}**. Umbral de certeza práctica vigente: **0.0200**.\n- `action_margin_B`: mediana **{qtile(qam,.5):.4f}**, p75 **{qtile(qam,.75):.4f}**, p90 **{qtile(qam,.90):.4f}**. Umbral: **0.0100**.\n- `position_margin_B`: mediana **{qtile(qpm,.5):.4f}**, p75 **{qtile(qpm,.75):.4f}**, p90 **{qtile(qpm,.90):.4f}**. Umbral: **0.0100**.\n\n## Lectura metodológica\n\nLa capa SEMB 0.2 no debe recalibrarse observando qué umbral produce la narrativa histórica más atractiva. Los archivos por generación, tipo de fragmento, longitud y cuantiles permiten localizar el mecanismo de incertidumbre sin usar los contrastes históricos como función objetivo. Si se desarrolla SEMB 0.3, sus parámetros deben fijarse con evidencia independiente del corpus histórico (validación sintética ampliada y, preferentemente, una muestra humana estratificada y ciega a la generación), bloquearse y sólo después aplicarse al corpus congelado.\n\n## Archivos asociados\n\n- `semb02_uncertainty_diagnostic.csv`: resumen total y por generación.\n- `semb02_uncertainty_by_candidate_type.csv`: diagnóstico por tipo FRAGSEG.\n- `semb02_uncertainty_by_token_bin.csv`: diagnóstico por longitud.\n- `semb02_uncertainty_quantiles.csv`: cuantiles de gate, márgenes y longitud.\n'''
    OUT_MD.write_text(md,encoding='utf-8')
    print(md)

if __name__=='__main__': main()
