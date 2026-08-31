# LTMD Analytics HTTP API 0.1

Versión de transporte: **LTMD Analytics HTTP 0.1**  
Motor de consulta: `LTMD_ANALYTICS_QUERY_ENGINE_0.1`

## Propósito

Esta capa expone por HTTP el motor exacto de consulta de LTMD Analytics sin convertir el ledger privado en un recurso descargable. La API es **read-only** y devuelve únicamente agregados, filtros, metadatos de versión, procedencia criptográfica y advertencias epistemológicas.

## Endpoints P0

### `GET /health`

Comprueba que el servicio está activo y que los insumos privados están disponibles. No revela rutas de filesystem.

### `GET /v1/meta`

Devuelve versiones, estado científico y vocabularios de filtros disponibles para el vertical de lenguas indígenas.

### `GET /v1/indigenous/query`

Parámetros repetibles:

- `generation`
- `grade_code`
- `wave`
- `language_group`
- `explicit_term`

Parámetros simples:

- `q`: etiqueta descriptiva de consulta;
- `group_by`: `generation | grade_code | wave | language_group | explicit_term`.

Ejemplo local:

```bash
curl --get 'http://127.0.0.1:8000/v1/indigenous/query' \
  --data-urlencode 'q=rarámuri por generación' \
  --data-urlencode 'language_group=Tarahumara / rarámuri' \
  --data-urlencode 'group_by=generation'
```

La respuesta no contiene `page_id`, URL de fuente, OCR, snippets ni hashes de página/OCR.

## Configuración privada

Variables de entorno:

```text
LTMD_INDIGENOUS_LEDGER_PATH=/ruta/privada/ltmd_u1_indigenous_languages_candidate_ledger_0_2.csv
LTMD_GENERATION_SUMMARY_PATH=/ruta/al/ltmd_u1_indigenous_languages_generation_summary_0_2.csv
```

`LTMD_GENERATION_SUMMARY_PATH` es opcional: si no se define, se utiliza la tabla pública versionada del repositorio.

El ledger privado **no debe**:

- guardarse dentro del repositorio;
- colocarse bajo `public_html`;
- aparecer en logs o respuestas HTTP;
- enviarse al navegador;
- copiarse a artefactos públicos de CI.

## Ejecución local

```bash
python -m pip install -r requirements-analytics.txt
export LTMD_INDIGENOUS_LEDGER_PATH=/ruta/privada/ledger.csv
flask --app analytics_api.app run --host 127.0.0.1 --port 8000
```

## cPanel / Passenger

El repositorio incluye `analytics_api/passenger_wsgi.py` como punto de entrada WSGI.

Configuración conceptual:

1. crear una aplicación Python separada para LTMD Analytics;
2. mantener su directorio de aplicación fuera de `public_html` cuando sea posible;
3. instalar `requirements-analytics.txt` en el entorno virtual de esa aplicación;
4. configurar el startup WSGI con `analytics_api/passenger_wsgi.py`;
5. definir `LTMD_INDIGENOUS_LEDGER_PATH` apuntando al ledger privado fuera del árbol público;
6. reiniciar la aplicación;
7. verificar `/health`, `/v1/meta` y una consulta acotada;
8. sólo después conectar una interfaz web.

No se fija todavía un dominio ni un origen CORS. Esa decisión corresponde al despliegue de la interfaz institucional y no debe anticiparse en código.

## Denominadores

Las tasas `pages_per_1000` se calculan únicamente cuando existe un denominador compatible. La versión 0.1 dispone de denominadores por **generación**. Si una consulta filtra por grado u ola, la API devuelve `pages_per_1000=null` y una advertencia, en lugar de dividir entre un universo que ya no corresponde al filtro.

## Estado epistemológico

Toda respuesta de consulta 0.1 utiliza:

```text
result_state = exploratory_signal
human_validation_complete = false
```

La existencia de una API no cambia el estado científico de la evidencia. `search_hit != historical_claim` y `computational_candidate != semantic_ready` siguen siendo reglas obligatorias.

## Límites P0

La API 0.1 no incluye:

- autenticación o cuentas;
- escritura o anotación;
- descarga del ledger;
- OCR;
- fragmentos fuente;
- IA generativa para interpretar resultados;
- CORS abierto;
- rate limiting distribuido.

Autenticación, cuotas y CORS deben introducirse antes de una exposición pública amplia o de funciones comerciales que requieran control de acceso.
