# Changelog

Todos los cambios notables de **Libro de Texto Mexicano Digital (LTMD)** se documentan aquí. El proyecto permanece en fase pre-1.0; las releases candidatas pueden cambiar antes de una primera liberación estable.

## [Unreleased]

Sin cambios acumulados después de la preparación de `v0.2.0-rc.1`.

## [0.2.0-rc.1] — 2026-08-31

Segunda candidata científica de LTMD. Este corte consolida la expansión corpus-wide de LTMD-U1, la Full-Text Research Layer, LTMD Analytics 0.1 y el endurecimiento de gobernanza del repositorio sin promover validaciones humanas o jurídicas que todavía no existen.

### Calidad del repositorio y arquitectura pública

- Definida explícitamente la frontera **LTMD Open / LTMD Research / LTMD Services**, manteniendo este repositorio como superficie canónica abierta de código, metodología, contratos, metadatos, hashes y derivados publicables.
- Añadidos `SUPPORT.md`, plantilla científica de pull request y formularios diferenciados para errores técnicos, datos/metodología y propuestas de capacidad.
- Añadido Dependabot para GitHub Actions y dependencias Python con cadencia semanal.
- Endurecido `scripts/audit_repository_quality.py` y `repository-quality.yml` como regression gate: cualquier workflow nuevo o modificado que introduzca o conserve `contents: write` o `git push` falla CI; la deuda heredada queda inventariada y separada para migración progresiva en #133.
- Elevado `SCIENTIFIC_REPOSITORY_STANDARD.md` con controles explícitos de seguridad de automatización, gobernanza de `main`, triage, límites de producto y mantenimiento progresivo.
- Actualizada la autoevaluación FAIR/FAIR4RS para reflejar la superficie comunitaria y registrar como brechas externas la protección efectiva de `main` y la auditoría gradual de permisos de workflows heredados.

### Expansión LTMD-U1

- Cerrado el censo operativo en **542/542 identidades** del universo U1.
- Elevada la cobertura técnica efectiva a **524/542 (96.68%)**.
- Cerrados **492/542 (90.77%)** objetos canónicos de procesamiento.
- Completadas técnicamente W1, W3, W4, W5, W6 y W9.
- Cerradas las cohortes fuente-admitidas de W7, W8, W10 y W11, preservando sus retenciones sin imputación.
- W2 permanece con cierre parcial y cuatro excepciones de routing explícitas.
- La validación semántica humana permanece en **0/542** y `WAITING_HUMAN_REFERENCE` sigue vigente.

### Procesamiento técnico

- Extendidos OCR temporal, PAGESTRUCT, FRAGSEG y análisis de reutilización textual exacta a las cohortes técnicamente admisibles de U1.
- Preservadas identidades históricas separadas de objetos canónicos cuando existen aliases o relaciones de reutilización demostradas.
- Mantenida la política de no promover coincidencias nominales, visuales, OCR o textuales a identidad documental sin evidencia suficiente.

### Full-Text Research Layer (FTRL)

- Consolidada `LTMD_FTRL_0.1`, una capa local y reconstruible de OCR completo por página orientada a concordancias históricas reproducibles.
- Añadido `scripts/build_page_ocr_corpus.py` con recuperación de activos fuente-admitidos, verificación SHA-256, Tesseract TXT+TSV, hashes de OCR y normalización conservadora; la ejecución admite reanudación segura.
- Añadidos `scripts/build_search_index.py`, `scripts/query_ocr_corpus.py` y `scripts/validate_ocr_corpus.py` para construir SQLite FTS5, consultar por texto/filtros y verificar integridad de corpus e índice.
- Añadido `schemas/ltmd_page_ocr.schema.json` como contrato de registro canónico por página.
- Documentadas arquitectura, procedencia y metodología en `docs/LTMD_FULL_TEXT_RESEARCH_LAYER.md`, `docs/LTMD_OCR_PROVENANCE.md` y `docs/LTMD_SEARCH_METHODOLOGY.md`.
- Fijadas las reglas `ocr_available != text_verified`, `search_hit != historical_claim` y `zero_hits != demonstrated_absence`.
- Los OCR íntegros, assets reconstruidos y SQLite permanecen bajo `local/` y no se versionan por defecto.

### LTMD Analytics 0.1

- Incorporada la capa LTMD Analytics 0.1 y su contrato técnico como parte de la arquitectura actual del proyecto.
- Incorporada una suite de pruebas independiente que forma parte de los gates de la candidata 0.2.0-rc.1.
- La existencia de una superficie analítica no cambia los estados epistemológicos de los datos: resultados computacionales, búsquedas y candidatos continúan separados de validación humana e interpretación histórica.

### Excepciones y trazabilidad

- Consolidado `data/catalog/ltmd_u1_retained_source_register.csv` con las **18 identidades** que explican exactamente el residual técnico de U1.
- Añadido `docs/LTMD_U1_RETAINED_SOURCE_REGISTER.md` con clases de retención, evidencia aceptable y reglas de cierre.
- Añadido `scripts/validate_u1_retained_source_register.py` y CI para exigir sincronía entre el registro residual y `data/catalog/ltmd_u1_coverage.md`.
- Las cuatro excepciones W2 de Matemáticas y las cinco fuentes W7 retenidas permanecen explícitas; no se imputan aliases por similitud.

### Integridad y documentación científica

- Añadido un ledger direccionado por contenido de la evidencia pública U1 con ruta, clase de artefacto, tamaño y SHA-256.
- Automatizada la regeneración del ledger de integridad cuando cambia la superficie pública relevante.
- Publicado `docs/LTMD_U1_MASTER_PLAN_0_3.md`, que reemplaza operativamente la línea base obsoleta del plan 0.2 sin reescribir el documento histórico.
- Sincronizadas las cifras públicas principales del estado U1 en documentación de cobertura y superficie del repositorio.
- Separadas como validaciones humanas independientes la exactitud OCR CER/WER (#123), el libro de códigos 0.1 (#124) y la inspección visual de 457 páginas `explicit_general` del estudio de lenguas indígenas (#95).

### Contexto histórico, derechos y cohorte contemporánea

- Añadido `docs/LTMD_HISTORICAL_CONTEXT_AND_RIGHTS.md` para documentar el valor de los Libros de Texto Gratuitos como fuente para la historia de la educación mexicana, con enlaces oficiales a CONALITEG, catálogo histórico y fuentes institucionales de contexto.
- Explicitado que LTMD **no posee ni reclama derechos de autor sobre los libros fuente** y que “gratuito” no equivale a dominio público o licencia abierta.
- Fijada la regla `publicly_accessible != openly_licensed`; el acceso mediante un visor institucional no se trata como autorización suficiente para republicar PDF, JPEG, páginas, ilustraciones u OCR completo.
- Reforzado `DATA_LICENSE.md` para separar con precisión software Apache-2.0, derivados originales CC BY 4.0 y materiales fuente de SEP/CONALITEG o terceros.
- Incorporado `data/catalog/conaliteg_primaria_2026_2027_inventory.csv` como **capa de catálogo**, con 42 entradas por grado y 39 visores únicos del ciclo oficial 2026–2027, sin redistribuir las obras fuente.
- Definida para la cohorte contemporánea una identidad de procedencia compuesta por fuente + ciclo + nivel + `viewer_key`, evitando asumir que la `clave` es globalmente única entre ciclos.
- Abierto #135 para gobernar la admisión técnica de la cohorte 2026–2027 sin confundir `cataloged`, `source_admitted`, `ocr_available`, `text_verified` y `semantic_ready`.

### Derechos, gobernanza y límites vigentes

- Las **18 retenciones** no se sustituyen por inferencia; requieren evidencia institucional, archivística o criptográfica suficiente, o deben cerrarse posteriormente como excepciones técnicas finales documentadas.
- No se redistribuyen páginas fuente, JPEG ni OCR íntegro restringido; FTRL mantiene esos artefactos como reconstrucciones locales por defecto.
- `ocr_available != text_verified`, `search_hit != historical_claim`, `computational_candidate != semantic_ready` y `publicly_accessible != openly_licensed` permanecen como guardas explícitas.
- El issue #2 continúa gobernando las categorías amarilla/roja de derechos hasta que exista aclaración externa o asesoría jurídica específica.
- No se declara DOI de LTMD hasta que exista un depósito real y verificable.
- #119 quedó cerrado después de verificar un ruleset activo sobre `main`, los tres checks obligatorios, ausencia de bypass, descripción canónica y los diez topics de descubrimiento.

## [0.1.0-rc.1] — 2026-08-15

Primera candidata de liberación metodológica y de infraestructura científica.

### Corpus e infraestructura

- Congelado el piloto CN5 con 759 imágenes fuente reales y 9,594 fragmentos reproducibles.
- Materializada la expansión CN4/CN6 con 1,897 posiciones declaradas, 1,888 JPEG reales y 19,067 fragmentos.
- Cerrada la Ola 2 de Ciencias Naturales con 19 libros, 3,177 JPEG fuente y 36,195 fragmentos.
- Consolidado un universo técnico de 64,856 ocurrencias de fragmento, explícitamente distinto de 64,856 observaciones históricas independientes.
- Indexado el Catálogo Histórico reproducible con 542 visores, 542 títulos recuperados y 191 familias normalizadas.
- Resueltos 35/37 visores de la familia estricta Ciencias Naturales; los dos restantes conservan posiciones internas no servidas por el recurso público.

### Procedencia y dependencia documental

- Incorporada verificación SHA-256 de activos fuente antes de OCR/análisis.
- Modeladas reutilización, revisión, reemplazo y aliases documentales.
- Documentada la relación CN4 1972↔1988 y los dos objetos CN6 bajo generación 1993.
- Demostrada identidad byte a byte de los aliases 2018→2019 en 652/652 pares de activos.

### OCR, PAGESTRUCT y FRAGSEG

- Ejecutados pipelines temporales de OCR sin redistribuir transcripciones extensas.
- Consolidada la clasificación estructural PAGESTRUCT para piloto y expansiones.
- Consolidada FRAGSEG para CN4/CN6 y Ola 2 usando `short_residual_candidate` en lugar del constructo problemático `heading_candidate`.
- Mantenida FRAGTYPE 0.3 como capa shadow no destructiva sobre el piloto.

### Clasificación semántica y validación

- Conservado SEMB 0.2 como resultado negativo/diagnóstico; no se recalibró retrospectivamente para maximizar diferencias históricas.
- Documentado 99.49% de incertidumbre global de SEMB 0.2 y su stress test sintético posterior.
- Preregistrada SEMB 0.3 con 480 casos humanos: 320 desarrollo y 160 validación bloqueada.
- Congelados criterios de aceptación, arquitecturas candidatas, gates, doble codificación y evaluación de una sola apertura.
- SEMB 0.3 permanece en `WAITING_HUMAN_REFERENCE`; esta release candidata no contiene modelo validado ni gold standard humano.

### Integridad y publicación

- `LTMD_INTEGRITY_0.5` verifica 150/150 artefactos críticos mediante tamaño y SHA-256.
- Añadido `METHODS_ARTICLE_DRAFT_0_2.md` y CI que recomputa sus cifras centrales desde los artefactos congelados.
- Actualizados README, índice maestro de método, estado del proyecto y snapshot metodológico a la escala actual.
- Preparada metadata CFF para `v0.1.0-rc.1` sin inventar DOI antes del depósito real.

### Derechos y límites

- Los materiales fuente de CONALITEG/SEP no se relicencian ni se redistribuyen masivamente desde LTMD.
- Las imágenes y textos fuente se reconstruyen temporalmente cuando son necesarios y se verifican por hash.
- La licencia del código y la licencia de derivados originales siguen siendo blockers explícitos antes de una release estable.

### No incluido como resultado definitivo

- No hay SEMB 0.3 validado.
- No hay validación humana abierta.
- No hay inferencia histórica semántica primaria basada en la expansión.
- No hay DOI asignado a esta candidata mientras no exista una publicación real en Zenodo.
