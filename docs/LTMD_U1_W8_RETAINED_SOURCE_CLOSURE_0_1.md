# LTMD-U1 W8 — cierre documental de fuentes retenidas 0.1

Versión: `LTMD_U1_W8_RETAINED_SOURCE_CLOSURE_0.1`.

## Alcance

Este documento cierra la investigación documental acotada de las cuatro identidades W8 Artes que permanecen fuera de la cohorte fuente-admitida:

- `H2018P3EAA`
- `H2018P4EAA`
- `H2018P5EAA`
- `H2018P6EAA`

El cierre es **documental**, no una promoción de fuente. No crea aliases, no incorpora bytes y no modifica `ocr_source_admitted`.

## Evidencia previa

El ledger transversal `data/catalog/ltmd_u1_retained_source_attempts.csv` ya conserva para las cuatro identidades:

1. consolidación del estado fuente retenido;
2. búsqueda por clave exacta en dominios oficiales e índices públicos;
3. ausencia de una representación institucional o archivística con correspondencia determinista y bytes verificables.

La cohorte W8 fuente-admitida permanece cerrada técnicamente en `docs/LTMD_U1_W8_COMPLETION.md`: 20/20 identidades históricas preservadas, 16 canónicos procesados y cuatro retenciones explícitas.

## Pasada final acotada — 2026-08-30

Artefacto: `data/catalog/ltmd_u1_w8_retained_source_final_search_2026-08-30.csv`.

Se limitaron los intentos a señales capaces de satisfacer el criterio de la issue #9:

- claves exactas de viewer;
- URI institucional exacto del viewer;
- patrón institucional exacto de activos `/c/{viewer_key}/{page}.jpg`;
- consulta del índice público vigente `CC-MAIN-2026-34` de Common Crawl para cada subárbol.

No se localizaron bytes institucionales o archivísticos que pudieran conservarse con tamaño, SHA-256 y correspondencia posicional determinista. Los fallos/no-resultados de infraestructura e índice **no se interpretan como prueba de inexistencia histórica**.

## Clasificación final de la investigación

| viewer_key | fuente admitida | clase documental de cierre |
|---|---|---|
| `H2018P3EAA` | no | `final_retention_after_bounded_search` |
| `H2018P4EAA` | no | `final_retention_after_bounded_search` |
| `H2018P5EAA` | no | `final_retention_after_bounded_search` |
| `H2018P6EAA` | no | `final_retention_after_bounded_search` |

Esta clase satisface el tercer criterio de cierre de la issue #9: retención final explícita después de una búsqueda acotada y reproducible.

## Separación frente a FTRL

`final_retention_after_bounded_search` es una **decisión de cierre documental de la investigación de fuentes**, no una mutación automática del estado FTRL. En este corte:

- `ocr_source_admitted`: sin cambios;
- corpus W8 procesado: sin cambios;
- conteo de páginas procesadas: sin cambios;
- `text_verified`: sin cambios;
- `semantic_ready`: sin cambios;
- estado estructurado del ledger FTRL global: sin cambios.

Por tanto, no se reinterpretan estas cuatro identidades como `final_exception` ni se altera `global_closure.eligible` mediante este documento.

## Condición de reactivación

La investigación sólo debe reactivarse si aparece evidencia nueva capaz de cambiar admisibilidad, por ejemplo:

- captura archivada del URI exacto con bytes recuperables;
- endpoint alternativo derivado de código o metadatos institucionales;
- reproducción oficial inequívoca con alineación posicional verificable;
- evidencia criptográfica o documental suficiente para reconstruir la representación sin imputación.

Hasta entonces, repetir búsquedas genéricas, aproximaciones por título/grado o comparaciones con materiales 2019 no añade evidencia y queda fuera del protocolo.
