# Especificación de comparación histórica computacional 0.1

Fecha de preregistro: 2026-08-15

## Estado temporal del preregistro

Se fija después de congelar RULEA 0.1 y **antes de disponer de resultados A/B del corpus**. SEMB 0.2 sólo podrá producir B si supera VALIDATION_B02; si B queda bloqueado, esta especificación permanece en espera y no se sustituye por una comparación A-only presentada como equivalente.

## Unidad y universo

Universo fuente analítico: `FRAGSEG_0.2`, 9,594 fragmentos procedentes de 639 páginas clasificadas `textual` o `mixed_text_image` por PAGESTRUCT 0.2.

Generaciones documentales:

- catálogo 1972;
- catálogo 1988;
- catálogo 1993, cuya obra piloto verificó primera edición bibliográfica 1998;
- catálogo 2014, tercera edición revisada 2014.

Nunca se convertirá `catalog_generation=1993` en “edición 1993”. En tablas históricas se conservarán ambos niveles cuando proceda.

## Estratos obligatorios

Toda tabla principal incluirá, como mínimo:

1. `all_body_fragments`: todos los 9,594 fragmentos;
2. `nonheading`: excluye `candidate_type=heading_candidate`;
3. `certain_nonheading`: excluye headings y cualquier `uncertain_A OR uncertain_B`;
4. `textual_only_certain_nonheading`: además restringe `source_structure_class=textual`;
5. `mixed_text_image_certain_nonheading`: mismo criterio para páginas mixtas, como análisis de sensibilidad de layout.

La **comparación histórica principal** usa `certain_nonheading`. Los demás estratos funcionan como controles.

## Tres especificaciones que deben coexistir

Por cada acción y posición se reportan por separado:

- `A_rate`: prevalencia RULEA 0.1;
- `B_rate`: prevalencia SEMB validado;
- `consensus_positive_rate`: A=1 y B=1.

También se reporta:

- `method_sensitive_rate`: A≠B;
- `consensus_negative_rate`: A=0 y B=0.

No se reemplazan A/B por una etiqueta adjudicada única.

## Denominadores

### Prevalencia primaria

Número de fragmentos positivos / todos los fragmentos del mismo estrato y generación. Se expresa como proporción y por 100 fragmentos.

### Composición entre fragmentos con acción

Para acciones se genera una segunda tabla cuyo denominador son sólo los fragmentos que poseen **al menos una acción consensus-positive**. Permite separar “cantidad de consignas de acción” de “composición cognitiva de las consignas”.

Para posiciones se aplica análogo denominador entre fragmentos con al menos una posición consensus-positive.

## Transiciones preregistradas

Se calculan exactamente estas cuatro comparaciones:

- 1972 → 1988;
- 1988 → 1993/ed.1998;
- 1993/ed.1998 → 2014;
- 1972 → 2014.

Para cada categoría y especificación A/B/consenso:

- prevalencia inicial;
- prevalencia final;
- diferencia absoluta en puntos porcentuales;
- razón de prevalencias cuando la prevalencia inicial >0;
- dirección `increase`, `decrease` o `no_change` cuando la diferencia exacta es 0.

No se introduce un umbral ad hoc de “importancia” antes de observar magnitudes.

## Robustez direccional

Una transición/categoría recibe `directionally_robust=1` sólo cuando:

1. A, B y consenso tienen la misma dirección no nula; y
2. la categoría no está dominada por casos inciertos porque la tabla procede de `certain_nonheading`.

Si A y B cambian en direcciones contrarias, se etiqueta `method_sensitive_direction` y no se utiliza para una afirmación histórica principal.

## Comparación de posiciones del alumno

La lectura central del piloto se organizará en tres familias interpretativas, sin modificar las etiquetas de base:

- **recepción/ejecución:** `receiver`, `instruction_follower`;
- **indagación/razonamiento:** `observer`, `experimenter`, `investigator`, `reasoner`;
- **agencia social:** `collaborator`, `decision_maker`, `community_agent`.

Estas familias son agregados interpretativos; las nueve posiciones originales se conservan y reportan siempre.

## Comparación de acciones

Además de las 16 acciones individuales se producirán agregados descriptivos preregistrados:

- **recepción/recuperación:** `recall`, `describe`;
- **observación/medición:** `observe`, `measure`;
- **razonamiento:** `explain`, `compare`, `classify`, `predict`, `infer`, `solve`;
- **indagación experimental:** `experiment`, `investigate`;
- **producción/interacción:** `discuss`, `create`;
- **agencia/acción:** `decide`, `act_on_environment`.

Los agregados se cuentan a nivel fragmento mediante OR: un fragmento con dos acciones de la misma familia cuenta una sola vez para la prevalencia de esa familia.

## Estadística inicial

La primera prueba historiográfica será descriptiva y reproducible. No se añaden pruebas de significación inferencial en 0.1. Motivo: los fragmentos no son observaciones independientes en sentido clásico; están anidados en sólo cuatro libros/documentos. Los efectos se describen mediante prevalencias, diferencias absolutas, razones y estabilidad metodológica A/B.

Cualquier modelo inferencial posterior requerirá una especificación nueva que trate explícitamente la estructura documental y no se añadirá para obtener significación post hoc.

## Salidas

Si B supera validación y auditoría:

- `fragment_analysis_dataset.csv` — unión derivada por `fragment_id`, sin texto;
- `historical_action_prevalence.csv`;
- `historical_position_prevalence.csv`;
- `historical_action_composition.csv`;
- `historical_position_composition.csv`;
- `historical_transitions.csv`;
- `historical_family_prevalence.csv`;
- `historical_comparison_summary.md` — lectura computacional provisional, explícitamente condicionada por estabilidad A/B.

## Regla de interpretación

No se afirmará que “los libros cambian pedagógicamente” a partir de una diferencia exclusiva de A o B. Las afirmaciones históricas principales deben apoyarse en dirección convergente A/B, señal de consenso y controles de layout/incertidumbre. El desacuerdo es un resultado metodológico y se conserva.
