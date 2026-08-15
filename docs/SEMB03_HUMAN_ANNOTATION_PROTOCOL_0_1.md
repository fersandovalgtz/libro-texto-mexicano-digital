# Protocolo de anotación humana SEMB 0.3

Versión: `SEMB03_HUMAN_ANNOTATION_PROTOCOL_0.1`

## Objetivo

Construir una referencia humana independiente para desarrollar y validar SEMB 0.3 sin utilizar como función objetivo los resultados históricos del corpus ni las salidas de los clasificadores A/B.

## Muestra

La muestra maestra contiene 480 fragmentos elegibles, 120 por generación. La selección se realiza exclusivamente a partir de metadatos FRAGSEG y hashes deterministas. Dentro de cada generación se incluyen 25 expositivos, 25 instrucciones, 25 preguntas, 20 casos de tipos menos frecuentes y 25 casos de remanente. La asignación a desarrollo (320 casos) y validación bloqueada (160 casos) se decide por hash antes de la anotación.

## Cegamiento

El anotador no debe conocer generación, página, tipo FRAGSEG, rol desarrollo/validación, etiquetas A/B ni resultados históricos. Los identificadores visibles son opacos y no codifican generación. El texto se reconstruye del ejemplar fuente sólo durante la sesión de anotación y se verifica contra el SHA-256 congelado. El texto OCR no se guarda en el archivo de anotaciones.

## Variables humanas

Cada caso recibe: (a) `actionable`: 1 si el fragmento solicita una acción/tarea, 0 si no la solicita, `u` si es genuinamente ambiguo; (b) cero o más etiquetas de acción del vocabulario controlado; (c) cero o más posiciones del estudiante; (d) confianza 1–3; y (e) nota breve de ambigüedad cuando sea necesaria.

Acciones permitidas: `observe`, `describe`, `recall`, `explain`, `compare`, `classify`, `measure`, `experiment`, `investigate`, `predict`, `infer`, `discuss`, `solve`, `create`, `decide`, `act_on_environment`.

Posiciones permitidas: `receiver`, `instruction_follower`, `observer`, `experimenter`, `investigator`, `reasoner`, `collaborator`, `decision_maker`, `community_agent`.

## Reglas de codificación

`actionable=0` implica que `action_labels` debe quedar vacío. Una pregunta que sólo solicita recuperar un dato puede etiquetarse `recall`; una pregunta que exige relación causal o justificación puede etiquetarse `explain`; problemas con procedimiento o respuesta razonada pueden usar `solve`; comparación explícita usa `compare`. No se debe inferir una acción que el fragmento no solicita o presupone de manera suficientemente clara.

Las posiciones describen el rol intelectual/práctico solicitado al estudiante, no el tema del texto. Un fragmento puramente expositivo puede etiquetarse `receiver`; seguir pasos prescritos corresponde a `instruction_follower`; producir explicación, inferencia, comparación o resolución razonada corresponde a `reasoner`; búsqueda autónoma de evidencia corresponde a `investigator`; intervención fuera de la tarea escolar puede corresponder a `community_agent`.

## Fiabilidad interanotador

Antes de abrir la validación bloqueada, se recomienda doble codificación independiente de al menos 120 casos (25% de la muestra), seleccionados de manera determinista y sin revelar su generación o rol. Se calcularán acuerdo de `actionable`, Jaccard y F1 multilabel por acción/posición, además de acuerdo por categoría. Las discrepancias de desarrollo pueden utilizarse para aclarar el manual; las discrepancias del conjunto bloqueado no deben utilizarse para retocar el modelo después de abrirlo.

## Desarrollo y validación

Los 320 casos de desarrollo pueden emplearse para seleccionar arquitectura, calibrar el gate, márgenes o estrategias multilabel y fijar SEMB 0.3. Tras bloquear versión, configuración y criterios de éxito, se abre una sola vez el conjunto de 160 casos de validación. Si SEMB 0.3 no alcanza los criterios preregistrados, se registra el fallo; no se iteran parámetros contra ese mismo conjunto.

## Persistencia y copyright

El repositorio público conserva IDs, hashes, metadatos, especificaciones y anotaciones, pero no texto OCR reconstruido. Las sesiones humanas se realizan con `scripts/annotate_semb03_interactive.py`, que usa archivos temporales y guarda únicamente la codificación. La carpeta `private/` está excluida del control de versiones.

## Condición para volver al análisis histórico

Las comparaciones históricas con SEMB 0.3 sólo podrán calcularse después de: (1) cerrar la referencia humana, (2) fijar el modelo con desarrollo, (3) pasar la validación bloqueada o documentar formalmente su fallo, y (4) congelar la versión de producción. Hasta entonces, los resultados históricos SEMB 0.2 permanecen exploratorios.
