# Memorando de decisión de licencias — LTMD 0.1

Fecha: **2026-08-15**  
Estado: **recomendación pre-release; no constituye por sí misma aplicación de licencia**.

## Decisión que debe cerrarse

El preflight de `v0.1.0-rc.1` identifica exactamente dos blockers de publicación:

1. licencia del código propio de LTMD;
2. licencia/política de reutilización de los datos y derivados originales de LTMD.

La decisión debe ser separada de los materiales fuente de CONALITEG/SEP: ninguna licencia que adopte LTMD puede otorgar derechos sobre obras, páginas, imágenes, ilustraciones o expresión textual de terceros que LTMD no posea o controle.

## Recomendación principal

### 1. Código propio: Apache License 2.0

**Recomendación:** aplicar `Apache-2.0` al código, scripts y workflows originales de LTMD sobre los que el titular del proyecto posea o controle los derechos necesarios.

Razones:

- es una licencia de software abierta, reconocida y reutilizable por proyectos que no pertenecen a Apache;
- permite uso, modificación y distribución bajo condiciones claras;
- incluye términos explícitos sobre contribuciones y patentes, útiles para una infraestructura científica que puede recibir colaboración futura;
- puede identificarse de forma estándar mediante `SPDX-License-Identifier: Apache-2.0`;
- la guía oficial indica incluir el texto completo en un archivo raíz `LICENSE` y contempla un archivo `NOTICE` para avisos de atribución.

Fuentes oficiales:

- https://www.apache.org/licenses/LICENSE-2.0
- https://www.apache.org/foundation/license-faq.html
- https://www.apache.org/legal/apply-license

### 2. Datos/derivados originales: CC BY 4.0 con alcance explícitamente limitado

**Recomendación:** aplicar `CC BY 4.0` únicamente a los metadatos, tablas analíticas, códigos, etiquetas, métricas, documentación de datos y otros derivados originales de LTMD **en la medida en que el proyecto posea derechos licenciables sobre ellos**.

Razones:

- permite compartir y adaptar, incluso comercialmente, con obligación de atribución;
- Creative Commons indica que las licencias 4.0 pueden utilizarse para bases de datos y, donde corresponda, cubren derechos sui generis sobre bases de datos;
- Creative Commons desaconseja NC y ND para bases de datos destinadas a uso académico/científico;
- CC BY preserva una obligación explícita de crédito, útil para una infraestructura académica que desea trazabilidad de procedencia y citación.

Fuentes oficiales:

- https://creativecommons.org/licenses/by/4.0/
- https://creativecommons.org/faq/
- https://wiki.creativecommons.org/wiki/Data

## Alternativa para datos: CC0

`CC0` maximizaría la reutilización de datos originales al intentar renunciar a derechos de autor y derechos relacionados en la mayor medida posible. Creative Commons señala que puede ser especialmente útil para ciencia y datos públicos.

No es la recomendación principal para este corte porque **CC0 no exige atribución**. LTMD ya dispone de una arquitectura fuerte de citación/procedencia y puede beneficiarse de que la obligación de crédito permanezca en el instrumento jurídico para sus derivados originales.

Fuente oficial:

- https://creativecommons.org/publicdomain/zero/1.0/

## Por qué no se recomienda NC o ND para el dataset derivado

Creative Commons desaconseja licencias `NonCommercial` o `NoDerivatives` para bases de datos destinadas a uso académico/científico. Además, ND dificultaría transformaciones, validaciones y análisis derivados, que son precisamente usos deseables de LTMD.

## Alcance propuesto de `DATA_LICENSE.md`

La futura política debería decir inequívocamente:

> Salvo indicación contraria, los metadatos, métricas, etiquetas, esquemas y datos derivados originales creados por LTMD se ofrecen bajo CC BY 4.0 únicamente en la medida en que Fernando Sandoval Gutiérrez/LTMD posea derechos licenciables sobre ellos. Esta licencia no se aplica a libros, páginas, imágenes, ilustraciones, texto fuente, OCR sustitutivo, marcas u otros materiales de CONALITEG/SEP o terceros. La inclusión de identificadores, hashes, URLs o hechos bibliográficos no implica reclamación de derechos exclusivos sobre hechos que no sean protegibles.

Debe añadirse además una tabla de inclusiones/exclusiones para evitar que el usuario interprete la licencia del dataset como licencia de la fuente primaria.

## Punto mexicano relevante

La Ley Federal del Derecho de Autor distingue la protección de las bases de datos que constituyan creaciones intelectuales por selección/disposición y señala que esa protección no se extiende a los datos y materiales en sí mismos (artículo 107). El artículo 148 contempla usos limitados de obras divulgadas —entre ellos cita no sustancial y reproducción de partes para crítica/investigación— bajo condiciones; LTMD no interpreta esas excepciones como autorización general para redistribuir OCR o páginas completas.

Fuente oficial:

- https://www.diputados.gob.mx/LeyesBiblio/ref/lfda.htm
- https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17068.html

## Portal fuente

Los términos generales de gob.mx autorizan visualización/descarga para uso personal y no comercial y restringen modificación, reproducción pública/comercial, distribución y transferencia de materiales. El Catálogo Histórico de CONALITEG continúa disponible públicamente y ofrece el canal institucional `info@conaliteg.gob.mx`.

Fuentes oficiales:

- https://www.gob.mx/terminos
- https://historico.conaliteg.gob.mx/

Por ello el modelo actual —reconstrucción temporal, verificación SHA-256, publicación de métricas/metadatos no sustitutivos y no redistribución masiva del contenido fuente— debe mantenerse aunque LTMD adopte licencias abiertas sobre **sus propias** contribuciones.

## Irrevocabilidad y control de derechos

Antes de aplicar CC BY 4.0 debe confirmarse que el titular que la aplica posee o controla los derechos pertinentes. Creative Commons advierte además que sus licencias y CC0 son irrevocables para quienes ya recibieron el material bajo esos términos.

Por esa razón este memorando **no crea todavía `LICENSE` ni `DATA_LICENSE.md`**. La candidata conserva `publish_ready=false` hasta que la decisión sea conscientemente adoptada y materializada.

## Implementación propuesta una vez aprobada la decisión

1. crear `LICENSE` con el texto oficial Apache License 2.0;
2. crear `NOTICE` con identificación del proyecto y advertencia de materiales de terceros;
3. crear `DATA_LICENSE.md` con CC BY 4.0 y exclusiones expresas de fuentes CONALITEG/SEP/terceros;
4. actualizar `CITATION.cff` con identificador de licencia de software si el esquema usado lo permite;
5. actualizar README, matriz de derechos y release notes;
6. ejecutar nuevamente `check-release-candidate.py`;
7. exigir `publish_ready=true` antes de crear el tag.

## Valoración

La combinación **Apache-2.0 para código + CC BY 4.0 para derivados originales**, con exclusiones documentadas para fuentes protegidas, ofrece un equilibrio adecuado entre apertura, reutilización científica, obligación de atribución y separación jurídica de los materiales fuente. Esta recomendación es de gobernanza de repositorio y gestión conservadora de riesgo; no sustituye asesoría jurídica individualizada sobre titularidad o excepciones de derecho de autor.
