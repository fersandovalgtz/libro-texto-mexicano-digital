# Estado consolidado de Libro de Texto Mexicano Digital

Fecha de corte: 2026-08-15

## 1. Estado general

LTMD dejó de ser únicamente un piloto de quinto grado. Actualmente posee:

1. un **piloto CN5** completo desde procedencia hasta una primera capa semántica exploratoria;
2. una **infraestructura SEMB 0.3 prehumana** cerrada y bloqueada correctamente;
3. una **expansión CN4/CN6** técnicamente completa hasta FRAGSEG, sin clasificación semántica productiva;
4. un **catálogo maestro reproducible** de los visores históricos de primaria;
5. una **auditoría de activos de la familia estricta Ciencias Naturales** con 35/37 visores completamente resueltos y sólo tres posiciones internas no servidas en dos objetos 2008;
6. una estrategia de publicación y release separada de la narrativa histórica final.

La principal frontera pendiente para inferencias semánticas históricas es epistemológica: referencia humana y validación de constructo.

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
- resultados históricos SEMB 0.2: **exploratorios**, no finales.

SEMB 0.2 produjo 99.49% de incertidumbre global y sólo 49 fragmentos simultáneamente ciertos en acción y posición. Una batería sintética independiente confirmó que el gate no transporta adecuadamente al lenguaje escolar diverso.

## 3. SEMB 0.3 — infraestructura prehumana cerrada

- 480 casos de referencia humana futura;
- 320 `development`;
- 160 `locked_validation`;
- 120 doble codificación para fiabilidad;
- IDs opacos y plantilla ciega;
- criterios `SEMB03_ACCEPTANCE_0.1` congelados antes de humanos;
- grid `SEMB03_CANDIDATES_0.1` congelado;
- desarrollo con `GroupKFold` por `page_id`;
- model lock criptográfico;
- evaluador de una sola apertura;
- consenso automático sólo para coincidencias exactas;
- desacuerdos requieren adjudicación humana;
- readiness: 16/16 módulos prehumanos materializados;
- etapa: `WAITING_HUMAN_REFERENCE`.

Candidatos sintéticos (no productivos): gate logístico BA 0.631; cabezal híbrido acciones 79.2% top-1; posiciones 77.8% top-1.

## 4. Corrección de FRAGSEG

`heading_candidate` se retiró como interpretación tipográfica. `FRAGTYPE_0.3_SHADOW` conserva límites/IDs/hashes y lo reinterpreta como unidad breve residual.

- elegibles originales SEMB: 5,037;
- elegibles shadow: 7,429;
- recuperables potenciales: 2,392 (+47.5%);
- muestra suplementaria: 160 unidades breves, 100 desarrollo + 60 validación.

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
- 245,141,456 bytes fuente recorridos;
- no se persisten imágenes fuente.

### OCR

- 1,888 páginas procesadas;
- 1,880 con texto detectable (99.58%);
- 8 `no_text_detected`;
- 0 `unresolved`;
- las 8 páginas sin texto muestran contenido visual sustantivo bajo proxies no semánticos.

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
- 34 páginas presentan huecos legítimos de secuencia por descarte de 40 candidatos de 0 tokens; no se renumeraron IDs.

## 7. Dependencia documental — hallazgos técnicos

### CN4 1972 ↔ 1988

- 188/214 páginas alineadas byte-idénticas = 87.9%;
- 26 páginas visualmente diferentes concentradas en 1–5, 96–99 y 192–214;
- mediana de similitud textual de las 26 cambiadas: 0.305;
- 94.1% de las ocurrencias de fragmento de CN4/1972 tienen texto exacto presente en CN4/1988;
- 92.1% de CN4/1988 tienen texto exacto presente en CN4/1972.

Interpretación técnica: `massive_page_reuse_with_localized_revision`.

### CN6 dentro de generación 1993

- objeto temprano: *Ciencias Naturales*, familia históricamente asociada con primera edición 1994;
- objeto de reemplazo: *Ciencias Naturales y desarrollo humano*, página legal recupera primera edición 1999;
- ambos permanecen como objetos distintos dentro de `catalog_generation=1993`.

Interpretación: `replacement_within_same_catalog_generation`.

### Ciencias Naturales 2018 ↔ 2019

Los cuatro visores estrictos de 2018 no sirven sus JPEG bajo la clave 2018. La auditoría de enrutamiento identificó las claves 2019 del mismo grado y una segunda auditoría comparó los **652 pares de activos** con las huellas ya persistidas de 2019:

- URL servida: 652/652 coincide con la URL fuente 2019;
- SHA-256: 652/652 idéntico;
- tamaño: 652/652 idéntico;
- grados 3º, 4º, 5º y 6º: 100% de identidad byte a byte.

Interpretación técnica: las entradas 2018 se conservan como registros institucionales distintos del catálogo, pero se modelan como `catalog_entry_aliases_same_asset_bytes` respecto de 2019. No constituyen observaciones de contenido independientes en la vista de contenido único y esta relación no convierte “2018” en año bibliográfico.

### Señal adicional

CN6/1988 y el objeto temprano CN6/1993 comparten 173 hashes textuales exactos. Se registra como señal de auditoría documental, no como conclusión curricular.

## 8. Vista reversible de contenido único

Sobre los 19,067 fragmentos CN4/CN6:

- 16,155 unidades textuales únicas;
- 1,857 unidades aparecen más de una vez;
- 1,731 unidades aparecen en dos o más libros;
- ratio global de unidades únicas / ocurrencias: 84.7%.

No se elimina ninguna ocurrencia. `content_unit_id` permite alternar entre:

- `object view`;
- `unique-content view`;
- `revision view`.

## 9. Familia completa Ciencias Naturales — readiness de activos

Inventario estricto:

- 37 visores;
- 6,616 posiciones declaradas;
- **35/37 visores (94.6%) con resolución completa de activos**;
- `full_direct`: 31;
- `full_alias_same_bytes`: 4;
- `partial_internal_unserved`: 2;
- `not_resolved`: 0;
- sólo **3 posiciones internas no servidas** persisten en toda la familia auditada.

Los dos objetos parciales son:

- `LTMD-CN3-G2008`: VP94;
- `LTMD-CN4-G2008`: VP76 y VP96.

Cada posición objetivo permaneció no servida después de cinco intentos, mientras las páginas inmediatamente anterior y posterior reprodujeron sus SHA-256 persistidos. Se clasifican como `internal_unserved_position_observed`, no como “páginas faltantes del libro”: una conclusión bibliográfica requeriría cotejo independiente.

La generación 2018 queda completamente resuelta mediante alias byte-idénticos a 2019 y no se vuelve a procesar como contenido independiente.

## 10. Publicación

Existe:

- `METHODS_ARTICLE_DRAFT_0_1.md`;
- esqueleto actualizado del artículo histórico;
- verificación ejecutable de cifras del artículo metodológico;
- estrategia de dos productos: artículo método/recurso + artículo histórico posterior a SEMB 0.3;
- checklist de primera release científica.

El artículo metodológico puede avanzar antes de SEMB 0.3. El artículo histórico no debe convertir resultados SEMB 0.2 en conclusiones finales.

## 11. Derechos

Política conservadora vigente:

- no versionar masivamente JPEG fuente;
- no publicar OCR íntegro como sustituto de la obra;
- reconstruir temporalmente y verificar SHA antes de procesar;
- publicar metadatos, hashes, métricas, código y derivados no sustitutivos;
- licenciar por separado código/derivados LTMD respecto de materiales fuente.

## 12. Integridad

`LTMD_INTEGRITY_0.4` amplió el manifiesto a catálogo, artículo y expansión. Los workflows fallan ante cardinalidades, hashes o invariantes inesperadas en vez de corregirlas silenciosamente.

Ejemplos ya registrados de fallos útiles:

- combine B02 fallido y recuperación de shards;
- cardinalidad CN4/CN6 manual errónea rechazada antes de publicar;
- FRAGSEG combine demasiado estricto respecto a gaps de secuencia, corregido sin renumerar IDs;
- auditoría familiar detectó primero las anomalías 2008/2018 y luego las resolvió por evidencia, sin declarar falsamente corpus completo;
- las URLs 2008 incorrectamente inferidas en una capa de diagnóstico fueron sustituidas por los identificadores reales `CI263` y `CI268` antes de interpretar sus 404.

## 13. Qué puede seguir haciéndose sin humanos

Permitido y científicamente útil:

- llevar a OCR, PAGESTRUCT y FRAGSEG los **19 objetos nuevos `full_direct`** que aún no forman parte del piloto/CN4-CN6;
- procesar los activos 2019 una sola vez y representar 2018 por alias de procedencia, evitando duplicación computacional y estadística;
- decidir una política técnica explícita para los dos objetos 2008 parciales sin rellenar sus tres huecos;
- ampliar documentación bibliográfica y curricular;
- analizar dependencia documental y contenido duplicado por hashes;
- terminar artículo metodológico, release, licencias y reproducibilidad;
- preparar otras familias disciplinares sólo hasta capas técnicas.

Bloqueado deliberadamente:

- usar candidatos sintéticos SEMB 0.3 como etiquetas históricas;
- recalibrar modelos mirando diferencias temporales;
- producir conclusiones semánticas finales sin referencia humana;
- abrir los 160 `locked_validation` antes de `model_lock`.

## 14. Diagnóstico

LTMD ya dispone de suficiente ingeniería para demostrar que el problema central no es extraer más texto. La capa documental de *Ciencias Naturales* está casi completamente resuelta a nivel de activos: 35/37 visores completos y sólo tres posiciones internas no servidas en dos objetos 2008. La siguiente mejora epistemológica de la capa semántica depende de referencia humana real. Mientras esa referencia se obtiene, la expansión técnica puede industrializarse sobre los objetos `full_direct` sin contaminar SEMB 0.3.
