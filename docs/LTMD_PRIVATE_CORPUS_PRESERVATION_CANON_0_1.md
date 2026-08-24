# Canon de preservación privada del corpus FTRL — 0.1

**Fecha:** 24 de agosto de 2026  
**Estado:** normativo para LTMD-U1  
**Ámbito:** productos restringidos derivados del procesamiento FTRL  
**Bóveda canónica:** espacio privado de Google Drive bajo control del responsable del proyecto; sus identificadores y enlaces no se publican en este repositorio.

## 1. Regla canónica

LTMD separa de manera obligatoria la **infraestructura pública reproducible** de los **productos restringidos completos** generados durante el procesamiento. GitHub conserva código, protocolos, contratos, hashes, cardinalidades y evidencia agregada `text-free`. El corpus OCR completo, las bases SQLite/FTS5, las colas detalladas de QC y otros derivados extensos que no deban redistribuirse públicamente se conservan de manera persistente en la bóveda privada de Google Drive del proyecto.

La reconstruibilidad local deja de ser, por sí sola, la política de preservación. A partir de este canon, los productos restringidos deben ser **reconstruibles y además archivados**.

## 2. Dos estados distintos

Cada corrida integral FTRL debe distinguir al menos:

- `computationally_validated`: la corrida pasó sus gates técnicos de fuente, OCR, cardinalidad, SQLite/FTS5, integridad, procedencia y QC;
- `archival_complete`: los productos restringidos de esa corrida fueron copiados a la bóveda privada, se registraron sus checksums y la copia fue verificada.

`computationally_validated` no implica `archival_complete`. Una corrida no debe presentarse como archivísticamente cerrada mientras sus productos completos sólo existan en un filesystem efímero de CI.

Esta distinción tampoco modifica las desigualdades epistemológicas vigentes:

- `corpus_ready != semantic_ready`;
- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`.

## 3. Productos mínimos que deben preservarse

Por cada corrida integral, cuando existan, se conservarán:

1. corpus OCR por página (`JSONL` o formato sucesor explícitamente versionado);
2. base SQLite con índice FTS5;
3. cola detallada de control de calidad;
4. manifiesto normalizado de activos fuente utilizado por la corrida;
5. inventario de procesamiento e identidades;
6. manifiesto agregado de ejecución `text-free`;
7. resumen agregado de QC `text-free`;
8. checksums SHA-256 de los archivos archivados;
9. metadatos mínimos de procedencia: ola, `run_id`, commit Git, fecha UTC, esquema, cardinalidad esperada/procesada y estado de validación.

Las imágenes fuente completas sólo se preservarán cuando sea jurídicamente y operativamente adecuado. Este canon no amplía derechos de redistribución sobre SEP, CONALITEG o terceros.

## 4. Estructura lógica de almacenamiento

La bóveda privada se organiza así:

```text
LTMD-U1 — corpus FTRL privado/
  00_CANON_y_manifiestos/
  W1 — Ciencias Naturales/
  W2 — Matemáticas/
  W3 — Español y Lengua/
  W4 — Ciencias Sociales/
  W5 — Historia/
  W6 — Geografía y Atlas/
  W7 — Formación Cívica y Ética/
  W8 — Artes/
  W9 — Educación Física/
  W10 — Integrados y Multiarea/
  W11 — Otros y No clasificados/
```

Cada ejecución se conserva en una carpeta inmutable de la forma:

```text
run_<run_id>__<short_commit>__<YYYY-MM-DD>/
  01_OCR_por_pagina/
  02_SQLite_FTS5/
  03_QC_detallado/
  04_Manifiestos_y_procedencia/
  05_Checksums_y_evidencia/
```

No se sobrescribe una corrida previa. Una nueva reconstrucción produce una nueva carpeta de corrida aunque la cohorte lógica sea la misma.

## 5. Seguridad y tránsito

El repositorio es público. Por tanto:

- nunca se versionará la clave privada de archivo;
- nunca se publicará OCR íntegro, SQLite, snippets extensos o QC detallado en commits, releases, issues o logs;
- los artefactos de GitHub Actions que contengan productos restringidos sólo podrán utilizarse como puente si el contenido está cifrado antes de la carga;
- el repositorio sólo contiene la **clave pública** de preservación (`security/ltmd_archive_public.pem`);
- la clave privada correspondiente permanece fuera de GitHub, en almacenamiento privado bajo control del proyecto;
- cualquier paquete temporal cifrado debe tener retención breve y sus checksums deben conservarse con la copia de Drive.

El cifrado de tránsito no sustituye la verificación de integridad. Cada archivo o paquete archivado debe conservar SHA-256 verificable.

## 6. Handoff cifrado desde CI

Cuando una corrida se ejecute en GitHub Actions y no exista una ruta autenticada directa hacia Google Drive, el puente permitido es:

1. generar los productos restringidos bajo `local/`;
2. validar la corrida completamente;
3. empaquetar únicamente los productos restringidos que deban conservarse;
4. generar una contraseña aleatoria de alta entropía;
5. cifrar el paquete con AES-256 y PBKDF2;
6. cifrar la contraseña con la clave pública RSA del proyecto usando OAEP/SHA-256;
7. eliminar del workspace el paquete sin cifrar y la contraseña en claro antes de cualquier carga;
8. cargar a Actions sólo el paquete cifrado, la contraseña envuelta y checksums no sensibles;
9. trasladar ese handoff cifrado a la bóveda privada de Google Drive;
10. verificar tamaño y SHA-256 en destino antes de declarar `archival_complete`.

El artefacto temporal cifrado no es el archivo canónico: Google Drive es el destino persistente.

## 7. Regla retroactiva

Este canon se aplica también a las corridas integrales anteriores. Si una ola fue validada técnicamente pero sus productos restringidos completos quedaron únicamente en almacenamiento efímero, deberá:

- recuperarlos si todavía existe una copia privada verificable; o
- reconstruir la corrida bajo el mismo commit/protocolo o una reconstrucción explícitamente equivalente y preservarla.

En particular, W5 Historia y la primera corrida exhaustiva W1 deben recibir una copia persistente verificable antes de considerarse `archival_complete`.

## 8. Evidencia pública permitida

GitHub puede publicar, sin exponer el corpus completo:

- contratos de alcance;
- manifiestos agregados `text-free`;
- hashes de activos y de paquetes archivados;
- cardinalidades;
- estadísticas QC agregadas;
- identificadores de workflow/run y commit;
- estado `archival_complete=yes/no` y fecha de verificación;
- nombre lógico de la ola y de la carpeta de corrida, pero **no** IDs, enlaces privados, credenciales o claves privadas de Google Drive.

## 9. Criterio de cierre archivístico

Una corrida alcanza `archival_complete=yes` únicamente cuando existe evidencia de que:

- el paquete o archivos restringidos esperados fueron preservados en la bóveda privada;
- la copia está asociada inequívocamente a `run_id` y commit;
- los SHA-256 coinciden con los generados en origen;
- el destino permanece privado;
- la clave necesaria para descifrar un handoff cifrado está preservada separadamente y fuera del repositorio público.

La ausencia de copia persistente es deuda técnica obligatoria, no un detalle opcional.

## 10. Relación con el protocolo exhaustivo

Este documento complementa `FTRL_U1_EXHAUSTIVE_EXECUTION_PROTOCOL_0_2.md`. El protocolo 0.2 gobierna **qué identidades y páginas deben procesarse**; este canon gobierna **cómo se preservan de forma persistente los productos completos resultantes**.

Ninguno sustituye al otro.
