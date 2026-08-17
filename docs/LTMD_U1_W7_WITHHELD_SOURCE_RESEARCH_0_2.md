# LTMD-U1 W7 — investigación de fuentes retenidas

Versión: `LTMD_U1_W7_WITHHELD_SOURCE_RESEARCH_0.2`.

Corte: **16 de agosto de 2026**.

## Propósito

Consolidar el estado de investigación de las cinco identidades W7 retenidas por fuente después del cierre técnico de la cohorte admisible. Esta versión incorpora el diagnóstico exacto del hueco 2014, la huella bibliográfica del propio objeto, las pruebas criptográficas contra vecinos, los probes archivísticos y el intento controlado de evaluar un espejo externo.

Ninguna de estas pruebas reduce el gate de procedencia. Las cinco identidades siguen preservadas y retenidas mientras no exista fuente suficiente para reconstruirlas sin imputación.

## Estado consolidado

| identidad | estado | evidencia fuente observada | decisión |
|---|---|---|---|
| `H2014P5FCA` | hueco aislado | 224/225 JPEG; página lógica 104 / `104.jpg` no servida | retenida |
| `H2018P3FCA` | subárbol no servido | 0/114 JPEG; 113 internos no servidos + terminal | retenida |
| `H2018P4FCA` | subárbol no servido | 0/130 JPEG; 129 internos no servidos + terminal | retenida |
| `H2018P5FCA` | subárbol no servido | 0/226 JPEG; 225 internos no servidos + terminal | retenida |
| `H2018P6FCA` | subárbol no servido | 0/210 JPEG; 209 internos no servidos + terminal | retenida |

La cohorte productiva W7 permanece en **25/30 identidades**.

## 1. Hueco exacto de H2014P5FCA

El diagnóstico reproducible `LTMD_U1_W7_WITHHELD_SOURCE_GAPS_0.1` aisló una sola anomalía interna en el objeto:

- página lógica del visor: **104**;
- índice de imagen: **104**;
- ruta oficial auditada: `https://historico.conaliteg.gob.mx/c/H2014P5FCA/104.jpg`;
- estado observado: `internal_unserved` / HTTP 404;
- JPEG servidos en el resto del objeto: **224**.

El objetivo de recuperación queda, por tanto, reducido a una posición documental exacta. No existe justificación para renumerar, interpolar o sustituir esa posición.

Productos:

- `data/catalog/ltmd_u1_w7_withheld_source_gaps.csv`
- `data/catalog/ltmd_u1_w7_withheld_source_gaps.md`

## 2. No existe un alias byte-exacto con otro libro W7 de quinto

`LTMD_U1_W7_H2014P5_EXACT_NEIGHBORS_0.1` comparó los SHA-256 ya auditados de las páginas servidas de `H2014P5FCA` contra otros visores W7 de quinto grado, posición por posición.

Resultados:

- `H2008P5FCA`: **0** coincidencias byte-exactas en las posiciones comparables;
- `H2011P5FCA`: **0** coincidencias byte-exactas;
- `H2019P5FCA`: **0** coincidencias byte-exactas en **224** posiciones comparables.

En consecuencia, la página 104 de 2019, 2011 o 2008 no puede incorporarse como continuación de un libro byte-idéntico. La vía de alias criptográfico queda descartada con la evidencia disponible.

Productos:

- `data/catalog/ltmd_u1_w7_h2014p5_exact_neighbors.csv`
- `data/catalog/ltmd_u1_w7_h2014p5_exact_neighbor_mismatches.csv`
- `data/catalog/ltmd_u1_w7_h2014p5_exact_neighbors.md`

## 3. Huella bibliográfica primaria de H2014P5FCA

`LTMD_U1_W7_H2014P5_BIBLIOGRAPHIC_FINGERPRINT_0.2` descargó únicamente las páginas lógicas **1–12** del propio visor institucional. Cada una fue verificada contra SHA-256 y tamaño del manifiesto fuente antes de OCR: **12/12 verificadas**.

La página legal lógica 4 fue sometida a un ensemble Tesseract en español (`PSM 3, 4, 6, 11, 12`). Múltiples modos reconocen de forma concordante:

- *Formación Cívica y Ética. Quinto grado*;
- Secretaría de Educación Pública / Subsecretaría de Educación Básica;
- **Primera edición, 2014**;
- **Tercera reimpresión, 2017 (ciclo escolar 2017-2018)**;
- derechos de la SEP con año 2014.

El ISBN no fue legible con suficiente fiabilidad en el JPEG servido. LTMD no lo completa desde una copia secundaria como si fuera una observación del objeto.

Productos:

- `data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.csv`
- `data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.md`

## 4. Consecuencia: `catalog_generation` no es fecha editorial

`H2014P5FCA` aparece bajo **Generación 2014**, pero la página legal del objeto institucional servido declara una **tercera reimpresión 2017** para el ciclo **2017–2018**.

Este caso falsifica el supuesto `catalog_generation == publication_year`. Por ello LTMD adopta el contrato transversal `LTMD_CATALOG_GENERATION_SEMANTICS_0.1`:

- `catalog_generation` se conserva como etiqueta institucional de cohorte/navegación;
- `first_edition_year`, `reprint_year`, `school_cycle` y demás fechas bibliográficas deben observarse por separado;
- ninguna fecha faltante se completa con el año de generación del catálogo.

Documento:

- `docs/LTMD_CATALOG_GENERATION_SEMANTICS_0_1.md`

Esta distinción también limita la interpretación de los cuatro objetos etiquetados como Generación 2018: la etiqueta por sí sola no demuestra fecha de edición ni autoriza relaciones con los visores 2019.

## 5. Probes archivísticos: infraestructura no concluyente

### Wayback CDX

`LTMD_U1_W7_WAYBACK_SOURCE_DISCOVERY_0.2` consultó los URI institucionales exactos del hueco 2014, los visores retenidos y los prefijos de activos 2018. Las consultas terminaron en HTTP 503 o timeout.

Resultado epistemológico: **no se obtuvo una consulta archivística válida**. Los ceros de captura no se interpretan como ausencia histórica.

Productos:

- `data/catalog/ltmd_u1_w7_wayback_source_discovery.csv`
- `data/catalog/ltmd_u1_w7_wayback_source_discovery.md`

### Common Crawl

`LTMD_U1_W7_COMMONCRAWL_SOURCE_DISCOVERY_0.2` limitó el probe a ocho índices, dos por año entre 2017 y 2020, y consultó únicamente URI institucionales exactos.

Para cada uno de los cinco objetivos hubo **0/8 consultas de índice válidas**. Por tanto, tampoco se deriva una afirmación de ausencia en Common Crawl.

Productos:

- `data/catalog/ltmd_u1_w7_commoncrawl_source_discovery.csv`
- `data/catalog/ltmd_u1_w7_commoncrawl_source_discovery.md`

## 6. Espejo externo 2017–2018: candidato no verificado

La identificación primaria de la tercera reimpresión 2017 justificó evaluar un sitio externo que presenta *Formación Cívica y Ética. Quinto grado* del ciclo 2017–2018. La prueba fue deliberadamente más estricta que una comparación visual casual.

El instrumento exigía:

1. anclajes CONALITEG verificados por SHA-256 y tamaño;
2. autodeclaración de número de página en la respuesta externa;
3. extracción de la URL de imagen desde el HTML recibido, sin adivinar nombre de archivo;
4. convergencia del offset en tres anclajes (`4`, `103`, `105`);
5. similitud OCR mínima antes de identificar una reconstrucción candidata.

Tres runs terminaron antes de publicar evidencia:

- `31990532400`: el landing servido al runner no expuso la navegación necesaria;
- `31990634303`: la ruta candidata de página no se autoverificó con el metadato exigido;
- `31990733990`: incluso con solicitud tipo navegador y autoverificación adicional, la página 2 no pudo identificarse reproduciblemente en el HTML recibido.

No se aceptó ninguna página externa. El workflow quedó **manual-only** para evitar reintentos automáticos y, especialmente, para evitar rebajar el umbral de evidencia.

Documento de estado:

- `docs/LTMD_U1_W7_H2014P5_EXTERNAL_MIRROR_STATUS_0_1.md`

## 7. Estado de los cuatro visores 2018

La evidencia técnica previa permanece vigente:

- el HTML institucional de los visores existe;
- el contrato JavaScript construye los JPEG por `./c/{ag_clave}/{ag_page}.jpg`;
- la muestra de conformidad de ruta produjo **12/12 HTTP 404** en los cuatro visores 2018;
- controles 2019 del mismo grado produjeron **12/12 HTTP 200**;
- el inventario completo registra subárboles 2018 no servidos bajo la ruta oficial observada;
- no existe evidencia que autorice sustituirlos por objetos 2019.

El estado correcto sigue siendo **identidad catalogada / activos observados no servidos / fuente productiva retenida**.

## 8. Criterio actualizado de recuperación

### H2014P5FCA

Prioridad: localizar una fuente reproducible de la **tercera reimpresión 2017, ciclo 2017–2018**, suficientemente identificada como el mismo objeto documental, y demostrar la correspondencia de la posición faltante.

Una fuente externa podría utilizarse, en el mejor de los casos, como **reconstrucción derivada con procedencia explícita**. No debe convertirse retroactivamente en `source_jpeg` del dominio CONALITEG.

La admisión canónica del objeto completo sólo puede cambiar si la procedencia permite cerrar la fuente sin imputación.

### H2018P3FCA / H2018P4FCA / H2018P5FCA / H2018P6FCA

Prioridad: encontrar evidencia de routing histórico, relocalización o registros bibliográficos que identifiquen inequívocamente los objetos. La búsqueda debe partir de claves/URI institucionales o de huellas bibliográficas demostradas, no de coincidencia de título y grado.

## 9. Estado al cierre de esta versión

No se modifica ninguna decisión de admisibilidad:

- identidades históricas W7: **30/30** preservadas;
- fuente productiva admitida: **25/30**;
- retenidas: **5/30**;
- aliases nuevos: **0**;
- reconstrucciones externas aceptadas: **0**.

El avance de esta versión no consiste en “rellenar” la página 104, sino en reducir la incertidumbre con evidencia falsable: se conoce la posición exacta del hueco, se descartaron aliases byte-exactos, se identificó la reimpresión institucional real, se corrigió la semántica temporal del catálogo y se documentaron explícitamente dos infraestructuras archivísticas no concluyentes y un espejo externo no verificable.
