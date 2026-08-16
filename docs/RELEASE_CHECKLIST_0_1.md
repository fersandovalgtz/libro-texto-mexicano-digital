# Checklist de primera liberación científica — LTMD 0.1

Fecha de creación: 2026-08-15  
Última actualización: 2026-08-15  
Candidata vigente: **v0.1.0-rc.1**

## Objetivo

Preparar una primera release archivable en GitHub/Zenodo sin confundir repositorio activo, release candidate y versión científica estable. La liberación debe ser reconstruible, citable y explícita sobre aquello que no redistribuye.

## Estado ejecutivo

El preflight endurecido de `v0.1.0-rc.1` reporta:

- `rc_technical_ready=true`;
- `publish_ready=true`;
- `technical_failures=[]`;
- `publish_blockers=[]`;
- `LTMD_INTEGRITY_0.6`: **166/166** artefactos críticos;
- recomputación SHA-256 de los 166 artefactos críticos: **PASS**, cero discrepancias;
- verificación del artículo metodológico: **PASS**;
- fuentes/working files prohibidos rastreados por Git: **0**;
- gate humano SEMB 0.3: **cerrado correctamente**.

La candidata está, por tanto, **lista para publicarse como release candidate metodológica/técnica**. Esto no convierte SEMB 0.3 en validado ni autoriza inferencias históricas sustantivas nuevas.

## Condiciones de release

### Identidad y citación

- [x] `CITATION.cff` presente.
- [x] versión semántica fijada: `v0.1.0-rc.1`.
- [x] archivo raíz `VERSION` materializado.
- [x] `CITATION.cff` actualizado con versión y fecha de candidata.
- [x] referencia bibliográfica provisional documentada.
- [ ] crear el tag exacto `v0.1.0-rc.1`.
- [ ] publicar GitHub Release asociada al tag.
- [ ] archivar esa release en Zenodo y registrar el DOI versionado real.
- [ ] añadir DOI/badge al README únicamente después de que exista realmente.

### Derechos y licencias

- [x] licencia del **software propio** materializada en `LICENSE`: Apache License 2.0.
- [x] licencia de **datos derivados originales licenciables** materializada en `DATA_LICENSE.md`: CC BY 4.0.
- [x] `DATA_LICENSE.md` limita el alcance a derechos poseídos/controlados por el licenciante.
- [x] materiales fuente CONALITEG/SEP y de terceros excluidos expresamente.
- [x] imágenes, libros, texto fuente y OCR sustitutivo fuera del paquete público ordinario.
- [x] separación formal entre código, derivados propios y materiales fuente.
- [x] comprobación automática de ausencia de fuentes/workfiles prohibidos rastreados.
- [x] política y decisión documentadas en `RIGHTS_PUBLICATION_MATRIX_0_2.md` y `LICENSE_DECISION_MEMO_0_1.md`.

### Integridad y reproducibilidad

- [x] manifiesto SHA-256 de artefactos críticos.
- [x] `LTMD_INTEGRITY_0.6` validado con **166/166** artefactos críticos y `missing_critical=[]`.
- [x] SHA-256 de cada entrada crítica recomputado por el preflight contra el checkout actual.
- [x] workflows reproducibles de las capas centrales.
- [x] CI de infraestructura SEMB 0.3.
- [x] verificación ejecutable de cifras del manuscrito metodológico.
- [x] preflight de release automatizado.
- [x] comprobación de ausencia de `private/`, `data/raw/`, `data/work/`, `downloads/` y `working/` rastreados.
- [x] dependencia Python directa de SEMB 0.2 fijada en `requirements-release.txt`.
- [x] runtime y límites de congelamiento documentados.
- [x] reporte específico de reproducibilidad materializado.
- [ ] opcional para una versión estable posterior: congelar Python patch-level y lock transitivo de wheels.
- [ ] regenerar integridad y repetir preflight sobre el corte documental final inmediatamente anterior al tag.

### Alcance científico

- [x] corpus piloto CN5 delimitado y auditado.
- [x] distinción formal entre generación del catálogo y edición bibliográfica.
- [x] PAGESTRUCT y FRAGSEG versionados.
- [x] resultado negativo SEMB 0.2 documentado.
- [x] protocolo SEMB 0.3 preregistrado antes de referencia humana.
- [x] primera release definida como metodológica/técnica, anterior a SEMB 0.3 humano.
- [x] SEMB 0.2 marcado como diagnóstico/exploratorio, no gold standard.
- [x] expansiones CN4/CN6 y Ola 2 incluidas sólo como `corpus_ready`, no `semantic_ready`.
- [x] 64,856 unidades descritas como **ocurrencias técnicas**, no observaciones históricas independientes.
- [x] SEMB 0.3 continúa en `WAITING_HUMAN_REFERENCE`.

### Documentación

- [x] README actualizado al corpus escalado y al estatus de release.
- [x] contexto curricular 0.2.
- [x] registro de fuentes primarias.
- [x] estrategia de publicación.
- [x] plan de expansión.
- [x] manuscrito metodológico 0.2.
- [x] `CHANGELOG.md`.
- [x] instalación/runtime mínimo documentado.
- [x] tabla de outputs públicos por workflow.
- [x] release notes específicas.
- [x] índice maestro de método actualizado.
- [ ] revisión sistemática de enlaces externos y alternativas archivadas, deseable para futuras releases estables.

### Expansión y dependencia documental

- [x] mecanismo reproducible de descubrimiento del Catálogo Histórico identificado.
- [x] relación documental de los dos objetos CN6 bajo generación 1993 documentada.
- [x] dependencia/reutilización CN4 1972↔1988 representada explícitamente.
- [x] aliases 2018→2019 demostrados por identidad byte a byte.
- [x] dos objetos 2008 parciales documentados conservadoramente.
- [x] CN4/CN6 y Ola 2 incluidos como infraestructura técnica, no inferencia semántica.

## Blockers vigentes

**El preflight no identifica blockers de publicación:** `publish_blockers=[]`.

Lo pendiente ya no es un bloqueo del paquete, sino la secuencia externa de publicación: crear tag, GitHub Release, depósito Zenodo y después registrar el DOI real.

El DOI **no** es una precondición del tag. Debe ser una salida del depósito real y nunca debe anticiparse.

## Decisión vigente

**`v0.1.0-rc.1` es la release candidate metodológica/técnica formal y está lista para publicación.** Su eventual publicación no cambia el gate científico: la futura release con resultados históricos semánticos continúa condicionada a SEMB 0.3 humano.

## Secuencia de promoción pública

1. cerrar este corte documental;
2. regenerar `LTMD_INTEGRITY_0.6`;
3. ejecutar el preflight y exigir `rc_technical_ready=true`, `publish_ready=true`, cero discrepancias SHA-256 y cero blockers;
4. crear el tag exacto `v0.1.0-rc.1` sobre el commit verificado;
5. publicar GitHub Release;
6. archivar en Zenodo;
7. registrar el DOI versionado real en la metadata de una actualización posterior, sin reescribir silenciosamente el tag archivado.

## Regla de no retroactividad

El DOI o tag de una release identifica exactamente el estado de código/datos de esa versión. Las correcciones posteriores producen una nueva release; no se reescribe silenciosamente una versión archivada.
