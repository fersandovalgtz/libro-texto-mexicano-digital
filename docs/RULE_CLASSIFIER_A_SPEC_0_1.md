# Clasificador pedagógico A — reglas transparentes 0.1

## Función

Primera especificación computacional independiente para etiquetar fragmentos LTMD según `CODEBOOK_0_1`, sin revisión humana. Se aplica después de `FRAGSEG_0.1` y trabaja con el texto OCR del fragmento sólo en memoria.

## Principio rector

**Inferencia conservadora:** ninguna categoría se asigna por el tema general de la página. Debe existir evidencia lingüística explícita en el fragmento. La ausencia de evidencia produce etiqueta ausente/`uncertain`, no una inferencia forzada.

## Acciones pedagógicas — señales iniciales

Las listas se normalizan por `casefold`, pero se preservan diacríticos en el pipeline textual de trabajo.

- `observe`: observa, observar, mira, examina, fíjate, identifica visualmente.
- `describe`: describe, caracteriza, anota características, indica cómo es.
- `recall`: recuerda, menciona, enumera, nombra, qué recuerdas, qué sabes.
- `explain`: explica, por qué, cómo ocurre, a qué se debe, justifica.
- `compare`: compara, semejanzas, diferencias, más que, menos que, relación entre.
- `classify`: clasifica, agrupa, ordena según, separa en, categoría.
- `measure`: mide, medición, centímetro, metro, balanza, termómetro, cronómetro, registra la medida.
- `experiment`: experimento, experimenta, materiales + procedimiento/manipulación, cambia/mezcla/coloca y observa resultado.
- `investigate`: investiga, busca información, consulta, entrevista, encuesta, averigua, indaga.
- `predict`: predice, anticipa, qué crees que ocurrirá, antes de observar.
- `infer`: infiere, concluye, deduce, a partir de los resultados/datos/observaciones.
- `discuss`: discute, comenten, conversen, debate, compara con tus compañeros, en equipo cuando exige intercambio sustantivo.
- `solve`: resuelve, calcula una respuesta, encuentra la solución, problema.
- `create`: elabora, construye, diseña, dibuja, crea, prepara, representa, modelo/maqueta/cartel cuando se solicita producirlo.
- `decide`: decide, elige, selecciona una alternativa, qué opción, toma una decisión, argumenta tu elección.
- `act_on_environment`: realiza/propon una acción de cuidado, prevención, salud, ambiente o comunidad fuera de la mera respuesta escolar.

## Reglas de coocurrencia

Las acciones son multietiqueta. No se fuerza exclusividad. Ejemplo: `observa ... compara ... explica` puede producir `observe + compare + explain`.

`experiment` no se asigna sólo porque aparezca la palabra “experimento” en texto expositivo. Debe coexistir una señal de acción dirigida al alumno o una estructura de materiales/procedimiento.

`investigate` exige búsqueda/producción de información no resuelta inmediatamente por el mismo fragmento.

`predict` y `infer` se distinguen temporalmente: anticipación antes de evidencia vs. conclusión desde evidencia.

## Posiciones del alumno — derivación conservadora

- `receiver`: fragmento expositivo sin acción dirigida al alumno.
- `instruction_follower`: instrucciones explícitas sin evidencia de elección metodológica/razonamiento autónomo.
- `observer`: acción `observe` con producción/uso de observación.
- `experimenter`: acción `experiment` válida.
- `investigator`: acción `investigate` válida con búsqueda/evidencia.
- `reasoner`: una o más de `explain`, `compare`, `predict`, `infer`, `solve`.
- `collaborator`: `discuss` o interacción sustantiva explícita con pares/familia/otros.
- `decision_maker`: `decide` con elección real, no simple selección de respuesta cerrada.
- `community_agent`: `act_on_environment` proyectada hacia familia, comunidad, salud o ambiente.

Las posiciones también son multietiqueta.

## Tipo funcional

El `candidate_type` de `FRAGSEG_0.1` se conserva como rasgo, pero A recalcula un tipo funcional de reglas (`type_A`) a partir del fragmento:

- expository
- instruction
- question
- activity
- experiment
- project
- assessment

Puede ser multietiqueta cuando la estructura lo justifique.

## Salida pública

Una fila por `fragment_id` en `fragment_labels_A.csv`, sin texto:

- `fragment_id`
- `type_A`
- columnas binarias por acción
- columnas binarias por posición
- scores/evidence_count
- `uncertain_A`
- `ruleset_version=RULEA_0.1`

## Incertidumbre

`uncertain_A=1` cuando:

- hay señal léxica contradictoria;
- el fragmento tiene <4 tokens salvo pregunta/encabezado claramente funcional;
- OCR/layout de la página tiene certeza baja;
- la única evidencia procede de una palabra polisémica aislada;
- el fragmento es extremadamente largo (>500 tokens) o `uncertain_boundary=1`.

## Validación computacional

Sin adjudicación humana. Se revisarán automáticamente:

- distribución de etiquetas por generación;
- tasa de `uncertain_A`;
- coocurrencias imposibles/sospechosas;
- sensibilidad al retirar términos ambiguos;
- estabilidad por longitud y clase estructural;
- comparación posterior con clasificador semántico B.
