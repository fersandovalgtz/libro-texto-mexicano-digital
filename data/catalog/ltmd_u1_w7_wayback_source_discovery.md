# LTMD-U1 W7 — descubrimiento archivístico de fuentes retenidas

Versión: `LTMD_U1_W7_WAYBACK_SOURCE_DISCOVERY_0.2`.

Observado UTC: `2026-08-17T03:04:49.908056+00:00`.

Contrato operativo: 5 consultas concurrentes; timeout 20s; 2 intentos por objetivo.

Se consulta Wayback CDX exclusivamente con URIs institucionales exactos o prefijos exactos ya demostrados por el contrato de routing. Una captura archivada es evidencia de disponibilidad histórica del URI, no prueba automática de identidad bibliográfica; una consulta sin capturas tampoco prueba inexistencia del recurso.

## Resumen

| objetivo | clase | estado CDX | capturas/URLs archivadas | primera | última |
|---|---|---|---:|---|---|
| `H2014P5FCA_page104` | `exact_missing_asset` | `cdx_network_error:HTTP 503` | 0 | `` | `` |
| `H2014P5FCA_viewer` | `exact_viewer` | `cdx_network_error:HTTP 503` | 0 | `` | `` |
| `H2018P3FCA_asset_subtree` | `exact_asset_subtree` | `cdx_network_error:URLError: <urlopen error timed out>` | 0 | `` | `` |
| `H2018P3FCA_viewer` | `exact_viewer` | `cdx_network_error:HTTP 503` | 0 | `` | `` |
| `H2018P4FCA_asset_subtree` | `exact_asset_subtree` | `cdx_network_error:URLError: <urlopen error timed out>` | 0 | `` | `` |
| `H2018P4FCA_viewer` | `exact_viewer` | `cdx_network_error:HTTP 503` | 0 | `` | `` |
| `H2018P5FCA_asset_subtree` | `exact_asset_subtree` | `cdx_network_error:URLError: <urlopen error timed out>` | 0 | `` | `` |
| `H2018P5FCA_viewer` | `exact_viewer` | `cdx_network_error:HTTP 503` | 0 | `` | `` |
| `H2018P6FCA_asset_subtree` | `exact_asset_subtree` | `cdx_network_error:HTTP 503` | 0 | `` | `` |
| `H2018P6FCA_viewer` | `exact_viewer` | `cdx_network_error:HTTP 503` | 0 | `` | `` |

## Objetivo prioritario H2014P5FCA

La página faltante exacta `c/H2014P5FCA/104.jpg` produjo **0** registro(s) CDX con estado `cdx_network_error:HTTP 503` en este corte.

Si existen capturas, el siguiente paso es recuperar sus bytes archivados y comprobar tipo, tamaño, SHA-256 y correspondencia posicional antes de cualquier admisión. Si no existen capturas, la retención permanece sin imputación.

## Límite epistemológico

Este proceso no busca candidatos 2019 por similitud. Los cuatro `H2018...` sólo se investigan por su visor institucional exacto y por el prefijo de activos que el código oficial del visor ya demostró. Ningún resultado de CDX modifica por sí solo `ocr_source_admitted`.
