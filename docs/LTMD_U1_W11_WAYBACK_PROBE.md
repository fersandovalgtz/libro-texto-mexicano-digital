# LTMD-U1 W11 — sondeo archivístico de URLs fuente retenidas

Versión: `LTMD_U1_W11_WAYBACK_PROBE_0.2`.

- Huecos consultados: **5/5**.
- Consultas exactas/transportes ejecutadas: **10/10**.
- Huecos con ≥1 captura CDX 200: **0/5**.
- Registros de captura únicos por digest/consulta: **0**.
- Consultas concluyentes sin captura: **10**.
- Consultas fallidas tras reintentos: **0**.

## Resultado por posición

| viewer | página | índice | capturas | primera | última | roles |
|---|---:|---:|---:|---|---|---|
| `H2014P1EAM` | 41 | 41 | 0 | — | — | — |
| `H2014P2EAM` | 13 | 13 | 0 | — | — | — |
| `H2014P2EAM` | 17 | 17 | 0 | — | — | — |
| `H2014P3COL` | 130 | 130 | 0 | — | — | — |
| `H2014P3MOR` | 15 | 15 | 0 | — | — | — |

## Regla

Una captura CDX sólo demuestra que Internet Archive indexó una respuesta 200 para la misma ruta institucional (o su variante de transporte HTTP). No demuestra todavía que el cuerpo archivado sea un JPEG válido ni autoriza su incorporación. Cualquier candidato debe verificarse temporalmente por firma JPEG, tamaño, SHA-256 y digest CDX, conservando timestamp, URL original y procedencia archivística. No se consultan páginas de otros libros como sustitutos.

El log de consultas distingue `success_no_capture` de `error`: un timeout o fallo del servicio no se interpreta como ausencia de captura. La ausencia concluyente en este sondeo sigue siendo un resultado negativo acotado, no prueba de inexistencia de otras copias.
