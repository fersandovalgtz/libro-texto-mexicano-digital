# Manual de anotación 0.1 — piloto de Ciencias Naturales, quinto grado

## Propósito

Convertir `CODEBOOK_0_1.md` en instrucciones operativas suficientemente precisas para que dos revisiones independientes puedan llegar a decisiones comparables.

Este manual **no modifica todavía el libro de códigos**. Explica cómo aplicarlo. Cualquier cambio de definición deberá registrarse como decisión y, si altera categorías, producir una nueva versión del libro de códigos.

## Unidad de anotación

La unidad es un **fragmento funcionalmente autónomo**, preferentemente:

- una consigna;
- una pregunta;
- una actividad delimitada;
- un bloque breve de explicación;
- un elemento de evaluación.

No cortar un fragmento sólo para obtener una categoría “limpia” si dos acciones forman parte de la misma consigna. Tampoco unir instrucciones independientes que podrían codificarse por separado.

## Secuencia obligatoria de decisión

### Paso 1 — ¿El fragmento pide una acción al estudiante?

- **No:** valorar `expository`; la posición del alumno puede ser `receiver` si la función dominante es recibir información.
- **Sí:** continuar al paso 2.

### Paso 2 — Tipo funcional

Registrar todos los tipos claramente observables:

- `instruction`: existe una orden/consigna explícita;
- `question`: existe una interrogación que requiere respuesta;
- `activity`: varias instrucciones/preguntas organizan una tarea delimitada;
- `experiment`: existe manipulación de materiales/condiciones y observación de resultados como evidencia;
- `project`: tarea extendida con varias fases/productos y cierto grado de planeación;
- `assessment`: el propósito explícito es comprobar/revisar aprendizaje;
- `expository`: exposición de información sin acción inmediata solicitada.

`experiment` no se asigna sólo porque el texto hable de un experimento histórico o científico.

### Paso 3 — Acción pedagógica solicitada

Preguntar: **¿qué debe hacer cognitivamente o prácticamente el alumno para cumplir la consigna?**

No inferir una acción porque sería pedagógicamente deseable. Sólo codificar acciones observables en el lenguaje o estructura de la tarea.

### Paso 4 — Posición pedagógica del alumno

Derivar la posición a partir de lo que el estudiante efectivamente debe hacer, no del discurso general del capítulo.

### Paso 5 — Dimensiones temáticas

Asignar sólo cuando sean claramente pertinentes al fragmento, no a todo el libro.

## Reglas de frontera entre acciones parecidas

### `observe` vs `describe`

- `observe`: obtener información atendiendo deliberadamente al fenómeno/objeto/imagen.
- `describe`: expresar las características observadas o conocidas.

Si pide “observa y escribe cómo es…”, codificar ambos.

### `recall` vs `explain`

- `recall`: la respuesta puede obtenerse principalmente recuperando información explícitamente aprendida/presentada.
- `explain`: exige relación causal, mecanismo, razón o interpretación.

Una pregunta que comienza con “¿por qué?” no es automáticamente `explain` si sólo solicita repetir una frase causal ya presentada literalmente; registrar la operación dominante según el contexto.

### `compare` vs `classify`

- `compare`: identificar semejanzas/diferencias o relaciones entre elementos.
- `classify`: asignar elementos a grupos/categorías usando un criterio.

Clasificar puede requerir comparar; sólo asignar `compare` adicionalmente cuando la comparación sea una acción explícita o necesaria como producto de la tarea.

### `experiment` vs `instruction_follower`

Una actividad experimental puede colocar simultáneamente al alumno como `experimenter` e `instruction_follower`.

- `experimenter`: manipula condiciones/materiales y obtiene evidencia.
- `instruction_follower`: la secuencia está fuertemente predeterminada.

No tratar estas posiciones como excluyentes.

### `investigate` vs `recall`/`lookup`

`investigate` requiere buscar, reunir, contrastar o producir información que no está resuelta inmediatamente en el fragmento, con al menos cierto trabajo de indagación.

Una orden del tipo “busca en el diccionario la definición de X” puede ser consulta externa, pero no necesariamente una investigación sustantiva. Registrar `investigate` sólo cuando la búsqueda tenga una finalidad indagatoria reconocible.

### `predict` vs `infer`

- `predict`: anticipar un resultado antes de comprobarlo/observarlo.
- `infer`: derivar una conclusión a partir de evidencia ya disponible.

### `discuss` vs `collaborator`

- `discuss` es una **acción**: intercambiar/contrastar/argumentar ideas.
- `collaborator` es una **posición**: la tarea requiere interacción sustantiva con otros.

Trabajar “en equipo” no implica `discuss` si sólo se reparten tareas. Discutir una idea en grupo sí puede implicar ambos.

### `create` vs respuesta escrita ordinaria

No codificar `create` por toda respuesta escrita, dibujo auxiliar o llenado de tabla. Requiere elaborar/diseñar/producir un objeto, representación, modelo, texto o propuesta con cierto componente constructivo.

### `decide` vs seleccionar respuesta correcta

`decide` implica valorar alternativas, criterios, riesgos o consecuencias. Elegir una opción de respuesta cerrada en un examen no convierte al alumno en `decision_maker`.

### `act_on_environment` vs contenido ambiental

Sólo se asigna cuando el alumno debe realizar/proponer una acción vinculada con salud, ambiente, comunidad o vida cotidiana más allá de contestar escolarmente.

Una explicación sobre contaminación no basta.

## Reglas para posiciones del alumno

### `receiver`

Usar cuando predomina recepción de información y no existe una acción explícita sustantiva. No combinar automáticamente con todas las demás posiciones sólo porque el alumno deba leer instrucciones.

### `instruction_follower`

La secuencia y forma de ejecución están sustancialmente prescritas.

### `observer`

El alumno obtiene evidencia/información mediante observación deliberada.

### `experimenter`

Manipula materiales o condiciones y usa resultados como evidencia.

### `investigator`

Busca/produce evidencia con margen de decisión o estrategia de indagación.

### `reasoner`

La tarea exige explicar, comparar, inferir, predecir o resolver mediante razonamiento. No asignar por mera dificultad temática.

### `collaborator`

La interacción con otros forma parte funcional de la tarea, no sólo del arreglo físico del grupo.

### `decision_maker`

Valora alternativas para adoptar una posición/decisión informada.

### `community_agent`

Proyecta conocimiento hacia cuidado, prevención, intervención o transformación fuera de la respuesta escolar inmediata.

## Ejemplos sintéticos de entrenamiento

Los siguientes ejemplos son inventados y **no provienen del corpus fuente**.

### Ejemplo A

“Observa durante cinco minutos las hojas de dos plantas y anota tres diferencias.”

- tipo: `instruction` / posible `activity` si forma parte de una tarea mayor;
- acciones: `observe`, `compare`, `describe`;
- posiciones: `observer`, `reasoner`.

### Ejemplo B

“¿Cuál es la función principal de los pulmones?” después de que la definición aparece literalmente en el texto.

- tipo: `question`;
- acción: `recall`;
- posición: no asignar `reasoner` sólo por ser una pregunta científica.

### Ejemplo C

“Antes de agregar la sal, escribe qué crees que ocurrirá; después mezcla y compara tu predicción con lo observado.”

- tipo: `instruction`, `activity`, posible `experiment` si existe manipulación/evidencia;
- acciones: `predict`, `experiment`, `observe`, `compare`;
- posiciones: `experimenter`, `observer`, `reasoner`, posiblemente `instruction_follower`.

### Ejemplo D

“Pregunta a tres personas de tu familia cómo ahorran agua, organiza sus respuestas y propón una acción para tu casa.”

- tipo: `activity`;
- acciones: `investigate`, `classify` o `compare` si se pide organizar con criterios, `create`/`decide`, `act_on_environment`;
- posiciones: `investigator`, `reasoner`, `community_agent`.

### Ejemplo E

“Lee el siguiente texto sobre la expedición científica.”

- tipo: `instruction` + contenido `expository`;
- acción pedagógica: no asignar `investigate` por el tema;
- posición dominante: `receiver`.

## Fragmentos con múltiples consignas

Si un fragmento contiene una cadena clara —por ejemplo “observa, compara y explica”— codificar las tres acciones.

Si contiene actividades separables con productos independientes, dividir en fragmentos diferentes antes de codificar.

## Incertidumbre

Cuando una categoría no pueda decidirse con seguridad:

1. no forzar el código;
2. registrar la duda en `Notas`;
3. marcar las alternativas posibles;
4. llevar el caso a segunda revisión;
5. si el mismo patrón aparece repetidamente, proponer aclaración del manual/libro de códigos para todos los casos, no sólo para ese ejemplo.

## Prohibiciones metodológicas

- no usar el año/generación para decidir el código;
- no asumir que libros recientes son más “constructivistas” o investigativos;
- no inferir acción por diseño gráfico;
- no asignar códigos por tema general del capítulo;
- no cambiar la definición para acomodar una hipótesis;
- no consultar estadísticas agregadas de la generación durante una codificación ciega si esto puede influir en la decisión.

## Resultado de la primera ronda

Las dificultades recurrentes deberán registrarse en una tabla de decisiones. Si alteran definiciones sustantivas se publicará `CODEBOOK_0_2.md`; si sólo añaden ejemplos/clarificaciones sin cambiar significado, se actualizará el manual preservando historial de commits.
