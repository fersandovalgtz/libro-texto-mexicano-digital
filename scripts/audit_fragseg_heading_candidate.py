#!/usr/bin/env python3
"""Audit the FRAGSEG heading_candidate heuristic using metadata only.

The current candidate_type rule is lexical/length based, not typographic. This
audit quantifies the historical pattern without reading OCR text or semantic
classifier outputs. It must not be used to infer true heading prevalence.
"""
from __future__ import annotations

import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path

MANIFEST=Path('data/derived/fragment_manifest.csv')
OUT=Path('data/derived/fragseg_heading_candidate_audit.csv')
TOK=Path('data/derived/fragseg_heading_candidate_token_profile.csv')
PAGE=Path('data/derived/fragseg_heading_candidate_page_profile.csv')
REPORT=Path('data/derived/fragseg_heading_candidate_audit.md')
VERSION='FRAGSEG_HEADING_AUDIT_0.1'
GENERATIONS=('1972','1988','1993','2014')


def pct(n,d):
    return round(100*n/d,4) if d else 0.0


def token_bin(n):
    if n < 4: return '<4'
    if n <= 6: return '4-6'
    if n <= 9: return '7-9'
    return '10-12'


def q(vals,p):
    if not vals: return ''
    vals=sorted(vals)
    if len(vals)==1: return vals[0]
    pos=(len(vals)-1)*p
    lo=int(pos); hi=min(lo+1,len(vals)-1); frac=pos-lo
    return round(vals[lo]*(1-frac)+vals[hi]*frac,4)


def main():
    rows=list(csv.DictReader(MANIFEST.open(encoding='utf-8')))
    assert len(rows)==9594
    audit=[]; tokrows=[]; pagerows=[]
    for gen in GENERATIONS:
        g=[r for r in rows if r['catalog_generation']==gen]
        h=[r for r in g if r['candidate_type']=='heading_candidate']
        nonh=[r for r in g if r['candidate_type']!='heading_candidate']
        toks=[int(r['token_count']) for r in h]
        chars=[int(r['char_count']) for r in h]
        lt4=sum(n<4 for n in toks); ge4=sum(n>=4 for n in toks)
        pages=defaultdict(lambda:{'n':0,'h':0,'lt4':0,'ge4':0})
        for r in g:
            p=pages[r['page_id']];p['n']+=1
            if r['candidate_type']=='heading_candidate':
                p['h']+=1
                if int(r['token_count'])<4:p['lt4']+=1
                else:p['ge4']+=1
        page_n=len(pages); pages_any=sum(v['h']>0 for v in pages.values())
        page_fracs=[v['h']/v['n'] for v in pages.values() if v['n']]
        audit.append({
            'generation':gen,'fragment_n':len(g),'heading_candidate_n':len(h),
            'heading_candidate_pct':pct(len(h),len(g)),
            'heading_lt4_n':lt4,'heading_lt4_pct_of_heading':pct(lt4,len(h)),
            'heading_4to12_n':ge4,'heading_4to12_pct_of_heading':pct(ge4,len(h)),
            'heading_token_median':q(toks,.5),'heading_token_p75':q(toks,.75),
            'heading_char_median':q(chars,.5),'heading_char_p75':q(chars,.75),
            'page_n':page_n,'pages_with_heading_candidate_n':pages_any,
            'pages_with_heading_candidate_pct':pct(pages_any,page_n),
            'median_page_heading_fraction':round(statistics.median(page_fracs),4) if page_fracs else '',
            'audit_version':VERSION,
        })
        c=Counter(token_bin(n) for n in toks)
        for b in ('<4','4-6','7-9','10-12'):
            tokrows.append({'generation':gen,'token_bin':b,'n':c[b],'pct_of_heading':pct(c[b],len(h)),'audit_version':VERSION})
        for pid,v in sorted(pages.items()):
            pagerows.append({'generation':gen,'page_id':pid,'fragment_n':v['n'],'heading_candidate_n':v['h'],
                             'heading_candidate_fraction':round(v['h']/v['n'],6) if v['n'] else 0,
                             'heading_lt4_n':v['lt4'],'heading_4to12_n':v['ge4'],'audit_version':VERSION})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    for path,data in ((OUT,audit),(TOK,tokrows),(PAGE,pagerows)):
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0].keys()));w.writeheader();w.writerows(data)
    lines=['# Auditoría de `heading_candidate` en FRAGSEG','',
           f'Versión: `{VERSION}`. Esta auditoría usa sólo metadatos persistidos. No lee OCR ni clasificadores semánticos.','',
           '## Advertencia de constructo','',
           '`heading_candidate` no es un detector tipográfico de encabezados. En FRAGSEG es una categoría residual basada en longitud: después de descartar señales de evaluación, proyecto, experimento, actividad, pregunta e instrucción, una unidad de ≤12 tokens y ≤100 caracteres recibe esa etiqueta. Por ello, su prevalencia no debe interpretarse como prevalencia histórica de encabezados reales.','',
           '## Perfil por generación','']
    for r in audit:
        lines.append(f"- {r['generation']}: {r['heading_candidate_n']}/{r['fragment_n']} ({r['heading_candidate_pct']:.2f}%) `heading_candidate`; {r['heading_lt4_pct_of_heading']:.2f}% de esos candidatos tienen <4 tokens y {r['heading_4to12_pct_of_heading']:.2f}% tienen 4–12 tokens; {r['pages_with_heading_candidate_pct']:.2f}% de las páginas contienen al menos uno.")
    lines += ['', '## Consecuencia metodológica','',
              'El crecimiento histórico de esta categoría debe tratarse como una señal de fragmentación/longitud hasta que una validación visual independiente determine qué proporción corresponde a encabezados tipográficos verdaderos. No debe utilizarse como hallazgo histórico primario ni como razón automática para excluir texto de SEMB 0.3.','']
    REPORT.write_text('\n'.join(lines),encoding='utf-8')
    print('wrote',OUT,TOK,PAGE,REPORT)

if __name__=='__main__': main()
