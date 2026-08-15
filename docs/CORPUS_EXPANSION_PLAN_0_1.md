# Plan de expansión controlada del corpus — LTMD 0.1

Fecha: 2026-08-15

## Principio

La expansión puede comenzar **antes de SEMB 0.3**, siempre que se limite a inventario, procedencia, adquisición temporal, auditoría de activos, OCR, estructura y segmentación. La clasificación semántica productiva de nuevos libros debe esperar a que el modelo validado exista y se congele.

## Unidad de expansión

Cada nuevo libro se incorpora como un objeto versionado con:

- `book_id` estable;
- nivel/grado/asignatura;
- `catalog_generation`;
- `edition_year` separado y sólo poblado si está verificado;
- edición/reimpresión/copyright/ISBN si existen;
- URL de visor y repositorio fuente;
- conteo de páginas declarado versus activos reales;
- páginas legales e índices identificados;
- estado de derechos/procedencia;
- manifest de páginas con hashes;
- auditoría OCR;
- PAGESTRUCT;
- FRAGSEG o versión futura compatible.

## Ola 1 — completar Ciencias Naturales de primaria superior

Objetivo: construir comparabilidad vertical sin cambiar todavía de dominio disciplinar.

Prioridad:

1. Ciencias Naturales 4º — generaciones 1972, 1988, 1993 y 2014 cuando existan como objetos comparables;
2. Ciencias Naturales 6º — mismas generaciones;
3. documentar excepciones cuando una generación use estructura integrada o no tenga objeto directamente equivalente.

Razón: el piloto de 5º ya aporta vocabulario, infraestructura y conocimiento de la arquitectura del visor. Los grados 4º–6º permiten estudiar si los patrones son específicos de quinto o forman una secuencia curricular.

## Ola 2 — Matemáticas

Construir una segunda familia disciplinar con fuerte presencia de consignas y resolución de problemas. Mantener ontología pedagógica común cuando sea válida, pero no asumir que todas las categorías de Ciencias Naturales transfieren con igual significado.

Antes de clasificación semántica se realizará una auditoría conceptual de `CODEBOOK_0_1` para decidir qué acciones son disciplina-generales y cuáles requieren extensiones.

## Ola 3 — Español / Lengua

Usar como contraste de régimen pedagógico: lectura, producción textual, conversación, interpretación y reflexión lingüística. Es probable que requiera ampliar acciones y posiciones; por ello debe tratarse como nueva versión de ontología y no simplemente ejecutarse con SEMB 0.3 de ciencias.

## Ola 4 — Ciencias Sociales / Historia / Geografía

La expansión deberá modelar explícitamente los cambios de organización disciplinar entre periodos. No comparar automáticamente “Ciencias Sociales” de un periodo con “Historia” o “Geografía” de otro como si fueran equivalentes documentales.

## Ola 5 — primeros grados / libros integrados

Tratar como corpus metodológicamente distinto. La unidad libro-asignatura puede desaparecer o mezclarse; la segmentación y el contexto visual adquieren mayor peso. No incorporarlos al mismo análisis longitudinal hasta definir una ontología documental compatible.

## Etapas permitidas antes de referencia humana SEMB 0.3

### Permitidas

- descubrimiento e inventario de visores;
- auditoría de disponibilidad;
- identificación de página legal, índice y paratextos;
- reconstrucción de activos;
- hashes y procedencia;
- OCR temporal y métricas técnicas;
- PAGESTRUCT;
- segmentación;
- estadísticas descriptivas no semánticas;
- documentación curricular/bibliográfica;
- auditorías de derechos;
- construcción de muestras humanas futuras.

### Bloqueadas

- usar candidatos sintéticos SEMB 0.3 como etiquetas definitivas;
- recalibrar el modelo con distribuciones de las nuevas generaciones;
- producir narrativa histórica comparativa basada en clasificador no validado;
- mezclar resultados de ontologías diferentes sin una tabla formal de correspondencia.

## Criterio de entrada de un nuevo objeto

Un libro puede declararse `corpus_ready` sólo si:

1. visor/activo fuente verificable;
2. inventario bibliográfico mínimo documentado;
3. páginas fuente auditadas y con hashes;
4. OCR/estructura ejecutables reproduciblemente;
5. derechos y política de redistribución documentados;
6. ninguna inconsistencia crítica de conteo permanece sin explicación.

Puede declararse `semantic_ready` únicamente después de existir un modelo/ontología validado apropiado para su dominio.

## Identificadores sugeridos

Mantener la convención:

`LTMD-{AREA}{GRADO}-G{GENERACION}`

Ejemplos previstos:

- `LTMD-CN4-G1972`
- `LTMD-CN6-G2014`
- `LTMD-MAT5-G1993`

La convención no codifica `edition_year`; éste permanece como metadato separado.

## Próximo trabajo automatizable

1. descubrir los visores de Ciencias Naturales 4º y 6º en las cuatro generaciones objetivo;
2. crear inventario preliminar con estatus `discovered_unverified`;
3. auditar front matter y activos;
4. ejecutar el pipeline técnico hasta FRAGSEG sin clasificación semántica;
5. comparar únicamente propiedades documentales/técnicas con el piloto de 5º.
