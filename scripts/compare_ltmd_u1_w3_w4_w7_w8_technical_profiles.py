#!/usr/bin/env python3
"""Strictly descriptive W3/W4/W7/W8 technical comparison."""
from __future__ import annotations
import csv
from pathlib import Path
from compare_ltmd_u1_w3_w4_w7_technical_profiles import CANDIDATES,STRUCT_CLASSES,W3_COMPLETION,W4_COMPLETION,W7_COMPLETION,W4_STRUCT,W4_FRAG,W4_UNITS,W4_OVERLAP,W7_STRUCT,W7_FRAG,W7_UNITS,W7_OVERLAP,pct,profile,profile_w3,ratio,read

VERSION='LTMD_U1_W3_W4_W7_W8_TECHNICAL_COMPARISON_0.1'
OUT=Path('data/derived/ltmd_u1_w3_w4_w7_w8_technical_comparison.csv')
REPORT=Path('docs/LTMD_U1_W3_W4_W7_W8_TECHNICAL_COMPARISON.md')
W8_STRUCT=Path('data/catalog/ltmd_u1_w8_artes_page_structure_summary.csv');W8_DETAIL=Path('data/catalog/ltmd_u1_w8_artes_page_structure.csv');W8_FRAG=Path('data/catalog/ltmd_u1_w8_artes_fragment_manifest_summary.csv');W8_UNITS=Path('data/catalog/ltmd_u1_w8_artes_exact_content_units.csv');W8_OVERLAP=Path('data/catalog/ltmd_u1_w8_artes_exact_viewer_overlap.csv');W8_COMPLETION=Path('docs/LTMD_U1_W8_COMPLETION.md')

def main():
 for p in (W3_COMPLETION,W4_COMPLETION,W7_COMPLETION,W8_COMPLETION):
  if not p.exists():raise SystemExit(f'missing completion prerequisite: {p}')
 if {r['classifier_version'] for r in read(W8_DETAIL)}!={'PAGESTRUCT_LTMD_U1_W8_ARTES_0.1'}:raise SystemExit('W8 PAGESTRUCT version drift')
 profiles=[profile_w3(),profile('W4',W4_STRUCT,W4_FRAG,W4_UNITS,W4_OVERLAP,2414,14,'PAGESTRUCT_LTMD_U1_W4_SOCIAL_SCIENCES_0.1','FRAGSEG_LTMD_U1_W4_SOCIAL_SCIENCES_0.1',0),profile('W7',W7_STRUCT,W7_FRAG,W7_UNITS,W7_OVERLAP,3261,25,'PAGESTRUCT_LTMD_U1_W7_CIVICS_ETHICS_0.1','FRAGSEG_LTMD_U1_W7_CIVICS_ETHICS_0.1',5),profile('W8',W8_STRUCT,W8_FRAG,W8_UNITS,W8_OVERLAP,1490,16,'PAGESTRUCT_LTMD_U1_W8_ARTES_0.1','FRAGSEG_LTMD_U1_W8_ARTES_0.1',4)]
 expected={'W3':{'eligible_pages':17337,'fragments':222490,'unique_exact_units':147375},'W4':{'eligible_pages':2018,'fragments':21380,'unique_exact_units':17735},'W7':{'eligible_pages':2745,'fragments':33451,'unique_exact_units':22651},'W8':{'eligible_pages':1025,'segmented_pages':1025,'fragments':14060,'unique_exact_units':10370,'repeated_exact_units':2035,'cross_viewer_exact_units':1991,'cross_generation_exact_units':1906,'viewer_pairs_with_exact_reuse':120}}
 for p in profiles:
  for field,value in expected[p['corpus']].items():
   if p[field]!=value:raise SystemExit(f"{p['corpus']}: {field} drift: {p[field]} != {value}")
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(profiles[0]));w.writeheader();w.writerows(profiles)
 by={p['corpus']:p for p in profiles};keys=['W3','W4','W7','W8'];headers=['W3 Español/Lengua','W4 Ciencias Sociales','W7 Cívica/Ética','W8 Artes']
 lines=['# LTMD-U1 — comparación técnica W3 ↔ W4 ↔ W7 ↔ W8','',f'Versión: `{VERSION}`.','', 'Comparación **estrictamente técnica y descriptiva** de productos cerrados de PAGESTRUCT, FRAGSEG y reutilización textual exacta. Las cuatro cohortes tienen dominios, inventarios, coberturas y topologías de fuente diferentes. Las tasas caracterizan representaciones computacionales; **no demuestran diferencias curriculares, pedagógicas, históricas ni efectos de reformas**.','', 'W7 representa 25 objetos fuente-admisibles y cinco identidades retenidas. W8 representa 16 objetos fuente-admisibles y cuatro identidades 2018 retenidas. W3 conserva su proyección explícita de aliases de provenance.','', '## Escala','', '| métrica | '+' | '.join(headers)+' |','|---|'+'|'.join(['---:']*4)+'|', '| objetos canónicos procesados | '+' | '.join(f"{by[k]['processed_viewers']:,}" for k in keys)+' |', '| identidades retenidas por fuente | '+' | '.join(f"{by[k]['source_withheld_viewers']:,}" for k in keys)+' |', '| páginas | '+' | '.join(f"{by[k]['pages']:,}" for k in keys)+' |', '| páginas elegibles | '+' | '.join(f"{by[k]['eligible_pages']:,} ({pct(by[k]['eligible_page_rate'])})" for k in keys)+' |', '| fragmentos | '+' | '.join(f"{by[k]['fragments']:,}" for k in keys)+' |', '| fragmentos / página elegible | '+' | '.join(ratio(by[k]['fragments_per_eligible_page']) for k in keys)+' |','', '## PAGESTRUCT','', '| clase | '+' | '.join(headers)+' |','|---|'+'|'.join(['---:']*4)+'|']
 for c in STRUCT_CLASSES:lines.append(f"| `{c}` | "+' | '.join(f"{by[k][f'struct_{c}_count']:,} ({pct(by[k][f'struct_{c}_rate'])})" for k in keys)+' |')
 lines+=['','## FRAGSEG — tipos candidatos técnicos','', '| tipo | '+' | '.join(headers)+' |','|---|'+'|'.join(['---:']*4)+'|']
 for c in CANDIDATES:lines.append(f"| `{c}` | "+' | '.join(f"{by[k][f'candidate_{c}_count']:,} ({pct(by[k][f'candidate_{c}_share'])})" for k in keys)+' |')
 lines+=['','## Reutilización textual exacta','', '| métrica | '+' | '.join(headers)+' |','|---|'+'|'.join(['---:']*4)+'|', '| unidades exactas únicas | '+' | '.join(f"{by[k]['unique_exact_units']:,}" for k in keys)+' |', '| unidades repetidas | '+' | '.join(f"{by[k]['repeated_exact_units']:,} ({pct(by[k]['repeated_unit_rate'])})" for k in keys)+' |', '| unidades en ≥2 visores | '+' | '.join(f"{by[k]['cross_viewer_exact_units']:,} ({pct(by[k]['cross_viewer_unit_rate'])})" for k in keys)+' |', '| unidades en ≥2 generaciones | '+' | '.join(f"{by[k]['cross_generation_exact_units']:,} ({pct(by[k]['cross_generation_unit_rate'])})" for k in keys)+' |', '| pares de visores con reuso exacto | '+' | '.join(f"{by[k]['viewer_pairs_with_exact_reuse']:,}" for k in keys)+' |','', '### Nota de schema W3','', 'W3 usa contadores de provenance `canonical_*`/`represented_catalog_generation_count`; W4/W7/W8 usan el schema posterior. La normalización de W3 es explícita y no reescribe productos cerrados.','', '## Uso permitido','', 'Auditar escala, densidad de segmentación, estructura y dependencia textual dentro del pipeline común; formular preguntas posteriores con bibliografía, temporalidad, composición de cohorte y validación humana modeladas por separado.','', '## Uso no permitido','', 'No interpretar tasas como evidencia directa de calidad, complejidad pedagógica, efecto de reforma, continuidad curricular o cambio histórico; las generaciones de catálogo no equivalen automáticamente a años editoriales.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(VERSION)
 for p in profiles:print(p['corpus'],p['processed_viewers'],p['pages'],p['eligible_pages'],p['fragments'],p['unique_exact_units'])
if __name__=='__main__':main()
