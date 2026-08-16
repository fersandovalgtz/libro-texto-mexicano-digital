# Changelog

Todos los cambios notables de **Libro de Texto Mexicano Digital (LTMD)** se documentan aquí. El proyecto permanece en fase pre-1.0; las releases candidatas pueden cambiar antes de una primera liberación estable.

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
