# LTMD-U1 — tablero de cobertura técnica

Versión: `LTMD_U1_COVERAGE_0.6`.

Este tablero se recompone desde la cola maestra por `operational_domain` y desde las actas de cierre W1–W5. **Cobertura técnica no equivale a preparación semántica.**

## Totales

- Universo U1: **542/542** identidades catalogadas.
- Cobertura técnica efectiva cerrada o resuelta: **262/542 (48.34%)**.
- Objetos canónicos de procesamiento: **236/542 (43.54%)**.
- Cobertura semántica humana validada incorporada al tablero: **0/542**.

## Por ola

| ola | dominio operacional | plan | efectiva | canónicos | restantes | estado |
|---|---|---:|---:|---:|---:|---|
| W1 | `ciencias_naturales` | 40 | 40 | 36 | 0 | `closed` |
| W2 | `matematicas` | 64 | 60 | 57 | 4 | `partial_with_preserved_exceptions` |
| W3 | `espanol_lengua` | 130 | 130 | 114 | 0 | `closed` |
| W4 | `ciencias_sociales` | 14 | 14 | 14 | 0 | `closed` |
| W5 | `historia` | 18 | 18 | 15 | 0 | `closed` |
| W6 | `geografia_atlas` | 42 | 0 | 0 | 42 | `source_first_active` |
| W7 | `civica_etica` | 30 | 0 | 0 | 30 | `queued` |
| W8 | `artes` | 20 | 0 | 0 | 20 | `queued` |
| W9 | `educacion_fisica` | 4 | 0 | 0 | 4 | `queued` |
| W10 | `integrados_multiarea` | 69 | 0 | 0 | 69 | `queued` |
| W11 | `otros_no_clasificados` | 111 | 0 | 0 | 111 | `queued` |

## Lectura correcta

W1, W3, W4 y W5 están cerradas técnicamente. W2 conserva cuatro excepciones de routing sin imputación. W6 está activo únicamente en source-first y por ello todavía no suma identidades a la cobertura técnica efectiva. W7–W11 permanecen en cola.

`wave_label` no se usa para reconstruir la partición científica porque la cola también codifica estados de ejecución como materialización y aliases; la partición se deriva de `operational_domain`.

`effective_technical_identities` puede incluir identidades documentales cubiertas mediante aliases o rutas demostradas criptográficamente; `canonical_processing_objects` evita duplicar procesamiento de contenido cuando la evidencia de identidad/reutilización lo permite.

`WAITING_HUMAN_REFERENCE` sigue vigente. PAGESTRUCT, FRAGSEG y la igualdad de hashes son infraestructura técnica; no validan por sí mismos categorías semánticas, continuidad curricular ni equivalencia pedagógica.
