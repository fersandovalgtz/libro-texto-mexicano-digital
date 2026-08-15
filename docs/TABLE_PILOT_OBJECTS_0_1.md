# Tabla — Objetos documentales del piloto LTMD 0.1

Tabla canónica para el artículo metodológico. Los campos bibliográficos sólo se consideran verificados cuando proceden de la auditoría del ejemplar concreto; la generación del catálogo se mantiene separada.

| book_id | Grado | Asignatura | Generación CONALITEG | Año de edición verificado | Edición | Copyright | ISBN | Páginas visor | Activos reales | Estado bibliográfico |
|---|---:|---|---:|---:|---|---:|---|---:|---:|---|
| `LTMD-CN5-G1972` | 5º | Ciencias Naturales | 1972 | — | — | señal 1972 | — | 259 | 258 | año de edición no verificado |
| `LTMD-CN5-G1988` | 5º | Ciencias Naturales | 1988 | — | — | 1977 | 968-29-0758-6 | 163 | 162 | año de edición no verificado |
| `LTMD-CN5-G1993` | 5º | Ciencias Naturales | 1993 | 1998 | Primera edición | 1998 | 970-18-1599-8 | 179 | 178 | verificado en página legal |
| `LTMD-CN5-G2014` | 5º | Ciencias Naturales | 2014 | 2014 | Tercera edición revisada | 2014 | 978-607-514-722-2 | 162 | 161 | verificado en página legal; primera 2010, segunda 2011 |

## Totales técnicos

- Posiciones declaradas por visores: **763**.
- Activos JPEG reales: **759**.
- Diferencia: **4 posiciones terminales sintéticas**, una por objeto.

## Regla de citación

En el manuscrito histórico:

- usar **“generación 1993 / primera edición 1998”**, no “libro de 1993” cuando se describa el objeto bibliográfico;
- usar **“generación 1988”** mientras el año de edición permanezca no verificado;
- no convertir la señal de copyright 1972 en `edition_year=1972` sin evidencia bibliográfica explícita;
- separar siempre cambio de catálogo, cambio editorial, reforma curricular y año/edición del ejemplar.

## Fuente de datos

`data/book_inventory.csv` y auditorías de front matter versionadas en el repositorio.
