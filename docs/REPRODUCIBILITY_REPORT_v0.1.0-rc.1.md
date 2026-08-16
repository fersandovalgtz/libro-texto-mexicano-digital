# Reporte de reproducibilidad — LTMD v0.1.0-rc.1

Fecha de corte: **2026-08-15**

## Dictamen

La candidata **v0.1.0-rc.1** alcanza readiness técnico y documental para publicación como release candidate. El preflight `LTMD_RELEASE_PREFLIGHT_0.3` registra:

- `rc_technical_ready=true`;
- `publish_ready=true`;
- `technical_failures=[]`;
- `publish_blockers=[]`;
- `LTMD_INTEGRITY_0.6` con **166/166** artefactos críticos;
- recomputación SHA-256 de los 166 artefactos críticos con **cero discrepancias**;
- verificación de cifras del artículo metodológico en PASS.

Este dictamen se refiere a la **release metodológica/técnica**. SEMB 0.3 continúa en `WAITING_HUMAN_REFERENCE` y el corpus expandido continúa `corpus_ready`, no `semantic_ready`.

## Corpus técnico del corte

| Capa | Activos reales | Fragmentos técnicos | Estado |
|---|---:|---:|---|
| Piloto CN5 | 759 | 9,594 | técnico cerrado; SEMB 0.2 diagnóstico |
| Expansión CN4/CN6 | 1,888 JPEG | 19,067 | `corpus_ready`, no `semantic_ready` |
| Ciencias Naturales Ola 2 | 3,177 JPEG | 36,195 | `corpus_ready`, no `semantic_ready` |
| **Total** | — | **64,856** | ocurrencias técnicas, no unidades históricas independientes |

La familia estricta _Ciencias Naturales_ comprende 37 visores y 35/37 tienen resolución completa de activos. Aliases, revisiones y reutilizaciones se conservan como relaciones documentales y no se borran para inflar independencia estadística.

## Integridad

`LTMD_INTEGRITY_0.6` amplía el corte 0.5 para incluir identidad de release, licencias, documentación reproducible y controles de publicación. El preflight exige simultáneamente:

- `critical_present_count == critical_count == 166`;
- `missing_critical == []`;
- recomputación SHA-256 de cada entrada crítica y cero mismatches;
- claim check del manuscrito en PASS y sin failures;
- ausencia de fuentes/working files prohibidos en Git;
- permanencia cerrada de los outputs humanos de SEMB 0.3;
- licencias materializadas y consistentes con la política documentada.

El manifiesto debe regenerarse sobre el **corte documental final anterior al tag**. Un commit móvil de `main` no es, por sí mismo, una release archivada.

## Runtime

Entorno de referencia: **Ubuntu 24.04**.

Dependencia Python directa fijada para SEMB 0.2:

```text
sentence-transformers==5.6.1
```

Modelo:

```text
intfloat/multilingual-e5-small
revision: fd1525a9fd15316a2d503bf26ab031a61d056e98
```

OCR:

```text
tesseract-ocr
tesseract-ocr-spa
```

La candidata declara **reproducibilidad de procedimiento/artefactos alta** y **congelamiento de entorno patch/wheel parcial**: Python patch-level y el árbol transitivo de wheels todavía no están totalmente fijados.

## Procedencia y reconstrucción de fuentes

Los pipelines que requieren páginas fuente resuelven el activo esperado, descargan temporalmente la imagen, calculan SHA-256, abortan ante discrepancia, ejecutan la derivación y eliminan el activo temporal. La release no necesita incorporar imágenes o transcripciones íntegramente reconstruidas para que las métricas derivadas sean auditables.

## Derechos y licencias

- software original: **Apache License 2.0** (`LICENSE`);
- derivados originales licenciables: **CC BY 4.0** (`DATA_LICENSE.md`);
- materiales fuente CONALITEG/SEP/terceros: excluidos expresamente de ambas concesiones salvo derecho independiente aplicable.

La validación de licencias es parte del preflight, pero permanece separada de la validación científica.

## Protección contra contaminación de release

El preflight inspecciona `git ls-files` y falla ante contenido rastreado bajo `private/`, `data/raw/`, `data/work/`, `downloads/` o `working/`, así como extensiones fuente/archivo prohibidas definidas por el control. `.gitignore` excluye rutas temporales y secretos `.env`.

## Gate semántico

La release candidata debe conservar ausentes:

- `data/validation/semb03_human_reference_consensus.csv`;
- `data/validation/semb03_locked_validation_reference.csv`;
- `data/derived/semb03_model_lock.json`;
- `data/derived/semb03_locked_validation_result.json`.

Su ausencia no es una incompletitud accidental, sino evidencia de que **no se ha saltado el protocolo humano preregistrado**.

## CI y verificaciones

Los controles de release incluyen manifiesto de integridad científica, verificador de cifras del manuscrito, auditorías de procedencia/dependencia y `check-release-candidate`. El preflight corre sobre Ubuntu 24.04 y publica:

- `data/derived/release_candidate_preflight.json`;
- `data/derived/release_candidate_preflight.md`.

Para evitar carreras entre regeneración del manifiesto y comprobación final existe un disparador determinista de preflight que no modifica el conjunto crítico.

## Blockers actuales

**Ninguno según el preflight:** `publish_blockers=[]`.

La ausencia de DOI no es un blocker previo al tag. El DOI debe resultar de un depósito real en Zenodo y no debe inventarse anticipadamente.

## Secuencia exacta para el tag

1. cerrar el corte documental;
2. regenerar `LTMD_INTEGRITY_0.6`;
3. ejecutar preflight determinista y exigir `publish_ready=true` y cero mismatches SHA-256;
4. etiquetar exactamente el commit verificado;
5. publicar GitHub Release asociada;
6. dejar que Zenodo archive la release/tag;
7. incorporar el DOI versionado real posteriormente, sin reescribir silenciosamente el tag archivado.

## Conclusión

**v0.1.0-rc.1 es una release candidate metodológica publicable y auditable, no una afirmación de completitud semántica ni una licencia sobre materiales fuente.** La siguiente frontera científica continúa siendo la referencia humana de SEMB 0.3.
