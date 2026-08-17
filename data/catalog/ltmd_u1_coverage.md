# LTMD-U1 — tablero de cobertura técnica

Versión: `LTMD_U1_COVERAGE_0.8`.

Este tablero se recompone desde la cola maestra por `operational_domain` y desde las actas de cierre W1–W7. **Cobertura técnica no equivale a preparación semántica.** En W7, la cobertura técnica registra exclusivamente la cohorte con fuente admitida; las cinco identidades retenidas por fuente continúan fuera de la cobertura efectiva y no se imputan.

## Totales

- Universo U1: **542/542** identidades catalogadas.
- Cobertura técnica efectiva cerrada o resuelta: **329/542 (60.70%)**.
- Objetos canónicos de procesamiento: **298/542 (54.98%)**.
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
| W7 | `civica_etica` | 30 | 25 | 25 | 5 | `partial_with_preserved_source_retentions` |
| W8 | `artes` | 20 | 0 | 0 | 20 | `queued` |
| W9 | `educacion_fisica` | 4 | 0 | 0 | 4 | `queued` |
| W10 | `integrados_multiarea` | 69 | 0 | 0 | 69 | `queued` |
| W11 | `otros_no_clasificados` | 111 | 0 | 0 | 111 | `queued` |

## Lectura correcta

W1, W3, W4, W5 y W6 están cerradas técnicamente. W2 conserva cuatro excepciones de routing sin imputación. **W7 tiene cierre técnico de su cohorte fuente-admitida: 25/30 identidades y 25 objetos canónicos. No constituye un cierre histórico 30/30.** Permanecen retenidas cinco identidades: `H2014P5FCA`, por un hueco interno aislado en la página lógica 104, y `H2018P3FCA`–`H2018P6FCA`, porque sus visores/configuración institucionales están presentes pero el subárbol oficial de activos observado no se sirve. Ninguna de esas cinco identidades se sustituye por similitud, cardinalidad, ciclo o fuente externa no verificada.

W8–W11 permanecen en cola.

`wave_label` no se usa para reconstruir la partición científica porque la cola también codifica estados de ejecución como materialización y aliases; la partición se deriva de `operational_domain`.

`effective_technical_identities` puede incluir identidades documentales cubiertas mediante aliases o rutas demostradas criptográficamente; `canonical_processing_objects` evita duplicar procesamiento de contenido cuando la evidencia de identidad/reutilización lo permite. En W7 no se usa ningún alias para las cinco retenciones de fuente: las 25 identidades efectivas corresponden a 25 objetos procesados directamente.

`WAITING_HUMAN_REFERENCE` sigue vigente. PAGESTRUCT, FRAGSEG y la igualdad de hashes son infraestructura técnica; no validan por sí mismos categorías semánticas, continuidad curricular ni equivalencia pedagógica.
