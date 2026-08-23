# Autoevaluación FAIR / FAIR4RS

Esta autoevaluación describe el estado de **Libro de Texto Mexicano Digital (LTMD)** como objeto digital de investigación. No constituye certificación externa.

| Dimensión | Estado | Evidencia / acción |
|---|---|---|
| Findable | parcial-avanzado | Repositorio público, `CITATION.cff`, `codemeta.json`, versionado y releases. Falta asignar DOI real a la release cuando exista depósito efectivo en Zenodo. |
| Accessible | avanzado | Código, documentación y derivados publicables accesibles en GitHub; fuentes de terceros se reconstruyen de acuerdo con las restricciones documentadas. |
| Interoperable | parcial-avanzado | Metadatos legibles por máquina, CSV/JSON y contratos metodológicos; la interoperabilidad semántica depende de cada capa y no se presume antes de validación. |
| Reusable | avanzado con límites | Licencia Apache-2.0 para software propio, `DATA_LICENSE.md` para derivados licenciables, procedencia, versiones, protocolos y documentación de incertidumbre. |
| FAIR4RS: identificación | parcial-avanzado | Releases y tags distinguen versiones; el DOI persistente se incorporará únicamente tras un depósito real. |
| FAIR4RS: metadatos | avanzado | `CITATION.cff` + CodeMeta 3.1 + README + documentación metodológica. |
| FAIR4RS: ejecutabilidad/reproducibilidad | avanzado | Dependencias de release, scripts versionados, GitHub Actions, manifiestos, hashes y reportes de integridad. |
| FAIR4RS: comunidad/contribución | mejorado en esta revisión | `CONTRIBUTING.md`, gobernanza, seguridad y reglas para cambios metodológicos. |

## Evidencia de madurez

LTMD conserva explícitamente versiones, denominadores, excepciones, relaciones documentales, integridad criptográfica y límites de la automatización. La distinción `corpus_ready` / `semantic_ready` es un control epistemológico central: la completitud técnica no se comunica como validez semántica.

## Brechas abiertas

1. **DOI de versión**: pendiente hasta que exista un depósito real en un archivo de preservación; no debe anticiparse en metadatos.
2. **Validación humana semántica**: continúa pendiente donde el protocolo la exige; los estados técnicos no deben promoverse automáticamente.
3. **Preservación externa adicional**: conviene mantener releases archivadas y, cuando el corte sea estable, registrar preservación complementaria además de GitHub.
4. **Metadatos de datos específicos**: las futuras releases pueden añadir JSON-LD/Dataset metadata por producto cuando la granularidad lo justifique.

## Criterio de actualización

Esta autoevaluación debe revisarse en cada release mayor o cuando cambien persistent identifiers, licencias, contratos de datos, política de acceso o alcance de validación.
