#!/usr/bin/env python3
"""Build the human-reference template for OCR validation.

The selected pages follow docs/EXTRACTION_SPEC.md: legal page + TOC + ten
preregistered positional pages per book. The template contains no source text.
A human transcriber fills `reference_excerpt` in a private working copy; that
text is not intended for GitHub while redistribution remains unresolved.
"""
from __future__ import annotations
import argparse,csv
from pathlib import Path

FIELDS=(
    'validation_id','book_id','catalog_generation','viewer_page','page_id',
    'sample_role','source_asset_url','reference_status','reference_excerpt',
    'reference_word_count','transcriber','reviewer','notes'
)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--inventory',default='data/book_inventory.csv'); ap.add_argument('--manifest',default='data/derived/page_manifest.csv'); ap.add_argument('--output',default='data/derived/ocr_human_reference_template.csv'); args=ap.parse_args()
    books=list(csv.DictReader(Path(args.inventory).open(encoding='utf-8',newline='')))
    pages=list(csv.DictReader(Path(args.manifest).open(encoding='utf-8',newline='')))
    by_key={(r['book_id'],int(r['viewer_page'])):r for r in pages}
    positional={}
    for r in pages:
        if r['qc_positional_candidate']=='yes': positional.setdefault(r['book_id'],[]).append(r)
    out=[]
    for b in books:
        bid=b['book_id']; gen=b['catalog_generation']; chosen=[]
        legal=(b.get('legal_viewer_page') or '').strip(); toc=(b.get('toc_viewer_page_start') or '').strip()
        if legal:
            r=by_key[(bid,int(legal))]; chosen.append(('legal',r))
        else:
            chosen.append(('legal_pending',None))
        if toc:
            r=by_key[(bid,int(toc))]; chosen.append(('toc',r))
        else:
            chosen.append(('toc_pending',None))
        for r in sorted(positional.get(bid,[]),key=lambda x:int(x['viewer_page'])):
            chosen.append((r['qc_slot'],r))
        for i,(role,r) in enumerate(chosen,1):
            out.append({
                'validation_id':f'{bid}-VAL{i:02d}',
                'book_id':bid,'catalog_generation':gen,
                'viewer_page':r['viewer_page'] if r else '',
                'page_id':r['page_id'] if r else '',
                'sample_role':role,
                'source_asset_url':r['source_asset_url'] if r else '',
                'reference_status':'pending_manual' if r else 'pending_page_identification',
                'reference_excerpt':'','reference_word_count':'','transcriber':'','reviewer':'',
                'notes':'Transcribir una muestra textual suficiente y verificarla manualmente; no publicar el texto de referencia mientras permanezca el semáforo amarillo.' if r else 'Identificar primero la página correspondiente y regenerar la plantilla.'
            })
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(out)
    print(f'Wrote {len(out)} validation rows to {path}')
    for b in books:
        rs=[r for r in out if r['book_id']==b['book_id']]
        print(b['book_id'],len(rs),'ready=',sum(bool(r['page_id']) for r in rs),'pending=',sum(not bool(r['page_id']) for r in rs))
if __name__=='__main__': main()
