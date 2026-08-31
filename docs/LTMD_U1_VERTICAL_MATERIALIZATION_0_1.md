# LTMD-U1 — materialización de verticales exploratorios 0.1

## Estado

Versión: `LTMD_U1_VERTICAL_MATERIALIZATION_0.1`  
Registro preregistrado: `LTMD_U1_VERTICAL_REGISTRY_0.1`  
Estado epistemológico: `exploratory_signal`  
Validación humana completa: **no**.

Esta materialización ejecuta, sin modificar después de observar resultados, las ocho especificaciones temáticas fusionadas previamente en el registro 0.1. Los resultados son señales léxicas/OCR derivadas de FTS5 y no equivalen a clasificaciones semánticas ni a afirmaciones históricas validadas.

## Universo

- 86,549 páginas del Índice Universal LTMD-U1 0.1.
- 492 objetos canónicos.
- Desgloses exactos por 11 generaciones, 6 grados y 11 olas operacionales para cada vertical.
- Contexto agregado de reutilización/similitud corpus-wide para cada vertical.

## Resultados globales

| Vertical | Páginas candidatas | Libros | Páginas por 1,000 | Con señal de reuso/similitud |
|---|---:|---:|---:|---:|
| Ciudadanía, democracia y derechos | 907 | 193 | 10.48 | 198 |
| Mujeres, género y familia | 6,569 | 475 | 75.90 | 1,748 |
| Medio ambiente y naturaleza | 2,526 | 400 | 29.19 | 541 |
| Migración y movilidad | 483 | 134 | 5.58 | 51 |
| Trabajo y economía | 8,559 | 473 | 98.89 | 2,318 |
| Discapacidad e inclusión | 150 | 54 | 1.73 | 48 |
| Ciencia y tecnología | 1,872 | 309 | 21.63 | 399 |
| Nación, identidad y México | 15,974 | 492 | 184.57 | 2,485 |

La amplitud de algunos verticales —especialmente `nation_identity_mexico`, `work_economy` y `gender_women_family`— es parte del resultado del protocolo preregistrado y **no** se corrige retrospectivamente. Cualquier refinamiento futuro deberá publicarse como una nueva versión del registro y de su materialización.

## Procedencia

- Registro SHA-256: `9a4f3b57c993b4ef86a821508bf050e3efd812f682b483862550dc977423d1c8`.
- Índice Universal SHA-256: `aec55cc7dd83c2e1e22d26e3baf8f7ca2e35e32898827ec84e6222edd4bcf7a2`.
- Reutilización/similitud SHA-256: `4c180f37b287f4c5cc81155aabd8a97e5feb6f40668c3baa296c4733f8063301`.
- Materialización integral reproducida: 120,354 bytes; SHA-256 `e2faab966faced48327634c4acd40a867b76add29612538736b91db8d3afb0ad`.

GitHub conserva un registro público agregado del resultado integral y su hash. El constructor puede regenerar el detalle completo a partir de los insumos privados canónicos.

## Privacidad y no regresión

La superficie pública no emite `page_id`, identificadores de objetos, pares concretos, OCR, snippets ni hashes de páginas fuente. `search_hit != historical_claim`, `computational_candidate != semantic_ready` y `zero_hits != demonstrated_absence` permanecen como reglas obligatorias. La materialización no crea aliases y el contexto de similitud no establece identidad documental ni equivalencia semántica.
