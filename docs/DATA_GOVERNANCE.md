# Gobernanza, procedencia y derechos

## Regla principal

Que un documento pueda consultarse públicamente no implica automáticamente que pueda redistribuirse íntegramente desde este repositorio.

El proyecto distingue **acceso**, **procesamiento para investigación** y **publicación/redistribución** como decisiones separadas.

## Para cada fuente se registrará

- institución responsable;
- URL original;
- fecha de acceso;
- términos de uso disponibles;
- aviso de derechos, cuando exista;
- posibilidad de descarga;
- posibilidad de minería o procesamiento;
- posibilidad de redistribuir originales;
- posibilidad de redistribuir texto extraído o datos derivados;
- decisión adoptada y fundamento documental.

## Separación de capas

### Fuente
Archivos originales obtenidos de repositorios institucionales. No se incorporan al historial de Git salvo autorización expresa o condición jurídica suficientemente clara.

### Copia de trabajo
Puede existir temporal o localmente para procesamiento reproducible, sujeta a las condiciones aplicables. Debe estar excluida mediante `.gitignore` y no formar parte de artefactos públicos de CI.

### Extracción intermedia
OCR completo, transcripciones extensas y otros derivados que reproduzcan sustancialmente el contenido fuente se mantienen fuera de GitHub mientras su redistribución no esté aclarada.

### Datos derivados publicables
Metadatos, identificadores, URLs de procedencia, conteos, dimensiones, etiquetas, clasificaciones, estadísticas y resultados agregados pueden versionarse cuando no reproduzcan sustancialmente la obra fuente.

### Código
Scripts propios de ingestión, transformación, validación y análisis podrán recibir una licencia de software independiente una vez tomada la decisión correspondiente.

## Política provisional para CONALITEG — 15 de agosto de 2026

La documentación oficial localizada confirma que CONALITEG ofrece los libros y el catálogo histórico mediante plataformas digitales de libre acceso para **consulta**. No se ha localizado, hasta esta revisión, una licencia abierta específica del Catálogo Histórico que autorice expresamente la redistribución masiva de imágenes o transcripciones completas.

Como referencia precautoria adicional, los términos generales de `gob.mx` autorizan visualización/descarga de materiales para uso personal y contienen restricciones de reproducción y distribución pública. Dado que el Catálogo Histórico opera en un dominio propio, esos términos se registran como referencia de cautela y no se asume sin más que constituyan el instrumento jurídico específico del visor histórico.

La Ley Federal del Derecho de Autor contempla limitaciones para crítica e investigación científica, entre otros supuestos. El proyecto no interpreta esas limitaciones como autorización automática para republicar un corpus textual o visual íntegro.

### Semáforo de publicación

**VERDE — puede versionarse/publicarse en el repositorio:**

- metadatos bibliográficos y técnicos;
- claves e identificadores del visor;
- URLs de procedencia;
- número de páginas y manifiestos de URLs;
- dimensiones, formatos y hashes cuando corresponda;
- conteos, frecuencias, estadísticas y medidas agregadas;
- etiquetas analíticas y clasificaciones;
- código, esquemas y documentación metodológica;
- resultados comparativos que no reproduzcan sustancialmente los libros.

**AMARILLO — conservar como material de trabajo hasta aclarar:**

- OCR completo por página;
- transcripciones extensas;
- fragmentos largos;
- miniaturas, portadas u otras reproducciones visuales.

**NO PUBLICAR POR AHORA:**

- JPEG originales del visor;
- libros completos o espejos del catálogo;
- paquetes masivos de archivos fuente descargados.

## Reglas para CI y automatización

1. Las imágenes fuente sólo podrán descargarse a almacenamiento temporal del runner.
2. Los workflows públicos no subirán imágenes ni texto OCR completo como artefactos.
3. Los artefactos de CI se limitarán a métricas, metadatos, estados de validación y resultados derivados.
4. Cualquier cambio que pretenda publicar OCR íntegro, imágenes o miniaturas requerirá revisar primero el issue jurídico correspondiente.
5. Las páginas legales de los ejemplares concretos del piloto deberán verificarse antes de cerrar la política definitiva.

## Fuentes documentales de referencia

- CONALITEG, “Los libros de texto gratuitos al alcance de todos”: https://www.gob.mx/conaliteg/articulos/los-libros-de-texto-gratuitos-al-alcance-de-todos
- Términos y condiciones de uso del portal gob.mx: https://www.gob.mx/terminos
- Ley Federal del Derecho de Autor, texto vigente consultable en Orden Jurídico Nacional: https://www.ordenjuridico.gob.mx/

Esta política es una medida interna de gobernanza de investigación y no sustituye asesoría jurídica profesional.
