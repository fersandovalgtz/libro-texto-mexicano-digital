#!/usr/bin/env python3
"""Audit W11 pipeline contracts without executing source/OCR processing.

This QA layer validates published topology/admissibility invariants, Python
syntax, downstream workflow_run chaining, coverage gating, and the absence of
tracked source-image work products. It does not promote W11 coverage.
"""
from __future__ import annotations
import ast,csv,subprocess
from collections import Counter
from pathlib import Path

ROOT=Path('.')
REPORT=Path('docs/LTMD_U1_W11_PIPELINE_AUDIT.md')
VERSION='LTMD_U1_W11_PIPELINE_AUDIT_0.1'
EXPECTED=111

PYTHON_FILES=[
 'scripts/build_ltmd_u1_w11_source_admissibility.py',
 'scripts/build_ltmd_u1_w11_processing_topology.py',
 'scripts/ocr_ltmd_u1_w11_book.py',
 'scripts/combine_ltmd_u1_w11_ocr.py',
 'scripts/extract_ltmd_u1_w11_structural_flags_book.py',
 'scripts/combine_ltmd_u1_w11_structural_flags.py',
 'scripts/classify_ltmd_u1_w11_page_structure.py',
 'scripts/segment_ltmd_u1_w11_fragments.py',
 'scripts/combine_ltmd_u1_w11_fragment_shards.py',
 'scripts/analyze_ltmd_u1_w11_exact_reuse.py',
 'scripts/build_ltmd_u1_w11_completion_report.py',
 'scripts/build_ltmd_u1_coverage_dashboard.py',
 'scripts/sync_readme_coverage.py',
]
CHAIN=[
 ('.github/workflows/build-ltmd-u1-w11-ocr.yml','build-ltmd-u1-w11-processing-topology'),
 ('.github/workflows/build-ltmd-u1-w11-pagestruct.yml','build-ltmd-u1-w11-ocr'),
 ('.github/workflows/build-ltmd-u1-w11-fragseg.yml','build-ltmd-u1-w11-pagestruct'),
 ('.github/workflows/build-ltmd-u1-w11-exact-reuse.yml','build-ltmd-u1-w11-fragseg'),
 ('.github/workflows/build-ltmd-u1-w11-completion.yml','build-ltmd-u1-w11-exact-reuse'),
]

def rows(path:str):
    p=ROOT/path
    if not p.exists():raise SystemExit(f'missing contract input: {path}')
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def req(cond:bool,msg:str):
    if not cond:raise SystemExit(f'W11 pipeline contract audit failed: {msg}')

def main():
    # Python syntax is checked without importing/running pipeline code.
    for path in PYTHON_FILES:
        p=ROOT/path;req(p.exists(),f'missing Python file {path}')
        try:ast.parse(p.read_text(encoding='utf-8'),filename=path)
        except SyntaxError as exc:raise SystemExit(f'Python syntax error {path}: {exc}')

    # Published source gate and topology must describe the same 111 identities.
    adm=rows('data/catalog/ltmd_u1_w11_source_admissibility.csv')
    proc=rows('data/catalog/ltmd_u1_w11_processing_inventory.csv')
    man=rows('data/catalog/ltmd_u1_w11_canonical_page_manifest.csv')
    req(len(adm)==EXPECTED and len({r['viewer_key'] for r in adm})==EXPECTED,'admissibility cardinality')
    req(len(proc)==EXPECTED and len({r['viewer_key'] for r in proc})==EXPECTED,'topology cardinality')
    req({r['viewer_key'] for r in adm}=={r['viewer_key'] for r in proc},'admissibility/topology identity drift')
    adm_by={r['viewer_key']:r for r in adm};proc_by={r['viewer_key']:r for r in proc}
    admitted={k for k,r in adm_by.items() if r['ocr_source_admitted']=='1'}
    withheld=set(adm_by)-admitted
    proc_admitted={k for k,r in proc_by.items() if r['source_admitted']=='1'}
    canonical={k for k,r in proc_by.items() if r['is_canonical_processing_object']=='1'}
    aliases={k for k,r in proc_by.items() if r['processing_mode']=='exact_source_alias'}
    req(admitted==proc_admitted,'source-admitted partition drift')
    req(admitted|withheld==set(adm_by) and not admitted&withheld,'admitted/withheld partition invalid')
    req(canonical<=admitted and aliases<=admitted,'canonical/alias outside admitted cohort')
    req(all(proc_by[k]['processing_mode']=='direct_canonical' for k in canonical),'canonical mode drift')
    req(all(proc_by[k]['processing_mode']=='withheld_source' for k in withheld),'withheld mode drift')
    req(all(proc_by[k]['canonical_viewer_key'] in canonical for k in aliases),'alias target outside canonical set')
    req(len(man)==sum(int(proc_by[k]['source_pages']) for k in canonical),'canonical manifest page cardinality')
    req({r['viewer_key'] for r in man}==canonical,'canonical manifest viewer coverage')
    req(len({r['page_id'] for r in man})==len(man),'duplicate canonical page IDs')
    req(all(r['asset_status']=='source_jpeg' and len(r['sha256'])==64 and int(r['byte_size'])>0 for r in man),'canonical manifest provenance fields')

    # Retained-hole evidence must account exactly for internal holes of withheld identities.
    holes=rows('data/catalog/ltmd_u1_w11_retained_source_holes.csv')
    req({r['viewer_key'] for r in holes}==withheld,'retained-hole identity set does not equal withheld set')
    expected_holes=sum(int(adm_by[k]['internal_unserved']) for k in withheld)
    req(len(holes)==expected_holes,'retained-hole row count does not match source gate')
    req(len({(r['viewer_key'],r['viewer_page'],r['source_image_index']) for r in holes})==len(holes),'duplicate retained-hole positions')

    # Downstream workflow_run chain is explicit.
    for path,upstream in CHAIN:
        p=ROOT/path;req(p.exists(),f'missing workflow {path}')
        text=p.read_text(encoding='utf-8')
        req('workflow_run:' in text and upstream in text,f'{path} does not declare upstream {upstream}')
        req('cancel-in-progress: false' in text,f'{path} concurrency must preserve active scientific runs')

    # Current coverage must keep W11 at zero until the completion report exists.
    cov=rows('data/catalog/ltmd_u1_coverage_summary.csv');w11=[r for r in cov if r['wave']=='W11']
    req(len(w11)==1,'coverage summary missing unique W11 row');w11=w11[0]
    completion=(ROOT/'docs/LTMD_U1_W11_COMPLETION.md').exists()
    if completion:
        req(int(w11['effective_technical_identities'])==len(admitted),'completed W11 effective coverage mismatch')
        req(int(w11['canonical_processing_objects'])==len(canonical),'completed W11 canonical coverage mismatch')
    else:
        req(w11['effective_technical_identities']=='0' and w11['canonical_processing_objects']=='0','W11 promoted before technical completion')

    # No transient/source raster should be tracked inside data/work or data/catalog.
    cp=subprocess.run(['git','ls-files','data'],capture_output=True,text=True,check=True)
    tracked=[x.strip() for x in cp.stdout.splitlines() if x.strip()]
    forbidden_ext={'.jpg','.jpeg','.png','.tif','.tiff','.webp','.bmp'}
    bad=[p for p in tracked if p.startswith('data/work/') or (p.startswith('data/catalog/') and Path(p).suffix.lower() in forbidden_ext)]
    req(not bad,f'tracked transient/source raster files: {bad[:10]}')

    states=Counter(r['source_state'] for r in adm)
    lines=['# LTMD-U1 W11 — auditoría contractual del pipeline','',f'Versión: `{VERSION}`.','',
           'Esta auditoría valida contratos e invariantes ya publicados; no ejecuta OCR ni modifica cobertura.','',
           '## Resultado',
           f'- Scripts Python auditados sintácticamente: **{len(PYTHON_FILES)}/{len(PYTHON_FILES)}**.',
           f'- Workflows downstream con `workflow_run` explícito: **{len(CHAIN)}/{len(CHAIN)}**.',
           f'- Identidades W11 reconciliadas: **{len(proc)}/{EXPECTED}**.',
           f'- Fuente admitida: **{len(admitted)}/{EXPECTED}**.',
           f'- Retenidas: **{len(withheld)}/{EXPECTED}**.',
           f'- Objetos canónicos: **{len(canonical)}**.',
           f'- Aliases byte-exactos: **{len(aliases)}**.',
           f'- Páginas canónicas: **{len(man):,}**.',
           f'- Huecos internos materializados: **{len(holes)}/{expected_holes}**.',
           f'- Cobertura W11 promovida: **{"sí" if completion else "no; correctamente bloqueada hasta el cierre"}**.',
           '- Rasters fuente/transitorios rastreados bajo `data/`: **0**.','','## Estados de fuente']
    for state,n in sorted(states.items()):lines.append(f'- `{state}`: **{n}**.')
    lines+=['','## Límite','El resultado `PASS` de esta auditoría demuestra coherencia interna del contrato técnico W11 en el corte auditado. No demuestra que OCR/PAGESTRUCT/FRAGSEG hayan terminado si sus artefactos finales aún no existen, ni convierte `otros_no_clasificados` en categoría semántica. `WAITING_HUMAN_REFERENCE` continúa vigente.','', '**Estado: PASS**']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
