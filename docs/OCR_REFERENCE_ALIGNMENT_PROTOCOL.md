# Protocolo de alineación de referencia humana y OCR para CER/WER

## Propósito

Garantizar que la referencia humana (`reference`) y la hipótesis OCR (`hypothesis`) utilizadas para calcular CER/WER correspondan **exactamente a la misma región visual de la página**.

Esta precisión se incorpora antes de iniciar la transcripción humana. Corrige una ambigüedad del plan inicial, que establecía un objetivo aproximado de 120 palabras pero no definía cómo alinear un segmento humano parcial con la salida OCR de una página completa.

## Principio central

**Nunca calcular CER/WER entre una referencia humana parcial y OCR de página completa.**

Ambos textos deben provenir del mismo `reference_scope`:

- `full_page`; o
- `crop_block` definido por coordenadas normalizadas.

## Opción A — `full_page`

Usar preferentemente cuando la página contenga hasta aproximadamente **180 palabras legibles** o cuando su estructura textual sea suficientemente breve para que la transcripción total resulte razonable.

Reglas:

1. transcribir todo el texto lingüísticamente relevante de la página en orden natural de lectura;
2. ejecutar OCR sobre la página completa;
3. normalizar ambos textos con la misma rutina antes del cálculo;
4. no omitir zonas difíciles del texto sólo porque el OCR falle en ellas.

## Opción B — `crop_block`

Usar cuando la página sea extensa o cuando una región delimitada permita alcanzar el tamaño de referencia previsto sin exigir transcripción completa.

### Tamaño previsto

Seleccionar un bloque continuo de aproximadamente **120–150 palabras humanas** cuando el material disponible lo permita.

El objetivo original de 120 palabras se conserva como referencia de tamaño, pero deja de ser una longitud rígida. La prioridad es la **alineación espacial y funcional**, no completar exactamente 120 tokens.

### Coordenadas normalizadas

Registrar:

- `crop_x0`
- `crop_y0`
- `crop_x1`
- `crop_y1`

con valores en el intervalo `[0,1]`, relativos al ancho y alto completos de la imagen fuente.

Interpretación:

- `(0,0)` = esquina superior izquierda;
- `(1,1)` = esquina inferior derecha.

Debe cumplirse:

`0 <= x0 < x1 <= 1`

`0 <= y0 < y1 <= 1`

### Selección del bloque

1. respetar el orden natural de lectura;
2. preferir una región rectangular que contenga uno o varios bloques completos y contiguos;
3. evitar cortar líneas por la mitad cuando sea razonablemente posible;
4. no elegir una región por saber de antemano que Tesseract la lee mejor;
5. no excluir de forma oportunista errores tipográficos, columnas, títulos o elementos difíciles si forman parte natural del bloque seleccionado;
6. registrar cualquier excepción en `notes`.

## Orden temporal obligatorio

Para evitar sesgo de selección:

1. abrir la página fuente;
2. decidir `full_page` o `crop_block` **sin consultar CER/WER**;
3. si se usa recorte, registrar coordenadas;
4. realizar la transcripción humana;
5. revisar la transcripción humana;
6. ejecutar/obtener OCR del mismo scope;
7. sólo entonces calcular CER/WER.

Consultar la salida OCR durante la definición de la referencia puede ayudar a detectar problemas técnicos, pero no debe usarse para mover selectivamente la región hacia una zona más fácil.

## Referencia humana

La referencia se construye **leyendo directamente la imagen fuente**.

No debe generarse mediante:

- corrección superficial de la salida OCR;
- copia del OCR seguida de cambios puntuales;
- un modelo de IA presentado como referencia humana.

La segunda revisión debe comprobar al menos:

- caracteres;
- acentos;
- signos de puntuación incluidos bajo la regla de normalización;
- orden de lectura;
- palabras partidas por guion/salto de línea;
- inclusión/exclusión consistente de numeración, encabezados y pies.

## Política de elementos no textuales y tipográficos

Antes de transcribir se aplican reglas uniformes:

### Incluir

- títulos y subtítulos dentro del scope;
- cuerpo de texto;
- preguntas/consignas dentro del scope;
- etiquetas textuales que formen parte funcional del texto evaluado.

### Registrar y tratar consistentemente

- numeración de página;
- encabezados/pies repetitivos;
- texto incrustado dentro de diagramas;
- palabras partidas al final de línea;
- símbolos científicos.

Si un elemento no puede representarse razonablemente en texto lineal, documentarlo en `notes` y aplicar la misma regla a referencia e hipótesis antes de calcular la métrica.

## Normalización antes de CER/WER

La rutina base del proyecto:

1. normalización Unicode NFC;
2. CRLF/CR → LF;
3. todos los espacios/saltos de línea → un espacio;
4. trim inicial/final.

Por defecto se **preserva mayúscula/minúscula**. Una evaluación adicional con `casefold` puede reportarse como sensibilidad, pero no sustituye la métrica principal.

La puntuación se mantiene inicialmente. Si se decide reportar una segunda métrica sin puntuación, deberá etiquetarse explícitamente y nunca reemplazar silenciosamente la versión principal.

## Almacenamiento privado

El trabajo textual se mantiene en Google Drive en:

**LTMD — referencia humana OCR (privada)**

ID: `1hSrWI6OIqzPmuif2AjencToWSVLZPdtY0V5SRfe6WOg`

Pestañas:

- `CER_WER_Primary_48`
- `Stress_12`

Campos privados:

- `human_reference_text_private`
- `ocr_region_text_private`

Estos campos no se exportan al repositorio público.

## Salida pública

Después del cálculo se pueden publicar/versionar únicamente métricas y metadatos, por ejemplo:

- `sample_id`;
- generación;
- `page_id`;
- `reference_scope`;
- coordenadas del recorte;
- número de caracteres/palabras de referencia e hipótesis;
- distancias de edición;
- CER;
- WER;
- estado de validación;
- versión del pipeline OCR.

No es necesario publicar los textos para reproducir la estructura del análisis ni auditar su diseño.

## Muestra primaria vs. estrés

### Primaria

48 páginas preregistradas. Sus resultados estiman la exactitud general del pipeline en la muestra posicional.

### Estrés

12 páginas seleccionadas específicamente por requerir fallback y alta dificultad técnica. Sus resultados miden robustez en casos difíciles.

**No deben combinarse automáticamente en una única media**, porque el suplemento de estrés sobrerrepresenta deliberadamente casos difíciles.

## Decisión metodológica

El requisito de alineación por `full_page`/`crop_block` queda fijado **antes de cualquier transcripción humana** y se considera parte de la especificación del piloto 0.1.
