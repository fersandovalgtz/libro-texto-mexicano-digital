#!/usr/bin/env python3
"""Independent semantic classifier B for LTMD fragments.

Uses a pinned multilingual SentenceTransformer model plus preregistered synthetic
prototype sentences. Reconstructs text ephemerally, verifies SHA-256 against the
frozen fragment manifest, and emits scores/labels only. It never reads RULEA
outputs and never persists source/fragment text or embeddings.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import tempfile
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from segment_fragments import (
    SOURCE_CODES, ELIGIBLE, run_tesseract, read_tsv, reconstruct_paragraphs,
    sentence_units, merge_units, norm as seg_norm, download_with_retry,
)

STRUCTURE=Path('data/derived/page_structure.csv')
MANIFEST=Path('data/derived/fragment_manifest.csv')
VERSION='SEMB_0.1'
MODEL_ID='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
MODEL_REV='f16484b452bc5449a3ad85665709a2648b51d735'

ACTION_PROTOTYPES={
'observe':['Observa atentamente un objeto o fenómeno y utiliza lo que notas.','Mira, examina o identifica propiedades mediante observación deliberada.'],
'describe':['Describe las características, estados o resultados que encuentras.','Expresa cómo es algo o qué propiedades presenta, sin explicar necesariamente sus causas.'],
'recall':['Recuerda y menciona información que ya aprendiste anteriormente.','Nombra o enumera conocimientos recuperados de la memoria.'],
'explain':['Explica por qué sucede un fenómeno o cómo funciona una relación.','Justifica una respuesta mediante razones, causas o mecanismos.'],
'compare':['Compara elementos para establecer semejanzas, diferencias o relaciones.','Contrasta dos condiciones y señala en qué se parecen o se diferencian.'],
'classify':['Clasifica objetos o casos usando criterios y categorías.','Agrupa o separa elementos según sus propiedades.'],
'measure':['Mide una magnitud con una escala, instrumento, conteo o procedimiento cuantitativo.','Obtén y registra una medida numérica de una propiedad.'],
'experiment':['Realiza un experimento manipulando materiales o condiciones y observa los resultados.','Cambia deliberadamente una condición para producir evidencia sobre un fenómeno.'],
'investigate':['Investiga buscando, reuniendo o contrastando información que no está resuelta de inmediato.','Consulta fuentes, realiza una indagación o reúne evidencia para responder una pregunta.'],
'predict':['Predice qué ocurrirá antes de observar o comprobar el resultado.','Anticipa un resultado futuro a partir de lo que sabes.'],
'infer':['Infiere una conclusión a partir de datos, observaciones o evidencias.','Deduce qué se puede concluir usando los resultados disponibles.'],
'discuss':['Discute ideas con otras personas y contrasta argumentos o puntos de vista.','Conversa o debate con compañeros para construir una respuesta.'],
'solve':['Resuelve un problema mediante razonamiento, relaciones u operaciones.','Encuentra una solución a una situación problemática.'],
'create':['Crea, diseña, construye o elabora un producto o representación.','Produce un dibujo, modelo, texto, cartel u objeto como resultado de la tarea.'],
'decide':['Decide entre alternativas valorando información, criterios o consecuencias.','Elige una opción y sustenta la decisión tomada.'],
'act_on_environment':['Realiza o propone una acción de cuidado, prevención o intervención en la vida real.','Aplica lo aprendido para actuar sobre salud, ambiente, familia, escuela o comunidad.'],
}
POSITION_PROTOTYPES={
'receiver':['El estudiante recibe o lee información sin una acción cognitiva explícita solicitada.','La función principal del alumno es atender a información que el texto presenta.'],
'instruction_follower':['El alumno sigue pasos definidos y ejecuta instrucciones con poca elección metodológica.','La tarea prescribe una secuencia que el estudiante debe cumplir.'],
'observer':['El alumno produce o utiliza información mediante observación sistemática.','El estudiante ocupa el papel de observador de objetos o fenómenos.'],
'experimenter':['El alumno manipula materiales o condiciones para obtener evidencia.','El estudiante ocupa el papel de experimentador.'],
'investigator':['El alumno busca o produce evidencia con cierto margen para investigar.','El estudiante ocupa el papel de investigador o indagador.'],
'reasoner':['El alumno explica, compara, infiere, predice o resuelve usando razonamiento.','El estudiante debe construir una respuesta razonada a partir de información o evidencia.'],
'collaborator':['El alumno construye la tarea mediante interacción sustantiva con otras personas.','El estudiante colabora, discute o trabaja con compañeros, familia u otros actores.'],
'decision_maker':['El alumno valora alternativas y toma una decisión informada.','El estudiante ocupa el papel de quien elige y justifica una opción.'],
'community_agent':['El alumno proyecta el conocimiento hacia una acción en familia, escuela, comunidad, salud o ambiente.','El estudiante actúa como agente de cuidado, prevención o transformación fuera de la respuesta escolar.'],
}


def prototype_matrix(model, mapping):
    labels=list(mapping)
    texts=[x for label in labels for x in mapping[label]]
    emb=model.encode(texts,normalize_embeddings=True,show_progress_bar=False)
    vectors=[]
    for i,label in enumerate(labels):
        v=emb[i*2:(i+1)*2].mean(axis=0)
        v=v/(np.linalg.norm(v)+1e-12)
        vectors.append(v)
    return labels,np.stack(vectors)


def select_labels(labels,scores,skip=False):
    """Apply preregistered threshold/margin decision rule."""
    if skip:
        return [],1,float('nan'),float('nan'),float('nan')
    order=np.argsort(-scores)
    top_i=int(order[0]); second_i=int(order[1]) if len(order)>1 else top_i
    top=float(scores[top_i]); second=float(scores[second_i]); margin=top-second
    if top < 0.42:
        return [],1,top,second,margin
    if top >= 0.46:
        chosen=[]
        for i in order:
            s=float(scores[int(i)])
            if s>=0.46 and s>=top-0.06:
                chosen.append(labels[int(i)])
            if len(chosen)>=3:
                break
        return chosen,0,top,second,margin
    if margin >= 0.035:
        return [labels[top_i]],0,top,second,margin
    chosen=[labels[top_i]]
    if second>=0.42:
        chosen.append(labels[second_i])
    return chosen,1,top,second,margin


def reconstruct_page_fragments(r,temp):
    gen=r['catalog_generation'];p=int(r['viewer_page']);psm=r['selected_psm'] or '3'
    img=temp/f'{gen}_{p:03d}.jpg';outbase=temp/f'{gen}_{p:03d}'
    download_with_retry(f"https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[gen]}/{p:03d}.jpg",img)
    if not run_tesseract(img,outbase,psm): raise RuntimeError(f'OCR failed {r["page_id"]}')
    rows=read_tsv(outbase.with_suffix('.tsv'));paras=reconstruct_paragraphs(rows);units=[]
    for para in paras: units.extend(sentence_units(para))
    merged=merge_units(units);out=[]
    for seq,(text,typ,sig,n) in enumerate(merged,1):
        if n==0:continue
        out.append((f"{r['page_id']}-F{seq:03d}",text,typ,n))
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--generation',required=True,choices=SOURCE_CODES);ap.add_argument('--out',required=True);args=ap.parse_args()
    structure=[r for r in csv.DictReader(STRUCTURE.open(encoding='utf-8')) if r['catalog_generation']==args.generation and r['primary_structure'] in ELIGIBLE]
    expected={r['fragment_id']:r for r in csv.DictReader(MANIFEST.open(encoding='utf-8')) if r['catalog_generation']==args.generation}
    assert expected and all(r['segmenter_version']=='FRAGSEG_0.2' for r in expected.values())
    model=SentenceTransformer(MODEL_ID,revision=MODEL_REV)
    action_labels,action_proto=prototype_matrix(model,ACTION_PROTOTYPES)
    pos_labels,pos_proto=prototype_matrix(model,POSITION_PROTOTYPES)
    outrows=[];seen=set()
    with tempfile.TemporaryDirectory(prefix=f'ltmd-semB-{args.generation}-') as td:
        temp=Path(td)
        for pi,r in enumerate(structure,1):
            frags=reconstruct_page_fragments(r,temp)
            texts=[]; metas=[]
            for fid,text,typ,n in frags:
                if fid not in expected: raise AssertionError(f'unexpected fragment {fid}')
                exp=expected[fid]
                digest=hashlib.sha256(seg_norm(text).encode('utf-8')).hexdigest()
                if digest!=exp['text_sha256']: raise AssertionError(f'hash mismatch {fid}')
                texts.append(text);metas.append((fid,typ,n,digest,exp))
            if texts:
                embeds=model.encode(texts,normalize_embeddings=True,show_progress_bar=False,batch_size=32)
                a_scores=embeds @ action_proto.T
                p_scores=embeds @ pos_proto.T
                for idx,(fid,typ,n,digest,exp) in enumerate(metas):
                    skip=(typ=='heading_candidate' or n<4)
                    alabs,au,atop,asecond,amargin=select_labels(action_labels,a_scores[idx],skip=skip)
                    plabs,pu,ptop,psecond,pmargin=select_labels(pos_labels,p_scores[idx],skip=skip)
                    trunc=int(n>90)
                    row={
                        'fragment_id':fid,'page_id':exp['page_id'],'catalog_generation':args.generation,
                        'action_labels_B':';'.join(alabs),'position_labels_B':';'.join(plabs),
                        'action_label_count_B':len(alabs),'position_label_count_B':len(plabs),
                        'action_top_score_B':'' if np.isnan(atop) else round(atop,6),
                        'action_second_score_B':'' if np.isnan(asecond) else round(asecond,6),
                        'action_margin_B':'' if np.isnan(amargin) else round(amargin,6),
                        'position_top_score_B':'' if np.isnan(ptop) else round(ptop,6),
                        'position_second_score_B':'' if np.isnan(psecond) else round(psecond,6),
                        'position_margin_B':'' if np.isnan(pmargin) else round(pmargin,6),
                        'uncertain_action_B':au,'uncertain_position_B':pu,
                        'uncertain_B':int(au or pu or trunc),'truncation_risk_B':trunc,
                        'text_sha256':digest,'semantic_model':MODEL_ID,'semantic_model_revision':MODEL_REV,
                        'semantic_rules_version':VERSION,
                    }
                    for label in action_labels: row[f'action_{label}_B']=int(label in alabs)
                    for label in pos_labels: row[f'position_{label}_B']=int(label in plabs)
                    outrows.append(row);seen.add(fid)
            for pth in temp.glob(f"{args.generation}_{int(r['viewer_page']):03d}*"):
                try:pth.unlink()
                except Exception:pass
            if pi%25==0: print(args.generation,'pages',pi,'/',len(structure),'labels',len(outrows))
    missing=set(expected)-seen
    if missing: raise AssertionError(f'missing {len(missing)} fragments; first={sorted(missing)[:5]}')
    if len(outrows)!=len(expected): raise AssertionError((len(outrows),len(expected)))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);fields=list(outrows[0].keys())
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(outrows)
    print('generation',args.generation,'rows',len(outrows),'uncertain',sum(int(r['uncertain_B']) for r in outrows),'truncation_risk',sum(int(r['truncation_risk_B']) for r in outrows))

if __name__=='__main__':main()
