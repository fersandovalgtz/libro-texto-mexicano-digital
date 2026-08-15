# Plan de análisis histórico posterior a validación

Versión: `HISTORICAL_ANALYSIS_PLAN_0.2`

## Condición de activación

Este plan sólo se ejecutará para análisis primario después de que SEMB 0.3 pase la validación bloqueada preregistrada. Hasta entonces, los resultados históricos existentes son exploratorios.

## Universo descriptivo

El piloto es un censo computacional de los fragmentos recuperados de **cuatro volúmenes seleccionados** de Ciencias Naturales de quinto grado asociados a las generaciones 1972, 1988, 1993 y 2014. No constituye una muestra probabilística de todos los libros de texto mexicanos. Por ello, intervalos y pruebas de sensibilidad cuantifican estabilidad analítica dentro del corpus seleccionado; no autorizan por sí solos generalización estadística a todo el sistema educativo nacional.

## Variables primarias

1. Prevalencia de cada acción pedagógica validada por generación.
2. Prevalencia de cada posición del estudiante validada por generación.
3. Familias preregistradas de acciones y posiciones.
4. Proporción de fragmentos sin acción explícita.
5. Proporción de salidas inciertas y cobertura efectiva del clasificador.

Las categorías que queden como `CONDITIONAL` en la validación SEMB 0.3 se reportarán por separado y no sostendrán afirmaciones históricas primarias.

## Contrastes temporales preregistrados

Se mantienen cuatro contrastes:

- 1972 → 1988;
- 1988 → 1993;
- 1993 → 2014;
- 1972 → 2014.

Para cada categoría se reportarán prevalencia inicial/final, diferencia absoluta en puntos porcentuales y razón de prevalencias cuando el denominador lo permita. La dirección del cambio no se seleccionará post hoc.

## Denominadores

El denominador primario será el conjunto de fragmentos semánticamente elegibles según la capa de fragmentación/tipificación que haya sido validada antes del análisis. Se publicarán explícitamente por generación:

- fragmentos fuente;
- fragmentos elegibles;
- fragmentos con salida cierta;
- fragmentos inciertos;
- fragmentos excluidos por razones técnicas.

No se permitirá cambiar el denominador para maximizar una diferencia histórica.

## Incertidumbre y sensibilidad

Se publicarán al menos tres vistas:

1. **principal:** salidas SEMB 0.3 que cumplen los criterios de certeza congelados;
2. **cobertura total:** todas las salidas, conservando una bandera de incertidumbre;
3. **sensibilidad metodológica:** comparación con el clasificador de reglas A y, cuando corresponda, con SEMB 0.2, identificando coincidencia, divergencia y dependencia del método.

La sensibilidad no podrá utilizarse para escoger retrospectivamente el método que produzca el resultado más claro.

## Unidad de dependencia

Los fragmentos de una misma página no son observaciones independientes. Cuando se calculen intervalos de estabilidad se utilizará remuestreo por **página** como unidad de clúster, no bootstrap ingenuo de fragmentos. Debido a que hay un solo volumen por generación en este piloto, esos intervalos describirán sensibilidad interna a la composición de páginas y no variación entre libros posibles.

## Multiplicidad

El informe mostrará todas las categorías preregistradas, no sólo las que cambien más. Si se calculan pruebas inferenciales exploratorias por múltiples categorías, se acompañarán de control FDR Benjamini–Hochberg y se etiquetarán explícitamente como exploratorias. La interpretación primaria se basará en magnitud, dirección, estabilidad metodológica y contexto histórico, no en un umbral aislado de p.

## Umbrales de magnitud

No se fijará una diferencia mínima como criterio de 'importancia histórica' antes de observar SEMB 0.3, porque la relevancia depende de la categoría y del contexto. Sin embargo, toda afirmación deberá reportar la magnitud absoluta completa y el denominador; cambios equivalentes a uno o pocos fragmentos no se presentarán retóricamente como transformaciones sustantivas.

## Contextualización historiográfica

Las tendencias computacionales se confrontarán con reformas curriculares, programas oficiales, libros para el maestro y literatura historiográfica pertinente. Esa contextualización servirá para interpretar mecanismos plausibles, no para redefinir categorías después de observar resultados.

## Transparencia negativa

Se publicarán también categorías estables, resultados nulos, categorías con baja fiabilidad, discrepancias entre métodos y fallos de cobertura. El objetivo es describir qué evidencia soporta el corpus y qué evidencia no soporta.
