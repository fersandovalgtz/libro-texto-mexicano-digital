# LTMD-U1 W2 — estado técnico de Matemáticas 0.1

Corte actualizado: 29 de agosto de 2026.  
Estado: **capa técnica 0.2 completada; gate post-W11 satisfecho; FTRL pendiente de ejecución/archivo; semántica no abierta**.

## Universo congelado

W2 contiene **64 visores** de Matemáticas dentro de LTMD-U1. `claves.json` declara **13,656 posiciones**. Los 64 visores comparten la arquitectura pública estándar `x.js → claves.json → ag_clave/ag_pages`.

## Resolución de activos

La auditoría SHA-256 por 64 shards produjo:

- 59 visores `direct_asset_ready`;
- 1 visor con dos huecos internos: `H2008P4MA276`;
- 4 visores DMA 2018 con ruta declarada no servida: `H2018P3DMA`, `H2018P4DMA`, `H2018P5DMA`, `H2018P6DMA`.

Los dos huecos de `H2008P4MA276` fueron recuperados de forma unívoca mediante alineamiento de vecinos byte-idénticos, offset fijo y cero discrepancias. El manifiesto reconciliado conserva la anomalía original y añade la fuente efectiva.

Resultado reconciliado:

- **60/64 identidades con activos efectivamente resueltos**;
- **4/64 excepciones de routing aún no resueltas**;
- **2 JPEG recuperados criptográficamente**;
- ningún visor 2018 DMA recibe crédito por mera similitud de título, grado o cardinalidad.

## Dependencia documental y cómputo único

Entre los visores completos se demostraron tres aliases de contenido exacto, página por página, con SHA-256 y byte-size:

- `H1982P4MA388` → canónico `H1972P4MA083`, 258 JPEG;
- `H1982P5MA394` → canónico `H1972P5MA089`, 304 JPEG;
- `H1982P6MA399` → canónico `H1972P6MA094`, 194 JPEG.

Por tanto, las 60 identidades efectivamente resueltas corresponden a **57 contenidos canónicos que requieren cómputo**. Los tres aliases conservan identidad documental propia, pero no se vuelven a OCRizar ni segmentar.

## DMA 2018

La comparación de configuración 2018↔2019 mostró el mismo `ag_pages` por grado, pero `ag_clave` distinto. Esa evidencia es insuficiente para declarar identidad documental o byte-alias. Los cuatro DMA 2018 permanecen explícitamente fuera del cómputo mientras no exista una prueba documental o criptográfica suficiente.

## OCR técnico 0.2 — COMPLETADO

La capa `LTMD_U1_W2_MATH_OCR_0.2` procesó los 57 contenidos canónicos y representa 60/64 identidades de catálogo mediante tres aliases exactos.

- **11,945/11,945 páginas fuente canónicas verificadas por SHA-256**;
- **11,812/11,945 (98.89%)** con texto detectado;
- **133** `no_text_detected`;
- **0 unresolved**;
- OCR íntegro no persistido; sólo métricas y controles de procedencia.

El combine final de OCR terminó en `success`; no fue necesario usar el workflow de recuperación preparado como contingencia.

## PAGESTRUCT 0.2 — COMPLETADO

- **11,945** páginas clasificadas;
- **10,145** páginas elegibles para FRAGSEG.

## FRAGSEG 0.2 — COMPLETADO

- **10,145** páginas con al menos un fragmento;
- **135,727** fragmentos técnicos.

El cierre técnico está documentado en `docs/LTMD_U1_W2_COMPLETION.md`. Esta capa no constituye por sí misma validación FTRL, cierre archivístico ni validación semántica.

## Reactivación FTRL — 29 de agosto de 2026

W11 cerró en `main` y sus controles post-merge requeridos quedaron verdes. La rama canónica `ftrl/w2-matematicas` fue sincronizada con el `main` resultante (`a1f8c248966d5210860fce8651a9975a89560f9c`). Con ello queda satisfecho el gate secuencial W11 → W2 y puede iniciarse la ejecución FTRL de Matemáticas.

La apertura de W2 **no** promueve todavía estados del completion ledger. Hasta que exista validación distribuida exhaustiva y preservación privada persistente verificada:

- las 60 identidades fuente-admitidas permanecen `pending`;
- los cuatro DMA 2018 permanecen `blocked_active_retention`;
- `archival_status` permanece `not_started`;
- `text_verified=false` y `semantic_ready=false`.

El contrato de activación queda fijado en `docs/LTMD_U1_W2_FTRL_ACTIVATION_0_1.md`.

## Pipeline vigente

`57 canónicos técnicos ✅ → FTRL distribuido → evidencia pública text-free + handoff privado cifrado → validación exhaustiva → preservación persistente verificada → promoción canónica de 60 identidades`

Los tres aliases sólo pueden heredar cobertura FTRL tras conservar la prueba exact-byte ya registrada. Los cuatro DMA 2018 permanecen fuera de esa cadena y no pueden ser sustituidos por ediciones 2019.

## Regla epistemológica

- `asset_ready` no equivale a `ocr_ready`;
- `ocr_ready` no equivale a `fragseg_ready`;
- `fragseg_ready` no equivale a `ftrl_validated`;
- `ftrl_validated` no equivale a `semantic_ready`;
- un alias exacto permite reutilizar cómputo, pero no elimina la identidad de catálogo;
- una recuperación puntual de página no demuestra identidad bibliográfica entre libros completos;
- ninguna transición del ledger puede inferirse de evidencia temporal o de un job incompleto: requiere cómputo validado y cierre archivístico verificable.
