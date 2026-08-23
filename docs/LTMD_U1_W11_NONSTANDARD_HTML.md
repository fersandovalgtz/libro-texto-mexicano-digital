# LTMD-U1 W11 — diagnóstico HTML de la ruta no estándar

Versión: `LTMD_U1_W11_NONSTANDARD_HTML_0.2`.

- Visores no estándar auditados: **11/11**.
- HTML 200: **11/11**.
- Recursos candidatos observados: **110**.
- Controles UI compartidos: **88**.
- Candidatos de fuente/documento no-UI: **22**.

## Tipos de recurso observado
- `jpg`: **22**.
- `png`: **88**.

## Por visor

| viewer | HTML | refs | candidatos | UI | fuente/doc | iframe | embed | object | PDF | imágenes | JSON |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `H1993P4CI192` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2008P4CI270` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2011P4CI316` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2014P1CAM` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2014P1EAM` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2014P2EAM` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2014P4CCA` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2018P1CAM` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2018P4CCA` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2019P1CAM` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |
| `H2019P4CCA` | 200 | 22 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 0 |

## Regla de interpretación
Los cuatro recursos `/pics/der.png`, `/pics/go.png`, `/pics/h.png` y `/pics/izq.png` se clasifican de forma explícita como controles UI compartidos, no como fuente documental. El diagnóstico examina atributos de recursos y literales con extensiones documentales/multimedia en el HTML; no descarga ni valida activos candidatos. La ausencia de candidato no demuestra por sí sola inexistencia de fuente: debe contrastarse además con la configuración oficial y cualquier otra evidencia servida reproduciblemente.
