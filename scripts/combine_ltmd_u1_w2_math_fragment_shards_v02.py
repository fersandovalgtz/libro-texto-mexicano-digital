#!/usr/bin/env python3
"""Combine canonical LTMD-U1 W2 Mathematics FRAGSEG 0.2 shards with integrity checks."""
from __future__ import annotations
import argparse,csv
from collections import Counter,defaultdict
from pathlib import Path
STRUCT=Path('data/catalog/ltmd_u1_w2_math_page_structure.csv');OUT=Path('data/catalog/ltmd_u1_w2_math_fragment_manifest.csv');SUMMARY=Path('data/catalog/ltmd_u1_w2_math_fragment_manifest_summary.csv');GAPS=Path('data/catalog/ltmd_u1_w2_math_fragment_sequence_gaps.csv');REPORT=Path('data/catalog/ltmd_u1_w2_math_fragment_manifest.md');VERSION='FRAGSEG_LTMD_U1_W2_MATH_0.2';ELIGIBLE={'textual','mixed_text_image'};EXPECTED=57

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w2_math_fragments');args=ap.parse_args();structure=list(csv.DictReader(STRUCT.open(encoding='utf-8')));viewers={r['viewer_key'] for r in structure};eligible={(r['viewer_key'],r['page_id']) for r in structure if r['primary_structure'] in ELIGIBLE}
 if len(viewers)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} canonical PAGESTRUCT viewers, found {len(viewers)}')
 files=sorted(p for p in Path(args.input_dir).rglob('fragment_*.csv') if not p.name.endswith('_failures.csv'));failfiles=sorted(Path(args.input_dir).rglob('fragment_*_failures.csv'))
 if len(files)!=EXPECTED or len(failfiles)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} fragment and failure shards, got {len(files)} / {len(failfiles)}')
 rows=[];seen=[];empty_pages=[]
 for p in files:
  rr=list(csv.DictReader(p.open(encoding='utf-8')))
  if not rr:raise SystemExit(f'empty fragment shard {p}')
  keys={r['viewer_key'] for r in rr};v={r['segmenter_version'] for r in rr}
  if len(keys)!=1 or v!={VERSION}:raise SystemExit(f'invalid shard {p}')
  seen+=list(keys);rows+=rr
 for p in failfiles:
  for r in csv.DictReader(p.open(encoding='utf-8')):
   if r['status']!='ok':raise SystemExit(f'fatal FRAGSEG failure persisted: {r}')
   empty_pages.append((r['viewer_key'],r['page_id']))
 if set(seen)!=viewers or len(seen)!=EXPECTED:raise SystemExit('canonical viewer coverage mismatch')
 ids=[r['fragment_id'] for r in rows]
 if len(ids)!=len(set(ids)):raise SystemExit(f'duplicate fragment IDs: {len(ids)-len(set(ids))}')
 pagekeys={(r['viewer_key'],r['page_id']) for r in rows}|set(empty_pages)
 if pagekeys!=eligible:raise SystemExit(f'eligible PAGESTRUCT coverage mismatch missing={len(eligible-pagekeys)} extra={len(pagekeys-eligible)}')
 bypage=defaultdict(list)
 for r in rows:bypage[(r['viewer_key'],r['page_id'])].append(int(r['fragment_sequence']))
 gaprows=[]
 for (key,pid),vals in sorted(bypage.items()):
  sv=sorted(vals)
  if any(v<=0 for v in sv) or len(sv)!=len(set(sv)):raise SystemExit(f'invalid fragment sequence {key} {pid}: {sv}')
  missing=[x for x in range(1,max(sv)+1) if x not in set(sv)] if sv else []
  if missing:gaprows.append({'viewer_key':key,'page_id':pid,'observed_fragment_count':len(sv),'max_sequence':max(sv),'missing_sequence_slots':' '.join(map(str,missing)),'missing_slot_count':len(missing)})
 rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page']),int(r['fragment_sequence'])));OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 if gaprows:
  with GAPS.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaprows[0]));w.writeheader();w.writerows(gaprows)
 else:GAPS.write_text('viewer_key,page_id,observed_fragment_count,max_sequence,missing_sequence_slots,missing_slot_count\n',encoding='utf-8')
 types=sorted({r['candidate_type'] for r in rows});counts=defaultdict(Counter);pages=defaultdict(set)
 for r in rows:counts[r['viewer_key']][r['candidate_type']]+=1;counts['ALL'][r['candidate_type']]+=1;pages[r['viewer_key']].add(r['page_id']);pages['ALL'].add(r['page_id'])
 summary=[]
 for key in sorted(viewers)+['ALL']:
  c=counts[key];row={'segmenter_version':VERSION,'viewer_key':key,'fragment_count':sum(c.values()),'segmented_page_count':len(pages[key])};row.update({t:c[t] for t in types});summary.append(row)
 with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
 allc=summary[-1];gap_slots=sum(int(r['missing_slot_count']) for r in gaprows);lines=['# FRAGSEG — LTMD-U1 W2 Matemáticas','',f'Versión: `{VERSION}`.','',f'- Visores canónicos computados: **{EXPECTED}**.',f'- Identidades de catálogo representadas efectivamente: **60/64** mediante 3 aliases exactos.',f'- Páginas elegibles PAGESTRUCT: **{len(eligible):,}**.',f'- Páginas con ≥1 fragmento: **{allc["segmented_page_count"]:,}**.',f'- Páginas elegibles sin fragmentos: **{len(empty_pages)}**.',f'- Fragmentos: **{allc["fragment_count"]:,}**.',f'- IDs únicos: **{len(set(ids)):,}**.',f'- Páginas con huecos legítimos de secuencia: **{len(gaprows)}**.',f'- Slots omitidos: **{gap_slots}**.','', '## Tipos candidatos']
 for t in types:lines.append(f'- `{t}`: {allc[t]:,}.')
 lines+=['','## Regla','`fragment_sequence` conserva la posición previa al descarte de candidatos de 0 tokens; se admiten huecos positivos auditados sin renumerar IDs. Cualquier fallo de descarga, SHA u OCR de ejecución hace fallar el shard. El texto completo no se persiste. `short_residual_candidate` sigue siendo una categoría técnica residual, no evidencia tipográfica ni pedagógica. Esta capa no es `semantic_ready`. Los cuatro DMA 2018 permanecen excluidos hasta resolver su routing.'];REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
