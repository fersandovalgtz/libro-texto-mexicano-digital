# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante métodos de historia de la educación, humanidades digitales, análisis computacional de textos e imágenes y ciencia abierta.

## Estado

**Piloto 0.1 — diseño del corpus y prueba de viabilidad.**

El proyecto inicia con un corpus pequeño y reproducible antes de cualquier ingestión masiva. El objetivo del piloto es demostrar que una selección histórica de libros permite producir comparaciones y datos derivados que no ofrece por sí solo el repositorio de origen.

## Pregunta general

¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

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

- `docs/` — metodología, modelo de datos, gobernanza y roadmap.
- `data/` — documentación y, cuando proceda, muestras o datos derivados.
- `scripts/` — rutinas reproducibles de ingestión, OCR, transformación y validación.
- `src/` — componentes reutilizables del proyecto.
- `notebooks/` — exploración reproducible y análisis del piloto.

## Fuente inicial

Catálogo Histórico de Libros de Texto Gratuitos de CONALITEG y catálogos contemporáneos. Toda ingestión deberá conservar la procedencia de cada unidad documental.

## Alcance del piloto 0.1

1. Elegir un grado/asignatura o línea curricular comparable.
2. Seleccionar tres o cuatro cortes temporales.
3. Construir inventario y metadatos mínimos.
4. Probar extracción de texto y segmentación por página.
5. Definir variables longitudinales.
6. Producir al menos una comparación histórica reproducible.
7. Decidir si conviene escalar al catálogo completo.

## Autoría y citación

Proyecto dirigido por Fernando Sandoval Gutiérrez. La forma de citación, versión archivada y DOI se formalizarán cuando el piloto alcance una primera liberación estable.

## Licencias y derechos

La licencia del código y de los datos derivados se definirá una vez concluida la auditoría inicial de derechos y términos de uso. Los derechos sobre materiales fuente permanecen con sus respectivos titulares.
