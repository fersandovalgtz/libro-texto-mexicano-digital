#!/usr/bin/env python3
"""Evaluate frozen SEMB 0.2 on the independent SEMB03 synthetic stress suite.

This is a diagnostic only. It does not tune SEMB 0.2 and must not be used as a
substitute for human validation. It reads no historical outputs.
"""
from __future__ import annotations
import csv, json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

from semantic_classifier_B02_core import SemanticB02

CASES=Path('data/validation/semb03_synthetic_stress_cases.csv')
OUT_JSON=Path('data/derived/semb02_synthetic_stress_result.json')
OUT_MD=Path('data/derived/semb02_synthetic_stress_result.md')
VERSION='SEMB02_SYNTH_STRESS_EVAL_0.1'


def labs(s):return {x for x in (s or '').split(';') if x}

def safe_div(a,b):return a/b if b else None

def main():
    rows=list(csv.DictReader(CASES.open(encoding='utf-8')))
    assert len(rows)==105 and all(r['suite_version']=='SEMB03_SYNTH_STRESS_0.1' for r in rows)
    eng=SemanticB02(); qs=eng.embed_texts([r['text'] for r in rows])
    rec=[]
    for r,q in zip(rows,qs):
        a=eng.select_actions(q,skip=False); p=eng.select_positions(q,skip=False)
        pred_actionable=int(float(a['gate_margin'])>=eng.gate_threshold)
        pred_actionable_certain=int(float(a['gate_margin'])>=eng.gate_threshold+0.02)
        top_action=eng.action_labels[int(np.argmax(a['scores']))]
        top_position=eng.position_labels[int(np.argmax(p['scores']))]
        rec.append({
            **r,
            'gate_margin':float(a['gate_margin']),
            'pred_actionable':pred_actionable,
            'pred_actionable_certain':pred_actionable_certain,
            'pred_action_labels':';'.join(a['labels']),
            'top_action':top_action,
            'action_margin':float(a['margin']),
            'uncertain_action':int(a['uncertain']),
            'pred_position_labels':';'.join(p['labels']),
            'top_position':top_position,
            'position_margin':float(p['margin']),
            'uncertain_position':int(p['uncertain']),
        })

    gate=[x for x in rec if x['expected_actionable'] in {'0','1'}]
    y=[int(x['expected_actionable']) for x in gate]; yh=[x['pred_actionable'] for x in gate]
    tp=sum(a==1 and b==1 for a,b in zip(y,yh)); tn=sum(a==0 and b==0 for a,b in zip(y,yh))
    fp=sum(a==0 and b==1 for a,b in zip(y,yh)); fn=sum(a==1 and b==0 for a,b in zip(y,yh))
    sens=safe_div(tp,tp+fn); spec=safe_div(tn,tn+fp); bal=(sens+spec)/2

    action_cases=[x for x in rec if x['focus']=='action']
    action_top1=sum(x['top_action'] in labs(x['expected_action_labels']) for x in action_cases)/len(action_cases)
    action_inclusion=sum(bool(labs(x['pred_action_labels']) & labs(x['expected_action_labels'])) for x in action_cases)/len(action_cases)
    pos_cases=[x for x in rec if x['focus']=='position']
    pos_top1=sum(x['top_position'] in labs(x['expected_position_labels']) for x in pos_cases)/len(pos_cases)
    pos_inclusion=sum(bool(labs(x['pred_position_labels']) & labs(x['expected_position_labels'])) for x in pos_cases)/len(pos_cases)

    neg=[x for x in rec if x['focus']=='gate_negative']
    pos_gate=[x for x in rec if x['expected_actionable']=='1']
    result={
      'evaluation_version':VERSION,
      'suite_version':'SEMB03_SYNTH_STRESS_0.1',
      'semantic_version':'SEMB_0.2',
      'n_cases':len(rec),
      'gate':{'tp':tp,'tn':tn,'fp':fp,'fn':fn,'sensitivity':sens,'specificity':spec,'balanced_accuracy':bal},
      'action_focus':{'n':len(action_cases),'top1_accuracy':action_top1,'final_label_inclusion_rate':action_inclusion,
                      'uncertain_rate':sum(x['uncertain_action'] for x in action_cases)/len(action_cases)},
      'position_focus':{'n':len(pos_cases),'top1_accuracy':pos_top1,'final_label_inclusion_rate':pos_inclusion,
                        'uncertain_rate':sum(x['uncertain_position'] for x in pos_cases)/len(pos_cases)},
      'negative_stress':{'n':len(neg),'false_positive_rate':sum(x['pred_actionable'] for x in neg)/len(neg),
                         'certain_false_positive_rate':sum(x['pred_actionable_certain'] for x in neg)/len(neg)},
      'positive_gate':{'n':len(pos_gate),'miss_rate':sum(not x['pred_actionable'] for x in pos_gate)/len(pos_gate),
                       'uncertain_or_missed_rate':sum((not x['pred_actionable_certain']) for x in pos_gate)/len(pos_gate)},
      'gate_margin_quantiles':{str(q):float(np.quantile([x['gate_margin'] for x in rec],q)) for q in (0.1,0.25,0.5,0.75,0.9)},
    }
    OUT_JSON.parent.mkdir(parents=True,exist_ok=True)
    json.dump(result,OUT_JSON.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    lines=['# SEMB 0.2 frente a batería sintética independiente','',f'Versión: `{VERSION}`. Batería: `SEMB03_SYNTH_STRESS_0.1`.','',
           '> Diagnóstico sintético: no sustituye referencia humana y no contiene texto del corpus histórico.','',
           '## Gate de acción',
           f"- n={len(gate)}; balanced accuracy={bal:.3f}; sensibilidad={sens:.3f}; especificidad={spec:.3f}.",
           f"- Falsos positivos en negativos de estrés: {result['negative_stress']['false_positive_rate']:.1%}; falsos positivos que además superan buffer de certeza: {result['negative_stress']['certain_false_positive_rate']:.1%}.",
           f"- En positivos, tasa de pérdida por gate: {result['positive_gate']['miss_rate']:.1%}; sin superar el buffer de certeza: {result['positive_gate']['uncertain_or_missed_rate']:.1%}.",'',
           '## Categorías',
           f"- Acciones: top-1={action_top1:.1%}; inclusión de etiqueta esperada en salida final={action_inclusion:.1%}; incertidumbre={result['action_focus']['uncertain_rate']:.1%}.",
           f"- Posiciones: top-1={pos_top1:.1%}; inclusión de etiqueta esperada={pos_inclusion:.1%}; incertidumbre={result['position_focus']['uncertain_rate']:.1%}.",'',
           '## Interpretación permitida',
           'La batería sirve para localizar fallos estructurales y construir casos de regresión antes de la referencia humana. No autoriza elegir parámetros por su efecto en diferencias históricas ni demuestra validez externa.']
    OUT_MD.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
