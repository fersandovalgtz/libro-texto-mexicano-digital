# Validación técnica de activos de página — 15 de agosto de 2026

## Propósito

Comprobar que la regla de construcción de URLs derivada del código público del visor corresponde a activos reales, sin descargar los cuerpos de las imágenes durante esta prueba.

## Método

Se generó un manifiesto de **763 páginas del visor** mediante `scripts/build_page_manifest.py`.

De acuerdo con `docs/EXTRACTION_SPEC.md`, se preregistraron diez candidatos posicionales por libro distribuidos 2/3/3/2 entre los cuatro cuartos del volumen. Las páginas `legal` y `toc` se incorporarán posteriormente tras identificar el front matter.

`scripts/verify_manifest_sample.py` realizó solicitudes HTTP `HEAD` concurrentes sobre esas 40 URLs. No se descargó el cuerpo de las imágenes.

## Resultado

- URLs probadas: **40**
- Respuestas HTTP 200: **40/40**
- `Content-Type: image/jpeg`: **40/40**
- Generaciones representadas: **4/4**

El patrón técnico queda validado para la muestra preregistrada.

## Tamaño anunciado de los JPEG en la muestra

| Generación | n | mínimo | mediana | máximo |
|---|---:|---:|---:|---:|
| 1972 | 10 | 48,265 B | 62,636 B | 77,335 B |
| 1988 | 10 | 39,815 B | 57,135 B | 77,400 B |
| 1993 | 10 | 66,681 B | 84,374 B | 99,772 B |
| 2014 | 10 | 284,236 B | 532,280 B | 1,383,537 B |

La diferencia de tamaño de archivo, especialmente en 2014, **no se interpreta por sí sola como diferencia de calidad OCR**. Puede reflejar dimensiones, compresión, complejidad visual, color u otros factores. La resolución efectiva y el error textual se medirán en la siguiente fase.

## Conclusión técnica

Se cumplen ya dos condiciones fundamentales del piloto:

1. los cuatro libros pueden enumerarse reproduciblemente;
2. las rutas de imágenes construidas a partir del código del visor corresponden a activos JPEG reales en una muestra estratificada de 40/40 casos.

El siguiente paso técnico es obtener una **muestra de trabajo controlada**, identificar página legal e índice, medir dimensiones/resolución y ejecutar la primera prueba de extracción/OCR sin versionar imágenes fuente en GitHub.
