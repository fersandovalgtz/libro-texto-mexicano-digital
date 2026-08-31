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
python3 -m pip install -r requirements-analytics.txt
export LTMD_INDIGENOUS_LEDGER_PATH=/ruta/privada/ledger.csv
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
6. colocar el ledger privado fuera del checkout Git y fuera de `public_html`;
7. definir `LTMD_INDIGENOUS_LEDGER_PATH` en el entorno de la aplicación;
8. opcionalmente definir `LTMD_GENERATION_SUMMARY_PATH`; si se omite se usa la tabla pública del repositorio;
9. registrar/habilitar la aplicación en cPanel Application Manager o el mecanismo Passenger provisto por el hosting;
10. reiniciar Passenger;
11. verificar `/health`, `/v1/meta` y una consulta acotada;
12. sólo después conectar una interfaz web.

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
