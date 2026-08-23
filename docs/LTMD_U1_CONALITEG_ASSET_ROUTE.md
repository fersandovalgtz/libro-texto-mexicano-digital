# LTMD-U1 — descubrimiento del patrón de activos CONALITEG

Versión: `LTMD_U1_CONALITEG_ASSET_ROUTE_0.3`.

Se inspeccionan temporalmente los módulos oficiales del visor y se retienen únicamente expresiones normalizadas relacionadas con imágenes. No se persiste el código completo ni imágenes fuente.

## `root-x`

- URL: `https://libros.conaliteg.gob.mx/x.js`.
- SHA-256: `ff795d0aa986540eec669fea57146db26b0da8f8d7043a9d8538700a498ddad2`.
- Expresiones de imagen observadas: **0**.
- Error: `ninguno`.


## `root-js`

- URL: `https://libros.conaliteg.gob.mx/js.js`.
- SHA-256: `f9a9e09cea856d0621d37c00835ee2cc08e70845a0a6d8f13cfddc917b44a690`.
- Expresiones de imagen observadas: **0**.
- Error: `ninguno`.


## `root-magazine`

- URL: `https://libros.conaliteg.gob.mx/magazine.js`.
- SHA-256: `5806fc2748e1a81be2b3ee60a09fe0af7af7837b36c099b406eb6927fe8be245`.
- Expresiones de imagen observadas: **2**.
- Error: `ninguno`.

- expresión: `// crea el string 001.jpg`
  - plantilla: `no_resuelta`
- expresión: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg')`
  - plantilla: `{base}/c/{ag_clave}/{page}.jpg`

## `2022-x`

- URL: `https://libros.conaliteg.gob.mx/2022/x.js`.
- SHA-256: `ba93f5bfa61541bfc54271b7b8eb21bb0d54d690fa6ffcfb82000005f3a1209a`.
- Expresiones de imagen observadas: **0**.
- Error: `ninguno`.


## `2022-js`

- URL: `https://libros.conaliteg.gob.mx/2022/js.js`.
- SHA-256: `f9a9e09cea856d0621d37c00835ee2cc08e70845a0a6d8f13cfddc917b44a690`.
- Expresiones de imagen observadas: **0**.
- Error: `ninguno`.


## `2022-magazine`

- URL: `https://libros.conaliteg.gob.mx/2022/magazine.js`.
- SHA-256: `bc490ee5abc49ccc33630647ca36b2c926fec0609dbb10210b6e63e68e76664c`.
- Expresiones de imagen observadas: **2**.
- Error: `ninguno`.

- expresión: `// crea el string 001.jpg`
  - plantilla: `no_resuelta`
- expresión: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg')`
  - plantilla: `{base}/c/{ag_clave}/{page}.jpg`

## Plantillas derivadas

- `{base}/c/{ag_clave}/{page}.jpg`

## Regla

Una plantilla derivada sólo habilita un probe de activos oficiales. No demuestra correspondencia con el visor histórico. La equivalencia exige cotejo criptográfico posicional completo de todas las páginas históricas servidas.
