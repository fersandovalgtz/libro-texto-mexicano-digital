# LTMD-U1 — tablero maestro de cobertura

Versión: **LTMD_U1_COVERAGE_0.1**  
Universo operativo U1: **542 visores** del snapshot vigente del Catálogo Histórico de CONALITEG.  
Familias normalizadas de título: **191**.

## Estado ejecutivo

- Catálogo censado: **542/542 (100.00%)**.
- Títulos normalizados: **542/542 (100.00%)**.
- Activos completamente resueltos y demostrados: **36/542 (6.64%)**; además **2** visores tienen resolución parcial documentada.
- FRAGSEG directamente materializado: **32/542 (5.90%)**.
- Cobertura FRAGSEG efectiva, contando aliases byte-idénticos ya representados: **36/542 (6.64%)**.
- Visores participantes en relaciones de dependencia ya registradas: **12/542 (2.21%)**.
- Cobertura semántica validada: **0/542 (0.00%)**; SEMB 0.3 continúa bloqueado por referencia humana.

La cobertura efectiva no elimina ni fusiona visores: los aliases conservan su identidad de catálogo y simplemente evitan reprocesar bytes ya demostrados como idénticos.

## Cobertura por dominio operativo

| dominio | visores | % U1 | activos full | FRAGSEG directo | cobertura efectiva | restantes | próxima ola |
|---|---:|---:|---:|---:|---:|---:|---|
| ciencias_naturales | 47 | 8.67% | 36 | 32 | 36 | 11 | U1-W1-ciencias_naturales |
| matematicas | 64 | 11.81% | 0 | 0 | 0 | 64 | U1-W2-matematicas |
| espanol_lengua | 130 | 23.99% | 0 | 0 | 0 | 130 | U1-W3-espanol_lengua |
| historia | 18 | 3.32% | 0 | 0 | 0 | 18 | U1-W4-historia |
| geografia_atlas | 42 | 7.75% | 0 | 0 | 0 | 42 | U1-W5-geografia_atlas |
| civica_etica | 30 | 5.54% | 0 | 0 | 0 | 30 | U1-W6-civica_etica |
| artes | 20 | 3.69% | 0 | 0 | 0 | 20 | U1-W7-artes |
| educacion_fisica | 4 | 0.74% | 0 | 0 | 0 | 4 | U1-W8-educacion_fisica |
| integrados_multiarea | 62 | 11.44% | 0 | 0 | 0 | 62 | U1-W9-integrados_multiarea |
| otros_no_clasificados | 125 | 23.06% | 0 | 0 | 0 | 125 | U1-W10-otros_revision |

## Regla de olas

La taxonomía anterior es **operativa**, derivada sólo de palabras fuertes del título normalizado; no es una ontología curricular ni una clasificación semántica del contenido. Los títulos con señales de más de un dominio pasan a `integrados_multiarea`; los títulos sin señal suficientemente fuerte permanecen en `otros_no_clasificados` para revisión controlada.

El orden de olas prioriza terminar Ciencias Naturales y después escalar a Matemáticas, Español/Lengua, Historia, Geografía/Atlas, Cívica/Ética, Artes, Educación Física, materiales integrados y finalmente títulos que requieren revisión operacional. Un alias verificado se considera cubierto efectivamente sin duplicar OCR/FRAGSEG.

## Límites de lectura

- `cataloged` no significa `asset_resolved`.
- `asset_resolved` no significa `ocr_ready`.
- `fragseg_materialized` no significa `semantic_ready`.
- Una ocurrencia técnica no equivale a una observación histórica independiente.
- Los estados se derivan conservadoramente de artefactos finales ya materializados; trabajo intermedio no terminado no se cuenta como cobertura de etapa.

## Archivos

- `data/catalog/ltmd_u1_coverage.csv` — matriz por visor.
- `data/catalog/ltmd_u1_coverage_summary.csv` — KPIs por etapa.
- `data/catalog/ltmd_u1_domain_summary.csv` — cobertura por dominio operativo.
- `data/catalog/ltmd_u1_wave_queue.csv` — cola ordenada para industrialización.
