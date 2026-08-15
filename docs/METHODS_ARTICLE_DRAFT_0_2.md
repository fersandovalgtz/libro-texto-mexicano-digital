# Libro de Texto Mexicano Digital: procedencia, dependencia documental y construcción reproducible de un corpus histórico-computacional de libros escolares mexicanos

**Borrador 0.2 — 15 de agosto de 2026**  
**Estado:** manuscrito metodológico de trabajo. Las cifras de infraestructura se derivan de artefactos versionados y verificables del repositorio. Los resultados semánticos históricos permanecen exploratorios; SEMB 0.3 continúa bloqueado a la espera de referencia humana.

## Resumen

Los libros de texto constituyen una fuente central para estudiar la materialización histórica del currículo, pero convertir colecciones digitales institucionales en corpus longitudinales exige resolver problemas que anteceden al análisis lingüístico: identidad documental, arquitectura del visor, procedencia de activos, duplicación editorial, dependencia entre objetos, reconocimiento óptico de caracteres, segmentación, derechos de redistribución y validez de constructo. Este trabajo presenta **Libro de Texto Mexicano Digital (LTMD)** como una infraestructura abierta y reproducible para el estudio histórico-computacional de los Libros de Texto Gratuitos mexicanos. El desarrollo comenzó con un piloto de cuatro volúmenes de *Ciencias Naturales* de quinto grado, asociado a las generaciones de catálogo 1972, 1988, 1993 y 2014, y posteriormente se amplió técnicamente a otros grados y generaciones de la misma familia disciplinar. El piloto contiene 759 imágenes reales y 9,594 fragmentos; una expansión CN4/CN6 añadió 1,888 páginas y 19,067 fragmentos, y una segunda ola técnica incorporó 19 libros, 3,177 páginas fuente y 36,195 fragmentos. En conjunto, las tres capas materializan **64,856 ocurrencias de fragmento**, cifra que deliberadamente no se interpreta como 64,856 observaciones históricas independientes.

La auditoría de la familia estricta *Ciencias Naturales* identificó 37 visores: 31 resuelven sus activos directamente, cuatro entradas de 2018 reutilizan byte a byte 652 activos de 2019, y dos objetos de 2008 conservan sólo tres posiciones internas que el recurso público no sirve. Este resultado obliga a distinguir entre entrada de catálogo, objeto documental, activo digital y unidad de contenido. LTMD preserva esa distinción mediante manifiestos de página, SHA-256, reconstrucción efímera del OCR, PAGESTRUCT, FRAGSEG y vistas reversibles de ocurrencia y contenido único. La Ola 2 verificó 3,177/3,177 SHA antes de OCR, detectó texto en 3,164 páginas (99.59%), clasificó 2,528 páginas como elegibles para segmentación y produjo 36,195 fragmentos con IDs únicos sin persistir transcripciones completas.

El artículo también documenta un resultado metodológico negativo: SEMB 0.2 marcó 99.49% de los fragmentos del piloto como inciertos, y una batería sintética independiente de 105 casos mostró balanced accuracy de 0.526 para su gate. En lugar de recalibrar el sistema observando diferencias históricas, se preregistró SEMB 0.3 con referencia humana ciega, separación desarrollo/validación bloqueada, criterios previos de aceptación y bloqueo criptográfico. El argumento central es que un corpus histórico-computacional defendible no se define por acumular OCR, sino por conservar trazabilidad entre fuente, objeto, transformación y afirmación; representar explícitamente la dependencia documental; y mantener barreras entre ingeniería de corpus, validación semántica e inferencia historiográfica.

**Palabras clave:** libros de texto; historia de la educación; humanidades digitales; corpus históricos; OCR; procedencia; reproducibilidad; dependencia documental; ciencia abierta; México; CONALITEG.

## 1. Introducción

Los libros de texto son simultáneamente objetos editoriales, dispositivos curriculares, artefactos de política educativa y mediadores de prácticas escolares. Su estudio histórico puede mostrar qué conocimientos se seleccionaron, cómo se organizaron, qué actividades se propusieron, qué posiciones se atribuyeron al estudiante y qué relaciones con el saber quedaron inscritas en la materialidad escolar. La continuidad institucional de los Libros de Texto Gratuitos mexicanos ofrece una oportunidad excepcional para construir series históricas de largo plazo.

La disponibilidad digital, sin embargo, no convierte automáticamente una colección en corpus. Un visor web puede declarar posiciones que no corresponden a archivos; distintas entradas de catálogo pueden reutilizar exactamente los mismos activos; una generación de catálogo puede contener objetos bibliográficamente posteriores; dos libros agrupados bajo la misma generación pueden corresponder a sustituciones editoriales; el OCR puede producir señal suficiente para procesamiento sin alcanzar exactitud filológica; y miles de fragmentos pueden ser estadísticamente dependientes porque proceden de páginas o ediciones reutilizadas.

LTMD trata estas dificultades como parte del método y no como inconvenientes periféricos. Su pregunta de infraestructura es sencilla: **para cada observación derivada, ¿puede reconstruirse de qué objeto procede, qué activo la sustenta, qué transformación sufrió y qué evidencia autoriza la interpretación?** Esta pregunta conduce a una arquitectura en capas donde catálogo, fuente, objeto documental, página, fragmento, clasificación y conclusión histórica permanecen conceptualmente separados.

El presente artículo describe esa arquitectura después de pasar de un piloto intensivo a una expansión técnica considerable de la familia *Ciencias Naturales*. El propósito no es presentar todavía una historia automatizada del currículo mexicano. Es mostrar cómo construir una base suficientemente trazable para que las inferencias históricas posteriores puedan ser auditadas y, cuando sea necesario, rechazadas.

## 2. Del catálogo al objeto documental

### 2.1. Generación de catálogo no equivale a año de edición

El piloto inicial seleccionó cuatro volúmenes de *Ciencias Naturales* de quinto grado asociados por el Catálogo Histórico de CONALITEG con las generaciones 1972, 1988, 1993 y 2014. Desde las primeras auditorías se hizo evidente que `catalog_generation` no debía utilizarse como sustituto de `edition_year`, `copyright_year`, edición o ISBN. La generación es una propiedad de agrupación institucional del catálogo; la edición es una propiedad bibliográfica del objeto.

Esta distinción se volvió aún más importante al expandir la familia. Dentro de una misma generación pueden coexistir objetos diferentes; entre generaciones distintas puede existir reutilización extensa; y una entrada de catálogo puede remitir, en la práctica, a activos digitales idénticos a los de otra entrada. Por ello LTMD modela por separado `book_id`, `viewer_key`, generación de catálogo, relaciones documentales y huellas de los activos.

### 2.2. La familia estricta de Ciencias Naturales

El inventario estricto identifica **37 visores** de *Ciencias Naturales* distribuidos en nueve generaciones del catálogo. La auditoría de readiness de activos produjo cuatro estados explícitos: `full_direct`, `full_alias_same_bytes`, `partial_internal_unserved` y `not_resolved`.

Treinta y un visores alcanzaron `full_direct`. Cuatro visores asociados a 2018 no sirvieron sus JPEG bajo la clave 2018, pero el análisis de enrutamiento identificó las claves 2019 del mismo grado. La comprobación posterior comparó **652 pares de activos** y obtuvo identidad de URL fuente, tamaño y SHA-256 en 652/652 casos. En consecuencia, las entradas 2018 permanecen como registros institucionales diferentes, pero se representan como `catalog_entry_aliases_same_asset_bytes` respecto de 2019. No se vuelven a procesar como observaciones de contenido independientes.

Los dos visores restantes corresponden a objetos de 2008. En ellos persisten tres posiciones internas no servidas por el recurso público: una en tercer grado y dos en cuarto. Cada objetivo falló cinco intentos mientras las posiciones inmediatamente vecinas reprodujeron correctamente los SHA-256 esperados. LTMD registra esas posiciones como `internal_unserved_position_observed`. No se las denomina “páginas faltantes del libro”, porque esa afirmación requeriría cotejo bibliográfico independiente.

El resultado general es **35/37 visores con resolución completa de activos, 94.6%**, y ningún visor en estado `not_resolved`. Más importante que el porcentaje es la consecuencia metodológica: un catálogo de 37 entradas no constituye automáticamente una serie de 37 contenidos independientes.

## 3. Reconstrucción de activos y procedencia criptográfica

### 3.1. Del visor a la página

La arquitectura pública observada en los visores históricos permite reconstruir la ruta entre HTML del libro, archivos de configuración y activos JPEG. LTMD no toma el contador visible del visor como evidencia suficiente de cardinalidad. Cada objeto se resuelve a posiciones concretas y se comprueba cuáles corresponden realmente a archivos servidos.

En el piloto CN5, 763 posiciones declaradas correspondieron a **759 imágenes JPEG reales**; cuatro posiciones terminales eran sintéticas. La expansión CN4/CN6 contenía 1,897 posiciones declaradas y **1,888 JPEG reales**, con nueve terminales sintéticos. La Ola 2 se construyó únicamente con objetos `full_direct` no procesados previamente y congeló una cola de **19 libros y 3,177 JPEG**.

### 3.2. SHA-256 como vínculo entre transformaciones

Cada activo fuente utilizado por una etapa intensiva se descarga temporalmente y se verifica contra el SHA-256 persistido antes de procesarse. Esta política separa dos funciones: el repositorio no necesita convertirse en espejo de imágenes fuente para conservar trazabilidad, pero una etapa posterior puede demostrar que operó sobre los mismos bytes previamente auditados.

En Ola 2, los **3,177/3,177 JPEG** superaron esa verificación antes del OCR. La misma lógica se reutilizó cuando PAGESTRUCT necesitó reconstruir páginas estructurales y cuando FRAGSEG reconstruyó las páginas elegibles para segmentación.

### 3.3. Derechos y persistencia mínima

LTMD adopta una política conservadora de datos. No versiona masivamente imágenes fuente ni publica OCR íntegro de los libros como sustituto de la obra. Persiste metadatos, hashes, métricas, código y derivados no sustitutivos. Cuando una operación requiere texto, lo reconstruye de forma efímera y elimina la copia de trabajo después de producir el derivado autorizado por el diseño.

Esta decisión no elimina los problemas jurídicos de las fuentes, pero evita confundir ciencia abierta con redistribución indiscriminada. La reproducibilidad se apoya en procedencia, código, identificadores y huellas, no necesariamente en replicar públicamente cada byte de la obra fuente.

## 4. OCR como señal técnica

### 4.1. Cobertura y exactitud son variables distintas

El OCR se usa primero como capa técnica. En el piloto, 757/759 páginas produjeron señal textual detectable. En CN4/CN6, 1,880/1,888 páginas lo hicieron. En Ola 2, **3,164/3,177 páginas, 99.59%**, presentaron texto detectable; 13 quedaron como `no_text_detected` y ninguna como `unresolved`.

Estas cifras no son CER ni WER. `text_detected` indica que existe señal suficiente bajo el pipeline para tareas técnicas posteriores; no mide por sí mismo fidelidad de caracteres o palabras. La evaluación de precisión requiere referencia humana específica.

### 4.2. OCR adaptativo y no-texto

La heterogeneidad histórica del diseño editorial hace inconveniente una única parametrización rígida. El pipeline evalúa configuraciones de segmentación de página de Tesseract y registra la configuración seleccionada junto con métricas técnicas. Una página sin texto detectable no se convierte automáticamente en “vacía”: puede representar ilustración, diagrama, fotografía, portada u otra función material significativa.

## 5. PAGESTRUCT: función documental antes de semántica

PAGESTRUCT clasifica páginas según función estructural antes de cualquier inferencia pedagógica. Portadas, índices, créditos y páginas predominantemente visuales no deben entrar de manera indiferenciada a conteos de acciones o posiciones del estudiante.

La Ola 2 clasificó sus 3,177 páginas como **1,459 `textual`, 1,069 `mixed_text_image`, 300 `visual_only`, 118 `toc_or_navigation`, 80 `bibliography_or_credits`, 150 `unknown` y 1 `front_matter`**. Las categorías `textual` y `mixed_text_image` dejaron **2,528 páginas elegibles para FRAGSEG**.

PAGESTRUCT es deliberadamente una capa técnica. Una página `textual` no queda por ello validada como unidad pedagógica, y una `visual_only` no se considera irrelevante históricamente. La función del clasificador es reducir contaminación entre paratexto, cuerpo y material visual sin borrar la estructura documental original.

## 6. FRAGSEG y el problema de la unidad de análisis

### 6.1. Del texto de página al fragmento reproducible

FRAGSEG transforma el texto reconstruido en unidades con `fragment_id`, `page_id`, posición, tipo candidato, longitud y huella del texto normalizado. En el piloto produjo **9,594 fragmentos**. En CN4/CN6 produjo **19,067**. La Ola 2 produjo **36,195 fragmentos**, todos con IDs únicos, distribuidos sobre las 2,528 páginas elegibles; ninguna página elegible quedó sin al menos un fragmento.

La composición de Ola 2 fue: 18,423 `short_residual_candidate`, 5,990 `question_candidate`, 4,897 `expository_candidate`, 4,720 `instruction_candidate`, 1,096 `activity_candidate`, 446 `experiment_candidate`, 432 `project_candidate` y 191 `assessment_candidate`.

### 6.2. Secuencias con huecos y no renumeración

FRAGSEG conserva la posición de un candidato antes del descarte de unidades de cero tokens. En Ola 2, 80 páginas presentan huecos legítimos de secuencia correspondientes a 97 slots omitidos. Los IDs no se renumeraron después del descarte. Esta decisión permite reconstruir el proceso y evita que una corrección técnica cambie silenciosamente la identidad de unidades ya derivadas.

### 6.3. El aprendizaje de `heading_candidate`

En el piloto, una auditoría mostró que `heading_candidate` era una denominación excesivamente interpretativa para una regla residual basada en unidades breves. En vez de reescribir retrospectivamente límites e IDs, se creó `FRAGTYPE_0.3_SHADOW`, que preserva unidades y hashes y sustituye la interpretación por `short_residual_candidate`.

El universo potencialmente elegible de fragmentos de cuatro o más tokens pasó de 5,037 a **7,429**, una diferencia de **2,392** unidades. La ampliación productiva quedó condicionada a validación humana. La Ola 2 ya utiliza la nomenclatura más conservadora `short_residual_candidate`, evitando transportar el constructo tipográfico no demostrado.

## 7. De 64,856 ocurrencias a unidades históricas defendibles

La suma de 9,594 fragmentos del piloto, 19,067 de CN4/CN6 y 36,195 de Ola 2 produce **64,856 ocurrencias de fragmento**. Esta cifra describe materialización técnica, no tamaño efectivo de una muestra histórica independiente.

La distinción es necesaria porque el corpus contiene reutilización documental demostrada. En CN4, 1972 y 1988 comparten 188/214 páginas byte-idénticas y presentan reutilización masiva de texto. En CN4/CN6 se construyó una vista reversible de contenido único: 19,067 ocurrencias corresponden a 16,155 unidades textuales únicas; 1,857 unidades aparecen más de una vez y 1,731 aparecen en dos o más libros. Los cuatro visores 2018, por su parte, reutilizan exactamente los activos 2019 y se excluyen de la cola de reprocesamiento.

Por ello LTMD distingue al menos tres perspectivas:

- **object view:** conserva cada ocurrencia dentro de su objeto documental;
- **unique-content view:** agrupa contenido idéntico para evitar inflar recuentos de diversidad textual;
- **revision view:** conserva relaciones entre objetos y localiza continuidad, sustitución o revisión.

Una inferencia histórica puede requerir una u otra vista. Ninguna debe imponerse silenciosamente como si las tres respondieran a la misma pregunta.

## 8. Clasificación pedagógica y resultado negativo de SEMB 0.2

El piloto desarrolló una ontología de acciones pedagógicas y posiciones funcionales del estudiante. Rule A opera mediante reglas explícitas; SEMB 0.2 emplea representación semántica y anchors. La comparación entre ambos métodos fue diseñada para revelar sensibilidad a la operacionalización, no para elegir retrospectivamente el método que produzca la historia más atractiva.

SEMB 0.2 mostró una limitación decisiva: **99.49%** de los fragmentos quedaron globalmente inciertos y sólo 49 cumplieron simultáneamente criterios de certeza de acción y posición. La longitud de los fragmentos no explica por sí sola la incertidumbre.

Una batería sintética independiente de **105 casos** confirmó que el problema no era sólo peculiaridad del corpus histórico. El gate alcanzó balanced accuracy **0.526**, con sensibilidad 0.597 y especificidad 0.455. Estos resultados se publican como resultado metodológico negativo: un sistema puede ser reproducible y, al mismo tiempo, insuficiente para sostener inferencias de constructo.

## 9. SEMB 0.3 y separación entre desarrollo e historia

La respuesta metodológica no fue bajar umbrales después de observar qué categorías aumentaban o disminuían históricamente. Tal procedimiento introduciría leakage y riesgo de selección favorable. En su lugar se diseñó SEMB 0.3 con referencia humana independiente.

La infraestructura prehumana contiene **480 casos**, divididos en **320 casos de desarrollo** y **160 casos de validación bloqueada**. Un subconjunto de **120 casos** se reserva para doble codificación. La muestra cubre **312 páginas** y los casos bloqueados cubren **138**. Los anotadores trabajan con IDs opacos y sin acceso a generación, rol experimental o salida del modelo.

Los criterios de aceptación, el espacio de candidatos y los stage gates se fijaron antes de observar la referencia humana. La secuencia prevista es: fiabilidad humana, consenso/adjudicación de desarrollo, desarrollo del modelo sólo con información permitida, bloqueo criptográfico, una sola apertura de validación y producción únicamente si los criterios preregistrados se superan.

La Ola 2 permanece fuera de esta fase. Está **`corpus_ready` pero no `semantic_ready`**. Ningún resultado de Rule A, SEMB 0.2 o candidato SEMB 0.3 se ha proyectado productivamente sobre sus 36,195 fragmentos para construir una narrativa histórica.

## 10. Workflows, fallos útiles e idempotencia

La reproducibilidad de LTMD no reside sólo en scripts individuales. Los workflows incorporan invariantes que detienen la publicación cuando cardinalidades, hashes o relaciones esperadas cambian. Durante la expansión aparecieron fallos que se conservaron como evidencia del control:

- un combine de SEMB 0.2 falló porque columnas textuales de labels fueron confundidas con columnas binarias; los shards válidos se recuperaron sin repetir la clasificación;
- una cardinalidad inicial errónea de CN4/CN6 fue rechazada antes de publicar;
- FRAGSEG detectó huecos legítimos de secuencia que no debían corregirse renumerando IDs;
- la auditoría familiar expuso primero las anomalías 2008/2018 y sólo cambió su estado cuando apareció evidencia específica;
- un diagnóstico 2008 había inferido URLs incorrectas; se sustituyeron por identificadores reales antes de interpretar los 404;
- en PAGESTRUCT Ola 2, un runner quedó detenido durante la instalación del runtime para CN3/2019. La recuperación reconstruyó únicamente ese shard y reutilizó los 18 artifacts válidos restantes.

FRAGSEG Ola 2 se volvió además idempotente: una vez materializado `FRAGSEG_CN_WAVE2_0.1`, activaciones posteriores deben detenerse antes de recalcular el corpus. La infraestructura busca así evitar tanto la pérdida de trabajo válido como la reproducción innecesaria de contenido ya congelado.

## 11. Integridad científica y versiones del corpus

Los derivados críticos se registran en un manifiesto de integridad que conserva tamaño y SHA-256 y falla si desaparece un artefacto obligatorio. `LTMD_INTEGRITY_0.5` amplía el corte criptográfico para incorporar la resolución de la familia *Ciencias Naturales*, las relaciones 2018↔2019, la auditoría 2008 y la Ola 2 completa desde cola de ingestión hasta FRAGSEG.

El objetivo del manifiesto no es impedir cambios. Un cambio legítimo produce una nueva huella y una nueva versión auditable. Su función es impedir que un resultado, artículo o análisis siga citando silenciosamente un archivo cuya identidad ya cambió.

## 12. Discusión

La expansión de LTMD permite formular cuatro principios metodológicos.

Primero, **catálogo no equivale a corpus**. La entrada institucional es una fuente de metadatos y acceso, pero la unidad analítica requiere resolver el objeto, sus activos y sus relaciones con otras entradas.

Segundo, **más fragmentos no significan automáticamente más evidencia independiente**. La reutilización editorial, las reediciones y los aliases pueden multiplicar ocurrencias sin aumentar proporcionalmente la diversidad documental. Las vistas de contenido único y revisión son necesarias para que el tamaño del dataset no se convierta en una falsa impresión de potencia histórica.

Tercero, **reproducibilidad no equivale a validez**. SEMB 0.2 es reproducible y, precisamente por ello, su fracaso de cobertura puede diagnosticarse con claridad. La validación de constructo exige referencia humana y criterios independientes de los resultados históricos que se desean estudiar.

Cuarto, **la ingeniería del corpus puede avanzar sin adelantar indebidamente la inferencia**. La Ola 2 demuestra que es posible industrializar procedencia, OCR, estructura y segmentación mientras se mantiene bloqueada la capa semántica. Esta separación permite acumular infraestructura sin contaminar el experimento de validación.

## 13. Limitaciones

La familia *Ciencias Naturales* no constituye una muestra probabilística de todos los libros de texto mexicanos ni de toda la producción editorial de CONALITEG. La cobertura de activos se refiere al recurso público observado, no a la completitud bibliográfica absoluta de cada edición física. Las tres posiciones internas 2008 no servidas no autorizan inferir pérdida material del ejemplar. La identidad byte a byte 2018↔2019 prueba reutilización del activo digital, no por sí sola identidad de todas las circunstancias editoriales o institucionales de ambas entradas.

Las métricas OCR de cobertura no sustituyen CER/WER. PAGESTRUCT y FRAGSEG son capas técnicas que requieren validación separada si se desean interpretar sus categorías como constructos históricos. Los 64,856 fragmentos son ocurrencias y no observaciones independientes. Finalmente, las conclusiones semánticas históricas continúan bloqueadas hasta que SEMB 0.3 supere la referencia humana y los criterios preregistrados.

## 14. Conclusión

LTMD ha pasado de un piloto de cuatro libros a una infraestructura histórica-computacional capaz de procesar decenas de objetos documentales sin perder la distinción entre catálogo, activo, objeto y contenido. La familia estricta de *Ciencias Naturales* tiene 35 de 37 visores con activos completamente resueltos; la expansión técnica materializa 64,856 ocurrencias de fragmento; y los procesos de OCR, estructura y segmentación se apoyan en procedencia verificable y reconstrucción efímera.

El avance más importante, sin embargo, no es cuantitativo. El proyecto ha incorporado mecanismos explícitos para reconocer aliases, revisiones, incertidumbre, resultados negativos, fallos de infraestructura y límites de inferencia. Ese diseño transforma un conjunto de páginas digitalizadas en una infraestructura científica: no porque elimine la incertidumbre, sino porque vuelve visible dónde está, qué evidencia la reduce y qué afirmaciones todavía no deben hacerse.

La siguiente frontera no consiste en ejecutar más clasificación automática sobre un corpus mayor. Consiste en completar la referencia humana de SEMB 0.3, bloquear el modelo resultante y sólo después reconstruir la comparación histórica sobre unidades documentales cuya procedencia y dependencia ya están formalmente representadas.

## Nota de reproducibilidad

Las cifras principales de este manuscrito deben permanecer vinculadas a artefactos derivados del repositorio mediante un verificador ejecutable. La publicación formal deberá citar la versión/release y DOI correspondientes al corte utilizado. Las imágenes fuente y el OCR íntegro no forman parte del paquete público de datos cuando su redistribución pueda sustituir a la fuente institucional.

## Referencias

La bibliografía historiográfica, curricular, de humanidades digitales, OCR y validación computacional se integrará en la versión destinada a envío editorial. Este borrador no incorpora referencias no verificadas ni marcadores bibliográficos ficticios.