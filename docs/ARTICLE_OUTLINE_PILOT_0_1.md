# Esqueleto de artículo — LTMD piloto 0.1

Fecha: 2026-08-15

## Título de trabajo

**Continuidad y ruptura en la acción pedagógica de los libros mexicanos de Ciencias Naturales: un análisis computacional longitudinal de quinto grado**

Título provisional. No debe presentarse como definitivo hasta cerrar la lectura historiográfica de los derivados.

## Pregunta central

¿Cómo cambia la concepción de aprender ciencias expresada en las acciones solicitadas al alumno y en las posiciones pedagógicas que le atribuyen los libros de Ciencias Naturales de quinto grado pertenecientes a las generaciones documentales 1972, 1988, 1993/edición 1998 y 2014?

## Aporte esperado

El artículo no pretende comparar únicamente frecuencia de “actividades”. El aporte es reconstruir longitudinalmente:

1. qué operaciones cognitivas/epistémicas solicita el texto;
2. qué posición atribuye al alumno frente al conocimiento científico;
3. qué transformaciones son estables bajo dos especificaciones computacionales independientes;
4. qué diferencias dependen del método de clasificación y deben considerarse metodológicamente sensibles.

## Corpus

Cuatro libros de Ciencias Naturales, quinto grado, Catálogo Histórico CONALITEG:

- generación 1972;
- generación 1988;
- generación 1993, obra piloto con primera edición bibliográfica verificada en 1998;
- generación 2014, tercera edición revisada 2014.

Regla bibliográfica: nunca equiparar automáticamente `catalog_generation` con `edition_year`.

## Diseño metodológico

### Fuente y extracción

- arquitectura del visor CONALITEG reconstruida;
- 763 páginas estructurales de visor;
- 759 JPEG fuente reales;
- trazabilidad por `book_id` / `page_id` / URL de activo.

### OCR

Tesseract español 5.3.4, `OMP_THREAD_LIMIT=1`, pipeline adaptativo:

1. `psm 3` basal;
2. ante cero palabras/fallo, `psm 11` y `psm 6`;
3. fallback válido con ≥5 palabras;
4. elegir fallback con mayor conteo.

Resultado técnico: 757/759 activos aceptados como `text_detected`, dos `no_text_detected`. El artículo debe aclarar que esta cobertura no equivale a páginas realmente textuales porque se comprobaron falsos positivos OCR sobre fotografías.

### Clasificación estructural

PAGESTRUCT 0.2 sobre 759/759 páginas. Universo principal body-only: 639 páginas `textual` o `mixed_text_image`. Páginas visuales, navegación, bibliografía/créditos y `unknown` se separan del análisis pedagógico principal.

### Segmentación

FRAGSEG 0.2:

- 639/639 páginas;
- 9,594 fragmentos;
- 0 fallos finales;
- sin texto público;
- identidad reproducible mediante `fragment_id` + SHA-256.

### Libro de códigos conceptual

16 acciones:

`observe, describe, recall, explain, compare, classify, measure, experiment, investigate, predict, infer, discuss, solve, create, decide, act_on_environment`.

9 posiciones:

`receiver, instruction_follower, observer, experimenter, investigator, reasoner, collaborator, decision_maker, community_agent`.

### Estrategia A — RULEA 0.1

Reglas lingüísticas transparentes, conservadoras, congeladas después de pruebas sintéticas pre-corpus. Ejecución 9,594/9,594 con SHA exacto. No se ajustaron patrones después de observar distribuciones del corpus.

### Estrategia B — SEMB 0.2

Clasificador semántico independiente, sin leer A para calibrarse. SEMB 0.1 se descartó antes del corpus por colapso geométrico. SEMB 0.2 utiliza Multilingual-E5 Small con revisión pinneada, tres anclas sintéticas cortas por categoría y separación estricta desarrollo/VALIDATION_B02. Sólo después de superar la validación sintética bloqueada se permitió acceso al corpus.

### Acuerdo computacional

No existe adjudicación humana. A y B permanecen visibles.

Métricas:

- n11/n10/n01/n00;
- binary agreement;
- positive Jaccard;
- Jaccard de conjuntos por fragmento;
- exact-set agreement;
- `stable_exact`, `stable_partial`, `method_sensitive`, `uncertain`.

### Comparación histórica principal

Estrato: `certain_nonheading`.

Se reportan simultáneamente:

- prevalencia A;
- prevalencia B;
- prevalencia consensus-positive A∩B;
- method-sensitive rate.

Transiciones preregistradas:

- 1972→1988;
- 1988→1993/ed.1998;
- 1993/ed.1998→2014;
- 1972→2014.

Una dirección histórica principal sólo puede denominarse robusta cuando A, B y consenso cambian en la misma dirección no nula.

## Estructura propuesta del manuscrito

### 1. Introducción

Problema: los libros de texto son artefactos curriculares que no sólo transmiten contenidos; distribuyen acciones y posiciones epistemológicas al alumno.

Vacío: falta una comparación longitudinal reproducible, a escala de fragmento, que separe contenido temático de la acción pedagógica solicitada y cuantifique sensibilidad metodológica.

Pregunta y aporte.

### 2. Contexto histórico-curricular

Debe articular, con fuentes externas verificadas:

- reforma/renovación de Ciencias Naturales de los años setenta;
- continuidad o recontextualización en el corte catalogado 1988;
- reforma de 1993 y cronología concreta del libro de quinto grado cuya primera edición es 1998;
- RIEB y configuración del libro revisado 2014;
- cambios declarados en enseñanza de ciencia, indagación, proyectos, ambiente, salud, participación y toma de decisiones.

No inferir estas tendencias desde los resultados computacionales; contrastarlas documentalmente.

### 3. Datos y método

Subsecciones:

3.1 Corpus y proveniencia CONALITEG.

3.2 Reconstrucción del visor y activos fuente.

3.3 OCR adaptativo y límites de `text_detected`.

3.4 PAGESTRUCT 0.2.

3.5 FRAGSEG 0.2.

3.6 Modelo conceptual de acciones/posiciones.

3.7 RULEA 0.1.

3.8 SEMB 0.1 fallido y SEMB 0.2 validado.

3.9 Acuerdo A/B, incertidumbre y regla de robustez.

3.10 Gobernanza jurídica y publicación únicamente de derivados no sustitutivos.

### 4. Resultados

#### 4.1 Calidad y composición del corpus analítico

Fuentes:

- `page_structure_summary.csv`;
- `fragment_segmentation_summary.csv`;
- `fragment_segmentation_audit.csv`.

#### 4.2 Estabilidad metodológica A/B

Fuentes:

- `fragment_labels_A_audit.csv`;
- `fragment_labels_B_audit.csv`;
- `classifier_AB_category_agreement.csv`;
- `classifier_AB_agreement_summary.csv`.

Regla: discutir `positive_jaccard` además de binary agreement para evitar que la abundancia de ceros infle el acuerdo aparente.

#### 4.3 Transformaciones en las acciones pedagógicas

Fuentes:

- `historical_action_prevalence.csv`;
- `historical_action_composition.csv`;
- `historical_family_prevalence.csv`;
- `historical_transitions.csv`.

Presentar primero las 16 acciones originales; usar familias sólo como síntesis interpretativa.

#### 4.4 Transformaciones en las posiciones del alumno

Fuentes:

- `historical_position_prevalence.csv`;
- `historical_position_composition.csv`;
- `historical_family_prevalence.csv`;
- `historical_transitions.csv`.

Ejes interpretativos preregistrados:

- recepción/ejecución;
- indagación/razonamiento;
- agencia social.

#### 4.5 Continuidades, rupturas y categorías method-sensitive

Fuentes:

- `exploratory_robust_transitions.csv`;
- `exploratory_method_sensitive_transitions.csv`;
- `exploratory_category_stability.csv`.

Distinguir explícitamente:

- resultado robusto preregistrado;
- priorización exploratoria por magnitud;
- sensibilidad metodológica.

### 5. Discusión

Preguntas guía:

- ¿Existe una transición desde recepción/ejecución hacia indagación/razonamiento?
- ¿Los cambios son lineales o aparecen rupturas/reversiones entre generaciones?
- ¿La generación 1988 constituye continuidad del ciclo setentero o una configuración distinta?
- ¿La renovación vinculada al ciclo de 1993/ed.1998 produce una ruptura mayor que el simple cambio de catálogo sugeriría?
- ¿2014 incrementa realmente agencia, decisión y acción comunitaria o sólo cambia el lenguaje curricular?
- ¿Qué categorías dependen demasiado del clasificador para sostener una interpretación histórica?

No responder estas preguntas hasta contrastar las tablas y la documentación curricular externa.

### 6. Limitaciones

Obligatorias:

- sólo cuatro libros/documentos y un grado/asignatura;
- fragmentos anidados en documentos, no observaciones independientes;
- OCR puede alterar lexicalización y orden espacial;
- CER/WER disponible contra referencia de operador, no gold standard humano independiente;
- ausencia deliberada de revisión/adjudicación humana;
- RULEA privilegia evidencia explícita y es conservador;
- SEMB depende de una arquitectura semántica y validación sintética;
- la concordancia A/B mide estabilidad entre especificaciones, no verdad de etiqueta;
- páginas visuales y layouts complejos requieren manejo estructural;
- restricciones de derechos impiden publicar el OCR completo o reconstrucciones del corpus;
- resultados no pueden generalizarse todavía a todos los grados/asignaturas.

### 7. Conclusiones

Sólo después del análisis contextual. Deben distinguir:

- hallazgo histórico robusto;
- resultado exploratorio;
- resultado method-sensitive;
- implicación metodológica para escalar LTMD.

## Figuras/tablas candidatas

1. Diagrama de pipeline: 759 activos → PAGESTRUCT → 639 páginas → 9,594 fragmentos → A/B → acuerdo → comparación.
2. Tabla de corpus por generación.
3. Heatmap de positive Jaccard A/B por acción y generación.
4. Perfil longitudinal de familias de acciones por generación, consenso A∩B.
5. Perfil longitudinal de posiciones del alumno, consenso A∩B.
6. Slope/dumbbell de transiciones robustas 1972→2014.
7. Tabla de categorías method-sensitive.
8. Figura conceptual recepción/ejecución ↔ indagación/razonamiento ↔ agencia social, únicamente si los datos justifican ese resumen.

## Siguiente paso científico

1. congelar/leer la capa exploratoria completa;
2. reconstruir contexto curricular con fuentes académicas/oficiales verificadas;
3. redactar Resultados 4.1–4.5 directamente desde los CSV;
4. contrastar resultados con contexto antes de redactar Discusión;
5. decidir revista/idioma sólo cuando el argumento histórico esté estabilizado.
