# Derechos, reutilización y minimización de redistribución — LTMD 0.1

Fecha: 2026-08-15

> Documento metodológico, no dictamen jurídico. La política se formula de manera conservadora mientras no exista una autorización/licencia expresa aplicable a los activos fuente concretos.

## Distinción básica

LTMD separa tres capas:

1. **material fuente**: libros, páginas JPEG, ilustraciones y texto íntegro servido por CONALITEG/SEP;
2. **copias temporales de trabajo**: bytes reconstruidos para OCR, verificación o análisis y eliminados al terminar el proceso;
3. **derivados LTMD**: metadatos, identificadores, hashes, métricas técnicas, scores, etiquetas analíticas, resúmenes agregados, protocolos, código y documentación producida por el proyecto.

La disponibilidad pública de un visor no se interpreta automáticamente como licencia de redistribución de los materiales fuente.

## Evidencia institucional consultada

CONALITEG se describe institucionalmente como el organismo encargado de producir y distribuir los Libros de Texto Gratuitos y señala que los contenidos educativos son desarrollados por la autoridad educativa correspondiente.

La institución mantiene asimismo apartados de transparencia, gobierno abierto y datos abiertos, además de conjuntos específicos de datos abiertos vinculados, entre otros temas, con distribución, proveedores y producción. En las páginas institucionales consultadas para esta auditoría **no se identificó una licencia abierta general aplicable de forma inequívoca a todos los archivos de imagen, texto u OCR de los libros históricos alojados en los visores**.

Fuentes institucionales consultadas:

- Catálogo/libros CONALITEG: https://libros.conaliteg.gob.mx/
- Política de Transparencia, Gobierno Abierto y Datos Abiertos: https://www.conaliteg.gob.mx/transparencia/transparencia_politica_transparencia.php
- Transparencia focalizada / Datos Abiertos: https://www.conaliteg.gob.mx/transparencia/transparencia_focalizada.php

## Política de LTMD para material fuente

Hasta contar con licencia/autorización expresa o una conclusión jurídica específica por objeto:

- **no** versionar masivamente los JPEG fuente en GitHub;
- **no** publicar OCR íntegro que funcione como sustituto textual del libro;
- **no** relicenciar materiales CONALITEG/SEP como si fueran obra original de LTMD;
- conservar URL, clave de visor, número de página, tamaño y SHA-256 para permitir trazabilidad;
- reconstruir imágenes/texto sólo de forma temporal durante workflows;
- publicar ejemplos mínimos únicamente cuando exista una justificación metodológica y de derechos documentada;
- separar la licencia futura del código/derivados LTMD de los derechos de las fuentes.

## Derivados de bajo riesgo de sustitución

El repositorio prioriza outputs que no permiten reconstruir por sí solos el libro completo:

- inventario bibliográfico;
- `page_id`, `fragment_id`, `book_id`;
- URL y claves de procedencia;
- SHA-256 y tamaños de archivo;
- métricas OCR sin transcripción;
- clases PAGESTRUCT;
- longitudes y señales funcionales de FRAGSEG;
- etiquetas/estadísticas computacionales cuando no contienen el texto fuente;
- matrices de solapamiento por hash;
- resultados agregados;
- código, protocolos y criterios de validación.

Los hashes se consideran mecanismos de integridad/procedencia, no copias del contenido.

## Fragmentos textuales y anotación humana

La herramienta de anotación debe reconstruir el texto de forma efímera y mostrar sólo la unidad necesaria al anotador. Las plantillas y resultados públicos persisten códigos/IDs, no el texto íntegro. Si en un artículo se requieren ejemplos textuales, se seleccionarán de manera limitada y con finalidad de crítica/análisis, documentando fuente y página.

## Licencias futuras de LTMD

Antes de la primera release estable deben resolverse por separado:

- licencia del **código** producido por LTMD;
- licencia de **metadatos y derivados originales** de LTMD;
- nota explícita de exclusión de derechos sobre los materiales fuente;
- tratamiento de tablas/outputs que eventualmente incorporen cantidades sustitutivas de texto fuente.

No debe colocarse una licencia única sobre todo el repositorio si puede interpretarse como licencia sobre materiales cuyo titular es tercero.

## Señal de datos abiertos

La existencia de una política gubernamental de datos abiertos es relevante para metadatos/conjuntos expresamente publicados bajo ese régimen, pero LTMD **no extrapola** esa condición a los libros digitalizados sin identificar el instrumento/licencia aplicable al activo concreto.

## Próximo control recomendado

Para una release científica:

1. archivar evidencia de las condiciones de uso vigentes en la fecha de release;
2. revisar página legal y titularidad de cada objeto;
3. decidir licencia del código y derivados LTMD de forma independiente;
4. si se desea redistribuir imágenes/OCR, obtener antes una base jurídica o autorización explícita y documentarla por versión.
