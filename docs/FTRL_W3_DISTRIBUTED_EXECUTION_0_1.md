# FTRL W3 — ejecución distribuida 0.1

## Alcance

Este protocolo fija la arquitectura exhaustiva de `W3 Español/Lengua` después del cierre canónico de W1 y de la medición controlada de runtime de W3. No implica validación textual ni semántica.

Denominador operativo: **130 identidades históricas, 114 objetos canónicos y 20,765 páginas fuente**.

## Evidencia para congelar la topología

El piloto canónico `32852599812`, sobre el commit `0e972fddce8e4efe4f194447c6e2dd33e81c95e7`, procesó 100/100 páginas y validó SQLite/FTS5/QC. La fase de ejecución duró 81 segundos. El manifiesto registró 100 `page_rows`, 100 `fts_rows`, `sqlite_integrity=ok`, confianza OCR media 81.6888244 y mediana 90.023849; 29 páginas quedaron señaladas para QC. Estos indicadores son técnicos: `ocr_available != text_verified`.

W1 aporta una segunda referencia empírica: sus shards de 407–408 páginas completaron OCR/SQLite/FTS5/QC de forma estable, con ejemplos observados alrededor de 0.94–1.02 segundos por página en la etapa de ejecución.

## Topología congelada

W3 se particiona de forma determinista mediante orden estable `(catalog_generation, grade_code, viewer_key, source_image_index)` y partición contigua balanceada en **52 shards**:

- 17 shards × 400 páginas;
- 35 shards × 399 páginas;
- total exacto: 20,765 páginas;
- máximo 8 shards concurrentes.

La elección conserva aproximadamente el tamaño por shard ya validado en W1. Se privilegia aislamiento de fallas, reiniciabilidad y trazabilidad frente a reducir el número de jobs.

## Gates de ejecución

Cada shard debe reconstruir los inputs canónicos, verificar el gate W1, ejecutar OCR, crear SQLite/FTS5, validar integridad y cardinalidad, construir QC y producir evidencia sin texto restringido. Los 52 shards deben compartir un mismo commit y workflow run.

El gate global sólo pasa si la unión de hashes de identidad de página es **exactamente 20,765/20,765, única y sin extras**, contra el manifiesto canónico W3.

## Preservación

Los productos restringidos de cada shard se comprimen y cifran antes de cualquier upload de Actions. La clave simétrica se envuelve con la clave pública archivística del proyecto. Actions funciona únicamente como handoff temporal.

Después de la validación computacional global, los handoffs se recuperan en entorno privado, se descifran y se consolidan mediante `scripts/consolidate_ftrl_w3_distributed.py`. Conforme al canon 0.2, Drive debe terminar con **una sola copia canónica consolidada de W3**, verificada por checksums y privacidad; los handoffs redundantes pueden eliminarse después del cierre.

## Estados epistemológicos

Incluso tras una ejecución exhaustiva exitosa:

- `distributed_computationally_validated != archival_complete`;
- `ocr_available != text_verified`;
- `corpus_ready != semantic_ready`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`.

La arquitectura productiva sólo se lanza mediante el stamp versionado `data/research/ltmd_u1_w3_distributed_run_stamp.json`, que se crea separadamente después de que esta configuración pase CI y sea fusionada a `main`.
