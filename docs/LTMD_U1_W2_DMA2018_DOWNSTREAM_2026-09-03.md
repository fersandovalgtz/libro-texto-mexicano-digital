# LTMD-U1 W2 DMA 2018 — downstream computacional

Fecha: 2026-09-03
Issue canónico: #167

## Alcance

Esta fase procesa únicamente `H2018P3DMA`, `H2018P4DMA`, `H2018P5DMA` y `H2018P6DMA` después de la resolución de routing demostrada en #4 / PR #165.

No incluye validación humana. Por decisión operativa del 2026-09-03, la validación humana queda diferida. Ningún resultado de esta fase puede promover `semantic_ready=true` ni convertirse por sí solo en afirmación histórica.

## Evidencia de entrada

La reverificación read-only ejecutada en GitHub Actions run `33680203778` produjo el artefacto `9866142958`, digest `sha256:e128a04a05b66835b53fa35870ef10203fdd9de5fe5fcd6b96c9f2229ff65a19`.

Resultado:

- `H2018P3DMA`: 225/225 JPEG esperados; un 404 terminal; cero huecos internos; cero errores.
- `H2018P4DMA`: 257/257 JPEG esperados; un 404 terminal; cero huecos internos; cero errores.
- `H2018P5DMA`: 225/225 JPEG esperados; un 404 terminal; cero huecos internos; cero errores.
- `H2018P6DMA`: 185/185 JPEG esperados; un 404 terminal; cero huecos internos; cero errores.
- Total: 892 JPEG servidos.
- Coincidencia SHA-256 con evidencia previa: 892/892.
- Persistencia de cuerpos fuente durante la reverificación: ninguna.

## Estados que no se confunden

`routing_resolved != downstream_processed`

`downstream_processed != ftrl_validated`

`ftrl_validated != text_verified`

`text_verified != semantic_ready`

## Derechos

El issue #2 permanece abierto. A 2026-09-03 no existe respuesta institucional de CONALITEG/SEP. El silencio no se interpreta como autorización.

La capa pública sólo puede conservar evidencia técnica no sustitutiva. No se publicarán JPEG fuente, PDF, OCR íntegro ni bases que permitan reconstruir secuencialmente las obras. No se eludirán controles de acceso.

## Criterio de cierre de #167

#167 sólo puede cerrarse cuando exista evidencia reproducible de las etapas downstream efectivamente ejecutadas para las cuatro identidades y cuando tablero, registro de retenciones y ledger aplicable estén sincronizados con esa evidencia.

La resolución del routing no basta. La ausencia de validación humana tampoco impide un cierre técnico, pero obliga a mantener separados los estados textuales y semánticos.