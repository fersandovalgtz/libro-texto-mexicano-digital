# LTMD-U1 W2 — estado técnico de Matemáticas 0.1

Corte actualizado: 2 de septiembre de 2026.  
Estado: **routing institucional resuelto 64/64; downstream técnico histórico aún cubre 60/64 identidades; semántica no abierta**.

## Universo congelado

W2 contiene **64 visores** de Matemáticas dentro de LTMD-U1. `claves.json` declara **13,656 posiciones**. Los 64 visores comparten la arquitectura pública estándar `x.js → claves.json → ag_clave/ag_pages`.

## Resolución de activos

La auditoría actual conserva **64/64 identidades con routing institucional efectivo demostrado**.

El caso `H2008P4MA276` conserva dos huecos internos recuperados de forma unívoca mediante alineamiento de vecinos byte-idénticos, offset fijo y cero discrepancias. El manifiesto reconciliado mantiene la anomalía original y la fuente efectiva.

Los cuatro DMA 2018 que antes estaban retenidos fueron reverificados de forma independiente el 2 de septiembre de 2026:

- `H2018P3DMA`;
- `H2018P4DMA`;
- `H2018P5DMA`;
- `H2018P6DMA`.

La ejecución read-only `33680203778` terminó en `success` sobre `24d583372286c64459816da75d07cc8ee9914609`. El gate exigió 892 JPEG institucionales servidos en total, cuatro 404 terminales esperados, cero huecos internos, cero errores y coincidencia SHA-256 contra la evidencia técnica previamente versionada. El artefacto `u1-w2-dma2018-reverification` quedó registrado como `9866142958`, digest `sha256:e128a04a05b66835b53fa35870ef10203fdd9de5fe5fcd6b96c9f2229ff65a19`.

Este resultado satisface el criterio de cierre de routing del issue #4. No demuestra identidad con las ediciones 2019 y no autoriza alias entre ciclos.

## Cobertura downstream histórica

La resolución de routing no promueve automáticamente OCR, PAGESTRUCT, FRAGSEG o FTRL.

La capa técnica ya cerrada antes de esta reverificación continúa representando **60/64 identidades de catálogo** mediante **57 contenidos canónicos** y tres aliases exact-byte. Los cuatro DMA 2018 recién resueltos quedan pendientes de una ejecución downstream específica antes de cualquier promoción adicional.

## OCR técnico 0.2 — corte histórico cerrado

- **11,945/11,945 páginas fuente canónicas verificadas por SHA-256**;
- **11,812/11,945 (98.89%)** con texto detectado;
- **133** `no_text_detected`;
- **0 unresolved** dentro del universo computado de 57 contenidos canónicos.

## PAGESTRUCT 0.2 — corte histórico cerrado

- **11,945** páginas clasificadas;
- **10,145** páginas elegibles para FRAGSEG.

## FRAGSEG 0.2 — corte histórico cerrado

- **10,145** páginas con al menos un fragmento;
- **135,727** fragmentos técnicos.

## FTRL

La resolución de routing de los cuatro DMA 2018 no equivale a validación FTRL. Cualquier procesamiento posterior debe ejecutarse y preservarse como etapa separada con sus propios gates.

## Regla epistemológica

- `asset_ready` no equivale a `ocr_ready`;
- `ocr_ready` no equivale a `fragseg_ready`;
- `fragseg_ready` no equivale a `ftrl_validated`;
- `ftrl_validated` no equivale a `semantic_ready`;
- un alias exacto permite reutilizar cómputo, pero no elimina la identidad de catálogo;
- una ruta institucional recuperada no demuestra identidad bibliográfica entre libros de ciclos distintos;
- ninguna transición del ledger se infiere de la resolución de routing: requiere cómputo validado y cierre archivístico verificable.
