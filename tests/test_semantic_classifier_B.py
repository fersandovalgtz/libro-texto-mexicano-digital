#!/usr/bin/env python3
"""Synthetic semantic preflight for SEMB_0.1.

No LTMD corpus text is used. Tests the pinned model, prototype construction and
preregistered decision function on invented held-out phrases.
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from classify_fragments_B import (
    SentenceTransformer, MODEL_ID, MODEL_REV, ACTION_PROTOTYPES, POSITION_PROTOTYPES,
    prototype_matrix, select_labels,
)


def classify(model, labels, proto, text):
    e=model.encode([text],normalize_embeddings=True,show_progress_bar=False)[0]
    scores=e @ proto.T
    chosen,unc,top,second,margin=select_labels(labels,scores,skip=False)
    order=np.argsort(-scores)
    ranked=[(labels[int(i)],float(scores[int(i)])) for i in order[:5]]
    return chosen,unc,top,second,margin,ranked


def expect_contains(result,label,text):
    chosen,unc,top,second,margin,ranked=result
    assert label in chosen, (text,label,chosen,unc,top,second,margin,ranked)


def main():
    model=SentenceTransformer(MODEL_ID,revision=MODEL_REV)
    al,ap=prototype_matrix(model,ACTION_PROTOTYPES)
    pl,pp=prototype_matrix(model,POSITION_PROTOTYPES)

    action_cases={
        'observe':'Examina con atención las hojas y usa lo que notes para responder.',
        'explain':'Da una razón que permita comprender por qué cambia este fenómeno.',
        'compare':'Contrasta los dos casos y establece en qué se parecen y en qué son distintos.',
        'experiment':'Manipula los materiales, cambia una condición y observa qué resultado se produce.',
        'investigate':'Consulta varias fuentes y reúne evidencia para averiguar la respuesta.',
        'predict':'Antes de hacer la prueba, anticipa qué resultado crees que ocurrirá.',
        'infer':'Usa los datos obtenidos para deducir una conclusión.',
        'discuss':'Intercambia argumentos con tus compañeros y debatan sus puntos de vista.',
        'create':'Diseña y construye una representación que comunique lo aprendido.',
        'decide':'Valora las alternativas, elige una y explica por qué la escogiste.',
        'act_on_environment':'Propón y realiza una acción para cuidar la salud de tu comunidad.',
    }
    for label,text in action_cases.items():
        expect_contains(classify(model,al,ap,text),label,text)

    position_cases={
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
    for label,text in position_cases.items():
        expect_contains(classify(model,pl,pp,text),label,text)

    # Short/heading fragments are explicitly skipped by policy regardless of model score.
    chosen,unc,*_=select_labels(al,np.ones(len(al)),skip=True)
    assert chosen==[] and unc==1

    print('SEMB synthetic preflight: OK')

if __name__=='__main__':main()
