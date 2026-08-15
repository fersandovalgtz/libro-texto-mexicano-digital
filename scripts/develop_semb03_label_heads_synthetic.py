#!/usr/bin/env python3
"""Synthetic-only diagnosis of SEMB label heads.

For each action/position there are exactly three clear synthetic examples. A
3-fold leave-one-example-per-label design trains class centroids on two examples
per label and tests the third. This asks whether the frozen embedding space is
more separable than the current hand-written anchors suggest. No corpus or human
reference is accessed.
"""
from __future__ import annotations
import csv,json
from collections import defaultdict
from pathlib import Path
import numpy as np

from semantic_classifier_B02_core import SemanticB02,unit

CASES=Path('data/validation/semb03_synthetic_stress_cases.csv')
OUT=Path('data/derived/semb03_label_heads_synthetic_development.json')
REPORT=Path('data/derived/semb03_label_heads_synthetic_development.md')
VERSION='SEMB03_LABEL_HEADS_SYNTH_DEV_0.1'

def one(s):
    x=[v for v in (s or '').split(';') if v]
    if len(x)!=1:raise ValueError(s)
    return x[0]

def eval_focus(rows,focus,labels,engine,emb):
    rr=[(i,r) for i,r in enumerate(rows) if r['focus']==focus]
    grouped=defaultdict(list)
    field='expected_action_labels' if focus=='action' else 'expected_position_labels'
    for i,r in rr:grouped[one(r[field])].append(i)
    assert set(grouped)==set(labels) and all(len(v)==3 for v in grouped.values())
    # Frozen head top-1 on all clear examples.
    scores=engine.action_scores(emb) if focus=='action' else engine.position_scores(emb)
    frozen=[]
    for i,r in rr:frozen.append(labels[int(np.argmax(scores[i]))]==one(r[field]))
    # 3 folds: for every category, hold out its kth example and form centroid from other two.
    proto_correct=[];hybrid_correct=[]
    fixed_avg=engine.action_avg if focus=='action' else engine.position_avg
    for k in range(3):
        protos=[];tests=[]
        for lab in labels:
            ids=grouped[lab];train=[ids[j] for j in range(3) if j!=k];test=ids[k]
            protos.append(unit(emb[train].mean(axis=0)))
            tests.append((test,lab))
        proto=np.stack(protos)
        hybrid=unit((proto+fixed_avg)/2)
        for i,lab in tests:
            proto_correct.append(labels[int(np.argmax(emb[i]@proto.T))]==lab)
            hybrid_correct.append(labels[int(np.argmax(emb[i]@hybrid.T))]==lab)
    # Full synthetic centroids are a provisional artifact for later human-development comparison only.
    full=np.stack([unit(emb[grouped[lab]].mean(axis=0)) for lab in labels])
    return {'n':len(rr),'frozen_anchor_top1':sum(frozen)/len(frozen),'synthetic_centroid_cv_top1':sum(proto_correct)/len(proto_correct),
            'hybrid_anchor_centroid_cv_top1':sum(hybrid_correct)/len(hybrid_correct),
            'full_synthetic_centroid_norms':[float(np.linalg.norm(x)) for x in full]}

def main():
    rows=list(csv.DictReader(CASES.open(encoding='utf-8')));assert len(rows)==105
    eng=SemanticB02();emb=eng.embed_texts([r['text'] for r in rows])
    actions=eval_focus(rows,'action',eng.action_labels,eng,emb)
    positions=eval_focus(rows,'position',eng.position_labels,eng,emb)
    result={'development_version':VERSION,'suite_version':'SEMB03_SYNTH_STRESS_0.1','semantic_model':eng.model.__class__.__name__,
            'corpus_accessed':False,'historical_outputs_accessed':False,'human_reference_accessed':False,
            'actions':actions,'positions':positions,'status':'PROVISIONAL_SYNTHETIC_ONLY'}
    OUT.parent.mkdir(parents=True,exist_ok=True);json.dump(result,OUT.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    lines=['# Diagnóstico sintético de cabezales semánticos SEMB 0.3','',f'Versión: `{VERSION}`. Diseño: tres folds, reteniendo un ejemplo por categoría en cada fold.','',
           '> No es validación humana. Evalúa separabilidad del espacio semántico y calidad relativa de los anchors sobre casos sintéticos claros.','',
           '## Acciones',f"- Anchors congelados SEMB 0.2, top-1: **{actions['frozen_anchor_top1']:.1%}**.",f"- Centroides aprendidos con 2 ejemplos/categoría, CV: **{actions['synthetic_centroid_cv_top1']:.1%}**.",f"- Híbrido anchor+centroide, CV: **{actions['hybrid_anchor_centroid_cv_top1']:.1%}**.",'',
           '## Posiciones',f"- Anchors congelados SEMB 0.2, top-1: **{positions['frozen_anchor_top1']:.1%}**.",f"- Centroides aprendidos con 2 ejemplos/categoría, CV: **{positions['synthetic_centroid_cv_top1']:.1%}**.",f"- Híbrido anchor+centroide, CV: **{positions['hybrid_anchor_centroid_cv_top1']:.1%}**.",'',
           '## Uso','Si los centroides superan claramente los anchors, la representación E5 conserva señal útil y SEMB 0.3 debe considerar cabezales supervisados/prototípicos. Si no mejoran, conviene evaluar una representación/modelo distinto en el conjunto humano de desarrollo.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
