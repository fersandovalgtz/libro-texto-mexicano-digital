# LTMD-U1 W3 — OCR técnico de Español/Lengua

Versión: `LTMD_U1_W3_SPANISH_OCR_0.1`.

- Identidades W3 cubiertas operacionalmente: **130/130**.
- Objetos canónicos procesados una sola vez: **114/114**.
- Aliases cubiertos por provenance sin recomputar OCR: **16** (byte-exactos: **8**; ruta 2018→2019: **8**).
- Huecos internos persistentes preservados sin renumeración: **8**.
- Páginas fuente canónicas procesadas: **20,765**.
- SHA-256 verificados: **20,765/20,765**.
- Texto detectado: **20,588/20,765 (99.15%)**.
- `no_text_detected`: **177**.
- `unresolved` en contenidos procesados: **0**.

El OCR íntegro no se persiste. Esta capa conserva sólo métricas técnicas y controles de procedencia. La confianza interna de Tesseract se usa para triage técnico y no equivale a exactitud textual validada.

## Nota de corrección

El primer render del reporte mostró por error `ruta 2018→2019: 0` debido a que el combinador buscaba el literal abreviado `route_alias_2018_to_2019`. La topología reconciliada usa el estado canónico `paired_route_alias_2018_to_2019`. El combinador quedó corregido y ahora exige además que `byte-exactos + ruta = aliases totales`, por lo que el desglose reproducible es **8 + 8 = 16**. Esta corrección afecta únicamente el contador descriptivo del reporte; no modifica páginas, hashes, OCR, canónicos ni provenance.

## Límite epistemológico vigente

No existe por ahora referencia humana para validación semántica. Por ello este producto autoriza PAGESTRUCT/FRAGSEG y análisis técnicos de estructura, reutilización y dependencia documental, pero no convierte clasificadores semánticos no validados en evidencia histórica primaria.
