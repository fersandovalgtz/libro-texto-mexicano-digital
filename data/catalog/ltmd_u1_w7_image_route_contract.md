# LTMD-U1 W7 — contrato de ruta de imagen

Versión: `LTMD_U1_W7_IMAGE_ROUTE_CONTRACT_0.1`.

Política: extracción exclusiva de JavaScript; no se solicitan activos de página.

- Fuente: `https://historico.conaliteg.gob.mx/magazine.js`.
- HTTP: **200**.
- SHA-256 de la fuente: `0a885166ba1252c650565eeb43218f72382450d268541533afe26cb62fe80d33`.
- Sentencias con `ag_page`: **21**.
- Sentencias de ruta/imagen: **7**.
- Sentencias explícitas que combinan `ag_clave` + `ag_page`: **6**.

## Transformación observada de página

- línea 74: `var ag_page = "";`
- línea 80: `ag_page = pad(0);`
- línea 82: `ag_page = ag_page.toString();`
- línea 86: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 93: `ag_page = pad(page);`
- línea 95: `ag_page = ag_page.toString();`
- línea 99: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 160: `var ag_page = "";`
- línea 166: `ag_page = pad(0);`
- línea 168: `ag_page = ag_page.toString();`
- línea 172: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 179: `ag_page = pad(page);`
- línea 181: `ag_page = ag_page.toString();`
- línea 185: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 208: `var ag_page = "";`
- línea 214: `ag_page = pad(0);`
- línea 216: `ag_page = ag_page.toString();`
- línea 220: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 227: `ag_page = pad(page);`
- línea 229: `ag_page = ag_page.toString();`
- línea 233: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`

## Construcción observada de URL

- línea 86: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 99: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 172: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 185: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 220: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`
- línea 233: `img.attr('src', './c/' + ag_clave + '/' + ag_page +'.jpg');`

Este contrato documenta únicamente el algoritmo observado en el código del visor. No demuestra que los archivos resultantes existan para todas las generaciones; esa disponibilidad debe comprobarse por separado y de forma mínima.
