# Criterios de aceptación preregistrados para SEMB 0.3

Versión: `SEMB03_ACCEPTANCE_0.1`

## Propósito

Este documento fija, **antes de disponer de la referencia humana**, las condiciones mínimas para considerar utilizable SEMB 0.3. Los umbrales no podrán modificarse después de observar el desempeño en la validación bloqueada de 160 fragmentos. Si el modelo falla, se registra el fallo y una versión posterior deberá usar un nuevo conjunto de validación independiente.

## Etapa 1 — calidad de la referencia humana

La referencia sólo podrá utilizarse para desarrollo si la doble codificación del subconjunto de 120 casos alcanza simultáneamente:

- acuerdo exacto de `actionable` ≥ 0.85;
- F1 multilabel media de acciones ≥ 0.75;
- F1 multilabel media de posiciones ≥ 0.70;
- ninguna categoría con al menos 10 positivos en la unión de ambos anotadores podrá tener F1 < 0.50 sin revisión explícita del manual;
- los desacuerdos deberán resolverse mediante una regla documentada, no mediante consulta a las salidas A/B ni a tendencias históricas.

Si estas condiciones no se cumplen, el problema se considera de **constructo/libro de códigos**, no del clasificador. Se revisa el manual y se realiza una nueva ronda de fiabilidad antes de desarrollar SEMB 0.3.

## Etapa 2 — desarrollo en 320 casos

El conjunto `development` puede utilizarse para comparar arquitecturas, seleccionar el gate de acción, calibrar reglas multilabel y definir incertidumbre. Está permitido optimizar sólo contra estos 320 casos y pruebas sintéticas previamente documentadas. Está prohibido consultar los 160 casos `locked_validation` durante esta etapa.

Antes de abrir validación deberán congelarse en un archivo versionado:

1. versión exacta del modelo y revisión;
2. anchors/prompts o pesos utilizados;
3. reglas de gate y multilabel;
4. umbrales de incertidumbre;
5. hash del código ejecutable;
6. métricas de desarrollo;
7. criterios de aceptación de este documento.

## Etapa 3 — validación bloqueada única

En los 160 casos bloqueados SEMB 0.3 deberá alcanzar simultáneamente:

### Detección de tarea (`actionable`)

- balanced accuracy ≥ 0.80;
- sensibilidad ≥ 0.75;
- especificidad ≥ 0.75.

### Acciones pedagógicas

Calculadas en los casos con referencia humana no ambigua:

- micro-F1 ≥ 0.75;
- macro-F1 sobre categorías con ≥5 positivos humanos ≥ 0.60;
- F1 por categoría ≥ 0.45 para toda categoría con ≥10 positivos humanos.

### Posiciones del estudiante

- micro-F1 ≥ 0.70;
- macro-F1 sobre categorías con ≥5 positivos humanos ≥ 0.55;
- F1 por categoría ≥ 0.40 para toda categoría con ≥10 positivos humanos.

### Cobertura e incertidumbre

- al menos 70% de los casos elegibles deberá recibir una salida no marcada globalmente como incierta;
- la incertidumbre no podrá diferir en más de 20 puntos porcentuales entre ninguna pareja de generaciones en el conjunto maestro una vez desplegado, salvo que una auditoría independiente demuestre una causa documental real;
- el sistema no deberá producir truncamiento silencioso: toda entrada que exceda la longitud admitida se marca explícitamente y queda fuera del análisis primario.

## Regla de decisión

**PASS:** se cumplen todos los mínimos de validación bloqueada. SEMB 0.3 puede congelarse como capa de producción y recién entonces se permite reconstruir la comparación histórica.

**CONDITIONAL:** las métricas globales pasan pero una categoría rara incumple un umbral por contar con menos de 10 positivos; esa categoría queda fuera de afirmaciones históricas primarias y se conserva como exploratoria.

**FAIL:** falla cualquier mínimo obligatorio. No se retoca el modelo contra los mismos 160 casos. El resultado se publica como fallo de validación y una versión posterior deberá definir un nuevo ciclo de desarrollo/validación.

## Regla anti-fuga

Las diferencias entre 1972, 1988, 1993 y 2014, los resultados A/B y los hallazgos exploratorios existentes **no son criterios de selección de SEMB 0.3**. Ningún parámetro puede justificarse porque produzca una trayectoria histórica más clara, plausible o atractiva.
