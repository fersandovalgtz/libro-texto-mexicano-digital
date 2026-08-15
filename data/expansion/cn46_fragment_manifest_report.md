# FRAGSEG — expansión CN4/CN6

Versión: `FRAGSEG_CN46_0.1`.

- Libros: **9**.
- Páginas con al menos un fragmento: **1,559**.
- Fragmentos: **19,067**.
- IDs de fragmento únicos: **19,067**.
- Páginas con huecos legítimos de secuencia: **34**.
- Slots omitidos por descarte de candidatos de 0 tokens: **40**.

## Tipos candidatos
- `activity_candidate`: 427.
- `assessment_candidate`: 36.
- `experiment_candidate`: 234.
- `expository_candidate`: 3,183.
- `instruction_candidate`: 2,906.
- `project_candidate`: 87.
- `question_candidate`: 3,711.
- `short_residual_candidate`: 8,483.

## Regla
La expansión usa `short_residual_candidate` desde su primera versión; no se reutiliza el nombre `heading_candidate`. Cada página fuente fue reconstruida y verificada por SHA-256 antes de OCR/segmentación. El texto no se persiste, sólo `text_sha256` y metadatos de unidad.

## Integridad de secuencia
`fragment_sequence` conserva la posición de la unidad candidata anterior al descarte de unidades de 0 tokens. Por ello pueden existir huecos sin que falten fragmentos válidos. Los IDs no se renumeran retrospectivamente; se auditan secuencias positivas y únicas y se publica la lista de páginas con huecos.

## Por libro
- `LTMD-CN4-G1972`: páginas=188; fragmentos=1455.
- `LTMD-CN6-G1972`: páginas=145; fragmentos=1462.
- `LTMD-CN4-G1988`: páginas=187; fragmentos=1496.
- `LTMD-CN6-G1988`: páginas=192; fragmentos=1493.
- `LTMD-CN4-G1993`: páginas=145; fragmentos=2408.
- `LTMD-CN6-G1993-DH`: páginas=230; fragmentos=3492.
- `LTMD-CN6-G1993-CN`: páginas=189; fragmentos=1486.
- `LTMD-CN4-G2014`: páginas=129; fragmentos=2385.
- `LTMD-CN6-G2014`: páginas=154; fragmentos=3390.
