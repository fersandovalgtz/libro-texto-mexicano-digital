#!/usr/bin/env python3
"""Targeted ephemeral OCR audit for the two CN6 objects in catalog generation 1993.

Purpose: resolve their bibliographic relationship without waiting for the broader
CN4/CN6 front-matter sweep. Only structured bibliographic statements are saved.
The page images and OCR text are deleted at the end of the run.
"""
from __future__ import annotations
import csv,re,subprocess,tempfile,unicodedata
from pathlib import Path
from urllib.request import Request,urlopen

OUT=Path('data/expansion/cn6_1993_legal_page_facts.csv')
REPORT=Path('data/expansion/cn6_1993_legal_page_facts.md')
VERSION='CN6_1993_LEGAL_AUDIT_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN6-1993 legal page audit'
OBJECTS=[
 ('LTMD-CN6-G1993-DH','H1993P6CI209','Ciencias Naturales y desarrollo humano'),
 ('LTMD-CN6-G1993-CN','H1993P6CI210','Ciencias Naturales'),
]

def get(url):
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:return r.read()

def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',s).strip()

def ocr(img,stem,psm):
    p=subprocess.run(['tesseract',str(img),str(stem),'-l','spa','--psm',str(psm)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    fp=stem.with_suffix('.txt')
    return fp.read_text(encoding='utf-8',errors='replace') if p.returncode==0 and fp.exists() else ''

def extract(t):
    t=norm(t);facts=[]
    ords={'primera':'1','segunda':'2','tercera':'3','cuarta':'4','quinta':'5','sexta':'6','septima':'7','octava':'8','novena':'9','decima':'10'}
    # Permit punctuation/OCR noise but force the year to be locally attached to an edition phrase.
    for m in re.finditer(r'\b(primera|segunda|tercera|cuarta|quinta|sexta|septima|octava|novena|decima)\s+(?:edici[o0]n|reimpresi[o0]n)\b.{0,65}?\b(19\d{2}|20\d{2})\b',t):
        phrase=m.group(0);kind='reprint' if 'reimpres' in phrase else 'edition'
        facts.append((kind,ords[m.group(1)],m.group(2),'explicit_ordinal'))
    # Catch common reversed Mexican colophon form: "1994, primera edición".
    for m in re.finditer(r'\b(19\d{2}|20\d{2})\b.{0,35}?\b(primera|segunda|tercera|cuarta|quinta|sexta|septima|octava|novena|decima)\s+(edici[o0]n|reimpresi[o0]n)\b',t):
        kind='reprint' if 'reimpres' in m.group(3) else 'edition'
        facts.append((kind,ords[m.group(2)],m.group(1),'explicit_ordinal_reversed'))
    for m in re.finditer(r'(?:derechos\s+reservados|d\.?\s*r\.?|copyright)\b.{0,80}?\b(19\d{2}|20\d{2})\b',t):facts.append(('copyright','',m.group(1),'explicit_rights'))
    for m in re.finditer(r'\bisbn\s*[:\-]?\s*([0-9x][0-9x\-\s]{7,24}[0-9x])',t,re.I):
        raw=re.sub(r'\s+',' ',m.group(1)).strip(' .,:;');digits=re.sub(r'[^0-9Xx]','',raw)
        if len(digits) in {10,13}:facts.append(('isbn','','',raw))
    return sorted(set(facts))

def main():
    rows=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-cn6g1993-') as td:
        td=Path(td)
        for bid,key,title in OBJECTS:
            # Existing audits identify viewer page 2 as the principal legal page.
            p=2;url=f'https://historico.conaliteg.gob.mx/c/{key}/{p:03d}.jpg';img=td/f'{key}.jpg';img.write_bytes(get(url))
            versions=[]
            for psm in (3,6,11):
                text=ocr(img,td/f'{key}_p{psm}',psm)
                versions.append((sum(c.isalnum() for c in text),psm,text,extract(text)))
            _,best_psm,best_text,best_facts=max(versions,key=lambda x:x[0])
            # Union facts across modes, but retain best-mode marker so a single OCR mode cannot silently decide.
            union=sorted({fact for _,_,_,facts in versions for fact in facts})
            for kind,ordinal,year,value in union:
                rows.append({'audit_version':VERSION,'book_id':bid,'viewer_key':key,'viewer_page':2,'title':title,'fact_type':kind,'ordinal':ordinal,'year':year,'value':value,'detected_in_best_psm':int((kind,ordinal,year,value) in best_facts),'best_psm':best_psm})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['audit_version','book_id','viewer_key','viewer_page','title','fact_type','ordinal','year','value','detected_in_best_psm','best_psm']
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    lines=['# Cotejo dirigido de páginas legales — CN6 / generación 1993','',f'Versión: `{VERSION}`. OCR efímero de visor 2 en los dos objetos; se conservan sólo hechos estructurados.','']
    for bid,key,title in OBJECTS:
        rr=[r for r in rows if r['book_id']==bid];facts=[]
        for r in rr:
            if r['fact_type']=='isbn':facts.append(f"ISBN {r['value']}")
            elif r['ordinal']:facts.append(f"{r['fact_type']} {r['ordinal']} → {r['year']}")
            else:facts.append(f"{r['fact_type']} → {r['year']}")
        lines.append(f"- `{bid}` / `{key}` / *{title}*: "+('; '.join(facts) if facts else 'sin secuencias estrictas recuperadas'))
    lines+=['','## Restricción','Un hecho recuperado por OCR sigue subordinado a la imagen fuente; este control evita promover años meramente incidentales, pero no sustituye una edición bibliográfica humana.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
