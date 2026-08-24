# LTMD-U1 FTRL completion ledger 0.2

## Propósito

El ledger 0.2 mantiene una fila por cada una de las 542 identidades documentales LTMD-U1 y conserva sin cambios el denominador exhaustivo, las disposiciones documentales y los estados FTRL ya demostrados. La revisión 0.2 incorpora la topología técnica W3 Español/Lengua que ya fue validada por el preflight FTRL, sin confundir esa preparación con una corrida FTRL integral.

El ledger sigue siendo exclusivamente metadata/text-free: no contiene OCR, snippets, imágenes fuente ni identificadores privados de Google Drive.

## Cambio respecto de 0.1

La versión 0.1 conocía topología FTRL explícita para W1 y W5. Tras el preflight W3, mantener las 130 identidades Español/Lengua como `pending_topology` dejó de describir correctamente la evidencia versionada. La versión 0.2 integra:

- 130 identidades W3;
- 114 objetos canónicos;
- 107 canónicos directos;
- 7 canónicos parciales con huecos digitales explícitos;
- 8 aliases byte-exactos;
- 8 relaciones de ruta 2018→2019 demostradas;
- 20,765 páginas fuente canónicas;
- 8 posiciones internas no servidas, documentadas y no rellenadas heurísticamente.

Las 130 identidades W3 permanecen con `ftrl_status=pending`, `corpus_ready=0`, `ocr_available=0`, `text_verified=0`, `semantic_ready=0` y `archival_complete=0` hasta que la secuencia de ejecución autorizada complete sus gates.

## Fuente de topología W3

La topología se toma de `data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv`. El generador 0.2 exige exactamente las cardinalidades y relaciones congeladas por `FTRL_W3_PREFLIGHT_PROTOCOL_0_1.md`; cualquier deriva hace fallar la generación.

Las siete identidades canónicas con huecos internos se registran como `source_ready=partial`. Las demás identidades W3 se registran como `source_ready=full`, incluidas aquellas cubiertas por una relación técnica demostrada hacia un objeto canónico. `source_ready` describe cobertura técnica reproducible, no completitud bibliográfica ni validación semántica.

## Separaciones obligatorias

- `topology_ready != corpus_ready`
- `preflight_ready != ftrl_validated`
- `corpus_ready != semantic_ready`
- `ocr_available != text_verified`
- `search_hit != historical_claim`
- `zero_hits != demonstrated_absence`
- `computationally_validated != archival_complete`

## Generación

Los productos canónicos siguen siendo:

- `data/research/ltmd_u1_ftrl_completion_ledger.csv`
- `data/research/ltmd_u1_ftrl_completion_summary.json`

A partir de esta revisión se generan mediante `scripts/build_ltmd_u1_ftrl_completion_ledger_v2.py`. El generador 0.1 se conserva como antecedente reproducible y es utilizado internamente para preservar los estados previamente demostrados antes de enriquecer W3.
