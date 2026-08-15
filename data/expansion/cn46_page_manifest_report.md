# Manifiesto de páginas — expansión CN4/CN6

Versión: `CN46_PAGE_MANIFEST_0.2`.

- Posiciones de visor: **1,897**.
- JPEG fuente verificados y hasheados: **1,888**.
- Posiciones terminales sintéticas: **9**.
- Bytes fuente recorridos para SHA-256: **245,141,456**.
- Hashes repetidos entre páginas: **188**.

## Por objeto
- `LTMD-CN4-G1972`: visor=215; JPEG=214; bytes=10,317,105; hashes únicos=214.
- `LTMD-CN6-G1972`: visor=211; JPEG=210; bytes=11,438,747; hashes únicos=210.
- `LTMD-CN4-G1988`: visor=215; JPEG=214; bytes=10,507,868; hashes únicos=214.
- `LTMD-CN6-G1988`: visor=243; JPEG=242; bytes=12,814,479; hashes únicos=242.
- `LTMD-CN4-G1993`: visor=179; JPEG=178; bytes=13,173,058; hashes únicos=178.
- `LTMD-CN6-G1993-DH`: visor=251; JPEG=250; bytes=18,988,083; hashes únicos=250.
- `LTMD-CN6-G1993-CN`: visor=243; JPEG=242; bytes=15,183,088; hashes únicos=242.
- `LTMD-CN4-G2014`: visor=162; JPEG=161; bytes=74,116,056; hashes únicos=161.
- `LTMD-CN6-G2014`: visor=178; JPEG=177; bytes=78,602,972; hashes únicos=177.

## Regla de procedencia
El manifiesto conserva URL, tamaño y SHA-256 de cada activo, pero no redistribuye el JPEG. Una etapa posterior debe reconstruir temporalmente el activo y comprobar el hash antes de producir OCR o derivados.

## Corrección de cardinalidad
La versión 0.1 del script contenía una aserción manual errónea (1,888 posiciones / 1,879 activos). El inventario auditado suma 1,897 posiciones / 1,888 activos; el workflow 0.1 falló antes de publicar, por lo que no existe un manifiesto incorrecto versionado.
