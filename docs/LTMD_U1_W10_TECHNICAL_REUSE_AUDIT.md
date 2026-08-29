# LTMD-U1 W10 — auditoría de reutilización técnica byte-exacta

Versión: `LTMD_U1_W10_TECHNICAL_REUSE_AUDIT_0.1`.

## Resultado

- Identidades históricas: **69**.
- Cohorte productiva re-sondeada: **68/68**.
- Excepción final conservada fuera de procesamiento: **`H2014P1ENA`**.
- Objetos canónicos previos auditados: **68**.
- Páginas fuente actuales comparadas 1:1: **11,937/11,937**.
- Identidad `(viewer_key, source_image_index)`: **exacta**.
- URL oficial de activo: **exacta**.
- Tamaño en bytes: **exacto**.
- SHA-256: **exacto**.
- Digest global determinista de fuente: `5b703cd00195226597b6255b8eee981b8b29b651c8707cc802c193a6e80d75a7`.
- Validador estricto del cierre técnico existente: **PASS**.
- Recalcular OCR por deriva de fuente: **no requerido**.

## Alcance científico

La coincidencia byte-exacta de toda la cohorte productiva permite reutilizar los productos técnicos W10 ya calculados sin recomputar OCR, PAGESTRUCT, FRAGSEG y reutilización textual exacta. La autorización es estrictamente computacional: cualquier diferencia de índice, URL, tamaño o SHA-256 habría detenido el proceso.

`computationally_validated=true` no equivale a `archival_complete=true`. La preservación privada verificable sigue pendiente. Asimismo, `text_verified=false` y `semantic_ready=false`; permanece vigente `WAITING_HUMAN_REFERENCE`.
