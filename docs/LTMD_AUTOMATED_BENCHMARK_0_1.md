# LTMD Automated Benchmark 0.1

Versión: `LTMD_AUTOMATED_BENCHMARK_0.1`

## Propósito

Este benchmark formaliza el máximo nivel de evaluación **íntegramente automatizable** de LTMD sin recurrir a referencia o codificación humana. Su objetivo es medir reproducibilidad, integridad, consistencia documental, estabilidad de metadatos, cobertura técnica y cumplimiento de guardas epistemológicas y jurídicas.

No mide validez semántica humana y no debe presentarse como sustituto de ella.

> `automated_benchmark_passed != human_semantic_validation`

> `computational_consistency != construct_validity`

> `reproducible != historically_true`

## Qué sí evalúa

### A. Integridad documental U1

- cardinalidad exacta del registro de retenciones;
- unicidad de `viewer_key` dentro del registro residual;
- estados de retención admitidos;
- separación entre retenciones activas y excepciones finales;
- coherencia con el universo U1 declarado.

### B. Cohorte contemporánea CONALITEG 2026–2027

- 42 entradas de catálogo;
- 39 visores únicos;
- duplicación únicamente de los tres visores docentes compartidos previstos;
- ciclo, nivel y estado `catalog_metadata_only` coherentes;
- separación explícita entre catálogo y admisión técnica.

### C. Coherencia de release

- `VERSION`, `CITATION.cff`, `codemeta.json` y README deben señalar la misma versión;
- las cifras públicas U1 deben permanecer sincronizadas: 542 visores, 524 de cobertura técnica efectiva y 492 objetos canónicos;
- una candidata no debe anticipar DOI inexistente.

### D. Guardas epistemológicas

El benchmark exige que la documentación preserve, como mínimo:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `computational_candidate != semantic_ready`;
- `publicly_accessible != openly_licensed`;
- la prohibición de tratar consistencia automática como verdad de referencia humana.

### E. Frontera de derechos

El repositorio debe conservar separadas:

- licencia Apache-2.0 del software;
- CC BY 4.0 sólo para derivados originales jurídicamente licenciables por LTMD;
- obras fuente SEP/CONALITEG y de terceros, que no quedan relicenciadas;
- procesamiento local/temporal frente a redistribución pública.

El benchmark comprueba además que no aparezcan PDF/JPEG fuente bajo las rutas públicas de catálogo/derivados que gobierna esta batería.

### F. Reproducibilidad del propio benchmark

El runner usa únicamente biblioteca estándar de Python, entradas versionadas y una baseline JSON explícita. Produce un JSON ordenado de forma determinista y falla con código distinto de cero si algún invariante obligatorio deja de cumplirse.

## Métricas de salida

El resultado incluye:

- `u1_universe`;
- `u1_effective_technical_coverage`;
- `u1_canonical_objects`;
- `u1_retained_total`;
- `u1_active_retentions`;
- `u1_final_exceptions`;
- `contemporary_catalog_entries`;
- `contemporary_unique_viewers`;
- `contemporary_shared_viewers`;
- `release_version`;
- estados booleanos por cada guardia;
- `engineering_readiness_score` de 0 a 100.

`engineering_readiness_score` es un resumen de invariantes técnicos. **No es una medida de calidad historiográfica, precisión semántica, validez de constructo ni verdad histórica.**

## Interpretación

Un resultado `PASS` permite afirmar:

> La superficie pública de LTMD satisface la batería automatizada preregistrada de integridad, coherencia, trazabilidad y gobernanza computacional correspondiente a esta versión.

No permite afirmar:

- que el OCR sea fiel a nivel de carácter frente a una transcripción humana;
- que una categoría automática represente adecuadamente un constructo historiográfico;
- que un resultado semántico constituya evidencia histórica validada;
- que ausencia de hits equivalga a ausencia histórica;
- que un libro públicamente accesible tenga licencia abierta.

## Ejecución

```bash
python scripts/run_automated_benchmark.py --check
python scripts/run_automated_benchmark.py --output /tmp/ltmd-benchmark.json
```

La baseline pública está en:

- `data/benchmarks/ltmd_automated_benchmark_0_1_baseline.json`

El workflow de CI es:

- `.github/workflows/automated-benchmark.yml`

## Relación con validaciones humanas históricas

Los issues #95, #123 y #124 pueden permanecer documentados como protocolos históricos o deuda no ejecutada, pero **no son dependencias del Automated Benchmark 0.1**. Ningún estado producido por esta batería debe promover automáticamente `text_verified` o `semantic_ready`.

La decisión metodológica vigente es maximizar la ciencia reproducible que puede sostenerse sin validación humana y etiquetar explícitamente el techo epistemológico de ese enfoque.