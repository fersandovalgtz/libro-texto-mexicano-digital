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
import urllib.request
from collections import Counter
from pathlib import Path

from segment_fragments import (
    SOURCE_CODES, ELIGIBLE, run_tesseract, read_tsv, reconstruct_paragraphs,
    sentence_units, merge_units, norm as seg_norm,
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

PATTERNS={
'observe':[r'\bobserv(?:a|a[nr]|e|en)\b',r'\bmira\b',r'\bexamina\b',r'\bf[ií]jate\b'],
'describe':[r'\bdescribe\b',r'\bdescriban\b',r'\bcaracteriza\b',r'\banota (?:las )?caracter[ií]sticas\b'],
'recall':[r'\brecuerda\b',r'\brecuerdas\b',r'\bmenciona\b',r'\benumera\b',r'\bnombra\b',r'\bqu[eé] sabes\b'],
'explain':[r'\bexplica\b',r'\bexpliquen\b',r'\bjustifica\b',r'\bpor qu[eé]\b',r'\ba qu[eé] se debe\b'],
'compare':[r'\bcompara\b',r'\bcomparen\b',r'\bsemejanzas?\b',r'\bdiferencias?\b'],
'classify':[r'\bclasifica\b',r'\bclasifiquen\b',r'\bagrupa\b',r'\bagrupen\b',r'\bsepara en\b'],
'measure':[r'\bmide\b',r'\bmidan\b',r'\bmedici[oó]n\b',r'\bterm[oó]metro\b',r'\bcron[oó]metro\b',r'\bbalanza\b',r'\bcent[ií]metr(?:o|os)\b',r'\bregistra (?:la|las) medida'],
'investigate':[r'\binvestiga\b',r'\binvestiguen\b',r'\bbusca informaci[oó]n\b',r'\bconsult(?:a|en)\b',r'\bentrevista\b',r'\bencuesta\b',r'\baverigua\b',r'\bindaga\b'],
'predict':[r'\bpredice\b',r'\bpredigan\b',r'\bqu[eé] crees que (?:ocurrir[aá]|pasar[aá]|suceder[aá])\b',r'\bantes de observar\b'],
'infer':[r'\binfiere\b',r'\bconcluye\b',r'\bconcluyan\b',r'\bdeduce\b',r'\ba partir de (?:los )?(?:resultados|datos|observaciones)\b'],
'discuss':[r'\bdiscute\b',r'\bdiscutan\b',r'\bcomenten\b',r'\bconversen\b',r'\bdebate\b',r'\bcon tus compa[nñ]eros\b'],
'solve':[r'\bresuelve\b',r'\bresuelvan\b',r'\bencuentra (?:la|una) soluci[oó]n\b',r'\bproblema\b'],
'create':[r'\belabora\b',r'\bconstruye\b',r'\bdise[nñ]a\b',r'\bdibuja\b',r'\bcrea\b',r'\bprepara\b',r'\bmaqueta\b',r'\bcartel\b'],
'decide':[r'\bdecide\b',r'\belige\b',r'\belijan\b',r'\bselecciona una alternativa\b',r'\btoma una decisi[oó]n\b',r'\bargumenta tu elecci[oó]n\b'],
}

EXPERIMENT_TERMS=[r'\bexperimento\b',r'\bexperimenta\b',r'\bprocedimiento\b',r'\bhip[oó]tesis\b']
MATERIAL_TERMS=[r'\bmateriales\b',r'\bnecesitas\b',r'\bvas a necesitar\b']
MANIPULATION=[r'\bmezcla\b',r'\bcoloca\b',r'\bagrega\b',r'\bintroduce\b',r'\bcalienta\b',r'\benfr[ií]a\b',r'\bcambia\b',r'\bmanipula\b']
COMMUNITY_CONTEXT=[r'\bfamilia\b',r'\bcomunidad\b',r'\bescuela\b',r'\bambiente\b',r'\bmedio ambiente\b',r'\bsalud\b',r'\bprevenci[oó]n\b',r'\bcuidado\b']
ACTION_OUTWARD=[r'\bprop[oó]n\b',r'\brealiza\b',r'\borganiza\b',r'\bparticipa\b',r'\bpromueve\b',r'\baplica\b',r'\bcomparte\b']
ASSESS=[r'\bevaluaci[oó]n\b',r'\bautoevaluaci[oó]n\b',r'\bqu[eé] aprend[ií]\b',r'\blo que aprend[ií]\b']
PROJECT=[r'\bproyecto\b']
ACTIVITY=[r'\bactividad\b',r'\ben equipo\b',r'\bpor equipos\b',r'\btrabaja en equipo\b']


def clean(s:str)->str:
    return unicodedata.normalize('NFKC',s).casefold()

def hits(text, pats):
    return sum(1 for p in pats if re.search(p,text,re.I))

def classify_text(text, meta):
    t=clean(text)
    acts={a:0 for a in ACTIONS}; evidence=Counter()
    for a,pats in PATTERNS.items():
        n=hits(t,pats); acts[a]=int(n>0); evidence[a]+=n

    exp_terms=hits(t,EXPERIMENT_TERMS); mats=hits(t,MATERIAL_TERMS); manip=hits(t,MANIPULATION)
    directed = meta['candidate_type'] in {'instruction_candidate','activity_candidate','experiment_candidate','project_candidate'} or any(acts.values())
    acts['experiment']=int(directed and (exp_terms>0 or (mats>0 and manip>0)))
    evidence['experiment']+=exp_terms+mats+manip if acts['experiment'] else 0

    comm=hits(t,COMMUNITY_CONTEXT); outward=hits(t,ACTION_OUTWARD)
    acts['act_on_environment']=int(comm>0 and outward>0 and directed)
    evidence['act_on_environment']+=comm+outward if acts['act_on_environment'] else 0

    # `discuss` requires interaction language, not merely the structural phrase "en equipo".
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
    if hits(t,PROJECT) or meta['candidate_type']=='project_candidate': types.append('project')
    if acts['experiment'] or meta['candidate_type']=='experiment_candidate': types.append('experiment')
    if hits(t,ACTIVITY) or meta['candidate_type']=='activity_candidate': types.append('activity')
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
    urllib.request.urlretrieve(f"https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[gen]}/{p:03d}.jpg",img)
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
