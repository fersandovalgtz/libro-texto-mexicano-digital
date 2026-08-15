#!/usr/bin/env python3
"""Shared synthetic/production core for SEMB_0.2.

The semantic architecture is fixed by the preregistered development protocol.
The only learned/selected values loaded from disk are the synthetic-development
`selected_method` and action-gate threshold. This module never reads RULEA.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL='intfloat/multilingual-e5-small'
REV='fd1525a9fd15316a2d503bf26ab031a61d056e98'
CONFIG_PATH=Path('data/derived/semantic_B02_development_result.json')
VERSION='SEMB_0.2'

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

MULTILABEL_BAND=0.02
UNCERTAIN_TOP_MARGIN=0.01
UNCERTAIN_GATE_BUFFER=0.02
MAX_ACTION_LABELS=3
MAX_POSITION_LABELS=2


def pref(s:str)->str:
    return 'query: '+s


def unit(x):
    n=np.linalg.norm(x,axis=-1,keepdims=True)
    return x/np.maximum(n,1e-12)


def load_config(path:Path=CONFIG_PATH):
    d=json.load(path.open(encoding='utf-8'))
    assert d['development_version']=='SEMB02_DEV_0.1'
    assert d['model']==MODEL and d['model_revision']==REV
    assert d['selected_method'] in {'average_anchor','max_anchor'}
    assert d['validation_B02_opened'] is False
    return d


def embed(model,texts):
    return model.encode([pref(x) for x in texts],normalize_embeddings=True,show_progress_bar=False,batch_size=64)


def build_anchor_space(model,mapping):
    labels=list(mapping)
    flat=[x for lab in labels for x in mapping[lab]]
    e=embed(model,flat).reshape(len(labels),3,-1)
    avg=unit(e.mean(axis=1))
    return labels,e,avg


def category_scores(q,e,avg,method):
    if method=='average_anchor':
        return q@avg.T
    if method=='max_anchor':
        return (q[:,None,None,:]*e[None,:,:,:]).sum(axis=-1).max(axis=-1)
    raise ValueError(method)


def rank_expected(labels,scores,expected):
    order=np.argsort(-scores)
    idx=labels.index(expected)
    rank=int(np.where(order==idx)[0][0])+1
    return rank,[(labels[int(i)],float(scores[int(i)])) for i in order]


def choose_category_labels(labels,scores,max_labels):
    order=np.argsort(-scores)
    top=float(scores[int(order[0])])
    second=float(scores[int(order[1])]) if len(order)>1 else top
    margin=top-second
    chosen=[]
    for idx in order:
        s=float(scores[int(idx)])
        if not chosen or s>=top-MULTILABEL_BAND:
            chosen.append(labels[int(idx)])
        if len(chosen)>=max_labels:
            break
    uncertain=int(margin < UNCERTAIN_TOP_MARGIN)
    return chosen,uncertain,top,second,margin


class SemanticB02:
    def __init__(self, config_path:Path=CONFIG_PATH):
        self.config=load_config(config_path)
        self.method=self.config['selected_method']
        self.gate_threshold=float(self.config['action_gate']['selected_threshold'])
        self.model=SentenceTransformer(MODEL,revision=REV)
        self.action_labels,self.action_e,self.action_avg=build_anchor_space(self.model,ACTION_ANCHORS)
        self.position_labels,self.position_e,self.position_avg=build_anchor_space(self.model,POSITION_ANCHORS)
        self.gate_pos=embed(self.model,ACTION_GATE_POS)
        self.gate_neg=embed(self.model,ACTION_GATE_NEG)

    def embed_texts(self,texts):
        return embed(self.model,texts)

    def action_gate_margin(self,q):
        q2=q if q.ndim==2 else q[None,:]
        margins=(q2@self.gate_pos.T).max(axis=1)-(q2@self.gate_neg.T).max(axis=1)
        return margins

    def action_scores(self,q):
        q2=q if q.ndim==2 else q[None,:]
        return category_scores(q2,self.action_e,self.action_avg,self.method)

    def position_scores(self,q):
        q2=q if q.ndim==2 else q[None,:]
        return category_scores(q2,self.position_e,self.position_avg,self.method)

    def select_actions(self,q,skip=False):
        if skip:
            return {'labels':[],'uncertain':1,'gate_margin':None,'top':None,'second':None,'margin':None,'scores':None}
        gate=float(self.action_gate_margin(q)[0])
        scores=self.action_scores(q)[0]
        if gate < self.gate_threshold:
            order=np.argsort(-scores)
            top=float(scores[int(order[0])]);second=float(scores[int(order[1])])
            return {'labels':[],'uncertain':1,'gate_margin':gate,'top':top,'second':second,'margin':top-second,'scores':scores}
        labels,unc,top,second,margin=choose_category_labels(self.action_labels,scores,MAX_ACTION_LABELS)
        if gate < self.gate_threshold+UNCERTAIN_GATE_BUFFER:
            unc=1
        return {'labels':labels,'uncertain':unc,'gate_margin':gate,'top':top,'second':second,'margin':margin,'scores':scores}

    def select_positions(self,q,skip=False):
        if skip:
            return {'labels':[],'uncertain':1,'top':None,'second':None,'margin':None,'scores':None}
        scores=self.position_scores(q)[0]
        labels,unc,top,second,margin=choose_category_labels(self.position_labels,scores,MAX_POSITION_LABELS)
        return {'labels':labels,'uncertain':unc,'top':top,'second':second,'margin':margin,'scores':scores}
