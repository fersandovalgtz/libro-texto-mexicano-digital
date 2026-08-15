#!/usr/bin/env python3
"""Corpus executor for SEMB_0.2, gated by locked synthetic validation.

This script refuses to run unless the versioned development selection exists and
VALIDATION_B02 passed its preregistered criteria. It never reads RULEA outputs.
Fragment text is reconstructed ephemerally, SHA-verified against FRAGSEG_0.2,
embedded, labeled, and discarded. No text or embeddings are persisted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path

from semantic_classifier_B02_core import SemanticB02, MODEL, REV, VERSION
from segment_fragments import (
    SOURCE_CODES, ELIGIBLE, run_tesseract, read_tsv, reconstruct_paragraphs,
    sentence_units, merge_units, norm as seg_norm, download_with_retry,
)

STRUCTURE=Path('data/derived/page_structure.csv')
MANIFEST=Path('data/derived/fragment_manifest.csv')
VALIDATION=Path('data/derived/semantic_B02_validation_result.json')


def verify_validation():
    d=json.load(VALIDATION.open(encoding='utf-8'))
    assert d['validation_version']=='VALIDATION_B02_LOCKED_0.1'
    assert d['semantic_version']==VERSION
    assert d['passed'] is True, 'SEMB 0.2 cannot access corpus: locked validation did not pass'
    assert d['corpus_accessed'] is False and d['ruleA_accessed'] is False
    return d


def reconstruct_page_fragments(r,temp):
    gen=r['catalog_generation']; p=int(r['viewer_page']); psm=r['selected_psm'] or '3'
    img=temp/f'{gen}_{p:03d}.jpg'; outbase=temp/f'{gen}_{p:03d}'
    download_with_retry(f"https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[gen]}/{p:03d}.jpg",img)
    if not run_tesseract(img,outbase,psm): raise RuntimeError(f'OCR failed {r["page_id"]}')
    rows=read_tsv(outbase.with_suffix('.tsv'))
    paras=reconstruct_paragraphs(rows); units=[]
    for para in paras: units.extend(sentence_units(para))
    merged=merge_units(units); out=[]
    for seq,(text,typ,sig,n) in enumerate(merged,1):
        if n==0: continue
        out.append((f"{r['page_id']}-F{seq:03d}",text,typ,n))
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--generation',required=True,choices=SOURCE_CODES); ap.add_argument('--out',required=True); args=ap.parse_args()
    validation=verify_validation()
    structure=[r for r in csv.DictReader(STRUCTURE.open(encoding='utf-8')) if r['catalog_generation']==args.generation and r['primary_structure'] in ELIGIBLE]
    assert structure and all(r['classifier_version']=='PAGESTRUCT_0.2' for r in structure)
    expected={r['fragment_id']:r for r in csv.DictReader(MANIFEST.open(encoding='utf-8')) if r['catalog_generation']==args.generation}
    assert expected and all(r['segmenter_version']=='FRAGSEG_0.2' for r in expected.values())
    engine=SemanticB02()
    assert engine.method==validation['selected_method']
    assert float(engine.gate_threshold)==float(validation['action_gate_threshold'])
    max_seq=int(getattr(engine.model,'max_seq_length',512) or 512)

    rows_out=[]; seen=set()
    with tempfile.TemporaryDirectory(prefix=f'ltmd-semB02-{args.generation}-') as td:
        temp=Path(td)
        for pi,r in enumerate(structure,1):
            frags=reconstruct_page_fragments(r,temp)
            texts=[]; metas=[]
            for fid,text,typ,n in frags:
                if fid not in expected: raise AssertionError(f'unexpected fragment {fid}')
                exp=expected[fid]
                digest=hashlib.sha256(seg_norm(text).encode('utf-8')).hexdigest()
                if digest!=exp['text_sha256']: raise AssertionError(f'hash mismatch {fid}')
                texts.append(text); metas.append((fid,typ,n,digest,exp))
            if texts:
                embeddings=engine.embed_texts(texts)
                token_lengths=[len(engine.model.tokenizer(t,add_special_tokens=True,truncation=False)['input_ids']) for t in texts]
                for q,tok_len,(fid,typ,n,digest,exp) in zip(embeddings,token_lengths,metas):
                    skip=(typ=='heading_candidate' or n<4)
                    a=engine.select_actions(q,skip=skip)
                    p=engine.select_positions(q,skip=skip)
                    trunc=int(tok_len>max_seq)
                    row={
                        'fragment_id':fid,'page_id':exp['page_id'],'catalog_generation':args.generation,
                        'action_labels_B':';'.join(a['labels']),'position_labels_B':';'.join(p['labels']),
                        'action_label_count_B':len(a['labels']),'position_label_count_B':len(p['labels']),
                        'action_gate_margin_B':'' if a['gate_margin'] is None else round(float(a['gate_margin']),6),
                        'action_gate_threshold_B':engine.gate_threshold,
                        'action_top_score_B':'' if a['top'] is None else round(float(a['top']),6),
                        'action_second_score_B':'' if a['second'] is None else round(float(a['second']),6),
                        'action_margin_B':'' if a['margin'] is None else round(float(a['margin']),6),
                        'position_top_score_B':'' if p['top'] is None else round(float(p['top']),6),
                        'position_second_score_B':'' if p['second'] is None else round(float(p['second']),6),
                        'position_margin_B':'' if p['margin'] is None else round(float(p['margin']),6),
                        'uncertain_action_B':int(a['uncertain']),'uncertain_position_B':int(p['uncertain']),
                        'uncertain_B':int(a['uncertain'] or p['uncertain'] or trunc),
                        'tokenizer_length_B':tok_len,'model_max_seq_length_B':max_seq,'truncation_risk_B':trunc,
                        'text_sha256':digest,'semantic_model':MODEL,'semantic_model_revision':REV,
                        'semantic_method':engine.method,'semantic_rules_version':VERSION,
                    }
                    for lab in engine.action_labels: row[f'action_{lab}_B']=int(lab in a['labels'])
                    for lab in engine.position_labels: row[f'position_{lab}_B']=int(lab in p['labels'])
                    rows_out.append(row); seen.add(fid)
            for pth in temp.glob(f"{args.generation}_{int(r['viewer_page']):03d}*"):
                try: pth.unlink()
                except Exception: pass
            if pi%25==0: print(args.generation,'pages',pi,'/',len(structure),'labels',len(rows_out))
    missing=set(expected)-seen
    if missing: raise AssertionError(f'missing {len(missing)} fragments; first={sorted(missing)[:5]}')
    assert len(rows_out)==len(expected)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows_out[0].keys())); w.writeheader(); w.writerows(rows_out)
    print('generation',args.generation,'rows',len(rows_out),'uncertain',sum(int(r['uncertain_B']) for r in rows_out),'truncation_risk',sum(int(r['truncation_risk_B']) for r in rows_out))

if __name__=='__main__': main()
