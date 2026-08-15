# Checklist de primera liberación científica estable — LTMD 0.1

Fecha de creación: 2026-08-15

## Objetivo

Preparar una primera release archivable en GitHub/Zenodo sin confundir “repositorio activo” con “versión científica cerrada”. La liberación debe ser reconstruible, citable y explícita sobre aquello que no redistribuye.

## Condiciones mínimas para release candidata

### Identidad y citación

- [x] `CITATION.cff` presente.
- [ ] fijar número de versión semántica (`v0.1.0` u otro) sólo al cerrar alcance;
- [ ] actualizar `CITATION.cff` con versión y fecha de release;
- [ ] archivar release en Zenodo y registrar DOI versionado;
- [ ] añadir DOI/badge al README después de que exista realmente;
- [ ] generar referencia bibliográfica recomendada para software/dataset y para artículos asociados.

### Derechos y licencias

- [ ] definir licencia del **código**;
- [ ] definir licencia de **datos derivados originales** cuando sea jurídicamente posible;
- [ ] documentar por separado que imágenes, libros y textos fuente de CONALITEG no son relicenciados por LTMD;
- [ ] revisar si alguna salida derivada textual cruza umbral de sustitución de la obra original;
- [ ] crear `LICENSE` y, si procede, `DATA_LICENSE.md`;
- [ ] incorporar una tabla de componentes/licencias en `docs/RIGHTS_AND_REUSE.md`.

### Integridad y reproducibilidad

- [x] manifiesto SHA-256 de artefactos críticos;
- [x] workflows reproducibles de las capas centrales;
- [x] CI de infraestructura SEMB 0.3;
- [x] verificación ejecutable de cifras del borrador metodológico;
- [ ] regenerar manifiesto de integridad inmediatamente antes del tag;
- [ ] ejecutar todos los workflows de auditoría definidos para la release;
- [ ] comprobar que ninguna ruta `private/` ni texto reconstruido temporalmente entra al tag;
- [ ] congelar `requirements`/versiones de runtimes necesarias para reproducción;
- [ ] generar un `REPRODUCIBILITY_REPORT.md` de release con commits, runtimes y estado de cada workflow.

### Alcance científico

- [x] corpus piloto CN5 delimitado y auditado;
- [x] distinción formal entre generación del catálogo y edición bibliográfica;
- [x] PAGESTRUCT y FRAGSEG versionados;
- [x] resultado negativo SEMB 0.2 documentado;
- [x] protocolo SEMB 0.3 preregistrado en el repositorio antes de referencia humana;
- [ ] decidir si la primera release ocurre **antes** de SEMB 0.3 humano como release metodológica, o después como release de piloto validado;
- [ ] si se libera antes, marcar inequívocamente los resultados históricos SEMB 0.2 como exploratorios y no incluir un dataset que parezca “gold standard”.

### Documentación

- [x] README actualizado al estado del piloto;
- [x] contexto curricular 0.2;
- [x] registro de fuentes primarias;
- [x] estrategia de publicación;
- [x] plan de expansión;
- [x] primer borrador de artículo metodológico;
- [ ] completar `CHANGELOG.md` desde el inicio del piloto hasta la release;
- [ ] documentar instalación/ejecución mínima reproducible;
- [ ] crear una tabla de outputs públicos por workflow;
- [ ] revisar enlaces externos y registrar fecha de acceso/alternativas archivadas cuando corresponda.

### Expansión

- [x] mecanismo reproducible de descubrimiento del Catálogo Histórico identificado;
- [x] visores CN4/CN6 descubiertos desde `libros_2023.js`;
- [ ] resolver relación documental de los dos objetos CN6 bajo generación 1993;
- [ ] decidir si los objetos de expansión forman parte de la primera release o permanecen como `expansion/experimental`;
- [ ] no mezclar semánticamente CN4/CN6 con el piloto CN5 antes de validación apropiada.

## Decisión recomendada hoy

No crear todavía una release “estable” sólo por disponer de muchos artefactos. Sí puede prepararse una **release metodológica pre-1.0** cuando estén cerradas licencia, derechos, dependencias, changelog y paquete reproducible. La release con resultados históricos semánticos debe permanecer condicionada a SEMB 0.3 humano.

## Regla de no retroactividad

El DOI o tag de una release debe identificar exactamente el estado de código/datos de esa versión. Las correcciones posteriores producen una nueva release; no se reescribe silenciosamente una versión archivada.
