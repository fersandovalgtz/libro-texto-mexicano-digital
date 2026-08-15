#!/usr/bin/env python3
"""Compare the 26 non-identical aligned CN4 1972/1988 pages without persisting text.

Each page pair is reconstructed, SHA-256 verified, OCRed with the same PSM, and
normalized. Only counts, hashes of normalized OCR, and similarity metrics persist.
"""
from __future__ import annotations
import csv,hashlib,re,subprocess,tempfile,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from urllib.request import Request,urlopen

MAN=Path('data/expansion/cn46_page_manifest.csv')
DIFF=Path('data/expansion/cn4_1972_1988_page_differences.csv')
OUT=Path('data/expansion/cn4_1972_1988_changed_page_similarity.csv')
REPORT=Path('data/expansion/cn4_1972_1988_changed_page_similarity.md')
VERSION='CN4_72_88_TEXTSIM_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN4 changed-page similarity'
A='LTMD-CN4-G1972';B='LTMD-CN4-G1988'

def download(row,path):
    h=hashlib.sha256()
    with urlopen(Request(row['source_asset_url'],headers={'User-Agent':UA}),timeout=40) as r,path.open('wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b:break
            h.update(b);f.write(b)
    if h.hexdigest()!=row['sha256']:raise RuntimeError(f"hash mismatch {row['page_id']}")

def ocr(img):
    p=subprocess.run(['tesseract',str(img),'stdout','-l','spa','--psm','3'],capture_output=True,text=True,timeout=60)
    if p.returncode:raise RuntimeError(p.stderr.strip() or 'tesseract error')
    return p.stdout

def norm(text):
    s=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z0-9]+',' ',s);return re.sub(r'\s+',' ',s).strip()

def main():
    m=list(csv.DictReader(MAN.open(encoding='utf-8')));byid={r['page_id']:r for r in m}
    diffs=list(csv.DictReader(DIFF.open(encoding='utf-8')))
    if len(diffs)!=26:raise SystemExit(f'expected 26 changed pages, found {len(diffs)}')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-cn4diff-') as td:
        td=Path(td)
        for d in diffs:
            ra=byid[d['page_a']];rb=byid[d['page_b']];ia=td/'a.jpg';ib=td/'b.jpg'
            download(ra,ia);download(rb,ib);ta=norm(ocr(ia));tb=norm(ocr(ib))
            wa=ta.split();wb=tb.split();char_sim=SequenceMatcher(None,ta,tb,autojunk=False).ratio();tok_sim=SequenceMatcher(None,wa,wb,autojunk=False).ratio()
            seta=set(wa);setb=set(wb);jac=len(seta&setb)/len(seta|setb) if seta|setb else 1.0
            rows.append({'audit_version':VERSION,'viewer_page':d['viewer_page'],'position_quartile':d['position_quartile'],'words_1972':len(wa),'words_1988':len(wb),'normalized_ocr_sha256_1972':hashlib.sha256(ta.encode()).hexdigest(),'normalized_ocr_sha256_1988':hashlib.sha256(tb.encode()).hexdigest(),'normalized_ocr_identical':int(ta==tb),'char_sequence_similarity':f'{char_sim:.6f}','token_sequence_similarity':f'{tok_sim:.6f}','token_set_jaccard':f'{jac:.6f}','similarity_class':'near_same_text' if tok_sim>=.95 else ('substantial_overlap' if tok_sim>=.70 else ('partial_overlap' if tok_sim>=.35 else 'different_or_sparse'))})
            ia.unlink(missing_ok=True);ib.unlink(missing_ok=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    counts={k:sum(r['similarity_class']==k for r in rows) for k in ('near_same_text','substantial_overlap','partial_overlap','different_or_sparse')}
    same=sum(int(r['normalized_ocr_identical']) for r in rows)
    med=sorted(float(r['token_sequence_similarity']) for r in rows);median=(med[12]+med[13])/2
    lines=['# Similitud textual de las 26 páginas distintas — CN4 1972/1988','',f'Versión: `{VERSION}`. OCR reconstruido temporalmente; no se conserva texto.','',f'- Páginas con imagen SHA distinta: **26**.\n- OCR normalizado exactamente idéntico: **{same}**.\n- Mediana de similitud secuencial de tokens: **{median:.3f}**.\n- `near_same_text` (≥0.95): **{counts["near_same_text"]}**.\n- `substantial_overlap` (0.70–0.95): **{counts["substantial_overlap"]}**.\n- `partial_overlap` (0.35–0.70): **{counts["partial_overlap"]}**.\n- `different_or_sparse` (<0.35): **{counts["different_or_sparse"]}**.','', '## Páginas con menor similitud']
    for r in sorted(rows,key=lambda x:float(x['token_sequence_similarity']))[:12]:lines.append(f"- VP{int(r['viewer_page']):03d}: token-sim={float(r['token_sequence_similarity']):.3f}; words={r['words_1972']}→{r['words_1988']}; `{r['similarity_class']}`.")
    lines+=['','## Regla','La similitud OCR no demuestra equivalencia editorial, pero ayuda a distinguir imágenes binariamente distintas con texto esencialmente igual de sustituciones de contenido. Las categorías son diagnósticas y no reemplazan inspección histórica del layout.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
