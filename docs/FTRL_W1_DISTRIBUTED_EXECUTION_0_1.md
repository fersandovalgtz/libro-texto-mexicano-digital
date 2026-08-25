# FTRL W1 — protocolo de ejecución distribuida 0.1

**Estado:** normativo para la recuperación de W1 después del límite temporal del runner hospedado  
**Ámbito:** W1 Ciencias Naturales, LTMD-U1  
**Denominador:** 40 identidades históricas, 36 objetos canónicos, 6,516 páginas fuente

## 1. Motivo técnico

La primera corrida integral W1 ejecutó los 6,516 activos en un único job de GitHub Actions con dos procesos OCR concurrentes. El job alcanzó su límite temporal de 360 minutos mientras Tesseract continuaba procesando páginas y fue cancelado antes de la validación global. Ese resultado es una cancelación operacional, no una validación ni una refutación del corpus.

W1 no puede promoverse desde esa corrida. `cancelled != validated`.

## 2. Cambio de arquitectura

La unidad documental no cambia. La ejecución se distribuye en **16 shards deterministas** que, en conjunto, deben ser una partición exacta y disjunta de las 6,516 páginas canónicas.

El algoritmo de partición es estable:

1. reconstruir el mismo manifiesto exhaustivo W1;
2. seleccionar únicamente JPEG fuente pertenecientes a objetos canónicos técnicamente cubiertos;
3. ordenar por `(catalog_generation, grade_code, viewer_key, source_image_index)`;
4. aplicar partición contigua balanceada en 16 shards.

Con 6,516 páginas, la distribución esperada es cuatro shards de 408 páginas y doce de 407 páginas.

Las olas y shards son logística computacional. No alteran identidad documental, relación de alias, procedencia ni denominador.

## 3. Validación de cada shard

Cada shard debe, dentro de su propio runner:

- descargar cada activo y comprobar su SHA-256 preregistrado;
- producir OCR por página con la misma versión de pipeline, idioma y PSM;
- construir un SQLite con FTS5 para ese shard;
- validar JSONL contra SQLite y hashes internos de OCR/search text;
- construir QC y resumen text-free;
- generar un manifiesto text-free de ejecución;
- demostrar que las páginas OCR corresponden exactamente a la partición fuente asignada.

Un shard sólo adquiere `status=validated` si todos esos gates pasan.

## 4. Seguridad

El repositorio es público. Por tanto, los productos restringidos de cada shard —OCR JSONL, SQLite y cualquier derivado restringido— nunca se cargan en texto claro.

Antes de salir del runner:

1. se empaquetan los productos restringidos;
2. se genera una contraseña aleatoria;
3. el paquete se cifra con AES-256-CBC + PBKDF2-SHA256;
4. la contraseña se envuelve con la clave pública RSA-4096 del proyecto mediante OAEP/SHA-256;
5. se elimina el paquete sin cifrar y la contraseña en claro;
6. Actions recibe únicamente el payload cifrado, la clave envuelta, checksums y un manifiesto text-free.

La clave privada permanece fuera de GitHub.

## 5. Gate de unión exhaustiva

Después de validar los 16 shards, un job agregador descarga exclusivamente las evidencias text-free y reconstruye por separado el manifiesto esperado W1.

El gate global exige simultáneamente:

- índices de shard exactamente `0..15`;
- una sola revisión Git y un solo run para todos los shards;
- 6,516 registros en total;
- 6,516 hashes únicos de identidad de página;
- igualdad de conjuntos entre los hashes observados y los derivados del manifiesto canónico;
- integridad SQLite `ok` en todos los shards;
- cardinalidad FTS igual a cardinalidad OCR en todos los shards;
- cardinalidad QC igual a cardinalidad OCR en todos los shards;
- ausencia de OCR/search text en la evidencia pública.

La suma aritmética de páginas por sí sola no demuestra exhaustividad: se exige igualdad del universo de páginas.

## 6. Estados

La ejecución distribuida introduce un estado técnico explícito:

`distributed_computationally_validated`

Significa que los 16 shards y su unión documental pasaron los gates anteriores. No equivale todavía a cierre archivístico:

`distributed_computationally_validated != archival_complete`.

Tampoco modifica:

- `ocr_available != text_verified`;
- `corpus_ready != semantic_ready`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`.

## 7. Consolidación privada

Los handoffs cifrados exitosos se trasladan al Google Drive privado canónico. En un entorno privado autorizado se descifran y se ejecuta `scripts/consolidate_ftrl_w1_distributed.py`.

La consolidación:

- reúne los 16 JSONL sin duplicados;
- compara nuevamente la unión contra las 6,516 páginas fuente;
- ordena canónicamente los registros;
- construye el JSONL completo;
- construye SQLite/FTS5 completo;
- valida integridad y cardinalidades;
- genera QC completo y manifiesto de corrida;
- emite evidencia text-free de consolidación.

Los productos completos consolidados deben cifrarse y preservarse persistentemente en Drive. Sólo después de verificar la copia y sus SHA-256 puede W1 alcanzar `archival_complete=yes`.

## 8. Regla de promoción

W3 continúa bloqueado hasta que W1 cumpla todos estos estados verificables:

1. 16/16 shards validados;
2. unión distribuida 6,516/6,516 validada;
3. 16/16 handoffs cifrados copiados y verificados en Drive;
4. consolidación privada completa validada;
5. archivo consolidado persistente verificado;
6. ledger y evidencia pública actualizados sin promover validación semántica.

La cancelación de la corrida monolítica anterior permanece como evidencia histórica y no se borra ni se reinterpreta como éxito.
