# LTMD-U1 W7 — probe acotado de ciclos faltantes, páginas 13–20

Versión: `LTMD_U1_W7_MISSING_CYCLE_WINDOW_13_20_0.1`.

- Targets derivados desde W7 admitido + Observations 0.4 sin `school_cycle_statement`: **12**.
- Ventana adicional: páginas lógicas **13–20**.
- Páginas descargadas temporalmente y verificadas SHA-256+tamaño: **96/96**.
- OCR independiente: PSM **3, 6, 11** por página.
- Objetos con ≥1 `school_cycle` fuerte multímodo en la ventana: **0/12**.
- Objetos sin ciclo fuerte en la ventana: **12/12**.

Un ciclo fuerte requiere el mismo `YYYY-YYYY+1` en ≥2 PSM sobre la misma página fuente SHA-verificada. Este probe **no promueve automáticamente observaciones ni candidatos**.

## Ciclos fuertes encontrados

| objeto | página | ciclo | PSM | SHA |
|---|---:|---|---|---|
| — | — | — | — | — |

## Sin ciclo fuerte en páginas 13–20

- `H2008P1CI251`.
- `H2008P2CI258`.
- `H2008P3CI264`.
- `H2008P4CI269`.
- `H2011P3CI308`.
- `H2014P1FCA`.
- `H2014P2FCA`.
- `H2014P3FCA`.
- `H2014P6FCA`.
- `H2019P1FCA`.
- `H2019P2FCA`.
- `H2019P3FCA`.

## Límite epistemológico

Cero hallazgos en esta ventana significa únicamente que páginas 13–20 no aportaron un ciclo fuerte bajo el contrato OCR 0.1. No demuestra que el ejemplar carezca de ciclo escolar. Si aparecen ciclos fuertes, una promoción posterior deberá preservar página, SHA y soporte PSM y recalcular Observations/Candidates de forma versionada.
