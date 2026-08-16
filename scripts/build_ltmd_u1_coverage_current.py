#!/usr/bin/env python3
"""Build current LTMD-U1 coverage by extending the frozen 0.2 baseline with W1 evidence.

The baseline builder remains intact for reproducibility. This wrapper reruns it,
then promotes W1 viewer stages only when their final artifact for that stage exists
and passes conservative cardinality/status checks.
"""
from __future__ import annotations
import csv,subprocess
from collections import defaultdict
from pathlib import Path

BASE_SCRIPT='scripts/build_ltmd_u1_coverage.py'
COVERAGE=Path('data/catalog/ltmd_u1_coverage.csv')
SUMMARY=Path('data/catalog/ltmd_u1_coverage_summary.csv')
DOMAIN=Path('data/catalog/ltmd_u1_domain_summary.csv')
QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
REPORT=Path('data/catalog/ltmd_u1_coverage.md')
W1_SCOPE=Path('data/catalog/ltmd_u1_w1_scope.csv')
W1_ASSET=Path('data/catalog/ltmd_u1_w1_1966_page_manifest_summary.csv')
W1_OCR=Path('data/catalog/ltmd_u1_w1_1966_ocr_summary.csv')
W1_PS=Path('data/catalog/ltmd_u1_w1_1966_page_structure_summary.csv')
W1_FRAG=Path('data/catalog/ltmd_u1_w1_1966_fragment_manifest_summary.csv')
VERSION='LTMD_U1_COVERAGE_0.3'
U=542

def rows(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def write_rows(p,rr):
    with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)

def main():
    subprocess.run(['python3',BASE_SCRIPT],check=True)
    cov=rows(COVERAGE)
    if len(cov)!=U:raise SystemExit(f'baseline coverage rows={len(cov)} expected={U}')
    byv={r['viewer_key']:r for r in cov}
    scope={r['viewer_key']:r for r in rows(W1_SCOPE)} if W1_SCOPE.exists() else {}
    book_to_viewer={r['book_id']:r['viewer_key'] for r in scope.values()}

    # Stage 1: source asset layer (includes page manifest readiness).
    if W1_ASSET.exists():
        for s in rows(W1_ASSET):
            v=book_to_viewer.get(s['book_id'])
            if not v:continue
            if int(s['asset_layer_ready'])!=1 or int(s['internal_unserved'])!=0:continue
            r=byv[v];r['book_id']=s['book_id'];r['asset_status']='full_direct_w1_1966';r['asset_resolved_full']='1';r['asset_resolved_partial']='0';r['page_manifest_ready']='1'

    # Stage 2: OCR. Require all source pages SHA verified and no unresolved.
    if W1_OCR.exists():
        for s in rows(W1_OCR):
            v=book_to_viewer.get(s['book_id'])
            if not v:continue
            if int(s['pages'])==int(s['sha_verified']) and int(s['unresolved'])==0:
                byv[v]['ocr_ready']='1'

    # Stage 3: PAGESTRUCT. The per-book page count must match the OCR source-page count.
    if W1_PS.exists() and W1_OCR.exists():
        ocr={r['book_id']:r for r in rows(W1_OCR)}
        for s in rows(W1_PS):
            if s['book_id']=='ALL':continue
            v=book_to_viewer.get(s['book_id'])
            if v and s['book_id'] in ocr and int(s['n_pages'])==int(ocr[s['book_id']]['pages']):byv[v]['pagestruct_ready']='1'

    # Stage 4: FRAGSEG. Only final per-book summary promotes direct/effective coverage.
    if W1_FRAG.exists():
        for s in rows(W1_FRAG):
            if s['book_id']=='ALL':continue
            v=book_to_viewer.get(s['book_id'])
            if not v:continue
            if int(s['fragment_count'])>0 and int(s['segmented_page_count'])>0:
                r=byv[v];r['fragseg_materialized']='1';r['effective_fragseg_coverage']='1';r['fragment_count_materialized']=s['fragment_count'];r['wave_priority']='0';r['wave_label']='U1-W0-materializado';r['queue_status']='materialized_direct'

    # Stamp version after all promotions.
    for r in cov:r['coverage_version']=VERSION
    write_rows(COVERAGE,cov)

    def cnt(field):return sum(int(r[field]) for r in cov)
    stages=[
      ('cataloged',cnt('cataloged'),'All viewers in frozen U1 catalog snapshot.'),
      ('title_normalized',cnt('title_normalized'),'Normalized title-core families.'),
      ('asset_resolved_full',cnt('asset_resolved_full'),'Full source-asset resolution demonstrated.'),
      ('asset_resolved_partial',cnt('asset_resolved_partial'),'Known partial source resolution; separate from full coverage.'),
      ('page_manifest_ready_direct',cnt('page_manifest_ready'),'Direct page/source manifest materialized.'),
      ('ocr_ready_direct',cnt('ocr_ready'),'Direct technical OCR layer materialized.'),
      ('pagestruct_ready_direct',cnt('pagestruct_ready'),'Direct PAGESTRUCT layer materialized.'),
      ('fragseg_materialized_direct',cnt('fragseg_materialized'),'Direct FRAGSEG materialized.'),
      ('effective_fragseg_coverage',cnt('effective_fragseg_coverage'),'Direct FRAGSEG plus verified byte-identical aliases.'),
      ('dependence_audited',cnt('dependence_audited'),'Viewer participates in registered documentary dependence.'),
      ('semantic_ready_validated',0,'SEMB 0.3 remains WAITING_HUMAN_REFERENCE.'),
    ]
    srows=[{'coverage_version':VERSION,'stage':s,'viewer_count':n,'universe_viewers':U,'percent':f'{100*n/U:.2f}','notes':note} for s,n,note in stages]
    write_rows(SUMMARY,srows)

    grouped=defaultdict(list)
    for r in cov:grouped[r['operational_domain']].append(r)
    # Preserve operational wave numbering already present on queued rows. For domains with
    # materialized rows, recover next wave from any queued row or prior domain output.
    old_domain={r['operational_domain']:r for r in rows(DOMAIN)} if DOMAIN.exists() else {}
    drows=[]
    for domain,rr in grouped.items():
        total=len(rr);direct=sum(int(r['fragseg_materialized']) for r in rr);effective=sum(int(r['effective_fragseg_coverage']) for r in rr);full=sum(int(r['asset_resolved_full']) for r in rr)
        prior=old_domain.get(domain,{})
        wave=prior.get('next_wave_label') or next((r['wave_label'] for r in rr if r['queue_status']=='queued'),'completed_domain')
        priority=prior.get('next_wave_priority') or next((r['wave_priority'] for r in rr if r['queue_status']=='queued'),'0')
        drows.append({'coverage_version':VERSION,'operational_domain':domain,'viewer_count':total,'percent_of_u1':f'{100*total/U:.2f}','asset_resolved_full':full,'fragseg_materialized_direct':direct,'effective_fragseg_coverage':effective,'remaining_effective':total-effective,'next_wave_priority':priority,'next_wave_label':wave})
    drows.sort(key=lambda r:(int(r['next_wave_priority']) if str(r['next_wave_priority']).isdigit() else 999,r['operational_domain']))
    write_rows(DOMAIN,drows)

    qf=['coverage_version','wave_priority','wave_label','queue_status','operational_domain','viewer_key','catalog_generation','grade_code','title_core','asset_status','effective_fragseg_coverage','coverage_inherited_from_viewer','source_url']
    qrows=sorted(cov,key=lambda r:(int(r['wave_priority']),int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    with QUEUE.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=qf);w.writeheader();w.writerows([{k:r[k] for k in qf} for r in qrows])

    sm={s:n for s,n,_ in stages};families=191
    lines=['# LTMD-U1 — tablero maestro de cobertura','',f'Versión: **{VERSION}**  ',f'Universo operativo U1: **{U} visores**.  ',f'Familias normalizadas de título: **{families}**.','', '## Estado ejecutivo','',
      f"- Catálogo censado: **{sm['cataloged']}/{U} ({100*sm['cataloged']/U:.2f}%)**.",
      f"- Títulos normalizados: **{sm['title_normalized']}/{U} ({100*sm['title_normalized']/U:.2f}%)**.",
      f"- Activos completamente resueltos: **{sm['asset_resolved_full']}/{U} ({100*sm['asset_resolved_full']/U:.2f}%)**; parciales documentados: **{sm['asset_resolved_partial']}**.",
      f"- Manifiesto directo: **{sm['page_manifest_ready_direct']}/{U} ({100*sm['page_manifest_ready_direct']/U:.2f}%)**.",
      f"- OCR directo: **{sm['ocr_ready_direct']}/{U} ({100*sm['ocr_ready_direct']/U:.2f}%)**.",
      f"- PAGESTRUCT directo: **{sm['pagestruct_ready_direct']}/{U} ({100*sm['pagestruct_ready_direct']/U:.2f}%)**.",
      f"- FRAGSEG directo: **{sm['fragseg_materialized_direct']}/{U} ({100*sm['fragseg_materialized_direct']/U:.2f}%)**.",
      f"- Cobertura FRAGSEG efectiva: **{sm['effective_fragseg_coverage']}/{U} ({100*sm['effective_fragseg_coverage']/U:.2f}%)**.",
      f"- Dependencia documental auditada: **{sm['dependence_audited']}/{U} ({100*sm['dependence_audited']/U:.2f}%)**.",
      '- Cobertura semántica validada: **0/542 (0.00%)**.','',
      'Los KPIs se promueven por etapa sólo cuando existe el artefacto final correspondiente. Un visor puede tener activos/OCR/PAGESTRUCT listos sin contar aún como FRAGSEG.','', '## Cobertura por dominio operativo','',
      '| dominio | visores | % U1 | activos full | FRAGSEG directo | cobertura efectiva | restantes | próxima ola |','|---|---:|---:|---:|---:|---:|---:|---|']
    for r in drows:lines.append(f"| {r['operational_domain']} | {r['viewer_count']} | {r['percent_of_u1']}% | {r['asset_resolved_full']} | {r['fragseg_materialized_direct']} | {r['effective_fragseg_coverage']} | {r['remaining_effective']} | {r['next_wave_label']} |")
    lines += ['', '## Límites de lectura','', '- `cataloged` no significa `asset_resolved`.','- `asset_resolved` no significa `ocr_ready`.','- `fragseg_materialized` no significa `semantic_ready`.','- Cobertura efectiva por alias conserva identidad documental y evita reprocesar bytes demostrados como idénticos.','- La taxonomía de dominios es logística, no una ontología curricular.','', '## Archivos','', '- `data/catalog/ltmd_u1_coverage.csv`','- `data/catalog/ltmd_u1_coverage_summary.csv`','- `data/catalog/ltmd_u1_domain_summary.csv`','- `data/catalog/ltmd_u1_wave_queue.csv`']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"{VERSION}: assets={sm['asset_resolved_full']} ocr={sm['ocr_ready_direct']} pagestruct={sm['pagestruct_ready_direct']} fragseg={sm['fragseg_materialized_direct']} effective={sm['effective_fragseg_coverage']}")

if __name__=='__main__':main()
