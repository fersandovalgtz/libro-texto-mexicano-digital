# SEMB 0.2 — addendum de selección de configuración sintética

Fecha: 2026-08-15

Este addendum se fija antes de ejecutar Multilingual-E5 sobre el conjunto de desarrollo y antes de abrir `VALIDATION_B02`.

## Métodos candidatos que realmente se compararán

Para evitar una búsqueda excesiva, el desarrollo se reduce a dos funciones de categoría:

1. `average_anchor`: promedio normalizado de las tres anclas cortas de cada categoría;
2. `max_anchor`: máximo coseno entre el fragmento y cualquiera de las tres anclas de la categoría.

El score contrastivo “categoría menos media de las demás” no se usa para ranking porque, aplicado a un mismo vector y al mismo conjunto de categorías, es una transformación monotónica del score de categoría y no cambia el orden. El centrado global ya falló con SEMB 0.1 y no se repetirá.

## Prefijo E5

Todos los textos —anclas y frases a clasificar— se codifican con prefijo `query: `, siguiendo el uso simétrico recomendado para semantic similarity. No se mezclan `query:` y `passage:` porque no se está ejecutando recuperación asimétrica documento-consulta.

## Selección de función de categoría

En el conjunto de desarrollo se calcula para acciones y posiciones:

- top-1 accuracy;
- top-3 accuracy;
- mean rank de la categoría esperada;
- worst rank.

Se elige **una sola función común para acciones y posiciones** maximizando, en este orden lexicográfico:

1. suma de top-1 correctos en acciones + posiciones;
2. suma de top-3 correctos;
3. menor suma de mean ranks;
4. menor worst rank total;
5. en empate absoluto, preferir `max_anchor` porque conserva sentidos distintos y evita difuminarlos mediante promedio.

No se permitirá elegir una función diferente por categoría.

## Compuerta acción/no-acción

Se crean tres anclas positivas sintéticas de `actionness` y tres negativas de exposición sin consigna. Para una frase:

`action_gate_margin = max(sim a anclas positivas) - max(sim a anclas negativas)`.

Se evalúan thresholds preregistrados: `0.00, 0.02, 0.04, 0.06`.

Con 16 frases positivas de desarrollo y 8 negativos sintéticos de desarrollo, se elige el threshold que maximice balanced accuracy. Desempates:

1. mayor especificidad sobre negativos;
2. mayor threshold (opción más conservadora).

El threshold resultante queda congelado antes de abrir VALIDATION_B02.

## Multietiqueta e incertidumbre

Después de pasar la compuerta:

- siempre se conserva la categoría top-1;
- se conserva una segunda categoría si su score está dentro de `0.02` del top-1;
- se conserva una tercera si también está dentro de `0.02`; máximo 3 acciones;
- posiciones: top-1 + una segunda dentro de `0.02`; máximo 2 posiciones;
- `uncertain_B=1` si la compuerta está a menos de `0.02` por encima del threshold o si el margen top1-top2 es <`0.01`;
- `heading_candidate` y fragmentos <4 tokens permanecen sin acciones y `uncertain_B=1` independientemente del embedding.

Estos valores no se optimizan con VALIDATION_B02.

## Conjunto negativo de desarrollo

Distinto de los ocho negativos bloqueados de validación:

1. “La Tierra gira alrededor del Sol y completa una órbita en un periodo determinado.”
2. “El termómetro es un instrumento utilizado para conocer la temperatura.”
3. “Las plantas necesitan agua y luz para realizar diversos procesos vitales.”
4. “Una hipótesis es una explicación provisional que puede ponerse a prueba.”
5. “Los materiales presentan propiedades físicas diferentes.”
6. “La observación científica permite obtener información de los fenómenos.”
7. “Un modelo es una representación simplificada de un objeto o proceso.”
8. “La prevención ayuda a disminuir algunos riesgos para la salud.”

## Regla de no-retorno

Una vez que el script de desarrollo imprima la configuración elegida, esa configuración se incorporará a SEMB 0.2 y se ejecutará `VALIDATION_B02` una sola vez. No se regresará al conjunto de desarrollo para cambiar el modelo después de conocer la validación.
