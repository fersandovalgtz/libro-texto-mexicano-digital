#!/usr/bin/env python3
"""Synchronize README coverage indicators from the reproducible U1 coverage summary."""
from __future__ import annotations
import csv,re
from datetime import date
from pathlib import Path

SUMMARY=Path('data/catalog/ltmd_u1_coverage_summary.csv')
README_ES=Path('README.md')
README_EN=Path('README.en.md')
TOTAL=542

MONTHS_ES={1:'enero',2:'febrero',3:'marzo',4:'abril',5:'mayo',6:'junio',7:'julio',8:'agosto',9:'septiembre',10:'octubre',11:'noviembre',12:'diciembre'}
LABEL_ES={'W1':'Ciencias Naturales','W2':'Matemáticas','W3':'Español / Lengua','W4':'Ciencias Sociales','W5':'Historia','W6':'Geografía / Atlas','W7':'Formación Cívica y Ética','W8':'Artes','W9':'Educación Física','W10':'Integrados / Multiarea','W11':'Otros / No clasificados'}
LABEL_EN={'W1':'Natural Sciences','W2':'Mathematics','W3':'Spanish / Language','W4':'Social Sciences','W5':'History','W6':'Geography / Atlas','W7':'Civics and Ethics','W8':'Arts','W9':'Physical Education','W10':'Integrated / Multiarea','W11':'Other / Unclassified'}

ES_STAGE={
 'ocr_complete_downstream_pending':'OCR completo; capas downstream pendientes',
 'scope_frozen_source_audit_pending':'alcance congelado; auditoría de fuente pendiente',
 'architecture_complete_inventory_pending':'arquitectura auditada; inventario pendiente',
 'source_asset_audit_in_progress':'inventario cerrado; auditoría de activos en curso',
 'asset_audit_complete_admissibility_pending':'activos auditados; admisibilidad pendiente',
 'source_admissibility_complete_topology_pending':'admisibilidad cerrada; topología pendiente',
 'source_topology_ready_processing_pending':'topología de fuente lista; procesamiento downstream pendiente',
}
EN_STAGE={
 'ocr_complete_downstream_pending':'OCR complete; downstream layers pending',
 'scope_frozen_source_audit_pending':'scope frozen; source audit pending',
 'architecture_complete_inventory_pending':'architecture audited; inventory pending',
 'source_asset_audit_in_progress':'inventory closed; asset audit in progress',
 'asset_audit_complete_admissibility_pending':'assets audited; admissibility pending',
 'source_admissibility_complete_topology_pending':'admissibility closed; topology pending',
 'source_topology_ready_processing_pending':'source topology ready; downstream processing pending',
}

def stage_es(r):
 s=r['stage'];eff=int(r['effective_technical_identities']);plan=int(r['planned_identities']);rem=int(r['remaining_to_effective'])
 if s=='closed':return f'cerrada técnicamente ({eff}/{plan})'
 if s=='partial_with_preserved_exceptions':return f'parcial; {rem} excepciones preservadas ({eff}/{plan})'
 if s=='source_admitted_cohort_closed_with_retentions':return f'cohorte fuente-admitida cerrada; {rem} retenidas ({eff}/{plan})'
 if s in ES_STAGE:return ES_STAGE[s]
 return f'en cola ({plan})'

def stage_en(r):
 s=r['stage'];eff=int(r['effective_technical_identities']);plan=int(r['planned_identities']);rem=int(r['remaining_to_effective'])
 if s=='closed':return f'technically closed ({eff}/{plan})'
 if s=='partial_with_preserved_exceptions':return f'partial; {rem} preserved exceptions ({eff}/{plan})'
 if s=='source_admitted_cohort_closed_with_retentions':return f'source-admitted cohort closed; {rem} retained ({eff}/{plan})'
 if s in EN_STAGE:return EN_STAGE[s]
 return f'queued ({plan})'

def pct(n):return f'{100*n/TOTAL:.2f}'

def sync_es(text,rows,eff,can):
 today=date.today();cut=f'{today.day} de {MONTHS_ES[today.month]} de {today.year}'
 text=re.sub(r'Corte documental de referencia: \*\*[^*]+\*\*\.',f'Corte documental de referencia: **{cut}**.',text)
 text=re.sub(r'<img src="https://img\.shields\.io/badge/cobertura%20técnica-[^"]+" alt="[^"]+">',f'<img src="https://img.shields.io/badge/cobertura%20técnica-{eff}%2F{TOTAL}%20·%20{pct(eff)}%25-455B55?style=flat-square" alt="{eff} de {TOTAL} cobertura técnica">',text)
 text=re.sub(r'<img src="https://img\.shields\.io/badge/canónicos-[^"]+" alt="[^"]+">',f'<img src="https://img.shields.io/badge/canónicos-{can}%2F{TOTAL}%20·%20{pct(can)}%25-5b4b8a?style=flat-square" alt="{can} objetos canónicos">',text)
 text=re.sub(r'\| Cobertura técnica efectiva cerrada o resuelta \| \*\*[^\n]+',f'| Cobertura técnica efectiva cerrada o resuelta | **{eff} / {TOTAL} ({pct(eff)}%)** |',text)
 text=re.sub(r'\| Objetos canónicos de procesamiento \| \*\*[^\n]+',f'| Objetos canónicos de procesamiento | **{can} / {TOTAL} ({pct(can)}%)** |',text)
 wave='### Cobertura U1\n\n| Ola | Dominio | Estado |\n|---|---|---|\n'+''.join(f"| {r['wave']} | {LABEL_ES[r['wave']]} | {stage_es(r)} |\n" for r in rows)+'\nEl tablero reproducible'
 text,n=re.subn(r'### Cobertura U1\n\n\| Ola \| Dominio \| Estado \|.*?\n\nEl tablero reproducible',wave,text,flags=re.S)
 if n!=1:raise SystemExit(f'ES coverage table sync failed: matches={n}')
 return text

def sync_en(text,rows,eff,can):
 today=date.today();cut=today.strftime('%d %B %Y').lstrip('0')
 text=re.sub(r'Reference cut: \*\*[^*]+\*\*\.',f'Reference cut: **{cut}**.',text)
 text=re.sub(r'<img src="https://img\.shields\.io/badge/technical%20coverage-[^"]+" alt="[^"]+">',f'<img src="https://img.shields.io/badge/technical%20coverage-{eff}%2F{TOTAL}%20·%20{pct(eff)}%25-455B55?style=flat-square" alt="{eff} of {TOTAL} technical coverage">',text)
 text=re.sub(r'<img src="https://img\.shields\.io/badge/canonical-[^"]+" alt="[^"]+">',f'<img src="https://img.shields.io/badge/canonical-{can}%2F{TOTAL}%20·%20{pct(can)}%25-5b4b8a?style=flat-square" alt="{can} canonical objects">',text)
 text=re.sub(r'\| Closed or resolved technical coverage \| \*\*[^\n]+',f'| Closed or resolved technical coverage | **{eff} / {TOTAL} ({pct(eff)}%)** |',text)
 text=re.sub(r'\| Canonical processing objects \| \*\*[^\n]+',f'| Canonical processing objects | **{can} / {TOTAL} ({pct(can)}%)** |',text)
 if '### U1 coverage' in text:
  wave='### U1 coverage\n\n| Wave | Domain | Status |\n|---|---|---|\n'+''.join(f"| {r['wave']} | {LABEL_EN[r['wave']]} | {stage_en(r)} |\n" for r in rows)
  text=re.sub(r'### U1 coverage\n\n\| Wave \| Domain \| Status \|.*?(?=\n## )',wave+'\n',text,flags=re.S)
 return text

def main():
 rows=list(csv.DictReader(SUMMARY.open(encoding='utf-8',newline='')))
 if len(rows)!=11 or sum(int(r['planned_identities']) for r in rows)!=TOTAL:raise SystemExit('coverage summary invariant failed')
 eff=sum(int(r['effective_technical_identities']) for r in rows);can=sum(int(r['canonical_processing_objects']) for r in rows)
 es=sync_es(README_ES.read_text(encoding='utf-8'),rows,eff,can);en=sync_en(README_EN.read_text(encoding='utf-8'),rows,eff,can)
 README_ES.write_text(es,encoding='utf-8');README_EN.write_text(en,encoding='utf-8')
 print(f'README coverage synchronized: effective={eff}/{TOTAL}, canonical={can}/{TOTAL}')

if __name__=='__main__':main()
