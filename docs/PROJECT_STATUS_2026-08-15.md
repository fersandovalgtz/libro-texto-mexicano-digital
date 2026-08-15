# Estado consolidado de Libro de Texto Mexicano Digital

Fecha de corte: 2026-08-15

## 1. Estado general

LTMD dejó de ser únicamente un piloto de quinto grado. A este corte posee cuatro capas claramente diferenciadas:

1. un **piloto CN5** completo desde procedencia hasta una primera capa semántica exploratoria;
2. una **infraestructura SEMB 0.3 prehumana** cerrada y bloqueada correctamente;
3. dos expansiones técnicas de la familia *Ciencias Naturales* cerradas hasta FRAGSEG: **CN4/CN6** y **Ola 2**;
4. una **auditoría de activos de la familia estricta Ciencias Naturales** con 35/37 visores completamente resueltos y sólo tres posiciones internas no servidas en dos objetos 2008.

El corpus técnico materializa **64,856 ocurrencias de fragmento**: 9,594 del piloto CN5, 19,067 de CN4/CN6 y 36,195 de Ola 2. Esta suma no equivale a 64,856 observaciones históricas independientes; LTMD representa explícitamente aliases, reutilización, revisiones y contenido repetido.

La principal frontera pendiente para inferencias semánticas históricas continúa siendo epistemológica: referencia humana y validación de constructo. Las expansiones están `corpus_ready`, no `semantic_ready`.

## 2. Piloto CN5 — consolidado

Corpus: *Ciencias Naturales*, quinto grado, generaciones CONALITEG 1972, 1988, 1993 y 2014.

- 763 posiciones de visor;
- 759 JPEG reales;
- 4 terminales sintéticos;
- OCR técnico: 757/759 con texto detectable;
- PAGESTRUCT 0.2: 759 páginas;
- FRAGSEG 0.2: 9,594 fragmentos;
- RULEA 0.1 aplicado;
- SEMB 0.2 aplicado;
- comparación A/B y primera capa histórica reproducible;
- resultados históricos SEMB 0.2: **exploratorios, no finales**.

SEMB 0.2 produjo 99.49% de incertidumbre global y sólo 49 fragmentos simultáneamente ciertos en acción y posición. Una batería sintética independiente de 105 casos produjo balanced accuracy 0.526 para el gate, con sensibilidad 0.597 y especificidad 0.455. El resultado se conserva como evidencia metodológica negativa, no como motivo para bajar umbrales observando la historia.

## 3. SEMB 0.3 — infraestructura prehumana cerrada

- 480 casos de referencia humana futura;
- 320 `development`;
- 160 `locked_validation`;
- 120 doble codificación para fiabilidad;
- 312 páginas cubiertas en la muestra y 138 en validación bloqueada;
- IDs opacos y plantilla ciega;
- criterios `SEMB03_ACCEPTANCE_0.1` congelados antes de humanos;
- grid `SEMB03_CANDIDATES_0.1` congelado;
- desarrollo con `GroupKFold` por `page_id`;
- model lock criptográfico;
- evaluador de una sola apertura;
- consenso automático sólo para coincidencias exactas;
- desacuerdos requieren adjudicación humana;
- etapa: `WAITING_HUMAN_REFERENCE`.

Los candidatos sintéticos siguen siendo no productivos. No se proyectan sobre las expansiones del corpus.

## 4. Corrección de FRAGSEG

`heading_candidate` se retiró como interpretación tipográfica. `FRAGTYPE_0.3_SHADOW` conserva límites, IDs y hashes y lo reinterpreta como unidad breve residual.

- elegibles originales SEMB: 5,037;
- elegibles shadow: 7,429;
- recuperables potenciales: 2,392 (+47.5%);
- muestra suplementaria: 160 unidades breves, 100 desarrollo + 60 validación.

La Ola 2 ya emplea la nomenclatura conservadora `short_residual_candidate`.

## 5. Catálogo maestro CONALITEG

Snapshot reproducible de la fuente pública de catálogo:

- 542 claves de visor;
- 542/542 visores alcanzables;
- 542/542 títulos HTML recuperados;
- 191 familias normalizadas de título nuclear;
- 8 grupos de título repetido, conservados como colas de auditoría;
- familia estricta *Ciencias Naturales*: 37 visores en nueve generaciones.

La identidad de un objeto se modela por `book_id` + `viewer_key`; la generación del catálogo no se usa como sustituto de edición.

## 6. Expansión CN4/CN6 — corpus técnico cerrado hasta FRAGSEG

Nueve objetos adicionales de cuarto y sexto grados en 1972, 1988, 1993 y 2014, incluyendo dos objetos distintos de sexto dentro de la generación 1993.

### Activos

- 1,897 posiciones declaradas;
- 1,888 JPEG reales;
- 9 terminales sintéticos;
- 1,888/1,888 JPEG con SHA-256 verificado;
- no se persisten imágenes fuente.

### OCR

- 1,888 páginas procesadas;
- 1,880 con texto detectable (99.58%);
- 8 `no_text_detected`;
- 0 `unresolved`.

### PAGESTRUCT

- textual: 877;
- mixed_text_image: 682;
- visual_only: 153;
- toc_or_navigation: 36;
- bibliography_or_credits: 30;
- front_matter: 2;
- unknown: 108;
- elegibles para FRAGSEG: 1,559 páginas.

### FRAGSEG

- 19,067 fragmentos únicos;
- 1,559 páginas segmentadas;
- `short_residual_candidate`: 8,483;
- `question_candidate`: 3,711;
- `expository_candidate`: 3,183;
- `instruction_candidate`: 2,906;
- `activity_candidate`: 427;
- `experiment_candidate`: 234;
- `project_candidate`: 87;
- `assessment_candidate`: 36;
- 34 páginas presentan huecos legítimos por descarte de 40 candidatos de 0 tokens; no se renumeraron IDs.

## 7. Ciencias Naturales Ola 2 — corpus técnico cerrado

La Ola 2 congeló exclusivamente objetos `full_direct` no pertenecientes al piloto ni a CN4/CN6. Excluyó los cuatro aliases 2018 y los dos objetos 2008 parciales.

### Cobertura

- 19 libros;
- 3,177 JPEG fuente;
- 3,177/3,177 SHA-256 verificados antes del OCR.

### OCR

- 3,164/3,177 páginas con texto detectable (99.59%);
- 13 `no_text_detected`;
- 0 `unresolved`.

### PAGESTRUCT

- `textual`: 1,459;
- `mixed_text_image`: 1,069;
- `visual_only`: 300;
- `toc_or_navigation`: 118;
- `bibliography_or_credits`: 80;
- `front_matter`: 1;
- `unknown`: 150;
- elegibles para FRAGSEG: 2,528 páginas.

### FRAGSEG

- 36,195 fragmentos;
- 36,195 IDs únicos;
- 2,528/2,528 páginas elegibles con al menos un fragmento;
- `short_residual_candidate`: 18,423;
- `question_candidate`: 5,990;
- `expository_candidate`: 4,897;
- `instruction_candidate`: 4,720;
- `activity_candidate`: 1,096;
- `experiment_candidate`: 446;
- `project_candidate`: 432;
- `assessment_candidate`: 191;
- 80 páginas con huecos legítimos, correspondientes a 97 slots de cero tokens descartados;
- el texto completo no se persiste.

PAGESTRUCT necesitó una recuperación de infraestructura para CN3/2019: se reconstruyó sólo el shard detenido y se reutilizaron los otros 18 artifacts válidos. FRAGSEG quedó idempotente para impedir reprocesamiento accidental una vez materializado `FRAGSEG_CN_WAVE2_0.1`.

## 8. Dependencia documental — hallazgos técnicos

### CN4 1972 ↔ 1988

- 188/214 páginas alineadas byte-idénticas = 87.9%;
- 26 páginas visualmente diferentes concentradas en 1–5, 96–99 y 192–214;
- mediana de similitud textual de las 26 cambiadas: 0.305;
- 94.1% de las ocurrencias de fragmento de CN4/1972 tienen texto exacto presente en CN4/1988;
- 92.1% de CN4/1988 tienen texto exacto presente en CN4/1972.

Interpretación técnica: `massive_page_reuse_with_localized_revision`.

### CN6 dentro de generación 1993

Se conservan dos objetos distintos dentro de `catalog_generation=1993`, uno temprano de *Ciencias Naturales* y otro de reemplazo, *Ciencias Naturales y desarrollo humano*. La generación de catálogo no se convierte en año bibliográfico.

Interpretación: `replacement_within_same_catalog_generation`.

### Ciencias Naturales 2018 ↔ 2019

Los cuatro visores estrictos de 2018 no sirven sus JPEG bajo la clave 2018. La auditoría de enrutamiento identificó las claves 2019 del mismo grado y comparó **652 pares de activos**:

- SHA-256: 652/652 idéntico;
- tamaño: 652/652 idéntico;
- grados 3º, 4º, 5º y 6º: 100% de identidad byte a byte.

Las entradas 2018 se conservan como registros institucionales distintos, pero se modelan como `catalog_entry_aliases_same_asset_bytes` respecto de 2019. No constituyen contenido independiente en la vista de contenido único.

## 9. Vista reversible de contenido único

Sobre los 19,067 fragmentos CN4/CN6:

- 16,155 unidades textuales únicas;
- 1,857 unidades aparecen más de una vez;
- 1,731 unidades aparecen en dos o más libros;
- ratio global de unidades únicas / ocurrencias: 84.7%.

No se elimina ninguna ocurrencia. `content_unit_id` permite alternar entre `object view`, `unique-content view` y `revision view`.

La misma lógica de dependencia deberá gobernar cualquier integración posterior de Ola 2 antes de hacer inferencia histórica agregada.

## 10. Familia completa Ciencias Naturales — readiness de activos

Inventario estricto:

- 37 visores;
- 6,616 posiciones declaradas;
- **35/37 visores (94.6%) con resolución completa de activos**;
- `full_direct`: 31;
- `full_alias_same_bytes`: 4;
- `partial_internal_unserved`: 2;
- `not_resolved`: 0;
- sólo **3 posiciones internas no servidas** persisten.

Los dos objetos parciales son `LTMD-CN3-G2008` (VP94) y `LTMD-CN4-G2008` (VP76 y VP96). Cada posición objetivo permaneció no servida después de cinco intentos, mientras las páginas anterior y posterior reprodujeron sus SHA-256 persistidos. Se clasifican como `internal_unserved_position_observed`, no como “páginas faltantes del libro”.

## 11. Publicación metodológica

Existe ahora:

- `METHODS_ARTICLE_DRAFT_0_1.md`, preservado como primera formulación;
- `METHODS_ARTICLE_DRAFT_0_2.md`, reescrito para la infraestructura escalada;
- verificación ejecutable de cifras del artículo contra artefactos congelados;
- estrategia de dos productos: artículo método/recurso + artículo histórico posterior a SEMB 0.3;
- checklist de primera release científica.

El artículo metodológico puede avanzar antes de SEMB 0.3. El artículo histórico no debe convertir resultados SEMB 0.2 en conclusiones finales.

## 12. Derechos

Política conservadora vigente:

- no versionar masivamente JPEG fuente;
- no publicar OCR íntegro como sustituto de la obra;
- reconstruir temporalmente y verificar SHA antes de procesar;
- publicar metadatos, hashes, métricas, código y derivados no sustitutivos;
- licenciar por separado código/derivados LTMD respecto de materiales fuente.

## 13. Integridad y fallos útiles

El corte de integridad vigente antes de esta actualización era `LTMD_INTEGRITY_0.4`; el siguiente corte debe incorporar explícitamente la auditoría familiar, aliases 2018/2019, evidencia 2008 y Ola 2 cerrada. Los workflows fallan ante cardinalidades, hashes o invariantes inesperadas en vez de corregirlas silenciosamente.

Ejemplos registrados:

- combine B02 fallido y recuperación de shards válidos;
- cardinalidad CN4/CN6 manual errónea rechazada antes de publicar;
- FRAGSEG corregido respecto a gaps de secuencia sin renumerar IDs;
- anomalías 2008/2018 resueltas sólo cuando apareció evidencia específica;
- URLs 2008 inicialmente inferidas se sustituyeron por `CI263` y `CI268` antes de interpretar respuestas;
- runner PAGESTRUCT Ola 2 detenido: recuperación sólo del shard CN3/2019;
- verificador del artículo 0.2 rechazó inicialmente confundir 1,897 posiciones CN4/CN6 con 1,888 JPEG reales, forzando a representar ambas cardinalidades por separado.

Estos fallos forman parte del registro metodológico del proyecto.

## 14. Qué puede seguir haciéndose sin humanos

La ola que antes figuraba como pendiente **ya está terminada**. Sin humanos todavía puede avanzarse en:

- consolidar `LTMD_INTEGRITY_0.5`;
- sincronizar README, índice metodológico y documentación de release;
- ampliar documentación bibliográfica y curricular sin inventar metadatos;
- extender análisis de dependencia documental y contenido duplicado por hashes;
- preparar otras familias disciplinares hasta capas técnicas equivalentes;
- terminar el artículo metodológico y preparar una release científica reproducible.

Sigue bloqueado deliberadamente:

- usar candidatos sintéticos SEMB 0.3 como etiquetas históricas;
- recalibrar modelos mirando diferencias temporales;
- clasificar productivamente Ola 2 con Rule A, SEMB 0.2 o SEMB 0.3 para producir una narrativa histórica;
- producir conclusiones semánticas finales sin referencia humana;
- abrir los 160 `locked_validation` antes de `model_lock`.

## 15. Diagnóstico

LTMD ya posee una infraestructura de corpus de escala sustancial dentro de *Ciencias Naturales*: activos auditados, procedencia criptográfica, OCR técnico, clasificación estructural, segmentación, representación de dependencia documental y 64,856 ocurrencias de fragmento. El cuello de botella ya no es extracción de texto.

El próximo salto científico depende de dos tareas distintas que no deben mezclarse: **cerrar la reproducibilidad documental de este corte** y **obtener referencia humana para SEMB 0.3**. La primera puede completarse ahora; la segunda seguirá gobernando cuándo es legítimo reabrir la inferencia semántica histórica.
