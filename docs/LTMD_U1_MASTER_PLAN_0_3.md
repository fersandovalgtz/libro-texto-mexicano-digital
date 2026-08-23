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
- identidades retenidas por deuda de fuente: **18/542 (3.32%)**;
- validación semántica humana incorporada al tablero: **0/542**.

La diferencia entre 524 identidades efectivamente cubiertas y 492 objetos canónicos no es una pérdida: refleja aliases y relaciones de identidad/reutilización técnicamente demostradas que evitan duplicar procesamiento sin borrar identidades históricas.

## 3. Estado por ola

| ola | dominio operacional | plan | cobertura efectiva | canónicos | retenciones | estado |
|---|---|---:|---:|---:|---:|---|
| W1 | Ciencias Naturales | 40 | 40 | 36 | 0 | cerrada |
| W2 | Matemáticas | 64 | 60 | 57 | 4 | cierre parcial con excepciones preservadas |
| W3 | Español / Lengua | 130 | 130 | 114 | 0 | cerrada |
| W4 | Ciencias Sociales | 14 | 14 | 14 | 0 | cerrada |
| W5 | Historia | 18 | 18 | 15 | 0 | cerrada |
| W6 | Geografía / Atlas | 42 | 42 | 37 | 0 | cerrada |
| W7 | Formación Cívica y Ética | 30 | 25 | 25 | 5 | cohorte fuente-admitida cerrada |
| W8 | Artes | 20 | 16 | 16 | 4 | cohorte fuente-admitida cerrada |
| W9 | Educación Física | 4 | 4 | 4 | 0 | cerrada |
| W10 | Integrados / Multiarea | 69 | 68 | 68 | 1 | cohorte fuente-admitida cerrada |
| W11 | Otros / No clasificados | 111 | 107 | 106 | 4 | cohorte fuente-admitida cerrada |
| **Total** |  | **542** | **524** | **492** | **18** |  |

La taxonomía por ola es logística y operacional. No constituye una ontología curricular ni autoriza inferencias históricas por sí sola.

## 4. Registro transversal de las 18 retenciones

La deuda técnica residual ya no se gestiona únicamente en documentos dispersos. `data/catalog/ltmd_u1_retained_source_register.csv` mantiene una fila por identidad retenida y `docs/LTMD_U1_RETAINED_SOURCE_REGISTER.md` documenta sus clases, evidencia admisible y reglas de cierre.

Distribución vigente:

- W2 Matemáticas: **4** identidades — issue #4;
- W7 Formación Cívica y Ética: **5** — issue #5;
- W8 Artes: **4** — issue #9;
- W10 Integrados / Multiarea: **1** — issue #11;
- W11 Otros / No clasificados: **4** — issues #13 y #14.

El validador `scripts/validate_u1_retained_source_register.py` exige que el número de filas del registro sea igual a `universo U1 - cobertura técnica efectiva` y que la distribución por ola coincida con la columna `restantes` del tablero.

## 5. Política para resolver retenciones

Una retención sólo puede levantarse mediante evidencia reproducible suficiente. Según el caso, son admisibles:

- ruta institucional efectiva del activo o secuencia faltante;
- captura archivada de la misma representación con correspondencia posicional inequívoca;
- relación institucional/documental explícita de reutilización;
- identidad byte-exacta demostrada criptográficamente con otra representación servida.

Deben preservarse URI o identificador archivístico, posición, tamaño, SHA-256, timestamp, procedencia y decisión de admisibilidad cuando correspondan.

No son suficientes por sí solos título, año, grado, cardinalidad, cercanía de identificador, similitud visual, OCR, parecido textual o pertenencia a una misma serie editorial. Estas señales pueden orientar investigación, pero no crean identidad documental.

## 6. Cierre técnico no significa 100% de activos servidos

El criterio de cierre U1 no exige ocultar excepciones para producir una cifra artificial de 542/542 procesados. Una identidad puede alcanzar estado técnico final como excepción documentada cuando una búsqueda acotada y reproducible no permita reconstruir su fuente sin imputación.

Por tanto, el proyecto debe distinguir:

- **cobertura efectiva**, cuando existe fuente o representación técnicamente admisible;
- **objeto canónico**, cuando existe una unidad real de procesamiento;
- **retención activa**, cuando la evidencia aún puede investigarse;
- **excepción técnica final**, cuando la ausencia o ambigüedad queda cerrada como resultado auditable.

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

### P1 — residual de fuentes

Investigar las 18 retenciones mediante búsquedas acotadas, reproducibles y documentadas. Promover únicamente casos con cadena de evidencia suficiente. Si una búsqueda razonable termina sin resolución, convertir la retención en excepción técnica final explícita en vez de prolongarla indefinidamente.

### P2 — consistencia transversal

Mantener sincronizados tablero, README, plan maestro, issues, manifiestos de integridad y metadatos científicos. Cualquier cifra pública de cobertura debe proceder del tablero canónico o ser comprobable contra él.

### P3 — corte de release posterior a U1

Preparar una nueva candidata de release sólo cuando la superficie pública sea coherente y las excepciones residuales tengan estado claro. La release debe congelar un corte; no perseguir continuamente `main`.

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
