# LTMD Full-Text Research Layer (FTRL)

Versión de arquitectura: `LTMD_FTRL_0.1`  
Estado: **prototipo funcional; piloto inicial W5 Historia**.

## Propósito

La **Full-Text Research Layer (FTRL)** incorpora a LTMD una capa reconstruible de transcripción OCR completa por página y búsqueda de texto completo. Su objetivo es permitir concordancias longitudinales reproducibles del tipo *cuándo, dónde y cómo aparece X* sin confundir una coincidencia automática con un hallazgo histórico validado.

La capa se diseña para responder preguntas sobre personajes, conceptos, instituciones y expresiones a lo largo del corpus técnicamente admitido: por ejemplo, `masonería`, `Benito Juárez`, `indígenas`, `Iglesia`, `democracia` o `Revolución mexicana`.

## Regla epistemológica

> `ocr_available != text_verified`  
> `search_hit != historical_claim`

El OCR es una representación computacional falible. Un resultado FTS es un **candidato trazable** que debe poder verificarse contra la página fuente antes de sostener una afirmación histórica. FTRL no modifica el estado de validación semántica humana de LTMD-U1.

## Arquitectura

```text
asset manifest fuente-admitido
        ↓
URL institucional + SHA-256 esperado
        ↓
recuperación local y verificación SHA-256
        ↓
Tesseract (texto TXT + confianza TSV)
        ↓
registro JSONL canónico por página
        ├── ocr_text_raw
        ├── ocr_sha256
        ├── search_text
        └── search_text_sha256
        ↓
SQLite
        ├── pages
        ├── identities
        └── pages_fts (FTS5)
        ↓
concordancia / exportación
        ↓
verificación humana de páginas candidatas
        ↓
análisis histórico
```

## Separación entre objeto canónico e identidad histórica

FTRL indexa el texto una sola vez por **objeto canónico de procesamiento**. Las identidades históricas que LTMD ya demostró como aliases byte-exactos se conservan en la tabla `identities`, apuntando al objeto canónico correspondiente.

Esta decisión evita duplicar OCR y evita inflar conteos por reutilización técnica, sin borrar que dos visores históricos puedan corresponder a identidades catalográficas distintas.

## Persistencia y derechos

Por defecto, **el texto OCR íntegro y la base SQLite completa son artefactos locales reconstruibles y no se versionan en GitHub**. El repositorio público conserva:

- código de reconstrucción;
- esquema del registro;
- metodología;
- manifiestos fuente y hashes ya admisibles;
- reglas de consulta y validación.

Esta separación reduce el riesgo de convertir LTMD en un mecanismo de redistribución masiva del texto de materiales cuyos derechos pertenecen a SEP/CONALITEG u otros titulares. No altera las licencias de las obras fuente.

## Artefactos locales

Rutas recomendadas:

```text
local/ftrl/
├── w5/assets/
├── ltmd_u1_w5_page_ocr.jsonl
└── ltmd_u1_w5_ocr_search.sqlite
```

`local/` está excluido de Git.

## Piloto W5 Historia

W5 es el primer dominio porque su cohorte técnica está cerrada y su `asset manifest` contiene URL de página y SHA-256 verificable. Las identidades 2018 que LTMD ya documentó como aliases exactos de 2019 no requieren OCR redundante.

### Requisitos del sistema

- Python 3.11 o superior;
- SQLite con FTS5;
- Tesseract OCR;
- datos de idioma español de Tesseract (`spa`).

### Construir OCR página por página

Prueba mínima:

```bash
python scripts/build_page_ocr_corpus.py \
  --asset-manifest data/catalog/ltmd_u1_w5_history_asset_manifest.csv \
  --processing-inventory data/catalog/ltmd_u1_w5_history_processing_inventory.csv \
  --wave W5 \
  --output local/ftrl/ltmd_u1_w5_page_ocr.jsonl \
  --cache-dir local/ftrl/w5/assets \
  --max-pages 10
```

Ejecución completa y reanudable:

```bash
python scripts/build_page_ocr_corpus.py \
  --asset-manifest data/catalog/ltmd_u1_w5_history_asset_manifest.csv \
  --processing-inventory data/catalog/ltmd_u1_w5_history_processing_inventory.csv \
  --wave W5 \
  --output local/ftrl/ltmd_u1_w5_page_ocr.jsonl \
  --cache-dir local/ftrl/w5/assets \
  --resume
```

Cada activo descargado se acepta para OCR únicamente si su SHA-256 coincide con el valor ya registrado en el manifiesto.

### Construir índice FTS5

```bash
python scripts/build_search_index.py \
  --input local/ftrl/ltmd_u1_w5_page_ocr.jsonl \
  --processing-inventory data/catalog/ltmd_u1_w5_history_processing_inventory.csv \
  --output local/ftrl/ltmd_u1_w5_ocr_search.sqlite
```

### Validar

```bash
python scripts/validate_ocr_corpus.py \
  --input local/ftrl/ltmd_u1_w5_page_ocr.jsonl \
  --db local/ftrl/ltmd_u1_w5_ocr_search.sqlite
```

### Consultar

```bash
python scripts/query_ocr_corpus.py \
  --db local/ftrl/ltmd_u1_w5_ocr_search.sqlite \
  --query 'masonería OR masón OR masones OR masónica OR masónicas'
```

Frase exacta:

```bash
python scripts/query_ocr_corpus.py \
  --db local/ftrl/ltmd_u1_w5_ocr_search.sqlite \
  --query '"Benito Juárez"'
```

Filtros:

```bash
python scripts/query_ocr_corpus.py \
  --db local/ftrl/ltmd_u1_w5_ocr_search.sqlite \
  --query 'yorkino OR yorkinos' \
  --generation 1993 \
  --grade-code 6 \
  --format json
```

## Normalización para búsqueda

`ocr_text_raw` conserva la salida textual de Tesseract. `search_text` aplica solamente una normalización conservadora y versionable:

1. Unicode NFKC;
2. eliminación del *soft hyphen*;
3. unión de guiones de final de línea únicamente entre caracteres alfabéticos;
4. colapso de espacios.

El índice FTS5 utiliza el tokenizador `unicode61 remove_diacritics 2`, por lo que la recuperación puede ser tolerante a diacríticos sin reescribir el OCR bruto.

## Identificación y hashes

Cada página canónica recibe un identificador del tipo:

```text
H1993P6HI214:src0032
```

`src0032` identifica la posición del activo fuente, no necesariamente el número impreso de página. Se conservan por separado:

- `source_sha256`: identidad criptográfica del JPEG admitido;
- `ocr_sha256`: identidad del texto OCR bruto;
- `search_text_sha256`: identidad del texto normalizado.

## Reanudación segura

`--resume` reutiliza una transcripción previa solo cuando coinciden:

- página canónica;
- `source_sha256`;
- versión del pipeline;
- versión de Tesseract;
- idioma OCR;
- PSM.

El archivo de salida se reconstruye primero como temporal y reemplaza al corpus anterior únicamente al terminar, de modo que un fallo de red u OCR no destruya una ejecución válida previa.

## Escalamiento

El orden previsto es:

1. W5 Historia como piloto funcional;
2. auditoría de recuperación, rendimiento y falsos negativos OCR;
3. generalización por olas fuente-admitidas;
4. construcción U1 sobre objetos canónicos técnicamente cubiertos;
5. consultas temáticas reproducibles;
6. validación humana de resultados usados en afirmaciones históricas.

Las 18 identidades actualmente fuera de cobertura técnica efectiva no se imputan ni se fuerzan dentro de FTRL.

## Fuera de alcance de 0.1

- corrección humana sistemática del OCR;
- reconocimiento exhaustivo de contenido puramente visual;
- inferencia semántica automática presentada como verdad histórica;
- redistribución pública de un volcado de transcripciones completas;
- resolución por FTRL de retenciones de fuente.

FTRL amplía la capacidad de consulta de LTMD sin debilitar sus reglas de procedencia, dependencia documental y validación.
