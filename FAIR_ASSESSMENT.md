# Autoevaluación FAIR / FAIR4RS

Esta autoevaluación describe el estado de **Libro de Texto Mexicano Digital (LTMD)** como objeto digital de investigación. No constituye certificación externa.

| Dimensión | Estado | Evidencia / acción |
|---|---|---|
| Findable | parcial-avanzado | Repositorio público, `CITATION.cff`, `codemeta.json`, versionado y releases. Falta asignar DOI real a la release cuando exista depósito efectivo en Zenodo. |
| Accessible | avanzado | Código, documentación y derivados publicables accesibles en GitHub; fuentes de terceros se reconstruyen de acuerdo con las restricciones documentadas. |
| Interoperable | parcial-avanzado | Metadatos legibles por máquina, CSV/JSON y contratos metodológicos; la interoperabilidad semántica depende de cada capa y no se presume antes de validación. |
| Reusable | avanzado con límites | Licencia Apache-2.0 para software propio, `DATA_LICENSE.md` para derivados licenciables, procedencia, versiones, protocolos, documentación de incertidumbre y frontera explícita entre infraestructura abierta y servicios operados. |
| FAIR4RS: identificación | parcial-avanzado | Releases y tags distinguen versiones; el DOI persistente se incorporará únicamente tras un depósito real. |
| FAIR4RS: metadatos | avanzado | `CITATION.cff` + CodeMeta 3.1 + README + documentación metodológica. |
| FAIR4RS: ejecutabilidad/reproducibilidad | avanzado | Dependencias de release, scripts versionados, GitHub Actions, manifiestos, hashes, reportes de integridad y auditoría automatizada de la superficie del repositorio. |
| FAIR4RS: comunidad/contribución | avanzado | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, gobernanza, plantilla científica de PR y formularios diferenciados de issues. |

## Evidencia de madurez

LTMD conserva explícitamente versiones, denominadores, excepciones, relaciones documentales, integridad criptográfica y límites de la automatización. La distinción `corpus_ready` / `semantic_ready` es un control epistemológico central: la completitud técnica no se comunica como validez semántica.

La superficie pública diferencia además **LTMD Open** de **LTMD Research** y **LTMD Services**. Esta separación documenta qué puede publicarse como infraestructura científica abierta y qué pertenece a una instancia operada, sin transformar materiales fuente de terceros en activos exclusivos ni alterar las obligaciones de procedencia.

## Brechas abiertas

1. **DOI de versión**: pendiente hasta que exista un depósito real en un archivo de preservación; no debe anticiparse en metadatos.
2. **Validación humana semántica**: continúa pendiente donde el protocolo la exige; los estados técnicos no deben promoverse automáticamente.
3. **Preservación externa adicional**: conviene mantener releases archivadas y, cuando el corte sea estable, registrar preservación complementaria además de GitHub.
4. **Metadatos de datos específicos**: las futuras releases pueden añadir JSON-LD/Dataset metadata por producto cuando la granularidad lo justifique.
5. **Protección efectiva de `main`**: el contenido del repositorio ya define el flujo por pull request y status checks, pero la protección de rama es una configuración externa a Git y debe verificarse y habilitarse en GitHub.
6. **Permisos explícitos en workflows heredados**: los controles nuevos usan mínimo privilegio; los workflows históricos sin `permissions:` explícito deben auditarse gradualmente antes de endurecerlos para evitar regresiones operativas.

## Criterio de actualización

Esta autoevaluación debe revisarse en cada release mayor o cuando cambien persistent identifiers, licencias, contratos de datos, política de acceso, alcance de validación, superficie pública o controles de publicación.