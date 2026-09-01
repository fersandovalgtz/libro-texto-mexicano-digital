# LTMD-U1 W7 — vecinos exactos de H2014P5FCA

Versión: `LTMD_U1_W7_H2014P5_EXACT_NEIGHBORS_0.1`.

Este análisis compara SHA-256 de páginas ya auditadas en la misma posición lógica. No descarga activos, no imputa la página 104 y no cambia el gate de admisibilidad.

## Comparación

| candidato | generación catálogo | páginas candidato | solapamiento posicional | exactas | distintas | tasa exacta | tiene pág. 104 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `H2008P5CI278` | 2008 | 86 | 86 | 0 | 86 | 0.000000 | 0 |
| `H2011P5CI326` | 2011 | 129 | 128 | 0 | 128 | 0.000000 | 1 |
| `H2018P5FCA` | 2018 | 225 | 224 | 0 | 224 | 0.000000 | 1 |
| `H2019P5FCA` | 2019 | 225 | 224 | 0 | 224 | 0.000000 | 1 |

## Mejor vecino observado

- Candidato: `H2008P5CI278`.
- Coincidencias SHA-256 en posiciones comparables: **0/86**.
- Tasa exacta posicional: **0.000000**.
- El candidato no contiene una fuente servida en la página lógica **104**.

## Regla de interpretación

Una tasa 1.0 sobre las páginas observables sería evidencia criptográfica de equivalencia posicional para esas páginas, pero no observa directamente la página faltante y por sí sola no convierte el libro completo en byte-idéntico. Cualquier uso de la página 104 de otro visor debe registrarse como reconstrucción derivada con procedencia explícita, salvo que evidencia archivística o documental independiente cierre la identidad del objeto.
