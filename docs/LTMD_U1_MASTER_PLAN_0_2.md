# Plan Maestro LTMD-U1 — cobertura integral de 542 visores

Versión: **LTMD_U1_MASTER_PLAN_0.2**  
Fecha de actualización: **2026-08-15**  
Universo de referencia: snapshot reproducible del Catálogo Histórico de CONALITEG incorporado a LTMD.

## 1. Objetivo rector

LTMD-U1 tiene como meta explícita **representar técnicamente los 542 visores únicos del universo U1**, sin reducir el proyecto a una muestra disciplinar. Ciencias Naturales fue el banco de pruebas; la estrategia actual es industrializar el mismo contrato técnico hacia el universo completo.

El criterio rector es:

> **542/542 visores con identidad documental, procedencia, resolución o excepción de activos, hashes, OCR técnico, PAGESTRUCT, FRAGSEG y dependencia documental explícita cuando exista; semántica sólo después de validación humana pertinente.**

El denominador U1 es `viewer_key`. Páginas y fragmentos son medidas complementarias, no sustitutos del número de objetos documentales.

## 2. Línea base posterior a W1

El tablero `LTMD_U1_COVERAGE_0.4` registra:

- catalogados: **542/542 (100.00%)**;
- títulos normalizados: **542/542 (100.00%)**;
- familias normalizadas: **191**;
- activos completamente resueltos: **40/542 (7.38%)**;
- resoluciones parciales activas: **0/542**;
- manifiesto/OCR/PAGESTRUCT/FRAGSEG directo: **36/542 (6.64%)**;
- cobertura FRAGSEG efectiva: **40/542 (7.38%)**;
- semántica humana validada: **0/542**.

El corpus directamente segmentado suma ahora **73,841 ocurrencias técnicas de fragmento**. Esta cifra no equivale a observaciones históricas independientes.

## 3. Hito 1 — U1-W1 Ciencias Naturales: COMPLETADA

El dominio operacional `ciencias_naturales` comprende 40 visores y quedó en:

- **40/40 activos full**;
- **36/40 FRAGSEG directo**;
- **40/40 cobertura efectiva**;
- **0 restantes**.

Los cuatro objetos no reprocesados directamente son aliases 2018→2019 byte-idénticos. Los dos objetos de 1966 fueron incorporados desde fuente y los dos 2008 fueron reconciliados conservando tres anomalías originales y tres recuperaciones criptográficas unívocas.

W1 añadió **8,985 fragmentos** al corpus directo:

- 1966: 4,618;
- 2008: 4,367.

Documento de cierre: `LTMD_U1_W1_COMPLETION_2026-08-15.md`.

## 4. Hito 2 — U1-W2 Matemáticas: ACTIVA

W2 está congelada en **64 visores**. La auditoría previa de arquitectura demuestra:

- 64/64 HTML 200;
- 64/64 `x.js`;
- 64/64 señal `ag_pages`;
- 64/64 arquitectura dinámica estándar;
- 0 casos de arquitectura no estándar en el probe.

`claves.json` declara **13,656 posiciones** para esos 64 visores.

Distribución documental de W2:

| generación | visores | posiciones declaradas |
|---:|---:|---:|
| 1972 | 6 | 1,350 |
| 1982 | 4 | 1,032 |
| 1988 | 4 | 1,018 |
| 1993 | 10 | 1,724 |
| 2008 | 6 | 1,224 |
| 2011 | 6 | 1,140 |
| 2014 | 12 | 2,760 |
| 2018 | 8 | 1,704 |
| 2019 | 8 | 1,704 |
| **Total** | **64** | **13,656** |

La etapa actual de W2 es la **auditoría empírica de activos por 64 shards**, donde cada posición declarada se prueba y cada JPEG servido se recorre para SHA-256 sin persistir la fuente.

## 5. Política industrial W2

La promoción de Matemáticas seguirá este orden:

1. auditar activos directos de los 64 visores;
2. clasificar cada objeto en `direct_asset_ready`, parcial, routing anomaly o probe failure;
3. detectar aliases exactos sólo mediante secuencia completa de SHA-256 alineados;
4. resolver huecos/rutas sin inferencia nominal;
5. congelar la cola de objetos técnicamente recuperables;
6. OCR por libro;
7. validar transferibilidad de PAGESTRUCT y FRAGSEG estructural;
8. ejecutar FRAGSEG por shards;
9. actualizar tablero U1;
10. no ejecutar semántica de Ciencias Naturales sobre Matemáticas.

Una anomalía de un libro no invalida ni fuerza a recalcular los demás objetos válidos.

## 6. Arquitectura universal

La fábrica U1 es:

`catálogo → viewer/book identity → asset audit → SHA-256 → OCR temporal → PAGESTRUCT → FRAGSEG → dependence/aliases → technical corpus`

Cada etapa conserva un artefacto final y el tablero sólo da crédito cuando ese artefacto existe y supera sus invariantes.

## 7. Cobertura directa y efectiva

`fragseg_materialized` significa que ese visor fue procesado directamente.

`effective_fragseg_coverage` puede heredarse únicamente mediante evidencia criptográfica suficiente de alias de bytes ya procesados. La herencia ahorra cómputo pero **no elimina la identidad documental ni convierte dos registros en una sola entidad bibliográfica**.

## 8. Anomalías y recuperación

La experiencia W1 fija una política general:

- un 404 interno se conserva como anomalía;
- un alias o fuente alternativa requiere evidencia, no similitud nominal;
- una recuperación puntual conserva la URL/estado original y la fuente efectiva;
- continuidad criptográfica no equivale automáticamente a identidad bibliográfica total;
- los fallos técnicos del runner se distinguen de fallos del corpus.

## 9. Olas posteriores

Después de W2:

- W3 Español/Lengua — 130 visores;
- W4 Ciencias Sociales — 14;
- W5 Historia — 18;
- W6 Geografía/Atlas — 42;
- W7 Cívica/Ética — 30;
- W8 Artes — 20;
- W9 Educación Física — 4;
- W10 Integrados/multiarea — 69;
- W11 Otros/revisión operacional — 111.

La taxonomía es logística, no una ontología curricular.

## 10. Carril semántico paralelo

SEMB 0.3 continúa en **`WAITING_HUMAN_REFERENCE`**.

La expansión técnica a 542 objetos puede avanzar sin fabricar etiquetas. Ningún dominio hereda automáticamente una validación semántica desarrollada para otro. Matemáticas, Español, Historia y otras áreas requerirán validación específica cuando sus preguntas analíticas lo exijan.

## 11. KPIs U1

El tablero reporta como mínimo:

- catalogados / 542;
- activos full / 542;
- OCR directo / 542;
- PAGESTRUCT directo / 542;
- FRAGSEG directo / 542;
- cobertura efectiva / 542;
- dependencia auditada / 542;
- semántica validada / 542;
- cobertura por dominio y ola.

## 12. Releases e integridad

`v0.1.0-rc.1` permanece como un corte histórico previo al programa U1 actual. No se reescribe.

Los artefactos U1 posteriores deberán entrar en nuevos cortes de integridad y nuevas releases cuando existan hitos suficientemente estables. La release no es una copia móvil de `main`.

## 13. Criterio de cierre U1

U1 se considera técnicamente completo cuando **542/542 visores** tengan representación defendible: procesamiento directo, alias exacto verificado o excepción técnica final explícitamente gobernada, con identidad y trazabilidad preservadas.

El cierre técnico del universo no implica que exista un único modelo semántico válido para los 542 objetos.

## 14. Horizonte U2

U2 —materiales fuera del snapshot de 542— sólo se abrirá con un denominador propio y versionado. Nunca se ampliará silenciosamente U1 ni se reescribirá su universo a posteriori.
