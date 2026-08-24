# FTRL W5 — validación real de 10 páginas

Fecha de ejecución: **24 de agosto de 2026 UTC**  
Estado: **validación técnica superada; no constituye validación semántica ni resultado historiográfico**.

## Identificación de la ejecución

La prueba se ejecutó en GitHub Actions mediante el workflow `Validate FTRL W5 real 10-page pilot`, introducido por el PR #17.

- workflow run: `32679930766`;
- head SHA probado: `bc5c7f304c65b54feefdd2d8b363caafa19b1e08`;
- merge ref probado por GitHub Actions: `e348e4086ea709b7e6391ba32547628964729820`;
- PR #17 integrado posteriormente en `main` como `bce79d919828f3781a9d2bcff11738b5b516323d`;
- artefacto temporal original: `ltmd-u1-w5-pilot-10-run-manifest`, ID `9503824076`;
- SHA-256 del ZIP del artefacto: `1d52ab801e7a7d5e5bbfd0064ffa276c9e34ce04efd478707481917d02a4fac5`.

El manifiesto sin texto extraído de ese artefacto se conserva permanentemente en:

- `data/research/validation/ltmd_u1_w5_pilot_10_run_manifest_2026-08-24.json`.

## Alcance documental

La selección operacional fue el límite reproducible `--pages 10` aplicado al manifiesto W5 ordenado por generación, grado, `viewer_key` e índice fuente. Las diez páginas pertenecieron al objeto canónico:

- `H1993P4HI198`;
- generación de catálogo: `1993`;
- grado: `4`;
- núcleo de título: `Historia`.

Se procesaron `src0000` y `src0002`–`src0010`. La ausencia de `src0001` no es un salto introducido por el OCR: refleja la secuencia fuente-admitida ya registrada en el manifiesto de activos.

## Cadena de integridad

La ejecución utilizó los siguientes insumos públicos de control:

| Artefacto | SHA-256 |
|---|---|
| `data/catalog/ltmd_u1_w5_history_asset_manifest.csv` | `120ea791e91938ef2cdcab7f790c7fac10a16abe53aef057d36658a059320f14` |
| `data/catalog/ltmd_u1_w5_history_processing_inventory.csv` | `66982ca6e1d61fcbf3e2ff56dd34a819ede16fa675c8cf16ff1c19b1443d207f` |

Cada JPEG se descargó mediante `build_page_ocr_corpus.py`, que compara sus bytes con `source_sha256` antes de permitir el OCR. La corrida llegó a término con las diez páginas, por lo que ninguna de las diez descargas presentó discrepancia criptográfica en esta ejecución.

Los productos locales no publicados quedaron identificados por:

| Producto local | SHA-256 | Tamaño |
|---|---|---:|
| JSONL OCR de 10 páginas | `a32f22697dfb7a95ea8e3420c15d890cc218eacd2c070799a95a46c934d95628` | 42,900 bytes |
| SQLite FTS5 | `c74f99f726b1a21eb928e785aed8d96ee4a9aa7811dfeeb693c9daac0ebb2fe5` | 126,976 bytes |

El workflow comprobó además con `git check-ignore` que ambos permanecieran bajo `local/` y no fueran candidatos a publicación accidental.

## Entorno reproducible

- CPython `3.12.14`;
- SQLite `3.45.1` con FTS5;
- Tesseract `5.3.4`;
- datos lingüísticos `spa`;
- PSM `3`;
- pipeline `LTMD_FTRL_OCR_0.1`;
- esquema de página `LTMD_PAGE_OCR_0.1`;
- runner Linux Ubuntu 24.04 en GitHub Actions.

## Resultados técnicos

| Indicador | Resultado |
|---|---:|
| páginas solicitadas | 10 |
| registros OCR producidos | 10 |
| filas `pages` en SQLite | 10 |
| filas FTS5 | 10 |
| `PRAGMA integrity_check` | `ok` |
| objetos canónicos representados | 1 |
| identidades históricas representadas | 1 |
| bytes fuente conocidos | 756,556 |
| caracteres OCR | 16,252 |
| palabras OCR | 2,778 |
| páginas con `search_text` vacío | 1 |
| páginas con confianza OCR observada | 9 |
| confianza media | 86.162176 |
| confianza mediana | 88.298368 |
| confianza mínima | 64.661886 |
| confianza máxima | 93.864448 |

La página `H1993P4HI198:src0000` produjo `0` caracteres y confianza no observable. `H1993P4HI198:src0010` produjo `50` caracteres con confianza `64.661886`, el mínimo del piloto. Estos dos casos quedan señalados para inspección visual; el registro técnico por sí solo no permite decidir si se trata de página sin texto, diseño gráfico, texto escaso o fallo de reconocimiento.

## Qué demuestra esta prueba

La ejecución demuestra, para este recorte real de diez páginas, que la cadena admitida por LTMD puede reconstruirse en un entorno limpio desde URLs fuente, verificar los bytes contra hashes preexistentes, ejecutar OCR español, construir un índice FTS5, preservar cardinalidad 10/10 y producir un manifiesto sin texto con procedencia técnica.

También demuestra que la política de no redistribución funciona en CI: el OCR íntegro y la base de búsqueda se generaron para comprobar el pipeline, pero permanecieron en `local/`; sólo el manifiesto de metadatos fue transferido como artefacto.

## Qué no demuestra

Esta prueba **no** demuestra todavía:

- cobertura completa de W5;
- calidad OCR suficiente en todas las generaciones, grados o diseños editoriales;
- ausencia de falsos negativos;
- validez semántica del texto reconocido;
- frecuencia o significado histórico de ningún término;
- desempeño sobre las 15 unidades canónicas y 18 identidades históricas de W5.

Por ello permanecen vigentes los gates `ocr_available != text_verified`, `search_hit != historical_claim` y `zero_hits != demonstrated_absence`.

## Siguiente gate

Antes de interpretar consultas historiográficas, el siguiente paso es ejecutar W5 completo y auditar manualmente una muestra estratificada. La revisión visual debe incluir al menos la página sin texto `src0000`, el caso de confianza mínima `src0010` y páginas ordinarias de distintas zonas de confianza, sin convertir la confianza media de Tesseract en una medida suficiente de exactitud textual.
