# OCR técnico — expansión CN4/CN6

Versión: `CN46_OCR_0.1`. Todas las páginas se reconstruyen temporalmente y su SHA-256 se verifica antes del OCR.

- JPEG procesados: **1,888**.
- SHA-256 verificados: **1,888**.
- Texto detectado: **1,880/1,888 (99.58%)**.
- No-text: **8**.
- Unresolved: **0**.

## Por objeto
- `LTMD-CN4-G1972`: 214/214 text; no-text=0; unresolved=0; psm3=201, psm11=5, psm6=8.
- `LTMD-CN4-G1988`: 214/214 text; no-text=0; unresolved=0; psm3=204, psm11=3, psm6=7.
- `LTMD-CN4-G1993`: 178/178 text; no-text=0; unresolved=0; psm3=165, psm11=4, psm6=9.
- `LTMD-CN4-G2014`: 161/161 text; no-text=0; unresolved=0; psm3=153, psm11=1, psm6=7.
- `LTMD-CN6-G1972`: 209/210 text; no-text=1; unresolved=0; psm3=172, psm11=5, psm6=32.
- `LTMD-CN6-G1988`: 241/242 text; no-text=1; unresolved=0; psm3=218, psm11=0, psm6=23.
- `LTMD-CN6-G1993-CN`: 236/242 text; no-text=6; unresolved=0; psm3=208, psm11=5, psm6=23.
- `LTMD-CN6-G1993-DH`: 250/250 text; no-text=0; unresolved=0; psm3=249, psm11=0, psm6=1.
- `LTMD-CN6-G2014`: 177/177 text; no-text=0; unresolved=0; psm3=171, psm11=1, psm6=5.

## Restricción
`text_detected` mide cobertura técnica, no exactitud CER/WER. El OCR íntegro no se persiste. Páginas `no_text_detected` o `unresolved` se conservan como diagnósticos y no se sustituyen silenciosamente. Esta expansión permanece técnica y no adquiere estatus `semantic_ready` por completar OCR.
