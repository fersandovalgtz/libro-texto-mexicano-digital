# LTMD-U1 W7 — diagnóstico de routing de visores no resueltos

Versión: `LTMD_U1_W7_ROUTING_DIAGNOSTICS_0.1`.

Este diagnóstico inspecciona únicamente HTML y JavaScript del mismo origen. No descarga ni conserva imágenes del libro.

- Visores no resueltos inspeccionados: **5**.

| visor | generación | grado | HTML | scripts mismo origen | evidencias de ruta | huecos internos previos |
|---|---:|---:|---:|---:|---:|---:|
| `H2014P5FCA` | 2014 | 5 | 200 | 5 | 40 | 1 |
| `H2018P3FCA` | 2018 | 3 | 200 | 5 | 40 | 113 |
| `H2018P4FCA` | 2018 | 4 | 200 | 5 | 40 | 129 |
| `H2018P5FCA` | 2018 | 5 | 200 | 5 | 40 | 225 |
| `H2018P6FCA` | 2018 | 6 | 200 | 5 | 40 | 209 |

## Interpretación

El archivo JSON conserva hashes y tamaños del HTML/JavaScript consultado junto con fragmentos mínimos que contienen indicadores de routing. Cualquier ruta alternativa deberá derivarse de esa evidencia antes de volver a sondear activos; no se autoriza inferir aliases por coincidencia de año, grado, título o cardinalidad.
