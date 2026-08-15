# Esqueleto de artículo histórico — LTMD piloto 0.2

Fecha: 2026-08-15

Estado: **reservado hasta completar SEMB 0.3**. Esta versión reemplaza como guía vigente a `ARTICLE_OUTLINE_PILOT_0_1.md`, que se conserva por trazabilidad.

## Título de trabajo

**Continuidad, ruptura y sensibilidad metodológica en la acción pedagógica de los libros mexicanos de Ciencias Naturales de quinto grado, 1972–2014**

El intervalo del título refiere a generaciones documentales del corpus, no a una serie anual continua.

## Pregunta central

¿Cómo cambian las acciones pedagógicas solicitadas al alumno y las posiciones epistemológicas que le atribuyen cuatro libros de Ciencias Naturales de quinto grado pertenecientes a las generaciones documentales 1972, 1988, 1993 —ejemplar de primera edición 1998— y 2014 —tercera edición revisada—, y qué parte de esas diferencias permanece estable bajo especificaciones computacionales validadas?

## Condición para redactar resultados históricos sustantivos

No redactar Resultados 4.2–4.5 ni Discusión como hallazgos históricos finales hasta que:

1. exista referencia humana auténtica;
2. SEMB 0.3 se desarrolle exclusivamente con los 320 casos `development`;
3. el candidato quede criptográficamente bloqueado;
4. supere una única apertura de los 160 `locked_validation` bajo `SEMB03_ACCEPTANCE_0.1`;
5. se aplique al corpus congelado sin modificar criterios;
6. se recalculen acuerdo y transiciones con la capa validada.

SEMB 0.2 y la comparación histórica actual permanecen como evidencia **exploratoria/metodológica**, no como estimador final.

## Aporte esperado

El artículo deberá aportar simultáneamente:

- una reconstrucción histórica-documental que distingue reforma curricular, generación editorial y edición bibliográfica;
- una unidad analítica reproducible a escala de fragmento;
- medición de acciones pedagógicas y posiciones del alumno con referencia humana independiente;
- evaluación explícita de cobertura, incertidumbre y sensibilidad a la especificación;
- una interpretación longitudinal que no confunda acuerdo computacional con verdad histórica.

## Corpus

Cuatro objetos de Ciencias Naturales, quinto grado, Catálogo Histórico CONALITEG:

- `LTMD-CN5-G1972`: generación 1972; `edition_year` no verificado;
- `LTMD-CN5-G1988`: generación 1988; copyright SEP 1977; ISBN 968-29-0758-6; `edition_year` no verificado;
- `LTMD-CN5-G1993`: generación 1993; primera edición verificada 1998; ISBN 970-18-1599-8;
- `LTMD-CN5-G2014`: generación 2014; tercera edición revisada 2014; ISBN 978-607-514-722-2.

## Contexto histórico

Usar como documentos rectores:

- `docs/PRIMARY_SOURCE_REGISTER_0_1.md`;
- `docs/CURRICULAR_CONTEXT_0_2.md`.

Regla: 1988 se denomina **generación documental/editorial** salvo nueva evidencia primaria que demuestre una reforma curricular específica de Ciencias Naturales.

## Método actualizado

### Corpus y procedencia

- 763 posiciones de visor declaradas;
- 759 activos JPEG reales;
- 759 páginas con identidad y procedencia verificadas;
- 757/759 con texto técnico detectado por OCR adaptativo;
- no se distribuye OCR íntegro ni imágenes fuente.

### PAGESTRUCT y FRAGSEG

- PAGESTRUCT 0.2: 759 páginas;
- universo body principal original: 639 páginas;
- FRAGSEG 0.2: 9,594 fragmentos con SHA-256.

La categoría histórica `heading_candidate` se reconoce ahora como residual de segmentación/longitud, no como detector tipográfico validado. `FRAGTYPE_0.3_SHADOW` conserva IDs, límites y hashes y demuestra que, con una regla de elegibilidad no basada en esa etiqueta residual, el universo potencial pasa de 5,037 a 7,429 fragmentos. Su adopción productiva depende de la validación suplementaria predefinida.

### Clasificador A

RULEA 0.1 permanece como especificación interpretable y conservadora. Su papel en el artículo final será una especificación comparativa/robustez, no una referencia de verdad.

### SEMB 0.2 como antecedente metodológico

SEMB 0.2 debe aparecer en Métodos/Limitaciones como un intento bloqueado pre-corpus cuya aplicación produjo 99.49% de incertidumbre. Las pruebas sintéticas independientes posteriores muestran balanced accuracy del gate 0.526 y confirman que el problema no se resuelve bajando un único umbral.

### SEMB 0.3

Diseño preregistrado:

- referencia humana: 480 fragmentos;
- 320 desarrollo + 160 validación bloqueada;
- 120 doble codificación para fiabilidad;
- IDs opacos para anotadores;
- discrepancias requieren adjudicación humana explícita;
- criterios cuantitativos congelados antes de referencia;
- espacio de modelos congelado en `SEMB03_CANDIDATES_0.1`;
- selección con GroupKFold por `page_id`;
- `model_lock` antes de abrir validación;
- validación bloqueada de una sola oportunidad.

Las pruebas sintéticas permiten únicamente priorizar arquitecturas para desarrollo humano: gate multivariable y cabezales híbridos anchor+prototipo. No autorizan producción.

## Estructura del manuscrito

### 1. Introducción

Plantear el libro de texto como artefacto curricular y dispositivo de acción: no sólo qué ciencia presenta, sino qué obliga/invita a hacer al estudiante y qué relación con el conocimiento construye.

Vacío: escasez de comparaciones longitudinales reproducibles que integren historia del currículo, procesamiento computacional y validación independiente a escala de unidad pedagógica.

### 2. Contexto histórico-documental

2.1 Reforma de 1972 y ciencias naturales.

2.2 1988 como problema de continuidad curricular versus renovación editorial.

2.3 Reforma de 1993 y desfase entre reforma normativa y primera edición 1998 del objeto analizado.

2.4 RIEB, quinto grado y tercera edición revisada 2014.

2.5 Distinción analítica: cambio curricular / editorial / pedagógico / bibliográfico.

### 3. Datos y método

3.1 Selección y procedencia del corpus.

3.2 Reconstrucción de visores y auditoría de activos.

3.3 OCR adaptativo y límites.

3.4 PAGESTRUCT.

3.5 FRAGSEG y problema de unidades breves residuales.

3.6 Ontología de acciones y posiciones.

3.7 RULEA.

3.8 Trayectoria SEMB 0.1→0.2 y diagnóstico de fallo.

3.9 Referencia humana y SEMB 0.3.

3.10 Fiabilidad interanotador y adjudicación.

3.11 Validación bloqueada y criterios de aceptación.

3.12 Comparación longitudinal, sensibilidad y dependencia por página.

3.13 Derechos, minimización de redistribución y ciencia abierta mediante derivados no sustitutivos.

### 4. Resultados

#### 4.1 Integridad y composición del corpus

Puede redactarse antes de SEMB 0.3: activos, cobertura OCR, PAGESTRUCT, FRAGSEG, distribución y auditorías.

#### 4.2 Validez del sistema de anotación/clasificación

Sólo después de referencia humana: fiabilidad, desempeño de SEMB 0.3, cobertura, incertidumbre y comparación con RULEA.

#### 4.3 Acciones pedagógicas por generación

Sólo después de SEMB 0.3 productivo.

#### 4.4 Posiciones del alumno por generación

Sólo después de SEMB 0.3 productivo.

#### 4.5 Transiciones robustas y sensibles al método

Reportar resultados del modelo validado y análisis de sensibilidad preregistrados. No rescatar retrospectivamente transiciones de SEMB 0.2 que desaparezcan.

### 5. Discusión

La discusión histórica deberá responder, sin asumir linealidad:

- continuidad 1972→1988;
- magnitud y naturaleza del corte 1988→1993/1998;
- relación entre lenguaje normativo de reformas y acciones efectivas del libro;
- cambios en recepción/ejecución, indagación/razonamiento y agencia social sólo cuando las categorías validadas lo sostengan;
- efecto de decisiones de segmentación y clasificación sobre la narrativa historiográfica.

### 6. Limitaciones obligatorias

- cuatro objetos, un grado y una asignatura;
- generaciones del catálogo no equivalen a años de edición;
- ausencia actual de fuente primaria institucional en línea para el plan SEP 1972, aunque existe copia de consulta y respaldo historiográfico;
- dependencia de fragmentos dentro de páginas/documentos;
- límites de OCR y layout;
- validación humana limitada a una muestra;
- tipos raros con pocos casos bloqueados;
- derechos de los materiales fuente;
- imposibilidad de generalizar a todos los LTG mexicanos sin expansión posterior.

### 7. Conclusión

Distinguir explícitamente entre:

- hallazgo histórico validado;
- sensibilidad metodológica;
- hallazgo documental/bibliográfico;
- implicación para el escalamiento de LTMD.

## Figuras/tablas candidatas

1. Pipeline completo con stage gates humanos.
2. Tabla de los cuatro objetos separando generación, edición y copyright.
3. Diagrama de cobertura: 759 páginas → 9,594 fragmentos → universo elegible → muestra humana.
4. Fiabilidad interanotador y matriz de desempeño SEMB 0.3.
5. Heatmap de estabilidad por categoría.
6. Perfil longitudinal de acciones validadas.
7. Perfil longitudinal de posiciones validadas.
8. Transiciones robustas versus sensibles al método.

## Estado actual de redacción

Puede redactarse ya con rigor: Introducción provisional, Contexto histórico-documental, Datos/Métodos hasta diseño SEMB 0.3 y Resultado 4.1 del corpus. Deben permanecer en reserva los resultados semánticos históricos y la discusión sustantiva hasta superar la validación humana bloqueada.
