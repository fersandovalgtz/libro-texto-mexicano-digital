#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
from urllib.request import Request,urlopen

OUT=Path('data/catalog/ltmd_u1_w2_math_dma_config.csv')
REPORT=Path('data/catalog/ltmd_u1_w2_math_dma_config.md')
UA='LibroTextoMexicanoDigital/U1-W2 DMA config audit'
PAIRS=[
 ('H2018P3DMA','H2019P3DMA'),('H2018P4DMA','H2019P4DMA'),
 ('H2018P5DMA','H2019P5DMA'),('H2018P6DMA','H2019P6DMA'),
]

def norm(v):
    if isinstance(v,(dict,list)): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    if v is None:return ''
    return str(v)

def main():
    with urlopen(Request('https://historico.conaliteg.gob.mx/claves.json',headers={'User-Agent':UA}),timeout=45) as r:
        cfg=json.loads(r.read().decode('utf-8-sig'))
    keys=sorted({k for a,b in PAIRS for k in (cfg.get(a,{})|cfg.get(b,{})).keys()})
    fields=['viewer_key','pair_key','catalog_generation']+keys
    rows=[]
    for a,b in PAIRS:
        for vk,g in ((a,'2018'),(b,'2019')):
            d=cfg.get(vk)
            if not isinstance(d,dict): raise SystemExit(f'missing config {vk}')
            row={'viewer_key':vk,'pair_key':a.replace('2018','PAIR'),'catalog_generation':g}
            for k in keys: row[k]=norm(d.get(k))
            rows.append(row)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    lines=['# LTMD-U1 W2 — configuración DMA 2018/2019','',f'Campos observados en `claves.json`: `{", ".join(keys)}`.','']
    for a,b in PAIRS:
        ca,cb=cfg[a],cfg[b]
        allkeys=sorted(set(ca)|set(cb))
        same=[k for k in allkeys if ca.get(k)==cb.get(k)]
        diff=[k for k in allkeys if ca.get(k)!=cb.get(k)]
        lines += [f'## {a} ↔ {b}',f'- Campos idénticos: {same}',f'- Campos distintos: {diff}','']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text())
if __name__=='__main__':main()
