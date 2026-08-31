# LTMD-U1 — registro declarativo de verticales exploratorios 0.1

Versión: `LTMD_U1_VERTICAL_REGISTRY_0.1`.

## Propósito

Este registro fija, **antes de inspeccionar resultados**, las expresiones FTS5 y los límites interpretativos de los siguientes verticales exploratorios de LTMD Analytics. El objetivo es evitar scripts temáticos aislados y ajustes retrospectivos de términos en función de los resultados observados.

El primer vertical, lenguas indígenas, conserva su metodología y ledger preregistrado 0.2. Este registro cubre verticales temáticos adicionales derivados directamente del Índice Universal corpus-wide.

## Regla metodológica

Cada vertical define:

- `vertical_id` estable;
- etiqueta descriptiva;
- `union_expression` FTS5 para la selección exploratoria total;
- dos o más `probes` desagregados;
- límite explícito de interpretación.

Las expresiones quedan congeladas al fusionar este registro. La primera materialización real debe usar exactamente estas expresiones. Cualquier cambio posterior requiere nueva versión del registro y no puede sobrescribir silenciosamente resultados 0.1.

## Verticales preregistrados

1. ciudadanía, democracia y derechos;
2. mujeres, género y familia;
3. medio ambiente y naturaleza;
4. migración y movilidad;
5. trabajo y economía;
6. discapacidad e inclusión;
7. ciencia y tecnología;
8. nación, identidad y México.

## Dimensiones obligatorias

Toda materialización 0.1 debe producir agregados para el universo total y desgloses por:

- generación;
- grado;
- ola operacional.

Los denominadores deben provenir del mismo Índice Universal que resuelve los hits.

## Contexto de reutilización

Cuando sea técnicamente posible, cada vertical debe anexar el contexto agregado de `LTMD_U1_REUSE_SIMILARITY_0.1` para advertir qué parte de sus señales participa en reutilización exacta o similitud aproximada. Ese contexto no modifica la selección léxica ni crea aliases.

## Estado científico

Todos los verticales 0.1 quedan en `exploratory_signal`.

Las reglas permanentes siguen siendo:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`;
- `computational_candidate != semantic_ready`;
- `similarity_candidate != semantic_equivalence`.

Una coincidencia lexical no prueba presencia curricular, tratamiento pedagógico, valoración normativa, representación social ni cambio histórico. Esos niveles requieren validación humana y diseño analítico específico.

## Privacidad

La materialización pública puede incluir expresiones preregistradas, conteos, tasas, dimensiones, hashes de procedencia y contexto agregado de reutilización. No puede publicar OCR íntegro, snippets fuente, page IDs, object IDs privados, hashes de página ni pares concretos de similitud.
