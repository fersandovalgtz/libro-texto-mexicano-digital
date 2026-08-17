#!/usr/bin/env python3
"""Synchronize bounded LTMD status sections with bibliography/integrity v0.11.

This deliberately patches only three anchored regions of the master status:
1. bibliographic observations/candidates after the fingerprint/support audit;
2. research-integrity section;
3. immediate priorities.

W2/W3/W4/W7 technical closure sections and comparison metrics are not rewritten.
The script refuses to run if anchors are missing or duplicated.
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
        raise SystemExit(f'anchor order invalid: {start!r} -> {end!r}')
    return text[:a] + replacement.rstrip() + '\n\n' + text[b:]


def main() -> None:
    text = PATH.read_text(encoding='utf-8')

    bibliography = '''### Observaciones bibliográficas 0.4 y recuperación OCR estrecha

La capa vigente es `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4`. El run **31996313631** (`success`) reconstruyó la capa sobre una cadena causal reproducible y publicó:

- observaciones semánticas: **95**;
- objetos con ≥1 observación: **26**;
- filas normalizadas de evidencia página/SHA: **97**;
- W7 admitidos cubiertos: **25/25**;
- `H2014P5FCA` conserva sus cuatro observaciones específicas pese a permanecer retenido del OCR productivo por su hueco de fuente.

La expansión desde 0.2 añadió únicamente dos `reprint_history_statement` mediante `LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.2` (run **31996256694**, `success`). Recovery 0.2 deriva sus cinco targets **desde el audit pre-recovery**, no desde la tabla final de candidatos, eliminando la dependencia circular detectada en la primera implementación.

La única normalización permitida es la confusión OCR documentada dentro de `reimpresión`, donde la `i` inmediatamente después de `re` puede aparecer como `l`, `I` o `1`. Se exige ≥2 PSM sobre la misma página SHA-verificada y que el año coincida con el inicio de un ciclo escolar fuerte ya observado.

Recuperaciones aceptadas:

- `H2011P5CI326`: `third_reprint:2013`, ciclo `2013-2014`, página 2, PSM `3;11;12`;
- `H2014P4FCA`: `third_reprint:2017`, ciclo `2017-2018`, página 2, PSM `3;4;6;11`.

Permanecen sin statement compatible, sin imputación:

- `H2008P5CI278` — ciclo `2008-2009`;
- `H2011P4CI315` — ciclo `2013-2014`, mientras la página legal lee reimpresión 2012;
- `H2011P6CI336` — ciclo `2013-2014`, mientras la página legal lee reimpresión 2012.

No existe fuzzy matching bibliográfico general. `catalog_generation` no participa en la recuperación.

### Candidatos de instancia bibliográfica 0.3

La capa de cronología de ejemplar vigente es `LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.3`, publicada por el run **31996365328** (`success`) y reconstruida directamente desde Observations 0.4.

Resultado:

- objetos evaluados: **26**;
- candidatos técnicos con año: **11**;
- objetos sin candidato estricto: **15**;
- Tier A — declaración editorial/reimpresión y ciclo en páginas completamente independientes: **0**;
- Tier B — declaración conjunta + página corroborante adicional: **2**;
- Tier C — declaración conjunta en una sola página: **9**;
- candidatos cuyo año difiere de `catalog_generation`: **6/11**.

Los once candidatos son:

- `H2008P1CI250` → 2010, `third_edition:2010`, ciclo `2010-2011`, Tier C;
- `H2008P2CI257` → 2008, `first_edition:2008`, ciclo `2008-2009`, Tier B;
- `H2008P6CI286` → 2008, `first_edition:2008`, ciclo `2008-2009`, Tier B;
- `H2011P1CI294` → 2013, `fourth_edition:2013`, ciclo `2013-2014`, Tier C;
- `H2011P2CI301` → 2013, `fourth_edition:2013`, ciclo `2013-2014`, Tier C;
- `H2011P5CI326` → 2013, `third_reprint:2013`, ciclo `2013-2014`, Tier C;
- `H2014P4FCA` → 2017, `third_reprint:2017`, ciclo `2017-2018`, Tier C;
- `H2014P5FCA` → 2017, `third_reprint:2017`, ciclo `2017-2018`, Tier C;
- `H2019P4FCA` → 2019, `fifth_edition:2019`, ciclo `2019-2020`, Tier C;
- `H2019P5FCA` → 2019, `second_edition:2019`, ciclo `2019-2020`, Tier C;
- `H2019P6FCA` → 2019, `second_edition:2019`, ciclo `2019-2020`, Tier C.

Seis de los once años difieren de la cohorte del catálogo (`H2008P1CI250`, `H2011P1CI294`, `H2011P2CI301`, `H2011P5CI326`, `H2014P4FCA`, `H2014P5FCA`). Este resultado refuerza empíricamente que `catalog_generation` no debe copiarse como fecha bibliográfica.

Los 15 objetos sin candidato permanecen explícitamente como datos faltantes: **12** carecen de `school_cycle` fuerte en la ventana 1–12 y **3** tienen ciclo fuerte pero ninguna edición/reimpresión compatible bajo las reglas vigentes.

`docs/LTMD_BIBLIOGRAPHIC_INSTANCE_POLICY_0_1.md` establece el lenguaje permitido. La antigua `LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1` y su audit se conservan únicamente como traza metodológica **supersedida para interpretación/publicación**. Los once años vigentes deben describirse como **candidatos técnicos de cronología de ejemplar**, con `human_validated=0`, no como fechas históricas definitivamente validadas.

Véanse `docs/LTMD_CATALOG_GENERATION_SEMANTICS_0_1.md`, `docs/DATA_MODEL.md`, `docs/DATA_GOVERNANCE.md`, `docs/HISTORICAL_ANALYSIS_PLAN_0_3.md`, `docs/LTMD_BIBLIOGRAPHIC_INSTANCE_POLICY_0_1.md`, `data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.md`, `data/catalog/ltmd_u1_w7_bibliographic_candidate_support.md`, `data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.md`, `data/catalog/ltmd_bibliographic_observations.md` y `data/catalog/ltmd_bibliographic_instance_candidates.md`.
'''

    text = replace_region(
        text,
        '### Observaciones bibliográficas 0.2',
        '## Ciencias Naturales y W2 Matemáticas',
        bibliography,
    )

    integrity = '''## Integridad científica

`LTMD_INTEGRITY_0.11` es el perímetro científico vigente. Preserva 0.10 y congela adicionalmente la cadena causal de candidatos bibliográficos:

`candidate-support 0.1 → recovery OCR estrecho 0.2 → observations 0.4 → candidates 0.3`.

También congela `docs/LTMD_BIBLIOGRAPHIC_INSTANCE_POLICY_0_1.md`, que define los tiers de evidencia y declara supersedida para interpretación/publicación la antigua semántica de “instance resolution”. Los experimentos históricos de resolución/audit permanecen en el repositorio como traza metodológica, pero no se promueven al perímetro crítico como fuente vigente de fechas.

El run **31996546000** concluyó `success` sobre el commit `13cac65f6fb1494ec4ef6776de3941446d8ed792`. El manifiesto publicado declara:

- archivos críticos: **405**;
- críticos presentes: **405/405**;
- `missing_critical=[]`;
- opcionales presentes: **9**.

El perímetro 0.11 conserva además todos los contratos ya fijados por 0.10: semántica de cohorte vs tiempo bibliográfico, fingerprint W7 300/300, auditoría multímodo/checksum, snapshot/criterios de aceptación de las cinco fuentes retenidas y comparador técnico W3↔W4↔W7.

Los fallos de infraestructura de Wayback/Common Crawl, el espejo externo no verificado y las interpretaciones bibliográficas supersedidas **no** se tratan como resultados científicos críticos.
'''
    text = replace_region(
        text,
        '## Integridad científica',
        '## Orquestación y recuperación',
        integrity,
    )

    priorities = '''## Prioridades inmediatas

1. Para los **12 objetos sin `school_cycle` fuerte**, ampliar de forma acotada la ventana bibliográfica más allá de las páginas 1–12, manteniendo verificación SHA+tamaño, no persistencia de imágenes/OCR completo y promoción sólo por reglas explícitas.
2. Para `H2008P5CI278`, `H2011P4CI315` y `H2011P6CI336`, investigar páginas legales/adicionales con OCR dirigido sin alterar la regla temporal: el ciclo ya existe, pero no hay statement editorial/reimpresión compatible; 2012 no debe convertirse en 2013 por conveniencia.
3. Para `H2014P5FCA`, continuar la búsqueda de una fuente reproducible de la **tercera reimpresión 2017 / ciclo 2017–2018** que permita recuperar la página 104 con procedencia suficiente; no convertir una copia externa en `source_jpeg` institucional.
4. Para los cuatro `H2018...`, priorizar routing histórico, relocalización o huellas documentales; mantener retención y evitar aliases 2019 mientras no aparezca evidencia suficiente.
5. Extender gradualmente el contrato bibliográfico página+SHA+soporte a W3/W4/W2 antes de construir cronologías editoriales amplias.
6. Incorporar al artículo metodológico la separación entre cohorte de catálogo y tiempo bibliográfico, la tasa de datos faltantes, los tiers de candidatos y el comparador W3↔W4↔W7, manteniendo separada la futura validación humana/semántica.
'''
    text = replace_region(
        text,
        '## Prioridades inmediatas',
        '## Principio de publicación',
        priorities,
    )

    if 'LTMD_INTEGRITY_0.10` es el perímetro científico vigente' in text:
        raise SystemExit('stale integrity 0.10 wording survived synchronization')
    if '### Observaciones bibliográficas 0.2' in text:
        raise SystemExit('stale observations 0.2 heading survived synchronization')
    if 'candidatos técnicos con año: **11**' not in text:
        raise SystemExit('candidate 11/26 summary missing after synchronization')

    PATH.write_text(text, encoding='utf-8')
    print('synchronized', PATH)
    print('bytes', PATH.stat().st_size)


if __name__ == '__main__':
    main()
