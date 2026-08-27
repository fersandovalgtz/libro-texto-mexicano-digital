# SEMB 0.3 — integridad del holdout y remediación 0.1

Fecha de auditoría: 2026-08-27.

## Hallazgo

La muestra pública `data/validation/semb03_human_reference_sample.csv` contiene 480 fragmentos: 320 marcados `development` y 160 marcados `locked_validation`. Los 160 identificadores nominalmente reservados quedaron visibles en el historial público antes de que existiera el mecanismo de `model lock`.

La primera publicación identificada de una muestra que exponía `fragment_id` y `analysis_role=locked_validation` es el commit `ea5a2c2f2da2c245d1ddbedf418732e9f640dfb8`, fechado 2026-08-15T19:38:38Z. La utilidad de lock irreversible apareció después, en `491b8663688765f2a70d4f9a4a71544f5c474653`, fechado 2026-08-15T19:51:18Z. Al momento de esta auditoría no existe `data/validation/semb03_model_lock.json` en `main`.

No se detectaron etiquetas humanas publicadas en la plantilla de anotación: los campos `annotator_id`, `annotation_round`, `actionable`, `action_labels`, `position_labels`, `annotation_confidence` y `ambiguity_note` permanecen vacíos. La incidencia, por tanto, no es una filtración de respuestas humanas; es una pérdida de independencia del conjunto nominalmente reservado.

## Decisión metodológica

Los 160 casos públicos previamente denominados `locked_validation` quedan **invalidados para cualquier afirmación futura de validación final ciega o verdaderamente held-out**. No se borran del historial y no se reetiquetan retroactivamente para ocultar el incidente. Pueden utilizarse únicamente como material de desarrollo o como auditoría de robustez explícitamente descrita como expuesta.

Un `model lock` creado después de esta exposición no puede rehabilitar esos 160 casos. La validación final de SEMB 0.3 requerirá un nuevo holdout privado de 160 fragmentos, 40 por generación, seleccionado sin consultar salidas semánticas del clasificador y excluyendo las 480 identidades de la muestra pública histórica.

## Nuevo contrato de holdout

El nuevo holdout se genera localmente con `scripts/prepare_semb03_private_holdout.py`. El script usa exclusivamente metadatos del `fragment_manifest.csv`, una semilla criptográfica privada almacenada bajo `private/` y un algoritmo congelado. La ruta `private/` ya está excluida por `.gitignore`.

El manifiesto que contiene `fragment_id` se guarda sólo bajo `private/` y **no debe entrar en Git**. El repositorio público puede recibir únicamente `data/validation/semb03_private_holdout_commitment.json`, que registra tamaño, distribución, versión del algoritmo y SHA-256 del manifiesto privado. Ese hash permite demostrar posteriormente que el conjunto evaluado coincide con el conjunto fijado antes del `model lock` sin revelar sus identidades durante el desarrollo.

El compromiso público debe existir antes de crear `semb03_model_lock.json`. La utilidad de lock se endurece para rechazar: a) un lock sin compromiso privado; b) un compromiso que publique IDs; c) un holdout que no excluya las 480 identidades públicas; d) un lock retroactivo después de un resultado de validación.

## Flujo correcto a partir de esta versión

1. Completar la referencia humana de desarrollo y la fiabilidad intercodificador sin utilizar el futuro holdout privado para ajuste.
2. Crear fuera de Git la semilla y el manifiesto del nuevo holdout de 160 casos.
3. Versionar únicamente el compromiso criptográfico público.
4. Congelar código, configuración, resultado de desarrollo, criterios de aceptación y compromiso mediante `scripts/lock_semb03_model.py`.
5. Sólo después del lock abrir el manifiesto privado a la evaluación final.
6. Publicar resultados agregados y, si metodológicamente conviene, revelar el manifiesto únicamente después de cerrada la evaluación.

## Efecto sobre el estado científico

Esta corrección no crea etiquetas humanas ni modifica la cobertura semántica U1. El valor sigue siendo **0/542** hasta que exista referencia humana efectivamente producida, validada e incorporada conforme al protocolo. Tampoco cambia la cobertura técnica 524/542.

La regla conservadora es deliberada: una validación final con un holdout comprometido vale menos que reconocer la exposición y sustituirlo antes de hacer afirmaciones de desempeño.
