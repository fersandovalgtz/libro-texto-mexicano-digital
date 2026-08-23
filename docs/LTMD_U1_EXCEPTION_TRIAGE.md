# LTMD-U1 — triage de excepciones técnicas preservadas

Versión: `LTMD_U1_EXCEPTION_TRIAGE_0.1`.

El triage agrupa las excepciones por patrón técnico de recuperación. No altera cobertura, no crea aliases y no establece prioridad histórica o semántica.

- Excepciones clasificadas: **18/18**.
- Huecos internos aislados: **6**.
- Routing/subárbol de fuente ausente: **12**.

## Estrategias

### Hueco interno aislado
Buscar primero la posición institucional exacta y sus capturas archivadas; después, si existe otra representación oficial completa, demostrar correspondencia posicional antes de admitir el cuerpo faltante. Una página vecina o de otro estado/edición no es sustituto.

### Routing o subárbol de fuente ausente
Resolver la configuración/ruta institucional como problema de conjunto: `ag_clave`, código del visor, mappings archivados o una secuencia alternativa explícitamente relacionada. La igualdad de título, grado, cardinalidad o generación próxima no crea un alias.

## Casos

| clase | ola | viewer | estado | issue |
|---|---|---|---|---|
| `isolated_internal_hole` | W7 | `H2014P5FCA` | `isolated_internal_unserved` | #5 |
| `isolated_internal_hole` | W10 | `H2014P1ENA` | `withheld_internal_unserved` | #11 |
| `isolated_internal_hole` | W11 | `H2014P1EAM` | `withheld_internal_unserved` | #13 |
| `isolated_internal_hole` | W11 | `H2014P2EAM` | `withheld_internal_unserved` | #13 |
| `isolated_internal_hole` | W11 | `H2014P3COL` | `withheld_internal_unserved` | #14 |
| `isolated_internal_hole` | W11 | `H2014P3MOR` | `withheld_internal_unserved` | #14 |
| `routing_or_source_subtree_absent` | W2 | `H2018P3DMA` | `routing_anomaly_all_or_near_all` | #4 |
| `routing_or_source_subtree_absent` | W2 | `H2018P4DMA` | `routing_anomaly_all_or_near_all` | #4 |
| `routing_or_source_subtree_absent` | W2 | `H2018P5DMA` | `routing_anomaly_all_or_near_all` | #4 |
| `routing_or_source_subtree_absent` | W2 | `H2018P6DMA` | `routing_anomaly_all_or_near_all` | #4 |
| `routing_or_source_subtree_absent` | W7 | `H2018P3FCA` | `official_route_sample_3of3_404` | #5 |
| `routing_or_source_subtree_absent` | W7 | `H2018P4FCA` | `official_route_sample_3of3_404` | #5 |
| `routing_or_source_subtree_absent` | W7 | `H2018P5FCA` | `official_route_sample_3of3_404` | #5 |
| `routing_or_source_subtree_absent` | W7 | `H2018P6FCA` | `official_route_sample_3of3_404` | #5 |
| `routing_or_source_subtree_absent` | W8 | `H2018P3EAA` | `withheld_source` | #9 |
| `routing_or_source_subtree_absent` | W8 | `H2018P4EAA` | `withheld_source` | #9 |
| `routing_or_source_subtree_absent` | W8 | `H2018P5EAA` | `withheld_source` | #9 |
| `routing_or_source_subtree_absent` | W8 | `H2018P6EAA` | `withheld_source` | #9 |

## Regla de cierre
Una excepción sólo sale de este triage después de que el artefacto técnico autoritativo de su ola cambie y el registro U1 se regenere. La clasificación de recuperación por sí sola no modifica `effective_technical_identities`.
