#!/usr/bin/env python3
"""Build PRIVATE OCR hypotheses aligned to human CER/WER reference regions.

This script is intended to run in a private/local environment, not in public CI.
It reads a private working CSV exported from the Google Sheet and the public
`data/derived/ocr_page_metrics.csv` file.

Important design choice:
- OCR is run on the FULL PAGE with the `selected_psm` frozen by OCR pipeline 0.1.
- For `crop_block`, words are filtered spatially from the full-page TSV using
  normalized bounding-box coordinates.
- Tesseract is NOT rerun on the crop, because cropping can change layout
  segmentation and would evaluate a different OCR problem.

The output contains `ocr_region_text_private` and therefore MUST remain private.
Do not commit it to GitHub.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

UA = "LibroTextoMexicanoDigital/0.1 private reference hypotheses"


def first(row:dict,*names:str)->str:
    for name in names:
        value=row.get(name)
        if value is not None and str(value).strip()!='':
            return str(value)
    return ''


def fetch(url:str,target:Path,timeout:int=35)->None:
    req=Request(url,headers={"User-Agent":UA})
    with urlopen(req,timeout=timeout) as r,target.open('wb') as fh:
        expected=r.headers.get('Content-Length')
        expected_n=int(expected) if expected and expected.isdigit() else None
        total=0
        while expected_n is None or total<expected_n:
            need=65536 if expected_n is None else min(65536,expected_n-total)
            chunk=r.read(need)
            if not chunk:
                break
            fh.write(chunk); total+=len(chunk)


def tsv_words(image:Path,psm:int,lang:str,timeout:int)->list[dict]:
    proc=subprocess.run(
        ['tesseract',str(image),'stdout','-l',lang,'--psm',str(psm),'tsv'],
        capture_output=True,text=True,timeout=timeout,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or f'tesseract exit {proc.returncode}')
    out=[]
    for row in csv.DictReader(proc.stdout.splitlines(),delimiter='\t'):
        text=(row.get('text') or '').strip()
        if not text:
            continue
        try:
            conf=float(row.get('conf') or -1)
            left=int(row.get('left') or 0); top=int(row.get('top') or 0)
            width=int(row.get('width') or 0); height=int(row.get('height') or 0)
            block=int(row.get('block_num') or 0); par=int(row.get('par_num') or 0)
            line=int(row.get('line_num') or 0); word=int(row.get('word_num') or 0)
        except ValueError:
            continue
        if conf < 0:
            continue
        out.append({
            'text':text,'conf':conf,'left':left,'top':top,'width':width,'height':height,
            'block':block,'par':par,'line':line,'word':word,
        })
    return out


def words_in_scope(words:list[dict],scope:str,coords:tuple[float,float,float,float]|None,image_width:int,image_height:int)->list[dict]:
    if scope=='full_page':
        return words
    if scope!='crop_block' or coords is None:
        raise ValueError(f'Unsupported/incomplete reference_scope: {scope!r}')
    x0,y0,x1,y1=coords
    left=x0*image_width; top=y0*image_height; right=x1*image_width; bottom=y1*image_height
    selected=[]
    for w in words:
        cx=w['left']+w['width']/2
        cy=w['top']+w['height']/2
        if left <= cx <= right and top <= cy <= bottom:
            selected.append(w)
    return selected


def reconstruct(words:list[dict])->str:
    # Tesseract TSV already emits rows in reading order. Explicitly preserve
    # line groups to make the reconstruction deterministic before whitespace
    # normalization in the CER/WER evaluator.
    lines=[]; current_key=None; current=[]
    for w in words:
        key=(w['block'],w['par'],w['line'])
        if current_key is None:
            current_key=key
        if key!=current_key:
            lines.append(' '.join(current)); current=[]; current_key=key
        current.append(w['text'])
    if current:
        lines.append(' '.join(current))
    return '\n'.join(lines).strip()


def coords_from(row:dict)->tuple[float,float,float,float]|None:
    if first(row,'reference_scope')!='crop_block':
        return None
    vals=[]
    for field in ('crop_x0','crop_y0','crop_x1','crop_y1'):
        raw=first(row,field)
        vals.append(float(raw))
    x0,y0,x1,y1=vals
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise ValueError('invalid crop bounds')
    return x0,y0,x1,y1


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('private_input',help='Private CSV exported from the reference Google Sheet')
    ap.add_argument('--page-metrics',default='data/derived/ocr_page_metrics.csv')
    ap.add_argument('--output',default='working/ocr_reference_hypotheses_private.csv')
    ap.add_argument('--lang',default='spa')
    ap.add_argument('--timeout',type=int,default=60)
    args=ap.parse_args()

    input_path=Path(args.private_input)
    rows=list(csv.DictReader(input_path.open(encoding='utf-8-sig',newline='')))
    metrics={r['page_id']:r for r in csv.DictReader(Path(args.page_metrics).open(encoding='utf-8',newline=''))}
    out=[]

    # Pillow is deliberately imported only here; this private helper needs the
    # source image dimensions to interpret normalized crop coordinates.
    from PIL import Image

    with tempfile.TemporaryDirectory(prefix='ltmd-private-hyp-') as d:
        root=Path(d)
        for row in rows:
            page_id=first(row,'page_id')
            scope=first(row,'reference_scope')
            if scope not in {'full_page','crop_block'}:
                row['ocr_region_text_private']=''
                row['ocr_psm_used']=''
                row['hypothesis_status']='pending_reference_scope'
                out.append(row); continue

            metric=metrics.get(page_id)
            if not metric:
                row['ocr_region_text_private']=''
                row['ocr_psm_used']=''
                row['hypothesis_status']='missing_page_metric'
                out.append(row); continue
            psm=first(metric,'selected_psm')
            if not psm:
                row['ocr_region_text_private']=''
                row['ocr_psm_used']=''
                row['hypothesis_status']='no_accepted_psm'
                out.append(row); continue

            url=first(row,'source_url','source_asset_url')
            image=root/f'{page_id}.jpg'
            try:
                fetch(url,image)
                with Image.open(image) as im:
                    iw,ih=im.size
                words=tsv_words(image,int(psm),args.lang,args.timeout)
                selected=words_in_scope(words,scope,coords_from(row),iw,ih)
                row['ocr_region_text_private']=reconstruct(selected)
                row['ocr_psm_used']=psm
                row['hypothesis_status']='ok'
                out.append(row)
            except Exception as exc:
                row['ocr_region_text_private']=''
                row['ocr_psm_used']=psm
                row['hypothesis_status']=f'error:{type(exc).__name__}:{exc}'
                out.append(row)
            finally:
                image.unlink(missing_ok=True)

    fields=list(rows[0].keys()) if rows else []
    for extra in ('ocr_psm_used','ocr_region_text_private','hypothesis_status'):
        if extra not in fields:
            fields.append(extra)
    output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(out)
    print(f'Wrote {len(out)} PRIVATE reference-hypothesis rows to {output}')
    print('Do not commit this output to GitHub.')

if __name__=='__main__':
    main()
