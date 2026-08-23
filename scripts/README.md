# Scripts

Las rutinas reproducibles de LTMD cubren inventario de fuentes, recuperación de metadatos, extracción/OCR, normalización, segmentación, validación, análisis de dependencia documental y generación de datos derivados.

Cada script debe poder ejecutarse sin depender de rutas personales y debe registrar versiones y procedencia.

## Full-Text Research Layer (FTRL)

La capa de investigación textual completa utiliza cuatro utilidades principales:

- `build_page_ocr_corpus.py`: reconstruye OCR completo por página a partir de un `asset manifest` fuente-admitido, verifica SHA-256 antes del OCR y permite reanudación segura.
- `build_search_index.py`: construye una base SQLite FTS5 local y preserva la relación entre objetos canónicos e identidades históricas/aliases.
- `query_ocr_corpus.py`: ejecuta concordancias, frases, operadores FTS5 y filtros por ola, generación, grado o visor.
- `validate_ocr_corpus.py`: valida unicidad, hashes OCR, hashes de texto de búsqueda e integridad del índice SQLite.

La arquitectura, el protocolo de consulta y la procedencia OCR se documentan en:

- `docs/LTMD_FULL_TEXT_RESEARCH_LAYER.md`
- `docs/LTMD_SEARCH_METHODOLOGY.md`
- `docs/LTMD_OCR_PROVENANCE.md`

El corpus OCR íntegro y la base SQLite se generan bajo `local/` y no se versionan por defecto.
