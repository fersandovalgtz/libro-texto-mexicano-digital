# Stage gates de SEMB 0.3

Versión: `SEMB03_STAGE_GATES_0.1`

El desarrollo de SEMB 0.3 se divide en puertas secuenciales para impedir fuga de información entre desarrollo, validación bloqueada y análisis histórico.

## G0 — infraestructura previa a referencia humana

Debe existir y pasar:

- muestra maestra de 480 fragmentos, 320 `development` y 160 `locked_validation`;
- plantilla ciega con IDs opacos;
- subconjunto de 120 casos para doble codificación;
- criterios de aceptación preregistrados;
- validador de anotaciones;
- evaluador de fiabilidad;
- generador de consenso que no adjudica desacuerdos automáticamente;
- batería sintética independiente;
- verificador de readiness.

Estado esperado mientras no haya referencia humana: `WAITING_HUMAN_REFERENCE`.

## G1 — fiabilidad humana

Dos anotadores independientes completan los 120 casos de fiabilidad. Los archivos se validan con `scripts/validate_semb03_annotations.py` y se evalúan con `scripts/evaluate_semb03_human_reliability.py`. Si no se cumplen los criterios de `SEMB03_ACCEPTANCE_0.1`, se revisa el constructo/manual antes de continuar.

## G2 — referencia de desarrollo

Se completa/adjudica la referencia humana de los 320 casos `development`. Los desacuerdos no pueden resolverse mediante consulta a A/B, generación del libro ni resultados históricos. Sólo esta referencia puede usarse para seleccionar SEMB 0.3.

## G3 — desarrollo computacional

Se comparan arquitecturas y parámetros usando exclusivamente desarrollo + pruebas sintéticas preregistradas. La salida debe registrar `development_n=320` y `locked_validation_accessed=false`.

## G4 — bloqueo del modelo

Antes de consultar los 160 casos bloqueados se ejecuta `scripts/lock_semb03_model.py`, que registra hashes SHA-256 del resultado de desarrollo, configuración, código y criterios de aceptación. El lock no puede sobrescribirse.

## G5 — validación bloqueada única

Se generan predicciones sobre los 160 casos sin modificar el modelo y se ejecuta `scripts/evaluate_semb03_locked_validation.py`. El evaluador se niega a correr sin lock y se niega a producir una segunda evaluación sobre el mismo conjunto.

## G6 — producción

Sólo un modelo que pasa G5 puede etiquetar el corpus completo como SEMB 0.3 para análisis histórico primario. Si falla G5, el resultado se conserva como fallo de validación; cualquier versión posterior requiere un nuevo conjunto independiente de validación.

## G7 — reapertura histórica

Las comparaciones 1972–2014 se reconstruyen desde cero después del lock y validación. Los hallazgos de SEMB 0.2 se consideran exploratorios y no condicionan la selección del modelo nuevo.
