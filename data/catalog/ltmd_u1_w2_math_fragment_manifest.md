# FRAGSEG — LTMD-U1 W2 Matemáticas

Versión: `FRAGSEG_LTMD_U1_W2_MATH_0.2`.

- Visores canónicos computados: **57**.
- Identidades de catálogo representadas efectivamente: **60/64** mediante 3 aliases exactos.
- Páginas elegibles PAGESTRUCT: **10,145**.
- Páginas con ≥1 fragmento: **10,145**.
- Páginas elegibles sin fragmentos: **0**.
- Fragmentos: **135,727**.
- IDs únicos: **135,727**.
- Páginas con huecos legítimos de secuencia: **580**.
- Slots omitidos: **702**.

## Tipos candidatos
- `activity_candidate`: 3,491.
- `assessment_candidate`: 184.
- `experiment_candidate`: 2,097.
- `expository_candidate`: 14,301.
- `instruction_candidate`: 18,660.
- `project_candidate`: 62.
- `question_candidate`: 28,102.
- `short_residual_candidate`: 68,830.

## Regla
`fragment_sequence` conserva la posición previa al descarte de candidatos de 0 tokens; se admiten huecos positivos auditados sin renumerar IDs. Cualquier fallo de descarga, SHA u OCR de ejecución hace fallar el shard. El texto completo no se persiste. `short_residual_candidate` sigue siendo una categoría técnica residual, no evidencia tipográfica ni pedagógica. Esta capa no es `semantic_ready`. Los cuatro DMA 2018 permanecen excluidos hasta resolver su routing.
