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

El repositorio debe mantener controles automatizados sobre su propia superficie de publicación: archivos normativos, metadatos, exclusión de artefactos privados/locales, plantillas de contribución y workflows críticos. Los controles nuevos no deben romper silenciosamente pipelines heredados; la deuda detectada debe convertirse en advertencia o migración explícita hasta que pueda elevarse con seguridad a gate obligatorio.

## 6. Seguridad de automatización

Los workflows deben declarar el menor conjunto de permisos de `GITHUB_TOKEN` que requieran. Los secretos no se versionan ni se incorporan a artefactos públicos. Las dependencias automatizadas deben actualizarse mediante cambios revisables y trazables.

Los workflows existentes sin permisos explícitos deben auditarse progresivamente antes de imponer cambios masivos que puedan alterar su comportamiento.

## 7. Gobernanza de cambios

`main` es la rama canónica y debe tratarse como superficie de publicación. Los cambios ordinarios deben entrar por ramas específicas y pull requests auditables. La plantilla de pull request debe exigir propósito, evidencia, validación, impacto científico, derechos, privacidad, reproducibilidad y riesgos.

Cuando la configuración de GitHub lo permita, `main` debe protegerse frente a borrados o force-push y exigir los status checks críticos antes de integrar cambios. La configuración efectiva de GitHub debe verificarse separadamente porque no forma parte del contenido versionado del repositorio.

## 8. Salud comunitaria y triage

El repositorio debe mantener, en ubicaciones reconocidas por GitHub, al menos:

- `README.md`;
- `LICENSE` y política diferenciada de datos;
- `CONTRIBUTING.md`;
- `CODE_OF_CONDUCT.md`;
- `SECURITY.md`;
- `SUPPORT.md`;
- plantilla de pull request;
- formularios diferenciados para errores técnicos, problemas de datos/metodología y propuestas de capacidad.

El triage debe impedir que una corrección técnica, una discrepancia documental y una afirmación científica nueva se traten como equivalentes.

## 9. FAIR / FAIR4RS

Cada release debe maximizar descubribilidad, acceso, interoperabilidad y reutilización mediante identificadores, metadatos, formatos documentados, licencias, procedencia y versionado. `FAIR_ASSESSMENT.md` debe actualizarse cuando cambien estas condiciones.

Para datos y derivados, la reutilización exige además procedencia suficientemente detallada, licencia clara cuando exista capacidad jurídica para otorgarla y uso de formatos y convenciones sostenibles para la comunidad.

## 10. Fronteras de producto y publicación

El repositorio público corresponde a **LTMD Open**. Las superficies operadas **LTMD Research** y **LTMD Services** pueden utilizar la infraestructura abierta sin alterar las licencias ni convertir materiales fuente de terceros en activos exclusivos.

`docs/LTMD_PRODUCT_BOUNDARIES.md` es normativo para decidir qué pertenece al repositorio público y qué debe permanecer en infraestructura operada o privada.

## 11. Comunicación científica

El README debe permitir comprender en pocos minutos: qué investiga LTMD, qué estado científico tiene, qué está validado y qué no, cómo reproducir el trabajo, cómo citarlo y dónde encontrar la documentación técnica. La complejidad detallada debe enlazarse a `docs/` en lugar de convertir la portada del repositorio en un cuaderno de laboratorio completo.

## 12. Releases

Una release pública debe incluir como mínimo:

- tag y versión coherentes;
- metadatos científicos actualizados;
- notas de release;
- reporte de reproducibilidad o integridad;
- documentación de limitaciones y cambios;
- artefactos o rutas de reconstrucción suficientes;
- DOI solo después de un depósito real y verificable.

Este estándar es normativo para la publicación del repositorio, no una afirmación de certificación externa.