# Protocolo de desarrollo y validación humana SEMB 0.3

Versión: `SEMB03_HUMAN_PROTOCOL_0.1`

## Propósito

SEMB 0.2 se conserva íntegramente como una capa preregistrada y reproducible. Su diagnóstico posterior mostró que la incertidumbre casi total no deriva principalmente de la longitud de los fragmentos, sino de la combinación de un gate de acción muy restrictivo y márgenes top-1/top-2 que rara vez superan los umbrales fijados. SEMB 0.3 se desarrollará como una nueva versión, sin modificar retrospectivamente SEMB 0.2.

El objetivo de SEMB 0.3 es obtener etiquetas semánticas de acción y posición pedagógica con una calibración empírica interpretable y una tasa de abstención útil, manteniendo una separación estricta entre desarrollo metodológico y resultados históricos.

## Regla contra fuga histórica

Ninguna decisión de arquitectura, umbral, anchor, regla de abstención o selección de método podrá usar como función objetivo: diferencias entre generaciones, dirección de tendencias históricas, magnitud de cambios 1972–1988–1993–2014, acuerdo con una narrativa historiográfica esperada ni resultados de RULEA/SEMB 0.2 sobre esas diferencias.

El muestreo para referencia humana se construye únicamente desde `fragment_manifest.csv`: generación, tipo de candidato, longitud, identificador y hash. El script de muestreo no lee `fragment_labels_A.csv`, `fragment_labels_B.csv`, los archivos A/B ni los resultados históricos.

## Muestra humana preregistrada

Tamaño total: 480 fragmentos elegibles, 120 por generación (1972, 1988, 1993 y 2014). Se excluyen `heading_candidate` y fragmentos de menos de 4 tokens porque SEMB 0.2 los trató explícitamente como unidades no clasificables.

Dentro de cada generación se fuerza cobertura de:

- 25 fragmentos `expository_candidate`;
- 25 `instruction_candidate`;
- 25 `question_candidate`;
- 20 de tipos de tarea menos frecuentes, agrupando `activity_candidate`, `experiment_candidate`, `project_candidate` y `assessment_candidate` cuando sean elegibles;
- 25 adicionales del resto de elegibles no seleccionados, para conservar heterogeneidad natural.

La selección es determinista mediante SHA-256 de `SEMB03_SAMPLE_0.1|fragment_id`, no mediante resultados semánticos.

## Separación desarrollo / validación

Los 480 casos se ordenan por un segundo hash independiente. Por generación, 80 se asignan a `development` y 40 a `locked_validation`, para un total de 320 y 160 respectivamente.

El conjunto `locked_validation` no puede abrirse para seleccionar método, anchors, umbrales o regla de abstención. Se abre una sola vez después de congelar SEMB 0.3.

Para máxima protección contra optimismo metodológico, el análisis histórico primario posterior a SEMB 0.3 deberá ejecutarse también sobre el corpus no usado en referencia humana (9,594 menos los 480 IDs de esta muestra). El resultado con corpus completo puede publicarse como análisis de sensibilidad.

## Anotación humana

La interfaz de anotación debe reconstruir el texto de manera efímera desde la fuente y no publicar texto OCR. El anotador no recibirá la variable `catalog_generation`, resultados de RULEA/SEMB ni estadísticas históricas. Es posible que rasgos lingüísticos o editoriales permitan inferir época; por ello se habla de cegamiento de metadatos, no de cegamiento histórico perfecto.

Cada fragmento debe recibir:

1. `actionable`: `yes`, `no` o `ambiguous`;
2. cero o más acciones del vocabulario SEMB: `observe`, `describe`, `recall`, `explain`, `compare`, `classify`, `measure`, `experiment`, `investigate`, `predict`, `infer`, `discuss`, `solve`, `create`, `decide`, `act_on_environment`;
3. cero o más posiciones: `receiver`, `instruction_follower`, `observer`, `experimenter`, `investigator`, `reasoner`, `collaborator`, `decision_maker`, `community_agent`;
4. `annotation_confidence`: `high`, `medium` o `low`;
5. nota breve sólo cuando exista ambigüedad real.

En `development`, un anotador primario codifica los 320 casos y una submuestra aleatoria preregistrada del 20% recibe segunda codificación. En `locked_validation`, los 160 casos reciben dos codificaciones independientes. Los desacuerdos se adjudican antes de calcular el rendimiento final, conservando también las etiquetas originales para medir acuerdo interevaluador.

## Métricas de desarrollo

Las métricas prioritarias son macro-F1 y sensibilidad/especificidad del gate `actionable`, F1 por etiqueta positiva, Jaccard de conjuntos positivos, exactitud de abstención y cobertura (proporción no abstained). La exactitud dominada por casos ambos-vacíos no puede ser métrica principal.

La regla de abstención debe optimizar una función explícita que penalice tanto error como abstención excesiva; debe reportarse una curva cobertura-rendimiento. No se aceptará una solución que alcance alta precisión clasificando sólo una fracción trivial del corpus.

## Criterio de congelamiento

Antes de abrir `locked_validation` deben quedar versionados:

- modelo y revisión exacta;
- anchors/prompts;
- método de similitud;
- regla del gate;
- umbrales por acción/posición si existen;
- regla de multietiqueta;
- regla de abstención;
- máximo de etiquetas;
- código de inferencia;
- hash del conjunto `development` y del artefacto de configuración.

Una vez abierta la validación bloqueada, cualquier modificación produce SEMB 0.4, no una corrección silenciosa de SEMB 0.3.

## Criterio mínimo para uso histórico primario

SEMB 0.3 sólo sustituirá a SEMB 0.2 como clasificador semántico primario si la validación bloqueada demuestra simultáneamente: cobertura sustancialmente superior a SEMB 0.2, rendimiento positivo no trivial en acciones y posiciones, comportamiento razonablemente estable entre los cuatro estratos generacionales y ausencia de una categoría cuya aparente calidad dependa exclusivamente de predominio de negativos.

Los valores numéricos de aceptación final se fijarán usando exclusivamente `development`, antes de abrir `locked_validation`.
