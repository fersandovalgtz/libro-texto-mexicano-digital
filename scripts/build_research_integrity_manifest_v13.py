#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.13 as an additive W8 closure over 0.12."""
from __future__ import annotations
import json
import build_research_integrity_manifest_v12 as v12

base=v12.base
base.VERSION='LTMD_INTEGRITY_0.13'
SCOPE=('LTMD v0.13: frozen v0.12 perimeter plus the source-admitted LTMD-U1 W8 Artes technical closure: 20 historical identities preserved, 16 direct canonical processing objects, four 2018 source-retained identities without imputation, 1,490 SHA-traced source pages, closed OCR/PAGESTRUCT/FRAGSEG, exact-text dependence products, explicit dispatch controls, and the W8 cross-layer completion validator/report')
SCOPE_ES=('perímetro v0.12 congelado + cierre técnico LTMD-U1 W8 Artes con fuente admisible: 20 identidades históricas preservadas, 16 objetos canónicos de procesamiento directo, cuatro identidades 2018 retenidas por fuente sin imputación, 1,490 páginas fuente trazadas por SHA, OCR/PAGESTRUCT/FRAGSEG cerrados, productos de dependencia textual exacta, controles explícitos de despacho y validador/informe transversal de cierre W8')

V13_CRITICAL=[
'data/catalog/ltmd_u1_w8_scope.csv','data/catalog/ltmd_u1_w8_scope.md','scripts/build_ltmd_u1_w8_artes_scope.py',
'data/catalog/ltmd_u1_w8_viewer_architecture.csv','data/catalog/ltmd_u1_w8_viewer_architecture.md','scripts/audit_ltmd_u1_w8_artes_architecture.py',
'data/catalog/ltmd_u1_w8_declared_inventory.csv','data/catalog/ltmd_u1_w8_declared_inventory_summary.csv','data/catalog/ltmd_u1_w8_declared_inventory.md','scripts/build_ltmd_u1_w8_artes_declared_inventory.py',
'data/catalog/ltmd_u1_w8_artes_asset_manifest.csv','data/catalog/ltmd_u1_w8_artes_asset_summary.csv','data/catalog/ltmd_u1_w8_artes_asset_audit.md','scripts/audit_ltmd_u1_w8_artes_assets_book.py',
'data/catalog/ltmd_u1_w8_artes_source_admissibility.csv','docs/LTMD_U1_W8_ARTES_SOURCE_ADMISSIBILITY.md','scripts/audit_ltmd_u1_w8_artes_source_admissibility.py',
'data/catalog/ltmd_u1_w8_processing_inventory.csv','data/catalog/ltmd_u1_w8_canonical_page_manifest.csv','docs/LTMD_U1_W8_ARTES_PROCESSING_TOPOLOGY.md','scripts/build_ltmd_u1_w8_artes_processing_topology.py','.github/workflows/ltmd-u1-w8-processing-topology-publish.yml',
'data/catalog/ltmd_u1_w8_artes_ocr_metrics.csv','data/catalog/ltmd_u1_w8_artes_ocr_summary.csv','data/catalog/ltmd_u1_w8_artes_ocr.md','scripts/ocr_ltmd_u1_w8_artes_book.py','scripts/combine_ltmd_u1_w8_artes_ocr.py','.github/workflows/build-ltmd-u1-w8-artes-ocr.yml',
'data/catalog/ltmd_u1_w8_artes_structural_keyword_flags.csv','data/catalog/ltmd_u1_w8_artes_page_structure.csv','data/catalog/ltmd_u1_w8_artes_page_structure_summary.csv','data/catalog/ltmd_u1_w8_artes_page_structure.md','scripts/extract_ltmd_u1_w8_artes_structural_flags_book.py','scripts/combine_ltmd_u1_w8_artes_structural_flags.py','scripts/classify_ltmd_u1_w8_artes_page_structure.py','.github/workflows/build-ltmd-u1-w8-artes-pagestruct.yml',
'data/catalog/ltmd_u1_w8_artes_fragment_manifest.csv','data/catalog/ltmd_u1_w8_artes_fragment_manifest_summary.csv','data/catalog/ltmd_u1_w8_artes_fragment_sequence_gaps.csv','data/catalog/ltmd_u1_w8_artes_fragment_manifest.md','scripts/segment_ltmd_u1_w8_artes_fragments.py','scripts/combine_ltmd_u1_w8_artes_fragment_shards.py','.github/workflows/build-ltmd-u1-w8-artes-fragseg.yml',
'data/catalog/ltmd_u1_w8_artes_exact_content_units.csv','data/catalog/ltmd_u1_w8_artes_exact_viewer_overlap.csv','data/catalog/ltmd_u1_w8_artes_exact_reuse.md','scripts/analyze_ltmd_u1_w8_artes_exact_reuse.py','.github/workflows/dispatch-ltmd-u1-w8-artes-exact-reuse.yml','data/control/ltmd_u1_w8_artes_exact_reuse_trigger.txt',
'docs/LTMD_U1_W8_COMPLETION.md','scripts/build_ltmd_u1_w8_completion_report.py','.github/workflows/build-ltmd-u1-w8-completion-report.yml','data/control/ltmd_u1_w8_completion_trigger.txt',
'scripts/build_research_integrity_manifest_v13.py']
for path in V13_CRITICAL:
    if path not in base.CRITICAL: base.CRITICAL.append(path)

def main():
    v12.main()
    data=json.loads(base.OUT.read_text(encoding='utf-8'));data['scope']=SCOPE;base.OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=base.REPORT.read_text(encoding='utf-8');old=f'Alcance: {v12.SCOPE_ES}.';new=f'Alcance: {SCOPE_ES}.'
    if old not in report: raise SystemExit('LTMD_INTEGRITY_0.13 scope postprocessor could not locate v0.12 scope line')
    base.REPORT.write_text(report.replace(old,new,1),encoding='utf-8')
if __name__=='__main__': main()
