# LTMD-U1 — integridad de la evidencia pública derivada

Versión: `LTMD_U1_EVIDENCE_INTEGRITY_0.1`.

Este control produce un inventario determinista y direccionado por contenido de la capa pública de evidencia LTMD-U1. Cada archivo incluido queda identificado por ruta, clase de artefacto, tamaño en bytes y SHA-256.

## Alcance

- Artefactos públicos verificados: **999**.
- Bytes públicos cubiertos: **397201957**.
- Algoritmo: **SHA-256**.
- Activos fuente originales descargados o persistidos por este control: **0**.
- OCR completo persistido por este control: **0**.
- El propio ledger y este informe se excluyen para evitar autorreferencia criptográfica.

## Cobertura por clase

| clase | archivos |
|---|---:|
| `automation` | 211 |
| `derived_data` | 413 |
| `evidence_report` | 102 |
| `landing_page` | 2 |
| `scholarly_metadata` | 2 |
| `scientific_code` | 269 |

## Regla de interpretación

Un SHA-256 distinto significa que el artefacto público cambió y el ledger debe regenerarse. Este control acredita integridad de los archivos derivados publicados en el repositorio; no autentica ni redistribuye los libros, páginas, imágenes u OCR fuente de CONALITEG/SEP, y no sustituye las verificaciones de procedencia y admisibilidad de cada ola.

Archivo canónico del ledger: `data/catalog/ltmd_u1_evidence_integrity.csv`.
