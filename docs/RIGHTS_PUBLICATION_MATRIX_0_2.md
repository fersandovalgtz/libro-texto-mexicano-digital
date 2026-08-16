# Matriz de derechos y publicación — LTMD 0.2

Fecha de revisión: **15 de agosto de 2026**  
Alcance: **v0.1.0-rc.1 / corpus escalado de Ciencias Naturales**

> Política conservadora de gestión de riesgo. No es una opinión jurídica vinculante. Una autorización o término específico emitido por CONALITEG/SEP o por el titular competente prevalece y debe incorporarse documentalmente.

## Fuentes oficiales verificadas

1. Catálogo Histórico de CONALITEG: https://historico.conaliteg.gob.mx/
2. Términos y condiciones de gob.mx: https://www.gob.mx/terminos
3. Ley Federal del Derecho de Autor — ficha oficial de la Cámara de Diputados; última reforma publicada señalada por la ficha: **15 de enero de 2026**: https://www.diputados.gob.mx/LeyesBiblio/ref/lfda.htm
4. Texto de consulta de la LFDA, incluidos artículos 107 y 148: https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17068.html
5. Creative Commons — licencias y datos: https://creativecommons.org/faq/
6. Apache License 2.0 — texto y guía oficial: https://www.apache.org/licenses/LICENSE-2.0

## Principio rector

La existencia de acceso público a un visor **no se interpreta como licencia abierta de redistribución**. Los términos generales de gob.mx permiten visualizar/descargar para uso personal y no comercial y contienen restricciones sobre modificación, reproducción pública/comercial, distribución y transferencia.

LTMD mantiene por ello una arquitectura que separa:

- **material fuente de terceros**;
- **copias temporales de trabajo**;
- **datos derivados no sustitutivos**;
- **código/documentación original de LTMD**.

## Semáforo de publicación

### VERDE — publicable/versionable con trazabilidad

- identificadores LTMD (`book_id`, `page_id`, `fragment_id`);
- generación, grado, asignatura y año/edición cuando estén verificados;
- ISBN y otros hechos bibliográficos;
- URLs oficiales de procedencia;
- tamaños, dimensiones y SHA-256;
- estados de resolución de activos;
- métricas OCR y conteos de texto sin transcripción íntegra;
- PAGESTRUCT/FRAGSEG como categorías y metadatos;
- códigos/etiquetas analíticas originales;
- frecuencias, agregados y resultados estadísticos;
- relaciones de alias, reutilización, revisión y reemplazo;
- manifiestos de gaps y estados técnicos;
- código, workflows y documentación propios;
- tablas derivadas que no reproduzcan expresión sustancial de la obra fuente.

### AMARILLO — trabajo interno o publicación caso por caso

- OCR completo mantenido localmente;
- transcripciones extensas;
- fragmentos textuales necesarios para ejemplos/validación;
- portadas, miniaturas y recortes;
- ilustraciones;
- embeddings u otras representaciones cuya capacidad de reconstrucción sea material;
- colecciones de muchos fragmentos que, acumulados, aproximen contenido sustancial de una obra.

La publicación requiere necesidad científica, proporcionalidad, atribución, análisis de sustitución y fundamento aplicable.

### ROJO — no publicar sin autorización/fundamento específico

- JPEG originales completos;
- PDF o reconstrucciones completas de libros;
- espejos del Catálogo Histórico;
- OCR íntegro públicamente reconstruible;
- dataset secuencial que permita reconstruir sustancialmente el texto completo;
- paquetes masivos de páginas o ilustraciones;
- redistribución a terceros de los archivos fuente descargados.

## Aplicación al corte v0.1.0-rc.1

| Componente | Estado | Política |
|---|---|---|
| Catálogo normalizado de 542 visores | Verde | metadatos/procedencia, no espejo de activos |
| Readiness 37 visores CN | Verde | estados, URLs, hashes, tamaños |
| Alias 2018→2019 | Verde | relaciones y evidencia hash; no duplicar JPEG |
| Auditoría 2008 | Verde | registrar posiciones internas no servidas sin inventar hecho bibliográfico |
| Manifiestos de páginas CN5/CN4/CN6/Ola2 | Verde | hashes/procedencia, no imagen fuente |
| Métricas OCR | Verde | métricas sin OCR íntegro |
| OCR temporal | Amarillo | procesamiento interno y eliminación posterior |
| PAGESTRUCT/FRAGSEG | Verde | categorías/metadatos derivados |
| Manifiestos de fragmentos | Verde sólo si no contienen texto fuente sustitutivo | mantener hashes/categorías, controlar cualquier campo textual |
| SEMB 0.2 resultados/diagnósticos | Verde | derivados analíticos; resultados históricos siguen exploratorios |
| Muestra SEMB 0.3 por IDs opacos | Verde | sin gold humano ni texto fuente masivo público |
| Gold/reference humana futura | Revisión previa | decidir publicación y derechos tras el gate correspondiente |
| Imágenes/páginas completas | Rojo | no incluir en GitHub/Zenodo |
| Código LTMD | Verde respecto de contenido | licencia propia aún debe adoptarse formalmente |
| Datos derivados LTMD | Verde respecto de contenido | licencia propia debe definir alcance y exclusiones |

## Ley Federal del Derecho de Autor y bases de datos

El artículo 107 establece protección de bases de datos/compilaciones cuando la selección o disposición constituya creación intelectual y aclara que esa protección no se extiende a los datos y materiales en sí mismos. LTMD no utiliza una licencia de derivados para reclamar exclusividad sobre hechos bibliográficos o hechos no protegibles.

El artículo 148 contempla usos limitados de obras divulgadas, incluidos la cita que no constituya reproducción simulada/sustancial y la reproducción de partes para crítica o investigación científica, sujetos a condiciones legales. LTMD **no** interpreta estas limitaciones como permiso general para redistribuir el OCR completo o las páginas de los libros.

## Licencias de las contribuciones propias

La recomendación de gobernanza para cerrar los blockers de la candidata es:

- **código original LTMD:** Apache License 2.0;
- **metadatos/derivados originales LTMD, en la medida en que existan derechos licenciables:** CC BY 4.0;
- **materiales fuente CONALITEG/SEP/terceros:** excluidos expresamente de ambas licencias.

La decisión completa y sus cautelas están en `LICENSE_DECISION_MEMO_0_1.md`. Las licencias no se consideran aplicadas hasta que existan los archivos correspondientes y el preflight marque `publish_ready=true`.

## Creative Commons: cautelas

CC BY 4.0 permite compartir y adaptar con atribución y puede utilizarse para bases de datos. Creative Commons desaconseja NC/ND para bases de datos científicas. Al mismo tiempo, las licencias CC son irrevocables respecto de quienes reciben material bajo ellas y sólo deben aplicarse cuando quien licencia posee o controla los derechos necesarios.

Esto hace indispensable una cláusula de **alcance limitado** en `DATA_LICENSE.md`: licenciar sólo las aportaciones originales de LTMD y excluir de forma visible texto, páginas, imágenes, ilustraciones, marcas y demás materiales de terceros.

## Operación técnica obligatoria

Para cualquier pipeline que necesite fuente protegida:

1. reconstruir/descargar temporalmente;
2. verificar SHA-256 contra el manifiesto;
3. procesar;
4. persistir únicamente outputs permitidos;
5. eliminar la copia temporal;
6. impedir que `private/`, `data/raw/` o `data/work/` entren al control de versiones.

El preflight de `v0.1.0-rc.1` automatiza parte de esta última defensa mediante `git ls-files`.

## Consulta institucional pendiente

Se mantiene como buena práctica solicitar a CONALITEG/SEP aclaración sobre OCR académico, publicación de fragmentos breves y posibles términos específicos distintos de los generales de gob.mx. El Catálogo Histórico publica actualmente el contacto `info@conaliteg.gob.mx`.

La falta de esa aclaración **no impide** publicar código, metadatos, hashes, métricas y análisis propios bajo una política conservadora; sí aconseja mantener amarillos/rojos fuera del paquete público hasta contar con fundamento suficiente.
