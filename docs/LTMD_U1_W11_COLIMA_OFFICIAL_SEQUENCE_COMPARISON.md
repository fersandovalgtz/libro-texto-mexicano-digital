# LTMD-U1 W11 — comparación criptográfica Colima histórico ↔ representaciones oficiales

Versión: `LTMD_U1_W11_COLIMA_OFFICIAL_SEQUENCES_0.1`.

- Visor histórico: `H2014P3COL`.
- Código oficial: `P3COL`.
- Cardinalidades oficiales observadas en `output.json`: **178, 179**.
- Posiciones históricas servidas: **160**.
- Hueco histórico: página **130**, índice **130**, archivo `130.jpg`.
- Imágenes persistidas: **0**.

## Candidatos

| candidato | base oficial | JPEG servidos | SHA idénticos | errores transporte | hueco válido | estado fuerte |
|---|---|---:|---:|---:|---|---|
| `root` | `https://libros.conaliteg.gob.mx/c/P3COL/` | 0/160 | 0/160 | 0 | no | no |
| `2022` | `https://libros.conaliteg.gob.mx/2022/c/P3COL/` | 160/160 | 0/160 | 0 | sí | no |
| `2021` | `https://libros.conaliteg.gob.mx/2021/c/P3COL/` | 160/160 | 0/160 | 0 | sí | no |
| `20` | `https://libros.conaliteg.gob.mx/20/c/P3COL/` | 160/160 | 0/160 | 0 | sí | no |

**Estado: `not_recoverable_by_exact_sequence`.**

## Regla

Una representación sólo puede proponerse para recuperación si las 160 posiciones históricas observables son JPEG válidos y byte-idénticos en el mismo basename/posición, sin errores de transporte, y el hueco exacto existe como JPEG válido. La cardinalidad, la clave corta o el título nunca bastan. Incluso un candidato fuerte requiere una actualización explícita de procedencia y de la compuerta W11; no se sustituye silenciosamente la fuente histórica.
