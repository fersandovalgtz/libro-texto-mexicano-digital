# LTMD-U1 W7 — conformidad de ruta 2018 frente a control 2019

Versión: `LTMD_U1_W7_2018_ROUTE_CONFORMANCE_0.1`.
Contrato de ruta aplicado: `LTMD_U1_W7_IMAGE_ROUTE_CONTRACT_0.2`.

Este probe usa exclusivamente la fórmula observada en el código oficial del visor. No prueba aliases, no sustituye claves y no persiste imágenes.

- Visores 2018: **4**; posiciones por visor: **3**; solicitudes: **12**.
- Controles 2019: **4**; posiciones por visor: **3**; solicitudes: **12**.
- 2018 HTTP 200 de imagen: **0/12**.
- 2018 HTTP 404: **12/12**.
- 2019 HTTP 200 de imagen: **12/12**.
- 2019 HTTP 404: **0/12**.

## Por visor

| generación | grado | visor | páginas lógicas | estados HTTP |
|---:|---:|---|---|---|
| 2018 | 3 | `H2018P3FCA` | 1, 2, 57 | 404, 404, 404 |
| 2018 | 4 | `H2018P4FCA` | 1, 2, 65 | 404, 404, 404 |
| 2018 | 5 | `H2018P5FCA` | 1, 2, 113 | 404, 404, 404 |
| 2018 | 6 | `H2018P6FCA` | 1, 2, 105 | 404, 404, 404 |
| 2019 | 3 | `H2019P3FCA` | 1, 2, 57 | 200, 200, 200 |
| 2019 | 4 | `H2019P4FCA` | 1, 2, 65 | 200, 200, 200 |
| 2019 | 5 | `H2019P5FCA` | 1, 2, 113 | 200, 200, 200 |
| 2019 | 6 | `H2019P6FCA` | 1, 2, 105 | 200, 200, 200 |

## Interpretación

El contraste es consistente con una ruptura o ausencia del subárbol de activos 2018 en la ruta que el propio visor oficial construye, mientras que la misma lógica funciona en los controles 2019. Esto descarta, para este muestreo, un error general de la fórmula de routing implementada por LTMD. No demuestra dónde fueron reubicados los activos 2018 ni autoriza usar 2019 como alias.
