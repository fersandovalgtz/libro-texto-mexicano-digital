# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante métodos de historia de la educación, humanidades digitales, análisis computacional de textos e imágenes y ciencia abierta.

## Estado

**Piloto 0.1 — corpus fijado; extracción y prueba de viabilidad en curso.**

El proyecto inicia con un corpus pequeño y reproducible antes de cualquier ingestión masiva. El corpus mínimo está formado por **Ciencias Naturales de quinto grado** en cuatro generaciones del Catálogo Histórico de CONALITEG: **1972, 1988, 1993 y 2014**.

La etiqueta de generación se conserva separada del año bibliográfico de la edición concreta. Las fechas de edición sólo se fijarán cuando puedan verificarse en la página legal o en una fuente primaria equivalente.

## Pregunta general

¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

## Pregunta del piloto 0.1

¿Cómo cambian entre generaciones curriculares la representación de la ciencia y el ambiente, el papel atribuido al alumno y el tipo de actividad pedagógica propuesta en los libros de Ciencias Naturales de quinto grado?

## Principio de procedencia

Este repositorio **no pretende redistribuir indiscriminadamente PDF, imágenes ni otros materiales originales de CONALITEG u otras instituciones**. Los originales se documentarán mediante identificadores, URL de procedencia y metadatos. Sólo se versionarán localmente o publicarán materiales cuando su condición jurídica y términos de uso lo permitan.

GitHub alojará principalmente:

- código y scripts reproducibles;
- esquemas y diccionarios de datos;
- registros de fuentes y procedencia;
- documentación metodológica;
- datos derivados cuya redistribución sea jurídicamente procedente;
- muestras permitidas para pruebas;
- resultados reproducibles del piloto.

## Arquitectura prevista

`fuente → inventario → ingestión → OCR/parsing → normalización → metadatos → unidades analíticas → datos derivados → análisis → visualización → publicación`

## Estructura

- `docs/` — metodología, modelo de datos, contexto curricular, libro de códigos, gobernanza y roadmap.
- `data/` — inventario y, cuando proceda, muestras o datos derivados.
- `scripts/` — rutinas reproducibles de inspección, ingestión, OCR, transformación y validación.
- `src/` — componentes reutilizables del proyecto.
- `notebooks/` — exploración reproducible y análisis del piloto.

Documentos metodológicos centrales:

- `docs/PILOT_0_1.md` — definición del corpus y pregunta del piloto;
- `docs/CURRICULAR_CONTEXT.md` — matriz histórica de las cuatro generaciones;
- `docs/CODEBOOK_0_1.md` — categorías preregistradas de acción pedagógica y posición del alumno;
- `docs/EXTRACTION_SPEC.md` — protocolo de extracción y control de calidad;
- `docs/DATA_MODEL.md` — modelo mínimo de datos;
- `docs/DATA_GOVERNANCE.md` — reglas de procedencia, derechos y publicación.

## Fuente inicial

Catálogo Histórico de Libros de Texto Gratuitos de CONALITEG y catálogos contemporáneos. Toda ingestión deberá conservar la procedencia de cada unidad documental.

## Avance del piloto 0.1

- [x] Fijar asignatura y grado comparables: Ciencias Naturales, quinto grado.
- [x] Seleccionar cuatro generaciones: 1972, 1988, 1993 y 2014.
- [x] Construir inventario inicial con URLs oficiales.
- [x] Separar generación del catálogo y año bibliográfico de la edición.
- [x] Formular pregunta longitudinal y variables iniciales.
- [x] Preregistrar libro de códigos analítico.
- [x] Definir protocolo de extracción y control de OCR.
- [ ] Auditar recursos subyacentes de los cuatro visores.
- [ ] Confirmar páginas legales, años de edición y número de páginas.
- [ ] Extraer/segmentar texto de trabajo y medir calidad.
- [ ] Generar primer dataset derivado por página/fragmento.
- [ ] Producir la primera comparación histórica reproducible.
- [ ] Decidir si conviene escalar al catálogo completo.

## Autoría y citación

Proyecto dirigido por Fernando Sandoval Gutiérrez. La forma de citación, versión archivada y DOI se formalizarán cuando el piloto alcance una primera liberación estable.

## Licencias y derechos

La licencia del código y de los datos derivados se definirá una vez concluida la auditoría inicial de derechos y términos de uso. Los derechos sobre materiales fuente permanecen con sus respectivos titulares.
