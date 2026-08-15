#!/usr/bin/env python3
"""Synthetic-only diagnostic for SEMB_0.1 prototype geometry.

Never reads LTMD corpus/manifests/labels. Reports prototype-prototype cosine
structure and full category rankings for invented held-out action phrases.
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from classify_fragments_B import (
    SentenceTransformer, MODEL_ID, MODEL_REV, ACTION_PROTOTYPES,
    POSITION_PROTOTYPES, prototype_matrix,
)

ACTION_CASES={
    'observe':'Examina con atención las hojas y usa lo que notes para responder.',
    'describe':'Expresa con tus palabras las características que ves en los dos objetos.',
    'recall':'Sin consultar el libro, menciona tres ideas que recuerdes del tema anterior.',
    'explain':'Da una razón que permita comprender por qué cambia este fenómeno.',
    'compare':'Contrasta los dos casos y establece en qué se parecen y en qué son distintos.',
    'classify':'Agrupa los objetos en categorías de acuerdo con una propiedad común.',
    'measure':'Obtén la longitud con una regla y registra el valor numérico.',
    'experiment':'Manipula los materiales, cambia una condición y observa qué resultado se produce.',
    'investigate':'Consulta varias fuentes y reúne evidencia para averiguar la respuesta.',
    'predict':'Antes de hacer la prueba, anticipa qué resultado crees que ocurrirá.',
    'infer':'Usa los datos obtenidos para deducir una conclusión.',
    'discuss':'Intercambia argumentos con tus compañeros y debatan sus puntos de vista.',
    'solve':'Encuentra una solución razonada para la situación problemática planteada.',
    'create':'Diseña y construye una representación que comunique lo aprendido.',
    'decide':'Valora las alternativas, elige una y explica por qué la escogiste.',
    'act_on_environment':'Propón y realiza una acción para cuidar la salud de tu comunidad.',
}


def cosine_matrix(x):
    return x @ x.T


def top_pairs(labels, mat, n=20):
    pairs=[]
    for i in range(len(labels)):
        for j in range(i+1,len(labels)):
            pairs.append((float(mat[i,j]),labels[i],labels[j]))
    return sorted(pairs,reverse=True)[:n]


def describe_space(name, labels, proto):
    mat=cosine_matrix(proto)
    vals=[float(mat[i,j]) for i in range(len(labels)) for j in range(i+1,len(labels))]
    print(f'## {name} prototype geometry')
    print('categories',len(labels),'pair_mean',round(float(np.mean(vals)),6),'pair_median',round(float(np.median(vals)),6),'pair_min',round(min(vals),6),'pair_max',round(max(vals),6))
    print('top confusable pairs:')
    for s,a,b in top_pairs(labels,mat): print(f'{s:.6f}\t{a}\t{b}')


def main():
    model=SentenceTransformer(MODEL_ID,revision=MODEL_REV)
    al,ap=prototype_matrix(model,ACTION_PROTOTYPES)
    pl,pp=prototype_matrix(model,POSITION_PROTOTYPES)
    describe_space('actions',al,ap)
    describe_space('positions',pl,pp)

    print('## held-out action rankings')
    texts=list(ACTION_CASES.values())
    emb=model.encode(texts,normalize_embeddings=True,show_progress_bar=False)
    scores=emb @ ap.T
    correct_top1=0; correct_top3=0
    for row,(expected,text) in enumerate(ACTION_CASES.items()):
        order=np.argsort(-scores[row])
        ranked=[(al[int(i)],float(scores[row,int(i)])) for i in order]
        rank=next(i+1 for i,(lab,_) in enumerate(ranked) if lab==expected)
        if rank==1: correct_top1+=1
        if rank<=3: correct_top3+=1
        print(f'CASE expected={expected} expected_rank={rank} expected_score={dict(ranked)[expected]:.6f}')
        for lab,s in ranked[:8]: print(f'  {lab:20s} {s:.6f}')
    print('top1_accuracy',correct_top1,'/',len(ACTION_CASES),round(correct_top1/len(ACTION_CASES),4))
    print('top3_accuracy',correct_top3,'/',len(ACTION_CASES),round(correct_top3/len(ACTION_CASES),4))

    # Generic educational instructions diagnose common-mode similarity.
    generic=[
        'Realiza la actividad indicada y responde lo que se solicita.',
        'Lee la consigna y cumple la tarea de acuerdo con las instrucciones.',
        'Trabaja con la información y completa el ejercicio solicitado.',
    ]
    ge=model.encode(generic,normalize_embeddings=True,show_progress_bar=False)
    gs=ge @ ap.T
    print('## generic educational instruction scores')
    for i,text in enumerate(generic):
        order=np.argsort(-gs[i])
        print('GENERIC',text)
        for j in order[:8]: print(f'  {al[int(j)]:20s} {float(gs[i,int(j)]):.6f}')

if __name__=='__main__': main()
