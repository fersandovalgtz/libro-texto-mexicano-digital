# Techo de trabajo automatizable de LTMD

Versión: `LTMD_AUTOMATION_CEILING_0.2`

Decisión metodológica vigente: **1 de septiembre de 2026**.

## Propósito

Este documento distingue qué avances pueden producirse legítimamente sin referencia humana y fija el techo epistemológico de LTMD bajo la decisión vigente de **no ejecutar validación humana como parte del proyecto**.

El objetivo ya no es “esperar” una referencia humana futura. El objetivo es maximizar integridad, reproducibilidad, robustez, controles sintéticos y consistencia computacional sin confundir esos atributos con validez de constructo o verdad histórica.

Reglas canónicas:

`automated_benchmark_passed != human_semantic_validation`

`computational_consistency != construct_validity`

`reproducible != historically_true`

## Trabajo automatizable legítimo

1. Auditoría estructural del corpus, procedencia, routing, hashes y reconstrucción reproducible.
2. Diagnóstico de incertidumbre y sensibilidad de modelos automáticos sin usar plausibilidad histórica como función objetivo.
3. Pruebas sintéticas independientes del corpus histórico.
4. Controles positivos y negativos sintéticos con comportamiento esperado preregistrado.
5. Pruebas metamórficas: transformaciones de entrada para las que el output debería permanecer estable o variar de manera predecible.
6. Determinismo entre ejecuciones idénticas y fingerprints de outputs.
7. Robustez ante perturbaciones técnicas controladas: ruido, blur, contraste, skew, resolución, truncación y otras transformaciones que no requieran juicio humano.
8. Auditoría de cobertura, longitud, concentración por página, grado, generación, ola y dominio.
9. Auditoría geométrica y estructural de layout sin convertir una heurística en categoría humana validada.
10. Comparación entre clasificadores automáticos como **consistencia inter-método**, nunca como accuracy.
11. Bootstrap, estabilidad de clusters, rankings, redes, centralidades, tópicos y change points.
12. Análisis de dependencia documental, reutilización, revisión, reemplazo, persistencia y novelty.
13. Análisis léxico, n-gramas y coocurrencias con supresión y privacidad preregistradas.
14. Detección de drift entre generaciones, siempre descrita como cambio computacional observable hasta interpretación historiográfica independiente.
15. Manifiestos criptográficos de integridad y provenance chaining.
16. Validación de contratos JSON, schemas, estados científicos y políticas de privacidad.
17. Benchmarking de tiempo, memoria y escalabilidad de pipelines cuando sea relevante.
18. Documentación de resultados negativos, límites y excepciones.
19. Contextualización del corpus con fuentes curriculares e historiográficas externas, manteniendo separación entre evidencia documental y señal computacional.

## Estados automáticos permitidos

La infraestructura puede producir estados como:

- `cataloged`;
- `source_admitted`;
- `ocr_available`;
- `computational_candidate`;
- `exploratory_signal`;
- `structurally_verified`;
- `cryptographically_verified`;
- `benchmark_passed`.

Estos estados describen propiedades técnicas o computacionales verificables.

## Estados que la automatización no puede promover

Sin referencia humana no es metodológicamente legítimo que LTMD marque automáticamente:

- `text_verified=true`;
- `semantic_ready=true`;
- `human_validated=true`;
- `ground_truth=true`;
- `historically_true=true`.

Tampoco es legítimo:

- afirmar que una categoría semántica automática es válida porque coincide consigo misma o con otro clasificador automático;
- llamar “verdad de referencia” a etiquetas producidas por un LLM, SEMB, Rule A u otro método automático;
- seleccionar thresholds o arquitecturas porque producen la trayectoria histórica más plausible, atractiva o compatible con expectativas previas;
- declarar que una heurística de layout equivale automáticamente a una categoría tipográfica humana;
- reportar CER/WER como exactitud frente a ground truth si no existe una transcripción humana;
- convertir agreement automático en accuracy;
- usar ausencia de hits como demostración de ausencia histórica;
- generalizar causalmente desde señales del corpus sin diseño inferencial apropiado.

## Sustitutos metodológicamente válidos a la validación humana

Cuando no existe referencia humana, LTMD puede elevar la calidad de una señal mediante evidencia convergente, siempre etiquetándola correctamente:

### Robustez

Una señal es más defendible si permanece estable ante perturbaciones pequeñas y razonables de entrada, parámetros y muestreo.

### Reproducibilidad

Una señal es más defendible si ejecuciones idénticas producen outputs byte-idénticos o diferencias explicables y versionadas.

### Convergencia inter-método

Dos métodos independientes que producen patrones similares aportan evidencia de estabilidad, pero no prueban que el constructo esté bien definido.

### Controles sintéticos

Casos artificiales con verdad conocida por construcción permiten probar si un algoritmo responde correctamente a propiedades formales específicas. Esto valida comportamiento del software, no semántica histórica del corpus real.

### Negative controls

Variables o relaciones que no deberían producir señal pueden ayudar a detectar leakage, sobreajuste o artefactos del pipeline.

### Bootstrap y sensibilidad

Intervalos, estabilidad de rankings, redes y change points frente a remuestreo permiten cuantificar fragilidad sin necesidad de etiquetas humanas.

### Evidencia documental dura

Hashes, identidad byte a byte, routing institucional, cardinalidades y relaciones exactas de reutilización son hechos computacional/documentalmente verificables y pueden sostener análisis fuertes sin validación semántica humana.

## Automated Benchmark

`LTMD_AUTOMATED_BENCHMARK_0.1` convierte este techo metodológico en una batería ejecutable. Se documenta en:

- `docs/LTMD_AUTOMATED_BENCHMARK_0_1.md`;
- `data/benchmarks/ltmd_automated_benchmark_0_1_baseline.json`;
- `scripts/run_automated_benchmark.py`;
- `.github/workflows/automated-benchmark.yml`.

El benchmark comprueba integridad U1, catálogo contemporáneo, coherencia de release, guardas epistemológicas, frontera de derechos y estados de materializaciones Analytics.

## Protocolos humanos archivados

Los antiguos frentes de validación humana #95, #123 y #124 se cerraron como `not planned` el 1 de septiembre de 2026. Sus protocolos y scripts permanecen versionados para que terceros puedan ejecutarlos si lo desean.

Su cierre **no equivale** a validación completada y no cambia retrospectivamente el estado científico de resultados existentes.

## Punto operativo final

LTMD considera agotado el requisito de trabajo humano cuando la infraestructura alcanza el máximo defendible mediante controles automáticos. El proyecto puede continuar creciendo científicamente mediante genealogía documental, robustez, redes semánticas exploratorias, cambio curricular computacional, análisis multimodal derivado, alineación curricular y cohortes contemporáneas, siempre dentro de las guardas anteriores.

El límite debe expresarse en cada producto: **alta reproducibilidad computacional no sustituye validez semántica humana**.