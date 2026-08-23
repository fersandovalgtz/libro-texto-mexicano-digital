# LTMD-U1 W11 — verificación de cuerpos archivados

Versión: `LTMD_U1_W11_WAYBACK_VERIFY_0.1`.

- Capturas candidatas recibidas: **0**.
- Cuerpos archivados verificados: **0**.
- Imágenes fuente persistidas: **0**.

## Estado por hueco

| viewer | página | capturas | verificadas | SHA-256 verificados distintos | estado |
|---|---:|---:|---:|---:|---|
| `H2014P1EAM` | 41 | 0 | 0 | 0 | `no_verified_capture` |
| `H2014P2EAM` | 13 | 0 | 0 | 0 | `no_verified_capture` |
| `H2014P2EAM` | 17 | 0 | 0 | 0 | `no_verified_capture` |
| `H2014P3COL` | 130 | 0 | 0 | 0 | `no_verified_capture` |
| `H2014P3MOR` | 15 | 0 | 0 | 0 | `no_verified_capture` |

- Huecos con exactamente un cuerpo archivado verificable por hash: **0/5**.

## Regla

Este resultado todavía no altera la admisibilidad W11. `single_verified_archived_body` significa que todas las capturas verificadas de esa posición convergen en un único SHA-256 y que el cuerpo recuperado es JPEG con digest CDX coherente; la incorporación requiere una revisión de procedencia que preserve URL institucional original, timestamp de captura y URL de replay. `archived_version_ambiguity` bloquea la recuperación automática.

Las imágenes archivadas se usan de forma temporal para verificación y no se incorporan a Git.
