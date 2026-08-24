# FTRL W5 — ejecución completa paralela

Versión operacional: `LTMD_FTRL_PARALLEL_RUN_0.1`  
Ámbito: W5 Historia.

## Problema que resuelve

W5 representa 15 objetos canónicos fuente-admitidos y 18 identidades históricas cubiertas. El inventario de procesamiento registra 2,653 JPEG directos para los objetos canónicos. Ejecutar el OCR como una única secuencia mezcla dos riesgos evitables: una interrupción tardía obliga a depender de una corrida larga y la trazabilidad por objeto queda menos visible.

La estrategia paralela divide W5 exclusivamente por `viewer_key` canónico. Cada shard usa el mismo manifiesto fuente, el mismo inventario de procesamiento, la misma verificación SHA-256 y el mismo pipeline OCR. Después, los JSONL locales se fusionan en orden determinista y sólo entonces se construyen el SQLite FTS5, el manifiesto de corrida y, si se solicita, las consultas preregistradas.

## Invariantes

La paralelización no cambia la unidad documental ni la topología de identidades:

- cada página pertenece a un único objeto canónico;
- cada activo se verifica contra el SHA-256 previamente admitido antes de OCR;
- ningún alias 2018 se procesa como un segundo corpus OCR;
- la tabla `identities` se reconstruye después de fusionar los 15 canónicos y debe representar 18 identidades históricas;
- dos shards no pueden compartir `page_id`;
- un shard no puede contener registros de otro `viewer_key`;
- la suma de páginas observadas por shard debe coincidir con `direct_source_jpegs` del inventario cuando la corrida es completa.

## Ejecución completa

```bash
python scripts/run_ftrl_w5_parallel.py \
  --workers 4 \
  --run-preregistered-queries
```

El número de workers es configurable. Cada proceso Tesseract recibe `OMP_THREAD_LIMIT=1` por defecto para evitar que la concurrencia entre shards se multiplique internamente de forma no controlada.

## Ejecución acotada para integración

Puede probarse la arquitectura con un subconjunto explícito y un límite por objeto:

```bash
python scripts/run_ftrl_w5_parallel.py \
  --workers 2 \
  --viewer-key H1993P4HI198 \
  --viewer-key H1993P5HI206 \
  --max-pages-per-viewer 2 \
  --output-dir local/ftrl-parallel-smoke
```

Una ejecución de este tipo se etiqueta como `parallel_subset` y **no** puede ejecutar el protocolo historiográfico preregistrado.

## Salidas locales

La corrida completa produce bajo `local/ftrl/`:

- `shards/<viewer_key>.jsonl`: OCR por objeto canónico;
- `w5/assets/<viewer_key>/...`: caché de imágenes fuente verificadas;
- `ltmd_u1_w5_full_page_ocr.jsonl`: corpus OCR fusionado;
- `ltmd_u1_w5_full_ocr_search.sqlite`: índice FTS5;
- `ltmd_u1_w5_query_candidates.json`: candidatos con snippets, si se ejecutan consultas.

Estos artefactos contienen material fuente u OCR y permanecen fuera de Git.

## Salidas sin texto aptas para preservación

La misma corrida genera:

- `ltmd_u1_w5_full_run_manifest.json`: hashes, entorno, cardinalidades, versiones y procedencia Git/CI;
- `ltmd_u1_w5_full_parallel_summary.json`: workers, duración, páginas esperadas/observadas y métricas por shard;
- `ltmd_u1_w5_query_summary.json`: conteos agregados del protocolo;
- `ltmd_u1_w5_query_locators.json`: localizadores de candidatos con identificadores, URLs fuente, hashes, confianza y ranking, sin snippets OCR.

La separación entre salidas restringidas y salidas sin texto permite conservar evidencia reproducible sin publicar el corpus reconocido.

## Validación al fusionar

El orquestador aborta si:

1. un shard falla;
2. un shard contiene una cantidad distinta de páginas a la esperada;
3. aparece JSON inválido;
4. un shard contiene un `viewer_key` ajeno;
5. se repite un `page_id` entre shards;
6. el total fusionado difiere de la suma esperada;
7. la cardinalidad del manifiesto final difiere del corpus fusionado;
8. el número de objetos canónicos del manifiesto difiere del número de shards;
9. en W5 completo, el SQLite no representa las 18 identidades históricas esperadas;
10. las validaciones existentes de SQLite/FTS o del corpus OCR fallan.

## Reanudación

Cada shard usa `--resume`. Si la estación conserva `local/ftrl/shards/` y la caché de activos, una nueva ejecución puede reutilizar registros cuyo SHA-256 fuente, versión de pipeline, Tesseract, idioma y PSM sigan coincidiendo. La fusión y el índice se reconstruyen después de validar todos los shards seleccionados.

## Límite epistemológico

La paralelización es una mejora de ejecución, no una mejora automática de reconocimiento. Mantiene vigentes:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`.

Una corrida completa técnicamente válida habilita la fase de auditoría visual y análisis; no la sustituye.
