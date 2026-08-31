# LTMD Analytics HTTP API 0.1

Versión de transporte: **LTMD Analytics HTTP 0.1**  
Motor corpus-wide: `LTMD_U1_CORPUS_QUERY_ENGINE_0.1`  
Motor del vertical indígena: `LTMD_ANALYTICS_QUERY_ENGINE_0.2`

## Propósito

Esta capa expone por HTTP dos superficies read-only sobre los insumos privados de LTMD-U1:

1. **consulta corpus-wide** sobre el Índice Universal de 86,549 páginas mediante FTS5, con filtros y denominadores exactos;
2. **vertical indígena preregistrado 0.2**, preservando su ledger de 1,151 candidatos y, cuando se configura, añadiendo contexto agregado de reutilización/similitud.

La API devuelve únicamente agregados, filtros, versiones, procedencia criptográfica y advertencias epistemológicas. No devuelve OCR, `page_id`, identificadores de objetos, snippets, URLs fuente, hashes de página ni pares concretos de similitud.

## Endpoints P0

### `GET /health`

Comprueba que el servicio y los insumos obligatorios del vertical están disponibles. Informa además, sin revelar rutas, si la consulta corpus-wide y el contexto de reutilización están configurados.

Campos relevantes:

- `corpus_query_configured`
- `reuse_context_configured`
- `corpus_query_engine_version`
- `human_validation_complete=false`

### `GET /v1/meta`

Devuelve versiones, estado científico, vocabularios de filtros del vertical indígena y estado de configuración corpus-wide. Si el Índice Universal está configurado, incluye su SHA-256 calculado por el servidor.

### `GET /v1/corpus/query`

Ejecuta una expresión FTS5 directamente sobre el Índice Universal privado y devuelve agregados seguros.

Parámetros repetibles:

- `generation`
- `grade_code`
- `wave`

Parámetros simples:

- `q`: expresión FTS5 obligatoria;
- `group_by`: `generation | grade_code | wave`.

Ejemplo:

```bash
curl --get 'http://127.0.0.1:8000/v1/corpus/query' \
  --data-urlencode 'q=democracia' \
  --data-urlencode 'group_by=generation'
```

La tasa `candidate_pages_per_1000` usa como denominador exactamente el mismo subuniverso afectado por los filtros activos. Cero hits no demuestran ausencia histórica.

### `GET /v1/indigenous/query`

Consulta el ledger preregistrado de lenguas indígenas sin recomputar su selección.

Parámetros repetibles:

- `generation`
- `grade_code`
- `wave`
- `language_group`
- `explicit_term`

Parámetros simples:

- `q`: etiqueta descriptiva de la consulta;
- `group_by`: `generation | grade_code | wave | language_group | explicit_term`.

Ejemplo:

```bash
curl --get 'http://127.0.0.1:8000/v1/indigenous/query' \
  --data-urlencode 'q=rarámuri por generación' \
  --data-urlencode 'language_group=Tarahumara / rarámuri' \
  --data-urlencode 'group_by=generation'
```

Cuando `LTMD_REUSE_SIMILARITY_PATH` está configurado junto con el Índice Universal, la respuesta puede incluir `reuse_context` en el total filtrado y en cada `breakdown`. Esa capa permanece `exploratory_signal`, no cambia la membresía del vertical y nunca crea aliases.

## Configuración privada

### Vertical indígena

```text
LTMD_INDIGENOUS_LEDGER_PATH=/ruta/privada/ltmd_u1_indigenous_languages_candidate_ledger_0_2.csv
LTMD_GENERATION_SUMMARY_PATH=/ruta/al/ltmd_u1_indigenous_languages_generation_summary_0_2.csv
```

`LTMD_GENERATION_SUMMARY_PATH` es opcional; si no se define, se usa la tabla pública versionada del repositorio.

### Consulta corpus-wide

```text
LTMD_UNIVERSAL_INDEX_PATH=/ruta/privada/ltmd_u1_universal_index_0_1.canonical.sqlite
LTMD_UNIVERSAL_INDEX_SHA256=aec55cc7dd83c2e1e22d26e3baf8f7ca2e35e32898827ec84e6222edd4bcf7a2
```

`LTMD_UNIVERSAL_INDEX_PATH` habilita por sí solo `/v1/corpus/query`. `LTMD_UNIVERSAL_INDEX_SHA256` es opcional pero **obligatorio para staging canónico**: si se define, el servidor verifica el archivo y degrada el servicio si no coincide.

### Contexto de reutilización/similitud

```text
LTMD_REUSE_SIMILARITY_PATH=/ruta/privada/ltmd_u1_reuse_similarity_0_1.sqlite
```

El artefacto de reutilización es opcional. Si se define, requiere también `LTMD_UNIVERSAL_INDEX_PATH`. El Índice Universal no requiere el artefacto de reutilización para operar.

Todos los artefactos privados deben permanecer:

- fuera del repositorio Git;
- fuera de `public_html`;
- fuera de artefactos públicos de CI;
- fuera de logs y respuestas HTTP.

## Ejecución local

```bash
python3 -m pip install -r requirements-analytics.txt
export LTMD_INDIGENOUS_LEDGER_PATH=/ruta/privada/ledger.csv
export LTMD_UNIVERSAL_INDEX_PATH=/ruta/privada/universal-index.sqlite
export LTMD_UNIVERSAL_INDEX_SHA256=aec55cc7dd83c2e1e22d26e3baf8f7ca2e35e32898827ec84e6222edd4bcf7a2
export LTMD_REUSE_SIMILARITY_PATH=/ruta/privada/reuse-similarity.sqlite
python3 -m flask --app analytics_api.app run --host 127.0.0.1 --port 8000
```

## cPanel / Phusion Passenger

La aplicación usa Flask/WSGI y el repositorio contiene **`passenger_wsgi.py` en la raíz**. La disponibilidad de Application Manager/Setup Python App depende del proveedor de hosting.

### Flujo canónico de staging

1. clonar o actualizar el repositorio dentro del home de la cuenta y **fuera de `public_html`**;
2. usar ese checkout como application root;
3. confirmar que el checkout contiene un `main` igual o posterior al commit que fusiona esta superficie corpus-wide;
4. crear/seleccionar un entorno Python 3;
5. instalar:

```bash
python3 -m pip install -r requirements-analytics.txt
```

6. usar el `passenger_wsgi.py` de la raíz como startup WSGI;
7. materializar fuera del checkout y fuera de `public_html`:
   - ledger indígena privado;
   - Índice Universal U1 canónico descomprimido;
   - reutilización/similitud U1 descomprimido;
8. verificar SHA-256 del Índice Universal: `aec55cc7dd83c2e1e22d26e3baf8f7ca2e35e32898827ec84e6222edd4bcf7a2`;
9. definir las variables de entorno anteriores;
10. registrar/habilitar la aplicación en Application Manager/Setup Python App/Passenger;
11. reiniciar Passenger;
12. ejecutar el gate HTTP completo descrito abajo;
13. sólo tras aprobar staging iniciar/conectar el frontend institucional.

### Reinicio Passenger

Cuando el proveedor use la convención estándar:

```bash
mkdir -p tmp
touch tmp/restart.txt
```

Si Setup Python App ofrece un botón/acción propia de reinicio, usar ese mecanismo.

## Gate HTTP de staging

El despliegue no se considera aprobado hasta verificar:

1. `GET /health` → 200, `status=ok`, `corpus_query_configured=true`;
2. `GET /v1/meta` → 200, `corpus_index_sha256` igual al SHA canónico y `human_validation_complete=false`;
3. `GET /v1/corpus/query?q=democracia&group_by=generation` → 200, respuesta `exploratory_signal`, sin contenido privado;
4. `GET /v1/indigenous/query` con el filtro rarámuri y `group_by=generation` → 200, agregados del ledger preregistrado;
5. `POST /v1/corpus/query` y `POST /v1/indigenous/query` → 405;
6. ninguna respuesta contiene rutas privadas, `page_id`, OCR, snippets, IDs de objetos, URL fuente o hashes de página/OCR;
7. no existe CORS abierto por defecto.

## Denominadores

La superficie corpus-wide calcula denominadores exactos desde el mismo Índice Universal para cualquier combinación de generación, grado y ola. El vertical indígena conserva sus denominadores metodológicos existentes y no los sustituye retrospectivamente por otra selección.

## Estado epistemológico

Toda consulta mantiene:

```text
result_state = exploratory_signal
human_validation_complete = false
```

Las reglas obligatorias siguen siendo:

- `ocr_available != text_verified`
- `search_hit != historical_claim`
- `zero_hits != demonstrated_absence`
- `computational_candidate != semantic_ready`
- `similarity_candidate != semantic_equivalence`

## Límites P0

La API no incluye autenticación/cuentas, escritura/anotación, descarga de artefactos privados, OCR/snippets, pares concretos de similitud, CORS abierto, rate limiting distribuido ni interpretación generativa de resultados. Esas capacidades deben diseñarse explícitamente antes de una exposición pública amplia o comercial con control de acceso.
