# LTMD v0.1.0-rc.1 — release notes

Fecha de candidata: **2026-08-15**  
Tipo: **release metodológica pre-1.0 / release candidate**  
Estado de preflight: **`publish_ready=true`**

## Qué congela esta candidata

`v0.1.0-rc.1` congela la infraestructura técnica y metodológica de **Libro de Texto Mexicano Digital** después del cierre del piloto CN5, la expansión CN4/CN6 y la Ola 2 de la familia _Ciencias Naturales_.

Incluye:

- 759 imágenes fuente reales y 9,594 fragmentos del piloto CN5;
- 1,888 JPEG reales y 19,067 fragmentos de la expansión CN4/CN6;
- 3,177 JPEG fuente y 36,195 fragmentos de Ola 2;
- **64,856 ocurrencias técnicas de fragmento** en total;
- catálogo histórico reproducible de 542 visores y 191 familias de título nuclear;
- resolución completa de activos para 35/37 visores de la familia estricta _Ciencias Naturales_;
- modelado explícito de reutilización, revisión, reemplazo y aliases documentales;
- `LTMD_INTEGRITY_0.6` con **166/166** artefactos críticos presentes;
- recomputación de los 166 SHA-256 críticos contra el checkout sin discrepancias;
- manuscrito metodológico 0.2 con verificación automática de cifras;
- infraestructura prehumana de SEMB 0.3 y sus gates de desarrollo/lock/validación;
- Apache License 2.0 para software propio;
- CC BY 4.0 para derivados originales licenciables bajo el alcance de `DATA_LICENSE.md`.

## Qué NO congela como resultado definitivo

Esta candidata **no** debe interpretarse como liberación de resultados históricos semánticos validados. No incluye SEMB 0.3 validado con referencia humana, gold standard humano abierto, inferencias históricas primarias basadas en los 64,856 fragmentos ni apertura de la validación bloqueada.

SEMB 0.2 se conserva como resultado negativo/diagnóstico y sus tendencias históricas siguen etiquetadas como exploratorias.

## Unidad de conteo

Las 64,856 unidades son **ocurrencias técnicas de fragmento**, no observaciones históricas independientes. El proyecto conserva relaciones documentales y vistas reversibles para evitar contar como independientes páginas o fragmentos reutilizados entre ediciones/visores.

## Derechos y licencias

El software original se licencia bajo Apache License 2.0. Los derivados originales sobre los que el licenciante posea o controle derechos suficientes se ofrecen bajo CC BY 4.0.

Ninguna de esas licencias se extiende por implicación a libros, páginas, PDF/JPEG, portadas, ilustraciones, texto fuente, OCR sustitutivo, marcas u otros materiales de CONALITEG/SEP o terceros. Los workflows que requieren fuente reconstruyen activos temporalmente, verifican SHA-256 y eliminan las copias de trabajo.

## Reproducibilidad

La candidata conserva scripts/workflows exactos, manifiestos de página/fragmento, hashes SHA-256, outputs derivados no sustitutivos, `requirements-release.txt`, documentación del entorno y controles automáticos de integridad y de cifras del artículo.

El entorno de referencia es Ubuntu 24.04. El congelamiento de Python patch-level y wheels transitivos sigue siendo parcial y está declarado como limitación, no ocultado.

## Estado del preflight

El control `LTMD_RELEASE_PREFLIGHT_0.3` exige:

- `rc_technical_ready=true`;
- `publish_ready=true`;
- cero technical failures y cero publish blockers;
- `LTMD_INTEGRITY_0.6` 166/166;
- recomputación SHA-256 completa sin discrepancias;
- claim check del manuscrito en PASS;
- licencias materializadas y con alcance correcto;
- ausencia de fuentes/workfiles prohibidos rastreados;
- permanencia cerrada del gate humano SEMB 0.3.

## Citación provisional antes del DOI

Mientras no exista un DOI versionado real:

> Sandoval Gutiérrez, Fernando. (2026). _Libro de Texto Mexicano Digital_ (v0.1.0-rc.1) [Software e infraestructura de investigación]. GitHub.

El DOI se incorporará sólo después de que Zenodo archive una release real. No se anticipará ni inventará un identificador persistente.

## Criterio de publicación

La RC puede publicarse cuando el commit final del corte documental reproduzca `publish_ready=true` y cero discrepancias SHA-256. La publicación de esta RC no constituye promoción a una versión semánticamente validada.

La secuencia externa es:

1. cerrar documentación del corte;
2. regenerar integridad;
3. repetir preflight sobre el corte estabilizado;
4. crear el tag exacto `v0.1.0-rc.1`;
5. publicar GitHub Release;
6. archivar en Zenodo;
7. registrar el DOI real posteriormente sin reescribir silenciosamente el tag archivado.
