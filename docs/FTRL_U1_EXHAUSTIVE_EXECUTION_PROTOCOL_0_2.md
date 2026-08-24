# Protocolo exhaustivo FTRL LTMD-U1 — 0.2

**Fecha:** 24 de agosto de 2026  
**Estado:** normativo para el escalamiento FTRL de LTMD-U1  
**Universo congelado:** 542 identidades documentales (`viewer_key`) censadas en `data/catalog/ltmd_u1_coverage.csv`  
**Sustituye:** el criterio de cierre por cohorte fuente-admitida de `FTRL_U1_SCALING_ROADMAP_0_1.md`

## 1. Regla rectora

FTRL-U1 se ejecutará de manera exhaustiva sobre el universo completo de LTMD-U1. La unidad de exhaustividad es la **identidad documental histórica**, no solamente el objeto canónico con fuente disponible ni la ola que resulte más sencilla de procesar.

> **Las 542 identidades deben permanecer en el denominador, recibir una disposición técnica explícita y auditable y ser recorridas por el protocolo. Ninguna identidad puede desaparecer por ausencia de fuente, alias, retención, excepción, materia, año, calidad OCR o conveniencia operativa.**

El procesamiento puede evitar duplicación de bytes cuando existe una relación criptográfica/documental demostrada, pero nunca puede borrar la identidad histórica que representa esos bytes.

## 2. Dos sentidos de “procesar todos los libros”

El mandato exhaustivo tiene dos capas simultáneas:

1. **Exhaustividad documental 542/542.** Cada `viewer_key` del universo maestro debe terminar con un estado FTRL explícito.
2. **Exhaustividad computacional de fuente.** Toda identidad con representación fuente admisible debe quedar cubierta por un objeto canónico procesado; todas sus páginas fuente admitidas deben atravesar verificación SHA-256, OCR, validación de corpus, indexación FTS5, procedencia y control de calidad.

Cuando dos o más identidades sean byte-exactas o estén cubiertas por una relación técnica demostrada, el OCR puede ejecutarse una sola vez sobre el objeto canónico. Las identidades relacionadas deben conservarse en el índice de identidades y en los conteos históricos. **No re-OCRizar bytes idénticos no constituye omisión.**

Cuando una identidad carezca de fuente reproduciblemente admisible, no se fabricará OCR ni se sustituirá por una fuente heurística. Esa identidad continúa dentro de 542 y debe permanecer como retención activa o excepción técnica final según evidencia documentada.

## 3. Universo y estado de partida

El corte vigente contiene:

- 542 identidades documentales en el universo LTMD-U1;
- 524 identidades con cobertura técnica efectiva cerrada o resuelta;
- 18 identidades fuera de cobertura efectiva;
- de esas 18, 13 son `active_retention` y 5 son `final_exception`;
- 492 objetos canónicos de procesamiento en el corte técnico general, cifra distinta del número de identidades porque las relaciones demostradas evitan duplicación.

Estas cifras describen el estado inicial del protocolo 0.2; no son metas suficientes de cierre FTRL.

## 4. Estados exhaustivos por identidad

Cada una de las 542 identidades debe pertenecer exactamente a una de estas disposiciones de alcance global:

- `required_ftrl_processing`: tiene fuente o representación técnicamente admisible y, por tanto, debe quedar cubierta por FTRL;
- `active_retention`: la fuente todavía no está resuelta de manera reproducible y la investigación técnica sigue abierta;
- `final_exception`: una investigación acotada y reproducible terminó sin fuente admisible; la imposibilidad documentada es el resultado técnico de esa identidad.

No se admite un cuarto estado implícito como “omitido”, “fuera de alcance”, “pendiente no registrado”, “no prioritario” o equivalente.

Una identidad sólo puede pasar de `active_retention` a:

- `required_ftrl_processing`, si aparece evidencia suficiente para admitir una representación y procesarla; o
- `final_exception`, si se completa una investigación acotada, reproducible y documentada que justifique el cierre negativo.

## 5. Obligación de procesamiento computacional

Para toda fuente admitida, el objeto canónico correspondiente debe satisfacer como mínimo:

1. identidad y relación con las identidades históricas explícitas;
2. manifiesto de activos reproducible;
3. SHA-256 de cada página fuente admitida;
4. tamaño de fuente conocido;
5. OCR reconstruible bajo `local/`;
6. registro de página FTRL por cada JPEG admitido;
7. SQLite `pages` con cardinalidad idéntica al corpus OCR;
8. SQLite FTS5 con cardinalidad idéntica a `pages`;
9. `PRAGMA integrity_check = ok`;
10. manifiesto de ejecución text-free ligado al commit y a la corrida CI;
11. cola y resumen de QC text-free;
12. preservación explícita de `zero_search_text`, confianza baja, confianza ausente y otras anomalías;
13. no publicación por defecto de OCR íntegro, SQLite, snippets o imágenes fuente cuando los derechos no lo permitan.

La falta de calidad OCR no autoriza excluir una página. La página se procesa, se marca para QC y permanece trazable.

## 6. Retenciones y excepciones: no son exclusiones

El registro `data/catalog/ltmd_u1_retained_source_register.csv` forma parte del universo FTRL, no de un universo externo.

Las `active_retention` son **trabajo pendiente obligatorio** para el cierre global. Una ola puede avanzar computacionalmente sobre sus fuentes disponibles, pero no puede declararse exhaustivamente cerrada mientras conserve retenciones activas.

Las `final_exception` permanecen en el denominador 542/542 y deben conservar evidencia de la búsqueda, límite metodológico y razón por la que no existe una representación fuente admisible. No reciben OCR ficticio y no aumentan el numerador de fuente procesada.

## 7. Olas: sólo mecanismo logístico

W1–W11 sirven para particionar el trabajo y controlar recursos. **Ninguna ola constituye el universo final del proyecto.**

El orden de ejecución puede optimizarse por costo y riesgo, pero no puede modificar el conjunto obligatorio. Completar W1, W3 o cualquier otra ola no autoriza detener FTRL-U1. Después de cada cierre intermedio se continúa con la siguiente deuda técnica hasta que las 542 identidades tengan disposición final y toda fuente admitida haya pasado por FTRL.

La expresión `cohorte fuente-admitida cerrada` sólo describe la parte computacional disponible de una ola; no equivale a `ola exhaustivamente cerrada` si existe cualquier `active_retention`.

## 8. Criterios de cierre

### 8.1 Cierre de una identidad

Una identidad está técnicamente dispuesta cuando se cumple exactamente una de estas condiciones:

- está cubierta por un objeto canónico FTRL integralmente validado;
- está cubierta por una relación técnica demostrada hacia un objeto canónico FTRL integralmente validado;
- tiene una `final_exception` documentada.

Una `active_retention` nunca cuenta como cierre.

### 8.2 Cierre de una ola

Una ola sólo puede llamarse **exhaustivamente cerrada** si todas sus identidades nominales cumplen 8.1 y no conserva `active_retention`.

### 8.3 Cierre global FTRL-U1

FTRL-U1 sólo puede declararse técnicamente exhaustivo cuando simultáneamente:

- el universo maestro contiene exactamente 542 identidades únicas;
- las 542 tienen disposición explícita;
- no existe ninguna `active_retention`;
- toda representación fuente admitida está cubierta por FTRL y sus cardinalidades de página son reproducibles;
- todas las relaciones de alias/reutilización usadas para evitar procesamiento redundante están demostradas y preservan las identidades históricas;
- las excepciones finales permanecen visibles como resultados negativos y no se contabilizan como fuente procesada;
- la evidencia pública de ejecución es text-free y auditable.

Por tanto, **524/542 de cobertura efectiva no es cierre global**, y tampoco lo es terminar todos los objetos actualmente admitidos mientras permanezca una retención activa.

## 9. Contrato legible por máquina

`data/research/ltmd_u1_exhaustive_scope_contract.json` congela el denominador y los invariantes del corte. `scripts/validate_ftrl_u1_exhaustive_scope.py` comprueba que:

- existen exactamente 542 `viewer_key` únicos en el tablero maestro;
- todas las identidades pertenecen a una ola W1–W11;
- el registro residual es subconjunto exacto del universo;
- las disposiciones `required_ftrl_processing`, `active_retention` y `final_exception` son mutuamente excluyentes y cubren 542/542;
- el corte vigente conserva 524 + 13 + 5 = 542;
- ninguna retención activa puede interpretarse como cierre global.

El validador es un gate de alcance, no una prueba de que las 524 identidades ya hayan completado FTRL. El progreso FTRL debe medirse por separado y nunca alterar el denominador.

## 10. Separación epistemológica

El mandato exhaustivo es técnico y documental. No modifica estas desigualdades:

- `corpus_ready != semantic_ready`;
- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`;
- `final_exception != source_resolved`.

Procesar todos los libros disponibles no equivale a validar semánticamente todos sus textos. La validación humana seguirá siendo una capa distinta y deberá declarar su propio denominador y diseño muestral o exhaustivo.

## 11. Política de avance

A partir de esta versión:

- no se detiene el escalamiento después de W1;
- no se omite una identidad por dificultad técnica;
- no se reduce el denominador para mejorar porcentajes;
- no se declara “completo” un subconjunto como si fuera LTMD-U1;
- cada nueva ola FTRL debe heredar este contrato;
- cualquier cambio futuro del universo requiere una versión U2 o una revisión explícita del snapshot, nunca una modificación silenciosa de U1.

## 12. Preservación persistente de productos restringidos

La ejecución exhaustiva y la preservación son obligaciones separadas y acumulativas. Los productos completos restringidos de FTRL —incluidos OCR por página, SQLite/FTS5 y QC detallado— no deben quedar únicamente en almacenamiento efímero después de una corrida integral.

A partir del 24 de agosto de 2026, toda corrida integral queda sujeta además a [`LTMD_PRIVATE_CORPUS_PRESERVATION_CANON_0_1.md`](LTMD_PRIVATE_CORPUS_PRESERVATION_CANON_0_1.md) y a `data/research/ltmd_private_corpus_storage_contract.json`.

La bóveda persistente canónica es un espacio privado de Google Drive bajo control del responsable del proyecto. El repositorio público no conserva identificadores, enlaces privados, credenciales ni claves privadas de esa bóveda.

Se distinguen expresamente:

- `computationally_validated`: la corrida pasó los gates técnicos FTRL;
- `archival_complete`: los productos restringidos fueron copiados a la bóveda privada y sus checksums fueron verificados.

Por tanto, `computationally_validated != archival_complete`. La deuda de preservación de corridas anteriores debe resolverse retroactivamente.

Este protocolo es la autoridad para interpretar el alcance exhaustivo de FTRL-U1; el canon de preservación privada es la autoridad complementaria para la custodia persistente de sus productos completos.
