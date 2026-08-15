# Solapamiento exacto de fragmentos — expansión CN4/CN6

Versión: `CN46_FRAGMENT_OVERLAP_0.1`. Fragmentos analizados: **19,067**.

## Pares con mayor número de textos exactos compartidos
- `LTMD-CN4-G1972` ↔ `LTMD-CN4-G1988`: hashes textuales compartidos=1351; 94.0% de los textos únicos de A y 92.0% de B.
- `LTMD-CN6-G1988` ↔ `LTMD-CN6-G1993-CN`: hashes textuales compartidos=173; 11.9% de los textos únicos de A y 12.0% de B.
- `LTMD-CN4-G2014` ↔ `LTMD-CN6-G2014`: hashes textuales compartidos=131; 6.0% de los textos únicos de A y 4.2% de B.
- `LTMD-CN6-G1972` ↔ `LTMD-CN6-G1988`: hashes textuales compartidos=64; 4.5% de los textos únicos de A y 4.4% de B.
- `LTMD-CN6-G1972` ↔ `LTMD-CN6-G2014`: hashes textuales compartidos=47; 3.3% de los textos únicos de A y 1.5% de B.
- `LTMD-CN6-G1988` ↔ `LTMD-CN6-G2014`: hashes textuales compartidos=47; 3.2% de los textos únicos de A y 1.5% de B.
- `LTMD-CN4-G1972` ↔ `LTMD-CN6-G1972`: hashes textuales compartidos=41; 2.9% de los textos únicos de A y 2.9% de B.
- `LTMD-CN4-G1988` ↔ `LTMD-CN6-G1972`: hashes textuales compartidos=41; 2.8% de los textos únicos de A y 2.9% de B.
- `LTMD-CN4-G2014` ↔ `LTMD-CN6-G1972`: hashes textuales compartidos=37; 1.7% de los textos únicos de A y 2.6% de B.
- `LTMD-CN6-G1993-DH` ↔ `LTMD-CN6-G2014`: hashes textuales compartidos=35; 1.0% de los textos únicos de A y 1.1% de B.
- `LTMD-CN4-G2014` ↔ `LTMD-CN6-G1988`: hashes textuales compartidos=33; 1.5% de los textos únicos de A y 2.3% de B.
- `LTMD-CN6-G1988` ↔ `LTMD-CN6-G1993-DH`: hashes textuales compartidos=33; 2.3% de los textos únicos de A y 1.0% de B.
- `LTMD-CN4-G1993` ↔ `LTMD-CN4-G2014`: hashes textuales compartidos=31; 1.4% de los textos únicos de A y 1.4% de B.
- `LTMD-CN4-G1972` ↔ `LTMD-CN6-G2014`: hashes textuales compartidos=30; 2.1% de los textos únicos de A y 1.0% de B.
- `LTMD-CN4-G1988` ↔ `LTMD-CN6-G2014`: hashes textuales compartidos=30; 2.0% de los textos únicos de A y 1.0% de B.
- `LTMD-CN4-G1972`: 1369/1455 ocurrencias de fragmento (94.1%) tienen texto exacto presente en el otro CN4 1972/1988.
- `LTMD-CN4-G1988`: 1378/1496 ocurrencias de fragmento (92.1%) tienen texto exacto presente en el otro CN4 1972/1988.

## Regla
Un `text_sha256` idéntico prueba identidad del texto normalizado de la unidad, no necesariamente identidad de layout ni equivalencia funcional. La deduplicación futura se implementará como vista analítica reversible y conservará todas las ocurrencias/procedencias.
