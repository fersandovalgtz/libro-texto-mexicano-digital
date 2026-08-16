# Checklist de primera liberación científica estable — LTMD 0.1

Fecha de creación: 2026-08-15  
Última actualización: 2026-08-15  
Candidata vigente: **v0.1.0-rc.1**

## Objetivo

Preparar una primera release archivable en GitHub/Zenodo sin confundir repositorio activo, release candidate y versión científica estable. La liberación debe ser reconstruible, citable y explícita sobre aquello que no redistribuye.

## Estado ejecutivo

El preflight automatizado de `v0.1.0-rc.1` reporta:

- `rc_technical_ready=true`;
- `technical_failures=[]`;
- `LTMD_INTEGRITY_0.5`: **150/150** artefactos críticos;
- verificación del artículo metodológico: **PASS**;
- fuentes/working files prohibidos rastreados por Git: **0**;
- gate humano SEMB 0.3: **cerrado correctamente**;
- `publish_ready=false` por dos blockers explícitos: `code_license_not_selected` y `derived_data_license_not_selected`.

Por tanto, la candidata está **técnicamente lista como RC**, pero todavía no debe publicarse como release cerrada hasta resolver las licencias.

## Condiciones de release

### Identidad y citación

- [x] `CITATION.cff` presente.
- [x] versión semántica de candidata fijada: `v0.1.0-rc.1`.
- [x] archivo raíz `VERSION` materializado.
- [x] `CITATION.cff` actualizado con versión y fecha de candidata.
- [x] referencia bibliográfica provisional documentada en las release notes.
- [ ] publicar tag/release real en GitHub cuando `publish_ready=true`.
- [ ] archivar esa release en Zenodo y registrar el DOI versionado real.
- [ ] añadir DOI/badge al README sólo después de que exista realmente.
- [ ] actualizar la referencia recomendada con el DOI versionado real sin reescribir silenciosamente tags archivados.

### Derechos y licencias

- [ ] seleccionar y materializar licencia del **código propio** (`LICENSE`). **BLOCKER**.
- [ ] seleccionar y materializar licencia/política de **datos derivados originales** (`DATA_LICENSE.md`). **BLOCKER**.
- [x] documentar por separado que imágenes, libros y textos fuente de CONALITEG/SEP no son relicenciados por LTMD.
- [x] excluir de la candidata redistribución masiva de páginas, imágenes y OCR íntegro.
- [x] separar conceptualmente código, derivados propios y materiales fuente en `RIGHTS_AND_REUSE_0_1.md`.
- [x] comprobar automáticamente que fuentes y workfiles prohibidos no estén rastreados.
- [ ] cerrar la decisión jurídica de licencia después de revisar la matriz de derechos vigente.

### Integridad y reproducibilidad

- [x] manifiesto SHA-256 de artefactos críticos.
- [x] `LTMD_INTEGRITY_0.5` validado con **150/150** artefactos críticos y `missing_critical=[]`.
- [x] workflows reproducibles de las capas centrales.
- [x] CI de infraestructura SEMB 0.3.
- [x] verificación ejecutable de cifras del borrador metodológico.
- [x] preflight de release automatizado (`check-release-candidate`).
- [x] comprobación automática de ausencia de `private/`, `data/raw/`, `data/work/`, `downloads/` y `working/` rastreados.
- [x] dependencia Python directa de SEMB 0.2 fijada en `requirements-release.txt`.
- [x] runtime y límites de congelamiento documentados en `REPRODUCIBILITY_ENVIRONMENT_0_1.md`.
- [x] reporte específico de reproducibilidad materializado en `REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md`.
- [ ] congelar Python patch-level y lock transitivo de wheels si se exige reproducción de entorno más estricta para una release estable.
- [ ] regenerar manifiesto de integridad inmediatamente antes del tag definitivo.
- [ ] ejecutar de nuevo el preflight sobre el commit exacto a etiquetar y exigir `publish_ready=true`.

### Alcance científico

- [x] corpus piloto CN5 delimitado y auditado.
- [x] distinción formal entre generación del catálogo y edición bibliográfica.
- [x] PAGESTRUCT y FRAGSEG versionados.
- [x] resultado negativo SEMB 0.2 documentado.
- [x] protocolo SEMB 0.3 preregistrado antes de referencia humana.
- [x] decisión tomada: la primera candidata ocurre **antes** de SEMB 0.3 humano y es metodológica/técnica.
- [x] SEMB 0.2 marcado inequívocamente como diagnóstico/exploratorio, no gold standard.
- [x] expansiones CN4/CN6 y Ola 2 incluidas sólo como corpus técnico `corpus_ready`, no como resultado `semantic_ready`.
- [x] 64,856 unidades descritas como **ocurrencias técnicas**, no como observaciones históricas independientes.
- [x] SEMB 0.3 continúa en `WAITING_HUMAN_REFERENCE` y el preflight verifica que no existan outputs humanos prematuros.

### Documentación

- [x] README actualizado al corpus escalado.
- [x] contexto curricular 0.2.
- [x] registro de fuentes primarias.
- [x] estrategia de publicación.
- [x] plan de expansión.
- [x] manuscrito metodológico 0.2.
- [x] `CHANGELOG.md` materializado para `v0.1.0-rc.1`.
- [x] instalación/runtime mínimo documentado.
- [x] tabla de outputs públicos por workflow en `RELEASE_OUTPUTS_0_1.md`.
- [x] release notes específicas en `RELEASE_NOTES_v0.1.0-rc.1.md`.
- [x] índice maestro de método actualizado.
- [ ] revisar sistemáticamente enlaces externos y registrar fecha de acceso/alternativas archivadas cuando corresponda.

### Expansión y dependencia documental

- [x] mecanismo reproducible de descubrimiento del Catálogo Histórico identificado.
- [x] visores CN4/CN6 descubiertos desde el snapshot institucional.
- [x] relación documental de los dos objetos CN6 bajo generación 1993 documentada.
- [x] dependencia/reutilización CN4 1972↔1988 representada explícitamente.
- [x] aliases 2018→2019 demostrados por identidad byte a byte.
- [x] dos objetos 2008 parciales documentados sin convertir posiciones no servidas en hechos bibliográficos no verificados.
- [x] CN4/CN6 y Ola 2 forman parte de la candidata como **infraestructura técnica**, no como inferencia semántica.
- [x] no mezclar semánticamente las expansiones con el piloto antes de validación apropiada.

## Blockers vigentes

A la fecha de este corte, el preflight identifica sólo dos blockers que impiden `publish_ready=true`:

1. `code_license_not_selected`;
2. `derived_data_license_not_selected`.

El DOI **no** es un blocker previo a publicar el tag: es una salida posterior del archivo real en Zenodo y no debe anticiparse ni inventarse.

## Decisión vigente

**v0.1.0-rc.1 es la candidata metodológica/técnica formal.** Puede auditarse y reproducirse como corte pre-1.0. No debe promoverse todavía a release pública cerrada hasta resolver licencias y volver a ejecutar los controles sobre el commit final.

La futura release con resultados históricos semánticos sigue condicionada a SEMB 0.3 humano; no se adelanta por disponer de un corpus técnico grande.

## Secuencia de promoción a release pública

1. resolver licencia del código y de derivados propios;
2. actualizar documentación de derechos si procede;
3. regenerar integridad sobre el commit final;
4. ejecutar el preflight y exigir `rc_technical_ready=true` y `publish_ready=true`;
5. crear el tag exacto;
6. publicar GitHub Release;
7. archivar en Zenodo;
8. registrar DOI versionado real en la metadata de la siguiente actualización permitida, sin reescribir silenciosamente el tag archivado.

## Regla de no retroactividad

El DOI o tag de una release identifica exactamente el estado de código/datos de esa versión. Las correcciones posteriores producen una nueva release; no se reescribe silenciosamente una versión archivada.
