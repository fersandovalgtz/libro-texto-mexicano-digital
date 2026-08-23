# LTMD-U1 — configuración de representaciones oficiales candidatas

Versión: `LTMD_U1_OFFICIAL_REPRESENTATION_CONFIG_0.2`.

Se extraen únicamente metadatos de configuración desde recursos oficiales CONALITEG y se contrastan con los manifiestos W11. No se declara equivalencia documental ni se persisten imágenes fuente.

## `H2014P3COL` / `P3COL`

- Filas históricas W11: **161**; rango índice **0–161**.
- Recursos oficiales textuales recuperados: **3/3**.
- Evidencias técnicas extraídas: **5**.

- `entry_html` → `https://libros.conaliteg.gob.mx/P3COL.htm` · HTTP 200 · SHA-256 `4468ef39b70d1af3e894da2f4856ebe2b48b4d248b97f3b307cd99825552a24c`
- `x_js` → `https://libros.conaliteg.gob.mx/2022/x.js` · HTTP 200 · SHA-256 `ba93f5bfa61541bfc54271b7b8eb21bb0d54d690fa6ffcfb82000005f3a1209a`
- `hash_js` → `https://libros.conaliteg.gob.mx/2022/hash.js` · HTTP 200 · SHA-256 `5c56c9d6b31c8de4d43a1099c1a80cbcca39f0a63696a10ef389d9eeaff84887`

Expresiones `fetch` observadas:
- `x_js`: `'../output.json'`

Construcción de `clavesUrl`:
- `x_js`: `getKeysFromUrl(urlActual)`

Cadenas candidatas de configuración:
- `entry_html`: `https://libros.conaliteg.gob.mx/2022/P3COL.htm`
- `x_js`: `../output.json`

Estados históricos observados:
- `internal_unserved`: **1**.
- `source_jpeg`: **160**.

## `H2014P3MOR` / `P3MOR`

- Filas históricas W11: **161**; rango índice **0–161**.
- Recursos oficiales textuales recuperados: **3/3**.
- Evidencias técnicas extraídas: **3**.

- `entry_html` → `https://libros.conaliteg.gob.mx/P3MOR.htm` · HTTP 200 · SHA-256 `cff90701808424d37abae1b8b75bf16a153e261abc85f34f6fbfa80a7d0876a4`
- `x_js` → `https://libros.conaliteg.gob.mx/x.js` · HTTP 200 · SHA-256 `ff795d0aa986540eec669fea57146db26b0da8f8d7043a9d8538700a498ddad2`
- `hash_js` → `https://libros.conaliteg.gob.mx/hash.js` · HTTP 200 · SHA-256 `5c56c9d6b31c8de4d43a1099c1a80cbcca39f0a63696a10ef389d9eeaff84887`

Estados históricos observados:
- `internal_unserved`: **1**.
- `source_jpeg`: **160**.

## Criterio para la siguiente compuerta

Sólo si estos metadatos permiten resolver un endpoint oficial de configuración y una secuencia con cardinalidad compatible se habilita comparación criptográfica temporal. Todas las posiciones históricas servidas deben concordar; coincidencia parcial, título, grado o clave corta no recuperan el hueco.
