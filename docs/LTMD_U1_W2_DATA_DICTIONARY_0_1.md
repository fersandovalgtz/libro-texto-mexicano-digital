# LTMD-U1 W2 — diccionario de datos y contrato de capas 0.1

Este documento describe el contrato técnico usado por Matemáticas W2. No define constructos pedagógicos ni sustituye una validación semántica.

## 1. Identidad documental

`viewer_key` identifica el visor del catálogo y nunca se elimina por deduplicación. `catalog_generation` es una agrupación del catálogo, no un año de edición. `book_id`, cuando existe, es un identificador interno de procesamiento y tampoco sustituye la referencia bibliográfica.

## 2. Fuente y procedencia

La auditoría cruda conserva por posición:

- `viewer_page`: posición declarada del visor;
- `source_image_index`: índice solicitado en la infraestructura pública;
- `source_asset_url`: URL probada originalmente;
- `asset_status`: resultado crudo de esa ruta;
- `byte_size` y `sha256`: evidencia de los bytes cuando existe JPEG;
- `is_final_declared_position`: permite distinguir un 404 final candidato a terminal sintético de un hueco interno.

Un `internal_unserved` no se convierte automáticamente en página faltante, ausencia bibliográfica o dato descartable.

## 3. Manifiesto reconciliado

La reconciliación **no sobrescribe** la fuente cruda. Añade:

- `effective_asset_status`: `source_jpeg`, `source_jpeg_recovered`, `terminal_synthetic` o `unresolved`;
- `effective_asset_url`: URL realmente usada para reconstruir temporalmente el byte;
- `effective_sha256` / `effective_byte_size`: fingerprint de la representación efectiva;
- `effective_source_viewer_key`: visor del que procede físicamente la representación efectiva;
- `resolution_method`: método por el que se obtuvo la representación;
- `original_anomaly_preserved`: señala que la ruta original presentaba anomalía aunque exista resolución efectiva.

Una recuperación por alineamiento de vecinos sólo resuelve **esa posición**. No demuestra identidad de documentos completos.

## 4. Aliases exactos

Un `full_byte_alias` requiere igualdad completa y alineada de `(viewer_page, SHA-256, byte_size)` en todos los JPEG efectivos del documento.

El alias conserva su `viewer_key`. Para cómputo:

- el contenido canónico se procesa una vez;
- el visor alias no recibe `fragseg_materialized_direct`;
- sólo después de que el canónico llegue a FRAGSEG puede recibir `effective_fragseg_coverage=1`;
- la igualdad de bytes no convierte dos registros de catálogo en una sola identidad bibliográfica.

## 5. OCR técnico 0.2

El OCR se ejecuta únicamente sobre contenidos canónicos efectivamente resueltos. Cada imagen se reconstruye temporalmente desde `effective_asset_url`, se verifica contra `effective_sha256` y `effective_byte_size`, se procesa y se elimina.

Se persisten métricas, no el OCR íntegro:

- `source_sha256_verified`;
- `attempts`;
- `selected_psm`;
- `recognized_words`;
- `ocr_chars`;
- `mean_word_confidence`;
- `median_word_confidence`;
- `low_confidence_word_rate`;
- `ocr_class`;
- `ocr_status`.

`no_text_detected` no significa automáticamente página vacía; es un estado técnico del OCR.

## 6. PAGESTRUCT 0.2

PAGESTRUCT clasifica estructura de página, no pedagogía. Clases:

- `textual`;
- `mixed_text_image`;
- `visual_only`;
- `front_matter`;
- `toc_or_navigation`;
- `bibliography_or_credits`;
- `unknown`.

Sólo `textual` y `mixed_text_image` pasan a FRAGSEG. Las reglas se mantienen iguales entre W1 y W2 para que las diferencias observadas no sean consecuencia de cambiar el clasificador entre disciplinas.

## 7. FRAGSEG 0.2

FRAGSEG persiste fragmentos derivados mediante:

- `fragment_id`;
- `page_id`;
- `fragment_sequence`;
- `candidate_type`;
- `token_count` / `char_count`;
- señales estructurales simples;
- `text_sha256`;
- `source_structure_class`;
- `classification_certainty`;
- `uncertain_boundary`.

El texto completo reconstruido no se persiste. `fragment_sequence` no se renumera para esconder candidatos descartados de cero tokens; los huecos legítimos se auditan.

`short_residual_candidate` es una categoría técnica residual y no evidencia que un fragmento sea tipográficamente un encabezado.

## 8. Estados de cobertura

LTMD mantiene separadas estas afirmaciones:

`asset_resolved_full` → existe representación fuente suficiente  
`page_manifest_ready` → la procedencia por página está materializada  
`ocr_ready` → OCR técnico canónico terminó bajo SHA  
`pagestruct_ready` → estructura de página materializada  
`fragseg_materialized_direct` → fragmentos calculados directamente  
`effective_fragseg_coverage` → directo o cubierto por alias byte-exacto  
`semantic_ready_validated` → constructos semánticos validados con referencia humana

Ninguna flecha implica automáticamente la siguiente.

## 9. Regla semántica

Matemáticas W2 permanece fuera de SEMB 0.3 de Ciencias Naturales. La disponibilidad de decenas de miles de fragmentos técnicos no autoriza a etiquetar actividades, posiciones pedagógicas u otros constructos sin una validación apropiada para ese dominio.
