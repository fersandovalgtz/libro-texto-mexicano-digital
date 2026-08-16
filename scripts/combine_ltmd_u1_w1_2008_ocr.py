#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from pathlib import Path
MAN=Path('data/catalog/ltmd_u1_w1_2008_page_manifest.csv');OUT=Path('data/catalog/ltmd_u1_w1_2008_ocr_metrics.csv');SUMMARY=Path('data/catalog/ltmd_u1_w1_2008_ocr_summary.csv');REPORT=Path('data/catalog/ltmd_u1_w1_2008_ocr.md');VERSION='LTMD_U1_W1_2008_OCR_0.1';BOOKS={'LTMD-CN3-G2008','LTMD-CN4-G2008'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w1_2008_ocr');a=ap.parse_args();files=sorted(Path(a.input_dir).glob('ocr_*.csv'))
 if len(files)!=2:raise SystemExit(f'expected 2 shards got {len(files)}')
 rr=[]
 for p in files:rr+=list(csv.DictReader(p.open(encoding='utf-8')))
 src=[r for r in csv.DictReader(MAN.open(encoding='utf-8')) if r['effective_asset_status'].startswith('source_jpeg')];exp={r['page_id'] for r in src};ids=[r['page_id'] for r in rr]
 if len(rr)!=355 or set(ids)!=exp or len(ids)!=len(set(ids)):raise SystemExit(f'OCR coverage mismatch rows={len(rr)} expected={len(exp)} unique={len(set(ids))}')
 if {r['book_id'] for r in rr}!=BOOKS or any(r['ocr_version']!=VERSION for r in rr):raise SystemExit('OCR identity/version mismatch')
 if any(r['source_sha256_verified']!='1' or r['ocr_status']!='ok' or r['ocr_class']=='unresolved' for r in rr):raise SystemExit('OCR provenance/status failure')
 rr.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])));OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 sums=[]
 for b in sorted(BOOKS):
  z=[r for r in rr if r['book_id']==b];sums.append({'ocr_version':VERSION,'book_id':b,'pages':len(z),'sha_verified':sum(r['source_sha256_verified']=='1' for r in z),'text_detected':sum(r['ocr_class']=='text_detected' for r in z),'no_text_detected':sum(r['ocr_class']=='no_text_detected' for r in z),'unresolved':0,'recognized_words':sum(int(r['recognized_words'] or 0) for r in z),'ocr_chars':sum(int(r['ocr_chars'] or 0) for r in z)})
 with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(sums[0]));w.writeheader();w.writerows(sums)
 text=sum(r['ocr_class']=='text_detected' for r in rr);no=355-text;REPORT.write_text(f'# LTMD-U1 W1 — OCR técnico 2008\n\nVersión: `{VERSION}`.\n\n- Páginas fuente efectivas: **355**.\n- SHA-256 verificados: **355/355**.\n- Texto detectado: **{text}/355 ({100*text/355:.2f}%)**.\n- `no_text_detected`: **{no}**.\n- `unresolved`: **0**.\n\nEl OCR íntegro no se persiste. Tres fuentes puntuales proceden del manifiesto de recuperación criptográfica y conservan esa trazabilidad.\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
