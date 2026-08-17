#!/usr/bin/env python3
"""Synchronize bounded LTMD master-status regions with integrity 0.12.

This patch assumes the v0.11 bibliography/status synchronization already ran.
It adds W7 bibliographic coverage + the bounded 13-20 negative probe, promotes
the integrity section to 0.12, and replaces immediate priorities. Other closure
sections are untouched.
"""
from __future__ import annotations

from pathlib import Path

PATH = Path('docs/LTMD_STATUS_2026-08-16.md')


def replace_region(text: str, start: str, end: str, replacement: str) -> str:
    if text.count(start) != 1:
        raise SystemExit(f'expected one start anchor {start!r}, found {text.count(start)}')
    if text.count(end) != 1:
        raise SystemExit(f'expected one end anchor {end!r}, found {text.count(end)}')
    a = text.index(start)
    b = text.index(end, a)
    if b <= a:
        raise SystemExit('invalid anchor ordering')
    return text[:a] + replacement.rstrip() + '\n\n' + text[b:]


def main() -> None:
    text = PATH.read_text(encoding='utf-8')

    marker = (
        'Véanse `docs/LTMD_CATALOG_GENERATION_SEMANTICS_0_1.md`, `docs/DATA_MODEL.md`, '
        '`docs/DATA_GOVERNANCE.md`, `docs/HISTORICAL_ANALYSIS_PLAN_0_3.md`, '
        '`docs/LTMD_BIBLIOGRAPHIC_INSTANCE_POLICY_0_1.md`, '
        '`data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.md`, '
        '`data/catalog/ltmd_u1_w7_bibliographic_candidate_support.md`, '
        '`data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.md`, '
        '`data/catalog/ltmd_bibliographic_observations.md` y '
        '`data/catalog/ltmd_bibliographic_instance_candidates.md`.'
    )
    if text.count(marker) != 1:
        raise SystemExit(f'expected one bibliography reference marker, found {text.count(marker)}')

    coverage = '''### Cobertura bibliográfica W7 y cierre de la ventana 13–20

El run **31996862753** (`success`) publicó `LTMD_U1_W7_BIBLIOGRAPHIC_COVERAGE_0.1`, una matriz de readiness que conserva las **30/30 identidades históricas** y separa completitud de fuente de completitud cronológica:

- fuente admitida: **25/30**;
- fuente retenida: **5/30**;
- objetos con observaciones bibliográficas: **26**;
- candidatos técnicos de instancia: **11** en total;
- candidatos sobre fuente admitida: **10**;
- `H2014P5FCA`: candidato bibliográfico disponible pero fuente parcialmente retenida;
- fuente admitida + observaciones pero sin ciclo: **12**;
- ciclo observado pero sin candidato: **3**;
- subárbol de fuente retenido: **4**.

Por generación de catálogo, la cobertura de candidatos es: 2008 **3/8**, 2011 **3/6**, 2014 **2/6** —uno de ellos `H2014P5FCA` con fuente retenida—, 2018 **0/4** por retención de fuente y 2019 **3/6**. Estos conteos son de readiness, no de validez histórica.

Para los **12 objetos fuente-admitidos sin `school_cycle` fuerte**, el run **31996766053** (`success`) ejecutó `LTMD_U1_W7_MISSING_CYCLE_WINDOW_13_20_0.1`:

- targets reproducibles: **12**;
- ventana adicional: páginas lógicas **13–20**;
- páginas descargadas temporalmente y verificadas SHA-256+tamaño: **96/96**;
- OCR independiente: PSM **3, 6, 11**;
- objetos con ciclo fuerte multímodo encontrado: **0/12**;
- objetos sin ciclo fuerte en esa ventana: **12/12**.

Este cero se interpreta sólo como **ausencia de un ciclo fuerte en páginas 13–20 bajo el contrato OCR 0.1**. No demuestra que los libros carezcan de ciclo escolar. La ventana queda cerrada; no se continuará un barrido secuencial indefinido por páginas. Nuevos intentos deberán partir de una pista bibliográfica/documental concreta o de una hipótesis de ubicación acotada.

Véanse `docs/LTMD_U1_W7_BIBLIOGRAPHIC_COVERAGE.md` y `data/catalog/ltmd_u1_w7_missing_cycle_window_13_20.md`.

'''
    text = text.replace(marker, coverage + marker, 1)

    integrity = '''## Integridad científica

`LTMD_INTEGRITY_0.12` es el perímetro científico vigente. Preserva 0.11 y congela adicionalmente:

- la matriz `LTMD_U1_W7_BIBLIOGRAPHIC_COVERAGE_0.1` sobre las 30 identidades históricas;
- el probe acotado `LTMD_U1_W7_MISSING_CYCLE_WINDOW_13_20_0.1` y su resultado negativo 0/12;
- los scripts/workflows que derivan targets, verifican las 96 páginas y producen ambos artefactos.

El run **31997048223** concluyó `success` sobre el commit `454126bba82f2534ca3965a787322c382a3b9db1`. El manifiesto publicado declara:

- archivos críticos: **414**;
- críticos presentes: **414/414**;
- `missing_critical=[]`;
- opcionales presentes: **9**.

0.12 mantiene íntegra la cadena causal congelada por 0.11: `candidate-support 0.1 → recovery OCR estrecho 0.2 → observations 0.4 → candidates 0.3`, junto con la policy que impide presentar los 11 candidatos como fechas históricas definitivamente validadas.

El resultado negativo 13–20 se considera evidencia científica acotada, no una prueba de inexistencia del ciclo escolar. Los experimentos archivísticos no concluyentes, el espejo externo no verificado y las interpretaciones bibliográficas supersedidas continúan fuera del perímetro crítico como resultados sustantivos.
'''
    text = replace_region(text, '## Integridad científica', '## Orquestación y recuperación', integrity)

    priorities = '''## Prioridades inmediatas

1. Para los **12 objetos sin ciclo fuerte**, detener el barrido secuencial abierto después del resultado 0/12 en páginas 13–20. La siguiente búsqueda debe ser documental/bibliográfica dirigida: catálogos, registros institucionales, páginas legales identificables, ISBN válidos o una pista explícita que justifique una nueva ventana acotada.
2. Para `H2008P5CI278`, `H2011P4CI315` y `H2011P6CI336`, mantener la contradicción visible: existe ciclo fuerte, pero no hay statement editorial/reimpresión compatible; en los dos objetos 2011 la página legal lee reimpresión 2012 y **no** debe convertirse en 2013 por conveniencia.
3. Para `H2014P5FCA`, continuar la búsqueda de una fuente reproducible de la **tercera reimpresión 2017 / ciclo 2017–2018** que permita recuperar la página 104 con procedencia suficiente, sin convertir una copia externa en `source_jpeg` institucional.
4. Para los cuatro `H2018...`, priorizar routing histórico, relocalización o huellas documentales; mantener retención y evitar aliases 2019 mientras no aparezca evidencia suficiente.
5. Extender gradualmente el contrato bibliográfico página+SHA+soporte a W3/W4/W2 antes de construir cronologías editoriales amplias.
6. Incorporar al artículo metodológico la separación entre cohorte de catálogo y tiempo bibliográfico, la matriz de coverage/readiness, el resultado negativo acotado 13–20, los tiers de candidatos y el comparador W3↔W4↔W7, manteniendo separada la futura validación humana/semántica.
'''
    text = replace_region(text, '## Prioridades inmediatas', '## Principio de publicación', priorities)

    if 'LTMD_INTEGRITY_0.11` es el perímetro científico vigente' in text:
        raise SystemExit('stale integrity 0.11 wording survived')
    if 'páginas lógicas **13–20**' not in text or 'ciclo fuerte multímodo encontrado: **0/12**' not in text:
        raise SystemExit('bounded probe summary missing after synchronization')
    if text.count('## Ciencias Naturales y W2 Matemáticas') != 1:
        raise SystemExit('technical closure body was structurally damaged')

    PATH.write_text(text, encoding='utf-8')
    print('synchronized', PATH)
    print('bytes', PATH.stat().st_size)


if __name__ == '__main__':
    main()
