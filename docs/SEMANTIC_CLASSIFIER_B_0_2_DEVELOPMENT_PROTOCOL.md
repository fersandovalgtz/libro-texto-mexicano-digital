# SEMB 0.2 — protocolo de desarrollo sintético y validación bloqueada

Fecha: 2026-08-15

## Antecedente

SEMB 0.1 falló antes del corpus. El diagnóstico sintético demostró colapso geométrico: prototipos de acciones con similitud media ≈0.945 y posiciones ≈0.959; top-1 de acciones 3/16. Cambiar entre promedio, nearest-prototype y centrado no resolvió la discriminación. SEMB 0.1 queda cerrado como intento fallido.

## Nueva arquitectura candidata

Modelo candidato: `intfloat/multilingual-e5-small`.

Revisión pinneada de pesos/modelo: `fd1525a9fd15316a2d503bf26ab031a61d056e98`.

La decisión de probar E5 se toma **antes de consultar el corpus LTMD**. La evaluación continuará exclusivamente con frases sintéticas.

## Separación desarrollo / validación

Las frases sintéticas utilizadas en SEMB 0.1 dejan de ser held-out y pasan a constituir el **conjunto de desarrollo**. Pueden utilizarse para comparar funciones de score, diseñar prototipos cortos y fijar umbrales.

Antes de implementar SEMB 0.2 se bloquea aquí un segundo conjunto, **VALIDATION_B02**, que no podrá usarse para cambiar prototipos, modelo o thresholds después de observar sus resultados. Si B 0.2 falla los criterios de aceptación en VALIDATION_B02, la versión se considera fallida y cualquier nueva arquitectura será SEMB 0.3 con un nuevo protocolo; no se iterará sobre esta validación.

## VALIDATION_B02 — acciones

- `observe`: “Mira cuidadosamente los cambios que ocurren y anota lo que puedas notar.”
- `describe`: “Indica cómo es cada muestra y cuáles son sus características visibles.”
- `recall`: “Sin revisar tus apuntes, escribe dos conceptos que aprendiste en la clase pasada.”
- `explain`: “Señala la causa del cambio y explica cómo se produce.”
- `compare`: “Establece una semejanza y una diferencia entre las dos situaciones.”
- `classify`: “Ordena los ejemplos en grupos usando una propiedad como criterio.”
- `measure`: “Usa la balanza para obtener la masa y registra el valor.”
- `experiment`: “Cambia la cantidad de agua, mantén lo demás igual y observa el resultado.”
- `investigate`: “Averigua en distintas fuentes qué información permite responder la pregunta.”
- `predict`: “Antes de iniciar la actividad, escribe qué esperas que suceda.”
- `infer`: “A partir de los datos de la tabla, deduce qué conclusión puede sostenerse.”
- `discuss`: “Conversa con tu equipo, contrasta sus argumentos y lleguen a una postura.”
- `solve`: “Determina cómo resolver la situación planteada y encuentra una respuesta.”
- `create`: “Construye un modelo que represente el fenómeno estudiado.”
- `decide`: “Escoge la alternativa más conveniente después de valorar sus consecuencias.”
- `act_on_environment`: “Organiza con tu familia una acción concreta para reducir un riesgo de salud.”

## VALIDATION_B02 — posiciones

- `receiver`: “El estudiante solamente lee información ya explicada y no recibe una tarea adicional.”
- `instruction_follower`: “El estudiante ejecuta exactamente una secuencia de pasos ya determinada.”
- `observer`: “El alumno obtiene datos al mirar de manera sistemática lo que sucede.”
- `experimenter`: “El estudiante modifica una condición de una prueba y obtiene evidencia.”
- `investigator`: “El alumno reúne información de diversas fuentes para responder una cuestión.”
- `reasoner`: “El estudiante usa datos y relaciones para justificar una conclusión.”
- `collaborator`: “El alumno necesita intercambiar ideas y construir la respuesta con otras personas.”
- `decision_maker`: “El estudiante evalúa opciones y elige una alternativa de manera fundamentada.”
- `community_agent`: “El alumno lleva el aprendizaje a una acción concreta en su comunidad.”

## VALIDATION_B02 — negativos de acción

Deben quedar sin acción B o como `uncertain/no-action`:

1. “El agua puede encontrarse en estado sólido, líquido o gaseoso.”
2. “Los mamíferos presentan características que permiten distinguirlos de otros animales.”
3. “La temperatura puede medirse con un termómetro.”
4. “Un experimento científico permite estudiar relaciones entre fenómenos.”
5. “Las diferencias entre materiales dependen de sus propiedades.”
6. “La comunidad está formada por personas que comparten un espacio.”
7. “Un cartel puede utilizarse para comunicar información.”
8. “La observación es una herramienta importante en el estudio de la naturaleza.”

## Prototipos 0.2

Para reducir el componente común de “consigna escolar”, los prototipos de acciones serán **anclas semánticas cortas**, tres por categoría, sin frases genéricas sobre alumno/tarea. Ejemplo conceptual: `observe → observación visual detallada / examinar propiedades / mirar cambios con atención`.

Las anclas se fijan en el código antes de ejecutar VALIDATION_B02.

## Scoring a desarrollar sólo con el conjunto de desarrollo

Se compararán como máximo estas funciones:

1. promedio de anclas por categoría;
2. máxima similitud contra las tres anclas;
3. score contrastivo: score de categoría menos media de scores de las demás categorías;
4. máxima similitud + compuerta semántica acción/no-acción.

La compuerta acción/no-acción tendrá anclas positivas sintéticas (“instrucción que pide realizar una operación”, etc.) y negativas (“texto expositivo sin consigna”, etc.).

El conjunto de desarrollo puede utilizarse para elegir una de esas cuatro funciones y thresholds dentro de una rejilla preregistrada:

- margen actionness: `0.00, 0.02, 0.04, 0.06`;
- margen top1-top2: `0.00, 0.01, 0.02, 0.04`;
- banda multilabel: `0.01, 0.02, 0.04, 0.06`;
- máximo 3 acciones, máximo 2 posiciones.

No se optimizará con etiquetas RULEA ni con texto LTMD.

## Criterios de aceptación en VALIDATION_B02

Una vez elegida la configuración usando sólo desarrollo, se ejecutará VALIDATION_B02 **una sola vez**.

Debe cumplir simultáneamente:

### Acciones
- top-1 esperado ≥12/16 (75 %);
- esperado en top-3 ≥15/16;
- ningún caso con rank esperado >4;
- al menos 7/8 negativos de acción sin etiqueta o marcados `uncertain/no-action`.

### Posiciones
- top-1 esperado ≥7/9;
- esperado en top-3 =9/9;
- ningún rank esperado >3.

Si no se cumplen estos umbrales, SEMB 0.2 se declara FAILED PRE-CORPUS. No se relajan después de ver VALIDATION_B02.

## Prohibiciones

Durante desarrollo y validación 0.2 queda prohibido leer:

- texto de fragmentos LTMD;
- `fragment_labels_A.csv`;
- regex/patrones de RULEA para calibrar B;
- distribuciones históricas por generación.

Sólo después de aprobar VALIDATION_B02 podrá ejecutarse B 0.2 sobre el corpus congelado FRAGSEG 0.2.
