# Matriz provisional de derechos y publicación — piloto 0.1

**Fecha de revisión:** 15 de agosto de 2026.

> Esta matriz es una política conservadora de gestión de riesgo para el proyecto, **no una opinión jurídica ni una determinación vinculante sobre derechos de autor**. Si CONALITEG/SEP o un titular competente proporciona autorización o términos específicos, éstos deberán prevalecer y quedar documentados.

## Fuentes oficiales revisadas

1. CONALITEG, “Conoce el Catálogo Histórico de los Libros de Texto Gratuitos” (23 de junio de 2019): el organismo declara que pone el catálogo histórico en línea a disposición de estudiantes y población general para conocer los materiales producidos desde 1960.  
   Fuente: https://www.gob.mx/conaliteg/articulos/conoce-el-catalogo-historico-de-los-libros-de-texto-gratuitos?idiom=es

2. Términos y condiciones de gob.mx: autorizan visualización y descarga para uso personal y no comercial; establecen restricciones a modificación, reproducción, exhibición pública, distribución y transferencia de materiales.  
   Fuente: https://www.gob.mx/terminos

3. Ley Federal del Derecho de Autor vigente. La página oficial de la Cámara de Diputados registra como última reforma la publicada en DOF el 14 de mayo de 2026.  
   Fuente: https://www.diputados.gob.mx/LeyesBiblio/ref/lfda.htm

4. Artículo 148 de la Ley Federal del Derecho de Autor: las obras divulgadas pueden utilizarse sin autorización en supuestos limitados, siempre que no se afecte su explotación normal, se cite la fuente y no se altere la obra. Entre esos supuestos se incluyen la cita no sustancial y la reproducción de partes de una obra para crítica e investigación científica, literaria o artística.  
   Fuente oficial de consulta: https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17068.html

5. CONALITEG mantiene como canal general de contacto `info@conaliteg.gob.mx`.  
   Fuente: https://www.conaliteg.gob.mx/ y páginas institucionales vigentes.

## Avisos observados en los cuatro ejemplares del piloto

| Generación | Evidencia de página legal | Tratamiento en el proyecto |
|---|---|---|
| 1972 | Página legal/corporativa localizada; la extracción disponible no muestra todavía un aviso inequívoco de copyright/año | No inferir dominio público ni licencia abierta |
| 1988 | `Derechos reservados SEP, 1977`; ISBN 968-29-0758-6 | Material expresamente tratado como protegido |
| 1993 | `Secretaría de Educación Pública, 1998`; Primera edición 1998; ISBN 970-18-1599-8 | No inferir permiso de redistribución a partir del acceso público |
| 2014 | `D.R. Secretaría de Educación Pública, 2014`; Tercera edición revisada 2014; ISBN 978-607-514-722-2 | Material expresamente tratado como protegido |

## Semáforo de publicación

### VERDE — publicable/versionable con procedencia

Estas salidas no reproducen de manera sustancial la expresión de los libros y son la política ordinaria del repositorio:

- `book_id`, `page_id` y otros identificadores internos;
- generación, grado, asignatura, edición/año cuando estén verificados;
- ISBN y metadatos bibliográficos;
- URL oficial de procedencia;
- número de páginas/activos;
- dimensiones y tamaño técnico de archivos;
- hashes/checksums;
- modo OCR utilizado;
- número de palabras/caracteres detectados;
- CER/WER y otras métricas de calidad;
- conteos y frecuencias agregadas;
- etiquetas y códigos analíticos creados por el proyecto;
- posición en el libro y variables estructurales;
- estadísticas de actividades, preguntas, acciones pedagógicas y representaciones;
- código, esquemas, documentación y workflows;
- tablas derivadas que no incluyan texto sustancial ni reproducciones visuales.

**Regla:** citar siempre la fuente y conservar trazabilidad a CONALITEG.

### AMARILLO — uso de trabajo / publicación sólo con justificación específica

- OCR completo mantenido localmente para investigación;
- transcripciones extensas por página;
- fragmentos textuales de extensión significativa;
- ejemplos textuales breves en artículos, documentación o interfaces;
- miniaturas;
- portadas;
- recortes de página;
- embeddings u otras representaciones que pudieran permitir reconstrucción sustancial del texto;
- conjuntos de fragmentos que, acumulados, puedan aproximarse a una reproducción sustancial.

**Regla:** no versionar por defecto. Para citas/fragmentos breves, evaluar necesidad científica, extensión, atribución, proporcionalidad y efecto sobre la explotación normal. Mantener separado el uso interno de la publicación pública.

### ROJO — no publicar sin autorización expresa o fundamento específico revisado

- JPEG originales completos del visor;
- PDF o reconstrucciones de libros completos;
- espejos del Catálogo Histórico;
- OCR íntegro de un libro completo;
- dataset público que permita reconstruir secuencialmente el texto completo;
- paquetes masivos de ilustraciones o páginas;
- redistribución de archivos descargados desde CONALITEG a terceros.

## Matriz por operación

| Operación | Estado | Razón de política |
|---|---|---|
| Consultar los visores oficiales | Verde | Es la finalidad explícita del Catálogo Histórico |
| Descargar temporalmente JPEG para ejecutar análisis | Amarillo | Necesario para investigación, pero los términos generales no equivalen a licencia de redistribución |
| Mantener copia de trabajo privada/local | Amarillo | Útil para reproducibilidad interna; no se asume derecho de publicación |
| Ejecutar OCR para investigación | Amarillo | Transformación/extracción interna; no implica permiso para difundir el OCR |
| Publicar métricas OCR | Verde | No reproduce el contenido expresivo sustancial |
| Publicar metadatos y URL | Verde | Trazabilidad y descripción |
| Publicar códigos/etiquetas de investigación | Verde | Creación analítica del proyecto |
| Publicar cita breve necesaria para análisis | Amarillo | Puede encuadrar en limitaciones legales, pero requiere proporcionalidad y atribución caso por caso |
| Publicar cientos/miles de fragmentos breves acumulados | Rojo/amarillo alto | La acumulación puede convertirse en reproducción sustancial |
| Publicar miniatura/portada | Amarillo | Puede incorporar ilustraciones/obras artísticas protegidas |
| Publicar JPEG de página | Rojo | Reproducción visual del material fuente |
| Publicar OCR completo | Rojo | Sustituye funcionalmente una parte sustancial o la totalidad de la obra |
| Publicar dataset estadístico/analítico con DOI | Verde | Objetivo recomendado del proyecto si no incorpora material expresivo sustancial |

## Interpretación del artículo 148 para este proyecto

El artículo 148 es relevante porque reconoce usos limitados de obras ya divulgadas, incluyendo citas y reproducción de **partes** para investigación científica, sujeto a condiciones. Sin embargo, el proyecto adopta tres cautelas:

1. la excepción de investigación no se interpreta como autorización general para poner a disposición del público un OCR completo de cada libro;
2. “partes” y “no afectar la explotación normal” requieren análisis contextual; no se fija aquí un número universal de palabras o páginas;
3. los términos del portal y los avisos específicos de cada obra también deben considerarse en la gestión de riesgo.

Por ello, el proyecto puede continuar científicamente mediante métricas, códigos, hashes y datos derivados mientras solicita una aclaración institucional para cualquier publicación textual/visual más ambiciosa.

## Preguntas que requieren aclaración de CONALITEG/SEP

1. ¿Autoriza CONALITEG/SEP la extracción OCR de los libros del Catálogo Histórico para investigación académica no comercial cuando los archivos fuente y el OCR completo se mantienen como material de trabajo no público?
2. ¿Puede publicarse un dataset derivado con metadatos, métricas, etiquetas, frecuencias y hashes por página, sin reproducir imágenes ni texto completo?
3. ¿Puede publicarse OCR completo o parcial en un repositorio académico/GitHub/Zenodo para reproducibilidad científica? En caso afirmativo, ¿bajo qué límites o licencia?
4. ¿Puede publicarse una selección de fragmentos breves como ejemplos anotados para validar un libro de códigos?
5. ¿Puede publicarse una miniatura de portada o página para documentación/interfaz de investigación? ¿Existen restricciones adicionales por obras artísticas incorporadas?
6. ¿Existe una licencia, autorización general o política específica distinta de los términos generales de gob.mx para los materiales del Catálogo Histórico?
7. ¿La autorización debe solicitarse a CONALITEG, a la Dirección General de Materiales Educativos/SEP o a otro titular/área jurídica según la generación y el libro?

## Decisión provisional

El proyecto **no necesita detener su análisis** mientras mantenga una arquitectura de publicación centrada en datos derivados no sustitutivos. El semáforo permanece:

- **verde** para metadatos, código, métricas y análisis;
- **amarillo** para OCR de trabajo, citas/fragmentos y elementos visuales;
- **rojo** para redistribución de páginas, imágenes u OCR íntegro.

El issue jurídico sólo podrá cerrarse plenamente tras obtener aclaración institucional o definir, con asesoría jurídica suficiente, una política final para los materiales amarillos/rojos.
