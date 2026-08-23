# LTMD-U1 — registro de excepciones técnicas preservadas

Versión: `LTMD_U1_PRESERVED_EXCEPTIONS_0.1`.

Este registro se deriva de artefactos técnicos de las olas y reúne únicamente excepciones de routing/fuente que permanecen explícitamente sin imputación. No representa pendientes semánticos ni convierte una excepción en evidencia histórica.

- Excepciones técnicas preservadas: **18**.
- Olas con excepciones: **5**.
- Reconciliación contra `remaining_to_effective`: **pendiente del cierre técnico W11**; la ola activa aún no debe contarse como cubierta.

## Por ola

| Ola | Excepciones | seguimiento |
|---|---:|---|
| W2 | 4 | #4 |
| W7 | 5 | #5 |
| W8 | 4 | #9 |
| W10 | 1 | #11 |
| W11 | 4 | #13 y #14 |

## Identidades

| Ola | viewer_key | tipo | estado técnico | issue |
|---|---|---|---|---|
| W2 | `H2018P3DMA` | `routing_unresolved` | `routing_anomaly_all_or_near_all` | #4 |
| W2 | `H2018P4DMA` | `routing_unresolved` | `routing_anomaly_all_or_near_all` | #4 |
| W2 | `H2018P5DMA` | `routing_unresolved` | `routing_anomaly_all_or_near_all` | #4 |
| W2 | `H2018P6DMA` | `routing_unresolved` | `routing_anomaly_all_or_near_all` | #4 |
| W7 | `H2014P5FCA` | `source_retained` | `isolated_internal_unserved` | #5 |
| W7 | `H2018P3FCA` | `source_retained` | `official_route_sample_3of3_404` | #5 |
| W7 | `H2018P4FCA` | `source_retained` | `official_route_sample_3of3_404` | #5 |
| W7 | `H2018P5FCA` | `source_retained` | `official_route_sample_3of3_404` | #5 |
| W7 | `H2018P6FCA` | `source_retained` | `official_route_sample_3of3_404` | #5 |
| W8 | `H2018P3EAA` | `source_retained` | `withheld_source` | #9 |
| W8 | `H2018P4EAA` | `source_retained` | `withheld_source` | #9 |
| W8 | `H2018P5EAA` | `source_retained` | `withheld_source` | #9 |
| W8 | `H2018P6EAA` | `source_retained` | `withheld_source` | #9 |
| W10 | `H2014P1ENA` | `source_retained` | `withheld_internal_unserved` | #11 |
| W11 | `H2014P1EAM` | `source_retained` | `withheld_internal_unserved` | #13 |
| W11 | `H2014P2EAM` | `source_retained` | `withheld_internal_unserved` | #13 |
| W11 | `H2014P3COL` | `source_retained` | `withheld_internal_unserved` | #14 |
| W11 | `H2014P3MOR` | `source_retained` | `withheld_internal_unserved` | #14 |

## Regla
Resolver una fila requiere actualizar primero la evidencia de su ola y recomputar únicamente las capas afectadas. El registro debe regenerarse después; no se elimina una excepción manualmente ni por semejanza con otra edición. `WAITING_HUMAN_REFERENCE` continúa separado de esta deuda técnica.
