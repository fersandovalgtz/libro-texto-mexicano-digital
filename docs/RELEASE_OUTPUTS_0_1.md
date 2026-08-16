# Outputs públicos por workflow — LTMD 0.1

Corte: **2026-08-15**  
Candidata: **v0.1.0-rc.1**

Este documento identifica qué produce cada cadena principal y qué tipo de material puede formar parte de una release de LTMD. La regla general es conservar **metadatos, hashes, métricas, estructuras y derivados no sustitutivos**, no redistribuir indiscriminadamente páginas, imágenes u OCR íntegro de las obras fuente.

| Capa / workflow | Outputs públicos principales | Contenido fuente redistribuido | Estado en RC |
|---|---|---:|---|
| Catálogo histórico | `data/catalog/conaliteg_historical_viewer_keys.csv`, inventario de títulos, title cores y grupos de auditoría | No | cerrado |
| Readiness familia CN | inventario estricto, readiness de activos, anomalías de routing | No | cerrado |
| Alias 2018→2019 | identidad de activos y relaciones de alias | No; sólo hashes/tamaños/relaciones | cerrado |
| Auditoría 2008 | posiciones internas no servidas y evidencia de intentos | No | cerrado |
| CN5 piloto — PAGESTRUCT/FRAGSEG | estructura de páginas, manifiesto de 9,594 fragmentos, hashes y metadatos | No OCR íntegro | cerrado |
| SEMB 0.2 | configuración congelada, resultados de desarrollo/validación sintética, resumen y diagnóstico de incertidumbre | No texto fuente íntegro | diagnóstico congelado |
| SEMB 0.3 prehumano | muestra por IDs opacos, protocolos, criterios, grid, stress cases y stage gates | No gold humano; no validación abierta | `WAITING_HUMAN_REFERENCE` |
| CN4/CN6 — page manifest | procedencia, posiciones, tamaño y SHA-256 | No JPEG | cerrado |
| CN4/CN6 — OCR | métricas por página y resumen | No transcripción íntegra | cerrado |
| CN4/CN6 — PAGESTRUCT | clases estructurales y resumen | No | cerrado |
| CN4/CN6 — FRAGSEG | manifiesto de 19,067 ocurrencias, tipos, hashes, gaps y vista de contenido único | No texto fuente sustitutivo | cerrado |
| Dependencia documental | relaciones, clusters, reutilización/revisión y diferencias | No | cerrado |
| Ola 2 — ingestión | cola de 19 libros y manifiesto de 3,177 activos | No JPEG | cerrado |
| Ola 2 — OCR | métricas y resumen, 3,177/3,177 hashes verificados | No transcripción íntegra | cerrado |
| Ola 2 — PAGESTRUCT | 3,177 páginas estructuradas, 2,528 elegibles | No | cerrado |
| Ola 2 — FRAGSEG | manifiesto de 36,195 ocurrencias y auditoría de gaps | No texto fuente sustitutivo | cerrado |
| Verificación del artículo | `data/derived/methods_article_claim_check.json` | No | PASS |
| Integridad científica | manifiesto SHA-256 global | No | `LTMD_INTEGRITY_0.5` |
| Preflight de release | JSON/Markdown con readiness y blockers | No | RC técnica PASS |

## Estados semánticos

`closed` o `corpus_ready` en una capa técnica significa que la reconstrucción, hashes, cardinalidades y outputs derivados de esa etapa están materializados y auditables. **No significa `semantic_ready`.**

En `v0.1.0-rc.1` sólo el piloto CN5 posee las capas experimentales Rule A/SEMB 0.2. Las expansiones CN4/CN6 y Ola 2 no se convierten en resultados históricos semánticos mediante un clasificador no validado.

## Material deliberadamente excluido del paquete público

- copias de trabajo en `data/work/`;
- activos en `data/raw/`;
- cualquier carpeta `private/`;
- PDF/JPEG/TIFF/JP2/ZIP fuente que sustituya o redistribuya la obra original;
- OCR íntegro reconstruido sólo para procesamiento;
- referencia humana SEMB 0.3 antes de que su protocolo autorice la apertura/publicación correspondiente;
- secretos y archivos `.env`.

El preflight de la candidata verifica automáticamente que las rutas y extensiones fuente/provisionales prohibidas no estén rastreadas por Git.

## Regla para futuras releases

Cada nueva release debe actualizar esta matriz cuando cambie uno de cuatro aspectos: un nuevo output se vuelve público, cambia el nivel de derechos/reutilización, una capa pasa de prehumana a validada o se incorpora un nuevo corpus técnico. La inclusión en GitHub no equivale por sí misma a permiso de relicenciamiento.
