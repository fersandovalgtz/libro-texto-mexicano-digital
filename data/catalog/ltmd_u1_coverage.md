# LTMD-U1 — tablero de cobertura técnica

Versión: `LTMD_U1_COVERAGE_0.9`.

Este tablero se recompone desde la cola maestra por `operational_domain` y desde las actas/cortes técnicos W1–W9. **Cobertura técnica no equivale a preparación semántica.** La promoción de W9 al numerador sólo ocurre cuando existe y pasa su acta de cierre técnico reproducible.

## Totales

- Universo U1: **542/542** identidades catalogadas.
- Cobertura técnica efectiva cerrada o resuelta: **345/542 (63.65%)**.
- Objetos canónicos de procesamiento cerrados: **314/542 (57.93%)**.
- Cobertura semántica humana validada incorporada al tablero: **0/542**.

## Por ola

| ola | dominio operacional | plan | efectiva | canónicos | restantes | estado |
|---|---|---:|---:|---:|---:|---|
| W1 | `ciencias_naturales` | 40 | 40 | 36 | 0 | `closed` |
| W2 | `matematicas` | 64 | 60 | 57 | 4 | `partial_with_preserved_exceptions` |
| W3 | `espanol_lengua` | 130 | 130 | 114 | 0 | `closed` |
| W4 | `ciencias_sociales` | 14 | 14 | 14 | 0 | `closed` |
| W5 | `historia` | 18 | 18 | 15 | 0 | `closed` |
| W6 | `geografia_atlas` | 42 | 42 | 37 | 0 | `closed` |
| W7 | `civica_etica` | 30 | 25 | 25 | 5 | `source_admitted_cohort_closed_with_retentions` |
| W8 | `artes` | 20 | 16 | 16 | 4 | `source_admitted_cohort_closed_with_retentions` |
| W9 | `educacion_fisica` | 4 | 0 | 0 | 4 | `ocr_complete_downstream_pending` |
| W10 | `integrados_multiarea` | 69 | 0 | 0 | 69 | `queued` |
| W11 | `otros_no_clasificados` | 111 | 0 | 0 | 111 | `queued` |

## Lectura correcta

W1, W3, W4, W5 y W6 están cerradas técnicamente. W2 conserva cuatro excepciones de routing sin imputación. W7 tiene cierre técnico de su cohorte fuente-admitida: 25/30 identidades y cinco retenciones explícitas. W8 tiene cierre técnico de su cohorte fuente-admitida: 16/20 identidades y cuatro retenciones explícitas. W9 conserva 4/4 fuentes canónicas y OCR SHA-verificado, pero permanece fuera del numerador principal hasta completar PAGESTRUCT, FRAGSEG, reutilización exacta y el cierre técnico. W10–W11 permanecen en cola.

`wave_label` no se usa para reconstruir la partición científica porque la cola también codifica estados de ejecución; la partición se deriva de `operational_domain`.

`effective_technical_identities` puede incluir identidades documentales cubiertas mediante aliases o rutas demostradas criptográficamente; `canonical_processing_objects` evita duplicar procesamiento de contenido cuando la evidencia de identidad/reutilización lo permite. En W7 y W8 las retenciones de fuente no se sustituyen por aliases heurísticos.

`WAITING_HUMAN_REFERENCE` sigue vigente. OCR, PAGESTRUCT, FRAGSEG y la igualdad de hashes son infraestructura técnica; no validan por sí mismos categorías semánticas, continuidad curricular ni equivalencia pedagógica.
