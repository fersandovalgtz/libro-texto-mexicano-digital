# LTMD Documentary Genealogy Benchmark 0.2

Versión metodológica: `LTMD_DOCUMENTARY_GENEALOGY_BENCHMARK_0.2`

## Propósito

Este benchmark cuantifica continuidad, novedad, rotación y supervivencia de **representaciones documentales observables** entre generaciones del corpus LTMD-U1 sin utilizar validación humana ni convertir similitud computacional en equivalencia semántica.

Su unidad primaria no es una idea, tema, intención curricular ni significado pedagógico. Es una representación identificada por hashes ya presentes en el Universal Index privado.

Guardas obligatorias:

- `exact_hash_equality != semantic_equivalence`;
- `near_exact_candidate != exact_identity`;
- `similarity_candidate != semantic_equivalence`;
- `documentary_persistence != curricular_persistence`;
- `documentary_novelty != pedagogical_innovation`;
- `turnover != causal_replacement`;
- `automated_benchmark_passed != human_semantic_validation`;
- `reproducible != historically_true`.

## Entradas

### Obligatoria

Universal Index privado LTMD-U1 `LTMD_U1_UNIVERSAL_INDEX_0.1`.

Se leen únicamente para cálculo interno:

- `catalog_generation`;
- `canonical_viewer_key`;
- `source_sha256`;
- `search_text_sha256`;
- `ocr_char_count`;
- `ocr_word_count`.

Los hashes, identificadores de página, identificadores de objeto y OCR no se emiten en el resultado público.

### Opcional

Artefacto privado `LTMD_U1_REUSE_SIMILARITY_0.1`. Si está disponible, añade un canal de sensibilidad basado en pares `near_exact_candidate` y `similarity_candidate`. Este canal permanece separado de las métricas de identidad exacta.

## Tres canales

### `source`

Identidad por igualdad de `source_sha256`.

Es el canal más estricto: evidencia igualdad de la representación binaria fuente observada. No prueba que dos objetos bibliográficos sean la misma edición ni que su significado sea equivalente.

### `text_admissible`

Identidad por igualdad de `search_text_sha256`, limitada a páginas con al menos 200 caracteres OCR y 30 palabras OCR.

Permite sensibilidad sobre representación textual normalizada en páginas con información mínima suficiente. `ocr_available != text_verified` permanece vigente.

### `text_all`

Sensibilidad por `search_text_sha256` sin aplicar el gate de baja información. Se publica para mostrar cuánto dependen los resultados del filtro técnico de admisibilidad.

## Transiciones entre generaciones consecutivas

Para cada par cronológicamente adyacente `A → B` se calculan dos familias de denominadores.

### Representaciones distintas

Sea `H_A` el conjunto de hashes distintos en A y `H_B` el conjunto en B.

**Documentary Persistence Rate**

`|H_A ∩ H_B| / |H_A|`

Proporción de representaciones distintas observadas en A que vuelven a observarse en B.

**Documentary Novelty Rate**

`|H_B \ H_A| / |H_B|`

Proporción de representaciones distintas de B no observadas en A.

**Documentary Turnover Rate**

`|H_A Δ H_B| / |H_A ∪ H_B|`

Distancia de Jaccard entre conjuntos de representaciones. No implica reemplazo causal.

### Ocurrencias de página

Una representación puede aparecer varias veces dentro de una generación. Para evitar que la métrica de conjuntos oculte ese fenómeno, se construye también un matching exacto máximo por hash:

`matched(h) = min(count_A(h), count_B(h))`

La suma de esos matches permite calcular persistencia, novedad y turnover ponderados por ocurrencias de página sin exponer los hashes.

## Incertidumbre automatizada

### Bootstrap

Para cada transición, las representaciones de la unión quedan en tres clases observables:

- compartidas;
- sólo A;
- sólo B.

El runner aplica bootstrap multinomial determinista con semilla preregistrada. Por defecto usa 2,000 réplicas y reporta intervalos percentiles de 95% para persistencia, novedad y turnover de representaciones distintas.

Los intervalos cuantifican incertidumbre de remuestreo bajo esta unidad documental. No reparan sesgos de cobertura, OCR o procedencia y no representan incertidumbre semántica.

## Supervivencia documental

Para cada hash se toma su primera generación observada y se cuenta cuántos pasos generacionales consecutivos permanece presente hasta su primera ausencia.

Si alcanza la última generación disponible, se trata como censura a la derecha.

Se reporta una tabla Kaplan–Meier discreta y, cuando la curva cruza 0.5, la mediana de supervivencia en **pasos generacionales**.

Esta medida es una vida media descriptiva de representaciones observadas. No es la vida media de un concepto, contenido curricular o política educativa.

## Control negativo temporal

El orden cronológico real de las generaciones se compara con órdenes permutados. Para cada permutación se calcula la media de persistencia exacta entre pares adyacentes.

El resultado pregunta: ¿la adyacencia temporal observada concentra más continuidad documental exacta que una adyacencia arbitraria entre generaciones?

El `upper_tail_p_value` es un control computacional de estructura temporal. No es una prueba causal ni una prueba de significación histórica.

## Sensibilidad near-exact

Cuando se proporciona el artefacto privado de reuse/similarity, se agregan por transición adyacente:

- pares `near_exact_candidate`;
- pares `similarity_candidate`;
- total de pares no exactos verificados.

No se calculan tasas de persistencia exacta a partir de esos pares. Este canal es sólo una señal de sensibilidad para evaluar cuánto material casi idéntico queda fuera de la identidad por hash.

## Privacidad y derechos

La salida pública no contiene:

- hashes fuente o de texto;
- IDs de página;
- IDs de objeto;
- texto OCR;
- imágenes;
- PDF;
- pares de páginas individuales.

El benchmark opera sobre derivados técnicos. La política general de derechos del proyecto sigue gobernada por `DATA_LICENSE.md` y `docs/LTMD_HISTORICAL_CONTEXT_AND_RIGHTS.md`.

## Contrato reproducible

Implementación:

- `scripts/run_documentary_genealogy_benchmark.py`;
- `schemas/ltmd_documentary_genealogy_benchmark_0_2.schema.json`;
- `tests/test_documentary_genealogy_benchmark.py`;
- `tests/test_documentary_genealogy_schema.py`.

El CI ejecuta fixtures sintéticos cuya verdad formal es conocida por construcción y verifica:

- denominadores de conjuntos;
- denominadores por ocurrencias;
- separación del gate `text_admissible`;
- bootstrap determinista;
- supervivencia y censura;
- control negativo temporal;
- separación de near-exact y exact identity;
- privacidad de la salida;
- rechazo de hashes inválidos;
- conformidad Draft 2020-12 del JSON.

## Estado de ejecución sobre el corpus real

La arquitectura y los contratos 0.2 pueden validarse íntegramente en CI con datos sintéticos. La corrida completa sobre LTMD-U1 requiere el Universal Index privado —y, para sensibilidad near-exact, el SQLite privado de reuse/similarity—. Esos binarios no están versionados en GitHub y los runs históricos inspeccionados no conservan artefactos descargables.

Por esa razón, **no se publican cifras 0.2 del corpus real hasta ejecutar el runner contra los artefactos privados auténticos**. Las cifras reales disponibles hasta entonces son las de `LTMD Documentary Genealogy 0.1`, derivadas del manifiesto público ya materializado.

Esta restricción es deliberada: `missing_private_artifact != permission_to_infer_or_fabricate_results`.
