# LTMD-U1 — protocolo de evaluación de calidad de recuperación 0.1

**Estado:** instrumento técnico de evaluación **privada**, no resultado empírico ni autorización comercial. Fecha de incorporación: 25-nov-2026.

## Pregunta que sí puede responder

Para una **consulta FTS5 fija** y un conjunto delimitado de páginas revisadas, ¿cuántas páginas recuperó correctamente el Índice Universal y cuántas recuperó u omitió indebidamente?

La prueba compara el motor real del Índice Universal con una referencia externa. Calcula TP (relevante y recuperada), FP (no relevante pero recuperada), FN (relevante pero omitida) y TN (no relevante ni recuperada); reporta precisión, exhaustividad/recall, F1 y especificidad **sólo para la muestra etiquetada**. Una muestra sintética permite probar el código, pero no produce una estimación de calidad del corpus.

No sustituye los estados canónicos de LTMD: \`ocr_available != text_verified\`, \`search_hit != historical_claim\`, \`zero_hits != demonstrated_absence\`. El resultado jamás eleva automáticamente \`semantic_ready\` ni \`human_validation_complete\`.

## Diseño de una referencia humana privada

1. Prerregistrar una pregunta histórica, el criterio operativo de relevancia, la expresión FTS5 exacta y sus variantes. Mantener el protocolo y el universo de muestreo fuera del repositorio público si incluyen datos restringidos.
2. Definir claramente el alcance del índice: generaciones, grado y ola. Extraer una **muestra independiente del conjunto de páginas elegibles**, no únicamente páginas que el buscador recuperó. Si se usan estratos, registrar pesos y probabilidades en un protocolo privado antes de estimar métricas poblacionales. El evaluador actual **no pondera estratos**, así que sus métricas son exclusivamente descriptivas de la muestra.
3. Revisar cada página contra una fuente visual legítima; etiquetar su pertinencia con independencia de la predicción del motor. Si las decisiones resultan ambiguas, documentar adjudicación y desacuerdos fuera de GitHub.
4. Registrar tanto resultados negativos como positivos. La omisión por OCR incorrecto es un posible FN aunque el término no aparezca en \`search_text\`.
5. Conservar anotaciones, URLs, imágenes, fragmentos, índices y expedientes privados exclusivamente en el entorno autorizado. Nunca adjuntarlos a una incidencia, pull request, CI o publicación pública.

La variable \`source_checked=true\` es una **declaración del expediente de referencia**, no una comprobación independiente de que alguien realizó la inspección; requiere supervisión y evidencias externas.

## Formato privado de entrada

Guardar bajo \`local/\` un JSON parecido al siguiente; los identificadores mostrados son **ficticios**:

\`\`\`json
{
  "version": "LTMD_U1_SEARCH_QUALITY_0.1",
  "reference_type": "human_adjudicated",
  "sampling_design": "independent_scope_sample",
  "query_expression": "democracia",
  "filters": {"generation": ["1993"], "grade_code": [], "wave": []},
  "labels": [
    {"page_id": "IDENTIFICADOR_PRIVADO_1", "relevant": true, "source_checked": true},
    {"page_id": "IDENTIFICADOR_PRIVADO_2", "relevant": false, "source_checked": true}
  ]
}
\`\`\`

Campos y restricciones:

- \`reference_type\`: \`human_adjudicated\` (revisión real de la imagen) o \`synthetic_fixture\` (sólo regresiones).
- \`sampling_design\`: \`independent_scope_sample\` o \`purposive_sample\`. En el segundo caso se advierte explícitamente la imposibilidad de extrapolar al corpus.
- \`query_expression\`: consulta exacta FTS5. Los filtros usan \`generation\`, \`grade_code\` y \`wave\` según el motor canónico. Cada página etiquetada debe pertenecer a ese ámbito.
- \`labels\`: entre 2 y 10,000 identidades privadas sin duplicados, con \`relevant\` booleano. Las referencias humanas exigen \`source_checked=true\`; se rechazan muestras sin clases positiva y negativa.
- El programa no descarga páginas ni crea anotaciones. No evalúa visión, OCR por carácter, concordancia entre evaluadores o validez conceptual de una categoría.

## Ejecución exclusivamente privada

Desde la raíz del repositorio, con el índice reconstruido y las etiquetas fuera de Git:

\`\`\`bash
python -m scripts.evaluate_u1_search_quality \
  --index local/ftrl/ltmd_u1_universal_index.sqlite \
  --reference local/evaluation/referencia_experta.json \
  --expected-index-sha256 HASH_CANONICO_DEL_INDICE \
  --output local/evaluation/reporte_agregado.json
\`\`\`

**La ruta del índice es ilustrativa:** usar la ruta canónica real del índice privado. El \`--expected-index-sha256\` es opcional, pero recomendable. El resultado incluye únicamente matriz de confusión agregada, métricas de la muestra, estado epistémico, avisos, versiones y hashes del índice y del JSON de referencia. No devuelve \`page_id\`, snippets, transcripciones OCR ni rutas privadas. Los hashes son recibos de ejecución, no permisos de redistribución de los archivos.

## Integración automática y criterios de salida

La CI incorpora \`tests/test_evaluate_u1_search_quality.py\`, que construye un índice SQLite FTS5 **completamente sintético** y cubre errores semánticos simulados, omisiones OCR simuladas, acentos, filtros, registros duplicados, referencia fuera de ámbito, fuentes humanas sin comprobación visual, búsquedas sin coincidencias, parámetros inválidos, verificación de SHA-256 y no divulgación de identificadores.

La CI **no** utiliza datos privados y **no** informa tasas de calidad real. En una segunda etapa hará falta ejecutar el instrumento con una muestra humana auténtica, auditar el diseño muestral y documentar intervalos de incertidumbre apropiados. No se ha establecido ni alcanzado un umbral de precisión/recall para declarar LTMD apto como producto; requerirá una decisión metodológica y comercial explícita.

## Gobierno

No crear una segunda base de datos pública de OCR ni exponer índices privados en GitHub Actions. Mantener abierta la compuerta de derechos [#2](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues/2). Esta implementación amplía la verificabilidad del proyecto sin cambiar su nivel de madurez comercial.
