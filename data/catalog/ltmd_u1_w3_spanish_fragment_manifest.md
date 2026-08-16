# FRAGSEG — LTMD-U1 W3 Español/Lengua

Versión: `FRAGSEG_LTMD_U1_W3_SPANISH_0.1`.

- Objetos canónicos computados: **114**.
- Identidades de catálogo cubiertas operacionalmente: **130/130** mediante **16** aliases de provenance.
- Huecos internos de fuente persistentes preservados sin renumeración: **8**.
- Páginas elegibles PAGESTRUCT: **17,337**.
- Páginas con ≥1 fragmento: **17,337**.
- Páginas elegibles sin fragmentos: **0**.
- Fragmentos: **222,490**.
- IDs únicos: **222,490**.
- Páginas con huecos legítimos de secuencia: **653**.
- Slots omitidos: **832**.

## Tipos candidatos
- `activity_candidate`: 4,205.
- `assessment_candidate`: 605.
- `experiment_candidate`: 795.
- `expository_candidate`: 31,149.
- `instruction_candidate`: 30,694.
- `project_candidate`: 1,354.
- `question_candidate`: 26,322.
- `short_residual_candidate`: 127,366.

## Regla
`fragment_sequence` conserva la posición previa al descarte de candidatos de 0 tokens; se admiten huecos positivos auditados sin renumerar IDs. Cualquier fallo de descarga, SHA u OCR de ejecución hace fallar el shard. El texto completo no se persiste. `short_residual_candidate` es una categoría técnica residual, no evidencia tipográfica ni pedagógica. Esta capa no es `semantic_ready`.

## Límite actual
El proyecto opera temporalmente sin referencia humana. FRAGSEG puede usarse para estructura, conteos técnicos, reutilización exacta y dependencia documental; no valida por sí mismo categorías pedagógicas o semánticas.
