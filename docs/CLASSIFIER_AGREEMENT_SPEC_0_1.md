# Especificación de acuerdo computacional A/B 0.1

Fecha de preregistro: 2026-08-15

## Propósito

Comparar RULEA 0.1 y SEMB 0.1 sin revisión ni adjudicación humana. El desacuerdo no se corrige: se conserva como evidencia sobre estabilidad metodológica de las categorías.

## Unidad

Una fila por `fragment_id` del manifiesto FRAGSEG 0.2. A y B deben cubrir exactamente el mismo conjunto de fragmentos y compartir el mismo `text_sha256` del manifiesto. Cualquier diferencia de cobertura/hash aborta el cálculo.

## Familias

Se evalúan por separado:

- 16 acciones pedagógicas;
- 9 posiciones del alumno.

No se mezclan acciones y posiciones en un único índice.

## Métricas por categoría

Para cada categoría y generación, más total:

- `n11`: A=1, B=1;
- `n10`: A=1, B=0;
- `n01`: A=0, B=1;
- `n00`: A=0, B=0;
- acuerdo binario `(n11+n00)/N`;
- acuerdo positivo `n11/(n11+n10+n01)`, equivalente a Jaccard binario de positivos;
- precisión de B respecto de A `n11/(n11+n01)` sólo como descriptor direccional, **no** como exactitud porque A no es gold standard;
- recall de B respecto de A `n11/(n11+n10)` con la misma cautela;
- prevalencia A y prevalencia B;
- diferencia absoluta de prevalencias.

No se utilizará kappa como métrica principal porque las categorías pueden tener prevalencias muy bajas y el objetivo es estabilidad entre especificaciones, no acuerdo entre observadores humanos. Puede calcularse después sólo como análisis suplementario si se documenta separadamente.

## Métricas por fragmento

Para cada fragmento:

- Jaccard del conjunto de acciones A vs. B;
- Jaccard del conjunto de posiciones A vs. B;
- exact-set agreement de acciones;
- exact-set agreement de posiciones;
- tamaño del conjunto A y B en cada familia;
- `uncertain_A`, `uncertain_B`;
- estrato de estabilidad:
  - `stable_exact`: conjuntos idénticos y ninguno incierto;
  - `stable_partial`: Jaccard ≥0.5 y ninguno incierto;
  - `method_sensitive`: Jaccard <0.5 y ninguno incierto;
  - `uncertain`: al menos una especificación marcada incierta.

Convención Jaccard: si ambos conjuntos son vacíos, Jaccard=1.0 y exact-set=1. Esta coincidencia vacía se reportará además separadamente para no inflar la interpretación substantiva.

## Agregados obligatorios

Por generación y total:

- media y mediana de Jaccard de acciones;
- media y mediana de Jaccard de posiciones;
- exact-set rate;
- empty-both rate;
- stable_exact/stable_partial/method_sensitive/uncertain;
- resultados all-fragments;
- resultados excluyendo fragmentos `heading_candidate`;
- resultados excluyendo `uncertain_A OR uncertain_B`;
- resultados por `source_structure_class` (`textual` vs `mixed_text_image`).

## Sensibilidad

SEMB 0.1 se evaluará bajo la regla principal preregistrada y, posteriormente, con su rejilla de umbrales. RULEA 0.1 no se recalibra para maximizar acuerdo con B. El acuerdo A/B no se usa para modificar retroactivamente las etiquetas de ninguna versión.

## Uso en interpretación histórica

Una categoría sólo puede sostener una afirmación histórica principal si:

1. su dirección temporal no depende exclusivamente de fragmentos `uncertain`;
2. RULEA y SEMB no producen tendencias generacionales contradictorias;
3. el resultado sobrevive al menos a una variante de sensibilidad B razonable;
4. la magnitud se reporta junto con el nivel de acuerdo metodológico.

Las categorías method-sensitive pueden seguir siendo un hallazgo metodológico, pero no se presentarán como cambio pedagógico robusto.
