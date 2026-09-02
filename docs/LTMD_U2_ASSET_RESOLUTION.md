# LTMD-U2 — resolución técnica de activos PDF

## Alcance

Esta capa documenta únicamente la **resolución de transporte** de los 39 objetos fuente CONALITEG de primaria 2026–2027 ya registrados por LTMD-U2. No constituye admisión de fuente, autorización de redistribución, disponibilidad de OCR, verificación textual, validación semántica ni evidencia histórica por sí misma.

Guardas obligatorias:

- `reader_shell_resolved != asset_resolved`
- `asset_resolved != source_admitted`
- `source_admitted != ocr_available`
- `ocr_available != text_verified`
- `computational_candidate != semantic_ready`
- `publicly_accessible != openly_licensed`

## Ruta observada del lector vigente

El 2 de septiembre de 2026 se inspeccionó de manera acotada el lector institucional `pdf-reader/reader.html` y su bundle JavaScript vigente. El bundle observado tenía 337,409 bytes y SHA-256 `f48a9486b2b0ffbeea70fd4bb80ab373c7fa3b6ef707c6789b1a4d819360206b`.

La lógica del lector toma los parámetros `clave`, `ciclo` y `nivel`; normaliza la clave como nombre PDF; construye la ruta relativa `assets/<nivel>/<ciclo>/<clave>.pdf`; y la resuelve desde `/pdf-reader/reader.html`. Para esta unidad U2 la plantilla efectiva es:

`https://libros.conaliteg.gob.mx/pdf-reader/assets/primaria/2026/<clave>.pdf`

El lector conserva además una ruta HTML heredada como fallback. Dos hipótesis previas —`/<ciclo>/<clave>.htm` y `/<ciclo>/<clave>.pdf`— fueron probadas de manera reproducible y devolvieron 404 para los 39 objetos; por ello no se usan como rutas canónicas de activos.

El registro mínimo y hashado de esta derivación está en `data/catalog/ltmd_u2_reader_route_2026_09_02.json`.

## Resultado 39/39

Se ejecutó una sonda HTTP limitada a los primeros 32 bytes de cada activo, usando solicitudes Range y sin persistir el cuerpo de los libros. Los 39 objetos devolvieron:

- HTTP `206`;
- `Content-Type: application/pdf`;
- `Accept-Ranges: bytes`;
- `Content-Range` expuesto;
- firma inicial `%PDF-`;
- tamaño total del activo derivable del `Content-Range`.

Por tanto, los 39 objetos quedan en `asset_resolution_state=resolved_pdf` para el corte observado del **2026-09-02**. El detalle por objeto está en `data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv`.

## Lo que deliberadamente no se afirma

Esta capa mantiene `source_admission_state=not_assessed` y `page_count_observation=not_observed` en los 39 casos. Un PDF técnicamente accesible puede estar sujeto a restricciones de derechos; su existencia no implica licencia abierta. Tampoco se infiere número de páginas, calidad de extracción, OCR ni corrección semántica a partir de la resolución HTTP.

## Proveniencia reproducible

La identificación exacta de la ruta se obtuvo en GitHub Actions run `33638648887`, sobre el head experimental `c1eb93b4310f44a2959ba4f56d236b625de496a1`. La validación 39/39 de los activos se obtuvo en run `33638766885`, sobre `f5f8a34f516640c551aa044d336e58ba38769ee1`.

Los artifacts originales, sus manifiestos y las tablas de observación se conservaron fuera del repositorio público en el archivo técnico privado del proyecto. El repositorio publica sólo la evidencia mínima necesaria para auditoría y reproducibilidad, no los libros fuente.

## Siguiente capa

La paginación deberá observarse mediante un método separado, reproducible y acotado. `asset_resolved` no autoriza por sí mismo a registrar un conteo de páginas. Cualquier futura capa de paginación deberá conservar método, presupuesto de bytes/rangos, versión del parser y estado de error por objeto, sin descargar ni redistribuir innecesariamente las obras completas.
