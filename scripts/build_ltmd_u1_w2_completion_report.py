#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

REC=Path('data/catalog/ltmd_u1_w2_math_reconciled_summary.csv')
ALIASES=Path('data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv')
OCR=Path('data/catalog/ltmd_u1_w2_math_ocr_summary.csv')
PS=Path('data/catalog/ltmd_u1_w2_math_page_structure_summary.csv')
FRAG=Path('data/catalog/ltmd_u1_w2_math_fragment_manifest_summary.csv')
OUT=Path('docs/LTMD_U1_W2_COMPLETION.md')
VERSION='LTMD_U1_W2_COMPLETION_0.1'

def load(p):
 if not p.exists():raise SystemExit(f'missing required W2 completion artifact: {p}')
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def main():
 rec=load(REC);aliases=load(ALIASES);ocr=load(OCR);ps=load(PS);frag=load(FRAG)
 if len(rec)!=64:raise SystemExit(f'reconciled viewers={len(rec)}')
 ready=[r for r in rec if r['effective_asset_ready']=='1'];unresolved=[r for r in rec if r['effective_asset_ready']!='1']
 if len(ready)!=60 or len(unresolved)!=4:raise SystemExit(f'W2 topology drift ready={len(ready)} unresolved={len(unresolved)}')
 if len(aliases)!=3 or any(r['all_effective_pages_byte_identical_aligned']!='1' for r in aliases):raise SystemExit('W2 exact alias invariant failed')
 if len(ocr)!=57 or {r['ocr_version'] for r in ocr}!={'LTMD_U1_W2_MATH_OCR_0.2'}:raise SystemExit('W2 OCR 0.2 invariant failed')
 if any(int(r['unresolved'])!=0 or int(r['sha_verified'])!=int(r['pages']) for r in ocr):raise SystemExit('W2 OCR unresolved/SHA failure')
 pdetail=[r for r in ps if r['viewer_key']!='ALL'];pall=[r for r in ps if r['viewer_key']=='ALL']
 if len(pdetail)!=57 or len(pall)!=1:raise SystemExit('W2 PAGESTRUCT summary invariant failed')
 fdetail=[r for r in frag if r['viewer_key']!='ALL'];fall=[r for r in frag if r['viewer_key']=='ALL']
 if len(fdetail)!=57 or len(fall)!=1 or {r['segmenter_version'] for r in fdetail}!={'FRAGSEG_LTMD_U1_W2_MATH_0.2'}:raise SystemExit('W2 FRAGSEG summary invariant failed')
 ocr_pages=sum(int(r['pages']) for r in ocr);ocr_text=sum(int(r['text_detected']) for r in ocr);ocr_no=sum(int(r['no_text_detected']) for r in ocr)
 p=pall[0];eligible=int(p['textual'])+int(p['mixed_text_image']);f=fall[0];fragments=int(f['fragment_count']);segpages=int(f['segmented_page_count'])
 recovered=sum(int(r['recovered_jpeg']) for r in rec);unresolved_positions=sum(int(r['effective_unresolved']) for r in rec)
 lines=['# LTMD-U1 W2 — cierre técnico de Matemáticas','',f'Versión: `{VERSION}`.','', '## Resultado ejecutivo','', '- Universo congelado: **64 visores**.',f'- Identidades con activos efectivamente resueltos: **{len(ready)}/64**.',f'- Excepciones de routing conservadas: **{len(unresolved)}/64**.',f'- JPEG recuperados criptográficamente: **{recovered}**.',f'- Posiciones no resueltas en las excepciones: **{unresolved_positions}**.',f'- Aliases documentales byte-idénticos: **{len(aliases)}**.',f'- Contenidos canónicos computados: **{len(ocr)}**.','', '## OCR 0.2','',f'- Páginas canónicas procesadas: **{ocr_pages:,}**.',f'- SHA-256 verificados: **{ocr_pages:,}/{ocr_pages:,}**.',f'- Texto detectado: **{ocr_text:,}**.',f'- `no_text_detected`: **{ocr_no:,}**.',f'- `unresolved`: **0**.','', '## PAGESTRUCT 0.2','',f"- Páginas clasificadas: **{int(p['n_pages']):,}**.",f'- Páginas elegibles para FRAGSEG: **{eligible:,}**.','', '## FRAGSEG 0.2','',f'- Páginas con ≥1 fragmento: **{segpages:,}**.',f'- Fragmentos técnicos: **{fragments:,}**.','', '## Cobertura','', 'Los 57 contenidos canónicos reciben procesamiento directo. Los 3 aliases heredan únicamente cobertura técnica efectiva después de demostrar identidad completa de sus páginas. Los 4 DMA 2018 permanecen como excepciones explícitas y no se imputan.','', '## Límite epistemológico','', 'Este cierre es técnico. Matemáticas no recibe automáticamente el clasificador semántico desarrollado para Ciencias Naturales; `fragseg_ready` no equivale a `semantic_ready`.']
 OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(OUT.read_text())
if __name__=='__main__':main()
