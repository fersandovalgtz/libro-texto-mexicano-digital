# LTMD-U1 — estado técnico derivado por máquina

Versión: `LTMD_U1_TECHNICAL_STATUS_0.1`.

Este documento se reconstruye desde los artefactos versionados del repositorio. No convierte la disponibilidad de una capa técnica en validación semántica.

## Frontera epistemológica vigente

El proyecto opera temporalmente sin referencia humana. OCR, PAGESTRUCT, FRAGSEG, hashes exactos, provenance y dependencia documental pueden avanzar. CER/WER validado contra referencia, confiabilidad intercodificador, consenso humano y validación SEMB03 permanecen cerrados. `SEMB03` sigue en `WAITING_HUMAN_REFERENCE`.

## W2 — Matemáticas

Estado técnico: **`complete`**. Véase `docs/LTMD_U1_W2_COMPLETION.md` para el cierre congelado.

## W3 — Español/Lengua

Estado técnico derivado: **`ocr_complete`**.

- Identidades: **130**.
- Objetos canónicos: **114**.
- Aliases por provenance: **16**.
- Páginas fuente canónicas: **20,765**.
- Huecos internos persistentes: **8**.
- Páginas OCR: **20,765**.
- SHA verificados: **20,765**.
- Texto detectado: **20,588**.
- Sin texto detectado: **177**.
- Unresolved: **0**.

## W4 — Ciencias Sociales

Estado técnico derivado: **`complete`**.

- Identidades: **14**.
- Objetos canónicos: **14**.
- Aliases por provenance: **0**.
- Páginas fuente canónicas: **2,414**.
- Huecos internos persistentes: **0**.
- Terminales sintéticos excluidos: **14**.
- Páginas OCR: **2,414**.
- SHA verificados: **2,414**.
- Texto detectado: **2,397**.
- Sin texto detectado: **17**.
- Unresolved: **0**.
- Páginas elegibles FRAGSEG: **2,018**.
- Fragmentos técnicos: **21,380**.
- IDs de fragmento únicos: **21,380**.
- Unidades textuales exactas únicas: **17,735**.
- Unidades exactas repetidas: **2,503**.
- Unidades presentes en ≥2 visores: **2,454**.
- Pares de visores con solapamiento exacto: **85**.

### PAGESTRUCT

- `textual`: 1,417.
- `mixed_text_image`: 601.
- `visual_only`: 179.
- `front_matter`: 1.
- `toc_or_navigation`: 33.
- `bibliography_or_credits`: 34.
- `unknown`: 149.

### Tipos FRAGSEG candidatos

- `activity_candidate`: 136.
- `assessment_candidate`: 5.
- `experiment_candidate`: 69.
- `expository_candidate`: 5,450.
- `instruction_candidate`: 3,145.
- `project_candidate`: 9.
- `question_candidate`: 1,707.
- `short_residual_candidate`: 10,859.

## Regla de lectura

Los conteos anteriores son controles de infraestructura científica. `text_detected` no es CER/WER; las clases PAGESTRUCT son estructurales; los tipos FRAGSEG son candidatos técnicos; y la igualdad de hash sólo documenta igualdad dentro de la representación técnica correspondiente.
