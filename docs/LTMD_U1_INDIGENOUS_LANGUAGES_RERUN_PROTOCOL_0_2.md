# LTMD-U1 — protocolo preregistrado de rerun sobre lenguas indígenas 0.2

**Versión:** `LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2`

**Fecha de congelamiento:** 2026-08-30.

## 1. Propósito

Este protocolo define **antes de ejecutar la nueva corrida integral** una recuperación determinista e independiente para el estudio de lenguas indígenas en la Full-Text Research Layer de LTMD-U1. No intenta ajustar parámetros para reproducir los agregados exploratorios 0.1. Si los resultados divergen, la divergencia se conserva y se explica.

## 2. Universo esperado

La corrida debe fallar si los SQLite privados suministrados no reconcilian exactamente:

- 86,549 `page_id` canónicos únicos;
- 492 `canonical_viewer_key` únicos.

Los duplicados exactos de `page_id` se eliminan. Un duplicado con conflicto de identidad canónica, `source_sha256`, `ocr_sha256`, generación o localizador de página provoca error fatal.

## 3. Privacidad y derechos

El script lee `search_text` privado, pero los artefactos públicos no contienen OCR ni snippets. El ledger público conserva sólo metadatos, localizadores, hashes, familias de coincidencia y estados de validación.

## 4. Normalización

Para recuperación solamente:

1. Unicode NFKD;
2. `casefold`;
3. eliminación de marcas combinantes;
4. tokenización ASCII alfanumérica `[a-z0-9]+`.

La normalización de búsqueda no reescribe ni corrige el OCR fuente y no se publica como transcripción.

## 5. Capa explícita directa

Una página entra como `explicit_general=1` si contiene al menos una de estas frases normalizadas:

- `lengua indigena`
- `lenguas indigenas`
- `idioma indigena`
- `idiomas indigenas`
- `lengua originaria`
- `lenguas originarias`
- `idioma originario`
- `idiomas originarios`

## 6. Conceptos lingüísticos con anclaje indígena

También puede entrar como `explicit_general=1` una página con alguno de estos conceptos:

- `diversidad linguistica`
- `pluralidad linguistica`
- `derechos linguisticos`
- `derecho linguistico`
- `discriminacion linguistica`
- `lengua nacional`
- `lenguas nacionales`

pero **sólo** si existe, dentro de una distancia máxima de 60 tokens, un anclaje indígena (`indigena`, `indigenas`, `originaria(s)`, `originario(s)`) o una lengua del lexicón nominal 0.2 que además haya pasado el filtro contextual de la sección siguiente.

## 7. Lenguas nombradas con contexto lingüístico

El lexicón 0.2 se congela deliberadamente en los 12 conjuntos comparables con el reporte 0.1. **No es un catálogo exhaustivo de las lenguas de México.**

- Náhuatl: `nahuatl`, `nahua`, `nahuas`
- Maya: `maya`, `mayas`
- Zapoteco: `zapoteco`, `zapoteca`, `zapotecos`, `zapotecas`
- Mixteco: `mixteco`, `mixteca`, `mixtecos`, `mixtecas`
- Purépecha/tarasco: `purepecha`, `purepechas`, `purhepecha`, `purhepechas`, `tarasco`, `tarasca`, `tarascos`, `tarascas`
- Otomí: `otomi`, `otomis`
- Huasteco/teenek: `huasteco`, `huasteca`, `huastecos`, `huastecas`, `teenek`, `tenek`
- Tarahumara/rarámuri: `tarahumara`, `tarahumaras`, `raramuri`, `raramuris`
- Cora/náayeri: `cora`, `coras`, `naayeri`, `nayeri`
- Mayo/yoreme: `mayo`, `mayos`, `yoreme`, `yoremes`
- Yaqui: `yaqui`, `yaquis`
- Tseltal/tzeltal: `tseltal`, `tseltales`, `tzeltal`, `tzeltales`

Una forma nominal sólo cuenta como `named_language_contextual=1` si se encuentra a **30 tokens o menos** de al menos una señal lingüística del conjunto congelado:

`lengua`, `lenguas`, `idioma`, `idiomas`, `habla`, `hablas`, `hablan`, `hablar`, `hablaba`, `hablaban`, `hablante`, `hablantes`, `bilingue`, `bilingues`, `bilinguismo`, `monolingue`, `monolingues`, `monolinguismo`, `vocabulario`, `palabra`, `palabras`, `traduccion`, `traducciones`, `traducir`, `traduce`, `traducido`, `dialecto`, `dialectos`, `linguistica`, `linguisticas`, `linguistico`, `linguisticos`, `alfabeto`, `alfabetos`, `escritura`, `escrito`, `escrita`, `oral`, `orales`, `oralidad`, `pronuncia`, `pronunciacion`.

Este requisito rechaza, por ejemplo, una referencia a la civilización maya sin contexto lingüístico próximo.

## 8. Indicador amplio 0.2

`broad_candidate=1` si:

- `explicit_general=1`, o
- `named_language_contextual=1`.

Una página se cuenta una sola vez en el indicador amplio aunque active varias familias o lenguas.

## 9. Salidas públicas

La corrida genera:

1. ledger de candidatos sin OCR;
2. resumen por generación con denominadores reales y tasas por 1,000 páginas;
3. conteos por conjunto lingüístico;
4. conteos lengua × generación;
5. manifiesto JSON con parámetros congelados, hashes de bases privadas por nombre de archivo, cardinalidad y hashes de los outputs.

Los paths locales completos de los SQLite no se publican; el manifiesto puede registrar nombres base y hashes criptográficos.

## 10. Estado científico

Todos los candidatos salen con `validation_status=not_visually_validated`. Esta corrida no cambia `text_verified`, `semantic_ready` ni estados archivísticos.

Siguen vigentes:

- `ocr_available != text_verified`
- `corpus_ready != semantic_ready`
- `search_hit != historical_claim`
- `zero_hits != demonstrated_absence`

## 11. Comparación con 0.1

Los agregados 0.1 se preservan como corte exploratorio histórico. La 0.2 es una corrida nueva, con lógica explícita preregistrada. No se calibrarán ventanas, vocabulario o filtros después de observar sus resultados con el propósito de acercarlos a 0.1.

Cualquier expansión futura —por ejemplo un lexicón más exhaustivo basado en un catálogo externo de lenguas— deberá versionarse como una nueva especificación y no sustituirá silenciosamente esta corrida.
