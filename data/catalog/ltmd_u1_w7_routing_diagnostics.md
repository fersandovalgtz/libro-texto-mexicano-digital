# LTMD-U1 W7 — diagnóstico de routing de visores no resueltos

Versión: `LTMD_U1_W7_ROUTING_DIAGNOSTICS_0.1`.

Este diagnóstico inspecciona únicamente HTML y JavaScript del mismo origen. No descarga ni conserva imágenes del libro.

- Visores no resueltos inspeccionados: **1**.

| visor | generación | grado | HTML | scripts mismo origen | evidencias de ruta | huecos internos previos |
|---|---:|---:|---:|---:|---:|---:|
| `H2014P5FCA` | 2014 | 5 | 200 | 5 | 40 | 1 |

## Interpretación

El archivo JSON conserva hashes y tamaños del HTML/JavaScript consultado junto con fragmentos mínimos que contienen indicadores de routing. Cualquier ruta alternativa deberá derivarse de esa evidencia antes de volver a sondear activos; no se autoriza inferir aliases por coincidencia de año, grado, título o cardinalidad.
