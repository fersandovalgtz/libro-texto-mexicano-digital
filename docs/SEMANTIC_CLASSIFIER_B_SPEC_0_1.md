# Clasificador pedagógico B — similitud semántica multilingüe 0.1

Fecha de preregistro: 2026-08-15

## Propósito

Construir una segunda especificación computacional **independiente** de RULEA 0.1 para etiquetar acciones pedagógicas y posiciones del alumno. B no usa los regex, conteos de evidencia ni etiquetas producidas por A, y no se entrena con ejemplos humanos del corpus.

## Modelo congelado

- modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- revisión fijada: `f16484b452bc5449a3ad85665709a2648b51d735`
- tarea: sentence similarity / embeddings multilingües
- dimensión de embedding: 384
- licencia declarada por el repositorio del modelo: Apache-2.0

La revisión se fija para evitar que cambios futuros en `main` alteren resultados. El modelo se descarga en CI y no se incorpora al repositorio LTMD.

## Independencia respecto de A

B recibe únicamente:

1. texto efímero reconstruido del fragmento;
2. `fragment_id`, `text_sha256`, longitud y metadatos técnicos mínimos;
3. un conjunto preregistrado de prototipos semánticos sintéticos.

No recibe ni consulta:

- `fragment_labels_A.csv`;
- patrones/regex de RULEA;
- conteos de evidencia A;
- correcciones humanas;
- ejemplos etiquetados del corpus.

## Verificación de identidad textual

Antes de obtener embeddings, la reconstrucción del fragmento debe reproducir exactamente `text_sha256` de FRAGSEG 0.2. Cualquier mismatch aborta el shard.

## Prototipos

Cada categoría se representa mediante **dos frases sintéticas** escritas antes de la ejecución. Se codifican ambas, se promedian sus vectores y se normaliza el vector medio. No se usarán frases extraídas de los libros.

### Acciones

`observe`
- “Observa atentamente un objeto o fenómeno y utiliza lo que notas.”
- “Mira, examina o identifica propiedades mediante observación deliberada.”

`describe`
- “Describe las características, estados o resultados que encuentras.”
- “Expresa cómo es algo o qué propiedades presenta, sin explicar necesariamente sus causas.”

`recall`
- “Recuerda y menciona información que ya aprendiste anteriormente.”
- “Nombra o enumera conocimientos recuperados de la memoria.”

`explain`
- “Explica por qué sucede un fenómeno o cómo funciona una relación.”
- “Justifica una respuesta mediante razones, causas o mecanismos.”

`compare`
- “Compara elementos para establecer semejanzas, diferencias o relaciones.”
- “Contrasta dos condiciones y señala en qué se parecen o se diferencian.”

`classify`
- “Clasifica objetos o casos usando criterios y categorías.”
- “Agrupa o separa elementos según sus propiedades.”

`measure`
- “Mide una magnitud con una escala, instrumento, conteo o procedimiento cuantitativo.”
- “Obtén y registra una medida numérica de una propiedad.”

`experiment`
- “Realiza un experimento manipulando materiales o condiciones y observa los resultados.”
- “Cambia deliberadamente una condición para producir evidencia sobre un fenómeno.”

`investigate`
- “Investiga buscando, reuniendo o contrastando información que no está resuelta de inmediato.”
- “Consulta fuentes, realiza una indagación o reúne evidencia para responder una pregunta.”

`predict`
- “Predice qué ocurrirá antes de observar o comprobar el resultado.”
- “Anticipa un resultado futuro a partir de lo que sabes.”

`infer`
- “Infiere una conclusión a partir de datos, observaciones o evidencias.”
- “Deduce qué se puede concluir usando los resultados disponibles.”

`discuss`
- “Discute ideas con otras personas y contrasta argumentos o puntos de vista.”
- “Conversa o debate con compañeros para construir una respuesta.”

`solve`
- “Resuelve un problema mediante razonamiento, relaciones u operaciones.”
- “Encuentra una solución a una situación problemática.”

`create`
- “Crea, diseña, construye o elabora un producto o representación.”
- “Produce un dibujo, modelo, texto, cartel u objeto como resultado de la tarea.”

`decide`
- “Decide entre alternativas valorando información, criterios o consecuencias.”
- “Elige una opción y sustenta la decisión tomada.”

`act_on_environment`
- “Realiza o propone una acción de cuidado, prevención o intervención en la vida real.”
- “Aplica lo aprendido para actuar sobre salud, ambiente, familia, escuela o comunidad.”

### Posiciones del alumno

`receiver`
- “El estudiante recibe o lee información sin una acción cognitiva explícita solicitada.”
- “La función principal del alumno es atender a información que el texto presenta.”

`instruction_follower`
- “El alumno sigue pasos definidos y ejecuta instrucciones con poca elección metodológica.”
- “La tarea prescribe una secuencia que el estudiante debe cumplir.”

`observer`
- “El alumno produce o utiliza información mediante observación sistemática.”
- “El estudiante ocupa el papel de observador de objetos o fenómenos.”

`experimenter`
- “El alumno manipula materiales o condiciones para obtener evidencia.”
- “El estudiante ocupa el papel de experimentador.”

`investigator`
- “El alumno busca o produce evidencia con cierto margen para investigar.”
- “El estudiante ocupa el papel de investigador o indagador.”

`reasoner`
- “El alumno explica, compara, infiere, predice o resuelve usando razonamiento.”
- “El estudiante debe construir una respuesta razonada a partir de información o evidencia.”

`collaborator`
- “El alumno construye la tarea mediante interacción sustantiva con otras personas.”
- “El estudiante colabora, discute o trabaja con compañeros, familia u otros actores.”

`decision_maker`
- “El alumno valora alternativas y toma una decisión informada.”
- “El estudiante ocupa el papel de quien elige y justifica una opción.”

`community_agent`
- “El alumno proyecta el conocimiento hacia una acción en familia, escuela, comunidad, salud o ambiente.”
- “El estudiante actúa como agente de cuidado, prevención o transformación fuera de la respuesta escolar.”

## Cálculo

1. codificar fragmentos y prototipos con embeddings normalizados;
2. vector de categoría = promedio normalizado de sus dos prototipos;
3. score = similitud coseno fragmento ↔ vector de categoría;
4. ejecutar acciones y posiciones como dos espacios de decisión separados.

## Regla principal de selección

Preregistrada antes de observar scores del corpus:

- fragmentos `heading_candidate` o con <4 tokens: no reciben acciones B; `uncertain_B=1`;
- si `top_score < 0.42`: ninguna etiqueta de esa familia y `uncertain_B=1`;
- si hay etiquetas con score ≥0.46 y dentro de 0.06 del mejor score: conservar hasta 3 etiquetas;
- si ninguna alcanza 0.46, conservar sólo la mejor cuando `top_score ≥0.42` y el margen respecto de la segunda sea ≥0.035;
- si `top_score ≥0.42` pero el margen es <0.035, conservar las dos primeras si ambas ≥0.42 y marcar `uncertain_B=1`;
- máximo 3 etiquetas por familia para evitar expansión semántica indiscriminada.

Un fragmento puede no recibir ninguna acción o posición B.

## Salida pública

`fragment_labels_B.csv`, sin texto fuente:

- `fragment_id`
- columnas binarias por acción B
- columnas binarias por posición B
- top score y segundo score por familia
- margen
- número de etiquetas
- `uncertain_B`
- `text_sha256`
- modelo, revisión y versión de reglas de decisión

No se publicarán embeddings de fragmentos en esta fase para evitar una superficie de reconstrucción innecesaria.

## Sensibilidad preregistrada

Después del resultado principal se recalcularán etiquetas sin volver a OCR usando una matriz privada/efímera de scores y tres umbrales de score: 0.38, 0.42 y 0.46; con bandas multilabel 0.04, 0.06 y 0.08. Los resultados públicos serán agregados de estabilidad, no la matriz textual.

## Comparación A/B

Se calcularán por categoría:

- acuerdo binario;
- Jaccard por fragmento para conjuntos de acciones y posiciones;
- proporción A+/B+, A+/B−, A−/B+, A−/B−;
- acuerdo por generación, longitud y clase estructural;
- estabilidad excluyendo `uncertain_A` y/o `uncertain_B`.

No habrá adjudicación humana. El desacuerdo se conserva como dato metodológico y puede formar parte de los resultados del artículo.
