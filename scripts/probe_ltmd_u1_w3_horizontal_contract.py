#!/usr/bin/env python3
from __future__ import annotations
import csv,re,json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request,urlopen
EX=Path('data/catalog/ltmd_u1_w3_architecture_exceptions.csv');OUT=Path('data/catalog/ltmd_u1_w3_horizontal_contract.csv');REPORT=Path('data/catalog/ltmd_u1_w3_horizontal_contract.md');VERSION='LTMD_U1_W3_HORIZONTAL_CONTRACT_0.1';UA='LibroTextoMexicanoDigital/U1-W3 horizontal contract probe'
def get(url):
 with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:return r.read().decode('utf-8','replace')
def main():
 ex=list(csv.DictReader(EX.open(encoding='utf-8')));rows=[]
 for r in ex:
  base=r['source_url'].rsplit('/',1)[0]+'/';js=get(urljoin(base,'x_horizontal.js'))
  vars={}
  for name,val in re.findall(r'\b(?:var\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(["\'][^"\']*["\']|\d+)',js):vars.setdefault(name,val.strip('"\''))
  patterns=sorted(set(re.findall(r'[A-Za-z0-9_./?&=+%-]{3,}\.(?:jpg|jpeg|png|json|js)',js,re.I)))
  rows.append({'probe_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'x_horizontal_url':urljoin(base,'x_horizontal.js'),'js_chars':len(js),'variable_literals':json.dumps(vars,ensure_ascii=False,sort_keys=True),'asset_patterns':json.dumps(patterns[:100],ensure_ascii=False),'mentions_ag_pages':int('ag_pages' in js),'mentions_ag_clave':int('ag_clave' in js),'mentions_claves_json':int('claves.json' in js),'mentions_magazine':int('magazine' in js.lower())})
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 lines=['# LTMD-U1 W3 — contrato de visores horizontales','',f'Versión: `{VERSION}`.','']
 for r in rows:lines += [f"## {r['viewer_key']}",f"- `x_horizontal.js`: {r['js_chars']} caracteres.",f"- menciona `ag_pages`: {r['mentions_ag_pages']}; `ag_clave`: {r['mentions_ag_clave']}; `claves.json`: {r['mentions_claves_json']}; `magazine`: {r['mentions_magazine']}.",f"- literales observados: `{r['variable_literals'][:1200]}`",f"- patrones de activos: `{r['asset_patterns'][:800]}`",'']
 lines+=['El probe analiza únicamente el JavaScript de arquitectura. No descarga ni persiste páginas del libro.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
