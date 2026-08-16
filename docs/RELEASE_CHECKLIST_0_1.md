# Checklist de primera liberación científica — LTMD 0.1

Fecha de creación: 2026-08-15  
Última actualización: 2026-08-15  
Release: **v0.1.0-rc.1**

## Estado ejecutivo

`v0.1.0-rc.1` fue publicada en GitHub como **prerelease metodológica/técnica** después de superar el preflight final.

El corte auditado demostró:

- `rc_technical_ready=true`;
- `publish_ready=true`;
- `technical_failures=[]`;
- `publish_blockers=[]`;
- `LTMD_INTEGRITY_0.6`: **166/166** artefactos críticos;
- recomputación SHA-256 completa: **PASS**, cero discrepancias;
- verificación del artículo metodológico: **PASS**;
- fuentes/working files prohibidos rastreados: **0**;
- gate humano SEMB 0.3: **cerrado correctamente**.

GitHub Release: https://github.com/fersandovalgtz/libro-texto-mexicano-digital/releases/tag/v0.1.0-rc.1

## Identidad y citación

- [x] `CITATION.cff` presente.
- [x] versión semántica fijada: `v0.1.0-rc.1`.
- [x] archivo raíz `VERSION` materializado.
- [x] metadata de versión/fecha preparada.
- [x] referencia bibliográfica provisional documentada.
- [x] tag anotado `v0.1.0-rc.1` creado.
- [x] GitHub Release publicada como prerelease.
- [ ] Zenodo debe ingerir/archivar la release y emitir un DOI real.
- [ ] añadir DOI/badge al README únicamente después de verificar ese registro.

## Derechos y licencias

- [x] software propio: Apache License 2.0 (`LICENSE`).
- [x] derivados originales licenciables: CC BY 4.0 (`DATA_LICENSE.md`).
- [x] alcance limitado a derechos poseídos/controlados por el licenciante.
- [x] materiales fuente CONALITEG/SEP y de terceros excluidos expresamente.
- [x] imágenes, libros, texto fuente y OCR sustitutivo fuera del paquete público ordinario.
- [x] separación formal entre código, derivados propios y materiales fuente.
- [x] comprobación automática de ausencia de fuentes/workfiles prohibidos.

## Integridad y reproducibilidad

- [x] manifiesto SHA-256 de artefactos críticos.
- [x] `LTMD_INTEGRITY_0.6` validado con 166/166 y `missing_critical=[]`.
- [x] SHA-256 crítico recomputado por el preflight contra el checkout.
- [x] workflows reproducibles de capas centrales.
- [x] CI de infraestructura SEMB 0.3.
- [x] verificación ejecutable de cifras del manuscrito.
- [x] preflight automatizado.
- [x] dependencia Python directa de SEMB 0.2 fijada.
- [x] runtime y límites de congelamiento documentados.
- [x] reporte específico de reproducibilidad.
- [ ] mejora futura opcional: congelar Python patch-level y lock transitivo de wheels.

## Alcance científico

- [x] piloto CN5 delimitado y auditado.
- [x] distinción `catalog_generation` / edición bibliográfica.
- [x] PAGESTRUCT y FRAGSEG versionados.
- [x] SEMB 0.2 documentado como resultado negativo/diagnóstico.
- [x] SEMB 0.3 preregistrado antes de referencia humana.
- [x] release definida como metodológica/técnica, anterior a SEMB 0.3 humano.
- [x] expansiones CN4/CN6 y Ola 2 tratadas como `corpus_ready`, no `semantic_ready`.
- [x] 64,856 unidades descritas como ocurrencias técnicas, no observaciones históricas independientes.
- [x] SEMB 0.3 permanece en `WAITING_HUMAN_REFERENCE`.

## Documentación

- [x] README de release/corpus.
- [x] contexto curricular y registro de fuentes.
- [x] estrategia de publicación y expansión.
- [x] manuscrito metodológico 0.2.
- [x] `CHANGELOG.md`.
- [x] release notes.
- [x] matriz de outputs públicos.
- [x] reporte de reproducibilidad.
- [x] matriz de derechos y memorando de licencias.
- [x] índice maestro de método.
- [ ] revisión sistemática de enlaces/archivos web, deseable en releases estables posteriores.

## Operaciones publicadas

- [x] corte documental cerrado.
- [x] integridad regenerada.
- [x] preflight final en success.
- [x] tag anotado creado.
- [x] GitHub prerelease creada.
- [x] workflow de publicación de una sola vez retirado de `main` después del éxito.
- [ ] depósito/ingesta Zenodo confirmado.
- [ ] DOI versionado incorporado sólo después de confirmación.

## Regla de no retroactividad

El tag `v0.1.0-rc.1` identifica un corte cerrado. `main` puede continuar evolucionando, pero el tag no debe moverse ni reescribirse para incorporar cambios posteriores o un DOI sobrevenido. Cualquier corrección científica o técnica material produce una nueva versión.

La publicación de esta RC **no** altera el gate semántico: la futura release con resultados históricos primarios sigue condicionada a la referencia humana de SEMB 0.3.
