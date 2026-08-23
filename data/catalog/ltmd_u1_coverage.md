# LTMD-U1 — tablero de cobertura técnica

Versión: `LTMD_U1_COVERAGE_0.13`.

Este tablero se recompone desde la cola maestra por `operational_domain` y desde las actas/cortes técnicos W1–W11. **Cobertura técnica no equivale a preparación semántica ni a fase de ejecución.** Una ola puede encontrarse activamente en procesamiento y seguir aportando cero al numerador hasta cumplir su cierre técnico.

## Totales

- Universo U1: **542/542** identidades catalogadas.
- Cobertura técnica efectiva cerrada o resuelta: **417/542 (76.94%)**.
- Objetos canónicos de procesamiento cerrados: **386/542 (71.22%)**.
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
| W9 | `educacion_fisica` | 4 | 4 | 4 | 0 | `closed` |
| W10 | `integrados_multiarea` | 69 | 68 | 68 | 1 | `source_admitted_cohort_closed_with_retentions` |
| W11 | `otros_no_clasificados` | 111 | 0 | 0 | 111 | `ocr_complete_pagestruct_pending` |

## Lectura correcta

W1, W3, W4, W5 y W6 están cerradas técnicamente. W2 conserva cuatro excepciones de routing sin imputación. W7 tiene cierre técnico de su cohorte fuente-admitida: 25/30 identidades y cinco retenciones explícitas. W8 tiene cierre técnico de su cohorte fuente-admitida: 16/20 identidades y cuatro retenciones explícitas. W9 está cerrada técnicamente en 4/4 identidades y cuatro objetos canónicos. W10 cerró técnicamente su cohorte fuente-admitida en 68/69 identidades y 68 objetos canónicos; las retenciones permanecen explícitas. W11 está activa en `ocr_complete_pagestruct_pending` con evidencia `docs/LTMD_U1_W11_OCR.md`, pero aporta 0/111 al numerador hasta completar una cadena técnica defendible.

`wave_label` no se usa para reconstruir la partición científica porque la cola también codifica estados de ejecución; la partición se deriva de `operational_domain`.

`effective_technical_identities` puede incluir identidades documentales cubiertas mediante aliases o rutas demostradas criptográficamente; `canonical_processing_objects` evita duplicar procesamiento de contenido cuando la evidencia de identidad/reutilización lo permite. Las retenciones de fuente no se sustituyen por aliases heurísticos.

`WAITING_HUMAN_REFERENCE` sigue vigente. OCR, PAGESTRUCT, FRAGSEG y la igualdad de hashes son infraestructura técnica; no validan por sí mismos categorías semánticas, continuidad curricular ni equivalencia pedagógica.
