# LTMD-U1 W11 — auditoría estricta de activos de la ruta no estándar con configuración oficial

Versión: `LTMD_U1_W11_NONSTANDARD_ASSET_AUDIT_0.1`.

- Visores auditados: **11/11**.
- Posiciones declaradas: **849**.
- JPEG servidos y hasheados: **837**.
- Candidatos terminales sintéticos estrictos: **9**.
- Posiciones internas no servidas: **3**.
- Visores `direct_asset_ready`: **9/11**.

## Por visor

| viewer | declaradas | JPEG | terminal | internas no servidas | direct ready |
|---|---:|---:|---:|---:|---:|
| `H1993P4CI192` | 67 | 66 | 1 | 0 | 1 |
| `H2008P4CI270` | 67 | 66 | 1 | 0 | 1 |
| `H2011P4CI316` | 66 | 65 | 1 | 0 | 1 |
| `H2014P1CAM` | 115 | 114 | 1 | 0 | 1 |
| `H2014P1EAM` | 49 | 48 | 0 | 1 | 0 |
| `H2014P2EAM` | 19 | 17 | 0 | 2 | 0 |
| `H2014P4CCA` | 66 | 65 | 1 | 0 | 1 |
| `H2018P1CAM` | 114 | 113 | 1 | 0 | 1 |
| `H2018P4CCA` | 66 | 65 | 1 | 0 | 1 |
| `H2019P1CAM` | 154 | 153 | 1 | 0 | 1 |
| `H2019P4CCA` | 66 | 65 | 1 | 0 | 1 |

## Regla
La anomalía de HTML se conserva como hecho técnico. El uso de `claves.json` sólo habilita esta auditoría porque la configuración existe explícitamente para los 11 visores; no se infiere por semejanza con otros. Cada JPEG servido se recorre para tipo, tamaño y SHA-256 y no se persiste.
