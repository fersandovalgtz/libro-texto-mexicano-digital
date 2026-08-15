#!/usr/bin/env python3
"""Audit bibliographic metadata signals in front matter without persisting OCR text.

Downloads/OCRs only front-matter pages ephemerally. Public output contains regex-
derived metadata candidates and boolean term signals, never the OCR transcript.
"""
from __future__ import annotations
import csv,re,tempfile,unicodedata
from pathlib import Path
from segment_fragments import SOURCE_CODES,download_with_retry,run_tesseract

STRUCT=Path('data/derived/page_structure.csv')
OUT=Path('data/derived/frontmatter_bibliographic_audit.csv')
REPORT=Path('data/derived/frontmatter_bibliographic_audit.md')
VERSION='FRONTMATTER_BIB_AUDIT_0.1'
GENS=('1972','1988','1993','2014')
PAGES=range(1,9)

def low(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',s)

def tsv_text(p):
    rows=list(csv.DictReader(open(p,encoding='utf-8',errors='replace'),delimiter='\t',quoting=csv.QUOTE_NONE))
    return ' '.join(r.get('text','') for r in rows if r.get('level')=='5' and r.get('text','').strip())

def years_near(text,terms,window=100):
    t=low(text);found=set()
    for term in terms:
        for m in re.finditer(term,t):
            seg=t[max(0,m.start()-window):m.end()+window]
            found.update(re.findall(r'\b(19[0-9]{2}|20[0-9]{2})\b',seg))
    return sorted(found)

def isbns(text):
    # Candidate only; normalize separators and retain forms that resemble 10/13 digit ISBN.
    vals=[]
    for m in re.finditer(r'(?i)isbn\s*[:\-]?\s*([0-9Xx][0-9Xx\-\s]{7,24}[0-9Xx])',text):
        raw=re.sub(r'\s+',' ',m.group(1)).strip(' .,:;')
        digits=re.sub(r'[^0-9Xx]','',raw)
        if len(digits) in {10,13}:vals.append(raw)
    return sorted(set(vals))

def main():
    struct=list(csv.DictReader(STRUCT.open(encoding='utf-8')));by={(r['catalog_generation'],int(r['viewer_page'])):r for r in struct}
    rows=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-frontmatter-') as td:
        temp=Path(td)
        for g in GENS:
            for p in PAGES:
                r=by.get((g,p));psm=(r.get('selected_psm') if r else '') or '3'
                img=temp/f'{g}_{p:03d}.jpg';out=temp/f'{g}_{p:03d}'
                try:
                    download_with_retry(f'https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[g]}/{p:03d}.jpg',img)
                    if not run_tesseract(img,out,psm):raise RuntimeError('ocr_failed')
                    text=tsv_text(out.with_suffix('.tsv'));t=low(text)
                    edition=years_near(text,[r'primera edici[oó]n',r'segunda edici[oó]n',r'tercera edici[oó]n',r'edici[oó]n revisada',r'edici[oó]n'])
                    copyright=years_near(text,[r'derechos reservados',r'd\.\s*r\.',r'copyright',r'©'])
                    printing=years_near(text,[r'impresi[oó]n',r'impreso',r'reimpresi[oó]n'])
                    all_years=sorted(set(re.findall(r'\b(19[0-9]{2}|20[0-9]{2})\b',t)))
                    rows.append({'audit_version':VERSION,'catalog_generation':g,'viewer_page':p,'ocr_ok':1,
                                 'edition_term':int('edicion' in t),'copyright_term':int('derechos reservados' in t or 'copyright' in t or 'd. r.' in t or 'd.r.' in t),
                                 'printing_term':int('impresion' in t or 'impreso' in t or 'reimpresion' in t),'isbn_term':int('isbn' in t),
                                 'edition_year_candidates':';'.join(edition),'copyright_year_candidates':';'.join(copyright),'printing_year_candidates':';'.join(printing),
                                 'isbn_candidates':';'.join(isbns(text)),'all_years_detected':';'.join(all_years),'ocr_char_count':len(text)})
                except Exception as e:
                    rows.append({'audit_version':VERSION,'catalog_generation':g,'viewer_page':p,'ocr_ok':0,'edition_term':'','copyright_term':'','printing_term':'','isbn_term':'','edition_year_candidates':'','copyright_year_candidates':'','printing_year_candidates':'','isbn_candidates':'','all_years_detected':'','ocr_char_count':0})
                for x in temp.iterdir():
                    try:x.unlink()
                    except Exception:pass
    assert len(rows)==32
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    lines=['# Auditoría bibliográfica automatizada de front matter','',f'Versión: `{VERSION}`. Se inspeccionan páginas 1–8 de las cuatro generaciones. El OCR es temporal; sólo se publican señales y candidatos bibliográficos derivados.','',
           '## Señales detectadas']
    for g in GENS:
        rr=[r for r in rows if r['catalog_generation']==g and r['ocr_ok']==1]
        ed=sorted({y for r in rr for y in str(r['edition_year_candidates']).split(';') if y});cr=sorted({y for r in rr for y in str(r['copyright_year_candidates']).split(';') if y});pr=sorted({y for r in rr for y in str(r['printing_year_candidates']).split(';') if y});isbn=sorted({x for r in rr for x in str(r['isbn_candidates']).split(';') if x})
        pages_ed=[str(r['viewer_page']) for r in rr if r['edition_term']];pages_cr=[str(r['viewer_page']) for r in rr if r['copyright_term']];pages_isbn=[str(r['viewer_page']) for r in rr if r['isbn_term']]
        lines.append(f"- {g}: páginas con marcador de edición={','.join(pages_ed) or 'ninguna'}; candidatos de año de edición={','.join(ed) or 'ninguno'}; copyright={','.join(cr) or 'ninguno'}; impresión={','.join(pr) or 'ninguno'}; páginas con ISBN={','.join(pages_isbn) or 'ninguna'}; ISBN candidatos={','.join(isbn) or 'ninguno'}.")
    lines += ['', '## Regla de interpretación','Una coincidencia de regex es un candidato técnico, no una verificación bibliográfica por sí sola. La ausencia de marcador explícito impide convertir automáticamente el año de la generación del catálogo en `edition_year`. Los metadatos ya verificados por inspección de página legal conservan prioridad.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
