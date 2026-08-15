# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante historia de la educación, humanidades digitales, análisis computacional y ciencia abierta.

## Estado actual

**Piloto computacional avanzado — corpus congelado y auditable; SEMB 0.2 diagnosticado; infraestructura prehumana de SEMB 0.3 materializada; referencia humana pendiente.**

El corpus piloto está formado por **Ciencias Naturales de quinto grado** en cuatro generaciones del Catálogo Histórico de CONALITEG: **1972, 1988, 1993 y 2014**. `catalog_generation` se mantiene separada del año bibliográfico del ejemplar concreto.

La arquitectura de los visores fue reconstruida y auditada. De 763 páginas declaradas, cuatro son terminales sintéticos sin JPEG; el corpus fuente real contiene **759 imágenes**. El pipeline OCR adaptativo obtiene texto aceptable en **757/759 (99.74%)** sin publicar transcripciones extensas.

La capa estructural y de segmentación produce un manifiesto congelado de **9,594 fragmentos** con identificadores y SHA-256 reproducibles. Existen un clasificador de reglas (A), SEMB 0.2 (B), comparación A/B y una primera capa histórica que se conserva como **exploratoria** mientras no exista validación humana suficiente.

## Pregunta general

¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

## Pregunta del piloto

¿Cómo cambian entre generaciones editoriales/curriculares la representación de la ciencia y el ambiente, el papel atribuido al alumno y el tipo de actividad pedagógica propuesta en los libros de Ciencias Naturales de quinto grado?

## SEMB 0.2: diagnóstico, no resultado definitivo

SEMB 0.2 fue desarrollado y bloqueado antes de acceder al corpus histórico. Al aplicarse a los 9,594 fragmentos produjo **99.49% de incertidumbre global**. Entre los **5,037 fragmentos elegibles** del diseño original, el gate/buffer de acción bloquea 89.16%, el margen de posición bloquea 74.83% y sólo 49 fragmentos satisfacen simultáneamente las reglas de certeza.

Una batería posterior de **105 casos sintéticos en español**, independiente del corpus histórico y aplicada al SEMB 0.2 ya congelado, confirmó un problema estructural del gate: balanced accuracy 0.526, sensibilidad 0.597 y especificidad 0.455; en negativos de estrés la tasa de falsos positivos es 53.3%. Por ello **no se corrigió SEMB 0.2 bajando umbrales a posteriori**.

## SEMB 0.3: protocolo prehumano congelado

Se materializó una referencia humana futura de **480 fragmentos**: 120 por generación, divididos por hash en **320 `development`** y **160 `locked_validation`**. Los IDs visibles son opacos y no revelan generación, página, tipo de fragmento ni rol de análisis. Un subconjunto de **120 casos** está reservado para doble codificación interanotador.

Antes de observar una sola anotación humana se congelaron:

- criterios cuantitativos de fiabilidad, desempeño, cobertura e incertidumbre;
- un grid cerrado de arquitecturas candidatas;
- validación cruzada `GroupKFold` por página durante desarrollo;
- prohibición de usar generación, Rule A, resultados históricos o SEMB 0.2 como features/objetivo de ajuste;
- validador de archivos de anotación;
- cálculo de fiabilidad;
- consenso automático únicamente para coincidencias exactas y cola de adjudicación humana para desacuerdos;
- bloqueo criptográfico del modelo antes de abrir validación;
- evaluador de validación de **una sola apertura**, que se niega a correr sin `model_lock` y se niega a reemplazar una evaluación ya existente.

El criterio de producción exige, entre otros mínimos, balanced accuracy del gate ≥0.80, micro-F1 de acciones ≥0.75, micro-F1 de posiciones ≥0.70, **≥70% de salidas ciertas**, brecha de incertidumbre entre generaciones ≤20 puntos porcentuales y ausencia de truncamiento silencioso.

## Candidatos sintéticos de SEMB 0.3

El material sintético ya no funciona como validación independiente del futuro SEMB 0.3; se usa únicamente como **desarrollo provisional prehumano**.

Dos diagnósticos sugieren una ruta razonable para llevar a los 320 humanos de desarrollo:

- un simple cambio del threshold del gate casi no ayuda (balanced accuracy 0.537), mientras una cabeza logística sobre rasgos de similitud semántica llega a **0.631** en validación cruzada sintética;
- para acciones, el híbrido anchor + centroide sintético alcanza **79.2% top-1** frente a 75.0% de los anchors congelados; para posiciones alcanza **77.8%** frente a 63.0%.

Estos candidatos se etiquetan `PROVISIONAL_SYNTHETIC_ONLY`: **no son SEMB 0.3 validado** y no pueden saltar directamente a producción.

## Corrección metodológica de `heading_candidate`

FRAGSEG 0.2 denominó `heading_candidate` a una categoría residual de unidades breves; la regla no utiliza evidencia tipográfica. Su prevalencia aumenta de 30.47% en 1972 a 58.16% en 2014 y aparece en casi todas las páginas.

Una auditoría de layout sobre 160 fragmentos tampoco encuentra una firma tipográfica consistente de encabezado: la altura mediana relativa es aproximadamente la misma que la del texto expositivo, casi no hay mayúsculas sostenidas y una proporción importante termina con puntuación.

Por ello existe `FRAGTYPE_0.3_SHADOW`, una capa **no destructiva** que conserva límites, IDs y hashes y renombra esas unidades como `short_residual_candidate`. Si la elegibilidad semántica se separa de la etiqueta residual, el universo potencial de fragmentos de ≥4 tokens pasa de **5,037 a 7,429 (+2,392; +47.5%)**.

No se incorporan automáticamente esos 2,392 casos al análisis. Se congeló una muestra suplementaria ciega de **160 unidades breves residuales** —100 desarrollo + 60 validación bloqueada— para decidir posteriormente, con juicio humano y contexto visual, qué unidades son encabezados reales y cuáles son contenido semánticamente analizable.

## Cobertura de la muestra humana principal

La muestra SEMB 0.3 de 480 casos abarca **312 páginas distintas**; los 160 casos bloqueados abarcan **138 páginas**. La mediana de longitud es 16 tokens frente a 15 en el universo elegible. La cobertura general por página y longitud es adecuada para el propósito de validación; los tipos funcionales raros tienen menor representación y no sostendrán inferencias finas sin evidencia adicional.

Se congelaron pesos descriptivos de postestratificación por generación × tipo y generación × longitud para análisis posterior de transportabilidad. No se utilizarán para redefinir el modelo a partir de los resultados históricos.

## Bibliografía y contexto curricular

El inventario distingue sistemáticamente generación de catálogo, edición y copyright. Actualmente:

- 1972: año de edición no verificado; una auditoría automática detecta señal de copyright 1972, sin convertirla en `edition_year`;
- 1988: año de edición no verificado; copyright SEP 1977 e ISBN 968-29-0758-6;
- generación 1993: **primera edición 1998**, ISBN 970-18-1599-8, verificada en página legal;
- 2014: **tercera edición revisada 2014**, ISBN 978-607-514-722-2, verificada en página legal.

La propia clasificación histórica de CONALITEG se interpreta como una organización institucional/editorial del catálogo, no automáticamente como una secuencia de reformas curriculares equivalentes. Las afirmaciones de contexto se separan por nivel de evidencia: objeto primario, norma oficial, fuente institucional retrospectiva e historiografía especializada.

## Principio de procedencia y derechos

Este repositorio **no redistribuye indiscriminadamente PDF, imágenes, OCR completo ni otros materiales originales de CONALITEG**. Los originales se documentan mediante identificadores, URL de procedencia y metadatos. Cuando una etapa necesita texto, éste se reconstruye temporalmente desde la fuente y se contrasta con el SHA-256 persistido.

GitHub aloja principalmente código reproducible, esquemas, registros de procedencia, documentación metodológica, datos derivados publicables, hashes, validaciones y resultados reproducibles.

## Arquitectura

`visor → JPEG → OCR temporal → PAGESTRUCT → FRAGSEG → metadatos/hashes → A / SEMB → auditorías → análisis condicionado a validación`

SEMB 0.3 añade:

`muestra ciega → fiabilidad humana → desarrollo 320 con GroupKFold por página → model lock → validación única 160 → producción → reconstrucción histórica`

## Documentos y derivados centrales

- `docs/METHODS_SNAPSHOT_2026-08-15.md` — instantánea metodológica completa;
- `docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md` — criterios congelados de aceptación;
- `docs/SEMB03_CANDIDATE_ARCHITECTURES_0_1.md` — espacio cerrado de arquitecturas;
- `docs/SEMB03_STAGE_GATES_0_1.md` — puertas desarrollo→lock→validación→producción;
- `docs/HISTORICAL_ANALYSIS_PLAN_0_2.md` — análisis histórico posterior a validación;
- `docs/SHORT_RESIDUAL_VALIDATION_PROTOCOL_0_1.md` — validación suplementaria de unidades breves;
- `docs/AUTOMATED_WORK_CEILING_0_1.md` — límite epistemológico del trabajo sin humanos;
- `data/derived/fragment_manifest.csv` — 9,594 fragmentos congelados;
- `data/derived/fragment_manifest_fragtype03_shadow.csv` — re-tipificación shadow no destructiva;
- `data/derived/semb02_uncertainty_diagnostic.md` — diagnóstico de SEMB 0.2;
- `data/derived/semb02_synthetic_stress_result.md` — stress test independiente de SEMB 0.2;
- `data/derived/fragseg_layout_proxy_audit.md` — auditoría geométrica del constructo residual;
- `data/derived/semb03_sample_coverage.md` — cobertura, páginas y longitud de la muestra;
- `data/validation/semb03_candidate_grid.json` — grid SEMB 0.3 legible por máquina;
- `data/derived/research_integrity_manifest.json` — huellas SHA-256 de artefactos críticos.

## Avance

- [x] Delimitar y auditar el corpus fuente.
- [x] OCR adaptativo: 757/759 páginas con texto aceptable.
- [x] PAGESTRUCT y manifiesto FRAGSEG de 9,594 fragmentos.
- [x] Clasificador A y SEMB 0.2; comparación A/B e historia exploratoria.
- [x] Diagnosticar el colapso de certeza de SEMB 0.2.
- [x] Construir stress test sintético independiente del corpus histórico.
- [x] Auditar y corregir conceptualmente `heading_candidate` sin alterar fragmentos.
- [x] Crear FRAGTYPE 0.3 shadow y cuantificar 2,392 unidades potencialmente recuperables.
- [x] Preregistrar muestra humana principal 480 = 320 desarrollo + 160 bloqueada.
- [x] Preregistrar 120 casos de fiabilidad interanotador.
- [x] Preregistrar muestra suplementaria de 160 unidades breves residuales.
- [x] Congelar criterios de éxito de SEMB 0.3.
- [x] Congelar grid de arquitecturas y selección GroupKFold por página.
- [x] Implementar validadores, consenso no adjudicador, model lock y evaluación única.
- [x] Añadir CI de la infraestructura y manifiesto criptográfico de integridad.
- [x] Preregistrar plan histórico posterior a validación.
- [ ] Obtener doble codificación humana y superar el gate de fiabilidad.
- [ ] Completar/adjudicar la referencia humana de los 320 casos de desarrollo.
- [ ] Desarrollar SEMB 0.3 únicamente sobre development y bloquearlo.
- [ ] Abrir una sola vez los 160 casos de validación.
- [ ] Aplicar SEMB 0.3 al corpus sólo si supera los criterios congelados.
- [ ] Decidir, mediante la muestra suplementaria, la política final para unidades breves residuales.
- [ ] Reconstruir y contextualizar la comparación histórica con la capa validada.
- [ ] Escalar el modelo metodológico a otras asignaturas, grados y generaciones.

## Estado epistemológico

La mayor parte del trabajo automatizable previo a humanos está ya realizada. Seguir agregando complejidad computacional puede producir más diagnósticos, pero **no resolverá por sí sola la pregunta central de validez de constructo**: si las categorías automáticas corresponden a juicios humanos reproducibles sobre las tareas pedagógicas y posiciones del alumno.

## Autoría y citación

Proyecto dirigido por **Fernando Sandoval Gutiérrez**. La versión archivada, DOI y forma de citación se formalizarán al alcanzar una liberación estable.

## Licencias y derechos

La licencia del código y de los datos derivados se definirá una vez concluida la auditoría de derechos y términos de uso. Los derechos sobre los materiales fuente permanecen con sus respectivos titulares.
