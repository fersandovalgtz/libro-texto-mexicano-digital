# Plan Maestro LTMD-U1 — cierre técnico, excepciones y transición a validación humana

Versión: **LTMD_U1_MASTER_PLAN_0.3**  
Fecha de actualización: **2026-08-23**  
Universo de referencia: snapshot reproducible de **542 visores únicos** del Catálogo Histórico de CONALITEG incorporado a LTMD.

## 1. Objetivo rector

LTMD-U1 representa un universo histórico-computacional de 542 identidades documentales. El proyecto no equipara catálogo, visor, activo, libro bibliográfico, contenido textual ni observación semántica. La meta técnica sigue siendo que cada identidad tenga una representación defendible mediante procesamiento directo, relación criptográfica/documental demostrada o excepción final explícita, con procedencia y límites preservados.

El criterio rector vigente es:

> **542/542 identidades con estado técnico explícito y auditable; ninguna imputación silenciosa; semántica sólo después de referencia humana pertinente.**

## 2. Corte técnico vigente

El tablero canónico `data/catalog/ltmd_u1_coverage.md` registra al 23 de agosto de 2026:

- universo histórico operativo: **542/542** identidades;
- cobertura técnica efectiva cerrada o resuelta: **524/542 (96.68%)**;
- objetos canónicos de procesamiento cerrados: **492/542 (90.77%)**;
- residual fuera de cobertura efectiva: **18/542 (3.32%)**;
- de ese residual, **13** identidades son retenciones activas y **5** son excepciones técnicas finales;
- validación semántica humana incorporada al tablero: **0/542**.

La diferencia entre 524 identidades efectivamente cubiertas y 492 objetos canónicos no es una pérdida: refleja aliases y relaciones de identidad/reutilización técnicamente demostradas que evitan duplicar procesamiento sin borrar identidades históricas.

## 3. Estado por ola

| ola | dominio operacional | plan | cobertura efectiva | canónicos | residual | ciclo residual | estado |
|---|---|---:|---:|---:|---:|---|---|
| W1 | Ciencias Naturales | 40 | 40 | 36 | 0 | — | cerrada |
| W2 | Matemáticas | 64 | 60 | 57 | 4 | 4 activas | cierre parcial con excepciones preservadas |
| W3 | Español / Lengua | 130 | 130 | 114 | 0 | — | cerrada |
| W4 | Ciencias Sociales | 14 | 14 | 14 | 0 | — | cerrada |
| W5 | Historia | 18 | 18 | 15 | 0 | — | cerrada |
| W6 | Geografía / Atlas | 42 | 42 | 37 | 0 | — | cerrada |
| W7 | Formación Cívica y Ética | 30 | 25 | 25 | 5 | 5 activas | cohorte fuente-admitida cerrada |
| W8 | Artes | 20 | 16 | 16 | 4 | 4 activas | cohorte fuente-admitida cerrada |
| W9 | Educación Física | 4 | 4 | 4 | 0 | — | cerrada |
| W10 | Integrados / Multiarea | 69 | 68 | 68 | 1 | 1 final | cohorte fuente-admitida cerrada |
| W11 | Otros / No clasificados | 111 | 107 | 106 | 4 | 4 finales | cohorte fuente-admitida cerrada |
| **Total** |  | **542** | **524** | **492** | **18** | **13 activas + 5 finales** |  |

La taxonomía por ola es logística y operacional. No constituye una ontología curricular ni autoriza inferencias históricas por sí sola.

## 4. Registro transversal del residual de fuente

La deuda técnica residual ya no se gestiona únicamente en documentos dispersos. `data/catalog/ltmd_u1_retained_source_register.csv` mantiene una fila por identidad fuera de cobertura y `docs/LTMD_U1_RETAINED_SOURCE_REGISTER.md` documenta sus clases, evidencia admisible, reglas de cierre y ciclo de vida.

Distribución vigente:

- W2 Matemáticas: **4 retenciones activas** — issue #4 abierto;
- W7 Formación Cívica y Ética: **5 retenciones activas** — issue #5 abierto;
- W8 Artes: **4 retenciones activas** — issue #9 abierto;
- W10 Integrados / Multiarea: **1 excepción técnica final** — issue #11 cerrado;
- W11 Otros / No clasificados: **4 excepciones técnicas finales** — issues #13 y #14 cerrados.

El validador `scripts/validate_u1_retained_source_register.py` exige que el número de filas del registro sea igual a `universo U1 - cobertura técnica efectiva`, que la distribución por ola coincida con la columna `restantes` del tablero y que el ciclo de vida permanezca en **13 `active_retention` + 5 `final_exception`** mientras no cambie la evidencia.

## 5. Política para resolver retenciones

Una retención activa sólo puede levantarse mediante evidencia reproducible suficiente. Según el caso, son admisibles:

- ruta institucional efectiva del activo o secuencia faltante;
- captura archivada de la misma representación con correspondencia posicional inequívoca;
- relación institucional/documental explícita de reutilización;
- identidad byte-exacta demostrada criptográficamente con otra representación servida.

Deben preservarse URI o identificador archivístico, posición, tamaño, SHA-256, timestamp, procedencia y decisión de admisibilidad cuando correspondan.

No son suficientes por sí solos título, año, grado, cardinalidad, cercanía de identificador, similitud visual, OCR, parecido textual o pertenencia a una misma serie editorial. Estas señales pueden orientar investigación, pero no crean identidad documental.

Una `final_exception` sólo debe reabrirse si aparece evidencia primaria o archivística nueva que no fue cubierta por la búsqueda acotada que produjo su cierre metodológico.

## 6. Cierre técnico no significa 100% de activos servidos

El criterio de cierre U1 no exige ocultar excepciones para producir una cifra artificial de 542/542 procesados. Una identidad puede alcanzar estado técnico final como excepción documentada cuando una búsqueda acotada y reproducible no permita reconstruir su fuente sin imputación.

Por tanto, el proyecto distingue:

- **cobertura efectiva**, cuando existe fuente o representación técnicamente admisible;
- **objeto canónico**, cuando existe una unidad real de procesamiento;
- **retención activa**, cuando la evidencia aún puede investigarse;
- **excepción técnica final**, cuando la ausencia o ambigüedad queda cerrada como resultado auditable.

Las cinco excepciones finales del corte actual —`H2014P1ENA`, `H2014P1EAM`, `H2014P2EAM`, `H2014P3COL` y `H2014P3MOR`— continúan fuera del numerador de cobertura. Su cierre metodológico no se convierte artificialmente en “fuente resuelta”.

## 7. Integridad de la evidencia pública

LTMD mantiene un ledger direccionado por contenido en `data/catalog/ltmd_u1_evidence_integrity.csv` y su informe en `docs/LTMD_U1_EVIDENCE_INTEGRITY.md`. La capa registra ruta, clase de artefacto, tamaño y SHA-256 sin incorporar libros, páginas fuente ni OCR íntegro restringido.

La integridad criptográfica acredita que el artefacto público no cambió silenciosamente. No sustituye la evaluación de procedencia, derechos, admisibilidad de fuente ni validez semántica.

## 8. Frontera epistemológica

La expansión técnica de U1 está casi agotada, pero el principal cuello de botella científico ya no es computacional. `WAITING_HUMAN_REFERENCE` sigue vigente.

Sin referencia humana no es legítimo:

- promover candidatos técnicos a categorías semánticas validadas;
- tratar etiquetas de modelos o reglas como verdad de referencia;
- seleccionar thresholds porque producen una trayectoria histórica atractiva;
- presentar como hallazgo sustantivo una tendencia cuya capa semántica no haya superado validación bloqueada;
- generalizar desde el piloto a la totalidad de los libros de texto mexicanos.

La prioridad metodológica posterior al cierre del carril técnico es ejecutar la referencia humana ya preregistrada y mantener separados desarrollo, validación bloqueada y análisis histórico.

## 9. Carril de validación humana

El trabajo humano debe conservar, como mínimo:

1. referencia OCR revisada para las muestras CER/WER preregistradas;
2. revisión humana del libro de códigos y de sus unidades de análisis;
3. doble codificación y adjudicación de la muestra prevista;
4. cálculo de acuerdo y decisión documentada sobre revisión del codebook;
5. bloqueo del modelo antes de abrir la validación final;
6. evaluación independiente de desempeño;
7. sólo después, análisis histórico de categorías semánticas validadas.

Los dominios no heredan automáticamente una validación semántica desarrollada para otra materia o tipo documental.

## 10. Publicación científica y releases

`v0.1.0-rc.1` permanece como corte histórico metodológico previo a la expansión U1 y no debe reescribirse.

El siguiente corte público debe producirse únicamente cuando exista un estado coherente entre:

- `VERSION`;
- `CITATION.cff`;
- `codemeta.json`;
- notas de release;
- tablero U1;
- registro de retenciones/excepciones;
- ledger de integridad;
- documentación de limitaciones;
- dependencias y procedimientos de reconstrucción.

Un DOI sólo se incorporará después de un depósito real y verificable. No debe anticiparse en metadatos.

## 11. Prioridades técnicas inmediatas

### P1 — trece retenciones activas

Concentrar la investigación de fuente en las **13 identidades todavía abiertas** de W2, W7 y W8 mediante búsquedas acotadas, reproducibles y documentadas. Promover únicamente casos con cadena de evidencia suficiente. Las cinco excepciones finales de W10/W11 no requieren más trabajo rutinario y sólo se reabren ante evidencia nueva.

### P2 — consistencia transversal

Mantener sincronizados tablero, README, plan maestro, issues, manifiestos de integridad y metadatos científicos. Cualquier cifra pública de cobertura debe proceder del tablero canónico o ser comprobable contra él.

### P3 — corte de release posterior a U1

Preparar una nueva candidata de release sólo cuando la superficie pública sea coherente y el ciclo de vida de las excepciones residuales esté explícito. La release debe congelar un corte; no perseguir continuamente `main`.

### P4 — transición humana

Ejecutar la referencia humana preregistrada. A partir de este punto, más automatización por sí sola no resuelve el principal problema epistemológico del proyecto.

## 12. Horizonte U2

U2 —materiales fuera del snapshot U1 de 542 identidades— sólo puede abrirse con denominador, versión, política de incorporación y tablero propios. U1 no se ampliará ni reescribirá silenciosamente a posteriori.

## 13. Criterio de finalización de U1

U1 alcanza cierre técnico cuando las **542 identidades** estén en uno de tres estados explícitos y defendibles:

1. procesamiento directo técnicamente cerrado;
2. cobertura efectiva mediante relación documental/criptográfica demostrada;
3. excepción técnica final documentada después de una investigación acotada y reproducible.

Ese cierre no implica validación semántica 542/542 ni convierte automáticamente el corpus técnico en evidencia histórica interpretada.

## 14. Cierre FTRL exhaustivo W10 — 29 de agosto de 2026

La cohorte fuente-admitida de **W10 — Integrados / Multiarea** quedó procesada y archivísticamente cerrada mediante el run distribuido `33237844420`, anclado al commit `4d0d9a38b650383e51fa44ddbf62510784281dc2`. El cierre comprende **68/68 objetos canónicos fuente-admitidos** y **11,937/11,937 páginas canónicas**, con unión global exacta, partición única y completa, integridad SQLite válida y preservación privada cifrada verificada por redescarga y SHA-256.

La identidad `H2014P1ENA` **no se imputa ni se procesa por sustitución**: conserva su disposición documental `final_exception`, ya establecida en el registro transversal. En consecuencia, el cierre W10 no altera la taxonomía global de **13 retenciones activas + 5 excepciones finales**. El ledger FTRL canónico se promueve de `LTMD_U1_FTRL_COMPLETION_LEDGER_0.8` a `LTMD_U1_FTRL_COMPLETION_LEDGER_0.9`, con **357 identidades validadas**, **167 pendientes de FTRL**, **13 retenciones activas** y **5 excepciones finales**. La secuencia operacional restante permanece preregistrada como **W11 → W2**.

Este cierre es computacional y archivístico. `ocr_available` no equivale a `text_verified`, y ninguna salida W10 queda promovida a `semantic_ready`.

