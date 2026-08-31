# LTMD-U1 — lenguas indígenas en los Libros de Texto Gratuitos 0.1

**Estado:** exploratorio computacional; no equivale a validación semántica.

**Fecha del corte:** 2026-08-30.

**Study ID:** `LTMD-U1-INDIGENOUS-LANGUAGES-0.1`.

**Base del repositorio:** `74dc38dac39bb7217481edc179cd9eee6e116547`.

## 1. Propósito

Este estudio documenta un primer corte longitudinal sobre la presencia y representación de las lenguas indígenas en la Full-Text Research Layer (FTRL) de LTMD-U1. Responde tres preguntas exploratorias:

1. ¿Cuándo aumenta o disminuye la presencia de referencias lingüísticas indígenas en los Libros de Texto Gratuitos (LTG)?
2. ¿Cuánto espacio ocupan esas referencias, medido como páginas candidatas y como tasa por 1,000 páginas de cada generación?
3. ¿Cómo cambia preliminarmente el marco escolar con que se presentan las lenguas indígenas?

La unidad primaria es la **página canónica OCR**. El estudio no promueve ninguna identidad a `text_verified` o `semantic_ready` y conserva los guardas metodológicos de LTMD:

- `ocr_available != text_verified`;
- `corpus_ready != semantic_ready`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`.

## 2. Alcance técnico

El corte trabaja sobre las once olas FTRL W1-W11 y sobre el universo técnicamente admitido y procesable reportado por el cierre global U1:

- 542 identidades históricas en el denominador fijo;
- 524 identidades `validated` técnicamente;
- 5 `final_exception`;
- 13 `blocked_active_retention`;
- 492 objetos canónicos procesados;
- 86,549 páginas fuente canónicas.

Por tanto, este estudio describe el corpus FTRL técnicamente disponible, **no una completitud archivística absoluta**. Las 18 identidades fuera de los 524 objetos procesados delimitan el alcance de cualquier afirmación negativa.

La serie observada en este corte comprende las generaciones 1960, 1966, 1972, 1982, 1988, 1993, 2008, 2011, 2014, 2018 y 2019. No debe presentarse todavía como una serie anual continua hasta 2026.

## 3. Diseño de recuperación

### 3.1 Capa A — discurso explícito general

Recupera formulaciones que tematizan directamente la cuestión lingüística indígena, por ejemplo:

- `lengua indígena` / `lenguas indígenas`;
- `idioma indígena` / `idiomas indígenas`;
- `lengua originaria` / `lenguas originarias`;
- `diversidad lingüística`;
- formulaciones equivalentes registradas durante la exploración.

Resultado agregado observado: **466 páginas en 144 libros**.

### 3.2 Capa B — lenguas nombradas con contexto lingüístico

Recupera nombres de lenguas o conjuntos lingüísticos sólo cuando la página contiene además señales de uso lingüístico como `lengua`, `idioma`, `hablar`, `hablante`, `bilingüe`, `vocabulario`, `palabra`, `traducción` o `dialecto`.

Esta restricción evita contar automáticamente referencias étnicas, civilizatorias, territoriales o toponímicas. Por ejemplo, `maya` no se interpreta como lengua si el contexto sólo se refiere a la civilización maya.

La unión depurada de las capas A y B produjo **1,214 páginas candidatas de alta pertinencia en 256 objetos canónicos**.

### 3.3 Estado de la sintaxis ejecutable

Las familias conceptuales quedaron documentadas durante la exploración, pero la **cadena FTS/regex exacta de cada iteración no quedó congelada en un artefacto público versionado**. En consecuencia:

- las cifras de esta versión son un resultado exploratorio registrado;
- no deben presentarse todavía como una corrida completamente reproducible bit a bit;
- antes de una publicación inferencial debe repetirse la recuperación con consultas exactas preregistradas y conservarse el ledger de candidatos.

Este faltante se registra deliberadamente para no reconstruir a posteriori una sintaxis que no fue preservada.

## 4. Resultados globales

| Indicador | Resultado | Interpretación correcta |
|---|---:|---|
| Corpus | 86,549 páginas / 492 objetos | universo canónico técnicamente procesado |
| Indicador amplio | 1,214 páginas / 256 libros | páginas con señal lingüística indígena de alta pertinencia |
| Discurso explícito | 466 páginas / 144 libros | tematización directa de lenguas indígenas/originarias/diversidad lingüística |
| Cobertura amplia | ~1.40% | páginas con al menos una señal; no porcentaje de palabras o currículo |
| Cobertura explícita | ~0.54% | subconjunto restrictivo del corpus |
| 1993 | 383 páginas candidatas; 83/114 libros | fuerte efecto de monografías estatales y descripción territorial |

La cifra 256/492 indica dispersión bibliográfica, no intensidad temática: basta una página para que un libro entre al conteo.

## 5. Resultado longitudinal normalizado

Las tasas se expresan como páginas candidatas por cada 1,000 páginas de la generación. El archivo canónico de esta versión es `data/research/ltmd_u1_indigenous_languages_generation_rates_0_1.csv`.

| Generación | Amplio / 1,000 | Explícito / 1,000 | Explícito como % del amplio |
|---:|---:|---:|---:|
| 1960 | 3.68 | 0.57 | 15.5% |
| 1966 | 4.64 | 1.65 | 35.6% |
| 1972 | 2.85 | 0.43 | 15.1% |
| 1982 | 2.73 | 1.82 | 66.7% |
| 1988 | 3.60 | 1.71 | 47.5% |
| 1993 | 17.64 | 3.32 | 18.8% |
| 2008 | 15.30 | 10.25 | 67.0% |
| 2011 | 15.24 | 11.30 | 74.1% |
| 2014 | 27.63 | 9.60 | 34.7% |
| 2018 | 7.65 | 1.46 | 19.1% |
| 2019 | 14.53 | 8.82 | 60.7% |

### 5.1 Lectura descriptiva

El indicador amplio y el explícito no siguen la misma trayectoria. 1993 muestra un gran salto en referencias lingüísticas contextualizadas, mientras que 2008-2011 elevan con mayor fuerza la tematización general explícita. 2014 presenta la tasa amplia más alta, pero la composición editorial de esa generación exige controlar por tipo de libro antes de atribuir el cambio a política curricular.

El descenso de 2018 tampoco puede interpretarse como retroceso: el corpus de esa generación es más pequeño y diferente en composición.

## 6. Lenguas con mayor visibilidad contextual

El archivo canónico de conteos es `data/research/ltmd_u1_indigenous_languages_named_language_counts_0_1.csv`.

| Lengua / conjunto | Páginas candidatas | Libros | Páginas/libro |
|---|---:|---:|---:|
| Náhuatl | 404 | 134 | 3.01 |
| Maya | 236 | 90 | 2.62 |
| Zapoteco | 89 | 61 | 1.46 |
| Mixteco | 70 | 44 | 1.59 |
| Purépecha / tarasco | 69 | 30 | 2.30 |
| Otomí | 54 | 33 | 1.64 |
| Huasteco / teenek | 43 | 19 | 2.26 |
| Tarahumara / rarámuri | 31 | 25 | 1.24 |
| Cora / náayeri | 27 | 21 | 1.29 |
| Mayo / yoreme | 27 | 15 | 1.80 |
| Yaqui | 23 | 11 | 2.09 |
| Tseltal / tzeltal | 20 | 15 | 1.33 |

**Los conteos se superponen.** Una misma página puede mencionar varias lenguas; por ello no deben sumarse para reconstruir las 1,214 páginas únicas.

Náhuatl y maya dominan la visibilidad contextual. Tarahumara/rarámuri presenta 31 páginas en 25 libros, una dispersión suficiente para justificar un subestudio longitudinal específico.

## 7. Periodización cualitativa preliminar

La exploración sugiere la siguiente hipótesis de trabajo:

### 1960-1966 — pluralidad reconocida con subordinación lingüística

Las lenguas indígenas aparecen como pluralidad persistente, a menudo dentro de una jerarquía que asigna centralidad al español como lengua oficial, nacional o común. Son frecuentes mapas, clasificación y referencias históricas.

### 1972-1988 — integración cultural

La pluralidad lingüística empieza a incorporarse de manera más explícita a la identidad mexicana. Aparecen préstamos al español, actividades comunitarias y formulaciones de enriquecimiento cultural.

### 1993 — territorialización y cuantificación

Las monografías estatales elevan fuertemente la visibilidad mediante censos, mapas, bilingüismo, distribución de hablantes y descripción de grupos etnolingüísticos. La lengua funciona a menudo como variable demográfica y territorial.

### 2008-2011 — giro pedagógico

Los materiales piden investigar, escuchar, recopilar palabras, poemas, canciones o adivinanzas y, en ciertos contextos, producir información vinculada con la lengua de la comunidad. La lengua deja de ser sólo objeto descrito y entra como recurso pedagógico vivo.

### 2014-2019 — diversidad, preservación y derechos

Aumenta la presencia de vocabularios sobre diversidad lingüística, lenguas originarias o nacionales, riesgo de desaparición, educación intercultural y discriminación lingüística.

Esta periodización es **heurística**. No implica sustitución lineal de un marco por otro y debe someterse a codificación humana.

## 8. Hipótesis rectora

La señal longitudinal no parece reducirse a un incremento de menciones. Sugiere una transformación del marco escolar:

> pluralidad subordinada al español -> integración cultural -> territorialización/censo -> valoración y uso pedagógico -> diversidad, preservación y derechos.

Esta secuencia es una **hipótesis histórica generada por recuperación computacional**, no una conclusión final. Para sostenerla en una publicación se requiere validación de página fuente, codificación del contexto y control de composición editorial.

## 9. Riesgos y sesgos

1. **OCR:** puede generar falsos positivos y falsos negativos.
2. **Terminología histórica:** vocablos como `dialecto`, `vernácula`, `castellanización` o formulaciones antiguas pueden escapar a consultas contemporáneas.
3. **Polisemia:** nombres como maya, tarahumara u otomí pueden referirse a pueblo, territorio, cultura o lengua.
4. **Composición editorial:** generaciones con monografías estatales o libros de entidad no son directamente comparables con generaciones de otra composición.
5. **No independencia textual:** libros relacionados o derivados pueden compartir contenido.
6. **Cobertura:** 13 retenciones activas y 5 excepciones finales delimitan las afirmaciones de ausencia.
7. **Causalidad:** frecuencia no demuestra por sí sola cambio de política lingüística; esa inferencia requiere documentos curriculares, normativos y editoriales externos.

## 10. Fase de validación requerida

La siguiente fase legítima debe:

1. congelar la sintaxis exacta de recuperación;
2. reconstruir el ledger de candidatos con `page_id`, viewer canónico, generación, grado, título, posición fuente, URL y hashes;
3. revisar visualmente cada candidato que sostenga una afirmación;
4. clasificar `verified_true`, `false_positive` o `uncertain`;
5. codificar función discursiva con `docs/LTMD_U1_INDIGENOUS_LANGUAGES_CODEBOOK_0_1.md`;
6. controlar por género editorial, asignatura y grado;
7. medir acuerdo intercodificador en una muestra antes de automatizar clasificación;
8. publicar sólo metadatos, conteos y paráfrasis permitidas, no OCR completo ni reproducciones de páginas fuente.

## 11. Productos derivados prioritarios

- artículo longitudinal general sobre representación de lenguas indígenas;
- estudio de cambio terminológico: `dialecto` / `lengua indígena` / `lengua originaria`;
- subestudio tarahumara/rarámuri;
- estudio de territorialización en 1993;
- estudio del giro pedagógico 2008-2011;
- análisis de desigualdad de visibilidad entre lenguas;
- atlas longitudinal interactivo de lenguaje escolar.

## 12. Licencia y derechos

Los agregados, métricas, etiquetas analíticas y tablas derivadas originales se publican conforme a `DATA_LICENSE.md` cuando LTMD posee facultad suficiente para licenciarlos. Este paquete **no redistribuye OCR íntegro, imágenes de página, PDFs fuente ni otros contenidos expresivos de SEP/CONALITEG**.

## 13. Archivos de esta versión

- `docs/LTMD_U1_INDIGENOUS_LANGUAGES_STUDY_0_1.md`
- `docs/LTMD_U1_INDIGENOUS_LANGUAGES_CODEBOOK_0_1.md`
- `data/research/ltmd_u1_indigenous_languages_generation_rates_0_1.csv`
- `data/research/ltmd_u1_indigenous_languages_named_language_counts_0_1.csv`
- `data/research/ltmd_u1_indigenous_languages_query_families_0_1.csv`
- `data/research/ltmd_u1_indigenous_languages_qualitative_examples_0_1.csv`
- `data/research/ltmd_u1_indigenous_languages_study_manifest_0_1.json`
- `data/validation/ltmd_u1_indigenous_languages_validation_template_0_1.csv`
