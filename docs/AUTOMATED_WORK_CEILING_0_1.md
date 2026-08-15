# Techo de trabajo automatizable antes de la referencia humana

Versión: `LTMD_AUTOMATION_CEILING_0.1`

## Propósito

Este documento distingue qué avances pueden producirse legítimamente sin referencia humana y cuáles requieren juicio humano para evitar que el proyecto confunda reproducibilidad computacional con validez de constructo.

## Trabajo automatizable y ya preparado

1. Auditoría estructural del corpus, OCR, procedencia, hashes y reconstrucción reproducible.
2. Diagnóstico de la incertidumbre de SEMB 0.2 y atribución de sus fuentes al gate, márgenes y exclusiones.
3. Pruebas sintéticas independientes del corpus histórico.
4. Desarrollo de candidatos algorítmicos exclusivamente sobre material sintético, claramente marcados como provisionales.
5. Auditoría de cobertura, longitud, concentración por página y pesos de postestratificación de la futura muestra humana.
6. Auditoría geométrica de `heading_candidate` mediante rasgos de layout sin persistir texto OCR.
7. Capa `FRAGTYPE_0.3_SHADOW` no destructiva, que preserva fragmentos/hashes y separa la elegibilidad semántica de la categoría residual de longitud.
8. Muestras ciegas para referencia semántica y para validar unidades breves residuales.
9. Criterios de aceptación preregistrados, stage gates, validador de anotaciones, cálculo de fiabilidad, cola de adjudicación, model lock y evaluación bloqueada de una sola apertura.
10. Plan de análisis histórico posterior a validación, incluyendo dependencia por página, multiplicidad, sensibilidad metodológica y límites de generalización.
11. Manifiesto criptográfico de integridad de artefactos críticos.

## Trabajo automatizable adicional permitido

- ampliar baterías sintéticas con fenómenos lingüísticos previamente definidos;
- ejecutar pruebas de regresión del software;
- probar candidatos de arquitectura contra material sintético y documentar sus fallos;
- mejorar robustez de workflows, hashes y trazabilidad;
- preparar scripts que calculen métricas futuras sin ejecutarlos sobre la validación bloqueada;
- documentar métodos, decisiones y resultados negativos;
- auditar representatividad de metadatos sin consultar etiquetas humanas ni resultados históricos como función objetivo;
- contextualizar el corpus con fuentes primarias curriculares, manteniendo esa historiografía separada del desarrollo del clasificador.

## Límites que no deben cruzarse

Sin referencia humana no es metodológicamente legítimo:

- afirmar que una categoría semántica automática es válida porque coincide consigo misma o con otro clasificador automático;
- llamar “verdad de referencia” a etiquetas producidas por un LLM o por SEMB/Rule A;
- seleccionar thresholds o arquitecturas porque producen la trayectoria histórica más plausible o atractiva;
- declarar que `heading_candidate` equivale a encabezado tipográfico real;
- promover un candidato sintético a SEMB 0.3 de producción;
- abrir los 160 casos de validación antes de bloquear el modelo desarrollado con los 320 casos humanos de desarrollo;
- presentar como hallazgo histórico primario resultados cuya capa semántica no haya pasado validación bloqueada;
- generalizar estadísticamente desde los cuatro volúmenes del piloto a todos los libros de texto mexicanos.

## Punto de transición

El proyecto habrá agotado razonablemente el trabajo pre-humano cuando estén completos: pruebas sintéticas, auditorías de cobertura/layout, infraestructura de integridad y validación, candidatos computacionales provisionales y documentación metodológica. A partir de ese punto, añadir más automatización puede aumentar complejidad pero no resolver el principal problema epistemológico: si las categorías representan de manera reproducible lo que investigadores humanos reconocen en los fragmentos.
