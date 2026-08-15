# Libro de Texto Mexicano Digital: construcción, trazabilidad y validación de un corpus histórico-computacional de libros escolares mexicanos

**Borrador 0.1 — 15 de agosto de 2026**  
**Estado:** manuscrito de trabajo. Las cifras de infraestructura están verificadas en el repositorio; la validación humana SEMB 0.3 permanece pendiente y se describe como diseño, no como resultado consumado.

## Resumen

Los libros de texto constituyen una fuente privilegiada para estudiar la materialización histórica del currículo, pero su análisis longitudinal a gran escala plantea problemas de procedencia, comparabilidad documental, reconocimiento óptico de caracteres, segmentación, derechos de redistribución y validez de las inferencias computacionales. Este trabajo presenta **Libro de Texto Mexicano Digital (LTMD)**, una infraestructura abierta y reproducible para el estudio histórico-computacional de los Libros de Texto Gratuitos mexicanos. El piloto se construyó con cuatro volúmenes de *Ciencias Naturales* de quinto grado agrupados por el Catálogo Histórico de la Comisión Nacional de Libros de Texto Gratuitos en las generaciones 1972, 1988, 1993 y 2014. La arquitectura pública de los visores fue reconstruida y auditada: 763 posiciones declaradas corresponden a 759 imágenes JPEG reales, de las cuales 757 produjeron texto técnicamente detectable mediante un pipeline OCR adaptativo. Una capa de clasificación estructural de páginas (PAGESTRUCT 0.2) y una segmentación reproducible (FRAGSEG 0.2) generaron 9,594 fragmentos con identificadores y hashes SHA-256. El proyecto evita redistribuir de forma indiscriminada imágenes u OCR completo: persiste metadatos, hashes, código y derivados no sustitutivos, y reconstruye temporalmente el texto cuando una etapa analítica lo requiere. Como caso de estudio sobre validez computacional, se documenta el desarrollo y fracaso de cobertura de un clasificador semántico preespecificado (SEMB 0.2): 99.49% de los fragmentos quedaron marcados como inciertos. Una batería sintética independiente de 105 casos confirmó un problema de calibración del gate (balanced accuracy 0.526), mostrando por qué la consistencia algorítmica no debe confundirse con validez histórica. En respuesta, se preregistró SEMB 0.3 con 480 unidades para referencia humana ciega, separación 320/160 entre desarrollo y validación bloqueada, doble codificación, criterios de aceptación previos, selección agrupada por página y bloqueo criptográfico antes de una única apertura de validación. LTMD propone así un modelo de edición histórico-digital que integra procedencia, ciencia abierta, resultados negativos y stage gates de validación, y que puede ampliarse a otros grados y asignaturas sin convertir el corpus fuente en un repositorio de copias no autorizadas.

**Palabras clave:** libros de texto; historia de la educación; humanidades digitales; procesamiento de lenguaje natural; OCR; ciencia abierta; reproducibilidad; México; CONALITEG.

## 1. Introducción

Los libros de texto son simultáneamente objetos editoriales, dispositivos curriculares, artefactos de política educativa y mediadores de prácticas escolares. Su estudio histórico permite observar no sólo qué contenidos fueron considerados enseñables en diferentes periodos, sino cómo se organizaron los saberes, qué actividades fueron propuestas, qué posiciones se asignaron a docentes y estudiantes y qué formas de relación con el conocimiento quedaron inscritas en la materialidad del libro. En México, la continuidad institucional de los Libros de Texto Gratuitos ofrece una oportunidad especialmente importante para construir series históricas comparables.

La disponibilidad digital, sin embargo, no convierte automáticamente una colección histórica en un corpus computacional. Un visor web puede representar las páginas mediante recursos separados, contener posiciones sintéticas o depender de JavaScript; el año bajo el que un catálogo agrupa un libro puede no coincidir con el año bibliográfico de la edición; la calidad del OCR puede variar entre periodos por tipografía, diseño e impresión; una página no equivale necesariamente a una unidad pedagógica; y una clasificación automática con aparente coherencia interna puede fallar cuando se traslada al lenguaje real del corpus. A ello se añade un problema jurídico y de ciencia abierta: reproducibilidad no equivale necesariamente a redistribución irrestricta de las fuentes.

LTMD fue diseñado para tratar esos problemas como parte constitutiva del método. El objetivo no es únicamente obtener una base de datos de textos escolares, sino crear una cadena auditable que permita responder, para cada observación derivada, **de qué objeto procede, cómo se obtuvo, qué transformación sufrió y qué grado de evidencia sostiene la inferencia final**.

El presente artículo describe la arquitectura y las decisiones metodológicas del piloto. Se concentra deliberadamente en la construcción del corpus, control de procedencia, OCR, estructura, segmentación, validación computacional y gobierno de datos. Los resultados históricos sustantivos sobre cambios en acciones pedagógicas y posiciones del alumno se reservan para una fase posterior condicionada a validación humana independiente. Esta separación es central: permite publicar la infraestructura y los resultados metodológicos negativos sin convertir un clasificador todavía insuficientemente validado en argumento historiográfico.

## 2. Diseño del piloto y selección documental

### 2.1. Cuatro objetos, no cuatro “años” equivalentes

El piloto utiliza cuatro volúmenes de *Ciencias Naturales* de quinto grado que el Catálogo Histórico de CONALITEG agrupa bajo las generaciones 1972, 1988, 1993 y 2014. La variable `catalog_generation` se conserva como dato documental del catálogo y se mantiene separada de `edition_year`, `copyright_year`, edición e ISBN.

Esta distinción resultó necesaria desde las primeras auditorías. El ejemplar de la generación 1993 contiene en su página legal una primera edición de **1998**, ISBN 970-18-1599-8. El de la generación 2014 corresponde a una **tercera edición revisada de 2014**, precedida por primera edición 2010 y segunda edición 2011, ISBN 978-607-514-722-2. El objeto etiquetado en la generación 1988 presenta copyright SEP 1977 e ISBN 968-29-0758-6, pero no ofrece evidencia suficiente para asignar 1988 como año de edición. En el objeto 1972 se detectan señales de copyright y marcador de edición, pero el año bibliográfico de edición permanece sin poblar por falta de una indicación inequívoca.

Por esta razón, las generaciones se tratan como **cortes documentales/editoriales del catálogo**, no como cuatro observaciones cronológicas homogéneas. El análisis histórico posterior deberá separar cambio curricular, cambio editorial y cambio bibliográfico del ejemplar.

### 2.2. Justificación disciplinar

*Ciencias Naturales* de quinto grado se eligió como caso intensivo porque permite observar una amplia gama de operaciones pedagógicas potencialmente distinguibles: observación, descripción, comparación, clasificación, medición, experimentación, investigación, inferencia, explicación, resolución de problemas, discusión, producción y toma de decisiones. El quinto grado se encuentra además en la primaria superior, donde las consignas tienden a ser suficientemente extensas para un análisis textual y donde las reformas curriculares de distintos periodos dejaron objetos documentales comparables.

El piloto no es una muestra probabilística de todos los libros de texto mexicanos. Es un estudio de cuatro objetos documentales cuidadosamente auditados cuyo propósito inicial es desarrollar y someter a prueba una arquitectura replicable.

## 3. Reconstrucción de la fuente digital

### 3.1. Del visor al activo de página

Los cuatro objetos utilizan la misma arquitectura pública observada en el Catálogo Histórico:

`HTML del libro → x.js → claves.json → magazine.js → /c/{clave}/{archivo}.jpg`

El nombre del HTML identifica la clave del visor. En el piloto las claves son `H1972P5CI084`, `H1988P5CI123`, `H1993P5CI200` y `H2014P5CNA`. `claves.json` proporciona, entre otros parámetros, el número de posiciones declarado para cada visor. La lógica de `magazine.js` construye las imágenes mediante una ruta JPEG por página.

La reconstrucción mostró una diferencia entre posiciones de visor y activos reales. Los cuatro visores declaran en conjunto **763 posiciones**, pero las posiciones terminales de cada volumen son sintéticas y no corresponden a JPEG. El corpus fuente real está compuesto por **759 imágenes de página**.

Esta auditoría evita un error aparentemente menor pero metodológicamente importante: asumir que el contador del visor equivale al número de archivos fuente. En LTMD, `viewer_page`, índice de imagen y foliación impresa son variables distintas.

### 3.2. Manifiesto de procedencia

Cada página se representa mediante un identificador estable, clave del libro, generación del catálogo, posición en el visor, URL técnica observada y metadatos de disponibilidad. Los activos necesarios para procesamiento pueden descargarse como copias temporales de trabajo, pero el repositorio público conserva principalmente metadatos, hashes y resultados derivados.

La procedencia se trata como una propiedad verificable, no como una nota narrativa. Las etapas posteriores pueden reconstruir temporalmente una página y comprobar que el texto o la unidad derivada corresponde al hash esperado.

## 4. OCR como capa técnica, no como sustituto editorial

### 4.1. Pipeline adaptativo

El corpus presenta heterogeneidad visual entre generaciones: composición tipográfica, ilustraciones, densidad textual y diagramación varían de forma sustantiva. Por ello se desarrolló un pipeline OCR adaptativo que evalúa diferentes configuraciones de Tesseract y persiste métricas técnicas por página, no necesariamente la transcripción completa.

De las 759 imágenes reales, **757** obtuvieron estado técnico de texto detectado bajo los criterios del pipeline, equivalente a 99.74%. Las dos restantes fueron tratadas mediante auditorías específicas de páginas sin texto o predominantemente visuales; la ausencia de OCR utilizable no se convirtió automáticamente en “página vacía”.

### 4.2. Límites de la cifra de cobertura

El 99.74% no debe interpretarse como 99.74% de exactitud de caracteres. Indica que el pipeline recuperó suficiente señal textual para continuar el procesamiento técnico en 757 páginas. La evaluación CER/WER requiere referencia humana de transcripción y se mantiene conceptualmente separada de la métrica de cobertura.

Esta separación evita presentar disponibilidad de texto como precisión lingüística. Las métricas OCR se utilizan para localizar páginas difíciles, evaluar truncamiento y documentar cobertura, mientras que cualquier evaluación de exactitud debe especificar su referencia.

### 4.3. Política de persistencia

El proyecto no publica de manera indiscriminada el OCR íntegro de los libros. Cuando una tarea analítica requiere texto, éste puede reconstruirse temporalmente a partir de la página fuente. Los derivados públicos se diseñan para ser auditables sin convertirse en copias sustitutivas de la obra original.

## 5. PAGESTRUCT: separar función documental antes de segmentar

La página constituye una unidad física útil para procedencia, pero no todas las páginas desempeñan la misma función. Portadas, páginas legales, índices y paratextos no deben tratarse automáticamente como cuerpo pedagógico. PAGESTRUCT 0.2 clasifica las 759 páginas en funciones estructurales antes de la segmentación semántica.

La clasificación estructural cumple dos objetivos. Primero, evita que títulos editoriales, índices o créditos entren sin control a conteos de actividad pedagógica. Segundo, conserva esas páginas como objetos documentales analizables para estudios bibliográficos y editoriales. Excluir del análisis semántico no equivale a eliminar del corpus.

## 6. FRAGSEG: de página a unidad pedagógica reproducible

### 6.1. Manifiesto congelado

FRAGSEG 0.2 se aplicó a las páginas de cuerpo seleccionadas y produjo **9,594 fragmentos**. Cada unidad conserva `fragment_id`, `page_id`, generación, posición dentro de la página, tipo candidato, longitud y SHA-256 del texto normalizado utilizado por las etapas analíticas.

La persistencia del hash permite separar dos exigencias que suelen confundirse: no es necesario publicar la transcripción extensa para poder comprobar posteriormente que una clasificación se realizó sobre la misma unidad textual.

### 6.2. El error útil de `heading_candidate`

Una auditoría posterior reveló una decisión de nomenclatura excesiva. FRAGSEG 0.2 etiquetaba como `heading_candidate` una categoría residual compuesta principalmente por unidades breves, sin emplear evidencia tipográfica suficiente para afirmar que fuesen encabezados reales.

La frecuencia de esa categoría aumentaba fuertemente entre generaciones, lo que habría permitido construir una narrativa histórica espuria sobre “más encabezados” en libros recientes. Se realizaron dos controles. Primero, se examinó su distribución por generación, página y longitud. Segundo, se reconstruyó temporalmente una muestra determinista de **160 fragmentos** —20 `heading_candidate` y 20 `expository_candidate` por generación— y se extrajeron proxies geométricos del OCR. La altura relativa mediana de los candidatos a encabezado fue cercana a 1.0 respecto del texto circundante; el uso dominante de mayúsculas fue excepcional y una proporción considerable presentó puntuación terminal. No apareció una firma tipográfica suficientemente consistente para sostener la interpretación original.

En lugar de resegmentar retrospectivamente el corpus, se construyó `FRAGTYPE_0.3_SHADOW`, que **preserva límites, IDs y hashes** y reinterpreta la etiqueta como `short_residual_candidate`. Si la elegibilidad semántica se separa de esa categoría residual y se mantiene un mínimo de cuatro tokens, el universo potencialmente elegible pasa de **5,037 a 7,429 fragmentos**, un incremento de 2,392 unidades (47.5% respecto del universo anterior). La adopción productiva de ese universo ampliado queda condicionada a una muestra suplementaria ciega de 160 unidades breves.

Este episodio se conserva como resultado metodológico, no se oculta como “error de implementación”: muestra cómo una etiqueta computacional aparentemente inocua puede transformarse en un constructo histórico no validado.

## 7. Ontología pedagógica y clasificación en dos especificaciones

El piloto distingue dos familias de variables: **acciones pedagógicas** solicitadas o atribuidas al estudiante y **posiciones** que describen su relación funcional con el conocimiento. El codebook incluye, entre otras, observar, describir, explicar, comparar, clasificar, medir, experimentar, investigar, predecir, inferir, discutir, resolver, crear y decidir; y posiciones como receptor, seguidor de instrucciones, observador, experimentador, investigador, razonador, colaborador, tomador de decisiones y agente comunitario.

Se desarrollaron dos aproximaciones computacionales independientes. RULEA 0.1 utiliza reglas explícitas e interpretables. SEMB explora representación semántica mediante embeddings y anchors en español. Ninguna de las dos se considera por definición una referencia de verdad.

El objetivo de mantener especificaciones distintas es permitir análisis de sensibilidad: una diferencia histórica que sólo existe bajo una operacionalización puede ser metodológicamente informativa, pero debe distinguirse de una señal estable entre métodos.

## 8. SEMB 0.2: por qué se publica un resultado negativo

### 8.1. Diseño

SEMB 0.2 utiliza `intfloat/multilingual-e5-small` con revisión fijada, anchors semánticos, un gate de acción, reglas multilabel y márgenes de incertidumbre. El sistema fue desarrollado y bloqueado antes de aplicarse al corpus histórico, precisamente para reducir la posibilidad de ajustar parámetros hasta obtener una narrativa temporal atractiva.

### 8.2. Fallo de cobertura en corpus

La ejecución completa mostró que **99.49% de los 9,594 fragmentos** quedaban globalmente marcados como inciertos. En el universo de 5,037 unidades elegibles bajo la regla original, el gate/buffer de acción bloqueaba 89.16% y el margen de posición 74.83%; sólo **49 fragmentos** cumplían simultáneamente los criterios de certeza de ambas dimensiones.

La longitud no explicaba por sí sola el problema: la incertidumbre permanecía extremadamente alta en intervalos sustantivos de tokens. Por ello, reducir el fenómeno a “fragmentos demasiado cortos” habría sido incorrecto.

### 8.3. Batería sintética independiente

Para distinguir entre un problema exclusivo del corpus histórico y una deficiencia más general del mecanismo de decisión, se creó después una batería de **105 casos sintéticos educativos en español** que no contiene texto histórico: 48 casos claros centrados en acciones, 27 centrados en posiciones y 30 negativos difíciles, incluidos enunciados donde vocabulario como “observar”, “comparar” o “investigar” aparece sin constituir una instrucción al alumno.

El SEMB 0.2 ya estaba congelado cuando se creó esta batería. Su gate obtuvo **balanced accuracy 0.526**, sensibilidad 0.597 y especificidad 0.455. En los negativos de estrés la tasa de falsos positivos fue 53.3%; en los positivos, 94.4% no logró superar el buffer de certeza. Los anchors aislados conservaron señal parcial —75.0% top-1 para acciones y 63.0% para posiciones—, sugiriendo que el cuello de botella no podía atribuirse únicamente al espacio de representación.

Publicar este resultado negativo cumple una función epistemológica. Si el proyecto hubiera rebajado a posteriori los umbrales hasta obtener más cobertura, la comparación histórica resultante habría estado condicionada por conocimiento del corpus. En cambio, SEMB 0.2 se conserva como intento fallido y sus resultados históricos se mantienen explícitamente exploratorios.

## 9. SEMB 0.3: stage gates antes de la referencia humana

### 9.1. Muestra

Antes de observar anotaciones humanas se congeló una muestra de **480 fragmentos**, 120 por generación. Mediante asignación determinista por hash se separaron **320 casos de desarrollo** y **160 casos de validación bloqueada**. Los identificadores presentados a anotadores son opacos y la plantilla ciega no revela generación, rol development/locked, `fragment_id`, `page_id`, tipo candidato ni resultados automáticos.

Un subconjunto de **120 casos** está reservado para doble codificación interanotador. Los desacuerdos no se resuelven mediante votación automática de algoritmos: requieren adjudicación humana explícita.

La muestra principal abarca **312 páginas distintas** y la validación bloqueada 138. La mediana de longitud es 16 tokens frente a 15 en el universo elegible, aunque existen tipos funcionales raros con escasa representación y por ello no se preregistran inferencias finas por todos los estratos.

### 9.2. Criterios de aceptación congelados

Los umbrales de desempeño, cobertura e incertidumbre fueron fijados antes de la referencia humana. La validación no se limita a F1 o accuracy: un modelo que clasifique correctamente una fracción pequeña y declare incierto casi todo el resto no será considerado suficiente para reconstruir tendencias históricas. El evaluador incluye controles de proporción de salidas ciertas, diferencias de incertidumbre entre generaciones y truncamiento.

### 9.3. Espacio de modelos preregistrado

También antes de observar etiquetas humanas se congelaron las familias de arquitecturas candidatas y sus grids. La selección sobre los 320 casos de desarrollo utilizará `GroupKFold` agrupado por `page_id`, evitando que fragmentos de una misma página aparezcan simultáneamente en entrenamiento y validación interna.

Pruebas sintéticas posteriores al diagnóstico de SEMB 0.2 se utilizan únicamente para priorizar candidatos, no como validación del nuevo sistema. Un gate logístico de baja dimensionalidad elevó la balanced accuracy sintética a 0.631 frente a 0.526 del gate antiguo; cabezales híbridos anchor+centroide alcanzaron 79.2% top-1 en acciones y 77.8% en posiciones. Estos valores están marcados como `PROVISIONAL_SYNTHETIC_ONLY` y deberán volver a compararse usando exclusivamente el conjunto humano de desarrollo.

### 9.4. Bloqueo y única apertura

Una vez seleccionado el candidato con desarrollo humano, código, parámetros, criterios y artefactos de resultado se congelarán mediante hashes. El evaluador de los 160 casos bloqueados se niega a correr sin un `model_lock` válido y se niega a sobrescribir un resultado de validación existente. El diseño implementa técnicamente una única oportunidad de prueba, no sólo una declaración de buenas intenciones.

## 10. Gobierno de datos, derechos y reproducibilidad

### 10.1. Ciencia abierta sin redistribución indiscriminada

LTMD distingue fuente, copia temporal de trabajo y dato derivado. Los derechos de los materiales originales permanecen con sus titulares. El repositorio evita convertir la infraestructura científica en un espejo de los libros: no distribuye sistemáticamente los JPEG fuente ni el OCR completo.

En cambio, publica o prepara para publicación:

- inventarios y metadatos bibliográficos;
- claves y URLs de procedencia;
- manifiestos de páginas y fragmentos;
- hashes;
- esquemas y codebooks;
- código de reconstrucción y análisis;
- métricas OCR y estructurales;
- etiquetas derivadas cuando su publicación sea metodológicamente y jurídicamente apropiada;
- protocolos, criterios y resultados de validación;
- bitácoras de decisiones y fallos.

Este patrón permite que otro investigador compruebe la cadena de transformación accediendo legítimamente a la fuente pública, sin que el repositorio entregue una copia sustitutiva del libro.

### 10.2. Integridad criptográfica

Los artefactos críticos del piloto se incorporan a un manifiesto que conserva tamaño y SHA-256. La desaparición de un archivo requerido hace fallar el workflow y cualquier modificación legítima genera una nueva huella. El manifiesto cubre corpus congelado, protocolos, criterios, scripts críticos y documentación analítica.

La infraestructura dispone además de CI para comprobar sintaxis, invariantes de muestra y comportamiento de los stage gates con datos ficticios que no pueden confundirse con la referencia científica.

## 11. Resultados metodológicos del piloto

El piloto permite establecer, antes de cualquier conclusión histórica final, cinco resultados metodológicos.

Primero, un visor histórico puede reconstruirse de manera reproducible a nivel de activo sin asumir que su contador corresponde uno a uno con archivos reales. La diferencia 763/759 habría pasado inadvertida con una extracción ingenua.

Segundo, es posible alcanzar cobertura OCR técnica casi completa manteniendo separada la evaluación de disponibilidad de texto de la exactitud de transcripción.

Tercero, la unidad analítica debe ser versionada y auditable. El caso `heading_candidate` muestra el riesgo de transformar una heurística residual en un constructo historiográfico. Preservar los mismos fragmentos y crear una capa shadow permitió corregir interpretación sin borrar la trayectoria metodológica.

Cuarto, preespecificar un modelo antes de observar el corpus no garantiza validez externa. SEMB 0.2 pasó su desarrollo sintético original pero produjo una cobertura prácticamente nula en el lenguaje histórico real. El resultado negativo justifica una referencia humana y criterios que penalizan la incertidumbre excesiva.

Quinto, los mecanismos de prevención de leakage y ajuste retrospectivo pueden implementarse en software: muestras opacas, particiones por hash, grids congelados, `GroupKFold` por página, model lock, una única apertura de validación y manifiestos de integridad reducen grados de libertad analíticos que de otro modo quedarían sólo documentados en prosa.

## 12. Discusión

### 12.1. Del corpus digital al argumento histórico

La principal propuesta de LTMD es que la construcción del corpus no constituye una etapa neutral previa al análisis. Decisiones sobre equivalencia bibliográfica, inclusión de páginas, OCR, segmentación y certeza de clasificación forman parte del argumento histórico porque determinan qué evidencia puede ser contada.

Esto es especialmente relevante en comparaciones temporales. Si un algoritmo segmenta libros recientes en más unidades breves que libros antiguos y esas unidades son etiquetadas automáticamente como encabezados, una diferencia técnica puede aparecer como cambio editorial. Si un clasificador presenta distinta incertidumbre entre generaciones, la comparación de prevalencias puede reflejar cobertura desigual en lugar de transformación pedagógica. Las auditorías deben acompañar, no suceder incidentalmente, a la interpretación histórica.

### 12.2. Resultados negativos como infraestructura científica

El fracaso de cobertura de SEMB 0.2 no constituye tiempo perdido. Al mantenerse versionado, permite identificar una fuente de error que sería invisible si sólo se publicara el modelo exitoso final. También fuerza una mejora del diseño: separar desarrollo y validación humanos, establecer criterios de cobertura y construir controles que impidan usar los resultados históricos como función de ajuste.

En humanidades digitales e historia cuantitativa, donde los conjuntos anotados suelen ser pequeños y las decisiones de operacionalización numerosas, esta transparencia puede ser tan importante como una mejora marginal de accuracy.

### 12.3. Escalabilidad disciplinada

La arquitectura puede ampliarse antes de que SEMB 0.3 esté validado, pero sólo en capas que no dependan de clasificación semántica: inventario, procedencia, activos, OCR, estructura, segmentación y bibliografía. El plan de expansión comienza con Ciencias Naturales de cuarto y sexto grados en generaciones comparables. Sólo después se propone pasar a otras asignaturas, porque la ontología pedagógica puede no transferir intacta entre dominios.

La distinción entre `corpus_ready` y `semantic_ready` evita que disponibilidad técnica se confunda con validez analítica.

## 13. Limitaciones

El piloto contiene cuatro objetos de una asignatura y grado; no representa estadísticamente al conjunto de Libros de Texto Gratuitos. Las generaciones del Catálogo Histórico no equivalen necesariamente a años de edición. El OCR tiene cobertura técnica alta pero la exactitud de caracteres no está establecida para toda la colección mediante referencia humana. PAGESTRUCT y FRAGSEG son clasificadores/heurísticas versionados y sujetos a revisión. La muestra humana prevista para SEMB 0.3, aunque estratificada y distribuida entre páginas, contiene pocos casos de algunos tipos raros. La dependencia entre fragmentos de una misma página exige procedimientos agrupados de validación e incertidumbre. Finalmente, la política de no redistribuir fuentes completas mejora prudencia jurídica pero impone que la replicación total dependa de la disponibilidad futura de los recursos de CONALITEG.

## 14. Conclusiones

LTMD demuestra que un corpus histórico-computacional de libros escolares puede construirse como una infraestructura de evidencia y no únicamente como una colección de transcripciones. En el piloto, 759 páginas fuente reales fueron convertidas en una cadena reproducible de estructura y 9,594 unidades fragmentarias sin perder la trazabilidad hacia el objeto original. Las auditorías revelaron dos problemas que una pipeline orientada sólo a producir resultados habría podido ocultar: una categoría de segmentación sobrerinterpretada y un clasificador semántico con cobertura insuficiente.

La respuesta metodológica fue conservar esos fallos, ampliar los controles y preregistrar una validación humana bloqueada antes de reconstruir la narrativa histórica. El siguiente paso epistemológico no es generar más etiquetas automáticas, sino demostrar que las categorías computacionales corresponden a juicios humanos reproducibles y que su cobertura permite comparaciones entre documentos temporalmente heterogéneos.

La infraestructura resultante es extensible. Su contribución más general es un principio de trabajo para colecciones históricas digitalizadas: **procedencia antes que volumen, versionado antes que corrección silenciosa, validación antes que narrativa y reproducibilidad sin asumir que ciencia abierta exige redistribuir íntegramente las fuentes**.

## Disponibilidad de código y datos

Código, protocolos, metadatos, manifiestos y derivados publicables se mantienen en el repositorio `fersandovalgtz/libro-texto-mexicano-digital`. Una versión archivada y citable deberá asociarse a una release estable y DOI. Los materiales fuente permanecen en los servicios de sus titulares; el repositorio documenta su procedencia y las transformaciones reproducibles sin pretender transferir sus derechos.

## Material suplementario previsto

- S1. Inventario bibliográfico del piloto.
- S2. Manifiesto de páginas y auditoría de 759 activos.
- S3. Métricas OCR por página.
- S4. Especificación PAGESTRUCT.
- S5. Especificación FRAGSEG y auditoría de unidades breves.
- S6. Codebook de acciones y posiciones.
- S7. Diagnóstico completo SEMB 0.2 y batería sintética.
- S8. Protocolo SEMB 0.3, criterios de aceptación y grid de candidatos.
- S9. Manifiesto de integridad SHA-256.
- S10. Registro de fuentes históricas y evidencia bibliográfica.

## Referencias de trabajo

La bibliografía formal se normalizará según la revista objetivo. En esta fase deben incorporarse al menos:

- Comisión Nacional de Libros de Texto Gratuitos. *Catálogo Histórico de Libros de Texto Gratuitos*.
- Estrada Rebull, M. del M. (2021). “Ciencias naturales en primaria en los años setenta en México: ¿Una reforma entre revoluciones?”. *Revista Mexicana de Historia de la Educación*, 9(18), 60–82. https://doi.org/10.29351/rmhe.v9i18.353
- Secretaría de Educación Pública. Acuerdo 181 por el que se establecen el plan y los programas de estudio para la educación primaria, 1993.
- Secretaría de Educación Pública. Acuerdo 540, 2010.
- Secretaría de Educación Pública. Acuerdo 592, 2011.

---

### Nota interna de cierre de borrador 0.1

Este manuscrito puede continuar hasta un borrador de envío **sin** completar resultados históricos SEMB 0.3. Antes de someterlo conviene: seleccionar revista, normalizar referencias, decidir licencia de código/derivados, actualizar DOI/release, incorporar un diagrama reproducible del pipeline y decidir si los resultados finales de fiabilidad SEMB 0.3 se incluyen como validación adicional del recurso o se reservan íntegramente para el artículo histórico.
