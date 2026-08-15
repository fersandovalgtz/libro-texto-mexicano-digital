# Libro de Texto Mexicano Digital — instantánea metodológica

Fecha de corte: **15 de agosto de 2026**.

## Alcance del piloto

El piloto trabaja con cuatro volúmenes seleccionados de Ciencias Naturales de quinto grado asociados a generaciones del catálogo histórico de 1972, 1988, 1993 y 2014. El inventario fuente contiene 759 imágenes reales de página. El pipeline estructural ha producido 9,594 fragmentos congelados con identificadores y hashes reproducibles.

El piloto es una comparación histórico-digital intensiva de cuatro objetos documentales, no una muestra probabilística de todos los libros de texto mexicanos.

## Pipeline consolidado

`fuente oficial → inventario/procedencia → OCR temporal → PAGESTRUCT → FRAGSEG → metadatos/hashes → clasificación A / SEMB → comparación de métodos → análisis histórico condicionado a validación`

Los textos OCR completos y embeddings no se publican como datos derivados del repositorio. Cuando una etapa necesita texto, se reconstruye de manera efímera desde la fuente y se verifica contra el SHA-256 persistido.

## PAGESTRUCT y FRAGSEG

La estructura de página está congelada como PAGESTRUCT 0.2 y la capa de fragmentos como FRAGSEG 0.2. La auditoría posterior reveló que `heading_candidate` era una denominación excesivamente fuerte: la regla original asignaba esa categoría de forma residual a unidades breves sin utilizar evidencia tipográfica.

Dos auditorías independientes sostienen esta corrección metodológica:

1. la prevalencia de `heading_candidate` crece fuertemente entre generaciones y aparece en casi todas las páginas, por lo que no puede interpretarse directamente como historia de encabezados;
2. una auditoría de layout de 160 fragmentos no muestra una separación tipográfica consistente entre `heading_candidate` y `expository_candidate`.

Por ello se creó `FRAGTYPE_0.3_SHADOW`, que no altera límites, IDs ni hashes y renombra la categoría residual como `short_residual_candidate`. Si la elegibilidad semántica se separa de esa etiqueta, el universo potencial de fragmentos de ≥4 tokens aumenta de 5,037 a 7,429 (+2,392). Esa ampliación no entra todavía al análisis primario: dispone de una muestra suplementaria ciega de 160 casos para futura validación humana.

## Clasificación semántica SEMB 0.2

SEMB 0.2 usa `intfloat/multilingual-e5-small`, revisión fijada, anchors en español y reglas preregistradas de gate, multilabel e incertidumbre. La capa se ejecutó sobre el corpus congelado y se comparó con un clasificador de reglas independiente.

El diagnóstico posterior demostró una cobertura insuficiente: 99.49% de los fragmentos quedaron globalmente inciertos. En los 5,037 fragmentos elegibles del diseño SEMB 0.2, el gate/buffer de acción bloquea 89.16%, el margen de posición bloquea 74.83% y sólo 49 fragmentos cumplen simultáneamente los criterios de certeza de acción y posición.

La longitud no explica el fenómeno: la incertidumbre permanece cercana a 99% en intervalos sustantivos de longitud.

## Prueba sintética independiente de SEMB 0.2

Se creó una batería de 105 casos educativos en español que no contiene texto del corpus histórico: 48 casos claros de acciones, 30 negativos de estrés y 27 casos de posiciones. Como SEMB 0.2 estaba congelado antes de esta batería, su evaluación sirve como diagnóstico externo sintético del modelo antiguo.

El gate SEMB 0.2 alcanza balanced accuracy 0.526 (sensibilidad 0.597; especificidad 0.455). En negativos de estrés produce 53.3% de falsos positivos y, en positivos, 94.4% no supera el buffer de certeza. Los anchors de acciones obtienen 75% top-1 en casos claros; los de posiciones, 63%.

Estos resultados no sustituyen referencia humana, pero corroboran que el problema de SEMB 0.2 no deriva únicamente de la composición histórica del corpus.

## SEMB 0.3 — diseño previo a humanos

Se congeló una muestra ciega de 480 fragmentos del universo elegible SEMB 0.2: 120 por generación, con 320 casos de desarrollo y 160 de validación bloqueada. Los IDs visibles al anotador son opacos; la plantilla no expone generación, rol development/locked, tipo de fragmento, página, hash ni resultados automáticos.

Un subconjunto de 120 casos se reserva para doble codificación interanotador. Se fijaron criterios de fiabilidad humana, desempeño semántico, cobertura e incertidumbre antes de observar anotaciones humanas.

La muestra cubre 312 páginas distintas; los 160 casos bloqueados cubren 138 páginas. Su mediana de longitud es 16 tokens frente a 15 en el universo elegible. Existen estratos funcionales raros con pocos casos bloqueados, por lo que no se preregistran inferencias finas por esos estratos.

## Stage gates

- **G0:** infraestructura y evidencia prehumana.
- **G1:** fiabilidad de la doble codificación humana.
- **G2:** consenso/adjudicación de referencia de desarrollo.
- **G3:** desarrollo computacional sólo con 320 humanos de desarrollo + material sintético permitido.
- **G4:** bloqueo criptográfico del modelo, configuración, código y criterios.
- **G5:** una sola apertura de los 160 casos de validación.
- **G6:** producción sólo si se superan criterios preregistrados.
- **G7:** reconstrucción del análisis histórico después de validación.

El evaluador G5 exige no sólo accuracy/F1, sino ≥70% de salidas ciertas, brecha de incertidumbre entre generaciones ≤20 puntos porcentuales y ausencia de truncamiento silencioso.

## Desarrollo sintético provisional para SEMB 0.3

Después de usar la batería para diagnosticar el modelo congelado SEMB 0.2, esos mismos casos pueden utilizarse como **desarrollo sintético de candidatos SEMB 0.3**, pero dejan de constituir una prueba independiente del nuevo sistema. Todo candidato derivado de ellos se marca `PROVISIONAL_SYNTHETIC_ONLY` y deberá volver a calibrarse/compararse en los 320 casos humanos de desarrollo.

Las diferencias históricas 1972–2014, las salidas de Rule A, las salidas históricas de SEMB 0.2 y los 160 humanos bloqueados están prohibidos como función de ajuste.

## Plan histórico posterior a validación

Los contrastes preregistrados son 1972→1988, 1988→1993, 1993→2014 y 1972→2014. Se publicarán todas las categorías válidas, denominadores completos, cobertura, incertidumbre, resultados nulos y sensibilidad entre métodos. La dependencia entre fragmentos de una misma página se tratará mediante remuestreo por página cuando se cuantifique estabilidad.

Debido al diseño documental del piloto, los intervalos describirán estabilidad dentro de los cuatro volúmenes seleccionados, no incertidumbre de muestreo sobre todos los libros de texto mexicanos.

## Estado epistemológico al corte

La infraestructura, procedencia, reproducibilidad, diagnósticos de SEMB 0.2 y diseño de validación SEMB 0.3 están sustancialmente maduros. Los hallazgos históricos semánticos existentes permanecen **exploratorios**. El principal bloqueo epistemológico es obtener una referencia humana fiable que permita demostrar que las categorías automáticas corresponden a juicios reproducibles de investigadores y no sólo a consistencia interna de algoritmos.
