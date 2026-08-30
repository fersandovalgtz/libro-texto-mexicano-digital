# LTMD-U1 W7 — investigación de fuentes retenidas 0.4

Versión: `LTMD_U1_W7_WITHHELD_SOURCE_RESEARCH_0.4`.

Este corte consolida la investigación reproducible de las cinco identidades W7 retenidas por fuente. **No modifica `ocr_source_admitted`** y no crea aliases.

## Estado de las cinco identidades

| identidad | decisión vigente | problema fuente | estado en este corte |
|---|---|---|---|
| `H2014P5FCA` | `withheld_source_gap` | un hueco interno aislado | visor/configuración presentes; 224 JPEG servidos; falta la página lógica 104 / `104.jpg` |
| `H2018P3FCA` | `withheld_source_subtree_unserved` | subárbol oficial no servido | visor/configuración presentes; activos retenidos |
| `H2018P4FCA` | `withheld_source_subtree_unserved` | subárbol oficial no servido | visor/configuración presentes; activos retenidos |
| `H2018P5FCA` | `withheld_source_subtree_unserved` | subárbol oficial no servido | visor/configuración presentes; activos retenidos |
| `H2018P6FCA` | `withheld_source_subtree_unserved` | subárbol oficial no servido | visor/configuración presentes; activos retenidos |

## 1. Presencia institucional reproducible

El snapshot `LTMD_U1_W7_WITHHELD_VIEWER_PRESENCE_0.1` verificó las cinco identidades sin solicitar ningún JPEG de página:

- `claves.json` respondió HTTP 200 y su SHA-256 fue `7fb55e583ee5190fd2153d95764426114f86946ea93d8545c07d5f03d7674037`.
- Las cinco claves permanecen presentes en esa configuración.
- `ag_pages` coincide exactamente con las cardinalidades congeladas por LTMD: 225, 114, 130, 226 y 210.
- Los cinco visores HTML respondieron HTTP 200.
- Los títulos HTML continúan identificando grado y generación de catálogo.

Artefactos:

- `data/catalog/ltmd_u1_w7_withheld_viewer_presence.csv`
- `data/catalog/ltmd_u1_w7_withheld_viewer_presence.md`

**Conclusión:** las cuatro retenciones 2018 no deben describirse como “libros inexistentes” ni como “visores desaparecidos”. En este corte son objetos de catálogo/configuración y visores institucionales presentes cuyos activos de página no se sirven bajo la ruta oficial observada.

## 2. Contrato de routing que permanece vigente

La evidencia ya congelada muestra que:

1. `claves.json` registra las cuatro claves `H2018P3FCA`–`H2018P6FCA` con sus cardinalidades.
2. El JavaScript del visor deriva `ag_clave` del nombre del archivo HTML y obtiene `ag_pages` desde `claves.json`.
3. La exploración de dependencias dinámicas localizó `magazine.js` y las definiciones de `addPage`/`loadPage`.
4. La ruta de imagen observada es `./c/{ag_clave}/{ag_page}.jpg` bajo el contrato de numeración ya documentado.
5. El probe de conformidad 2018 produjo 12/12 HTTP 404, mientras los controles 2019 del mismo grado produjeron 12/12 HTTP 200.

No apareció en las dependencias institucionales inspeccionadas un segundo endpoint de imagen determinista que autorice probar una relocalización alternativa. Por tanto, **no se ensayan rutas inventadas**.

## 3. `H2014P5FCA`: identificación bibliográfica del objeto servido

La huella bibliográfica `LTMD_U1_W7_H2014P5_BIBLIOGRAPHIC_FINGERPRINT_0.2` auditó las páginas lógicas 1–12. Los 12 JPEG fueron verificados contra SHA-256 y tamaño antes del OCR. La página legal 4, sometida a ensemble OCR, contiene evidencia redundante de:

- `Primera edición, 2014`;
- `Tercera reimpresión, 2017`;
- `ciclo escolar 2017-2018`.

El ISBN no pudo leerse con fiabilidad suficiente y **no se imputa** desde fuentes secundarias.

Esta evidencia demuestra que `catalog_generation=2014` no equivale al año de impresión/reimpresión del objeto efectivamente servido. La temporalidad bibliográfica se modela por separado en la capa de observaciones bibliográficas.

## 4. Hueco exacto de `H2014P5FCA`

La auditoría compacta del manifiesto fuente localiza el único hueco en:

- página lógica: **104**;
- índice de activo esperado por el contrato: **`104.jpg`**.

Las otras 224 posiciones JPEG están servidas y hasheadas. La comparación criptográfica posicional contra otros libros W7 de quinto grado no encontró una página byte-idéntica que permita resolver el hueco mediante alias exacto; en particular, `H2019P5FCA` no constituye sustituto byte-exacto.

## 5. Infraestructura archivística consultada

Se implementaron probes de descubrimiento exacto sobre Wayback CDX y Common Crawl. En los cortes ejecutados, ambos servicios resultaron técnicamente inconcluyentes para los objetivos retenidos. Los fallos de consulta **no se interpretan como ausencia histórica**, porque el índice no produjo una respuesta válida y recuperable que permita afirmar cero capturas.

Los probes se conservan como evidencia de método/infraestructura, no como prueba negativa sobre los libros.

## 6. Espejo externo 2017–2018

Se implementó un experimento de alineación contra un espejo externo de la obra de quinto grado. Tres ejecuciones no lograron autoverificar de forma reproducible las páginas del espejo desde GitHub Actions antes de comparar contenido. No se publicó ninguna alineación ni se incorporó imagen alguna.

El workflow quedó `workflow_dispatch`-only. La ruta queda congelada como **candidato externo no verificado** y no debe reintentarse reduciendo los criterios de identificación.

## 7. Umbral para levantar una retención

Una identidad retenida sólo puede cambiar a `ocr_source_admitted=1` si aparece evidencia que permita reconstruir la fuente sin imputación. Son admisibles, por ejemplo:

- recuperación del activo institucional exacto o de una captura archivada del URI exacto;
- relocalización determinista demostrada desde metadatos/código institucional;
- reproducción oficial/documental inequívocamente vinculada al mismo objeto, con correspondencia posicional demostrable y procedencia explícita.

No bastan:

- mismo título;
- mismo grado;
- misma cardinalidad;
- generación próxima;
- similitud OCR o visual aislada;
- alta reutilización textual;
- existencia del objeto 2019 del mismo grado.

## 8. Resultado de los cortes previos

Las cinco retenciones permanecen vigentes. El avance científico es preciso:

- **las cinco identidades están institucionalmente presentes como configuración + visor**;
- el problema 2014 es un único hueco posicional identificado y el objeto servido está bibliográficamente caracterizado como tercera reimpresión 2017 de una primera edición 2014;
- el problema 2018 es de servicio/routing de activos, no de ausencia demostrada del objeto de catálogo;
- no existe evidencia suficiente para un alias 2018→2019 ni para una reconstrucción externa de la página 104;
- cualquier recuperación futura queda condicionada a una cadena de procedencia verificable.

## 9. Búsqueda acotada adicional — 2026-08-30

Artefacto: `data/catalog/ltmd_u1_w7_withheld_source_bounded_search_2026-08-30.csv`.

Se ejecutó una última pasada orientada exclusivamente a los URI institucionales exactos, sin búsqueda por similitud de título o grado:

1. se mantuvo como contrato de referencia `https://historico.conaliteg.gob.mx/c/{ag_clave}/{ag_page}.jpg` y, para el hueco 2014, el URI exacto de `104.jpg`;
2. se reintentó descubrimiento archivístico con Wayback CDX; el servicio volvió a fallar/timeoutear desde rutas de acceso independientes, por lo que el resultado sigue siendo **técnicamente inconcluyente**;
3. se consultó el índice público vigente `CC-MAIN-2026-34` de Common Crawl para el URI 2014 y los cuatro subárboles 2018; no se obtuvieron registros de captura utilizables ni bytes WARC, y algunos accesos devolvieron error de infraestructura;
4. se localizó el repositorio técnico independiente `jlochoap/LTGbasic`, cuyo README documenta el mismo patrón histórico `/c/{clave}/{page}.jpg`; esta coincidencia corrobora la construcción de ruta, pero el repositorio no conserva los bytes objetivo y por tanto no aporta evidencia de manifestación.

### Decisión del corte 0.4

- fuentes nuevas admitidas: **0/5**;
- aliases creados: **0**;
- cambios a `ocr_source_admitted`: **0**;
- retenciones vigentes: **5/5**.

La búsqueda acotada queda **agotada bajo las fuentes actualmente disponibles**. Esto no convierte las retenciones en excepciones finales ni autoriza cerrar la issue #5: el documento de criterios de aceptación exige bytes recuperados, procedencia, correspondencia posicional y hashes para levantar una retención. Tampoco se volverán a ejecutar búsquedas genéricas o barridos repetitivos sin una pista documental nueva.

### Condición de reactivación

Reabrir investigación activa sobre una identidad únicamente si aparece al menos una de estas señales nuevas:

- captura archivada identificada del URI exacto;
- cambio observable en el servicio institucional de activos;
- código/metadato institucional que revele un endpoint alternativo determinista;
- reproducción oficial con identificador inequívoco y posibilidad de alineación posicional.

Hasta entonces, las cinco identidades permanecen como `blocked_active_retention` en la clausura global y la deuda documental se conserva explícitamente sin bloquear el corpus ya admitido.
