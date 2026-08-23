# LTMD-U1 — estado técnico derivado por máquina

Versión: `LTMD_U1_TECHNICAL_STATUS_0.3`.

Corte de referencia: **23 de agosto de 2026**.

Este documento resume el estado técnico transversal de LTMD-U1 a partir del tablero canónico `data/catalog/ltmd_u1_coverage.md` y de las actas de cierre por ola. No convierte la disponibilidad de una capa técnica en validación semántica y no sustituye los reportes detallados de cada cohorte.

## Frontera epistemológica vigente

El proyecto opera todavía sin referencia humana incorporada al tablero U1. OCR, PAGESTRUCT, FRAGSEG, hashes exactos, procedencia y dependencia documental pueden cerrar técnicamente una cohorte; CER/WER validado contra referencia, confiabilidad intercodificador, consenso humano y validación semántica permanecen separados. `WAITING_HUMAN_REFERENCE` continúa vigente.

## Estado agregado

| indicador | estado |
|---|---:|
| Universo histórico operativo | **542/542** |
| Cobertura técnica efectiva cerrada o resuelta | **524/542 (96.68%)** |
| Objetos canónicos de procesamiento cerrados | **492/542 (90.77%)** |
| Residual fuera de cobertura efectiva | **18/542 (3.32%)** |
| Retenciones activas | **13/542 (2.40%)** |
| Excepciones técnicas finales | **5/542 (0.92%)** |
| Validación semántica humana incorporada | **0/542** |

`effective_technical_identities` puede incluir identidades documentales cubiertas mediante relaciones de fuente o aliases demostrados. `canonical_processing_objects` evita reprocesamiento redundante cuando existe evidencia suficiente, sin borrar identidades históricas.

## Estado por ola

| ola | dominio operacional | plan | efectiva | canónicos | residual | ciclo residual | estado técnico |
|---|---|---:|---:|---:|---:|---|---|
| W1 | `ciencias_naturales` | 40 | 40 | 36 | 0 | — | `closed` |
| W2 | `matematicas` | 64 | 60 | 57 | 4 | 4 activas | `partial_with_preserved_exceptions` |
| W3 | `espanol_lengua` | 130 | 130 | 114 | 0 | — | `closed` |
| W4 | `ciencias_sociales` | 14 | 14 | 14 | 0 | — | `closed` |
| W5 | `historia` | 18 | 18 | 15 | 0 | — | `closed` |
| W6 | `geografia_atlas` | 42 | 42 | 37 | 0 | — | `closed` |
| W7 | `civica_etica` | 30 | 25 | 25 | 5 | 5 activas | `source_admitted_cohort_closed_with_retentions` |
| W8 | `artes` | 20 | 16 | 16 | 4 | 4 activas | `source_admitted_cohort_closed_with_retentions` |
| W9 | `educacion_fisica` | 4 | 4 | 4 | 0 | — | `closed` |
| W10 | `integrados_multiarea` | 69 | 68 | 68 | 1 | 1 final | `source_admitted_cohort_closed_with_retentions` |
| W11 | `otros_no_clasificados` | 111 | 107 | 106 | 4 | 4 finales | `source_admitted_cohort_closed_with_retentions` |

## Residual de fuente

Las **18 identidades** fuera de la cobertura técnica efectiva están consolidadas en `data/catalog/ltmd_u1_retained_source_register.csv` y explicadas en `docs/LTMD_U1_RETAINED_SOURCE_REGISTER.md`.

Trece permanecen como `active_retention` y constituyen trabajo técnico abierto: cuatro W2, cinco W7 y cuatro W8. Las otras cinco ya son `final_exception`: `H2014P1ENA` en W10 y cuatro identidades W11 (`H2014P1EAM`, `H2014P2EAM`, `H2014P3COL`, `H2014P3MOR`). Sus issues especializados #11, #13 y #14 cerraron la investigación disponible de fuente mediante búsquedas acotadas y reproducibles sin recuperación admisible.

Una excepción final no se considera cubierta ni procesada. Permanece en el residual U1 para que la cifra 524/542 no oculte límites de fuente, pero deja de tratarse como trabajo ordinario pendiente. Sólo debe reabrirse si aparece evidencia institucional o archivística nueva con correspondencia suficiente.

## Actas de cierre y evidencia

Las actas y reportes por ola conservan el detalle de auditoría de activos, admisibilidad, topología canónica, OCR, PAGESTRUCT, FRAGSEG, reutilización exacta y excepciones. La vista agregada autoritativa para numeradores y denominadores es `data/catalog/ltmd_u1_coverage.md`; el plan vigente es `docs/LTMD_U1_MASTER_PLAN_0_3.md`.

La integridad de la superficie pública derivada se controla adicionalmente mediante `data/catalog/ltmd_u1_evidence_integrity.csv` y `docs/LTMD_U1_EVIDENCE_INTEGRITY.md`, con SHA-256 y tamaño por artefacto.

## Regla de lectura

Los estados técnicos anteriores son controles de infraestructura científica. `text_detected` no equivale a exactitud OCR validada; las clases PAGESTRUCT son estructurales; los tipos FRAGSEG son candidatos técnicos; y la igualdad de hash sólo documenta igualdad dentro de la representación correspondiente. Ninguna de estas capas sustituye por sí misma la referencia humana necesaria para afirmaciones semánticas, pedagógicas o históricas sustantivas.
