#!/usr/bin/env python3
"""Synthetic-only evaluation of alternative SEMB scoring functions.

No corpus, RULEA labels, or RULEA patterns are read. Uses the same preregistered
prototype sentences and held-out invented cases to isolate scoring geometry.
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from classify_fragments_B import SentenceTransformer, MODEL_ID, MODEL_REV, ACTION_PROTOTYPES, POSITION_PROTOTYPES

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
POSITION_CASES={
'receiver':'El estudiante únicamente recibe y lee la información que se le presenta.',
'instruction_follower':'El alumno ejecuta una serie de pasos ya establecidos sin elegir el procedimiento.',
'observer':'El estudiante obtiene información mirando sistemáticamente las propiedades del fenómeno.',
'experimenter':'El alumno modifica condiciones y materiales para obtener evidencia experimental.',
'investigator':'El estudiante busca información y evidencia mediante una indagación propia.',
'reasoner':'El alumno debe justificar una conclusión usando datos y relaciones.',
'collaborator':'El estudiante construye la respuesta mediante discusión y trabajo con otras personas.',
'decision_maker':'El alumno compara opciones y toma una decisión fundamentada.',
'community_agent':'El estudiante aplica lo aprendido para intervenir en el cuidado de su comunidad.',
}


def unit(x):
    n=np.linalg.norm(x,axis=-1,keepdims=True)
    return x/np.maximum(n,1e-12)


def build(model,mapping):
    labels=list(mapping)
    flat=[p for label in labels for p in mapping[label]]
    em=model.encode(flat,normalize_embeddings=True,show_progress_bar=False)
    by=np.stack([em[i*2:(i+1)*2] for i in range(len(labels))])
    avg=unit(by.mean(axis=1))
    return labels,by,avg


def score_methods(q,by,avg):
    # 1. baseline averaged normalized category prototypes
    raw_avg=q@avg.T
    # 2. nearest individual prototype, preserving distinct senses instead of averaging
    raw_max=(q[:,None,None,:]*by[None,:,:,:]).sum(axis=-1).max(axis=-1)
    # 3. remove common component defined only by prototype ensemble, then renormalize
    centroid=avg.mean(axis=0)
    q_c=unit(q-centroid)
    avg_c=unit(avg-centroid)
    centered_avg=q_c@avg_c.T
    # 4. center every individual prototype, then nearest prototype
    by_c=unit(by-centroid)
    centered_max=(q_c[:,None,None,:]*by_c[None,:,:,:]).sum(axis=-1).max(axis=-1)
    return {
        'raw_avg':raw_avg,
        'raw_max':raw_max,
        'centered_avg':centered_avg,
        'centered_max':centered_max,
    }


def evaluate(name,model,mapping,cases):
    labels,by,avg=build(model,mapping)
    expected=list(cases)
    q=model.encode(list(cases.values()),normalize_embeddings=True,show_progress_bar=False)
    methods=score_methods(q,by,avg)
    print(f'## {name}')
    for m,s in methods.items():
        top1=0;top3=0;ranks=[];margins=[]
        print('METHOD',m)
        for i,exp in enumerate(expected):
            order=np.argsort(-s[i]); rank=int(np.where(order==labels.index(exp))[0][0])+1
            top1+=rank==1;top3+=rank<=3;ranks.append(rank);margins.append(float(s[i,order[0]]-s[i,order[1]]))
            print(f'  {exp:20s} rank={rank:2d} score={float(s[i,labels.index(exp)]): .6f} top={labels[int(order[0])]:20s} top_score={float(s[i,order[0]]): .6f} margin={margins[-1]:.6f}')
        print('SUMMARY',m,'top1',top1,'/',len(expected),'top3',top3,'/',len(expected),'mean_rank',round(float(np.mean(ranks)),3),'median_rank',float(np.median(ranks)),'mean_top_margin',round(float(np.mean(margins)),6))


def main():
    model=SentenceTransformer(MODEL_ID,revision=MODEL_REV)
    evaluate('actions',model,ACTION_PROTOTYPES,ACTION_CASES)
    evaluate('positions',model,POSITION_PROTOTYPES,POSITION_CASES)

if __name__=='__main__':main()
