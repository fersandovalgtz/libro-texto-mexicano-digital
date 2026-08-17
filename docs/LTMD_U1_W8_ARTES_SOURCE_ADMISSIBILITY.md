# LTMD-U1 W8 Artes — compuerta de admisibilidad de fuente

Versión: `LTMD_U1_W8_ARTES_SOURCE_ADMISSIBILITY_0.1`.

## Resultado

- Identidades W8 reconciliadas exactamente 1:1: **20/20**.
- `SOURCE_ADMISSIBLE`: **16/20**.
- `SOURCE_RETAINED`: **4/20**.
- Alias creados: **0**.
- Estado semántico de las 20 identidades: `WAITING_HUMAN_REFERENCE`.

Las cinco capas de identidad —cola U1, scope W8, arquitectura, inventario declarado y resumen de activos— contienen exactamente el mismo conjunto de 20 `viewer_key`. El auditor `scripts/audit_ltmd_u1_w8_artes_source_admissibility.py` aborta si detecta cualquier deriva entre ellas.

Para esta cohorte, `book_id` se materializa como el mismo valor literal de `viewer_key` después de comprobar la reconciliación 1:1. Esta materialización no crea una equivalencia nueva ni autoriza inferencias de identidad histórica fuera de W8.

## Retenciones de fuente

Las cuatro identidades retenidas son:

- `H2018P3EAA`: 90 posiciones declaradas; 0 JPEG servidos; 90 posiciones internas no servidas.
- `H2018P4EAA`: 90 posiciones declaradas; 0 JPEG servidos; 90 posiciones internas no servidas.
- `H2018P5EAA`: 90 posiciones declaradas; 0 JPEG servidos; 90 posiciones internas no servidas.
- `H2018P6EAA`: 98 posiciones declaradas; 0 JPEG servidos; 98 posiciones internas no servidas.

Los cuatro visores 2018 conservan arquitectura oficial verificable, pero el subtree de activos observado no sirve los JPEG declarados. Por tanto, la retención es **de fuente**; no es una falla de identidad ni de arquitectura. LTMD no imputará contenido desde 2019, desde el mismo grado ni desde ningún libro vecino para llenar esos huecos.

## Regla de admisión

Una identidad es `SOURCE_ADMISSIBLE` sólo cuando satisface simultáneamente:

1. reconciliación exacta 1:1 entre las capas documentales;
2. `ag_clave == viewer_key`;
3. arquitectura dinámica estándar verificada;
4. al menos un JPEG fuente efectivamente servido;
5. cero huecos internos;
6. cero errores de sondeo;
7. como máximo un candidato terminal sintético; y
8. `direct_asset_ready=1`.

El resultado actual deja 16 identidades técnicamente habilitadas para abrir la fase OCR/FRAGSEG y cuatro en `SOURCE_RETAINED`.

## Límites de interpretación

La admisibilidad de fuente es una condición técnica. **No demuestra** independencia semántica, continuidad curricular, equivalencia histórica ni preparación para análisis sustantivo. Las 20 identidades permanecen en `WAITING_HUMAN_REFERENCE`.

No se crea ningún alias por semejanza de título, grado, generación, cardinalidad, OCR o apariencia visual. Una dependencia o alias posterior sólo podrá sostenerse mediante identidad criptográfica exacta o evidencia documental inequívoca.

Este gate **no incrementa por sí mismo** la cobertura técnica efectiva global de U1. W8 sólo podrá incorporarse a esa cobertura después de completar OCR/FRAGSEG, verificar integridad y procedencia, ejecutar análisis de dependencia por hashes exactos y publicar la evidencia correspondiente.

Los activos de terceros se recuperan únicamente para verificación/procesamiento temporal. Los JPEG fuente no se persisten ni se relicencian como parte de LTMD.
