# FRAGSEG — Ciencias Naturales Ola 2

Versión: `FRAGSEG_CN_WAVE2_0.1`.

- Libros: **19**.
- Páginas elegibles PAGESTRUCT: **2,528**.
- Páginas con ≥1 fragmento: **2,528**.
- Páginas elegibles sin fragmentos: **0**.
- Fragmentos: **36,195**.
- IDs únicos: **36,195**.
- Páginas con huecos legítimos de secuencia: **80**.
- Slots omitidos: **97**.

## Tipos candidatos
- `activity_candidate`: 1,096.
- `assessment_candidate`: 191.
- `experiment_candidate`: 446.
- `expository_candidate`: 4,897.
- `instruction_candidate`: 4,720.
- `project_candidate`: 432.
- `question_candidate`: 5,990.
- `short_residual_candidate`: 18,423.

## Regla
`fragment_sequence` conserva la posición previa al descarte de candidatos de 0 tokens; por eso se admiten huecos positivos y auditados sin renumerar IDs. Cualquier fallo de descarga, SHA u OCR de ejecución hace fallar el shard. El texto completo no se persiste. Esta capa sigue siendo técnica, no `semantic_ready`.
