# Arquitectura del visor histórico de CONALITEG — auditoría 2026-08-15

## Resultado

La auditoría reproducible del piloto 0.1 confirmó que los cuatro libros seleccionados utilizan la misma arquitectura pública de visor.

Cadena observada:

`HTML del libro → x.js → claves.json → magazine.js → /c/{ag_clave}/{archivo}.jpg`

No se encontró un PDF enlazado directamente desde el HTML del visor. La unidad técnica de acceso observada es una imagen JPEG por página.

## Identificación del libro

`x.js` obtiene la clave a partir del nombre del archivo HTML:

`H1972P5CI084.htm → H1972P5CI084`

La misma regla produce las cuatro claves del piloto:

| Generación del catálogo | Clave del visor | Páginas del visor |
|---|---|---:|
| 1972 | `H1972P5CI084` | 259 |
| 1988 | `H1988P5CI123` | 163 |
| 1993 | `H1993P5CI200` | 179 |
| 2014 | `H2014P5CNA` | 162 |

**Total del piloto: 763 páginas del visor.**

Los conteos proceden de `claves.json`, donde cada clave contiene `ag_pages`.

## Construcción de la imagen de página

Las funciones `loadPage`, `loadSmallPage` y `loadLargePage` están definidas en `magazine.js` y utilizan la misma ruta:

`./c/ + ag_clave + / + ag_page + .jpg`

La función `pad()` rellena el índice numérico a tres dígitos.

Regla observada:

- página 1 del visor → índice de imagen `0` → `000.jpg`;
- páginas 2..N del visor → índice igual al número de página → `002.jpg`, `003.jpg`, ...;
- la lógica actual del visor no solicita `001.jpg`.

Ejemplo derivado para la generación 1972:

`https://historico.conaliteg.gob.mx/c/H1972P5CI084/026.jpg`

Este patrón se conserva como **metadato de procedencia**. La enumeración de URLs no implica autorización para redistribuir las imágenes.

## Implicación para el pipeline

El pipeline del piloto puede separar claramente:

1. **manifiesto público**: clave, número de páginas, URL técnica por página;
2. **copia de trabajo**: imágenes necesarias para extracción, mantenidas fuera de GitHub mientras no se aclare su redistribución;
3. **extracción intermedia**: OCR/texto por página, inicialmente local;
4. **datos derivados**: clasificación, conteos y variables analíticas versionables.

La arquitectura es común a los cuatro cortes, por lo que no se requieren cuatro ingestas diferentes: una sola rutina parametrizada por `viewer_key` y `page_count` cubre el corpus piloto.

## Reproducibilidad

Scripts relevantes:

- `scripts/inspect_viewer.py`
- `scripts/probe_viewer_architecture.py`
- `scripts/trace_viewer_manifest.py`
- `scripts/resolve_viewer_manifest.py`
- `scripts/build_page_manifest.py`
- `scripts/verify_manifest_sample.py`

Workflows:

- `.github/workflows/audit-viewers.yml`
- `.github/workflows/resolve-manifest.yml`
- `.github/workflows/build-page-manifest.yml`

## Precaución metodológica

`viewer_page`, `source_image_index` y `printed_page_number` son variables distintas. No se asumirá que el número mostrado por el visor coincide con la foliación impresa. Esa correspondencia se establecerá durante la clasificación de páginas y la revisión de front matter.
