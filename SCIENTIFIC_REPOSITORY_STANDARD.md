# Estándar científico del repositorio

Este documento fija el estándar mínimo de publicación para **Libro de Texto Mexicano Digital (LTMD)**. Se inspira en prácticas de ciencia abierta, FAIR/FAIR4RS y metadatos legibles por máquina, pero se adapta al problema específico de estudiar documentos educativos históricos con materiales fuente de terceros.

## 1. Metadatos científicos

Una release científica debe mantener consistentes:

- `CITATION.cff`;
- `codemeta.json`;
- `VERSION`;
- licencia de software y estrategia de licencia de datos;
- fecha, tag y notas de release;
- identificador persistente solo cuando exista realmente.

## 2. Reproducibilidad

La release debe declarar dependencias, pipeline, entradas permitidas, artefactos generados, hashes o manifiestos de integridad y comandos suficientes para reproducir los resultados dentro del alcance publicado.

## 3. Procedencia

Toda transformación debe conservar una ruta verificable hacia la identidad documental y la fuente. Los aliases, sustituciones de ruta, páginas faltantes, fallos de servidor y excepciones no pueden resolverse mediante imputación silenciosa.

## 4. Separación epistemológica

LTMD distingue fuente, procesamiento técnico, derivado computacional, validación humana e interpretación histórica. `corpus_ready` no implica `semantic_ready`; un pipeline completo no convierte automáticamente una señal computacional en evidencia histórica confirmada.

## 5. Calidad de datos y software

Antes de una release deben ejecutarse las validaciones automatizadas aplicables y documentarse failures, blockers y excepciones. Los cambios en definiciones, contratos, denominadores o reglas de análisis requieren documentación explícita.

## 6. FAIR / FAIR4RS

Cada release debe maximizar descubribilidad, acceso, interoperabilidad y reutilización mediante identificadores, metadatos, formatos documentados, licencias, procedencia y versionado. `FAIR_ASSESSMENT.md` debe actualizarse cuando cambien estas condiciones.

## 7. Comunicación científica

El README debe permitir comprender en pocos minutos: qué investiga LTMD, qué estado científico tiene, qué está validado y qué no, cómo reproducir el trabajo, cómo citarlo y dónde encontrar la documentación técnica. La complejidad detallada debe enlazarse a `docs/` en lugar de convertir la portada del repositorio en un cuaderno de laboratorio completo.

## 8. Releases

Una release pública debe incluir como mínimo:

- tag y versión coherentes;
- metadatos científicos actualizados;
- notas de release;
- reporte de reproducibilidad o integridad;
- documentación de limitaciones y cambios;
- artefactos o rutas de reconstrucción suficientes;
- DOI solo después de un depósito real y verificable.

Este estándar es normativo para la publicación del repositorio, no una afirmación de certificación externa.
