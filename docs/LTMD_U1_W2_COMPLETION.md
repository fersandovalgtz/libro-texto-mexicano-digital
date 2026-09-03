# LTMD-U1 W2 — cierre técnico de Matemáticas

Versión: `LTMD_U1_W2_COMPLETION_0.2`.

## Resultado ejecutivo

- Universo congelado: **64 visores**.
- Identidades con routing institucional resuelto: **64/64**.
- Excepciones de routing activas: **0/64**.
- JPEG recuperados criptográficamente en `H2008P4MA276`: **2**.
- Aliases documentales byte-idénticos: **3**.
- Contenidos canónicos computados en el corte OCR/PAGESTRUCT/FRAGSEG ya cerrado: **57**.
- Identidades representadas por ese corte downstream histórico: **60/64**.

## Cierre de routing DMA 2018 — 2 de septiembre de 2026

Los cuatro visores `H2018P3DMA`, `H2018P4DMA`, `H2018P5DMA` y `H2018P6DMA` dejaron de ser excepciones de routing después de una reverificación independiente read-only.

La ejecución GitHub Actions `33680203778` terminó en `success` y verificó el gate definido para las rutas institucionales. La evidencia técnica quedó en el artefacto `9866142958`, digest `sha256:e128a04a05b66835b53fa35870ef10203fdd9de5fe5fcd6b96c9f2229ff65a19`.

El cierre de routing **no** convierte esas cuatro identidades en OCR/FTRL validadas. Tampoco demuestra alias con 2019.

## OCR 0.2 — corte histórico

- Páginas canónicas procesadas: **11,945**.
- SHA-256 verificados: **11,945/11,945**.
- Texto detectado: **11,812**.
- `no_text_detected`: **133**.
- `unresolved`: **0** dentro de los 57 contenidos computados.

## PAGESTRUCT 0.2 — corte histórico

- Páginas clasificadas: **11,945**.
- Páginas elegibles para FRAGSEG: **10,145**.

## FRAGSEG 0.2 — corte histórico

- Páginas con ≥1 fragmento: **10,145**.
- Fragmentos técnicos: **135,727**.

## Cobertura y siguiente capa

Los 57 contenidos canónicos reciben el procesamiento downstream histórico ya cerrado. Los tres aliases exact-byte heredan cobertura sólo bajo la prueba criptográfica registrada. Los cuatro DMA 2018 ahora tienen routing resuelto, pero deben pasar por una ejecución downstream específica antes de promover su estado en OCR, PAGESTRUCT, FRAGSEG o FTRL.

## Límite epistemológico

Este cierre separa explícitamente dos capas:

`routing_resolved != downstream_processed`

`downstream_processed != ftrl_validated`

`ftrl_validated != semantic_ready`

La resolución de una ruta técnica no autoriza inferencias semánticas ni equivalencias documentales entre ciclos.
