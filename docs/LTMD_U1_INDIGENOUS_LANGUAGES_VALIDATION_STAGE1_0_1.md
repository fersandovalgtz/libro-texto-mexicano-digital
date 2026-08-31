# LTMD-U1 — validación visual de lenguas indígenas, Stage 1 (0.1)

## Estado y dependencia

Este protocolo continúa `LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2` sin modificar sus reglas de recuperación ni sus resultados. El rerun 0.2 produjo 1,151 páginas candidatas, de las cuales 457 pertenecen a la capa `explicit_general`. Todas permanecen en estado `not_visually_validated`.

La prioridad de Stage 1 es validar visualmente las 457 páginas `explicit_general` contra su activo fuente antes de formular inferencias históricas o promover cualquier registro a `semantic_ready`.

## Principios no negociables

- `ocr_available != text_verified`.
- `search_hit != historical_claim`.
- La unidad inicial de revisión es la página fuente, no el hit OCR.
- No se publica OCR, transcripción extensa, snippet ni imagen fuente.
- La validación sólo puede cambiar el estado científico después de inspección visual de la página correspondiente.
- Los resultados 0.2 no se recalibran retrospectivamente a partir de la validación; cualquier cambio futuro del algoritmo de recuperación requiere nueva versión.

## Cola privada de validación

La cola se construye localmente desde el ledger privado `ltmd_u1_indigenous_languages_candidate_ledger_0_2.csv` con:

```bash
python scripts/prepare_indigenous_validation_sample.py \
  --candidate-ledger /ruta/privada/ltmd_u1_indigenous_languages_candidate_ledger_0_2.csv \
  --output-csv /ruta/privada/ltmd_u1_indigenous_languages_validation_queue_0_1.csv \
  --manifest-json /ruta/privada/ltmd_u1_indigenous_languages_validation_queue_manifest_0_1.json \
  --expected-explicit 457
```

El script falla si la cardinalidad de la capa explícita deja de ser 457, si faltan campos requeridos o si un `page_id` duplicado presenta conflicto de identidad/hashes.

La cola resultante contiene únicamente identificadores, metadatos de fuente, hashes, términos de consulta ya derivados y campos vacíos de codificación. No contiene `search_text`, OCR ni fragmentos.

## Doble codificación preregistrada

Antes de observar resultados de validación, Stage 1 fija una selección determinista para acuerdo intercodificador:

- estratificación por `generation`;
- ranking pseudoaleatorio reproducible mediante SHA-256 de `seed + page_id`;
- 10% de cada generación, redondeado hacia arriba;
- mínimo de 2 páginas por generación cuando el estrato lo permita;
- si un estrato tiene menos de 2 páginas, se selecciona completo.

El conjunto puede reconstruirse exactamente con el mismo ledger y seed. Cambiar tasa, mínimo o seed constituye una nueva versión del protocolo.

## Secuencia de revisión

Cada una de las 457 páginas debe pasar por:

1. comprobación de que `source_asset_url` corresponde al `page_id` y al `canonical_viewer_key` esperados;
2. comprobación visual de que la página fuente carga y corresponde a la posición declarada;
3. decisión `verified_true | false_positive | uncertain`;
4. clasificación con `LTMD_U1_INDIGENOUS_LANGUAGES_CODEBOOK_0_1.md` sólo cuando la evidencia visual lo permite;
5. registro conservador de `false_positive_cause` cuando proceda;
6. adjudicación posterior de desacuerdos en las páginas marcadas `double_code_required=1`.

## Causas de falso positivo

Stage 1 admite, como mínimo, las siguientes categorías no expresivas:

- `ocr_error`;
- `homonym_or_polysemy`;
- `non_linguistic_named_group`;
- `context_too_weak`;
- `source_mismatch`;
- `other_documented`.

Estas categorías describen la causa de exclusión y no sustituyen la evidencia visual.

## Acuerdo y adjudicación

Las páginas de doble codificación se revisan de forma independiente por dos codificadores. El acuerdo debe estimarse por variable y no como una única cifra agregada cuando las variables sean multietiqueta. Las discrepancias se conservan; la adjudicación produce un estado final separado de Código A y Código B.

No se revisa el codebook durante la primera pasada. Si los desacuerdos muestran definiciones insuficientes, se congela el conjunto inicial, se documentan los problemas y se crea `CODEBOOK_0_2.md`; nunca se sobrescribe 0.1.

## Puerta de salida de Stage 1

Stage 1 sólo se considera completo cuando:

- 457/457 páginas explícitas tienen decisión visual registrada;
- 0 filas permanecen sin resolver salvo excepciones humanas documentadas;
- la muestra de doble codificación está completa y adjudicada;
- existe un manifiesto de hashes de la cola y sus salidas;
- los falsos positivos están cuantificados por causa y generación;
- cualquier promoción científica se realiza en un artefacto posterior y versionado, no modificando el rerun 0.2.

Hasta entonces, los conteos 0.2 siguen siendo **resultados de recuperación de candidatos**, no prevalencias históricas validadas.
