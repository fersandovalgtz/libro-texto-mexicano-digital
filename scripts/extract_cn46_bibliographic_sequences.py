#!/usr/bin/env python3
"""Extract strict bibliographic sequences from CN4/CN6 front matter ephemerally.

Unlike the broad regex audit, this parser only persists facts attached to explicit
bibliographic phrases (primera/segunda/tercera edición, reimpresión, D.R./derechos
reservados, ISBN). OCR text itself is never committed.
"""
from __future__ import annotations
import csv,json,re,subprocess,tempfile,unicodedata
from pathlib import Path
from urllib.request import Request,urlopen

DISC=Path('data/expansion/cn46_viewer_candidates.csv')
OUT=Path('data/expansion/cn46_bibliographic_sequences.csv')
REPORT=Path('data/expansion/cn46_bibliographic_sequences.md')
BASE='https://historico.conaliteg.gob.mx/'
UA='LibroTextoMexicanoDigital/0.1 strict bibliography audit'
VERSION='CN46_BIBSEQ_0.1'

def get(url):
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:return r.read()

def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[\r\n\t]+',' ',s);s=re.sub(r'\s+',' ',s)
    return s.strip()

def run(img,base,psm):
    p=subprocess.run(['tesseract',str(img),str(base),'-l','spa','--psm',str(psm)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    fp=base.with_suffix('.txt')
    return fp.read_text(encoding='utf-8',errors='replace') if p.returncode==0 and fp.exists() else ''

def best(img,stem):
    candidates=[]
    for psm in (3,4,6,11,12):
        txt=run(img,stem.with_name(stem.name+f'_p{psm}'),psm)
        candidates.append((sum(c.isalnum() for c in txt),txt))
    return max(candidates,default=(0,''))[1]

def book_id(r):
    if r['viewer_key']=='H1993P6CI209':return 'LTMD-CN6-G1993-DH'
    if r['viewer_key']=='H1993P6CI210':return 'LTMD-CN6-G1993-CN'
    return f"LTMD-CN{r['grade']}-G{r['catalog_generation']}"

def imgurl(key,p):return f'{BASE}c/{key}/{0 if p==1 else p:03d}.jpg'

def extract(text):
    t=norm(text)
    rec=[]
    ordmap={'primera':1,'segunda':2,'tercera':3,'cuarta':4,'quinta':5,'sexta':6,'septima':7,'octava':8,'novena':9,'decima':10}
    # Tight windows reduce accidental years from nearby credits/bibliography.
    for m in re.finditer(r'\b(primera|segunda|tercera|cuarta|quinta|sexta|septima|octava|novena|decima)\s+edici[o0]n\b.{0,45}?\b(19\d{2}|20\d{2})\b',t):
        rec.append(('edition',ordmap[m.group(1)],m.group(2),'explicit_ordinal_edition'))
    for m in re.finditer(r'\bedici[o0]n\s+revisada\b.{0,45}?\b(19\d{2}|20\d{2})\b',t):rec.append(('edition_revised','',m.group(1),'explicit_revised_edition'))
    for m in re.finditer(r'\b(primera|segunda|tercera|cuarta|quinta|sexta|septima|octava|novena|decima)\s+reimpresi[o0]n\b.{0,45}?\b(19\d{2}|20\d{2})\b',t):rec.append(('reprint',ordmap[m.group(1)],m.group(2),'explicit_ordinal_reprint'))
    for m in re.finditer(r'\breimpresi[o0]n\b.{0,35}?\b(19\d{2}|20\d{2})\b',t):rec.append(('reprint','',m.group(1),'explicit_reprint'))
    for m in re.finditer(r'(?:derechos\s+reservados|d\.?\s*r\.?|copyright)\b.{0,70}?\b(19\d{2}|20\d{2})\b',t):rec.append(('copyright','',m.group(1),'explicit_rights'))
    isb=[]
    for m in re.finditer(r'\bisbn\s*[:\-]?\s*([0-9x][0-9x\-\s]{7,24}[0-9x])',t,re.I):
        raw=re.sub(r'\s+',' ',m.group(1)).strip(' .,:;');digits=re.sub(r'[^0-9Xx]','',raw)
        if len(digits) in {10,13}:isb.append(raw)
    return sorted(set(rec)),sorted(set(isb))

def main():
    viewers=[r for r in csv.DictReader(DISC.open(encoding='utf-8')) if r['verification_status']=='verified_title']
    rows=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-bibseq-') as td:
        td=Path(td)
        for r in viewers:
            key=r['viewer_key'];bid=book_id(r)
            for p in range(1,9):
                img=td/f'{key}_{p}.jpg';stem=td/f'{key}_{p}'
                try:
                    img.write_bytes(get(imgurl(key,p)));text=best(img,stem);seq,isb=extract(text)
                    if seq or isb:
                        if not seq:rows.append({'audit_version':VERSION,'book_id':bid,'viewer_key':key,'viewer_page':p,'fact_type':'isbn','ordinal':'','year':'','value':x,'evidence_class':'explicit_isbn'}) for x in isb
                        else:
                            for typ,ordinal,year,ev in seq:rows.append({'audit_version':VERSION,'book_id':bid,'viewer_key':key,'viewer_page':p,'fact_type':typ,'ordinal':ordinal,'year':year,'value':'','evidence_class':ev})
                            for x in isb:rows.append({'audit_version':VERSION,'book_id':bid,'viewer_key':key,'viewer_page':p,'fact_type':'isbn','ordinal':'','year':'','value':x,'evidence_class':'explicit_isbn'})
                except Exception:pass
                for f in td.iterdir():
                    try:f.unlink()
                    except Exception:pass
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['audit_version','book_id','viewer_key','viewer_page','fact_type','ordinal','year','value','evidence_class']
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    lines=['# Secuencias bibliográficas estrictas CN4/CN6','',f'Versión: `{VERSION}`. Sólo se publican hechos capturados junto a frases bibliográficas explícitas; el OCR completo se elimina.','']
    for bid in sorted({r['book_id'] for r in rows}):
        rr=[r for r in rows if r['book_id']==bid];facts=[]
        for x in rr:
            if x['fact_type']=='isbn':facts.append(f"ISBN {x['value']} (p.{x['viewer_page']})")
            elif x['ordinal']:facts.append(f"{x['fact_type']} {x['ordinal']} → {x['year']} (p.{x['viewer_page']})")
            else:facts.append(f"{x['fact_type']} → {x['year']} (p.{x['viewer_page']})")
        lines.append(f"- `{bid}`: "+'; '.join(facts))
    if not rows:lines.append('- No se detectaron secuencias estrictas; requiere revisión del parser o fuente.')
    lines+=['','## Regla','La extracción automática de una secuencia explícita constituye evidencia bibliográfica estructurada más fuerte que una mera proximidad de año, pero todavía debe conservar la imagen fuente como autoridad última. No se infieren secuencias ausentes.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
