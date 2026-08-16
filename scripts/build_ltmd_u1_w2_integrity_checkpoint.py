#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

VERSION='LTMD_U1_W2_INTEGRITY_0.1'
OUTJ=Path('data/derived/ltmd_u1_w2_integrity_checkpoint.json')
OUTM=Path('data/derived/ltmd_u1_w2_integrity_checkpoint.md')
CRITICAL=[
 'docs/LTMD_U1_W2_MATHEMATICS_STATUS_0_1.md','docs/LTMD_U1_W2_COMPLETION.md',
 'data/catalog/ltmd_u1_w2_scope.csv','data/catalog/ltmd_u1_w2_declared_inventory.csv','data/catalog/ltmd_u1_w2_viewer_architecture.md',
 'data/catalog/ltmd_u1_w2_math_asset_manifest.csv','data/catalog/ltmd_u1_w2_math_asset_summary.csv','data/catalog/ltmd_u1_w2_math_asset_states.csv',
 'data/catalog/ltmd_u1_w2_math_internal_recoveries.csv','data/catalog/ltmd_u1_w2_math_reconciled_manifest.csv','data/catalog/ltmd_u1_w2_math_reconciled_summary.csv',
 'data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv','data/catalog/ltmd_u1_w2_math_document_relationships.csv',
 'data/catalog/ltmd_u1_w2_math_ocr_metrics.csv','data/catalog/ltmd_u1_w2_math_ocr_summary.csv','data/catalog/ltmd_u1_w2_math_ocr.md',
 'data/catalog/ltmd_u1_w2_math_page_structure.csv','data/catalog/ltmd_u1_w2_math_page_structure_summary.csv','data/catalog/ltmd_u1_w2_math_page_structure.md',
 'data/catalog/ltmd_u1_w2_math_fragment_manifest.csv','data/catalog/ltmd_u1_w2_math_fragment_manifest_summary.csv','data/catalog/ltmd_u1_w2_math_fragment_sequence_gaps.csv','data/catalog/ltmd_u1_w2_math_fragment_manifest.md',
 'scripts/ocr_ltmd_u1_w2_math_book.py','scripts/combine_ltmd_u1_w2_math_ocr.py',
 'scripts/extract_ltmd_u1_w2_math_structural_flags_book.py','scripts/combine_ltmd_u1_w2_math_structural_flags_v02.py','scripts/classify_ltmd_u1_w2_math_page_structure_v02.py',
 'scripts/segment_ltmd_u1_w2_math_fragments_v02.py','scripts/combine_ltmd_u1_w2_math_fragment_shards_v02.py',
 'scripts/build_ltmd_u1_w2_completion_report.py','scripts/build_ltmd_u1_coverage_w2_current.py'
]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 missing=[x for x in CRITICAL if not Path(x).is_file()]
 if missing:raise SystemExit('missing W2 critical files: '+', '.join(missing))
 files=[{'path':x,'bytes':Path(x).stat().st_size,'sha256':sha(Path(x))} for x in CRITICAL]
 payload={'integrity_version':VERSION,'scope':'LTMD-U1 W2 Mathematics post-release main checkpoint','historical_release_untouched':'v0.1.0-rc.1','critical_count':len(files),'missing_critical':[],'files':files}
 OUTJ.parent.mkdir(parents=True,exist_ok=True);OUTJ.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['# LTMD-U1 W2 — checkpoint de integridad','',f'Versión: `{VERSION}`.','',f'- Artefactos críticos: **{len(files)}/{len(CRITICAL)}**.', '- `missing_critical=[]`.', '- Este checkpoint pertenece a la evolución de `main` posterior a `v0.1.0-rc.1`; no modifica ni reatribuye el tag histórico.','','| archivo | bytes | SHA-256 |','|---|---:|---|']
 for r in files:lines.append(f"| `{r['path']}` | {r['bytes']:,} | `{r['sha256']}` |")
 OUTM.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(f'{VERSION}: {len(files)}/{len(CRITICAL)} critical files verified')
if __name__=='__main__':main()
