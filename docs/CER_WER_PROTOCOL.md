# Protocolo de validación CER/WER — piloto 0.1

## Objetivo

Cuantificar el error real del OCR mediante comparación contra una referencia humana, sin utilizar la confianza interna de Tesseract como sustituto de precisión.

## Muestra preregistrada

Se conserva la selección definida en `docs/EXTRACTION_SPEC.md`: **12 páginas por libro**, 48 en total.

Por cada generación:

- 1 página legal;
- 1 página de índice;
- 10 páginas posicionales fijadas antes de observar el OCR: 2 del primer cuarto, 3 del segundo, 3 del tercero y 2 del cuarto final.

Las 48 páginas están enumeradas en `data/derived/ocr_human_reference_template.csv` una vez generado dicho archivo. No se sustituirá una página por su dificultad OCR. Sólo podrá sustituirse si carece de texto suficiente para producir una referencia y la sustitución deberá ser la página textual más cercana, con registro explícito en `notes` y `docs/DECISIONS.md`.

## Unidad de referencia humana

En cada página se transcribirá manualmente una **muestra textual continua y verificable**, suficiente para calcular error de caracteres y palabras. No es necesario transcribir la página completa si el bloque elegido es representativo y tiene longitud adecuada.

Regla operativa inicial:

- objetivo de **80–150 palabras** cuando la página lo permita;
- seleccionar un bloque continuo, no palabras aisladas;
- conservar ortografía, acentos, mayúsculas y puntuación visibles en la fuente;
- no “corregir” errores tipográficos del libro;
- omitir únicamente elementos puramente decorativos que no formen parte del bloque seleccionado;
- registrar cualquier duda de lectura.

Para páginas con menos de 80 palabras útiles se transcribirá todo el texto legible disponible y se marcará `short_reference` en las notas.

## Doble control humano

La referencia deberá tener dos estados:

1. `transcribed` — primera transcripción manual;
2. `verified` — segunda revisión contra la imagen fuente.

CER/WER destinado a decisiones científicas se calculará sólo sobre referencias `verified`.

## Archivo privado de trabajo

Las transcripciones humanas y el OCR íntegro permanecen fuera de GitHub mientras esté vigente el semáforo jurídico amarillo.

El evaluador `scripts/evaluate_ocr_cer_wer.py` espera un CSV privado con, al menos:

- `validation_id`;
- `book_id`;
- `catalog_generation`;
- `page_id`;
- `reference_text`;
- `hypothesis_text`.

El script genera únicamente métricas y no copia los textos al archivo de salida.

## Normalización para el cálculo

Versión basal:

- Unicode NFC;
- normalización de espacios y saltos de línea a un espacio;
- preservación de mayúsculas/minúsculas por defecto;
- preservación de tildes y puntuación;
- tokenización WER por espacios.

Podrá reportarse adicionalmente una variante `casefold` para diagnóstico, pero la métrica principal conservará el caso original.

## Métricas

### CER

`CER = distancia de edición de caracteres / caracteres de referencia`

### WER

`WER = distancia de edición de palabras / palabras de referencia`

Se reportarán ambas por página, generación y corpus.

## Criterios internos preregistrados

Los umbrales de CER definidos en `docs/EXTRACTION_SPEC.md` se mantienen:

- CER ≤ 2 %: excelente para análisis léxico;
- >2 % y ≤5 %: utilizable con normalización y cautela;
- >5 % y ≤10 %: requiere corrección o uso analítico limitado;
- >10 %: no usar para análisis textual automático sin intervención adicional.

Estos son criterios internos del proyecto, no estándares universales.

## Regla de decisión

El pipeline OCR se considerará técnicamente suficiente para escalar análisis textual cuando:

1. no existan fallos sistemáticos de obtención/procesamiento;
2. al menos 90 % de las páginas de contenido produzcan texto procesable;
3. la distribución CER/WER sea compatible con el tipo de análisis previsto;
4. cualquier generación claramente más difícil tenga una ruta de corrección documentada.

La evaluación por generación es obligatoria: un buen promedio general no podrá ocultar un desempeño deficiente en un corte histórico específico.
