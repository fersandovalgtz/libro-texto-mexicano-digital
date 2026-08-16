# LTMD-U1 W3 — readiness de Español/Lengua 0.1

Corte: 15 de agosto de 2026.  
Estado: **preingestión técnica preparada; activos no auditados todavía**.

## Universo

- **130 visores** congelados desde LTMD-U1.
- **23,894 posiciones declaradas** por `claves.json`.
- Cobertura temporal del catálogo: generaciones 1960–2019.

## Arquitectura

- 130/130 HTML alcanzables.
- 126/130 usan la interfaz estándar `x.js`.
- 4/130 usan la interfaz `x_horizontal.js`:
  - `H1993P1ES139`;
  - `H1993P2ES147`;
  - `H2014P1LEA`;
  - `H2014P2LEA`.

El probe de `x_horizontal.js` demuestra que esos cuatro visores siguen utilizando el mismo contrato de catálogo/datos: `claves.json`, `ag_pages`, `ag_clave` y `magazine.js`. La diferencia observada es de interfaz/orientación, no evidencia de ausencia del material.

Por tanto, W3 se tratará operacionalmente como:

- **126 visores con UI estándar**;
- **4 visores con UI horizontal**;
- **130 visores bajo el mismo contrato de catálogo**, sujetos todavía a auditoría empírica de JPEG y SHA-256.

## Partición industrial

Las 23,894 posiciones se dividieron de forma determinista en **14 batches**, ninguno mezcla generaciones y ninguno supera 2,500 posiciones declaradas. La partición es logística; no altera el denominador W3 ni implica independencia histórica.

## Próxima frontera técnica

Antes de cualquier OCR productivo de Español/Lengua se requiere:

1. auditoría empírica de activos por viewer/batch;
2. clasificación de terminales, huecos internos y problemas de routing;
3. recuperación documentada cuando proceda;
4. detección de aliases exactos por SHA-256;
5. selección de contenidos canónicos de cómputo;
6. sólo después OCR → PAGESTRUCT → FRAGSEG.

W3 no hereda ningún clasificador semántico de Ciencias Naturales ni de Matemáticas. La expansión técnica puede avanzar sin abrir semántica.
