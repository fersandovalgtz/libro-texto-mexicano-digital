# FRAGSEG — LTMD-U1 W1 1966

Versión: `FRAGSEG_LTMD_U1_W1_1966_0.1`.

- Libros: **2**.
- Páginas elegibles PAGESTRUCT: **313**.
- Páginas con ≥1 fragmento: **313**.
- Páginas elegibles sin fragmentos: **0**.
- Fragmentos: **4,618**.
- IDs únicos: **4,618**.
- Páginas con huecos legítimos de secuencia: **37**.
- Slots omitidos: **39**.

## Tipos candidatos
- `activity_candidate`: 29.
- `experiment_candidate`: 24.
- `expository_candidate`: 946.
- `instruction_candidate`: 736.
- `question_candidate`: 257.
- `short_residual_candidate`: 2,626.

## Regla
`fragment_sequence` conserva la posición previa al descarte de candidatos de 0 tokens; se admiten huecos positivos auditados sin renumerar IDs. Cualquier fallo de descarga, SHA u OCR de ejecución hace fallar el shard. El texto completo no se persiste. Esta capa es técnica, no `semantic_ready`.
