# LTMD U1 — FTRL completion ledger 0.5

**Estado efectivo:** 2026-08-27  
**Ámbito de esta versión:** promoción de W4 Ciencias Sociales después de validación computacional exhaustiva y cierre archivístico privado verificado.

## Resultado

`LTMD_U1_FTRL_COMPLETION_LEDGER_0.5` incorpora W4 a la cohorte FTRL cerrada sin modificar el universo documental U1 ni los estados de las fuentes retenidas.

La promoción se apoya en la corrida distribuida W4 `33033136922`, commit fuente `455e0f21434162c4b77a0b5d52269b65512c486d`:

- 14 identidades históricas;
- 14 objetos canónicos de procesamiento;
- 2,414 páginas fuente canónicas;
- 8 shards exhaustivos;
- unión global exacta y única 2,414/2,414;
- SQLite/FTS5 íntegro y cardinal al corpus por shard;
- QC técnico cardinal a 2,414 páginas;
- 0 huecos persistentes de fuente dentro de la cohorte W4.

La preservación privada fue completada conforme al canon FTRL: los ocho handoffs cifrados fueron preservados, redescargados y verificados contra los digests de la corrida; los productos restringidos se descifraron únicamente en entorno privado para comprobar estructura, checksums, SQLite/FTS5 y QC; posteriormente se produjo una copia consolidada privada única, se preservó en la bóveda y se volvió a descargar para comprobar su SHA-256. La evidencia pública conserva únicamente metadatos, hashes y agregados no sustitutivos.

El registro público de cierre es `data/research/ltmd_u1_w4_archival_closure.json`. No contiene IDs de Drive, URLs privadas, claves ni OCR íntegro.

## Estado global U1 después de W4

El generador `scripts/build_ltmd_u1_ftrl_completion_ledger_v5.py` deriva y CI comprueba los siguientes invariantes:

- universo documental: **542** identidades;
- FTRL `validated` + `archival_complete`: **244** identidades;
- objetos canónicos FTRL validados: **216**;
- páginas fuente canónicas bajo FTRL validado: **37,606**;
- excepciones finales documentadas: **5**;
- retenciones activas: **13**;
- identidades procesables aún pendientes: **280**;
- disposición terminal estricta: **249/542**;
- identidades restantes: **293**.

Las 13 retenciones activas y las 5 excepciones finales permanecen exactamente en su ciclo documental previo. Esta versión no resuelve ni reclasifica fuentes.

## Límites epistemológicos

W4 queda cerrado en sentido computacional y archivístico. Esto no implica verificación humana del OCR, validación del libro de códigos ni interpretación histórica de los contenidos.

Se mantienen obligatoriamente:

- `ocr_available != text_verified`;
- `corpus_ready != semantic_ready`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`;
- `computationally_validated != semantic_validated`.

Por tanto, después de esta promoción:

- `text_verified = 0/542`;
- `semantic_ready = 0/542`.

## Secuencia operativa

La secuencia preregistrada del issue #64 continúa con **W9 Educación Física**, seguida de W7, W8, W10, W11 y W2. W2 permanece al final por sus excepciones activas de cobertura.

La versión 0.5 no expande U1 y no autoriza incorporar nuevas identidades históricas sin abrir una versión/universo documental separado.
