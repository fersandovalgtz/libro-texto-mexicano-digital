# LTMD v0.1.0-rc.1 — release notes

Fecha de candidata: **2026-08-15**  
Tipo: **release metodológica pre-1.0 / release candidate**

## Qué congela esta candidata

`v0.1.0-rc.1` congela la infraestructura técnica y metodológica de **Libro de Texto Mexicano Digital** después del cierre del piloto CN5, la expansión CN4/CN6 y la Ola 2 de la familia *Ciencias Naturales*.

La candidata incluye:

- 759 imágenes fuente reales y 9,594 fragmentos del piloto CN5;
- 1,888 JPEG reales y 19,067 fragmentos de la expansión CN4/CN6;
- 3,177 JPEG fuente y 36,195 fragmentos de Ola 2;
- **64,856 ocurrencias técnicas de fragmento** en total;
- catálogo histórico reproducible de 542 visores y 191 familias de título nuclear;
- resolución completa de activos para 35/37 visores de la familia estricta *Ciencias Naturales*;
- modelado explícito de reutilización, revisión, reemplazo y aliases documentales;
- `LTMD_INTEGRITY_0.5` con 150/150 artefactos críticos presentes;
- manuscrito metodológico 0.2 con verificación automática de cifras;
- infraestructura prehumana de SEMB 0.3 y sus gates de desarrollo/lock/validación.

## Qué NO congela como resultado definitivo

Esta candidata **no** debe interpretarse como liberación de resultados históricos semánticos validados.

No incluye:

- SEMB 0.3 validado con referencia humana;
- gold standard humano abierto;
- inferencias históricas primarias basadas en los 64,856 fragmentos;
- apertura de la validación bloqueada;
- DOI de Zenodo, mientras no exista un depósito real asociado al tag definitivo;
- una licencia general que relicencie materiales fuente de CONALITEG/SEP.

SEMB 0.2 se conserva como resultado negativo/diagnóstico y sus tendencias históricas siguen etiquetadas como exploratorias.

## Unidad de conteo

Las 64,856 unidades son **ocurrencias técnicas de fragmento**, no observaciones históricas independientes. El proyecto conserva relaciones documentales y vistas reversibles para evitar contar como independientes páginas o fragmentos reutilizados entre ediciones/visores.

## Procedencia y derechos

Los libros, páginas, ilustraciones y texto fuente de CONALITEG/SEP no se redistribuyen masivamente desde esta release candidata. Los workflows reconstruyen activos temporalmente, verifican SHA-256, derivan métricas/estructuras y eliminan las copias temporales.

La licencia del código propio y la licencia de metadatos/derivados originales deben resolverse separadamente antes de declarar una release estable.

## Reproducibilidad

La candidata conserva:

- scripts y workflows exactos;
- manifiestos de página/fragmento;
- hashes SHA-256;
- outputs derivados no sustitutivos;
- `requirements-release.txt` con dependencia Python directa fijada para SEMB 0.2;
- entorno de referencia documentado en `docs/REPRODUCIBILITY_ENVIRONMENT_0_1.md`;
- controles automáticos de integridad y de cifras del artículo.

El entorno todavía no está congelado a nivel completo de patch/wheel para Python y dependencias transitivas; esta limitación queda documentada y no se oculta.

## Citación provisional antes del DOI

Mientras no exista un DOI versionado real, la forma recomendada de referirse a esta candidata es:

> Sandoval Gutiérrez, Fernando. (2026). *Libro de Texto Mexicano Digital* (v0.1.0-rc.1) [Software e infraestructura de investigación]. GitHub.

Después de depositar la release real en Zenodo, la referencia debe incorporar el DOI versionado asignado a ese depósito y `CITATION.cff` deberá actualizarse sin modificar retroactivamente tags previos.

## Criterio para pasar de RC a release estable

La candidata sólo podrá promoverse a una primera release estable cuando, como mínimo:

1. se resuelvan y documenten por separado la licencia del código y la de derivados LTMD;
2. se complete el preflight de release sin blockers técnicos;
3. se regenere el manifiesto de integridad sobre el commit exacto a etiquetar;
4. se compruebe que no hay fuentes privadas/temporales versionadas;
5. se publique el tag/release en GitHub;
6. Zenodo archive exactamente ese tag y emita el DOI versionado;
7. README y `CITATION.cff` incorporen el DOI sólo después de su existencia real.
