# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante historia de la educación, humanidades digitales, análisis computacional y ciencia abierta.

## Estado actual

**Infraestructura histórico-computacional en expansión — piloto CN5 congelado y auditable; catálogo histórico indexado; CN4/CN6 convertido en corpus técnico; SEMB 0.3 permanece correctamente bloqueado a la espera de referencia humana.**

LTMD ya opera en tres escalas diferenciadas:

1. **piloto semántico CN5** — Ciencias Naturales de quinto grado en generaciones 1972, 1988, 1993 y 2014;
2. **expansión técnica CN4/CN6** — nueve objetos adicionales auditados en esas generaciones, sin clasificación semántica productiva;
3. **catálogo maestro** — snapshot reproducible de los 542 visores históricos actualmente expuestos por el catálogo público, con 542 títulos recuperables y 191 familias de título nuclear normalizadas.

La separación entre estas escalas es deliberada: que un objeto sea técnicamente procesable (`corpus_ready`) no lo convierte automáticamente en `semantic_ready`.

## Pregunta general

¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

## Piloto CN5

El corpus piloto está formado por **Ciencias Naturales de quinto grado** en cuatro generaciones del Catálogo Histórico de CONALITEG: **1972, 1988, 1993 y 2014**. `catalog_generation` se mantiene separada del año bibliográfico del ejemplar concreto.

La arquitectura de los visores fue reconstruida y auditada. De 763 posiciones declaradas, cuatro son terminales sintéticos sin JPEG; el corpus fuente real contiene **759 imágenes**. El pipeline OCR adaptativo obtiene texto técnicamente detectable en **757/759 (99.74%)** sin publicar transcripciones extensas.

PAGESTRUCT y FRAGSEG producen un manifiesto congelado de **9,594 fragmentos** con identificadores y SHA-256 reproducibles. Existen un clasificador de reglas (A), SEMB 0.2 (B), comparación A/B y una primera capa histórica que se conserva como **exploratoria** mientras no exista validación humana suficiente.

## SEMB 0.2: diagnóstico, no resultado definitivo

SEMB 0.2 fue desarrollado y bloqueado antes de acceder al corpus histórico. Al aplicarse a los 9,594 fragmentos produjo **99.49% de incertidumbre global**. Entre los **5,037 fragmentos elegibles** del diseño original, sólo 49 satisfacen simultáneamente las reglas de certeza de acción y posición.

Una batería posterior de **105 casos sintéticos en español**, independiente del corpus histórico y aplicada al SEMB 0.2 ya congelado, confirmó un problema estructural del gate: balanced accuracy 0.526, sensibilidad 0.597 y especificidad 0.455; en negativos de estrés la tasa de falsos positivos es 53.3%. Por ello **no se corrigió SEMB 0.2 bajando umbrales a posteriori**.

## SEMB 0.3: protocolo prehumano congelado

Se materializó una referencia humana futura de **480 fragmentos**: 120 por generación, divididos por hash en **320 `development`** y **160 `locked_validation`**. Los IDs visibles son opacos y no revelan generación, página, tipo de fragmento ni rol de análisis. Un subconjunto de **120 casos** está reservado para doble codificación interanotador.

Antes de observar una sola anotación humana se congelaron:

- criterios cuantitativos de fiabilidad, desempeño, cobertura e incertidumbre;
- un grid cerrado de arquitecturas candidatas;
- validación cruzada `GroupKFold` por página durante desarrollo;
- prohibición de usar generación, Rule A, resultados históricos o SEMB 0.2 como features/objetivo de ajuste;
- validador de archivos de anotación y cálculo de fiabilidad;
- consenso automático únicamente para coincidencias exactas y cola de adjudicación humana para desacuerdos;
- bloqueo criptográfico del modelo antes de abrir validación;
- evaluador de validación de **una sola apertura**, que se niega a correr sin `model_lock` y se niega a reemplazar una evaluación ya existente.

El readiness automático registra **16/16 módulos prehumanos materializados** y mantiene la etapa `WAITING_HUMAN_REFERENCE`.

## Candidatos sintéticos de SEMB 0.3

El material sintético funciona únicamente como **desarrollo provisional prehumano**. Un simple cambio del threshold del gate casi no ayuda (balanced accuracy 0.537), mientras una cabeza logística sobre rasgos de similitud semántica llega a **0.631** en validación cruzada sintética. Para acciones, el híbrido anchor + centroide alcanza **79.2% top-1**; para posiciones, **77.8%**.

Estos candidatos se etiquetan `PROVISIONAL_SYNTHETIC_ONLY`: **no son SEMB 0.3 validado** y no pueden saltar directamente a producción.

## Corrección metodológica de unidades breves

FRAGSEG 0.2 denominó `heading_candidate` a una categoría residual de unidades breves sin evidencia tipográfica suficiente. Una auditoría de layout sobre 160 fragmentos no encontró una firma consistente de encabezado.

Por ello existe `FRAGTYPE_0.3_SHADOW`, una capa **no destructiva** que conserva límites, IDs y hashes y renombra esas unidades como `short_residual_candidate`. Si la elegibilidad semántica se separa de la etiqueta residual, el universo potencial de fragmentos de ≥4 tokens pasa de **5,037 a 7,429 (+2,392; +47.5%)**.

No se incorporan automáticamente esos casos al análisis: una muestra suplementaria ciega de **160 unidades breves residuales** —100 desarrollo + 60 validación bloqueada— decidirá posteriormente la política final.

## Catálogo maestro reproducible

LTMD ya no depende de búsquedas manuales en la interfaz. El Catálogo Histórico carga un archivo público `libros_2023.js`; el proyecto conserva un snapshot con SHA-256 y extrae de manera reproducible los identificadores de visor sin ejecutar JavaScript remoto.

Estado actual del índice:

- **542 claves de visor** detectadas;
- **542/542 visores alcanzables**;
- **542/542 títulos HTML recuperados**;
- **191 familias de título nuclear** tras normalización conservadora de capitalización/diacríticos;
- **8 grupos de títulos repetidos** que se conservan como colas de auditoría, nunca como instrucciones automáticas de deduplicación.

La familia de título nuclear **Ciencias Naturales** contiene **37 visores** en nueve generaciones. El piloto CN5 y la expansión CN4/CN6 actual cubren **12/37** de esos visores de título estricto; materiales históricamente relacionados con títulos distintos, como *Ciencias Naturales y desarrollo humano*, se modelan por relación documental y no se fuerzan dentro de la familia nominal.

## Expansión CN4/CN6

Se descubrieron y auditaron **nueve objetos** de Ciencias Naturales de cuarto y sexto grados en las generaciones 1972, 1988, 1993 y 2014. La generación 1993 contiene dos objetos distintos de sexto grado, por lo que la expansión usa `book_id` y `viewer_key` como identidad documental y no supone un único libro por generación.

### Procedencia y activos

- posiciones declaradas por los nueve visores: **1,897**;
- JPEG fuente reales: **1,888**;
- terminales sintéticos: **9**;
- los **1,888 JPEG** fueron recorridos y verificados mediante SHA-256;
- el manifiesto de páginas persiste URL, tamaño, hash y procedencia, pero no redistribuye las imágenes fuente.

### OCR técnico

Todas las fuentes se reconstruyen temporalmente y deben coincidir con su SHA-256 antes de OCR:

- **1,888/1,888** fuentes verificadas;
- **1,880/1,888 (99.58%)** con texto detectado;
- **8** páginas `no_text_detected`;
- **0** páginas `unresolved`.

Las ocho páginas sin texto OCR fueron auditadas mediante proxies visuales y las ocho muestran contenido visual sustantivo; ninguna se clasificó como casi vacía. `text_detected` mide cobertura técnica, no exactitud CER/WER.

### PAGESTRUCT CN4/CN6

La capa estructural se adaptó para agrupar por `book_id` y verificar el hash de cada imagen reconstruida:

- `textual`: **877**;
- `mixed_text_image`: **682**;
- `visual_only`: **153**;
- `toc_or_navigation`: **36**;
- `bibliography_or_credits`: **30**;
- `front_matter`: **2**;
- `unknown`: **108**.

Las clases `textual` + `mixed_text_image` producen **1,559 páginas elegibles** para FRAGSEG. La expansión usa desde su primera versión el nombre `short_residual_candidate` y no repite el constructo problemático `heading_candidate`.

## Dependencia documental: una nueva dimensión de LTMD

La expansión demostró que `catalog_generation` **no puede usarse como sustituto automático de edición, año ni independencia documental**.

### CN4: generación 1972 ↔ 1988

Los dos objetos tienen 214 páginas fuente alineables. **188/214 (87.9%) son byte-idénticas y ocupan la misma posición**. Las 26 páginas restantes se concentran en 1–5, 96–99 y el bloque final 192–214. En esas páginas cambiadas, la mediana de similitud secuencial del OCR normalizado es sólo **0.305**: hay reutilización masiva acompañada por revisión localizada, no una simple copia íntegra ni dos observaciones independientes.

### CN6 dentro de la generación 1993

El catálogo contiene simultáneamente:

- `LTMD-CN6-G1993-CN` — *Ciencias Naturales*, objeto temprano de la reforma, históricamente asociado con primera edición 1994 y reimpresiones posteriores;
- `LTMD-CN6-G1993-DH` — *Ciencias Naturales y desarrollo humano*, cuya página legal recupera **primera edición 1999** y cuya relación histórica es de reemplazo del objeto anterior.

Ambos se conservan. LTMD modela ahora `catalog_generation + edition_year + document_role + viewer_key` y mantiene clusters de dependencia documental. La deduplicación es una vista analítica reversible, nunca una operación que borra procedencia.

## Bibliografía y contexto curricular

El inventario distingue sistemáticamente generación de catálogo, edición y copyright. En el piloto CN5:

- 1972: año de edición no verificado; señal de copyright 1972 sin convertirla en `edition_year`;
- 1988: año de edición no verificado; copyright SEP 1977 e ISBN 968-29-0758-6;
- generación 1993: **primera edición 1998**, ISBN 970-18-1599-8, verificada en página legal;
- 2014: **tercera edición revisada 2014**, ISBN 978-607-514-722-2, verificada en página legal.

Las afirmaciones de contexto se separan por nivel de evidencia: objeto primario, norma oficial, fuente institucional retrospectiva e historiografía especializada.

## Derechos y reutilización

Este repositorio **no redistribuye indiscriminadamente PDF, imágenes, OCR completo ni otros materiales originales de CONALITEG**. Los originales se documentan mediante identificadores, URL de procedencia, tamaños y hashes. Cuando una etapa necesita texto o imagen, el material se reconstruye temporalmente, se verifica contra SHA-256 y se elimina al concluir la tarea.

GitHub aloja principalmente código reproducible, esquemas, registros de procedencia, documentación metodológica, datos derivados no sustitutivos, hashes, validaciones y resultados reproducibles. Código y derivados propios se licenciarán separadamente de los derechos de los materiales fuente.

## Arquitectura

`catálogo → visor → manifiesto de páginas + SHA → OCR temporal → PAGESTRUCT → FRAGSEG → metadatos/hashes → clasificación validada → análisis histórico`

SEMB 0.3 añade:

`muestra ciega → fiabilidad humana → desarrollo 320 con GroupKFold por página → model lock → validación única 160 → producción → reconstrucción histórica`

La expansión añade explícitamente:

`book_id + edition_year + document_role + document_cluster_id → object view / unique-content view / revision view`

## Publicación científica

El proyecto separa dos productos para evitar que un solo artículo mezcle infraestructura con resultados semánticos todavía no validados:

1. **artículo de método/recurso digital**, cuyo primer borrador ya existe en `docs/METHODS_ARTICLE_DRAFT_0_1.md` y puede avanzar con corpus, procedencia, OCR, segmentación, resultados negativos y diseño de validación;
2. **artículo histórico-educativo**, reservado hasta que SEMB 0.3 supere la referencia humana bloqueada y se reconstruyan las tendencias.

Las cifras centrales del borrador metodológico se verifican automáticamente contra los datos mediante CI para impedir desalineación entre manuscrito y repositorio.

## Integridad científica

`LTMD_INTEGRITY_0.4` controla actualmente **102 artefactos críticos** mediante tamaño y SHA-256, además de derivados reproducibles adicionales. El manifiesto cubre el piloto, protocolos SEMB, artículo metodológico, catálogo maestro, expansión CN4/CN6, relaciones documentales, OCR y PAGESTRUCT.

## Documentos centrales

- `docs/METHODS_ARTICLE_DRAFT_0_1.md` — primer borrador real del artículo metodológico;
- `docs/METHODS_SNAPSHOT_2026-08-15.md` — instantánea metodológica del piloto;
- `docs/PRIMARY_SOURCE_REGISTER_0_1.md` — jerarquía y pendientes de fuentes históricas;
- `docs/CURRICULAR_CONTEXT_0_2.md` — contexto curricular con niveles de evidencia;
- `docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md` — criterios congelados de aceptación;
- `docs/SEMB03_CANDIDATE_ARCHITECTURES_0_1.md` — espacio cerrado de arquitecturas;
- `docs/SEMB03_STAGE_GATES_0_1.md` — puertas desarrollo→lock→validación→producción;
- `docs/DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md` — reglas preregistradas para reutilización, revisión y reemplazo documental;
- `docs/CN6_1993_DOCUMENT_RELATION_0_1.md` — relación entre los dos objetos de sexto en la generación 1993;
- `docs/RIGHTS_AND_REUSE_0_1.md` — política conservadora de fuentes y derivados;
- `docs/PUBLICATION_STRATEGY_0_1.md` — separación artículo de método / artículo histórico;
- `docs/CORPUS_EXPANSION_PLAN_0_1.md` — estrategia de escalamiento;
- `docs/RELEASE_CHECKLIST_0_1.md` — requisitos para primera release científica estable;
- `data/catalog/conaliteg_historical_title_inventory.csv` — inventario maestro de 542 visores/títulos;
- `data/catalog/conaliteg_title_cores.csv` — normalización documental de familias;
- `data/catalog/ciencias_naturales_family_inventory.csv` — familia estricta Ciencias Naturales;
- `data/expansion/cn46_page_manifest.csv` — manifiesto SHA-256 de 1,897 posiciones / 1,888 JPEG;
- `data/expansion/cn46_ocr_page_metrics.csv` — métricas OCR sin transcripción;
- `data/expansion/cn46_page_structure.csv` — PAGESTRUCT de expansión;
- `data/derived/research_integrity_manifest.json` — manifiesto criptográfico global.

## Avance

### Piloto CN5 / validación semántica

- [x] Delimitar y auditar el corpus fuente.
- [x] OCR adaptativo: 757/759 páginas con texto detectable.
- [x] PAGESTRUCT y FRAGSEG: 9,594 fragmentos.
- [x] Clasificador A y SEMB 0.2; comparación A/B e historia exploratoria.
- [x] Diagnosticar el colapso de certeza de SEMB 0.2.
- [x] Construir stress test sintético independiente del corpus histórico.
- [x] Auditar y corregir conceptualmente `heading_candidate` sin alterar fragmentos.
- [x] Crear FRAGTYPE 0.3 shadow y cuantificar 2,392 unidades potencialmente recuperables.
- [x] Preregistrar 480 casos humanos = 320 desarrollo + 160 validación bloqueada.
- [x] Preregistrar 120 casos de fiabilidad y 160 unidades breves suplementarias.
- [x] Congelar criterios, grid, GroupKFold, model lock y evaluación única.
- [ ] Obtener doble codificación humana y superar el gate de fiabilidad.
- [ ] Completar/adjudicar la referencia humana de desarrollo.
- [ ] Desarrollar, bloquear y validar SEMB 0.3.
- [ ] Reconstruir la historia semántica sólo si supera los criterios congelados.

### Catálogo y expansión

- [x] Congelar snapshot del catálogo histórico y 542 claves de visor.
- [x] Recuperar 542/542 títulos y normalizarlos en 191 familias.
- [x] Delimitar los 37 visores de la familia estricta Ciencias Naturales.
- [x] Descubrir y auditar nueve objetos CN4/CN6.
- [x] Construir manifiesto SHA-256 de 1,888 JPEG de expansión.
- [x] Ejecutar OCR técnico: 1,880/1,888 con texto; 0 unresolved.
- [x] Auditar las 8 páginas sin texto como contenido visual.
- [x] Ejecutar PAGESTRUCT sobre 1,888 páginas.
- [x] Detectar y modelar dependencia documental CN4 1972↔1988 y CN6 1993→1999.
- [ ] Finalizar FRAGSEG técnico CN4/CN6 y publicar manifiesto combinado.
- [ ] Incorporar progresivamente los 25 visores restantes de la familia estricta Ciencias Naturales.
- [ ] No ejecutar clasificación semántica productiva sobre la expansión hasta disponer de un modelo validado apropiado.

## Estado epistemológico

La infraestructura prehumana de SEMB 0.3 está completa. El límite restante para resultados semánticos históricos no es de ingeniería, sino de **validez de constructo y referencia humana**. La expansión técnica puede continuar —inventario, procedencia, OCR, estructura, segmentación y relaciones documentales— sin violar ese bloqueo.

## Autoría y citación

Proyecto dirigido por **Fernando Sandoval Gutiérrez**. `CITATION.cff` está presente; la versión archivada, DOI de release y licencias finales se formalizarán al cerrar una liberación científica estable.

## Licencias y derechos

Los derechos sobre los materiales fuente permanecen con sus respectivos titulares. La licencia del código y de los datos derivados propios de LTMD se definirá de forma separada antes de la primera release estable.
