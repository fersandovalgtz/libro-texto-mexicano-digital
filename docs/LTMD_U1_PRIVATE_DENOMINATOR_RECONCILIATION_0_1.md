# LTMD-U1 — conciliación de estratos con el manifiesto privado de denominadores

**Versión:** `LTMD_U1_PRIVATE_DENOMINATOR_AUDIT_0.1`  
**Fecha de auditoría:** 2026-11-09 (hora de Chihuahua)  
**Referencia de trabajo:** [#171](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues/171), [PR #179](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/pull/179)  
**Estado:** conciliación estructural y numérica ejecutada correctamente con el manifiesto **auténtico, privado**; no es validación semántica humana ni autorización de publicación de celdas.

## Fuentes y autenticidad

- Original preservado **fuera del repositorio público**: `ltmd_u1_corpus_analytics_manifest_0_1.json` dentro de Drive → LTMD-U1 corpus FTRL privado → `00_CANON_y_manifiestos/05_ANALYTICS_PRIVATE`.
- Huella SHA-256 del original cotejada con `data/research/ltmd_u1_corpus_analytics_manifest_summary_0_1.json`: `0966bba7bdd7410476e0eec42a3a5257a18994e8754666a649243b7fc4dda13a`.
- Índice Universal referido en ambos manifiestos: `aec55cc7dd83c2e1e22d26e3baf8f7ca2e35e32898827ec84e6222edd4bcf7a2`. Esta igualdad documental **no reejecuta** el índice privado FTS5.
- Fuentes públicas: `data/analytics/ltmd_analytics_indigenous_strata_0_1.csv`, `ltmd_analytics_indigenous_generation_0_1.csv` y `ltmd_analytics_indigenous_manifest_0_1.json`. Se verifican SHA y normalización legítima LF/CRLF.

## Resultados reales de conciliación

| Comprobación | Resultado |
| --- | --- |
| Celdas privadas no vacías (generación × grado × ola) | 267 |
| Estratos públicos con candidatos automatizados | 140 |
| Estratos con clave exacta en el manifiesto | **140/140** |
| Claves públicas sin denominador privado | **0** |
| Duplicados en claves privadas/publicadas | **0** |
| Estratos con candidatos > denominador de páginas | **0** |
| Celdas privadas sin fila en el agregado de candidatos | **127** |
| Suma de páginas del universo técnico | **86,549** |
| Suma de observaciones candidatas del estudio | **1,151** |
| Reconciliación de márgenes por generación, grado y ola | **Correcta** |
| Reconciliación de las 11 generaciones y sus candidatos | **Correcta** |

Las 127 celdas sin fila en el agregado **no demuestran ausencia histórica ni ausencia de OCR**. La proporción 140/267 describe únicamente la presencia de filas de candidatos en el estudio temático y **no es una cobertura de validación semántica**.

## Reproducibilidad local sin exposición de insumos

El algoritmo de auditoría está en `scripts/reconcile_u1_atlas_denominators.py`. Se ejecuta en un equipo o entorno **privado** donde el usuario ya tenga acceso legítimo al manifiesto original:

```sh
python scripts/reconcile_u1_atlas_denominators.py \
  --private-manifest "/ruta/privada/ltmd_u1_corpus_analytics_manifest_0_1.json" \
  --certificate-out "/ruta/privada/ltmd_u1_denominator_audit_certificate.json"
```

Las rutas públicas a resumen, agregado de estratos, generaciones y manifiesto indígena se resuelven por defecto en el checkout del repositorio; pueden sobrescribirse con los argumentos `--public-summary`, `--public-indigenous-manifest`, `--strata` y `--generation`.

El certificado produce **exclusivamente** resultados de consistencia agregados, estados epistemológicos y huellas conocidas; excluye todas las claves de las 267 celdas, sus páginas y tasas individuales. Tampoco emite OCR, `page_id`, `viewer_key`, URLs, imágenes ni rutas privadas. El manifiesto completo nunca debe añadirse a Git ni a artefactos públicos de CI.

El workflow `.github/workflows/test-ltmd-analytics.yml` ejecuta **12 pruebas sobre datos sintéticos declarados como tales** para impedir fugas, alterar huellas, falsificar estados científicos o introducir denominadores erróneos. **La CI pública NO ejecuta el manifiesto privado**: la conciliación real se realizó fuera del repositorio y se preserva su certificado de control, no su entrada.

## Frontera de interpretación y continuidad

La conciliación permite afirmar que existen denominadores técnicos exactos para cada uno de los 140 estratos candidatos. **No habilita automáticamente** su exportación pública ni el cálculo de indicadores curriculares validados: `human_validation_complete=false`, `semantic_ready=false` y `search_hit != historical_claim`. Los libros únicos tampoco pueden sumarse entre cohortes.

La próxima actuación, **condicionada a revisión de derechos #2 y metodología**, será determinar qué tasas estratificadas derivadas podrían entrar en el atlas de forma agregada y no sustitutiva; la implementación de una API con datos privados en staging continúa separada. No se cierra #171, no se fusiona el PR y no se despliega sitio comercial por esta conciliación.
