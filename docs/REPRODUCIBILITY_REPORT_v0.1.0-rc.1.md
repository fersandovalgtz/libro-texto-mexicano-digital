# Reporte de reproducibilidad — LTMD v0.1.0-rc.1

Fecha de corte: **2026-08-15**

## Dictamen

La candidata **v0.1.0-rc.1** alcanza **readiness técnico de release candidate**. El preflight automatizado reporta `rc_technical_ready=true`, `technical_failures=[]`, `LTMD_INTEGRITY_0.5` con **150/150** artefactos críticos y verificación de cifras del artículo metodológico en PASS.

La candidata **no está todavía lista para publicación pública como release cerrada**: `publish_ready=false` mientras no se materialicen una licencia del código propio y una licencia/política explícita de reutilización de los derivados originales de LTMD. Este bloqueo jurídico se mantiene separado de la reproducibilidad técnica.

## Corpus técnico del corte

| Capa | Activos reales | Fragmentos técnicos | Estado |
|---|---:|---:|---|
| Piloto CN5 | 759 | 9,594 | técnico cerrado; SEMB 0.2 diagnóstico |
| Expansión CN4/CN6 | 1,888 JPEG | 19,067 | `corpus_ready`, no `semantic_ready` |
| Ciencias Naturales Ola 2 | 3,177 JPEG | 36,195 | `corpus_ready`, no `semantic_ready` |
| **Total** | — | **64,856** | ocurrencias técnicas, no unidades históricas independientes |

La familia estricta *Ciencias Naturales* comprende 37 visores y 35/37 tienen resolución completa de activos. Los aliases, revisiones y reutilizaciones se conservan como relaciones documentales y no se borran para inflar independencia estadística.

## Integridad

El corte científico utiliza `LTMD_INTEGRITY_0.5`. El preflight exige simultáneamente:

- `critical_present_count == critical_count == 150`;
- `missing_critical == []`;
- `METHODS_ARTICLE_CLAIMS_0.2` en PASS y sin failures;
- ausencia de fuentes/working files prohibidos en Git;
- permanencia cerrada de los outputs humanos de SEMB 0.3.

El manifiesto debe regenerarse una vez más sobre el **commit exacto que vaya a etiquetarse**. Este reporte no convierte un commit móvil de `main` en release archivada.

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

El flujo semántico congelado comprueba Tesseract 5.3.4. Los pipelines técnicos de catálogo, procedencia, OCR, PAGESTRUCT y FRAGSEG utilizan ampliamente la biblioteca estándar de Python y Tesseract externo.

La candidata declara **reproducibilidad de procedimiento/artefactos alta** y **congelamiento de entorno patch/wheel parcial**: Python patch-level y el árbol transitivo de wheels todavía no están totalmente fijados. Esta limitación está documentada, no ocultada.

## Procedencia y reconstrucción de fuentes

Los pipelines que requieren páginas fuente:

1. resuelven la URL/activo esperado;
2. descargan temporalmente la imagen;
3. calculan SHA-256;
4. abortan si el hash no coincide con el manifiesto;
5. ejecutan la derivación correspondiente;
6. eliminan el activo temporal.

La release no necesita incorporar imágenes o transcripciones íntegramente reconstruidas para que las métricas derivadas sean auditables.

## Protección contra contaminación de release

El preflight inspecciona `git ls-files` y falla si encuentra contenido rastreado bajo:

- `private/`;
- `data/raw/`;
- `data/work/`;
- `downloads/`;
- `working/`;

También rechaza extensiones fuente/archivo como PDF, TIFF, JP2 o ZIP. `.gitignore` excluye expresamente las rutas temporales y secretos `.env`.

## Gate semántico

La release candidata debe conservar ausentes:

- `data/validation/semb03_human_reference_consensus.csv`;
- `data/validation/semb03_locked_validation_reference.csv`;
- `data/derived/semb03_model_lock.json`;
- `data/derived/semb03_locked_validation_result.json`.

Su ausencia en este corte no es incompletitud accidental, sino evidencia de que **no se ha saltado el protocolo humano preregistrado**.

## CI y verificaciones

Para el corte candidato se consideran controles de release:

- manifiesto de integridad científica;
- verificador de cifras del artículo metodológico;
- auditorías de procedencia y dependencia documental de las capas cerradas;
- `check-release-candidate`, que separa readiness técnico de readiness de publicación.

El workflow de preflight se ejecuta sobre Ubuntu 24.04 y publica sus resultados en:

- `data/derived/release_candidate_preflight.json`;
- `data/derived/release_candidate_preflight.md`.

## Blockers actuales

Sólo quedan dos blockers explícitos de publicación identificados por el preflight:

1. `code_license_not_selected`;
2. `derived_data_license_not_selected`.

No se considera blocker previo al tag la ausencia de DOI: el DOI debe existir **después** de que GitHub/Zenodo archive una release real, nunca inventarse anticipadamente.

## Secuencia exacta para el tag definitivo

1. resolver/documentar licencias;
2. ejecutar nuevamente los workflows de verificación relevantes;
3. regenerar `LTMD_INTEGRITY_0.5` sobre el commit final;
4. ejecutar `check-release-candidate` y exigir `publish_ready=true`;
5. etiquetar exactamente ese commit;
6. publicar la release GitHub asociada al tag;
7. dejar que Zenodo archive esa release/tag;
8. incorporar el DOI versionado real a `CITATION.cff` y README en una versión posterior o en la metadata permitida sin reescribir silenciosamente el tag archivado.

## Conclusión

**v0.1.0-rc.1 es una candidata metodológica técnicamente auditable, no una afirmación de completitud semántica ni una licencia implícita sobre materiales fuente.** La frontera restante para publicación es jurídica/documental, mientras SEMB 0.3 continúa correctamente bloqueado por referencia humana.
