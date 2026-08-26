# LTMD-U1 — ledger exhaustivo de completitud FTRL 0.4

La versión 0.4 promueve **W6 Geografía/Atlas** únicamente después de dos cierres independientes: validación computacional exhaustiva y preservación archivística privada. El denominador documental permanece inalterado en **542 identidades**.

## Cambio respecto de 0.3

W6 pasa de `pending` a `validated` para sus 42 identidades, con 37 objetos canónicos y 5,258 páginas. La corrida distribuida `32908105382` demostró una unión exacta y única de 16 shards. La consolidación privada reconstruyó 5,258 registros y validó SQLite/FTS5 con integridad `ok` y 5,258 filas FTS. Los 16 handoffs cifrados quedaron preservados en almacenamiento privado persistente y fueron re-descargados; sus SHA-256 coincidieron con los digests originales de GitHub Actions.

Durante la reanudación de carga se detectaron 12 copias redundantes de los shards 0–11. Fueron eliminadas antes del cierre, dejando exactamente 16 handoffs únicos. Este saneamiento no alteró ningún producto canónico ni sus hashes.

La promoción **no** modifica los límites epistemológicos: `ocr_available != text_verified` y `corpus_ready != semantic_ready`. W6 conserva `text_verified=0` y `semantic_ready=0`.

## Estado exhaustivo tras W6

- Universo fijo: 542 identidades.
- `required_ftrl_processing`: 524.
- `active_retention`: 13.
- `final_exception`: 5.
- FTRL validado y archivísticamente cerrado: 230 identidades (W1 + W3 + W5 + W6).
- Disposición terminal estricta: 235/542 identidades (230 validadas + 5 excepciones finales), **43.4%**.
- Restan 307/542 identidades, **56.6%**: 294 procesables pendientes y 13 retenciones activas.
- Objetos canónicos validados: 202.
- Páginas fuente canónicas validadas: 35,192.

El cierre global continúa siendo inelegible mientras existan olas FTRL pendientes o retenciones activas.
