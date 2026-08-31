# LTMD Analytics HTTP API 0.1

Versión de transporte: **LTMD Analytics HTTP 0.1**  
Motor de consulta del vertical indígena: `LTMD_ANALYTICS_QUERY_ENGINE_0.2`

## Propósito

Esta capa expone por HTTP el vertical de lenguas indígenas sin convertir el ledger privado en un recurso descargable. La selección preregistrada del estudio 0.2 se conserva. Cuando se configuran los artefactos corpus-wide, la API añade contexto agregado de reutilización/similitud a la selección filtrada y a cada grupo, sin cambiar membresía ni estado epistemológico.

La API es **read-only** y devuelve únicamente agregados, filtros, metadatos de versión, procedencia criptográfica y advertencias epistemológicas.

## Endpoints P0

### `GET /health`

Comprueba que el servicio está activo y que los insumos privados obligatorios están disponibles. Si el contexto corpus-wide se configura, exige que sus dos artefactos estén presentes. No revela rutas de filesystem.

### `GET /v1/meta`

Devuelve versiones, estado científico y vocabularios de filtros disponibles para el vertical de lenguas indígenas. Incluye `reuse_context_configured` para indicar si el runtime dispone del contexto corpus-wide.

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

La respuesta no contiene `page_id`, URL de fuente, OCR, snippets, hashes de página/OCR ni pares concretos de similitud.

Cuando está configurado el contexto corpus-wide, la respuesta puede incluir `reuse_context` en el total filtrado y en cada elemento de `breakdown`. Esos conteos describen reutilización/similitud que toca exactamente ese subconjunto; no reclasifican candidatos y permanecen en `exploratory_signal`.

## Configuración privada

Variables obligatorias para el vertical:

```text
LTMD_INDIGENOUS_LEDGER_PATH=/ruta/privada/ltmd_u1_indigenous_languages_candidate_ledger_0_2.csv
LTMD_GENERATION_SUMMARY_PATH=/ruta/al/ltmd_u1_indigenous_languages_generation_summary_0_2.csv
```

`LTMD_GENERATION_SUMMARY_PATH` es opcional: si no se define, se utiliza la tabla pública versionada del repositorio.

Contexto corpus-wide opcional:

```text
LTMD_UNIVERSAL_INDEX_PATH=/ruta/privada/ltmd_u1_universal_index_0_1.canonical.sqlite
LTMD_REUSE_SIMILARITY_PATH=/ruta/privada/ltmd_u1_reuse_similarity_0_1.sqlite
```

Las dos variables corpus-wide forman un par: deben definirse **ambas o ninguna**. Una configuración parcial degrada el servicio en vez de ignorarse silenciosamente.

Los artefactos privados **no deben**:

- guardarse dentro del repositorio;
- colocarse bajo `public_html`;
- aparecer en logs o respuestas HTTP;
- enviarse al navegador;
- copiarse a artefactos públicos de CI.

## Ejecución local

```bash
python3 -m pip install -r requirements-analytics.txt
export LTMD_INDIGENOUS_LEDGER_PATH=/ruta/privada/ledger.csv
# Opcional, pero emparejado:
export LTMD_UNIVERSAL_INDEX_PATH=/ruta/privada/universal-index.sqlite
export LTMD_REUSE_SIMILARITY_PATH=/ruta/privada/reuse-similarity.sqlite
python3 -m flask --app analytics_api.app run --host 127.0.0.1 --port 8000
```

## cPanel / Phusion Passenger

Esta sección se verificó contra la documentación oficial vigente de cPanel el **30 de agosto de 2026**. cPanel documenta Flask como framework WSGI válido y utiliza Phusion Passenger/Application Manager para registrar aplicaciones Python.

El repositorio incluye **`passenger_wsgi.py` en la raíz de la aplicación**, siguiendo la convención documentada por cPanel.

### Prerrequisitos del hosting

El proveedor/servidor debe disponer de Python 3, `pip`/entorno virtual y Passenger/Application Manager. En cPanel moderno la disponibilidad exacta depende del sistema operativo y de que el proveedor haya habilitado Application Manager y los módulos Passenger correspondientes.

No modificar paquetes de WHM desde esta aplicación si la cuenta no tiene privilegios administrativos. Si Application Manager o Python App no existe en la cuenta, escalar al proveedor de hosting en lugar de improvisar otro runtime dentro de `public_html`.

### Flujo recomendado

1. clonar o actualizar el repositorio en un directorio de aplicación dentro del home de la cuenta y **fuera de `public_html`**;
2. usar ese checkout como application root;
3. crear/seleccionar un entorno Python 3 para la aplicación;
4. instalar dependencias:

```bash
python3 -m pip install -r requirements-analytics.txt
```

5. asegurar que el startup WSGI es `passenger_wsgi.py`;
6. colocar el ledger privado, el Índice Universal y el artefacto de reutilización/similitud fuera del checkout Git y fuera de `public_html`;
7. definir `LTMD_INDIGENOUS_LEDGER_PATH`;
8. opcionalmente definir `LTMD_GENERATION_SUMMARY_PATH`; si se omite se usa la tabla pública del repositorio;
9. para el backend corpus-wide completo, definir conjuntamente `LTMD_UNIVERSAL_INDEX_PATH` y `LTMD_REUSE_SIMILARITY_PATH`;
10. registrar/habilitar la aplicación en cPanel Application Manager o el mecanismo Passenger provisto por el hosting;
11. reiniciar Passenger;
12. verificar `/health`, `/v1/meta` y una consulta acotada con `reuse_context`;
13. sólo después conectar una interfaz web.

### Reinicio Passenger

Cuando el proveedor use la convención estándar documentada por cPanel, se puede solicitar reinicio creando o actualizando el archivo:

```bash
mkdir -p tmp
touch tmp/restart.txt
```

La operación debe ejecutarse dentro de la raíz de la aplicación. Si el hosting usa una interfaz específica de **Setup Python App**, usar su acción de reinicio cuando esté disponible.

### Referencias oficiales consultadas

- cPanel & WHM: *How to Install a Python WSGI Application*;
- cPanel & WHM: *Using Passenger Applications*;
- cPanel & WHM: *Application Manager*.

No se fija todavía un dominio ni un origen CORS. Esa decisión corresponde al despliegue de la interfaz institucional y no debe anticiparse en código.

## Denominadores

Las tasas `pages_per_1000` se calculan únicamente cuando existe un denominador compatible. La versión actual del vertical dispone de denominadores por **generación**. Si una consulta filtra por grado u ola, la API devuelve `pages_per_1000=null` y una advertencia, en lugar de dividir entre un universo que ya no corresponde al filtro.

El contexto de reutilización/similitud no altera ese denominador ni la selección del vertical; sólo agrega conteos sobre las páginas candidatas ya filtradas.

## Estado epistemológico

Toda respuesta utiliza:

```text
result_state = exploratory_signal
human_validation_complete = false
```

`reuse_context.result_state` también es obligatoriamente `exploratory_signal`.

La existencia de una API no cambia el estado científico de la evidencia. `search_hit != historical_claim`, `computational_candidate != semantic_ready` y `similarity_candidate != semantic_equivalence` siguen siendo reglas obligatorias.

## Límites P0

La API 0.1 no incluye:

- autenticación o cuentas;
- escritura o anotación;
- descarga del ledger o de artefactos privados;
- OCR;
- fragmentos fuente;
- pares concretos de reutilización/similitud;
- IA generativa para interpretar resultados;
- CORS abierto;
- rate limiting distribuido.

Autenticación, cuotas y CORS deben introducirse antes de una exposición pública amplia o de funciones comerciales que requieran control de acceso.
