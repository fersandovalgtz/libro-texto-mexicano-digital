#!/usr/bin/env python3
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

MAN=Path('data/catalog/ltmd_u1_w2_math_reconciled_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w2_math_reconciled_summary.csv')
OUT=Path('data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv')
REPORT=Path('data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.md')
VERSION='LTMD_U1_W2_MATH_RECONCILED_EXACT_ALIASES_0.1'

def load(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main():
    manifest=load(MAN); summary=load(SUMMARY)
    ready={r['viewer_key']:r for r in summary if int(r['effective_asset_ready'])==1}
    by=defaultdict(list)
    for r in manifest:
        if r['viewer_key'] in ready and r['effective_asset_status'] in ('source_jpeg','source_jpeg_recovered'):
            by[r['viewer_key']].append(r)
    signatures=defaultdict(list)
    for v,rr in by.items():
        rr.sort(key=lambda r:int(r['viewer_page']))
        sig=tuple((int(r['viewer_page']),r['effective_sha256'],int(r['effective_byte_size'])) for r in rr)
        expected=int(ready[v]['effective_real_jpeg'])
        if len(sig)!=expected or any(not sha for _,sha,_ in sig):raise SystemExit(f'incomplete effective signature {v}')
        signatures[sig].append(v)
    aliases=[]; group=0
    for sig,vs in sorted(signatures.items(),key=lambda x:x[1]):
        if len(vs)<2:continue
        group+=1; vs=sorted(vs); canonical=vs[0]
        for v in vs[1:]:
            aliases.append({'alias_version':VERSION,'alias_group':f'MATH-RECON-ALIAS-{group:03d}','viewer_key':v,'canonical_viewer_key':canonical,'effective_jpeg_count':len(sig),'all_effective_pages_byte_identical_aligned':1,'interpretive_limit':'Operational byte alias on reconciled assets only; catalog identities remain distinct.'})
    fields=['alias_version','alias_group','viewer_key','canonical_viewer_key','effective_jpeg_count','all_effective_pages_byte_identical_aligned','interpretive_limit']
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(aliases)
    lines=['# LTMD-U1 W2 — aliases exactos sobre manifiesto reconciliado','',f'Versión: `{VERSION}`.','',f'- Visores efectivamente resueltos: **{len(ready)}**.',f'- Grupos exactos: **{len({r["alias_group"] for r in aliases})}**.',f'- Visores alias adicionales al canónico: **{len(aliases)}**.','','Se exige identidad completa de `(viewer_page, SHA-256, byte_size)` sobre todos los JPEG efectivos. Las páginas recuperadas participan con su SHA efectivo; no se usa similitud textual ni metadata para declarar alias.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
