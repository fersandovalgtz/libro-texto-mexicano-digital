# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante historia de la educación, humanidades digitales, análisis computacional de textos e imágenes y ciencia abierta.

## Estado actual

**Piloto analítico activo — corpus estructurado y fragmentado; primera capa comparativa A/B construida; validación semántica humana SEMB 0.3 en preparación.**

El corpus piloto está formado por **Ciencias Naturales de quinto grado** en cuatro generaciones del Catálogo Histórico de CONALITEG: **1972, 1988, 1993 y 2014**. La generación se conserva separada del año bibliográfico de cada edición.

La arquitectura de los visores fue reconstruida y auditada. De 763 páginas declaradas por los visores, cuatro son terminales sintéticos sin JPEG; el corpus fuente real contiene **759 imágenes**. El pipeline OCR adaptativo obtiene texto aceptable en **757/759 (99.74%)** sin publicar transcripciones extensas.

La capa estructural clasifica las páginas y la capa de segmentación produce un manifiesto congelado de **9,594 fragmentos**. Sobre ese manifiesto existen actualmente dos aproximaciones independientes de clasificación pedagógica: un clasificador de reglas (A) y un clasificador semántico basado en embeddings (B).

## Pregunta general

¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

## Pregunta del piloto

¿Cómo cambian entre generaciones curriculares la representación de la ciencia y el ambiente, el papel atribuido al alumno y el tipo de actividad pedagógica propuesta en los libros de Ciencias Naturales de quinto grado?

## Estado de la clasificación semántica

SEMB 0.2 fue desarrollado y bloqueado antes de acceder al corpus histórico. Al aplicarse a los 9,594 fragmentos produjo una tasa de incertidumbre global de **99.49%**. Un diagnóstico posterior mostró que el problema no se explica principalmente por la longitud de los fragmentos: entre los 5,037 fragmentos elegibles, el gate de acción bloquea 89.16%, el margen de posición bloquea 74.83% y sólo 49 casos satisfacen simultáneamente las reglas de certeza.

Por este motivo, los resultados históricos derivados de SEMB 0.2 se conservan como **exploratorios**. No se han rebajado umbrales a posteriori para favorecer una narrativa histórica.

El proyecto prepara ahora **SEMB 0.3**, que utilizará una referencia humana independiente de 480 fragmentos (120 por generación), dividida por hash en **320 casos de desarrollo** y **160 de validación bloqueada**. Los IDs visibles para anotadores son opacos y no revelan generación ni rol desarrollo/validación. Un subconjunto de **120 casos** está reservado para doble codificación interanotador.

## Hallazgo metodológico sobre `heading_candidate`

La auditoría de fragmentación demostró que `heading_candidate` no debe interpretarse como un detector de encabezados tipográficos. Es una categoría residual basada principalmente en longitud. Su frecuencia aumenta de 30.47% de los fragmentos en 1972 a 58.16% en 2014 y aparece en 94.74%–100% de las páginas, por lo que el patrón se tratará como señal de fragmentación/longitud hasta contar con validación visual independiente.

## Principio de procedencia y derechos

Este repositorio **no redistribuye indiscriminadamente PDF, imágenes, OCR completo ni otros materiales originales de CONALITEG**. Los originales se documentan mediante identificadores, URL de procedencia y metadatos. Las imágenes fuente y las transcripciones extensas se utilizan como copias temporales de trabajo mientras no exista una base jurídica explícita para redistribuirlas.

GitHub aloja principalmente código reproducible, esquemas y diccionarios, registros de procedencia, documentación metodológica, datos derivados publicables, hashes, metadatos, validaciones y resultados reproducibles. El texto OCR reconstruido para anotación humana no se persiste en el repositorio.

## Arquitectura del piloto

`visor HTML → recursos del visor → JPEG de página → OCR temporal → estructura de página → fragmentación → metadatos/hashes → clasificación A/B → auditorías → comparación histórica`

La fase SEMB 0.3 añade:

`muestra humana ciega → desarrollo 320 → modelo bloqueado → validación 160 → producción sobre corpus congelado → nueva comparación histórica`

## Estructura

- `docs/` — metodología, especificaciones, protocolos, contexto curricular, decisiones y roadmap.
- `data/` — inventario, controles, validación y datos derivados publicables.
- `scripts/` — inspección, OCR, segmentación, clasificación, diagnóstico y validación reproducibles.
- `.github/workflows/` — materialización reproducible de las capas derivadas y auditorías.
- `notebooks/` — exploración reproducible cuando procede.

## Documentos y derivados centrales

Entre los archivos actualmente relevantes se encuentran:

- `docs/CODEBOOK_0_1.md` — categorías analíticas de acción pedagógica y posición del alumno;
- `docs/HISTORICAL_COMPARISON_SPEC_0_1.md` — reglas de comparación histórica;
- `docs/EXPLORATORY_FINDINGS_SPEC_0_1.md` — separación entre resultados preregistrados y exploración post hoc;
- `docs/SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md` — protocolo de referencia humana ciega para SEMB 0.3;
- `data/derived/fragment_manifest.csv` — manifiesto congelado de 9,594 fragmentos;
- `data/derived/fragment_labels_A.csv` — clasificador A;
- `data/derived/fragment_labels_B.csv` — SEMB 0.2;
- `data/derived/classifier_AB_agreement_summary.csv` — acuerdo A/B;
- `data/derived/historical_comparison_summary.md` — comparación histórica preregistrada;
- `data/derived/exploratory_historical_findings.md` — hallazgos exploratorios;
- `data/derived/semb02_uncertainty_diagnostic.md` — diagnóstico del 99.49% de incertidumbre;
- `data/derived/fragseg_heading_candidate_audit.md` — auditoría del constructo `heading_candidate`;
- `data/validation/semb03_human_reference_sample.csv` — muestra maestra SEMB 0.3;
- `data/validation/semb03_human_reference_annotation_template.csv` — plantilla ciega;
- `data/validation/semb03_reliability_subset.csv` — subconjunto de doble codificación.

## Avance

- [x] Delimitar corpus comparable: Ciencias Naturales, quinto grado, cuatro generaciones.
- [x] Reconstruir y auditar los cuatro visores históricos.
- [x] Construir manifiesto reproducible de 759 páginas fuente reales.
- [x] Ejecutar y auditar OCR técnico integral: 757/759 con texto aceptable.
- [x] Clasificar estructura de página.
- [x] Segmentar el corpus en 9,594 fragmentos con hashes reproducibles.
- [x] Construir clasificador A basado en reglas.
- [x] Desarrollar, bloquear y aplicar SEMB 0.2.
- [x] Construir comparación A/B y primera capa histórica reproducible.
- [x] Separar hallazgos robustos exploratorios de hallazgos sensibles al método.
- [x] Diagnosticar formalmente el cuello de botella de incertidumbre de SEMB 0.2.
- [x] Auditar el constructo `heading_candidate` y retirar su interpretación tipográfica automática.
- [x] Preregistrar muestra humana ciega SEMB 0.3: 480 casos, 320 desarrollo + 160 validación bloqueada.
- [x] Preparar 120 casos para fiabilidad interanotador.
- [x] Implementar herramienta de anotación que reconstruye texto efímeramente y persiste sólo códigos.
- [ ] Completar la codificación humana de desarrollo y la doble codificación de fiabilidad.
- [ ] Fijar criterios cuantitativos de éxito de SEMB 0.3 antes de abrir la validación bloqueada.
- [ ] Desarrollar y bloquear SEMB 0.3 sobre los 320 casos de desarrollo.
- [ ] Abrir una sola vez los 160 casos de validación y documentar el resultado.
- [ ] Aplicar SEMB 0.3 al corpus congelado si supera la validación.
- [ ] Recalcular la comparación histórica con la nueva capa validada.
- [ ] Validar visualmente la categoría residual `heading_candidate` y decidir si requiere una nueva versión del segmentador.
- [ ] Escalar el modelo metodológico a otras asignaturas, grados y generaciones.

## Registro metodológico

Además del historial de commits y esta documentación, el proyecto mantiene una bitácora técnica. Los intentos fallidos metodológicamente relevantes se conservan: el objetivo no es ocultar las rutas que no funcionaron, sino hacer auditable cómo se llegó a cada decisión.

## Autoría y citación

Proyecto dirigido por **Fernando Sandoval Gutiérrez**. La forma de citación, versión archivada y DOI se formalizarán cuando el piloto alcance una primera liberación estable.

## Licencias y derechos

La licencia del código y de los datos derivados se definirá una vez concluida la auditoría de derechos y términos de uso. Los derechos sobre los materiales fuente permanecen con sus respectivos titulares.
