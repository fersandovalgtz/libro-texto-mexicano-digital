# LTMD-U1 W7 — contrato observado del routing del visor

Versión: `LTMD_U1_W7_VIEWER_ROUTE_CONTRACT_0.1`.

Esta capa observa `claves.json` y `x.js` del visor histórico de CONALITEG. No solicita ni conserva imágenes de los libros.

- Visores W7 no resueltos: **5**.
- SHA-256 de `claves.json`: `7fb55e583ee5190fd2153d95764426114f86946ea93d8545c07d5f03d7674037`.
- SHA-256 de `x.js`: `209526b121455c45b743c43f7a269126c2d510cbb77bd6945d5798703ec2cdc3`.
- Fragmentos técnicos de routing retenidos: **5**.

## Entradas observadas en `claves.json`

| visor | generación | grado | campos observados | entrada |
|---|---:|---:|---|---|
| `H2014P5FCA` | 2014 | 5 | `ag_clave, ag_pages` | `{"ag_clave": "H2014P5FCA", "ag_pages": 225}` |
| `H2018P3FCA` | 2018 | 3 | `ag_clave, ag_pages` | `{"ag_clave": "H2018P3FCA", "ag_pages": 114}` |
| `H2018P4FCA` | 2018 | 4 | `ag_clave, ag_pages` | `{"ag_clave": "H2018P4FCA", "ag_pages": 130}` |
| `H2018P5FCA` | 2018 | 5 | `ag_clave, ag_pages` | `{"ag_clave": "H2018P5FCA", "ag_pages": 226}` |
| `H2018P6FCA` | 2018 | 6 | `ag_clave, ag_pages` | `{"ag_clave": "H2018P6FCA", "ag_pages": 210}` |

## Regla epistemológica

Una ruta alternativa para activos sólo puede incorporarse al pipeline si puede reconstruirse de manera determinista a partir de estas fuentes observadas. Coincidencias por año, grado, título o número de páginas no constituyen evidencia suficiente.

El JSON asociado conserva los fragmentos mínimos de JavaScript relevantes para auditar esa reconstrucción.
