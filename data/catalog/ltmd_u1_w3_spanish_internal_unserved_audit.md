# LTMD-U1 W3 — auditoría focal de posiciones internas no servidas Español/Lengua

Versión: `LTMD_U1_W3_SPANISH_INTERNAL_UNSERVED_0.1`.

- Visores parciales auditados: **7**.
- Posiciones internas re-auditadas: **8**.
- Persisten como `internal_unserved_position_observed`: **8**.
- Recuperadas inesperadamente: **0**.
- Inconclusas: **0**.

## Casos
- `H1993P4ES193`: VP236=internal_unserved_position_observed; controles vecinos SHA=OK.
- `H2008P3ES265`: VP17=internal_unserved_position_observed; controles vecinos SHA=OK.
- `H2008P3ES266`: VP206=internal_unserved_position_observed; controles vecinos SHA=OK.
- `H2008P4ES271`: VP129=internal_unserved_position_observed; controles vecinos SHA=OK.
- `H2008P4ES272`: VP77=internal_unserved_position_observed, VP226=internal_unserved_position_observed; controles vecinos SHA=OK.
- `H2011P2ES305`: VP105=internal_unserved_position_observed; controles vecinos SHA=OK.
- `H2014P2ESA`: VP218=internal_unserved_position_observed; controles vecinos SHA=OK.

## Política de corpus
Un hueco digital persistente y local, rodeado por vecinos que reproducen sus SHA persistidos, no invalida todo el libro. El visor puede entrar al OCR con esa posición explícitamente ausente, sin renumerar páginas ni fabricar continuidad. Si una posición reaparece, su hash recuperado se incorpora como suplemento de reconciliación. Un caso inconcluso bloquea únicamente ese visor hasta resolverlo.
