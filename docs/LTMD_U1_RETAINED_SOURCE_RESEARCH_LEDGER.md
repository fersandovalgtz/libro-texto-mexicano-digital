# LTMD-U1 — ledger de investigación de fuentes retenidas

Versión: `LTMD_U1_RETAINED_SOURCE_ATTEMPTS_0.1`  
Corte inicial: **27 de agosto de 2026**.

## Propósito

Este ledger convierte la investigación residual de fuentes de LTMD-U1 en una secuencia auditable de intentos. Su unidad no es el libro ni el visor, sino un **intento de investigación** vinculado inequívocamente a una identidad que ya existe en `data/catalog/ltmd_u1_retained_source_register.csv`.

El ledger no sustituye el registro canónico de retenciones y no puede, por sí solo, modificar la cobertura. Su función es documentar qué se intentó, sobre qué identidad, con qué alcance, qué resultado produjo y si ese resultado es suficiente para justificar una transición de ciclo de vida.

## Relación con el registro canónico

En el corte de apertura existen **13 retenciones activas**:

- W2 Matemáticas: `H2018P3DMA`, `H2018P4DMA`, `H2018P5DMA`, `H2018P6DMA`;
- W7 Formación Cívica y Ética: `H2014P5FCA`, `H2018P3FCA`, `H2018P4FCA`, `H2018P5FCA`, `H2018P6FCA`;
- W8 Artes: `H2018P3EAA`, `H2018P4EAA`, `H2018P5EAA`, `H2018P6EAA`.

Las cinco `final_exception` de W10/W11 no se incorporan a la búsqueda rutinaria. Sólo pueden reaparecer en este ledger mediante un intento con método `new_evidence_trigger_review`, es decir, cuando exista una representación primaria o archivística nueva que justifique reabrir el caso.

## Corte inicial de intentos

La versión 0.1 contiene **26 intentos sobre 13 identidades**:

1. **13 consolidaciones de evidencia existente**, una por retención activa, que convierten en filas estructuradas los resultados ya documentados en los informes W2/W7 y en el issue W8;
2. **13 búsquedas exactas de clave realizadas el 27 de agosto de 2026** sobre dominios oficiales CONALITEG y buscadores públicos. No apareció un resultado indexado exacto para ninguna de las trece claves; para `H2014P5FCA` se añadió además `104.jpg` a la consulta.

El segundo punto es únicamente evidencia de descubrimiento. **Un resultado de índice vacío no demuestra que la fuente histórica no existió, que no fue archivada o que sea irrecuperable.** Por ello todas las filas conservan `state_after=active_retention`.

## Semántica de campos

- `ledger_version`: versión del contrato de datos.
- `attempt_id`: identificador estable del intento, con forma `RS-YYYYMMDD-NNN`.
- `attempt_date`: fecha ISO del registro del intento.
- `wave`, `viewer_key`, `tracking_issue`: unión explícita con el registro canónico.
- `method`: procedimiento utilizado, por ejemplo consolidación documental o búsqueda exacta de clave.
- `scope`: superficie donde se ejecutó o consolidó el intento.
- `query_or_target`: consulta o blanco exacto.
- `outcome`: resultado técnico del intento.
- `evidence_reference`: referencia al artefacto, issue, búsqueda o URI que permite auditar el resultado.
- `evidence_sha256`: digest de la evidencia cuando existe un artefacto admitido; puede quedar vacío para resultados negativos/de descubrimiento.
- `admissibility`: fuerza probatoria del intento para modificar el ciclo de vida.
- `state_before`, `state_after`: transición explícita; en un resultado negativo deben permanecer iguales.
- `notes`: límites y lectura metodológica del intento.

## Reglas de admisibilidad

El ledger distingue tres valores de `admissibility`:

### `discovery_only`

El resultado sirve para orientar o acotar investigación, pero no puede resolver la identidad. Ejemplos: una búsqueda de índice sin resultados o una señal secundaria todavía no verificada.

### `not_admissible_to_resolve`

Existe evidencia técnica reproducible del problema, pero no una representación suficiente para levantar la retención. Ejemplos: ruta declarada no servida, hueco interno identificado o subárbol oficial que responde 404 bajo el contrato documentado.

### `admissible_to_resolve`

Se reserva para evidencia que satisface la compuerta de fuente: ruta institucional efectiva, captura archivada inequívoca, relación documental explícita o identidad criptográfica demostrada. En el contrato 0.1 una fila que cambie de estado debe usar esta clase y conservar un SHA-256 de la evidencia admitida.

## Prohibiciones automáticas

El validador impide que resultados como `no_indexed_result`, `declared_route_unserved`, `isolated_gap_unresolved`, `official_subtree_unserved`, `source_unresolved`, `archive_inconclusive` o `candidate_unverified` cambien el ciclo de vida.

También impide:

- registrar identidades que no están en el registro de retenciones;
- alterar ola o issue de seguimiento;
- declarar `state_before` distinto del registro canónico;
- reabrir una excepción final mediante búsqueda rutinaria;
- declarar evidencia resolutiva sin digest SHA-256;
- dejar una retención activa sin al menos una consolidación de evidencia de partida.

La implementación está en `scripts/validate_u1_retained_source_attempts.py` y utiliza únicamente la biblioteca estándar de Python.

## Resultado científico del corte 0.1

La creación del ledger **no cambia las cifras de cobertura**. LTMD-U1 permanece en **524/542 (96.68%)** de cobertura técnica efectiva, con **13 retenciones activas y 5 excepciones técnicas finales**.

El avance es de trazabilidad: a partir de este corte, una búsqueda fallida, un candidato externo, una captura archivada o una eventual resolución pueden incorporarse como eventos comparables y verificables sin reescribir retrospectivamente los documentos de cada ola.

## Próximo criterio de trabajo

Los siguientes intentos deben priorizar evidencia de mayor fuerza probatoria y evitar repetir búsquedas exactas ya registradas salvo cambio de infraestructura o aparición de una pista concreta. Una retención sólo se promoverá cuando la cadena de procedencia satisfaga el protocolo general del registro residual; en caso contrario, el ledger crecerá sin inflar la cobertura.

`WAITING_HUMAN_REFERENCE` permanece intacto. Este ledger pertenece al carril técnico-documental y no valida categorías semánticas ni afirmaciones históricas.
