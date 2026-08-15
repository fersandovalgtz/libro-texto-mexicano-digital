#!/usr/bin/env python3
"""Develop a provisional SEMB 0.3 actionability gate using synthetic data only.

This script is deliberately barred from corpus labels/history. It compares:
1) the frozen SEMB 0.2 gate at threshold 0;
2) a fold-tuned threshold on the existing gate margin;
3) a low-dimensional logistic gate over frozen semantic similarity features.

Performance is estimated with deterministic stratified 5-fold CV. The final fitted
candidate is a DEVELOPMENT ARTIFACT, not a validated production model.
"""
from __future__ import annotations
import csv,json
from pathlib import Path
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score,recall_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from semantic_classifier_B02_core import SemanticB02

CASES=Path('data/validation/semb03_synthetic_stress_cases.csv')
OUT=Path('data/derived/semb03_gate_synthetic_development.json')
REPORT=Path('data/derived/semb03_gate_synthetic_development.md')
VERSION='SEMB03_GATE_SYNTH_DEV_0.1'
FEATURES=('gate_pos_max','gate_neg_max','gate_margin','action_top','action_second','action_margin','position_top','position_second','position_margin','receiver_score','instruction_follower_score','reasoner_score')

def metrics(y,p):
    return {'balanced_accuracy':float(balanced_accuracy_score(y,p)),
            'sensitivity':float(recall_score(y,p,pos_label=1)),
            'specificity':float(recall_score(y,p,pos_label=0))}

def best_threshold(m,y,idx):
    best=None
    for t in np.arange(-0.05,0.0501,0.001):
        score=balanced_accuracy_score(y[idx],(m[idx]>=t).astype(int))
        cand=(score,-abs(t),float(t))
        if best is None or cand>best:best=cand
    return best[2]

def main():
    rows=list(csv.DictReader(CASES.open(encoding='utf-8')))
    rows=[r for r in rows if r['expected_actionable'] in {'0','1'}]
    assert len(rows)==105
    y=np.array([int(r['expected_actionable']) for r in rows],dtype=int)
    eng=SemanticB02();q=eng.embed_texts([r['text'] for r in rows])
    gate_pos=(q@eng.gate_pos.T).max(axis=1);gate_neg=(q@eng.gate_neg.T).max(axis=1);gm=gate_pos-gate_neg
    a=eng.action_scores(q);p=eng.position_scores(q)
    ao=np.sort(a,axis=1)[:,-2:];po=np.sort(p,axis=1)[:,-2:]
    pi={lab:i for i,lab in enumerate(eng.position_labels)}
    X=np.column_stack([gate_pos,gate_neg,gm,ao[:,-1],ao[:,-2],ao[:,-1]-ao[:,-2],po[:,-1],po[:,-2],po[:,-1]-po[:,-2],p[:,pi['receiver']],p[:,pi['instruction_follower']],p[:,pi['reasoner']]])
    assert X.shape==(105,len(FEATURES))

    frozen=(gm>=0).astype(int)
    skf=StratifiedKFold(n_splits=5,shuffle=True,random_state=20260815)
    tuned=np.zeros_like(y);logp=np.zeros_like(y);fold_thresholds=[]
    for train,test in skf.split(X,y):
        t=best_threshold(gm,y,train);fold_thresholds.append(t);tuned[test]=(gm[test]>=t).astype(int)
        model=make_pipeline(StandardScaler(),LogisticRegression(C=0.5,class_weight='balanced',solver='liblinear',random_state=20260815,max_iter=2000))
        model.fit(X[train],y[train]);logp[test]=model.predict(X[test])

    # Fit full synthetic candidate for later evaluation on human DEVELOPMENT only.
    full=make_pipeline(StandardScaler(),LogisticRegression(C=0.5,class_weight='balanced',solver='liblinear',random_state=20260815,max_iter=2000))
    full.fit(X,y);sc=full.named_steps['standardscaler'];lr=full.named_steps['logisticregression']
    final_threshold=best_threshold(gm,y,np.arange(len(y)))
    result={'development_version':VERSION,'synthetic_suite_version':'SEMB03_SYNTH_STRESS_0.1','n':len(y),'positive_n':int(y.sum()),'negative_n':int((1-y).sum()),
            'corpus_accessed':False,'historical_outputs_accessed':False,'human_reference_accessed':False,
            'feature_names':list(FEATURES),
            'frozen_B02_gate_cv_equivalent':metrics(y,frozen),
            'fold_tuned_margin_cv':{**metrics(y,tuned),'fold_thresholds':fold_thresholds,'full_synthetic_selected_threshold':final_threshold},
            'logistic_semantic_features_cv':metrics(y,logp),
            'provisional_full_fit':{'standardizer_mean':sc.mean_.tolist(),'standardizer_scale':sc.scale_.tolist(),'coef':lr.coef_[0].tolist(),'intercept':float(lr.intercept_[0]),'C':0.5,'class_weight':'balanced'},
            'status':'PROVISIONAL_SYNTHETIC_ONLY','allowed_next_use':'Evaluate/retune on the 320-case human DEVELOPMENT reference when available; never promote directly to production.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);json.dump(result,OUT.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    lines=['# Desarrollo sintético del gate SEMB 0.3','',f'Versión: `{VERSION}`. n={len(y)} casos sintéticos; positivos={int(y.sum())}; negativos={int((1-y).sum())}.','',
           '> Este artefacto NO es validación humana ni autoriza producción. Sirve para decidir si hay arquitecturas plausibles que llevar al conjunto humano de desarrollo.','',
           '## Validación cruzada estratificada de 5 folds']
    for name,key in [('SEMB 0.2, gate congelado','frozen_B02_gate_cv_equivalent'),('Margen con threshold seleccionado sólo en train de cada fold','fold_tuned_margin_cv'),('Regresión logística sobre rasgos semánticos','logistic_semantic_features_cv')]:
        m=result[key];lines.append(f"- **{name}:** balanced accuracy={m['balanced_accuracy']:.3f}; sensibilidad={m['sensitivity']:.3f}; especificidad={m['specificity']:.3f}.")
    lines += ['',f"Threshold de margen ajustado sobre todos los sintéticos, sólo como candidato para desarrollo humano posterior: **{final_threshold:.3f}**.",'',
              '## Regla de uso','La arquitectura logística y el threshold sintético pueden entrar como candidatos en G3, pero deberán compararse y calibrarse nuevamente usando exclusivamente los 320 casos humanos `development`. Ningún resultado histórico interviene en esta selección.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
