# LTMD-U1 — resultados del rerun preregistrado sobre lenguas indígenas 0.2

**Versión:** `LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2`

**Fecha de ejecución:** 2026-08-30.

## 1. Qué demuestra esta corrida

La versión 0.2 ejecuta un algoritmo congelado antes de la corrida y deliberadamente independiente del corte exploratorio 0.1. El objetivo no fue reproducir sus cifras, sino comprobar qué señales sobreviven cuando la recuperación se vuelve explícita, determinista y auditable.

La enumeración de entrada reconcilió exactamente:

- 288 bases SQLite privadas;
- 86,549 `page_id` únicos;
- 492 objetos canónicos;
- 0 conflictos de hashes o identidad entre páginas duplicadas.

La cardinalidad coincide con el cierre FTRL-U1. Por tanto, la corrida no depende de una muestra parcial de las páginas técnicamente procesadas.

## 2. Resultado agregado 0.2

La nueva corrida recuperó:

- **1,151 páginas candidatas amplias**;
- **457 páginas de discurso explícito general**;
- **859 páginas con al menos una de las 12 lenguas/conjuntos del lexicón 0.2 en contexto lingüístico próximo**;
- **165 páginas** pertenecen simultáneamente a la capa explícita y a la capa nominal contextual;
- **266 objetos canónicos** contienen al menos un candidato.

Todos los registros permanecen en `not_visually_validated`. Ninguno cambia el estado científico del corpus.

## 3. Robustez frente al corte exploratorio 0.1

El resultado más importante de la repetición es que la capa **explícita** es muy estable:

- 0.1: 466 páginas;
- 0.2: 457 páginas;
- diferencia: **−9 páginas (−1.9%)**.

La estabilidad aumenta en las generaciones recientes:

| Generación | Explícito 0.1 | Explícito 0.2 |
|---:|---:|---:|
| 2008 | 67 | 67 |
| 2011 | 86 | 87 |
| 2014 | 132 | 131 |
| 2018 | 4 | 4 |
| 2019 | 74 | 74 |

En cambio, el indicador amplio cambia más:

- 0.1: 1,214 páginas;
- 0.2: 1,151 páginas;
- diferencia: **−63 páginas (−5.2%)**.

Esto es metodológicamente esperable: la capa amplia depende de decisiones sobre contexto, polisemia y ventanas de proximidad, mientras que expresiones directas como `lenguas indígenas` son más estables.

## 4. Serie normalizada 0.2

| Generación | Páginas totales | Amplio / 1,000 | Explícito / 1,000 | Nominal contextual / 1,000 |
|---:|---:|---:|---:|---:|
| 1960 | 3,536 | 6.5045 | 0.5656 | 5.9389 |
| 1966 | 6,680 | 6.4371 | 1.7964 | 5.0898 |
| 1972 | 7,020 | 3.9886 | 0.4274 | 3.5613 |
| 1982 | 3,292 | 2.4301 | 1.5188 | 0.9113 |
| 1988 | 5,274 | 4.1714 | 1.5169 | 3.0338 |
| 1993 | 21,708 | 16.9062 | 2.9482 | 15.2478 |
| 2008 | 6,538 | 16.0600 | 10.2478 | 8.5653 |
| 2011 | 7,611 | 16.2922 | **11.4308** | 6.7008 |
| 2014 | 13,752 | **20.3607** | 9.5259 | **15.4159** |
| 2018 | 2,744 | 9.1108 | 1.4577 | 8.7464 |
| 2019 | 8,394 | 15.0107 | 8.8158 | 10.2454 |

La separación entre las dos curvas conserva el patrón interpretativo principal del corte 0.1:

- **1993** muestra una densidad nominal/contextual muy alta pero una densidad explícita mucho menor;
- **2008–2011** elevan bruscamente el discurso explícito;
- **2011** alcanza la tasa explícita más alta de la serie 0.2;
- **2014** conserva el máximo de presencia amplia, aunque el efecto de composición editorial debe controlarse;
- **2019** mantiene una tasa explícita alta frente a las generaciones tempranas.

Por sí misma, esta forma de la serie todavía no prueba causalidad curricular, pero refuerza la hipótesis de que el cambio histórico no consiste únicamente en nombrar más lenguas: cambia el grado en que la diversidad lingüística se tematiza explícitamente.

## 5. Resultado por lengua: usar como cola de validación, no como prevalencia final

Los 12 conjuntos del lexicón congelado producen:

| Lengua / conjunto | Páginas candidatas 0.2 | Libros |
|---|---:|---:|
| Náhuatl | 360 | 145 |
| Maya | 266 | 103 |
| Zapoteco | 100 | 70 |
| Mixteco | 88 | 56 |
| Purépecha / tarasco | 83 | 37 |
| Mayo / yoreme | 73 | 57 |
| Huasteco / teenek | 65 | 28 |
| Otomí | 54 | 34 |
| Tarahumara / rarámuri | 42 | 31 |
| Yaqui | 39 | 21 |
| Cora / náayeri | 28 | 22 |
| Tseltal / tzeltal | 25 | 18 |

Estos conteos son **candidatos de recuperación**. No deben citarse todavía como número de páginas históricamente válidas de cada lengua.

## 6. Diagnóstico crítico: el caso `mayo`

La repetición 0.2 produjo una alerta metodológica útil. El grupo Mayo/yoreme aumentó de 27 candidatos en 0.1 a 73 en 0.2. De esos 73 candidatos, **64 contienen la forma singular `mayo`**.

Una revisión diagnóstica privada del OCR de los primeros candidatos de esa forma mostró contaminación evidente por:

- el mes de mayo;
- `Cinco de Mayo`;
- títulos y usos léxicos no etnolingüísticos;
- al menos un error OCR compatible con una palabra distinta.

Por tanto, **73 no puede interpretarse como prevalencia de la lengua mayo**. Este hallazgo no invalida la corrida: demuestra por qué el ledger de candidatos debe preceder a la validación humana y por qué la homonimia debe registrarse explícitamente.

No se modifica retroactivamente el algoritmo 0.2 para eliminar esos casos. Hacerlo después de observar el resultado rompería la lógica preregistrada. Una regla de desambiguación futura deberá versionarse como 0.3 o resolverse mediante validación humana.

## 7. Tarahumara / rarámuri

La corrida 0.2 recupera **42 páginas candidatas en 31 libros**, frente a 31 páginas en 25 libros del corte 0.1. Su distribución 0.2 es:

- 1966: 3 páginas;
- 1993: 12;
- 2008: 8;
- 2011: 2;
- 2014: 10;
- 2019: 7.

La persistencia en varias generaciones y la dispersión bibliográfica sostienen la pertinencia de un subestudio específico. La diferencia 0.1↔0.2 obliga, sin embargo, a validar las 42 páginas antes de formular una trayectoria histórica propia de rarámuri/tarahumara.

## 8. Qué parte de la hipótesis 0.1 gana apoyo

La siguiente formulación permanece como **hipótesis**, pero gana robustez descriptiva:

> pluralidad subordinada al español → integración cultural → territorialización/censo → valoración y uso pedagógico → diversidad, preservación y derechos.

La evidencia más fuerte que aporta 0.2 para esa hipótesis es cuantitativa y estructural:

1. las tasas explícitas son bajas en las generaciones tempranas;
2. 1993 eleva mucho la presencia nominal/contextual sin elevar en la misma proporción la tematización explícita;
3. 2008 y 2011 muestran un salto claro de discurso explícito;
4. 2014 y 2019 mantienen niveles explícitos muy superiores a la mayor parte de las generaciones tempranas.

La asignación de etiquetas como `subordination_to_spanish`, `territorialization`, `pedagogical_turn` o `rights_affirming` sigue requiriendo el codebook y revisión visual de página.

## 9. Artefactos y trazabilidad

La corrida está anclada en:

- `docs/LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_PROTOCOL_0_2.md`;
- `scripts/analyze_indigenous_languages.py`;
- `tests/test_analyze_indigenous_languages.py`;
- `data/research/ltmd_u1_indigenous_languages_rerun_summary_0_2.json`;
- `data/research/ltmd_u1_indigenous_languages_generation_summary_0_2.csv`;
- `data/research/ltmd_u1_indigenous_languages_named_language_counts_0_2.csv`;
- `data/research/ltmd_u1_indigenous_languages_named_language_by_generation_0_2.csv`;
- comparadores 0.1↔0.2 por generación y lengua.

La corrida produjo además un ledger text-free de 1,151 candidatos. Su SHA-256 queda registrado en el resumen de ejecución. El ledger completo permanece como derivado privado/reconstruible hasta la fase de validación visual; los agregados públicos no lo convierten en evidencia semánticamente validada.

## 10. Siguiente fase científica

La prioridad ya no es ajustar las cifras. Es **validar la cola de candidatos**.

Orden recomendado:

1. validar primero las 457 páginas de discurso explícito, porque forman la señal más reproducible;
2. estratificar por generación y género editorial;
3. codificar cada página validada con `LTMD_U1_INDIGENOUS_LANGUAGES_CODEBOOK_0_1`;
4. registrar falsos positivos por causa (`OCR`, homonimia, contexto étnico no lingüístico, contexto insuficiente);
5. seleccionar una muestra doblemente codificada para acuerdo;
6. sólo después publicar inferencias sobre cambio discursivo y comparaciones por lengua.

## 11. Regla de interpretación vigente

`search_hit != historical_claim` sigue siendo la regla decisiva. La principal ganancia científica de 0.2 es que el estudio ya posee una **segunda medición independiente y reproducible** y sabemos con precisión qué componentes son robustos y cuáles requieren validación más estricta.
