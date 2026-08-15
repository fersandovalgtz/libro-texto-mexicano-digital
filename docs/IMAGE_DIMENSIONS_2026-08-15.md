# Dimensiones de imagen de la muestra técnica — 15 de agosto de 2026

## Método

Se utilizaron solicitudes HTTP `Range` sobre las 40 páginas posicionales preregistradas. El script leyó como máximo los primeros 64 KiB de cada JPEG y extrajo ancho/alto desde el marcador SOF. No se persistieron cuerpos de imagen.

Resultado: **40/40 mediciones exitosas**, todas con respuesta HTTP 206.

## Dimensiones observadas

| Generación | Muestra | Dimensiones | Orientación |
|---|---:|---:|---|
| 1972 | 10 páginas | 670 × 993 px | vertical |
| 1988 | 10 páginas | 670 × 993 px | vertical |
| 1993 | 10 páginas | 797 × 1045 px | vertical |
| 2014 | 10 páginas | 969 × 1276 px | vertical |

Dentro de cada generación, las diez páginas de la muestra presentaron las mismas dimensiones.

## Interpretación técnica

La diferencia de resolución digital es verificable: 2014 contiene más píxeles por página que 1993 y que los cortes 1972/1988. Esto no permite inferir automáticamente precisión OCR; además intervienen tipografía, contraste, diseño, ilustración, compresión y calidad del escaneo.

La comparación de OCR deberá reportarse **por generación**, no únicamente para el corpus agregado.

## Decisión

Dado que el visor histórico entrega imágenes JPEG y no se ha identificado una capa textual asociada, el piloto continuará con OCR sobre una muestra controlada. Los textos OCR completos permanecerán como extracción intermedia de trabajo hasta resolver la política de redistribución. GitHub conservará inicialmente código y métricas derivadas, no transcripciones extensas.

Script: `scripts/probe_jpeg_dimensions.py`.
