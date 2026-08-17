# LTMD-U1 W7 — estado del espejo externo candidato para H2014P5FCA

Versión: `LTMD_U1_W7_H2014P5_EXTERNAL_MIRROR_STATUS_0.1`.

Corte: **16 de agosto de 2026**.

## Resultado

El espejo externo identificado para *Formación Cívica y Ética. Quinto grado* del ciclo 2017–2018 permanece clasificado como **candidato externo no verificado**. No se ha incorporado ninguna imagen externa, no se ha reconstruido la página lógica 104 y no se ha modificado `ocr_source_admitted` para `H2014P5FCA`.

La política vigente es **no relajar el umbral de verificación para conseguir una coincidencia**.

## Motivación de la prueba

La auditoría fuente W7 demostró que `H2014P5FCA` tiene 224 JPEG institucionales servidos y un único hueco interno: página lógica **104**, ruta oficial auditada `c/H2014P5FCA/104.jpg`, HTTP 404.

La huella bibliográfica extraída directamente de páginas servidas de ese visor, verificadas previamente contra SHA-256 y tamaño, identifica el objeto como:

- *Formación Cívica y Ética. Quinto grado*.
- Primera edición, **2014**.
- Tercera reimpresión, **2017**.
- Ciclo escolar **2017–2018**.

Esto justificó evaluar, de manera no canónica, un espejo externo que declara el mismo libro/ciclo como posible fuente para una reconstrucción derivada de la posición faltante.

## Contrato de validación diseñado

El instrumento `scripts/evaluate_ltmd_u1_w7_h2014p5_external_mirror.py` fue diseñado para:

1. verificar cada anclaje CONALITEG contra el SHA-256 y tamaño ya congelados;
2. aceptar una página externa sólo si el HTML recibido por el runner se autodeclara como la página esperada;
3. extraer la URL de imagen desde ese mismo HTML, sin construir el nombre del archivo por heurística;
4. comparar OCR de tres anclajes oficiales (`4`, `103`, `105`) contra el candidato;
5. aceptar un mapeo sólo si los tres anclajes convergen en el mismo offset y superan un umbral mínimo de similitud;
6. mantener cualquier página candidata como **reconstrucción derivada**, separada de `source_jpeg`.

## Ejecuciones

### Run 31990532400

La navegación visible públicamente no apareció en el HTML recibido por GitHub Actions. El landing no expuso los enlaces de página requeridos. La ejecución terminó antes de descargar o comparar imágenes candidatas y no publicó resultados.

### Run 31990634303

Se probó la ruta de página observada en la navegación pública como ruta candidata. El HTML servido al runner no permitió autoverificar la página 2 con el metadato requerido. La ejecución terminó antes de publicar resultados.

### Run 31990733990

Se endureció la solicitud con un `User-Agent` de navegador y una segunda vía de autoverificación mediante texto `Página N / 226` o metadatos equivalentes. La ruta candidata de la página 2 volvió a no autodeclararse de forma verificable en la respuesta recibida por GitHub Actions. La ejecución terminó antes de publicar resultados.

## Decisión

Tres fallos consistentes de **autoverificación de la fuente externa**, no de los datos CONALITEG, son suficientes para detener los reintentos automáticos. El workflow `.github/workflows/evaluate-ltmd-u1-w7-h2014p5-external-mirror.yml` queda disponible únicamente mediante `workflow_dispatch` manual.

El candidato externo no se rechaza como obra posible; queda **no verificable con la infraestructura reproducible actual**. No se inferirá de esta limitación que el espejo sea falso, que la página no exista o que no corresponda al mismo libro.

## Consecuencia para H2014P5FCA

El estado fuente no cambia:

- identidad histórica: preservada;
- JPEG institucionales observados: **224/225**;
- hueco: página lógica **104**;
- fuente canónica completa: **no**;
- `ocr_source_admitted`: **0**;
- alias con 2019 u otro visor: **ninguno**;
- reconstrucción derivada aceptada: **ninguna**.

## Condición para reabrir esta vía

La prueba sólo debe retomarse cuando exista una forma reproducible de recuperar una página del espejo y demostrar desde la propia respuesta el libro y la posición, o cuando una fuente documental independiente establezca una relación inequívoca entre ese espejo y la tercera reimpresión 2017 servida por CONALITEG.

No se reducirá el umbral de autoverificación para hacer que el candidato pase.
