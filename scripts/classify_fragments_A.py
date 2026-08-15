#!/usr/bin/env python3
"""Transparent rule-based pedagogical classifier A for LTMD fragments.

Reconstructs fragment text ephemerally using the frozen segmentation functions,
verifies SHA-256 against fragment_manifest.csv, emits labels/evidence only, and
never persists fragment text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path

from segment_fragments import (
    SOURCE_CODES, ELIGIBLE, run_tesseract, read_tsv, reconstruct_paragraphs,
    sentence_units, merge_units, norm as seg_norm, download_with_retry,
)

STRUCTURE=Path('data/derived/page_structure.csv')
MANIFEST=Path('data/derived/fragment_manifest.csv')
VERSION='RULEA_0.1'

ACTIONS=[
    'observe','describe','recall','explain','compare','classify','measure','experiment',
    'investigate','predict','infer','discuss','solve','create','decide','act_on_environment'
]
POSITIONS=[
    'receiver','instruction_follower','observer','experimenter','investigator','reasoner',
    'collaborator','decision_maker','community_agent'
]
DIRECTED_TYPES={
    'instruction_candidate','activity_candidate','experiment_candidate',
    'project_candidate','question_candidate','assessment_candidate'
}

# Core evidence consists primarily of explicit request/action forms. Every label is
# also gated by directed functional context, preventing expository statements such
# as "se observa un cambio" from becoming student actions.
CORE_PATTERNS={
'observe':[r'\bobserva\b',r'\bobserven\b',r'\bobservar\b',r'\bmira\b',r'\bmiren\b',r'\bmirar\b',r'\bexamina\b',r'\bexaminen\b',r'\bexaminar\b',r'\bf[ií]jate\b',r'\bf[ií]jense\b'],
'describe':[r'\bdescribe\b',r'\bdescriban\b',r'\bdescribir\b',r'\bcaracteriza\b',r'\bcaractericen\b',r'\bcaracterizar\b',r'\banota (?:las )?caracter[ií]sticas\b'],
'recall':[r'\brecuerda\b',r'\brecuerdas\b',r'\brecuerden\b',r'\brecordar\b',r'\bmenciona\b',r'\bmencionen\b',r'\bmencionar\b',r'\benumera\b',r'\benumerar\b',r'\bnombra\b',r'\bnombrar\b',r'\bqu[eé] sabes\b'],
'explain':[r'\bexplica\b',r'\bexpliquen\b',r'\bexplicar\b',r'\bjustifica\b',r'\bjustifiquen\b',r'\bjustificar\b',r'\bpor qu[eé]\b',r'\ba qu[eé] se debe\b'],
'compare':[r'\bcompara\b',r'\bcomparen\b',r'\bcomparar\b'],
'classify':[r'\bclasifica\b',r'\bclasifiquen\b',r'\bclasificar\b',r'\bagrupa\b',r'\bagrupen\b',r'\bagrupar\b',r'\bsepara en\b',r'\bseparar en\b'],
'measure':[r'\bmide\b',r'\bmidan\b',r'\bmedir\b',r'\bregistra (?:la|las) medida',r'\bregistrar (?:la|las) medida'],
'investigate':[r'\binvestiga\b',r'\binvestiguen\b',r'\binvestigar\b',r'\bbusca informaci[oó]n\b',r'\bbusquen informaci[oó]n\b',r'\bbuscar informaci[oó]n\b',r'\bconsult(?:a|en)\b',r'\bconsultar\b',r'\bentrevista\b',r'\bentrevistar\b',r'\bencuesta\b',r'\bencuestar\b',r'\baverigua\b',r'\baveriguar\b',r'\bindaga\b',r'\bindagar\b'],
'predict':[r'\bpredice\b',r'\bpredigan\b',r'\bpredecir\b',r'\bqu[eé] crees que (?:ocurrir[aá]|pasar[aá]|suceder[aá])\b',r'\bantes de observar\b'],
'infer':[r'\binfiere\b',r'\binfieran\b',r'\binferir\b',r'\bconcluye\b',r'\bconcluyan\b',r'\bconcluir\b',r'\bdeduce\b',r'\bdeduzcan\b',r'\bdeducir\b',r'\ba partir de (?:los )?(?:resultados|datos|observaciones)\b'],
'discuss':[r'\bdiscute\b',r'\bdiscutan\b',r'\bdiscutir\b',r'\bcomenten\b',r'\bcomentar\b',r'\bconversen\b',r'\bconversar\b',r'\bdebate\b',r'\bdebatan\b',r'\bdebatir\b',r'\bcon tus compa[nñ]eros\b'],
'solve':[r'\bresuelve\b',r'\bresuelvan\b',r'\bresolver\b',r'\bencuentra (?:la|una) soluci[oó]n\b',r'\bencontrar (?:la|una) soluci[oó]n\b'],
'create':[r'\belabora\b',r'\belaboren\b',r'\belaborar\b',r'\bconstruye\b',r'\bconstruyan\b',r'\bconstruir\b',r'\bdise[nñ]a\b',r'\bdise[nñ]en\b',r'\bdise[nñ]ar\b',r'\bdibuja\b',r'\bdibujen\b',r'\bdibujar\b',r'\bcrea\b',r'\bcreen\b',r'\bcrear\b',r'\bprepara\b',r'\bpreparen\b',r'\bpreparar\b'],
'decide':[r'\bdecide\b',r'\bdecidan\b',r'\bdecidir\b',r'\belige\b',r'\belijan\b',r'\belegir\b',r'\bselecciona una alternativa\b',r'\bseleccionar una alternativa\b',r'\btoma una decisi[oó]n\b',r'\btomar una decisi[oó]n\b',r'\bargumenta tu elecci[oó]n\b'],
}

# Contextual nouns/phrases are never sufficient outside directed context.
CONTEXT_PATTERNS={
    'compare':[r'\bsemejanzas?\b',r'\bdiferencias?\b'],
    'measure':[r'\bmedici[oó]n\b',r'\bterm[oó]metro\b',r'\bcron[oó]metro\b',r'\bbalanza\b',r'\bcent[ií]metr(?:o|os)\b'],
    'solve':[r'\bproblema\b',r'\bsoluci[oó]n\b'],
    'create':[r'\bmaqueta\b',r'\bcartel\b',r'\bmodelo\b'],
}

EXPERIMENT_DIRECT=[r'\bexperimenta\b',r'\bexperimenten\b',r'\bexperimentar\b',r'\brealiza (?:un|el) experimento\b',r'\brealicen (?:un|el) experimento\b',r'\brealizar (?:un|el) experimento\b']
EXPERIMENT_CONTEXT=[r'\bexperimento\b',r'\bprocedimiento\b',r'\bhip[oó]tesis\b']
MATERIAL_TERMS=[r'\bmateriales\b',r'\bnecesitas\b',r'\bvas a necesitar\b']
MANIPULATION=[r'\bmezcla\b',r'\bmezclen\b',r'\bmezclar\b',r'\bcoloca\b',r'\bcoloquen\b',r'\bcolocar\b',r'\bagrega\b',r'\bagreguen\b',r'\bagregar\b',r'\bintroduce\b',r'\bintroduzcan\b',r'\bintroducir\b',r'\bcalienta\b',r'\bcalienten\b',r'\bcalentar\b',r'\benfr[ií]a\b',r'\benfriar\b',r'\bcambia\b',r'\bcambiar\b',r'\bmanipula\b',r'\bmanipular\b']
COMMUNITY_CONTEXT=[r'\bfamilia\b',r'\bcomunidad\b',r'\bescuela\b',r'\bambiente\b',r'\bmedio ambiente\b',r'\bsalud\b',r'\bprevenci[oó]n\b',r'\bcuidado\b']
ACTION_OUTWARD=[r'\bprop[oó]n\b',r'\bpropongan\b',r'\bproponer\b',r'\brealiza\b',r'\brealicen\b',r'\brealizar\b',r'\borganiza\b',r'\borganic(?:en|e)\b',r'\borganizar\b',r'\bparticipa\b',r'\bparticipen\b',r'\bparticipar\b',r'\bpromueve\b',r'\bpromuevan\b',r'\bpromover\b',r'\baplica\b',r'\bapliquen\b',r'\baplicar\b',r'\bcomparte\b',r'\bcompartan\b',r'\bcompartir\b']
ASSESS=[r'\bevaluaci[oó]n\b',r'\bautoevaluaci[oó]n\b',r'\bqu[eé] aprend[ií]\b',r'\blo que aprend[ií]\b']
PROJECT=[r'\bproyecto\b']
ACTIVITY=[r'\bactividad\b',r'\ben equipo\b',r'\bpor equipos\b',r'\btrabaja en equipo\b']


def clean(s:str)->str:
    return unicodedata.normalize('NFKC',s).casefold()

def hits(text, pats):
    return sum(1 for p in pats if re.search(p,text,re.I))

def classify_text(text, meta):
    t=clean(text)
    directed = meta['candidate_type'] in DIRECTED_TYPES or '?' in text or '¿' in text
    acts={a:0 for a in ACTIONS}; evidence=Counter()

    for a,pats in CORE_PATTERNS.items():
        n=hits(t,pats)
        if directed and n>0:
            acts[a]=1
            evidence[a]+=n

    # Contextual evidence is accepted only in a directed fragment. For compare,
    # solve, create and measure it can independently signal the requested operation
    # when the segmenter already identified a question/instruction/activity context.
    if directed:
        for a,pats in CONTEXT_PATTERNS.items():
            n=hits(t,pats)
            if n>0:
                acts[a]=1
                evidence[a]+=n

    exp_direct=hits(t,EXPERIMENT_DIRECT)
    exp_context=hits(t,EXPERIMENT_CONTEXT)
    mats=hits(t,MATERIAL_TERMS)
    manip=hits(t,MANIPULATION)
    acts['experiment']=int(directed and (exp_direct>0 or (mats>0 and manip>0) or (exp_context>0 and manip>0)))
    if acts['experiment']:
        evidence['experiment']+=exp_direct+exp_context+mats+manip

    comm=hits(t,COMMUNITY_CONTEXT); outward=hits(t,ACTION_OUTWARD)
    acts['act_on_environment']=int(directed and comm>0 and outward>0)
    if acts['act_on_environment']:
        evidence['act_on_environment']+=comm+outward

    # `discuss` requires interaction language, not merely "en equipo".
    # `decide` requires an explicit choice verb; closed-answer selection alone is not enough.
    reasoner=any(acts[a] for a in ['explain','compare','predict','infer','solve'])
    positions={p:0 for p in POSITIONS}
    positions['observer']=acts['observe']
    positions['experimenter']=acts['experiment']
    positions['investigator']=acts['investigate']
    positions['reasoner']=int(reasoner)
    positions['collaborator']=acts['discuss']
    positions['decision_maker']=acts['decide']
    positions['community_agent']=acts['act_on_environment']

    any_action=any(acts.values())
    if meta['candidate_type']=='expository_candidate' and not any_action and int(meta['token_count'])>=4:
        positions['receiver']=1
    if meta['candidate_type']=='instruction_candidate' and not any(positions[p] for p in ['observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent']):
        positions['instruction_follower']=1

    types=[]
    if hits(t,ASSESS) or meta['candidate_type']=='assessment_candidate': types.append('assessment')
    if (hits(t,PROJECT) and directed) or meta['candidate_type']=='project_candidate': types.append('project')
    if acts['experiment']: types.append('experiment')
    if (hits(t,ACTIVITY) and directed) or meta['candidate_type']=='activity_candidate': types.append('activity')
    if meta['candidate_type']=='question_candidate' or '?' in text or '¿' in text: types.append('question')
    if meta['candidate_type']=='instruction_candidate' or (any_action and 'question' not in types): types.append('instruction')
    if not types and meta['candidate_type']=='expository_candidate': types.append('expository')
    if not types and meta['candidate_type']=='heading_candidate': types.append('heading')
    if not types: types.append('other')

    evidence_count=sum(evidence.values())
    uncertain=int(
        int(meta['uncertain_boundary'])==1 or
        meta['classification_certainty']=='low' or
        (int(meta['token_count'])<=3 and 'question' not in types and 'heading' not in types) or
        (evidence_count==1 and meta['candidate_type']=='heading_candidate')
    )
    return acts,positions,types,evidence_count,uncertain


def reconstruct_page_fragments(r,temp):
    gen=r['catalog_generation']; p=int(r['viewer_page']); psm=r['selected_psm'] or '3'
    img=temp/f'{gen}_{p:03d}.jpg'; outbase=temp/f'{gen}_{p:03d}'
    download_with_retry(f"https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[gen]}/{p:03d}.jpg",img)
    if not run_tesseract(img,outbase,psm): raise RuntimeError(f'OCR failed {r["page_id"]}')
    rows=read_tsv(outbase.with_suffix('.tsv'))
    paras=reconstruct_paragraphs(rows); units=[]
    for para in paras: units.extend(sentence_units(para))
    merged=merge_units(units)
    out=[]
    for seq,(text,typ,sig,n) in enumerate(merged,1):
        if n==0: continue
        out.append((f"{r['page_id']}-F{seq:03d}",text,typ,n))
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--generation',required=True,choices=SOURCE_CODES); ap.add_argument('--out',required=True)
    args=ap.parse_args()
    structure=[r for r in csv.DictReader(STRUCTURE.open(encoding='utf-8')) if r['catalog_generation']==args.generation and r['primary_structure'] in ELIGIBLE]
    expected={r['fragment_id']:r for r in csv.DictReader(MANIFEST.open(encoding='utf-8')) if r['catalog_generation']==args.generation}
    labels=[]; seen=set()
    with tempfile.TemporaryDirectory(prefix=f'ltmd-ruleA-{args.generation}-') as td:
        temp=Path(td)
        for i,r in enumerate(structure,1):
            for fid,text,typ,n in reconstruct_page_fragments(r,temp):
                if fid not in expected: raise AssertionError(f'unexpected fragment {fid}')
                exp=expected[fid]
                digest=hashlib.sha256(seg_norm(text).encode('utf-8')).hexdigest()
                if digest != exp['text_sha256']:
                    raise AssertionError(f'hash mismatch {fid}: {digest} != {exp["text_sha256"]}')
                meta=dict(exp); meta['candidate_type']=typ; meta['token_count']=n
                acts,pos,types,ev,unc=classify_text(text,meta)
                row={'fragment_id':fid,'page_id':exp['page_id'],'catalog_generation':args.generation,'type_A':';'.join(types)}
                row.update({f'action_{a}':acts[a] for a in ACTIONS})
                row.update({f'position_{p}':pos[p] for p in POSITIONS})
                row.update({'evidence_count_A':ev,'uncertain_A':unc,'ruleset_version':VERSION,'text_sha256':digest})
                labels.append(row); seen.add(fid)
            for pth in temp.glob(f"{args.generation}_{int(r['viewer_page']):03d}*"):
                try: pth.unlink()
                except Exception: pass
            if i%25==0: print(args.generation,'pages',i,'/',len(structure),'labels',len(labels))
    missing=set(expected)-seen
    if missing: raise AssertionError(f'missing {len(missing)} expected fragments; first={sorted(missing)[:5]}')
    if len(labels)!=len(expected): raise AssertionError((len(labels),len(expected)))
    fields=list(labels[0].keys())
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(labels)
    print('generation',args.generation,'labels',len(labels),'uncertain',sum(int(r['uncertain_A']) for r in labels))

if __name__=='__main__': main()
