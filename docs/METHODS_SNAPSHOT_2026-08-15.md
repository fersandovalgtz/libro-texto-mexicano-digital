# Libro de Texto Mexicano Digital — instantánea metodológica

Fecha de corte: **15 de agosto de 2026**.

## Alcance al corte

LTMD combina un piloto semántico intensivo y dos expansiones técnicas de la familia *Ciencias Naturales*.

El **piloto CN5** trabaja con cuatro volúmenes de quinto grado asociados a generaciones del catálogo histórico de 1972, 1988, 1993 y 2014: 759 imágenes reales y 9,594 fragmentos congelados. Es la única capa que llega actualmente a Rule A, SEMB 0.2 y comparación semántica exploratoria.

La expansión **CN4/CN6** incorpora nueve objetos adicionales: 1,897 posiciones declaradas, 1,888 JPEG reales y 19,067 fragmentos. La **Ola 2** incorpora 19 libros `full_direct`, 3,177 JPEG y 36,195 fragmentos. En conjunto las tres capas materializan **64,856 ocurrencias técnicas de fragmento**.

Esa cifra no se interpreta como 64,856 observaciones históricas independientes. El corpus contiene reutilización editorial, revisiones, objetos de reemplazo y aliases de catálogo demostrados; por ello LTMD distingue entre ocurrencia documental y contenido independiente.

## Pipeline consolidado

`fuente institucional → catálogo/identidad documental → resolución de activos → SHA-256 → OCR temporal → PAGESTRUCT → FRAGSEG → metadatos/hashes → [validación semántica] → clasificación → análisis histórico condicionado a validación`

Los textos OCR completos y embeddings no se publican como datos derivados del repositorio. Cuando una etapa necesita texto, se reconstruye de manera efímera desde la fuente y se verifica contra el SHA-256 persistido.

## Identidad documental y readiness de activos

La familia estricta *Ciencias Naturales* contiene **37 visores**. El readiness actual es:

- 31 `full_direct`;
- 4 `full_alias_same_bytes`;
- 2 `partial_internal_unserved`;
- 0 `not_resolved`;
- 35/37 visores con resolución completa de activos;
- tres posiciones internas no servidas en los dos objetos 2008 parciales.

Los cuatro visores 2018 se mantienen como entradas institucionales distintas, pero una auditoría de **652 pares de activos** demostró identidad SHA-256 y tamaño 652/652 respecto de los activos 2019 correspondientes. La relación se representa como alias de contenido y no como observación independiente.

Las posiciones 2008 no servidas se registran como `internal_unserved_position_observed`; no se interpretan como páginas bibliográficamente faltantes sin cotejo externo.

## OCR técnico

La cobertura OCR se interpreta como señal técnica, no como CER/WER.

- piloto CN5: 757/759 páginas con texto detectable;
- CN4/CN6: 1,880/1,888 (99.58%), 8 `no_text_detected`, 0 `unresolved`;
- Ola 2: 3,164/3,177 (99.59%), 13 `no_text_detected`, 0 `unresolved`;
- Ola 2: 3,177/3,177 SHA-256 fuente verificados antes de OCR.

Una página `no_text_detected` no se equipara a página vacía; puede ser material visual históricamente relevante.

## PAGESTRUCT

PAGESTRUCT separa función documental antes de inferencia pedagógica. No convierte sus categorías en constructos semánticos.

En Ola 2, las 3,177 páginas quedaron distribuidas en:

- `textual`: 1,459;
- `mixed_text_image`: 1,069;
- `visual_only`: 300;
- `toc_or_navigation`: 118;
- `bibliography_or_credits`: 80;
- `front_matter`: 1;
- `unknown`: 150.

Las categorías `textual` + `mixed_text_image` produjeron **2,528 páginas elegibles** para FRAGSEG.

## FRAGSEG y unidad de análisis

La estructura del piloto está congelada como FRAGSEG 0.2. La auditoría posterior reveló que `heading_candidate` era una denominación excesivamente fuerte: se aplicaba residualmente a unidades breves sin evidencia tipográfica suficiente.

`FRAGTYPE_0.3_SHADOW` conserva límites, IDs y hashes y sustituye la interpretación por `short_residual_candidate`. El universo potencial de fragmentos de ≥4 tokens aumenta de 5,037 a 7,429 (+2,392), pero esa ampliación permanece condicionada a validación humana.

La Ola 2 ya usa la nomenclatura conservadora y produjo **36,195 fragmentos únicos por ID** sobre 2,528/2,528 páginas elegibles. Su distribución es:

- `short_residual_candidate`: 18,423;
- `question_candidate`: 5,990;
- `expository_candidate`: 4,897;
- `instruction_candidate`: 4,720;
- `activity_candidate`: 1,096;
- `experiment_candidate`: 446;
- `project_candidate`: 432;
- `assessment_candidate`: 191.

Ochenta páginas conservan huecos legítimos de secuencia por 97 slots de cero tokens descartados. Los IDs no se renumeran retroactivamente.

## Dependencia documental

LTMD mantiene al menos tres vistas analíticas:

- `object view`: cada ocurrencia en su objeto;
- `unique-content view`: contenido idéntico agrupado;
- `revision view`: continuidad, sustitución y revisión entre objetos.

En CN4/CN6, 19,067 ocurrencias corresponden a 16,155 unidades textuales únicas; 1,857 unidades aparecen más de una vez y 1,731 aparecen en dos o más libros. CN4 1972↔1988 presenta reutilización masiva de páginas y texto; 2018↔2019 presenta alias byte-idéntico en los cuatro grados auditados.

La dependencia documental debe resolverse antes de interpretar el crecimiento del corpus como crecimiento equivalente de evidencia histórica.

## Clasificación semántica SEMB 0.2

SEMB 0.2 usa `intfloat/multilingual-e5-small`, revisión fijada, anchors en español y reglas preregistradas de gate, multilabel e incertidumbre. Se ejecutó sólo sobre el piloto congelado y se comparó con un clasificador de reglas independiente.

El diagnóstico demostró cobertura insuficiente: **99.49%** de los fragmentos quedaron globalmente inciertos y sólo 49 cumplen simultáneamente criterios de certeza de acción y posición. La longitud no explica por sí sola el fenómeno.

## Prueba sintética independiente de SEMB 0.2

Una batería de 105 casos educativos en español, creada después del congelamiento de SEMB 0.2 y sin texto del corpus histórico, permitió un diagnóstico externo sintético.

El gate alcanza balanced accuracy **0.526**, sensibilidad **0.597** y especificidad **0.455**. Estos resultados no sustituyen referencia humana, pero demuestran que la limitación no puede atribuirse únicamente a la composición histórica del piloto.

SEMB 0.2 se conserva como resultado metodológico negativo reproducible. No se baja el umbral observando qué historia resultaría más conveniente.

## SEMB 0.3 — diseño previo a humanos

Se congeló una muestra ciega de **480 casos**: 320 de desarrollo y 160 de validación bloqueada. Un subconjunto de 120 se reserva para doble codificación interanotador. La muestra cubre 312 páginas; la validación bloqueada cubre 138.

Los anotadores no reciben generación, rol development/locked, resultados automáticos ni otros indicadores capaces de inducir ajuste retrospectivo. Los criterios de aceptación y candidatos quedaron fijados antes de observar anotaciones humanas.

## Stage gates

- **G0:** infraestructura y evidencia prehumana.
- **G1:** fiabilidad de la doble codificación humana.
- **G2:** consenso/adjudicación de referencia de desarrollo.
- **G3:** desarrollo computacional sólo con humanos de desarrollo + material sintético permitido.
- **G4:** bloqueo criptográfico del modelo, configuración, código y criterios.
- **G5:** una sola apertura de los 160 casos de validación.
- **G6:** producción sólo si se superan criterios preregistrados.
- **G7:** reconstrucción del análisis histórico después de validación.

El evaluador G5 exige desempeño, cobertura, control de incertidumbre por generación y ausencia de truncamiento silencioso.

## Separación entre expansión técnica y experimento semántico

CN4/CN6 y Ola 2 están **`corpus_ready` pero no `semantic_ready`**. No se han convertido en una nueva narrativa histórica mediante Rule A, SEMB 0.2 ni SEMB 0.3.

Esta separación es deliberada: permite industrializar procedencia, OCR, estructura y segmentación sin que el tamaño del corpus influya en la calibración de un clasificador todavía no validado humanamente.

## Reproducibilidad operativa

Los workflows comprueban cardinalidades, hashes e invariantes antes de publicar. Los fallos se tratan como evidencia útil:

- SEMB B02 recuperó shards válidos después de un fallo de combine;
- CN4/CN6 rechazó una cardinalidad manual errónea;
- los gaps FRAGSEG se corrigieron sin renumerar IDs;
- las anomalías 2008/2018 sólo cambiaron de estado con evidencia específica;
- PAGESTRUCT Ola 2 recuperó sólo CN3/2019 después de que un runner se detuviera, reutilizando 18 shards válidos;
- FRAGSEG Ola 2 quedó idempotente;
- el verificador del artículo distingue ahora posiciones declaradas de activos JPEG reales.

## Plan histórico posterior a validación

Los contrastes preregistrados del piloto son 1972→1988, 1988→1993, 1993→2014 y 1972→2014. Se publicarán denominadores, cobertura, incertidumbre, resultados nulos y sensibilidad entre métodos. La dependencia de fragmentos se tratará a la escala documental apropiada.

La expansión a más objetos requerirá redefinir explícitamente el estimando histórico: no basta con agregar fragmentos mientras existen aliases y revisiones entre libros.

## Estado epistemológico al corte

La ingeniería de corpus de *Ciencias Naturales* está sustancialmente madura: 35/37 visores completamente resueltos, Ola 2 cerrada y **64,856 ocurrencias técnicas de fragmento** acumuladas. El principal bloqueo ya no es extracción ni segmentación.

Los hallazgos semánticos existentes permanecen **exploratorios**. La siguiente apertura legítima de la capa semántica depende de una referencia humana fiable y de superar los stage gates de SEMB 0.3. Hasta entonces, la expansión técnica y la documentación reproducible pueden continuar sin contaminar el experimento.
