# Protocolo de acuerdo entre codificadores/revisiones 0.1

## Objetivo

Cuantificar y documentar la consistencia con que se aplica `CODEBOOK_0_1.md` antes de usar sus categorías para una comparación histórica o para entrenar reglas/modelos automáticos.

La finalidad no es obtener un número de “confiabilidad” aislado, sino identificar **fronteras conceptuales que requieren aclaración**.

## Principio de conservación

Nunca sobrescribir un desacuerdo con la decisión final.

Para cada fragmento sometido a doble revisión deben conservarse tres capas:

1. **Código A** — primera decisión independiente;
2. **Código B** — segunda decisión independiente, sin consultar el código A;
3. **Código final/adjudicado** — decisión después de comparar y documentar el desacuerdo.

## Universo

La validación final prevista contiene **100 fragmentos**, 25 por generación.

### Primera codificación

Los 100 fragmentos reciben Código A.

### Doble codificación

Se someterán a Código B **40 fragmentos**, diez por generación (40 % del corpus de validación).

La submuestra se fijará **después de que existan los 100 `sample_id` pero antes de que el revisor B vea los códigos de A**, mediante selección determinista:

1. separar por generación;
2. calcular SHA-256 de `sample_id + '|double-review-0.1'`;
3. ordenar por hash;
4. tomar los primeros diez de cada generación.

Así se evita escoger manualmente los casos “fáciles” o “interesantes”.

## Independencia

### Diseño preferido

Dos personas distintas realizan A y B de manera independiente.

### Si sólo existe un revisor humano disponible

Puede realizarse una segunda codificación ciega por la misma persona después de un intervalo suficiente, pero deberá reportarse como **consistencia intra-codificador**, no como acuerdo inter-codificador. No se presentará como equivalente metodológico a dos revisores independientes.

## Dimensiones sometidas a acuerdo

La primera evaluación formal se concentrará en:

1. `fragment_type`;
2. `pedagogical_actions`;
3. `student_positions`.

Las dimensiones temáticas se revisarán cualitativamente en esta fase y podrán incorporarse a una medición formal posterior si generan resultados analíticos centrales.

## Naturaleza multietiqueta

Las categorías no son mutuamente excluyentes. Por ejemplo:

`observe + compare + infer`

puede ser una codificación válida del mismo fragmento.

Por ello no debe reducirse el acuerdo a una sola categoría nominal.

## Métricas previstas

### 1. Acuerdo exacto del conjunto

Proporción de fragmentos en que A y B asignan exactamente el mismo conjunto de etiquetas.

Es una métrica exigente y se reportará por dimensión.

### 2. Jaccard por fragmento

Para dos conjuntos de códigos A y B:

`J = |A ∩ B| / |A ∪ B|`

Si ambos conjuntos son vacíos, el caso se registra por separado y no se usa para inflar artificialmente la media.

Reportar:

- media;
- mediana;
- distribución;
- por generación;
- por dimensión.

### 3. Acuerdo binario por etiqueta

Cada etiqueta se transforma en una variable presente/ausente. Para cada código con prevalencia suficiente se reportan:

- porcentaje de acuerdo;
- acuerdo positivo;
- acuerdo negativo;
- Cohen κ cuando sea interpretable.

### 4. Problema de prevalencia

Una κ baja puede coexistir con acuerdo observado alto cuando una categoría es muy rara. Por ello:

- no se interpretará κ aisladamente;
- si la prevalencia produce una paradoja evidente, se podrá calcular Gwet AC1/AC2 o una medida robusta equivalente;
- el informe conservará siempre prevalencia y matriz de desacuerdos.

### 5. Confusiones conceptuales

Se producirá una tabla cualitativa de pares problemáticos, por ejemplo:

- `observe` / `describe`;
- `recall` / `explain`;
- `experiment` / `instruction_follower`;
- `investigate` / búsqueda simple;
- `discuss` / `collaborator`;
- `decide` / selección de respuesta;
- `act_on_environment` / tema ambiental.

## Umbrales internos de preparación

No son estándares universales; son puertas de decisión del piloto.

Antes de automatizar se buscará:

- Jaccard medio ≥ **0.80** para acciones pedagógicas;
- Jaccard medio ≥ **0.80** para posiciones del alumno;
- acuerdo observado binario ≥ **0.90** en las etiquetas suficientemente frecuentes o justificación explícita de las excepciones;
- ausencia de una confusión sistemática no resuelta en alguna categoría analíticamente central.

No se “mejorará” una métrica eliminando casos difíciles.

## Adjudicación

Después de terminar B:

1. calcular el desacuerdo antes de discutir casos;
2. identificar patrones de confusión;
3. revisar los fragmentos discordantes;
4. registrar el motivo de la decisión final;
5. determinar si el problema es aplicación incorrecta o definición ambigua;
6. si cambia una definición, crear `CODEBOOK_0_2.md` y documentar qué códigos necesitan recodificación.

## Regla de recodificación

Si `CODEBOOK_0_2.md` modifica sustantivamente una categoría:

- identificar todos los fragmentos afectados;
- recodificarlos bajo la nueva versión;
- conservar A/B originales;
- registrar `codebook_version_final`;
- recalcular acuerdo sólo cuando ambas revisiones correspondan a definiciones comparables.

## Ceguera respecto de la hipótesis histórica

Durante la codificación:

- evitar consultar frecuencias acumuladas por generación;
- no usar la edad del libro como argumento interpretativo;
- cuando sea viable, el revisor B debe trabajar con `sample_id` y página sin consultar la codificación A;
- el acuerdo se calcula antes de producir la narrativa comparativa 1972–1988–1993/1998–2014.

## Salidas publicables

El repositorio puede publicar:

- IDs de fragmentos;
- códigos A/B/finales;
- versión del libro de códigos;
- estados de revisión;
- matrices de acuerdo;
- Jaccard y medidas por etiqueta;
- notas metodológicas resumidas que no reproduzcan el fragmento fuente.

Las transcripciones completas usadas para codificar permanecen fuera del repositorio mientras la política jurídica esté en amarillo.

## Criterio de avance

La comparación histórica definitiva de acciones pedagógicas **no comenzará** hasta:

1. completar A para los 100 fragmentos;
2. completar B para los 40 seleccionados;
3. calcular acuerdo;
4. adjudicar discordancias;
5. estabilizar el libro de códigos;
6. registrar la versión final usada para el análisis.
