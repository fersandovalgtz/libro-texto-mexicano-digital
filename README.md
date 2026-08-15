# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante métodos de historia de la educación, humanidades digitales, análisis computacional de textos e imágenes y ciencia abierta.

## Estado

**Piloto 0.1 — viabilidad técnica demostrada; validación humana y construcción del dataset analítico en curso.**

El corpus mínimo está formado por **Ciencias Naturales de quinto grado** en cuatro generaciones del Catálogo Histórico de CONALITEG: **1972, 1988, 1993 y 2014**.

La etiqueta de generación se conserva separada del año bibliográfico de la edición concreta. Las fechas de edición sólo se fijan cuando pueden verificarse en la página legal o en una fuente primaria equivalente.

La arquitectura de los cuatro visores ya fue reconstruida. `claves.json` declara 763 páginas de visor, pero la auditoría integral demostró que cada libro contiene una página terminal sintética sin JPEG. El corpus fuente real del piloto es de **759 imágenes**. El barrido OCR integral detectó texto en **698 activos (91.96 %)** sin publicar ni versionar las transcripciones.

## Pregunta general

¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

## Pregunta del piloto 0.1

¿Cómo cambian entre generaciones curriculares la representación de la ciencia y el ambiente, el papel atribuido al alumno y el tipo de actividad pedagógica propuesta en los libros de Ciencias Naturales de quinto grado?

## Principio de procedencia

Este repositorio **no pretende redistribuir indiscriminadamente PDF, imágenes, OCR completo ni otros materiales originales de CONALITEG u otras instituciones**. Los originales se documentan mediante identificadores, URL de procedencia y metadatos. Las imágenes fuente y las transcripciones extensas se utilizan únicamente como copias temporales/de trabajo mientras no exista una base jurídica explícita para redistribuirlas.

GitHub aloja principalmente:

- código y scripts reproducibles;
- esquemas y diccionarios de datos;
- registros de fuentes y procedencia;
- documentación metodológica;
- datos derivados cuya redistribución sea jurídicamente procedente;
- muestras de metadatos y registros de validación;
- resultados reproducibles del piloto.

## Arquitectura observada del corpus piloto

`visor HTML → x.js → claves.json → magazine.js → JPEG de página → OCR temporal → métricas/datos derivados`

La arquitectura analítica prevista continúa como:

`fuente → inventario → ingestión → OCR/parsing → normalización → metadatos → unidades analíticas → datos derivados → análisis → visualización → publicación`

## Estructura

- `docs/` — metodología, modelo de datos, contexto curricular, libro de códigos, gobernanza, decisiones y roadmap.
- `data/` — inventario, registros de control y datos derivados publicables.
- `scripts/` — rutinas reproducibles de inspección, ingestión, OCR, transformación y validación.
- `src/` — componentes reutilizables del proyecto.
- `notebooks/` — exploración reproducible y análisis del piloto.

Documentos metodológicos centrales:

- `docs/PILOT_0_1.md` — definición del corpus y pregunta del piloto;
- `docs/CURRICULAR_CONTEXT.md` — matriz histórica de las cuatro generaciones;
- `docs/CODEBOOK_0_1.md` — categorías preregistradas de acción pedagógica y posición del alumno;
- `docs/EXTRACTION_SPEC.md` — protocolo de extracción y control de calidad;
- `docs/OCR_BENCHMARK_2026-08-15.md` — diagnóstico de concurrencia y configuración OCR;
- `docs/FULL_PILOT_OCR_PROFILE_2026-08-15.md` — perfil integral de los 759 activos;
- `docs/HUMAN_CODEBOOK_VALIDATION_PROTOCOL.md` — protocolo previo a cualquier clasificación automática;
- `docs/DATA_MODEL.md` — modelo mínimo de datos;
- `docs/DATA_GOVERNANCE.md` — reglas de procedencia, derechos y publicación;
- `docs/DECISIONS.md` — decisiones metodológicas que modifican el procedimiento.

## Fuente inicial

Catálogo Histórico de Libros de Texto Gratuitos de CONALITEG y catálogos contemporáneos. Toda ingestión conserva la procedencia de cada unidad documental.

## Avance del piloto 0.1

- [x] Fijar asignatura y grado comparables: Ciencias Naturales, quinto grado.
- [x] Seleccionar cuatro generaciones: 1972, 1988, 1993 y 2014.
- [x] Construir inventario inicial con URLs oficiales.
- [x] Separar generación del catálogo, año bibliográfico y copyright.
- [x] Formular pregunta longitudinal y variables iniciales.
- [x] Preregistrar libro de códigos analítico.
- [x] Definir protocolo de extracción y control de OCR.
- [x] Auditar recursos subyacentes de los cuatro visores.
- [x] Resolver la arquitectura de imágenes y construir manifiesto reproducible.
- [x] Localizar páginas legales e índices en los cuatro libros.
- [x] Verificar bibliografía primaria disponible: 1993 = primera edición 1998; 2014 = tercera edición revisada 2014.
- [x] Ejecutar OCR técnico integral de los 759 JPEG sin persistir transcripciones.
- [x] Superar el umbral técnico global de páginas con texto: 91.96 %.
- [x] Preregistrar muestra de 48 páginas para CER/WER.
- [x] Preregistrar pool de 100 páginas para validación humana del libro de códigos.
- [ ] Completar CER/WER contra referencia humana.
- [ ] Auditar las 61 páginas `no_text_detected` y distinguir falsos negativos de páginas visuales/casi vacías.
- [ ] Codificar manualmente 25 fragmentos por generación.
- [ ] Revisar/estabilizar el libro de códigos.
- [ ] Generar primer dataset derivado por fragmento.
- [ ] Producir la primera comparación histórica reproducible.
- [ ] Decidir si conviene escalar al catálogo completo.

## Registro metodológico

Además del historial de commits y esta documentación, el proyecto mantiene una **bitácora técnica detallada en Notion**. La bitácora conserva secuencia operativa, intentos fallidos, parámetros, hallazgos, correcciones, límites interpretativos y decisiones. GitHub conserva la capa técnica reproducible; Notion conserva el relato metodológico completo.

## Autoría y citación

Proyecto dirigido por Fernando Sandoval Gutiérrez. La forma de citación, versión archivada y DOI se formalizarán cuando el piloto alcance una primera liberación estable.

## Licencias y derechos

La licencia del código y de los datos derivados se definirá una vez concluida la auditoría inicial de derechos y términos de uso. Los derechos sobre materiales fuente permanecen con sus respectivos titulares.
