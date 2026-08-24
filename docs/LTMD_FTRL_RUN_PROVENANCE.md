# LTMD FTRL — manifiesto de ejecución y procedencia

Versión: `LTMD_FTRL_RUN_0.1`  
Estado: **especificación operativa para ejecuciones locales FTRL**.

## Propósito

Cada ejecución de la Full-Text Research Layer debe producir, además del corpus OCR local y del índice SQLite FTS5, un **manifiesto de corrida sin texto fuente**. El manifiesto registra qué artefactos y versiones intervinieron, qué cardinalidades resultaron, qué entorno de software se observó y qué hashes identifican las entradas y salidas locales.

El objetivo es que una afirmación del tipo “la búsqueda se ejecutó sobre W5” pueda traducirse a una cadena auditable: manifiesto de activos → inventario de procesamiento → corpus OCR → índice FTS5 → manifiesto de corrida → protocolo de consulta → verificación humana de candidatos.

## Regla de publicación

El manifiesto se diseñó para ser **publicable como metadato derivado**: no contiene imágenes, OCR íntegro ni snippets. Puede conservar hashes de artefactos locales cuya redistribución está restringida, porque el hash permite comprobar identidad sin reconstruir el contenido.

La publicación efectiva de cualquier manifiesto debe seguir la matriz vigente de derechos y no cambia la clasificación jurídica de las obras fuente.

## Generación

El orquestador W5 genera el manifiesto automáticamente después de construir y validar el índice:

```bash
python scripts/run_ftrl_w5_pilot.py --full
```

También puede generarse de forma independiente:

```bash
python scripts/summarize_ftrl_run.py \
  --input local/ftrl/ltmd_u1_w5_full_page_ocr.jsonl \
  --db local/ftrl/ltmd_u1_w5_full_ocr_search.sqlite \
  --asset-manifest data/catalog/ltmd_u1_w5_history_asset_manifest.csv \
  --processing-inventory data/catalog/ltmd_u1_w5_history_processing_inventory.csv \
  --label full \
  --output local/ftrl/ltmd_u1_w5_full_run_manifest.json
```

## Contenido mínimo

El manifiesto registra:

- versión de esquema y etiqueta de corrida;
- fecha UTC de generación;
- versión de Python, implementación, SQLite y plataforma;
- SHA-256 y tamaño del JSONL OCR y de la base SQLite;
- SHA-256 de los manifiestos de entrada cuando se proporcionan;
- número de páginas, objetos canónicos, generaciones y grados;
- distribución de páginas por generación y grado;
- versiones de esquema, pipeline OCR, Tesseract, idioma y PSM observadas;
- resumen de confianza OCR, caracteres y palabras;
- páginas con `search_text` vacío;
- integridad SQLite, cardinalidad FTS e identidades históricas representadas.

Los paths se serializan de forma portable: se prefieren rutas relativas al repositorio y, si una entrada se encuentra fuera de él, se conserva sólo el nombre de archivo para evitar filtrar rutas personales del sistema.

## Validaciones duras

`scripts/summarize_ftrl_run.py` aborta si:

1. falta el JSONL o el índice;
2. un archivo de procedencia declarado no existe;
3. el JSONL está vacío o contiene JSON inválido;
4. `PRAGMA integrity_check` no devuelve `ok`;
5. `pages` y `pages_fts` difieren;
6. la cardinalidad de páginas del JSONL difiere de la base SQLite.

Por tanto, `status = validated` significa **integridad técnica interna del paquete de corrida**, no exactitud semántica del OCR ni validez histórica de los resultados.

## Esquema

El contrato público vive en:

- `schemas/ltmd_ftrl_run_manifest.schema.json`

La versión inicial es `LTMD_FTRL_RUN_0.1`. Cambios incompatibles requieren una nueva versión explícita.

## Relación con FAIR y procedencia

Este manifiesto operacionaliza el principio de que los datos y metadatos reutilizables deben conservar procedencia detallada y, cuando sea posible, legible por máquina. No pretende sustituir un modelo formal completo de procedencia; sirve como capa mínima y verificable que puede mapearse posteriormente a PROV-O o empaquetarse dentro de un RO-Crate.

## Límites epistemológicos

El manifiesto no convierte:

- OCR en transcripción verificada;
- una coincidencia FTS en afirmación histórica;
- ausencia de hits en ausencia demostrada;
- alias técnico en equivalencia bibliográfica o semántica.

Su función es hacer reproducible **qué se procesó, con qué versión y con qué integridad**, manteniendo separada la interpretación.
