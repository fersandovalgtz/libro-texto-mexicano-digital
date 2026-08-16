# LTMD-U1 — tablero maestro de cobertura

Versión: **LTMD_U1_COVERAGE_0.3**  
Universo operativo U1: **542 visores**.  
Familias normalizadas de título: **191**.

## Estado ejecutivo

- Catálogo censado: **542/542 (100.00%)**.
- Títulos normalizados: **542/542 (100.00%)**.
- Activos completamente resueltos: **38/542 (7.01%)**; parciales documentados: **2**.
- Manifiesto directo: **34/542 (6.27%)**.
- OCR directo: **34/542 (6.27%)**.
- PAGESTRUCT directo: **34/542 (6.27%)**.
- FRAGSEG directo: **32/542 (5.90%)**.
- Cobertura FRAGSEG efectiva: **36/542 (6.64%)**.
- Dependencia documental auditada: **12/542 (2.21%)**.
- Cobertura semántica validada: **0/542 (0.00%)**.

Los KPIs se promueven por etapa sólo cuando existe el artefacto final correspondiente. Un visor puede tener activos/OCR/PAGESTRUCT listos sin contar aún como FRAGSEG.

## Cobertura por dominio operativo

| dominio | visores | % U1 | activos full | FRAGSEG directo | cobertura efectiva | restantes | próxima ola |
|---|---:|---:|---:|---:|---:|---:|---|
| ciencias_naturales | 40 | 7.38% | 38 | 32 | 36 | 4 | U1-W1-ciencias_naturales |
| matematicas | 64 | 11.81% | 0 | 0 | 0 | 64 | U1-W2-matematicas |
| espanol_lengua | 130 | 23.99% | 0 | 0 | 0 | 130 | U1-W3-espanol_lengua |
| ciencias_sociales | 14 | 2.58% | 0 | 0 | 0 | 14 | U1-W4-ciencias_sociales |
| historia | 18 | 3.32% | 0 | 0 | 0 | 18 | U1-W5-historia |
| geografia_atlas | 42 | 7.75% | 0 | 0 | 0 | 42 | U1-W6-geografia_atlas |
| civica_etica | 30 | 5.54% | 0 | 0 | 0 | 30 | U1-W7-civica_etica |
| artes | 20 | 3.69% | 0 | 0 | 0 | 20 | U1-W8-artes |
| educacion_fisica | 4 | 0.74% | 0 | 0 | 0 | 4 | U1-W9-educacion_fisica |
| integrados_multiarea | 69 | 12.73% | 0 | 0 | 0 | 69 | U1-W10-integrados_multiarea |
| otros_no_clasificados | 111 | 20.48% | 0 | 0 | 0 | 111 | U1-W11-otros_revision |

## Límites de lectura

- `cataloged` no significa `asset_resolved`.
- `asset_resolved` no significa `ocr_ready`.
- `fragseg_materialized` no significa `semantic_ready`.
- Cobertura efectiva por alias conserva identidad documental y evita reprocesar bytes demostrados como idénticos.
- La taxonomía de dominios es logística, no una ontología curricular.

## Archivos

- `data/catalog/ltmd_u1_coverage.csv`
- `data/catalog/ltmd_u1_coverage_summary.csv`
- `data/catalog/ltmd_u1_domain_summary.csv`
- `data/catalog/ltmd_u1_wave_queue.csv`
