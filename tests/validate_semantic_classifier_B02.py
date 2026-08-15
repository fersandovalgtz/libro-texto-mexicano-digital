#!/usr/bin/env python3
"""One-shot locked validation for SEMB_0.2.

The phrases and acceptance criteria were preregistered before E5 development.
This script MUST NOT read LTMD corpus text or RULEA outputs. Configuration comes
only from the versioned synthetic development result.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from semantic_classifier_B02_core import SemanticB02, rank_expected, VERSION

OUT=Path('data/derived/semantic_B02_validation_result.json')

ACTION_VALID={
'observe':'Mira cuidadosamente los cambios que ocurren y anota lo que puedas notar.',
'describe':'Indica cómo es cada muestra y cuáles son sus características visibles.',
'recall':'Sin revisar tus apuntes, escribe dos conceptos que aprendiste en la clase pasada.',
'explain':'Señala la causa del cambio y explica cómo se produce.',
'compare':'Establece una semejanza y una diferencia entre las dos situaciones.',
'classify':'Ordena los ejemplos en grupos usando una propiedad como criterio.',
'measure':'Usa la balanza para obtener la masa y registra el valor.',
'experiment':'Cambia la cantidad de agua, mantén lo demás igual y observa el resultado.',
'investigate':'Averigua en distintas fuentes qué información permite responder la pregunta.',
'predict':'Antes de iniciar la actividad, escribe qué esperas que suceda.',
'infer':'A partir de los datos de la tabla, deduce qué conclusión puede sostenerse.',
'discuss':'Conversa con tu equipo, contrasta sus argumentos y lleguen a una postura.',
'solve':'Determina cómo resolver la situación planteada y encuentra una respuesta.',
'create':'Construye un modelo que represente el fenómeno estudiado.',
'decide':'Escoge la alternativa más conveniente después de valorar sus consecuencias.',
'act_on_environment':'Organiza con tu familia una acción concreta para reducir un riesgo de salud.',
}
POSITION_VALID={
'receiver':'El estudiante solamente lee información ya explicada y no recibe una tarea adicional.',
'instruction_follower':'El estudiante ejecuta exactamente una secuencia de pasos ya determinada.',
'observer':'El alumno obtiene datos al mirar de manera sistemática lo que sucede.',
'experimenter':'El estudiante modifica una condición de una prueba y obtiene evidencia.',
'investigator':'El alumno reúne información de diversas fuentes para responder una cuestión.',
'reasoner':'El estudiante usa datos y relaciones para justificar una conclusión.',
'collaborator':'El alumno necesita intercambiar ideas y construir la respuesta con otras personas.',
'decision_maker':'El estudiante evalúa opciones y elige una alternativa de manera fundamentada.',
'community_agent':'El alumno lleva el aprendizaje a una acción concreta en su comunidad.',
}
NEG_VALID=[
'El agua puede encontrarse en estado sólido, líquido o gaseoso.',
'Los mamíferos presentan características que permiten distinguirlos de otros animales.',
'La temperatura puede medirse con un termómetro.',
'Un experimento científico permite estudiar relaciones entre fenómenos.',
'Las diferencias entre materiales dependen de sus propiedades.',
'La comunidad está formada por personas que comparten un espacio.',
'Un cartel puede utilizarse para comunicar información.',
'La observación es una herramienta importante en el estudio de la naturaleza.',
]


def ranking_rows(engine, family, mapping):
    texts=list(mapping.values())
    q=engine.embed_texts(texts)
    if family=='actions':
        labels=engine.action_labels; score_matrix=engine.action_scores(q)
    else:
        labels=engine.position_labels; score_matrix=engine.position_scores(q)
    rows=[];top1=0;top3=0;worst=0
    for i,expected in enumerate(mapping):
        rank,ranked=rank_expected(labels,score_matrix[i],expected)
        top1+=rank==1;top3+=rank<=3;worst=max(worst,rank)
        rows.append({
            'expected':expected,'rank':rank,
            'expected_score':round(dict(ranked)[expected],6),
            'top_label':ranked[0][0],'top_score':round(ranked[0][1],6),
            'top3':[{'label':lab,'score':round(score,6)} for lab,score in ranked[:3]],
        })
    return rows,{'top1':top1,'top3':top3,'worst_rank':worst,'n':len(mapping)}


def main():
    engine=SemanticB02()
    action_rows,am=ranking_rows(engine,'actions',ACTION_VALID)
    position_rows,pm=ranking_rows(engine,'positions',POSITION_VALID)

    neg_embeddings=engine.embed_texts(NEG_VALID)
    neg_rows=[];neg_correct=0
    for text,q in zip(NEG_VALID,neg_embeddings):
        sel=engine.select_actions(q,skip=False)
        correct=(len(sel['labels'])==0 or int(sel['uncertain'])==1)
        neg_correct+=int(correct)
        neg_rows.append({
            'text_sha256':__import__('hashlib').sha256(text.encode('utf-8')).hexdigest(),
            'label_count':len(sel['labels']),'labels':sel['labels'],'uncertain':int(sel['uncertain']),
            'gate_margin':None if sel['gate_margin'] is None else round(float(sel['gate_margin']),6),
            'correct_abstain_or_uncertain':bool(correct),
        })

    checks={
        'actions_top1_ge_12_of_16':am['top1']>=12,
        'actions_top3_ge_15_of_16':am['top3']>=15,
        'actions_worst_rank_le_4':am['worst_rank']<=4,
        'negative_abstain_or_uncertain_ge_7_of_8':neg_correct>=7,
        'positions_top1_ge_7_of_9':pm['top1']>=7,
        'positions_top3_eq_9_of_9':pm['top3']==9,
        'positions_worst_rank_le_3':pm['worst_rank']<=3,
    }
    passed=all(checks.values())
    result={
        'validation_version':'VALIDATION_B02_LOCKED_0.1',
        'semantic_version':VERSION,
        'model':engine.config['model'],'model_revision':engine.config['model_revision'],
        'selected_method':engine.method,'action_gate_threshold':engine.gate_threshold,
        'action_metrics':am,'position_metrics':pm,'negative_correct':neg_correct,'negative_n':len(NEG_VALID),
        'checks':checks,'passed':passed,
        'action_cases':action_rows,'position_cases':position_rows,'negative_cases':neg_rows,
        'corpus_accessed':False,'ruleA_accessed':False,
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not passed:
        raise SystemExit('VALIDATION_B02 FAILED: frozen acceptance criteria not met')
    print('VALIDATION_B02 PASSED')

if __name__=='__main__':main()
