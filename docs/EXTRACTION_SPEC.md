# Especificación de extracción y control de calidad — piloto 0.1

## Objetivo

Definir de antemano cómo pasar de los cuatro visores oficiales a un corpus analítico reproducible sin convertir el repositorio GitHub en un espejo de materiales fuente.

## Capas de datos

### Capa A — fuente / copia de trabajo

Archivos o imágenes necesarios para procesamiento local. **No se versionan en GitHub** salvo que posteriormente exista una base jurídica explícita para hacerlo.

Cada copia de trabajo deberá registrar:

- `book_id`;
- URL oficial;
- fecha de obtención;
- método de obtención;
- número de recursos/páginas;
- hash/checksum cuando sea posible;
- observaciones de integridad.

### Capa B — extracción intermedia

Texto por página y metadatos técnicos. Por defecto se conserva localmente hasta aclarar derechos de redistribución de transcripciones extensas.

Formato lógico mínimo por página:

- `page_id`;
- `book_id`;
- `file_page_number`;
- `printed_page_number` si puede identificarse;
- `page_type`;
- `extraction_method`;
- `text_length_chars`;
- `ocr_engine` si aplica;
- `ocr_quality_status`;
- `source_asset_hash` cuando exista.

### Capa C — datos derivados publicables

Información que no reproduce sustancialmente el libro:

- conteos;
- etiquetas analíticas;
- clasificación de fragmentos;
- frecuencias de acciones pedagógicas;
- medidas estructurales;
- entidades y conceptos cuando sean justificables;
- estadísticas de imágenes/actividades;
- resultados comparativos.

Esta capa será la base de los CSV/JSON versionados en GitHub.

## Orden técnico de extracción

1. auditar el HTML/visor;
2. identificar si existe PDF, texto nativo, imágenes por página u otro formato;
3. contar y enumerar recursos;
4. conservar una manifestación local con URL/hash, no necesariamente los binarios;
5. intentar extracción de texto nativo;
6. usar OCR sólo para páginas que carezcan de texto útil;
7. normalizar saltos de línea y caracteres sin borrar la transcripción original de trabajo;
8. segmentar por unidades funcionales;
9. generar únicamente después los datos derivados.

## Tipos de página

Lista inicial:

- `cover`
- `legal`
- `presentation`
- `toc`
- `chapter_or_block_opener`
- `content`
- `activity`
- `assessment`
- `back_matter`
- `unknown`

Una página puede contener actividad y texto expositivo simultáneamente; `page_type` describe su función predominante y las variables binarias registran rasgos adicionales.

## Muestra de control de calidad textual

Para cada libro se seleccionarán inicialmente **12 páginas estratificadas**, siempre que existan:

- página legal;
- índice;
- 2 páginas del primer cuarto;
- 3 del segundo cuarto;
- 3 del tercer cuarto;
- 2 del último cuarto.

Total previsto: hasta 48 páginas para los cuatro libros.

Si una página seleccionada contiene muy poco texto, se sustituirá por la página de contenido más cercana y se registrará la sustitución.

## Validación de OCR

En cada página de control se transcribirá manualmente una muestra textual suficiente para comparar salida automática y referencia humana.

Métricas previstas:

- tasa de error de caracteres (CER);
- tasa de error de palabras (WER), cuando la tokenización sea estable;
- proporción de caracteres anómalos;
- porcentaje de páginas vacías o con extracción fallida.

Los umbrales serán **criterios internos del proyecto**, no estándares universales:

- CER ≤ 2 %: extracción excelente para análisis léxico;
- CER > 2 % y ≤ 5 %: utilizable con normalización y cautela;
- CER > 5 % y ≤ 10 %: requiere corrección o uso analítico limitado;
- CER > 10 %: no usar para análisis textual automático sin intervención adicional.

La clasificación podrá revisarse tras observar la distribución real de errores, pero cualquier cambio quedará registrado en `docs/DECISIONS.md`.

## Segmentación funcional

La segmentación deberá conservar una relación trazable:

`book_id → page_id → fragment_id`

El fragmento analítico corresponderá preferentemente a:

- una consigna;
- una pregunta;
- una explicación autónoma;
- una actividad delimitada;
- un elemento de evaluación;
- un bloque corto de texto expositivo cuando sea necesario para análisis temático.

No se publicará automáticamente el texto completo del fragmento hasta resolver el issue jurídico correspondiente. La tabla derivada puede conservar hashes, longitud, etiquetas y conteos sin reproducir el contenido.

## Muestreo para validar el libro de códigos

Una vez segmentado el corpus se tomarán **25 fragmentos por generación**, estratificados por tipo de página y posición en el libro. Los 100 fragmentos se codificarán manualmente antes de entrenar o aplicar clasificadores automáticos.

## Criterio de éxito técnico del piloto

El pipeline supera la prueba técnica si:

1. los cuatro libros pueden enumerarse de manera reproducible;
2. al menos 90 % de las páginas de contenido producen texto procesable mediante extracción nativa u OCR;
3. existe una muestra humana que permita cuantificar error;
4. cada fragmento derivado conserva trazabilidad a libro y página;
5. el análisis comparativo puede regenerarse desde scripts documentados;
6. ningún paso exige publicar en GitHub archivos fuente cuya redistribución no esté aclarada.
