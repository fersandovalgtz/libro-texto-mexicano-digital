#!/usr/bin/env python3
"""Interactive blinded annotator for SEMB 0.3 human reference.

Reconstructs only the sampled fragment currently being annotated, verifies its
SHA-256 against the frozen sample manifest, displays no generation/historical
metadata, and persists annotations only (never OCR text).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import tempfile
from pathlib import Path

from segment_fragments import SOURCE_CODES, download_with_retry, run_tesseract, read_tsv, reconstruct_paragraphs, sentence_units, merge_units, norm

SAMPLE=Path('data/validation/semb03_human_reference_sample.csv')
STRUCTURE=Path('data/derived/page_structure.csv')
ACTIONS=('observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment')
POSITIONS=('receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent')
FIELDS=('sample_id','annotator_id','annotation_round','actionable','action_labels','position_labels','annotation_confidence','ambiguity_note')


def parse_labels(raw,allowed):
    vals=[x.strip() for x in raw.split(';') if x.strip()]
    bad=[x for x in vals if x not in allowed]
    if bad: raise ValueError('invalid labels: '+', '.join(bad))
    return ';'.join(dict.fromkeys(vals))


def reconstruct(sample_row,structure,temp):
    page_id=sample_row['page_id']; gen=sample_row['catalog_generation']
    s=structure[page_id]; p=int(s['viewer_page']); psm=s['selected_psm'] or '3'
    img=temp/f'{gen}_{p:03d}.jpg'; outbase=temp/f'{gen}_{p:03d}'
    download_with_retry(f"https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[gen]}/{p:03d}.jpg",img)
    if not run_tesseract(img,outbase,psm): raise RuntimeError('OCR failed for sampled page')
    rows=read_tsv(outbase.with_suffix('.tsv')); units=[]
    for para in reconstruct_paragraphs(rows): units.extend(sentence_units(para))
    merged=merge_units(units)
    for seq,(text,typ,sig,n) in enumerate(merged,1):
        fid=f'{page_id}-F{seq:03d}'
        if fid==sample_row['fragment_id']:
            digest=hashlib.sha256(norm(text).encode('utf-8')).hexdigest()
            if digest!=sample_row['text_sha256']: raise RuntimeError('SHA mismatch; corpus reconstruction is not identical')
            return text
    raise RuntimeError('sampled fragment not reconstructed')


def read_existing(path):
    if not path.exists(): return {}
    return {r['sample_id']:r for r in csv.DictReader(path.open(encoding='utf-8'))}


def save(path,rows,order):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader()
        for sid in order:
            if sid in rows:w.writerow({k:rows[sid].get(k,'') for k in FIELDS})


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--annotator',required=True,help='opaque annotator code, e.g. A01')
    ap.add_argument('--round',default='1')
    ap.add_argument('--out',default='private/semb03_annotations.csv')
    ap.add_argument('--limit',type=int,default=0,help='0 = all remaining')
    args=ap.parse_args()
    sample=list(csv.DictReader(SAMPLE.open(encoding='utf-8')))
    # Use annotator-facing order already frozen in the public template.
    template=list(csv.DictReader(Path('data/validation/semb03_human_reference_annotation_template.csv').open(encoding='utf-8')))
    byid={r['sample_id']:r for r in sample}; order=[r['sample_id'] for r in template]
    assert set(order)==set(byid) and len(order)==480
    structure={r['page_id']:r for r in csv.DictReader(STRUCTURE.open(encoding='utf-8'))}
    out=Path(args.out); existing=read_existing(out); done=0
    with tempfile.TemporaryDirectory(prefix='ltmd-semb03-annotation-') as td:
        temp=Path(td)
        for sid in order:
            if sid in existing and existing[sid].get('annotator_id')==args.annotator: continue
            if args.limit and done>=args.limit: break
            text=reconstruct(byid[sid],structure,temp)
            print('\n'+'='*78)
            print('Muestra:',sid)
            print('-'*78)
            print(text)
            print('-'*78)
            while True:
                actionable=input('¿Hay una acción/tarea solicitada? [1=sí, 0=no, u=ambiguo, q=salir]: ').strip().lower()
                if actionable=='q': save(out,existing,order); return
                if actionable in {'1','0','u'}: break
            print('Acciones permitidas:',', '.join(ACTIONS))
            while True:
                raw=input('Etiquetas de acción separadas por ; (vacío si ninguna): ').strip()
                try:
                    acts=parse_labels(raw,ACTIONS)
                    if actionable=='0' and acts: print('Si actionable=0, deje acciones vacías.'); continue
                    break
                except ValueError as e: print(e)
            print('Posiciones permitidas:',', '.join(POSITIONS))
            while True:
                try:
                    poss=parse_labels(input('Etiquetas de posición separadas por ; : ').strip(),POSITIONS); break
                except ValueError as e: print(e)
            while True:
                conf=input('Confianza [1=baja, 2=media, 3=alta]: ').strip()
                if conf in {'1','2','3'}: break
            note=input('Nota de ambigüedad (opcional): ').strip()
            existing[sid]={'sample_id':sid,'annotator_id':args.annotator,'annotation_round':args.round,
                           'actionable':actionable,'action_labels':acts,'position_labels':poss,
                           'annotation_confidence':conf,'ambiguity_note':note}
            save(out,existing,order); done+=1
            # Remove OCR intermediates before the next case; no text is persisted.
            for p in temp.iterdir():
                try:p.unlink()
                except Exception:pass
    print('Anotaciones nuevas:',done,'archivo:',out)

if __name__=='__main__': main()
