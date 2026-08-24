# Protocolo de ejecución integral FTRL W5 Historia

Versión operativa: 0.2  
Estado: preregistrado y corregido antes de la primera corrida OCR integral W5  
Alcance: LTMD-U1, ola W5 Historia

## Propósito

Este protocolo fija las condiciones de la primera ejecución integral de la Full-Text Research Layer (FTRL) sobre W5 Historia. Su función es evitar que la definición de completitud, las verificaciones de integridad o el tratamiento de los resultados se modifiquen después de observar el corpus completo.

La corrida integral no constituye por sí misma validación semántica ni demuestra afirmaciones historiográficas. Produce una infraestructura de recuperación trazable que deberá someter cada candidato relevante a verificación contra la página fuente.

## Corrección preregistrada de cardinalidad — 24 de agosto de 2026

La primera activación integral, GitHub Actions run `32743452417`, se detuvo deliberadamente en el preflight **antes de ejecutar OCR**. El gate calculó directamente desde `data/catalog/ltmd_u1_w5_history_processing_inventory.csv` la suma de `direct_source_jpegs` para los 15 objetos marcados como `is_canonical_processing_object=1` y obtuvo **2,653 páginas**.

La expectativa previa de 2,443 páginas era un error aritmético de la preparación del workflow. No provenía del inventario y no se modifica para acomodar un resultado observado: la corrección se realiza precisamente porque el gate reproducible rechazó esa cifra antes de procesar el corpus completo. Por tanto, la cardinalidad preregistrada vigente es **2,653**.

## Cohorte congelada

La topología de procesamiento vigente contiene:

- 18 identidades históricas técnicamente cubiertas;
- 15 objetos canónicos de procesamiento;
- 2,653 JPEG fuente admitidos para OCR;
- tres identidades 2018 representadas técnicamente mediante relaciones de alias de ruta demostradas hacia 2019, sin borrar su identidad histórica.

La cardinalidad esperada se deriva de `data/catalog/ltmd_u1_w5_history_processing_inventory.csv` y no debe ajustarse para hacer coincidir una corrida incompleta.

## Ejecución

La referencia ejecutable es:

```bash
python scripts/run_ftrl_w5_pilot.py \
  --full \
  --run-preregistered-queries \
  --output-dir local/ftrl
```

El workflow `.github/workflows/validate-ftrl-w5-full.yml` reproduce este procedimiento en un runner limpio de GitHub Actions y exige Tesseract con datos `spa`, SQLite FTS5 y Python 3.12.

## Gates de completitud

Una corrida integral sólo puede clasificarse como validada si cumple simultáneamente:

1. 2,653 registros de página FTRL;
2. 2,653 filas en la tabla `pages` de SQLite;
3. 2,653 filas FTS5;
4. `PRAGMA integrity_check = ok`;
5. 15 visores canónicos de procesamiento;
6. 18 identidades históricas representadas en el índice;
7. cero páginas con tamaño de fuente ausente en el manifiesto de procedencia;
8. commit Git exacto y contexto de CI registrados en el manifiesto de corrida;
9. outputs restringidos —OCR por página, SQLite y candidatos con snippets— fuera de publicación y cubiertos por `.gitignore`;
10. artefactos públicos limitados al manifiesto de corrida sin texto y al resumen agregado de consultas sin snippets.

Cualquier discrepancia mantiene la corrida en estado diagnóstico y no autoriza declarar W5 completo.

## Consultas preregistradas

La corrida integral ejecutará el protocolo congelado en `data/research/ltmd_ftrl_w5_preregistered_queries.csv` únicamente después de validar el corpus y el índice.

El archivo local de candidatos puede contener snippets OCR y no debe versionarse ni redistribuirse sin revisión separada de derechos. El resumen público sólo podrá contener conteos, distribuciones, hashes de expresiones de consulta, reglas de verificación y metadatos no sustitutivos.

## Interpretación

Se mantienen como reglas obligatorias:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`;
- un alias técnico no implica identidad bibliográfica;
- una coincidencia de búsqueda debe verificarse contra el activo fuente antes de utilizarse como evidencia histórica;
- una ausencia de hits debe evaluarse a la luz de cobertura, calidad OCR y variantes de recuperación.

## Auditoría posterior obligatoria

Después de una corrida integral válida deberán revisarse manualmente, como mínimo:

- páginas con `search_text` vacío;
- páginas del extremo inferior de confianza OCR;
- todas las páginas candidatas utilizadas en una afirmación historiográfica;
- controles de errores OCR previsibles para las consultas preregistradas.

La página `H1993P4HI198:src0000`, que produjo cero caracteres en el piloto de 10 páginas, y `H1993P4HI198:src0010`, que registró la confianza mínima de ese piloto, permanecen casos prioritarios de auditoría técnica.

## Evidencia pública esperada

La primera corrida integral válida debe producir, como mínimo:

- un manifiesto `LTMD_FTRL_RUN_0.1` sin texto fuente;
- un resumen `LTMD_FTRL_QUERY_PROTOCOL_0.1` sin expresiones en claro ni snippets;
- identificación del commit exacto y del run de GitHub Actions;
- cardinalidades finales y distribución de confianza OCR;
- registro explícito de páginas sin texto recuperable;
- acta metodológica posterior que distinga diagnóstico técnico de resultados históricos.

Este protocolo no anticipa resultados de las consultas ni autoriza publicar el OCR íntegro.