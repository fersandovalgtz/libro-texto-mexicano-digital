# Plan de análisis histórico — temporalidad y niveles de inferencia

Versión: `HISTORICAL_ANALYSIS_PLAN_0.3`

Supersede `HISTORICAL_ANALYSIS_PLAN_0.2` en la definición del eje temporal. Conserva sus principios de denominadores, dependencia por página, multiplicidad, sensibilidad y transparencia negativa, pero elimina la posibilidad de interpretar automáticamente las generaciones del catálogo como años editoriales.

## 1. Niveles de análisis

LTMD distingue tres niveles que no deben mezclarse:

### A. Descripción técnica del corpus

Puede ejecutarse sin referencia humana y comprende, entre otros:

- cobertura de fuente;
- OCR y estructura de página;
- fragmentación;
- reutilización textual exacta;
- dependencia documental;
- distribución de clases técnicas;
- comparación de perfiles computacionales.

Estas salidas describen la representación LTMD y no constituyen por sí mismas interpretación histórica o pedagógica.

### B. Análisis por cohortes del catálogo

Puede comparar grupos definidos por `catalog_generation` cuando la pregunta se formule explícitamente sobre la organización/cohorte institucional del Catálogo Histórico. Debe llamarse **comparación por generación/cohorte de catálogo**, no comparación por año de publicación.

### C. Análisis histórico-bibliográfico

Las afirmaciones sobre cambio editorial, circulación de ediciones, cronología, reformas o persistencia histórica requieren una temporalidad bibliográfica demostrada por objeto: `edition_year`, `reprint_year`, `school_cycle`, `copyright_year` u otra fecha primaria pertinente.

Una cohorte del catálogo sólo puede incorporarse a este nivel cuando su relación con la fecha histórica usada esté documentada explícitamente.

## 2. Regla temporal obligatoria

Todo análisis longitudinal debe declarar en métodos y tablas cuál eje temporal emplea:

- `catalog_generation`;
- `edition_year`;
- `reprint_year`;
- `school_cycle`;
- `copyright_year`;
- otra variable primaria documentada.

No se permite sustituir una por otra silenciosamente.

La evidencia interna de `H2014P5FCA` falsifica la igualdad automática entre cohorte y fecha editorial: el objeto está en `catalog_generation=2014`, pero su página legal institucional SHA-verificada declara `Primera edición, 2014` y `Tercera reimpresión, 2017 (ciclo escolar 2017-2018)`.

## 3. Cobertura bibliográfica y datos faltantes

La ausencia de una fecha bibliográfica verificable es un dato faltante, no una invitación a imputar el valor de `catalog_generation`.

Para cada análisis histórico-bibliográfico se publicará:

- número de objetos elegibles;
- número y proporción con temporalidad verificada;
- tipo de evidencia utilizado;
- número de objetos excluidos por fecha no demostrada;
- sensibilidad a la exclusión, cuando sea pertinente.

No se imputarán fechas por título, grado, cardinalidad, proximidad de cohorte, similitud visual, similitud OCR o reutilización textual.

## 4. Evidencia bibliográfica

La capa `data/catalog/ltmd_bibliographic_observations.csv` conserva observaciones atómicas con página y SHA de evidencia. Una fecha puede considerarse `verified` para análisis histórico sólo cuando la observación que la sustenta cumple el contrato de `docs/DATA_MODEL.md`.

Una lectura OCR con `human_validated=0` conserva procedencia fuerte de página, pero debe distinguirse de una transcripción humana validada. Si el análisis depende críticamente de una palabra o cifra OCR ambigua, la observación no se promueve por inferencia.

## 5. Contrastes históricos

Los antiguos contrastes 1972→1988→1993→2014 pueden conservarse **únicamente como contrastes entre generaciones de catálogo** mientras no exista una cronología bibliográfica completa para los objetos involucrados.

Si posteriormente las fechas editoriales se verifican, se construirá una tabla de correspondencia explícita entre:

- objeto;
- generación de catálogo;
- edición;
- reimpresión;
- ciclo escolar;
- fecha utilizada en el contraste.

La dirección del cambio y los contrastes primarios se fijarán antes de observar el resultado semántico correspondiente.

## 6. Denominadores y dependencia

El denominador primario debe estar definido antes del análisis y no cambiar para maximizar diferencias. Se publicarán por cohorte/fecha:

- páginas fuente y elegibles;
- fragmentos fuente y elegibles;
- salidas ciertas e inciertas cuando exista una capa semántica;
- exclusiones técnicas;
- exclusiones por temporalidad bibliográfica no demostrada.

Los fragmentos de una misma página no son observaciones independientes. Los intervalos de estabilidad usarán la página como unidad mínima de clúster. Cuando existan múltiples libros por grupo temporal, la dependencia entre páginas del mismo libro deberá modelarse también.

## 7. Semántica y referencia humana

El proyecto opera actualmente sin referencia humana suficiente para validar como primarias las categorías semánticas automáticas. Por ello:

- PAGESTRUCT, FRAGSEG y reuso exacto pueden sostener descripción técnica;
- categorías pedagógicas/semánticas automáticas siguen siendo instrumentales o exploratorias mientras no exista un régimen de validación suficiente;
- una diferencia técnica entre W3, W4 o W7 no debe redactarse como transformación curricular, pedagógica o histórica.

La ausencia de referencia humana cambia el nivel de inferencia admisible, no el estándar de procedencia y reproducibilidad.

## 8. Contextualización historiográfica

La vinculación con reformas curriculares, programas oficiales, libros para el maestro y literatura historiográfica debe realizarse después de establecer qué objetos y fechas están efectivamente representados. El contexto histórico puede explicar o problematizar un patrón; no puede utilizarse para fabricar la fecha bibliográfica de un objeto.

## 9. Multiplicidad, sensibilidad y transparencia negativa

Se mantienen las reglas de 0.2:

- reportar todas las categorías preregistradas, no sólo las llamativas;
- usar FDR para familias de pruebas inferenciales exploratorias cuando corresponda;
- privilegiar magnitud, dirección y estabilidad sobre un umbral aislado de `p`;
- publicar resultados nulos, baja cobertura, discrepancias entre métodos y fallos de fuente;
- no seleccionar retrospectivamente el método que produzca el resultado más claro.

## 10. Regla de publicación

Toda afirmación temporal en un artículo, dataset, visualización o API debe poder responder dos preguntas:

1. **¿qué variable temporal representa este eje?**
2. **¿qué evidencia primaria vincula cada objeto con ese valor?**

Si alguna respuesta no está disponible, la salida debe presentarse como comparación de cohortes del catálogo o como exploración técnica, no como cronología editorial demostrada.
