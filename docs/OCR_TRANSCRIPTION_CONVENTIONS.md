# Convenciones de transcripción y normalización OCR — piloto 0.1

**Fecha de congelación:** 15 de agosto de 2026  
**Momento metodológico:** antes de calcular el primer CER/WER contra referencia humana.

## Propósito

Este documento fija cómo se construirá la referencia humana y cómo se normalizarán referencia e hipótesis OCR antes de calcular tasas de error. Su función es impedir que las reglas se modifiquen retrospectivamente después de observar qué páginas o generaciones producen peores resultados.

El objetivo del OCR en *Libro de Texto Mexicano Digital* no es reproducir tipográficamente una página, sino obtener texto suficientemente fiel para análisis histórico-computacional. Por ello se distinguen **fidelidad ortográfica** y **fidelidad léxica**.

## 1. Región de evaluación

Referencia humana y OCR deben corresponder exactamente a la misma región de imagen.

Cada registro usa:

- `reference_scope = full_page` cuando se evalúa toda la página;
- `reference_scope = crop_block` cuando se evalúa un rectángulo continuo;
- `crop_x0`, `crop_y0`, `crop_x1`, `crop_y1` como coordenadas normalizadas en `[0,1]` cuando existe recorte.

La región se fija **antes** de leer el resultado OCR correspondiente.

### 1.1 Elementos fuera de la región

Se excluyen mediante el recorte cuando no son parte del contenido textual que interesa analizar:

- folios aislados de página;
- márgenes vacíos;
- ilustraciones sin texto;
- ornamentos puramente gráficos.

No se elimina retrospectivamente una zona sólo porque el OCR la reconozca mal.

### 1.2 Páginas de texto escaso

El objetivo de 120–150 palabras es orientativo, no obligatorio. Si una página contiene menos texto relevante, se evalúa todo el bloque textual disponible y se registra su longitud real. No se sustituye la página preregistrada.

## 2. Convención de referencia humana

La referencia se transcribe **leyendo la imagen fuente**, no corrigiendo superficialmente la salida OCR.

Se conserva:

- ortografía histórica visible;
- acentuación;
- mayúsculas/minúsculas;
- puntuación con función lingüística;
- numeración de listas y números de página que formen parte de un índice o tabla;
- abreviaturas e iniciales;
- nombres propios tal como aparecen.

No se moderniza ortografía, no se corrigen supuestas erratas del impreso y no se completan palabras por conocimiento externo.

### 2.1 Saltos de línea

Los saltos de línea de maquetación no se consideran contenido. La transcripción sigue el orden natural de lectura y usa espacios normales entre unidades.

Cuando una palabra está partida exclusivamente por final de línea, se reconstruye como una sola palabra. Un guion lingüístico real dentro de una palabra o nombre se conserva en la referencia ortográfica.

### 2.2 Líderes de puntos

Las secuencias de puntos usadas para alinear títulos y números de página en índices son **maquetación**, no puntuación lingüística. No es necesario reproducir el número exacto de puntos en la referencia humana. El evaluador elimina secuencias de líderes antes de calcular ambas familias de métricas.

### 2.3 Texto dudoso

Si un carácter o palabra no puede resolverse razonablemente por inspección visual:

1. se marca en notas;
2. pasa obligatoriamente a segunda revisión;
3. si continúa irresoluble y afecta materialmente la comparación, el registro puede quedar `excluded_justified`;
4. nunca se adivina a partir del OCR que se pretende evaluar.

## 3. Segunda revisión

Toda referencia humana debe pasar una segunda lectura antes de que su CER/WER sea considerado definitivo.

La segunda revisión comprueba:

- región correcta;
- orden de lectura;
- signos diacríticos;
- nombres propios y cifras;
- separación/unión de palabras;
- puntuación significativa;
- correspondencia exacta entre región de referencia y región OCR.

Un resultado previo a esta revisión se etiqueta **provisional**.

## 4. Normalización ortográfica

La métrica ortográfica evalúa fidelidad de caracteres y palabras conservando diferencias lingüísticamente visibles.

Antes de comparar:

1. normalización Unicode NFC;
2. normalización de finales de línea;
3. recomposición de palabras partidas por guion de final de línea cuando el salto es inequívocamente de maquetación;
4. eliminación de líderes de puntos (`...`, `. . . .` y equivalentes repetidos);
5. normalización de espacios múltiples a un espacio;
6. normalización de variantes tipográficas de comillas y rayas a una representación canónica.

Se conservan:

- mayúsculas/minúsculas;
- acentos;
- puntuación lingüística;
- números;
- guiones internos lingüísticos.

Resultados:

- `cer_orthographic`;
- `wer_orthographic`.

## 5. Normalización léxica — métrica principal para viabilidad analítica

La métrica léxica parte del texto ortográficamente normalizado y aplica además:

1. `casefold` Unicode;
2. eliminación de puntuación y símbolos como separadores;
3. conservación de letras, marcas diacríticas y números;
4. normalización final de espacios.

Los acentos **no** se eliminan: distinguir `México` de una salida `Mexico` sigue contando como error porque la pérdida de diacríticos afecta calidad textual.

Resultados:

- `cer_lexical`;
- `wer_lexical`.

**Para decidir si el OCR es apto para análisis textual, `CER/WER` sin calificativo en reportes narrativos se referirá a la versión léxica.** La versión ortográfica se reportará como control secundario.

## 6. Tratamiento de folios y encabezados

Un folio aislado que sólo identifica la página se excluye mediante región cuando sea posible. No se elimina por posprocesamiento después de ver el OCR.

En cambio, números que pertenecen al contenido —por ejemplo, numeración de capítulos o páginas de destino en un índice— permanecen en referencia y evaluación.

Los encabezados corrientes se incluyen o excluyen según la región fijada; la decisión se toma antes de evaluar el resultado OCR.

## 7. Orden de lectura

En páginas con una sola columna se sigue de arriba abajo.

En listas e índices se sigue el orden visual de entradas. El título de la página se incluye si cae dentro de la región fijada.

En futuras páginas multicolumna o con cajas laterales, la región se subdividirá o se documentará un orden explícito antes de transcribir. No se concatenarán bloques ambiguos sin registrar la decisión.

## 8. Dos familias de resultados y regla de interpretación

Se calcularán ambas familias para cada registro validado:

| familia | sensibilidad | uso |
|---|---|---|
| ortográfica | mayúsculas, diacríticos, puntuación lingüística y caracteres | control de fidelidad editorial |
| léxica | palabras/letras/números después de neutralizar maquetación y puntuación | **criterio principal de viabilidad para análisis histórico-computacional** |

Los resultados de la muestra primaria de 48 páginas y del suplemento de estrés de 12 páginas se reportan por separado.

## 9. Umbrales exploratorios

Los siguientes cortes son criterios internos iniciales para `CER lexical`, no estándares universales:

- `≤ 0.02`: excelente;
- `> 0.02–0.05`: utilizable con cautela;
- `> 0.05–0.10`: requiere corrección/preprocesamiento o uso limitado;
- `> 0.10`: no usar para análisis textual automático sin intervención adicional.

WER se reportará conjuntamente y no se reducirá a un único umbral hasta observar la muestra completa, para no fijar retrospectivamente un criterio a partir de tres páginas.

## 10. Primer lote congelado — 1972

Antes de producir métricas se fijaron las siguientes regiones de trabajo sobre imágenes de 670×993 px:

| muestra | página visor | región px | región normalizada aprox. | razón |
|---|---:|---|---|---|
| `LTMD-CER-1972-LEGAL` | 4 | `(100,139)-(576,395)` | `(0.149254,0.139980)-(0.859701,0.397784)` | bloque continuo de créditos ≈120 palabras; evita extender la referencia a toda la página legal |
| `LTMD-CER-1972-TOC` | 7 | `(35,20)-(635,950)` | `(0.052239,0.020141)-(0.947761,0.956697)` | título + las 23 entradas del índice; excluye márgenes vacíos |
| `LTMD-CER-1972-Q1_1` | 26 | `(28,22)-(635,135)` | `(0.041791,0.022155)-(0.947761,0.135952)` | todo el bloque textual de la página; excluye ilustraciones y folio 26 |

Estas regiones no se modificarán por observar un resultado OCR desfavorable. Cualquier corrección por error material de coordenadas se documentará como desviación del protocolo.

## 11. Gobernanza

La transcripción humana y la hipótesis OCR de cada región son **material privado de trabajo**. Se almacenan en Google Drive y no se versionan en GitHub. El repositorio público conserva únicamente:

- IDs y procedencia;
- coordenadas de región;
- longitud de referencia/hipótesis;
- conteos de ediciones;
- CER/WER y métricas derivadas;
- código y documentación metodológica.
