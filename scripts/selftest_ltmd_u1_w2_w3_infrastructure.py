#!/usr/bin/env python3
from __future__ import annotations
import csv,py_compile
from pathlib import Path

SCRIPTS=[
'scripts/ocr_ltmd_u1_w2_math_book.py','scripts/combine_ltmd_u1_w2_math_ocr.py',
'scripts/extract_ltmd_u1_w2_math_structural_flags_book.py','scripts/combine_ltmd_u1_w2_math_structural_flags_v02.py',
'scripts/classify_ltmd_u1_w2_math_page_structure_v02.py','scripts/segment_ltmd_u1_w2_math_fragments_v02.py',
'scripts/combine_ltmd_u1_w2_math_fragment_shards_v02.py','scripts/build_ltmd_u1_coverage_w2_current.py',
'scripts/build_ltmd_u1_w2_completion_report.py','scripts/build_ltmd_u1_w3_spanish_scope.py',
'scripts/audit_ltmd_u1_w3_spanish_architecture.py','scripts/build_ltmd_u1_w3_spanish_declared_inventory.py',
'scripts/build_ltmd_u1_w3_batch_plan.py','scripts/extract_ltmd_u1_w3_architecture_exceptions.py',
'scripts/probe_ltmd_u1_w3_special_viewers.py','scripts/probe_ltmd_u1_w3_horizontal_contract.py',
'scripts/audit_ltmd_u1_w3_ag_clave_reuse.py','scripts/audit_ltmd_u1_w3_spanish_assets_book.py',
'scripts/combine_ltmd_u1_w3_spanish_asset_shards.py']

def load(path):
 with open(path,encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def main():
 for s in SCRIPTS:
  if not Path(s).exists():raise SystemExit(f'missing script {s}')
  py_compile.compile(s,doraise=True)
 rec=load('data/catalog/ltmd_u1_w2_math_reconciled_summary.csv');aliases=load('data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv')
 assert len(rec)==64
 ready={r['viewer_key'] for r in rec if r['effective_asset_ready']=='1'}
 alias={r['viewer_key'] for r in aliases if r['all_effective_pages_byte_identical_aligned']=='1'}
 assert len(ready)==60 and len(alias)==3 and alias<=ready and len(ready-alias)==57
 w3=load('data/catalog/ltmd_u1_w3_declared_inventory.csv');batches=load('data/catalog/ltmd_u1_w3_batch_plan.csv');arch=load('data/catalog/ltmd_u1_w3_viewer_architecture.csv')
 assert len(w3)==130 and len({r['viewer_key'] for r in w3})==130
 assert sum(int(r['declared_positions']) for r in w3)==23894
 assert len(batches)==130 and len({r['batch_id'] for r in batches})==14 and {r['viewer_key'] for r in batches}=={r['viewer_key'] for r in w3}
 assert all(int(r['batch_declared_positions'])<=2500 for r in batches)
 assert len(arch)==130 and sum(int(r['standard_dynamic_architecture']) for r in arch)==126
 print('PASS: compiled',len(SCRIPTS),'scripts; W2 topology 64/60/57+3/4 and W3 130/23894/14/126+4 invariants hold')
if __name__=='__main__':main()
