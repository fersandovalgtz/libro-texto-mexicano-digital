# LTMD-U2 — resolución estructural de paginación 0.1

## Propósito

Esta capa registra el número estructural de páginas de los 39 objetos fuente de LTMD-U2 correspondientes al catálogo CONALITEG de primaria observado para el ciclo 2026–2027. Se mantiene separada de la resolución del lector y de los activos PDF, así como de cualquier decisión posterior de admisión al corpus, OCR, verificación textual, licencia o validación semántica.

Las guardas son explícitas:

- `reader_shell_resolved != asset_resolved`
- `asset_resolved != page_count_observed`
- `page_count_observed != source_admitted`
- `source_admitted != ocr_available`
- `ocr_available != text_verified`
- `computational_candidate != semantic_ready`
- `publicly_accessible != openly_licensed`

## Resultado observado

El 2 de septiembre de 2026 se resolvió `page_count_state=observed` para **39/39** objetos. La suma de los contadores estructurales `/Pages /Count` es **10,392 páginas**; el mínimo observado es 91 y el máximo 371.

La evidencia versionada se encuentra en:

- `data/catalog/ltmd_u2_page_count_resolution_2026_09_02.csv`
- `data/catalog/ltmd_u2_page_count_resolution_2026_09_02.manifest.json`
- `schemas/ltmd_u2_page_count_resolution.schema.json`

El SHA-256 de la tabla CSV observada es `f08732c0e6cf29654843a2c09b0dac3d2288d3701d7faa98f62c014b1d94a557`.

## Método

Los PDF fuente no se descargan ni se persisten. El observador `scripts/observe_u2_page_count_resolution.py` realiza solicitudes HTTP Range acotadas sobre el host institucional y sigue la estructura PDF necesaria para llegar al contador raíz de páginas:

1. confirma firma PDF, `application/pdf`, HTTP 206 y longitud remota mediante un rango de un byte;
2. lee una cola acotada del archivo y localiza el último `startxref`;
3. lee la tabla xref clásica y, si existe, su cadena `/Prev`;
4. localiza la referencia `/Root` del trailer;
5. resuelve el catálogo y su referencia `/Pages`;
6. resuelve el nodo raíz `/Pages` y lee su `/Count`;
7. registra solamente metadatos estructurales y de transporte.

El presupuesto preregistrado para la observación fue de 4 MiB por objeto. En la corrida completa se transfirieron **18,950,119 bytes** en total; el máximo real para un objeto fue 2,461,786 bytes. No se persistieron bytes de los PDF fuente.

## Desarrollo y falsación de métodos alternativos

La ruta final se adoptó después de pruebas acotadas que descartaron aproximaciones más costosas o inaplicables para estos archivos:

- `len(reader.pages)` con pypdf agotó 16 MiB y luego 8 MiB sobre P0CMA antes de obtener el conteo;
- acceder al catálogo mediante pypdf siguió requiriendo suficiente resolución xref para agotar el presupuesto de 8 MiB;
- P0CMA no está linearizado, por lo que `/Linearized /N` no estaba disponible en los primeros 64 KiB;
- `startxref` sí apuntó a una tabla xref clásica; una ventana inicial de 512 KiB resultó insuficiente, mientras que 3 MiB cubrió la tabla completa y permitió llegar a `/Pages /Count`.

Estos resultados negativos se conservan como procedencia experimental; no forman parte de la superficie productiva de esta capa.

## Validación cruzada previa al escalamiento

Antes de ejecutar los 39 objetos se comprobó el método en cuatro escalas de tamaño:

| Objeto | Tamaño remoto aproximado | `/Pages /Count` | Bytes de red |
| --- | ---: | ---: | ---: |
| P5LPM | 4.9 MB | 99 | 229,554 |
| P4PEA | 33.6 MB | 363 | 434,240 |
| P3MLA | 100.0 MB | 259 | 484,860 |
| P0CMA | 281.1 MB | 191 | 2,461,786 |

Los cuatro casos resolvieron mediante xref clásico con cinco solicitudes Range cada uno.

## Procedencia computacional

La corrida exhaustiva de descubrimiento fue GitHub Actions run `33643015731`, sobre el commit experimental `9138e963d0f1f6b3b30d3e985757bafb3a1a77ec`. El artifact text-free fue `9851660198`, con SHA-256 `9a534320c9b77ed2c3a59988bfd7ee04369784772d76a816281337df2ef3d485`.

La tabla resultante se vuelve a validar en el repositorio contra:

- las 39 identidades canónicas de `ltmd_u2_source_objects_2026_2027.csv`;
- los 39 activos `resolved_pdf` de `ltmd_u2_asset_resolution_2026_09_02.csv`;
- identidad de `viewer_key` y `asset_url`;
- longitud remota observada previamente;
- cardinalidad 39→39;
- suma estructural fijada en 10,392 páginas;
- presupuesto de red por objeto;
- referencias `/Root` y `/Pages` válidas;
- ausencia de errores en los 39 registros.

## Límites epistemológicos y jurídicos

Un `/Pages /Count` observado establece un conteo estructural declarado por el árbol de páginas del PDF servido en ese momento. No demuestra por sí mismo calidad visual, completitud editorial, correspondencia con una edición impresa, OCR utilizable, texto correcto, licencia abierta ni aptitud semántica. Tampoco admite automáticamente el objeto al corpus analítico.

Por ello, los 39 registros mantienen:

- `source_admission_state=not_assessed`
- `text_verification_state=not_assessed`

La accesibilidad pública del archivo no se interpreta como permiso de redistribución. Esta capa publica únicamente evidencia estructural y de procedencia; no redistribuye los PDF fuente.
