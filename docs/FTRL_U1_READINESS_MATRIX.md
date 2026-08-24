# FTRL U1 — matriz de preparación por cohorte

Versión: `LTMD_FTRL_U1_READINESS_0.1`  
Fecha: 2026-08-24  
Universo de referencia: LTMD-U1, 542 identidades documentales.

## Propósito

Esta matriz define el orden de escalamiento de la Full-Text Research Layer (FTRL) desde W5 hacia LTMD-U1 sin convertir el cierre técnico de una ola en una afirmación de preparación OCR, validación textual o validez semántica.

La unidad operativa de preparación es la **cohorte fuente-admitida**, no la ola completa. Las identidades retenidas o cerradas como excepción técnica permanecen fuera del procesamiento FTRL mientras no exista evidencia nueva que modifique su estado.

## Estados

- `REFERENCE_FULL_VALIDATION`: cohorte de referencia con corrida FTRL integral en validación; no implica todavía auditoría humana de OCR ni validación historiográfica.
- `PREFLIGHT_REQUIRED`: cohorte técnicamente cerrada, candidata a FTRL, pero todavía requiere un preflight específico que demuestre inventario canónico, resolución de activos, cardinalidad de páginas y validación SHA-256 antes de OCR masivo.
- `PREFLIGHT_REQUIRED_WITH_EXCLUSIONS`: igual que el estado anterior, pero el alcance FTRL debe excluir de forma explícita y contable las identidades retenidas o las excepciones finales.

Ninguno de estos estados equivale a `semantic_ready`.

## Matriz

| Ola | Dominio | Plan | Cobertura efectiva | Canónicos | Residual fuera de cobertura | Estado FTRL | Alcance permitido antes de OCR |
|---|---|---:|---:|---:|---:|---|---|
| W1 | Ciencias Naturales | 40 | 40 | 36 | 0 | `PREFLIGHT_REQUIRED` | 36 canónicos; confirmar manifiestos y cardinalidad de páginas |
| W2 | Matemáticas | 64 | 60 | 57 | 4 activas | `PREFLIGHT_REQUIRED_WITH_EXCLUSIONS` | 57 canónicos; excluir las 4 retenciones activas |
| W3 | Español / Lengua | 130 | 130 | 114 | 0 | `PREFLIGHT_REQUIRED` | 114 canónicos; confirmar manifiestos y cardinalidad de páginas |
| W4 | Ciencias Sociales | 14 | 14 | 14 | 0 | `PREFLIGHT_REQUIRED` | 14 canónicos; confirmar manifiestos y cardinalidad de páginas |
| W5 | Historia | 18 | 18 | 15 | 0 | `REFERENCE_FULL_VALIDATION` | 15 canónicos / 18 identidades; referencia metodológica |
| W6 | Geografía / Atlas | 42 | 42 | 37 | 0 | `PREFLIGHT_REQUIRED` | 37 canónicos; confirmar manifiestos y cardinalidad de páginas |
| W7 | Formación Cívica y Ética | 30 | 25 | 25 | 5 activas | `PREFLIGHT_REQUIRED_WITH_EXCLUSIONS` | 25 canónicos; excluir las 5 retenciones activas |
| W8 | Artes | 20 | 16 | 16 | 4 activas | `PREFLIGHT_REQUIRED_WITH_EXCLUSIONS` | 16 canónicos; excluir las 4 retenciones activas |
| W9 | Educación Física | 4 | 4 | 4 | 0 | `PREFLIGHT_REQUIRED` | 4 canónicos; confirmar manifiestos y cardinalidad de páginas |
| W10 | Integrados / Multiarea | 69 | 68 | 68 | 1 final | `PREFLIGHT_REQUIRED_WITH_EXCLUSIONS` | 68 canónicos; excluir la excepción técnica final |
| W11 | Otros / No clasificados | 111 | 107 | 106 | 4 finales | `PREFLIGHT_REQUIRED_WITH_EXCLUSIONS` | 106 canónicos; conservar la diferencia identidad/canónico y excluir 4 excepciones finales |
| **Total** |  | **542** | **524** | **492** | **18** |  |  |

## Regla de promoción a FTRL ejecutable

Una cohorte sólo podrá pasar de `PREFLIGHT_REQUIRED*` a una ejecución OCR masiva cuando un preflight reproducible confirme, como mínimo:

1. conjunto congelado de identidades históricas y objetos canónicos;
2. manifiesto de activos por objeto canónico;
3. cardinalidad exacta de páginas fuente admitidas;
4. resolución completa o excepciones internas explícitas y preservadas;
5. SHA-256 verificable de cada activo admitido antes de OCR;
6. relaciones de alias documentadas sin OCR redundante;
7. salida restringida bajo `local/` y evidencia pública libre de texto fuente extenso;
8. runner y validador capaces de fallar ante deriva de inventario o procedencia.

La prueba de W5 mostró por qué este gate debe ser obligatorio: una cardinalidad preregistrada obsoleta debe producir un fallo temprano, no una corrida silenciosamente inconsistente.

## Orden de escalamiento recomendado

W5 permanece como implementación de referencia hasta cerrar su validación integral. Después, el orden técnico debe priorizar cohortes pequeñas y cerradas para comprobar que el runner generalizado no contiene supuestos específicos de Historia: W9 y W4 son candidatos naturales para ese smoke test. Sólo entonces conviene escalar a cohortes mayores como W1, W6 y W3. W2, W7, W8, W10 y W11 pueden procesarse por su cohorte admitida, pero sus exclusiones deben viajar en manifiestos, resúmenes y reportes de cobertura.

Este orden es metodológico, no historiográfico: no expresa prioridad sustantiva entre materias.

## Guardas epistemológicas

- `corpus_ready != semantic_ready`
- `ocr_available != text_verified`
- `search_hit != historical_claim`
- `zero_hits != demonstrated_absence`
- cierre técnico de ola != preparación FTRL demostrada
- excepción técnica final != fuente resuelta

## Fuentes canónicas de estado

La matriz debe mantenerse sincronizada con `data/catalog/ltmd_u1_coverage.md`, `docs/LTMD_U1_MASTER_PLAN_0_3.md` y `data/catalog/ltmd_u1_retained_source_register.csv`. Cuando esas fuentes cambien, esta matriz no debe actualizarse por inferencia manual: el siguiente paso es automatizar una comprobación de consistencia en CI.
