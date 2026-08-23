# LTMD-U1 W11 — diagnóstico HTML de la ruta no estándar

Versión: `LTMD_U1_W11_NONSTANDARD_HTML_0.3`.

- Visores no estándar auditados: **11/11**.
- HTML 200: **11/11**.
- Recursos únicos observados por visor y consolidados: **66**.
- Controles UI compartidos: **44**.
- Recursos globales de interfaz/sitio: **22**.
- Candidatos de fuente/documento: **0**.

## Tipos de recurso observado
- `jpg`: **22**.
- `png`: **44**.

## Por visor

| viewer | HTML | recursos | UI | sitio | fuente/doc | iframe | embed | object | PDF | imágenes | JSON |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `H1993P4CI192` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2008P4CI270` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2011P4CI316` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2014P1CAM` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2014P1EAM` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2014P2EAM` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2014P4CCA` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2018P1CAM` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2018P4CCA` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2019P1CAM` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| `H2019P4CCA` | 200 | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |

## Regla de interpretación
Los cuatro `/pics/*.png` de navegación y los dos JPG globales `tw.jpg`/`tw_conaliteg.jpg` se clasifican como chrome compartido, no como fuente documental. El diagnóstico deduplica URLs dentro de cada visor y examina atributos/literales con extensiones documentales o multimedia. La evidencia HTML se interpreta junto con `claves.json`; en esta cohorte la configuración oficial constituye una ruta independiente que aún debe verificarse activo por activo.
