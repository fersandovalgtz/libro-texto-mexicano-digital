# Índice maestro de método — piloto 0.1

Este documento organiza la documentación metodológica de **Libro de Texto Mexicano Digital**. Su función es evitar que el procedimiento quede disperso entre archivos y permitir reconstruir el estado del piloto desde una sola entrada.

## 1. Diseño del piloto y contexto

- `PILOT_0_1.md` — corpus, lógica de selección y alcance del piloto.
- `CURRICULAR_CONTEXT.md` — contexto curricular e histórico de las generaciones 1972, 1988, 1993 y 2014.
- `RESEARCH_QUESTIONS.md` — preguntas de investigación candidatas.
- `ROADMAP.md` — fases, puertas de decisión y pendientes.
- `DECISIONS.md` — decisiones que modificaron el método y su justificación.

## 2. Fuentes, procedencia y derechos

- `SOURCE_REGISTER.md` — registro de fuentes institucionales, condiciones y decisiones de uso.
- `DATA_GOVERNANCE.md` — reglas de procedencia, almacenamiento, publicación y separación de capas.
- `RIGHTS_PUBLICATION_MATRIX.md` — semáforo verde/amarillo/rojo por tipo de operación y producto.
- `DRAFT_CONALITEG_RIGHTS_INQUIRY.md` — borrador de consulta institucional; **no enviado**.
- `SOURCE_AUDIT_2026-08-15.md` — auditoría inicial de la fuente CONALITEG.

## 3. Arquitectura técnica del Catálogo Histórico

- `VIEWER_ARCHITECTURE.md` — reconstrucción `HTML → x.js → claves.json → magazine.js → JPEG`.
- `ASSET_VALIDATION_2026-08-15.md` — comprobación inicial de activos y diferencias técnicas.
- `EXTRACTION_SPEC.md` — capas de datos, unidades, control de calidad y criterios de éxito.

Scripts relacionados:

- `../scripts/inspect_viewer.py`
- `../scripts/build_page_manifest.py`
- `../scripts/validate_inventory.py`

Datos relacionados:

- `../data/book_inventory.csv`
- `../data/derived/page_manifest.csv` cuando se regenere/ versione según el flujo correspondiente.

## 4. OCR — diagnóstico, cobertura y dataset técnico

- `OCR_BENCHMARK_2026-08-15.md` — detección del problema de concurrencia y configuración estable.
- `NO_TEXT_PAGE_AUDIT_2026-08-15.md` — auditoría de los 61 falsos negativos/casos problemáticos del modo basal.
- `FULL_PILOT_OCR_PROFILE_2026-08-15.md` — perfil completo basal → fallback → barrido adaptativo definitivo.
- `OCR_PAGE_METRICS_DATASET.md` — diccionario/procedencia del dataset permanente de 759 páginas.
- `OCR_TECHNICAL_STRUCTURE_BY_QUARTILE.md` — heterogeneidad técnica por posición/cuatril del libro.

Scripts relacionados:

- `../scripts/ocr_adaptive_metrics.py`
- `../scripts/audit_no_text_pages.py`
- `../scripts/diagnose_hard_ocr_page.py`
- `../scripts/summarize_ocr_structure_by_quartile.py`

Datos derivados:

- `../data/derived/ocr_full_pilot_baseline_summary.csv`
- `../data/derived/ocr_full_pilot_summary.csv`
- `../data/derived/ocr_page_metrics.csv`
- `../data/derived/no_text_page_register.csv`
- `../data/derived/no_text_page_audit_summary.csv`
- `../data/derived/ocr_structure_by_quartile.csv`

**Estado:** cobertura OCR cerrada para el piloto: **757/759 = 99.74 %** con texto aceptado; 2 páginas no textuales/marginales; 0 activos sin resolver.

## 5. Exactitud OCR — CER/WER

### Diseño de muestra

- `../data/samples/ocr_cer_wer_page_sample.csv` — muestra primaria preregistrada de 48 páginas.
- `../data/derived/cer_sample_technical_summary.csv` — auditoría de representación técnica de la muestra primaria.
- `../data/samples/ocr_cer_wer_stress_sample.csv` — suplemento de estrés de 12 páginas fallback.

### Protocolos

- `OCR_REFERENCE_ALIGNMENT_PROTOCOL.md` — `full_page` vs `crop_block`, coordenadas normalizadas y reglas de referencia humana.
- `OCR_REGION_HYPOTHESIS_METHOD.md` — extracción de hipótesis OCR espacialmente alineada desde TSV de página completa.
- `CER_WER_EXECUTION_WORKFLOW.md` — flujo extremo a extremo después de que exista referencia humana revisada.

### Scripts

- `../scripts/build_private_ocr_reference_hypotheses.py` — genera hipótesis textual **privada** alineada por región.
- `../scripts/evaluate_ocr_cer_wer.py` — calcula CER/WER y produce métricas sin texto.
- `../scripts/summarize_ocr_cer_wer.py` — agrega métricas por generación manteniendo primaria/estrés separadas.

### Capa privada

Las referencias humanas y las hipótesis OCR comparables se almacenan en una hoja privada de Google Drive. La ubicación exacta se conserva únicamente en la bitácora privada de Notion. **No se publican IDs/URLs privados ni textos de referencia en GitHub.**

**Estado:** software, muestras, almacenamiento y protocolo listos. Falta deliberadamente la referencia humana y su segunda revisión; por tanto, **no existen todavía resultados CER/WER válidos**.

## 6. Libro de códigos y anotación humana

- `CODEBOOK_0_1.md` — categorías preregistradas.
- `HUMAN_CODEBOOK_VALIDATION_PROTOCOL.md` — secuencia de validación humana.
- `ANNOTATION_MANUAL_0_1.md` — reglas de frontera y ejemplos sintéticos.
- `CODER_AGREEMENT_PROTOCOL_0_1.md` — diseño A/B, doble revisión, métricas y adjudicación.

Muestra:

- `../data/samples/human_validation_page_pool.csv` — 100 páginas, 25 por generación.

Herramientas:

- `../data/templates/coder_agreement_input_schema.csv`
- `../scripts/evaluate_coder_agreement.py`

Capa de trabajo:

Notion contiene una base de validación con 100/100 candidatos y campos separados para Código A, Código B y decisión final/adjudicada.

**Estado:** infraestructura lista; no se han automatizado ni fijado todavía resultados pedagógicos. La interpretación histórica permanece bloqueada deliberadamente hasta completar validación humana.

## 7. Modelo del futuro dataset de fragmentos

- `DATA_MODEL.md` — modelo 0.3 y reglas de trazabilidad.
- `../data/derived/fragments_schema.csv` — esquema público previsto del dataset de fragmentos.

Cadena requerida:

`book_id → page_id → fragment_id → código A/B/final → agregación`

El esquema conserva:

- calidad OCR heredada;
- CER/WER cuando exista;
- códigos A/B/final;
- versión del libro de códigos;
- estado de segunda revisión/adjudicación;
- hash y longitud del fragmento;
- estado jurídico/publicación;
- sin columna pública de texto completo por defecto.

## 8. Registro metodológico privado

La bitácora completa vive en Notion bajo **Bitácora técnica detallada — Libro de Texto Mexicano Digital**.

Funciones de la bitácora:

- registrar orden cronológico;
- conservar intentos fallidos y correcciones;
- registrar runs, parámetros y commits importantes;
- documentar cambios de interpretación;
- conservar ubicaciones privadas de Drive que no deben aparecer en GitHub;
- asegurar que el relato metodológico no dependa sólo del historial de commits.

## 9. Regla de sincronización

Cuando un hallazgo modifica el método:

1. actualizar código/esquema/documentación en GitHub;
2. registrar decisión, razón, parámetros y consecuencia en Notion;
3. actualizar el issue técnico/jurídico correspondiente si cambia su estado;
4. conservar la versión anterior cuando sea necesaria para trazabilidad;
5. no presentar como “cerrado” un paso que dependa aún de revisión humana.

## 10. Estado resumido de las puertas del piloto

| Puerta | Estado |
|---|---|
| Continuidad del corpus | Cumplida |
| Acceso reproducible | Cumplida |
| Arquitectura del visor | Cumplida |
| Cobertura OCR | **Cumplida: 99.74 %** |
| Dataset técnico por página | Cumplida |
| Política jurídica para derivados verdes | Operativa provisionalmente |
| CER/WER humano | **Pendiente** |
| Libro de códigos validado | **Pendiente** |
| Dataset de fragmentos | Pendiente de validación humana |
| Comparación historiográfica | Pendiente |
| Decisión de escalar | Pendiente |

## 11. Próximo punto de avance real

El siguiente salto científico ya no requiere más ingeniería de cobertura. Requiere:

1. construir y revisar referencias humanas para CER/WER;
2. medir exactitud real del OCR;
3. realizar inventario/codificación humana de fragmentos;
4. estabilizar el libro de códigos;
5. sólo entonces generar y analizar el dataset de fragmentos.

Cualquier automatización adicional debe servir a esas etapas y no adelantarse a ellas.
