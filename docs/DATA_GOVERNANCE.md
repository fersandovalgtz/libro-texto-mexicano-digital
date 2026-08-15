# Gobernanza, procedencia y derechos

## Regla principal

Que un documento pueda consultarse públicamente **no implica automáticamente que pueda redistribuirse íntegramente** desde este proyecto.

Se distinguen de manera expresa cuatro operaciones jurídicamente y técnicamente distintas:

1. **acceso/consulta** del recurso oficial;
2. **adquisición temporal o copia de trabajo** para investigación;
3. **procesamiento/minería** —por ejemplo OCR, segmentación o análisis computacional—;
4. **publicación/redistribución** de originales, transcripciones o derivados.

Una autorización o viabilidad en una capa no se traslada automáticamente a las demás.

## Para cada fuente se registrará

- institución responsable;
- URL original;
- fecha de acceso;
- términos de uso disponibles;
- aviso de derechos, cuando exista;
- posibilidad de descarga;
- método técnico de acceso;
- tratamiento de copias de trabajo;
- posibilidad de publicar originales;
- posibilidad de publicar texto extraído;
- posibilidad de publicar datos derivados;
- decisión adoptada y evidencia que la sustenta.

## Separación de capas

### Fuente

Archivos originales obtenidos de repositorios institucionales. No se incorporan al historial de Git salvo autorización expresa o condición jurídica suficientemente clara.

### Copia de trabajo

Puede existir temporal o localmente para procesamiento reproducible, sujeta a las condiciones aplicables. Debe estar excluida mediante `.gitignore` y no formar parte de artefactos públicos de CI.

### Extracción intermedia

OCR completo, transcripciones extensas, recortes y otros derivados que reproduzcan sustancialmente la expresión de la obra se mantienen fuera de GitHub mientras su redistribución no esté aclarada.

### Datos derivados publicables

Metadatos, identificadores, URLs de procedencia, hashes, conteos, dimensiones, métricas OCR, CER/WER, etiquetas, códigos, clasificaciones, frecuencias, medidas estructurales y estadísticas pueden versionarse cuando no reproduzcan sustancialmente la obra fuente.

### Código

Scripts propios de ingestión, transformación, validación y análisis pueden licenciarse independientemente de los materiales fuente una vez tomada la decisión correspondiente.

## Política provisional para CONALITEG — revisión ampliada 15 de agosto de 2026

### Evidencia oficial de acceso

CONALITEG publicó en 2019 que pone a disposición de estudiantes y población general el **Catálogo Histórico de Libros de Texto Gratuitos en línea** para disfrutar y conocer materiales producidos desde 1960. Este lenguaje prueba una finalidad explícita de **consulta pública**, pero no contiene por sí mismo una licencia abierta de reutilización o redistribución.

Fuente: https://www.gob.mx/conaliteg/articulos/conoce-el-catalogo-historico-de-los-libros-de-texto-gratuitos?idiom=es

### Términos generales de gob.mx

Los términos generales de gob.mx autorizan visualizar y descargar materiales para uso personal y no comercial, y establecen restricciones a modificación, reproducción, exhibición pública, distribución y transferencia.

Fuente: https://www.gob.mx/terminos

Dado que el Catálogo Histórico opera en un subdominio/infraestructura específica y no se ha localizado un instrumento de licencia propio del catálogo, estos términos se consideran **evidencia precautoria relevante**, pero el proyecto no afirma que resuelvan por sí solos toda la cadena de titularidad de cada edición histórica.

### Ley Federal del Derecho de Autor

La página oficial de la Cámara de Diputados registra como última reforma de la Ley Federal del Derecho de Autor la publicada en el DOF el **14 de mayo de 2026**.

Fuente: https://www.diputados.gob.mx/LeyesBiblio/ref/lfda.htm

El artículo 148 permite, bajo condiciones, ciertos usos de obras ya divulgadas sin autorización del titular patrimonial, siempre que no se afecte su explotación normal, se cite la fuente y no se altere la obra. Entre los supuestos se encuentran:

- cita de textos cuando la cantidad no constituya reproducción simulada y sustancial;
- reproducción de **partes** de la obra para crítica e investigación científica, literaria o artística;
- otros supuestos específicos previstos por la ley.

Fuente oficial de consulta del artículo: https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17068.html

**Interpretación conservadora del proyecto:** estas limitaciones son relevantes para investigación y citas, pero **no se interpretan como una autorización general para poner a disposición del público OCR completos, imágenes de páginas o reconstrucciones de libros enteros**.

## Avisos observados en los ejemplares del piloto

### Generación 1972

Página legal/corporativa localizada en visor 4. La extracción disponible no ha mostrado todavía una declaración inequívoca de copyright o año editorial que permita inferir una condición distinta. **No se presume dominio público ni licencia abierta.**

### Generación 1988

Página legal visor 2:

- `Derechos reservados SEP, 1977`;
- ISBN 968-29-0758-6.

Se trata expresamente como material protegido.

### Generación 1993

Página legal visor 2:

- Secretaría de Educación Pública, 1998;
- Primera edición, 1998;
- ISBN 970-18-1599-8.

El acceso público no se interpreta como licencia de republicación.

### Generación 2014

Página legal visor 2:

- D.R. Secretaría de Educación Pública, 2014;
- Tercera edición revisada, 2014;
- ISBN 978-607-514-722-2.

Se trata expresamente como material protegido.

## Semáforo de publicación

### VERDE — publicable/versionable con procedencia

- metadatos bibliográficos y técnicos;
- claves e identificadores del visor;
- URLs oficiales;
- número de páginas y activos;
- dimensiones y formatos;
- hashes/checksums;
- modo OCR utilizado;
- métricas OCR, CER/WER y tasas de error;
- conteos y estadísticas;
- etiquetas, anotaciones y códigos analíticos creados por el proyecto;
- frecuencias y medidas agregadas;
- código, esquemas y documentación;
- resultados y tablas derivados que no reproduzcan de manera sustancial la expresión de los libros.

### AMARILLO — material de trabajo / publicación sólo con análisis específico

- OCR completo mantenido localmente;
- transcripciones extensas;
- fragmentos textuales de extensión significativa;
- citas breves usadas como ejemplos;
- miniaturas;
- portadas;
- recortes de página;
- embeddings u otras representaciones si existe riesgo razonable de reconstrucción del contenido;
- conjuntos acumulados de fragmentos que puedan aproximarse a una reproducción sustancial.

No se versionan por defecto.

### ROJO — no publicar sin autorización expresa o fundamento específico revisado

- JPEG originales completos del visor;
- PDF o reconstrucciones completas;
- espejo total/parcial sustitutivo del Catálogo Histórico;
- OCR íntegro de libros completos;
- dataset público que permita reconstruir secuencialmente el texto completo;
- paquetes masivos de ilustraciones/páginas;
- redistribución de archivos fuente a terceros.

## Matriz operativa resumida

| Operación | Estado provisional |
|---|---|
| Consulta de visores | Verde |
| Descarga temporal para procesamiento | Amarillo |
| Copia de trabajo privada | Amarillo |
| OCR interno para investigación | Amarillo |
| Publicar métricas OCR | Verde |
| Publicar metadatos/URLs/hashes | Verde |
| Publicar códigos y estadísticas | Verde |
| Cita breve científicamente necesaria | Amarillo, caso por caso |
| Colección pública de muchos fragmentos | Amarillo alto / rojo según sustancialidad |
| Miniatura/portada | Amarillo |
| JPEG de página | Rojo |
| OCR completo | Rojo |
| Dataset derivado con DOI sin contenido sustitutivo | Verde |

La matriz completa se mantiene en `docs/RIGHTS_PUBLICATION_MATRIX.md`.

## Reglas para CI y automatización

1. Las imágenes fuente sólo se descargan a almacenamiento temporal del runner.
2. Los workflows no publican imágenes ni texto OCR completo como artefactos.
3. Los artefactos públicos se limitan a métricas, metadatos, estados y datos derivados.
4. Todo dataset que pase de artefacto efímero a archivo permanente se valida antes del commit.
5. Un cambio que pretenda publicar OCR, imágenes, miniaturas o fragmentos extensos exige reabrir/revisar la decisión jurídica correspondiente.
6. La salida de modelos o embeddings deberá evaluarse por riesgo de reconstrucción antes de publicarse.
7. La procedencia oficial debe permanecer trazable hasta `book_id` y `page_id`.

## Consulta institucional preparada

Se preparó `docs/DRAFT_CONALITEG_RIGHTS_INQUIRY.md`, dirigido al canal institucional `info@conaliteg.gob.mx` identificado en las páginas oficiales de CONALITEG.

El borrador solicita aclaración específica sobre:

- OCR de investigación no público;
- publicación de métricas/datos derivados;
- OCR parcial o completo en GitHub/Zenodo;
- fragmentos breves de ejemplo;
- miniaturas y portadas;
- área/titular competente;
- existencia de términos específicos del Catálogo Histórico.

**El borrador no ha sido enviado.** El silencio o ausencia de respuesta nunca se interpretará como autorización.

## Regla de cierre del issue jurídico

El issue de derechos no debe considerarse plenamente cerrado hasta que ocurra al menos una de estas situaciones:

1. exista una respuesta institucional suficiente que permita fijar el tratamiento de las categorías amarillas/rojas; o
2. se obtenga asesoría jurídica específica suficiente para adoptar una política final documentada.

Mientras tanto, el proyecto puede continuar con su arquitectura verde de metadatos, métricas, códigos y datos derivados no sustitutivos.

Esta política es una medida interna de gobernanza de investigación y **no sustituye asesoría jurídica profesional**.
