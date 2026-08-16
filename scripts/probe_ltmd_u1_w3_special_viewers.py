#!/usr/bin/env python3
from __future__ import annotations
import csv,re,json
from pathlib import Path
from urllib.request import Request,urlopen

EX=Path('data/catalog/ltmd_u1_w3_architecture_exceptions.csv')
OUT=Path('data/catalog/ltmd_u1_w3_special_viewer_probe.csv')
REPORT=Path('data/catalog/ltmd_u1_w3_special_viewer_probe.md')
VERSION='LTMD_U1_W3_SPECIAL_VIEWER_PROBE_0.1'
UA='LibroTextoMexicanoDigital/U1-W3 special viewer probe'

def fetch(url):
 with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:return r.read().decode('utf-8','replace')
def clean(x):return re.sub(r'\s+',' ',x).strip()
def main():
 rows=list(csv.DictReader(EX.open(encoding='utf-8')));out=[]
 for r in rows:
  html=fetch(r['source_url']);scripts=re.findall(r'<script[^>]+src=["\']([^"\']+)',html,re.I);styles=re.findall(r'<link[^>]+href=["\']([^"\']+)',html,re.I);imgs=re.findall(r'<img[^>]+src=["\']([^"\']+)',html,re.I);hrefs=re.findall(r'<a[^>]+href=["\']([^"\']+)',html,re.I)
  tokens=sorted(set(re.findall(r'[A-Za-z0-9_./?-]{3,}\.(?:js|json|jpg|jpeg|png|pdf)(?:\?[^"\'\s<]*)?',html,re.I)))
  out.append({'probe_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'script_srcs':json.dumps(scripts,ensure_ascii=False),'style_hrefs':json.dumps(styles,ensure_ascii=False),'img_srcs':json.dumps(imgs[:20],ensure_ascii=False),'anchor_hrefs_sample':json.dumps(hrefs[:30],ensure_ascii=False),'asset_tokens':json.dumps(tokens[:100],ensure_ascii=False),'html_chars':len(html),'source_url':r['source_url']})
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 lines=['# LTMD-U1 W3 — probe de visores especiales','',f'Versión: `{VERSION}`.','']
 for r in out:
  lines += [f"## {r['viewer_key']}",f"- Scripts: `{r['script_srcs']}`",f"- Tokens de activos detectados: `{r['asset_tokens'][:800]}`",'']
 lines+=['Este probe persiste únicamente referencias estructurales observadas en el HTML, no contenido de páginas.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
