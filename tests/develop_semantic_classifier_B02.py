#!/usr/bin/env python3
"""Synthetic development for SEMB_0.2 using multilingual E5.

Never reads LTMD corpus, FRAGSEG manifest, RULEA outputs, or RULEA patterns.
Chooses scoring method and actionness threshold using only preregistered dev data.
Also writes a machine-readable synthetic development result so the selected
configuration does not depend on ephemeral CI logs.
"""
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL='intfloat/multilingual-e5-small'
REV='fd1525a9fd15316a2d503bf26ab031a61d056e98'
RESULT_PATH=Path('data/derived/semantic_B02_development_result.json')

ACTION_ANCHORS={
'observe':['observación visual detallada','examinar propiedades con atención','mirar cambios y objetos cuidadosamente'],
'describe':['describir características','expresar propiedades observadas','decir cómo es algo'],
'recall':['recordar información aprendida','recuperar conocimiento de la memoria','mencionar lo aprendido anteriormente'],
'explain':['explicar causas y mecanismos','dar razones de por qué ocurre algo','justificar cómo funciona un fenómeno'],
'compare':['comparar semejanzas y diferencias','contrastar dos casos','establecer relaciones entre elementos'],
'classify':['clasificar por criterios','agrupar según propiedades','organizar elementos en categorías'],
'measure':['medir una magnitud','obtener una medida numérica','usar un instrumento para medir'],
'experiment':['experimentar manipulando condiciones','cambiar variables y observar resultados','realizar una prueba con materiales'],
'investigate':['investigar en fuentes','buscar y reunir evidencia','indagar para responder una pregunta'],
'predict':['predecir antes de comprobar','anticipar un resultado','decir qué ocurrirá antes de observarlo'],
'infer':['inferir desde evidencias','deducir una conclusión','concluir a partir de datos'],
'discuss':['discutir ideas con otros','debatir argumentos','intercambiar puntos de vista'],
'solve':['resolver un problema','encontrar una solución','obtener una respuesta mediante razonamiento'],
'create':['crear un producto o representación','diseñar y construir algo','elaborar un modelo dibujo o cartel'],
'decide':['tomar una decisión','elegir entre alternativas','valorar opciones y escoger una'],
'act_on_environment':['actuar para cuidar salud o ambiente','intervenir en familia escuela o comunidad','realizar una acción de prevención o cuidado'],
}
POSITION_ANCHORS={
'receiver':['recibir información sin tarea','leer contenido expositivo','atender a información presentada'],
'instruction_follower':['seguir pasos predeterminados','ejecutar instrucciones prescritas','cumplir una secuencia definida'],
'observer':['papel de observador','obtener datos mediante observación','mirar sistemáticamente fenómenos'],
'experimenter':['papel de experimentador','manipular condiciones para obtener evidencia','realizar experimentos'],
'investigator':['papel de investigador','buscar evidencia mediante indagación','investigar con cierto margen de decisión'],
'reasoner':['razonar con datos y relaciones','construir una respuesta razonada','explicar inferir comparar o resolver'],
'collaborator':['colaborar con otras personas','trabajar mediante interacción sustantiva','discutir y construir en grupo'],
'decision_maker':['tomar decisiones informadas','elegir después de valorar alternativas','papel de decisor'],
'community_agent':['actuar en comunidad o ambiente','aplicar conocimiento fuera de la tarea escolar','agente de cuidado prevención o transformación'],
}
ACTION_GATE_POS=['instrucción que pide realizar una operación','consigna dirigida que solicita hacer algo','pregunta o tarea que exige una acción o respuesta']
ACTION_GATE_NEG=['texto expositivo sin consigna','información presentada sin pedir una acción','afirmación descriptiva destinada solamente a ser leída']

ACTION_DEV={
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
POSITION_DEV={
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
NEG_DEV=[
'La Tierra gira alrededor del Sol y completa una órbita en un periodo determinado.',
'El termómetro es un instrumento utilizado para conocer la temperatura.',
'Las plantas necesitan agua y luz para realizar diversos procesos vitales.',
'Una hipótesis es una explicación provisional que puede ponerse a prueba.',
'Los materiales presentan propiedades físicas diferentes.',
'La observación científica permite obtener información de los fenómenos.',
'Un modelo es una representación simplificada de un objeto o proceso.',
'La prevención ayuda a disminuir algunos riesgos para la salud.',
]


def pref(s): return 'query: '+s

def unit(x):
    n=np.linalg.norm(x,axis=-1,keepdims=True)
    return x/np.maximum(n,1e-12)

def embed(model,texts):
    return model.encode([pref(x) for x in texts],normalize_embeddings=True,show_progress_bar=False,batch_size=64)

def build(model,mapping):
    labels=list(mapping)
    flat=[x for lab in labels for x in mapping[lab]]
    e=embed(model,flat).reshape(len(labels),3,-1)
    avg=unit(e.mean(axis=1))
    return labels,e,avg

def scores(q,e,avg,method):
    if method=='average_anchor': return q@avg.T
    if method=='max_anchor': return (q[:,None,None,:]*e[None,:,:,:]).sum(axis=-1).max(axis=-1)
    raise ValueError(method)

def metrics(labels,s,expected,verbose=True):
    top1=top3=0;ranks=[];worst=0
    details=[]
    for i,exp in enumerate(expected):
        order=np.argsort(-s[i]);rank=int(np.where(order==labels.index(exp))[0][0])+1
        ranks.append(rank);worst=max(worst,rank);top1+=rank==1;top3+=rank<=3
        detail={
            'expected':exp,'rank':rank,'expected_score':round(float(s[i,labels.index(exp)]),6),
            'top_label':labels[int(order[0])],'top_score':round(float(s[i,order[0]]),6),
            'top_margin':round(float(s[i,order[0]]-s[i,order[1]]),6),
        }
        details.append(detail)
        if verbose:
            print(f"  expected={exp:20s} rank={rank:2d} expected_score={detail['expected_score']:.6f} top={detail['top_label']:20s} top_score={detail['top_score']:.6f} margin={detail['top_margin']:.6f}")
    summary={'top1':top1,'top3':top3,'mean_rank':float(np.mean(ranks)),'worst':worst}
    return summary,details

def balanced_accuracy(pos_margins,neg_margins,threshold):
    tp=sum(x>=threshold for x in pos_margins);fn=len(pos_margins)-tp
    tn=sum(x<threshold for x in neg_margins);fp=len(neg_margins)-tn
    sens=tp/len(pos_margins);spec=tn/len(neg_margins)
    return (sens+spec)/2,sens,spec,tp,tn

def main():
    model=SentenceTransformer(MODEL,revision=REV)
    al,ae,aavg=build(model,ACTION_ANCHORS)
    pl,pe,pavg=build(model,POSITION_ANCHORS)
    aq=embed(model,list(ACTION_DEV.values()));pq=embed(model,list(POSITION_DEV.values()))
    method_results={}; method_details={}
    for method in ['average_anchor','max_anchor']:
        print('## METHOD',method,'ACTIONS')
        am,ad=metrics(al,scores(aq,ae,aavg,method),list(ACTION_DEV))
        print('ACTION SUMMARY',am)
        print('## METHOD',method,'POSITIONS')
        pm,pd=metrics(pl,scores(pq,pe,pavg,method),list(POSITION_DEV))
        print('POSITION SUMMARY',pm)
        method_results[method]=(am,pm); method_details[method]={'actions':ad,'positions':pd}
    def key(m):
        a,p=method_results[m]
        return (a['top1']+p['top1'],a['top3']+p['top3'],-(a['mean_rank']+p['mean_rank']),-(a['worst']+p['worst']),1 if m=='max_anchor' else 0)
    chosen=max(method_results,key=key)
    print('CHOSEN_METHOD',chosen,'key',key(chosen))

    pos_gate=embed(model,ACTION_GATE_POS);neg_gate=embed(model,ACTION_GATE_NEG)
    posq=embed(model,list(ACTION_DEV.values()));negq=embed(model,NEG_DEV)
    def gate_margin(q):
        return (q@pos_gate.T).max(axis=1)-(q@neg_gate.T).max(axis=1)
    pm=gate_margin(posq);nm=gate_margin(negq)
    print('POS_GATE_MARGINS',','.join(f'{x:.6f}' for x in pm))
    print('NEG_GATE_MARGINS',','.join(f'{x:.6f}' for x in nm))
    candidates=[]; gate_rows=[]
    for th in [0.00,0.02,0.04,0.06]:
        ba,sens,spec,tp,tn=balanced_accuracy(pm,nm,th)
        candidates.append((ba,spec,th,sens,tp,tn))
        gate_rows.append({'threshold':th,'balanced_accuracy':ba,'sensitivity':sens,'specificity':spec,'tp':tp,'tn':tn})
        print('GATE',th,'balanced_accuracy',round(ba,6),'sensitivity',round(sens,6),'specificity',round(spec,6),'tp',tp,'tn',tn)
    best=max(candidates,key=lambda x:(x[0],x[1],x[2]))
    print('CHOSEN_GATE_THRESHOLD',best[2],'balanced_accuracy',best[0],'sensitivity',best[3],'specificity',best[1])

    result={
        'development_version':'SEMB02_DEV_0.1',
        'model':MODEL,'model_revision':REV,'e5_prefix':'query: ',
        'selected_method':chosen,
        'selection_key':list(key(chosen)),
        'method_metrics':{m:{'actions':method_results[m][0],'positions':method_results[m][1]} for m in method_results},
        'selected_method_details':method_details[chosen],
        'action_gate':{
            'selected_threshold':best[2],
            'balanced_accuracy':best[0],
            'sensitivity':best[3],
            'specificity':best[1],
            'positive_margins':[round(float(x),6) for x in pm],
            'negative_margins':[round(float(x),6) for x in nm],
            'grid':gate_rows,
        },
        'fixed_multilabel_band':0.02,
        'fixed_uncertainty_top_margin':0.01,
        'fixed_uncertainty_gate_buffer':0.02,
        'max_action_labels':3,
        'max_position_labels':2,
        'validation_B02_opened':False,
    }
    RESULT_PATH.parent.mkdir(parents=True,exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('WROTE_RESULT',RESULT_PATH)

if __name__=='__main__': main()
