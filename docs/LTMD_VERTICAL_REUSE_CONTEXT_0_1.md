# LTMD — contexto transversal de reutilización para verticales 0.1

Versión: `LTMD_VERTICAL_REUSE_CONTEXT_0.1`.

Esta capa conecta un vertical temático ya definido con la infraestructura corpus-wide de LTMD-U1 **sin volver a seleccionar ni reclasificar sus páginas**. El insumo mínimo es un ledger privado con `page_id`; el builder exige mapeo completo contra el Índice Universal y calcula únicamente agregados seguros a partir de `LTMD_U1_REUSE_SIMILARITY_0.1`.

## Propósito

Los conteos temáticos longitudinales pueden incluir contenido repetido entre libros o generaciones. El contexto transversal permite advertir ese hecho sin confundir:

- igualdad de bytes fuente;
- igualdad de representación textual OCR/search;
- similitud aproximada;
- identidad documental, equivalencia curricular o significado histórico.

Ninguna señal crea aliases ni modifica el estado epistemológico del vertical.

## Primer caso real — lenguas indígenas

El ledger preregistrado 0.2 conserva 1,151 páginas candidatas. Las 1,151 se mapearon exactamente al Índice Universal; no hubo candidatas huérfanas.

El cruce corpus-wide identifica 136 páginas candidatas con alguna señal de reutilización o similitud, equivalentes a 11.8158% del ledger. De ellas, 124 tienen alguna señal que cruza generaciones. En las capas específicas:

- 28 páginas participan en reutilización exacta de fuente entre objetos; 24 cruzan generaciones;
- 40 participan en igualdad exacta de representación textual entre objetos; 36 cruzan generaciones;
- 98 participan en una señal aproximada de similitud; 18 alcanzan `near_exact_candidate`;
- 90 páginas candidatas participan en similitud aproximada que cruza generaciones;
- existen 49 pares de similitud en los que ambas páginas pertenecen al propio vertical, 9 de ellos `near_exact_candidate`.

Estas cifras **no corrigen ni validan** las 1,151 candidatas. Añaden contexto para interpretar tendencias y para que LTMD Analytics pueda advertir cuando una señal temática está parcialmente asociada con material repetido.

## Privacidad

El registro público no contiene `page_id`, IDs de objetos, pares concretos, OCR, snippets ni hashes por página. Publica únicamente cardinalidades, hashes de los tres artefactos de entrada y el estado científico.

## Estado científico

`result_state=exploratory_signal`, `human_validation_complete=false`. La selección indígena permanece `not_visually_validated` y la nueva capa de contexto no promueve resultados a `human_validated` ni `semantic_ready`.

## Reutilización futura

El builder es vertical-agnóstico: cualquier vertical posterior con un ledger privado de páginas puede reutilizar el mismo contrato. Esto evita duplicar lógica temática y convierte la advertencia de reutilización en una capacidad común de LTMD Research.
