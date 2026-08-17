# LTMD-U1 W7 — investigación de fuentes retenidas

Versión: `LTMD_U1_W7_WITHHELD_SOURCE_RESEARCH_0.1`.

Corte de investigación: **16 de agosto de 2026**.

## Propósito

Documentar evidencia externa e interna útil para intentar resolver las cinco identidades W7 retenidas por fuente sin degradar el gate de admisibilidad, sin sustituciones heurísticas y sin convertir similitud de catálogo en identidad documental.

Identidades bajo investigación:

- `H2014P5FCA`.
- `H2018P3FCA`.
- `H2018P4FCA`.
- `H2018P5FCA`.
- `H2018P6FCA`.

La cohorte productiva W7 permanece en 25/30 mientras no aparezca evidencia fuente suficiente para alguna de estas identidades.

## 1. Semántica institucional de `catalog_generation`

La interfaz viva del Catálogo Histórico de CONALITEG presenta un campo con la instrucción **“Indique el año en el que considera inició su educación primaria”** y, como alternativa de navegación, una selección de **“generación”**. Actualmente muestra, entre otras, Generación 2014, Generación 2018 y Generación 2019.

Fuente oficial consultada:

- https://historico.conaliteg.gob.mx/

Regla metodológica derivada: `catalog_generation` se conserva en LTMD como **etiqueta institucional de cohorte/navegación del catálogo**. No se tratará automáticamente como año de publicación, edición o impresión del libro. Esas fechas requieren evidencia bibliográfica independiente del propio objeto.

Esta precisión es importante para W7: una coincidencia entre “Generación 2018” y “Generación 2019” no autoriza interpretar los objetos como ediciones anuales consecutivas ni a sustituir uno por otro.

## 2. Alcance histórico declarado por CONALITEG y evolución de la interfaz

Una nota oficial de CONALITEG publicada el 23 de junio de 2019 describía el Catálogo Histórico como un recurso para consultar materiales producidos **de 1960 a 2017**. La interfaz viva actual, en cambio, ofrece también generaciones 2018 y 2019.

Fuente oficial:

- https://www.gob.mx/conaliteg/articulos/conoce-el-catalogo-historico-de-los-libros-de-texto-gratuitos?idiom=es

Esto documenta que el catálogo y/o su navegación evolucionaron con posterioridad. No permite inferir por sí solo la fecha editorial de un `H2018...` o `H2019...`; refuerza la necesidad de separar **etiqueta de generación del catálogo** de **fecha bibliográfica demostrada**.

## 3. Contexto curricular 2018–2020

La SEP informó el 29 de junio de 2017 que la primera fase de los nuevos planes y programas entraría en vigor en el ciclo **2018–2019** para preescolar, primero y segundo de primaria y primero de secundaria; la segunda etapa, para tercero a sexto de primaria y segundo y tercero de secundaria, se programó para **2019–2020**.

Fuente oficial:

- https://www.gob.mx/sep/prensa/comunicado-171?idiom=es

Esta cronología hace especialmente importante no equiparar mecánicamente una etiqueta de catálogo “2018” con una edición curricular 2018 de los libros de 3.º a 6.º. El dato curricular es contexto documental, no una prueba de identidad entre activos.

## 4. Estado técnico de los visores retenidos

El visor `H2014P5FCA.htm` continúa respondiendo en el dominio oficial y se identifica como Formación Cívica y Ética, 5.º, Generación 2014:

- https://historico.conaliteg.gob.mx/H2014P5FCA.htm

El visor `H2018P3FCA.htm` también continúa respondiendo y se identifica como Formación Cívica y Ética, 3.º, Generación 2018:

- https://historico.conaliteg.gob.mx/H2018P3FCA.htm

La evidencia LTMD ya congelada demostró que el contrato JavaScript del visor construye los activos mediante `./c/{ag_clave}/{ag_page}.jpg`. Bajo ese contrato, los cuatro subárboles 2018 retenidos no sirven sus JPEG en la ruta oficial observada; los controles 2019 del mismo grado sí respondieron en la muestra de conformidad. Por tanto, el estado correcto sigue siendo:

- **objeto/visor institucional presente**;
- **ruta de activos observada no servida**;
- **identidad histórica preservada**;
- **OCR productivo retenido**;
- **sin alias 2018→2019**.

## 5. Fuentes oficiales contemporáneas que no son todavía prueba de identidad

El dominio actual de libros CONALITEG mantiene páginas genéricas para Formación Cívica y Ética, por ejemplo:

- https://libros.conaliteg.gob.mx/P3FCA.htm
- https://libros.conaliteg.gob.mx/P4FCA.htm
- https://libros.conaliteg.gob.mx/P5FCA.htm
- https://libros.conaliteg.gob.mx/P6FCA.htm

También existen copias PDF oficiales en la Nueva Escuela Mexicana Digital para varios grados. Estas fuentes pueden servir para recuperar páginas legales, créditos, ISBN u otros rasgos bibliográficos comparables, pero **no se incorporarán como sustitutos de H2018...** sin demostrar primero que corresponden al mismo objeto documental o a una reproducción autorizadamente equivalente.

## 6. Estrategia de recuperación diferenciada

### H2014P5FCA

El problema es un único hueco interno dentro de un objeto casi completamente servido. La siguiente acción debe identificar la página lógica e índice de imagen exactos desde el manifiesto de auditoría ya existente. Después se buscará esa posición en:

1. rutas oficiales alternativas documentadas;
2. capturas archivadas del mismo URI institucional;
3. una reproducción oficial cuyo objeto bibliográfico pueda vincularse inequívocamente con `H2014P5FCA`.

Una página recuperada sólo se admitirá si puede documentarse la cadena de procedencia y su correspondencia con la posición faltante.

### H2018P3FCA / P4FCA / P5FCA / P6FCA

Aquí no existe un hueco aislado: el patrón es de subárbol no servido. La recuperación debe buscar primero evidencia de **routing histórico o relocalización**, no contenido parecido. Las rutas de investigación prioritarias son:

1. archivos web del URI exacto del visor y de sus subárboles `c/H2018.../`;
2. metadatos o páginas legales en repositorios oficiales SEP/CONALITEG que permitan identificar edición, impresión, autores, ISBN u otra huella bibliográfica;
3. comparación criptográfica página a página con candidatos sólo después de establecer una relación documental plausible;
4. mantenimiento de la retención si no se alcanza ese umbral.

## 7. Criterio de admisibilidad para una futura recuperación

Una identidad retenida sólo podrá pasar a `ocr_source_admitted=1` si la nueva evidencia permite reconstruir su fuente sin imputación. La mera coincidencia de título, grado, número de páginas, etiqueta de generación, orden de catálogo o similitud visual no es suficiente.

Si un candidato resulta byte-idéntico o puede vincularse mediante evidencia bibliográfica/documental independiente, la relación se registrará explícitamente y de forma reversible. Si no, la ausencia seguirá siendo un resultado científico documentado.

## Resultado de este corte

Este corte **no modifica** las cinco decisiones de retención. Su aporte es epistemológico y operativo: corrige la lectura de `catalog_generation`, documenta que al menos los visores institucionales consultados siguen presentes aunque sus activos puedan no estar servidos, y separa la estrategia de recuperación del hueco 2014 de la investigación de routing de los cuatro subárboles 2018.
