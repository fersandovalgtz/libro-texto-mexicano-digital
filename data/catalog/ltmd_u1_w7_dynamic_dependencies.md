# LTMD-U1 W7 — dependencias dinámicas del visor

Versión: `LTMD_U1_W7_DYNAMIC_DEPENDENCIES_0.1`.

Política: inspección exclusiva de HTML/JavaScript del mismo origen; no se solicitan activos de página.

- Fuentes iniciales: **10**.
- Fuentes inspeccionadas en total: **14**.
- Dependencias JavaScript nuevas descubiertas: **4**.
- Dependencias nuevas con HTTP 200: **4**.
- Evidencias de carga dinámica: **1**.
- Definiciones observadas de `addPage`: **1**.
- Definiciones observadas de `loadPage`: **1**.
- Evidencias explícitas de ruta de imagen: **12**.

## Dependencias nuevas

- `https://historico.conaliteg.gob.mx/turn.js` — HTTP 200 — 74062 bytes — SHA-256 `e27644257b9749b709baddc8fa3edbcd88c2945ed4e435500fdd4b276686d380` — descubierta desde `https://historico.conaliteg.gob.mx/x.js`.
- `https://historico.conaliteg.gob.mx/turn.html4.min.js` — HTTP 200 — 23173 bytes — SHA-256 `aeeec025bf16c6883326184c12d4df0b2ac78b674c74a40ac2cfc5e9e341ef42` — descubierta desde `https://historico.conaliteg.gob.mx/x.js`.
- `https://historico.conaliteg.gob.mx/zoom.min.js` — HTTP 200 — 12137 bytes — SHA-256 `46b7e7e4f04487b7be39a704b2203dbb7e173c2a1fcd3eaae6483052ae398360` — descubierta desde `https://historico.conaliteg.gob.mx/x.js`.
- `https://historico.conaliteg.gob.mx/magazine.js` — HTTP 200 — 7455 bytes — SHA-256 `0a885166ba1252c650565eeb43218f72382450d268541533afe26cb62fe80d33` — descubierta desde `https://historico.conaliteg.gob.mx/x.js`.

## Resultado

Se localizó al menos una definición observable de `addPage`; el JSON conserva la fuente y el snippet hasheado para el siguiente paso de reconstrucción de ruta.
