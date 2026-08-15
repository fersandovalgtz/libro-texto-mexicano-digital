# Roadmap

## Fase 0 — constitución del proyecto — completada

- [x] Definir identidad, alcance y unidad de análisis.
- [x] Registrar fuentes y restricciones jurídicas provisionales.
- [x] Diseñar esquema mínimo de metadatos.
- [x] Seleccionar corpus piloto.
- [x] Crear repositorio independiente y reglas de gobernanza.

## Fase 1 — piloto 0.1/0.2 — en curso avanzado

### Corpus e infraestructura — completado
- [x] Fijar Ciencias Naturales, quinto grado, como corpus inicial.
- [x] Verificar continuidad en generaciones 1972, 1988, 1993 y 2014.
- [x] Inventariar los cuatro libros y separar generación, edición y copyright.
- [x] Reconstruir arquitectura de los visores.
- [x] Construir manifiesto reproducible.
- [x] Distinguir 763 páginas estructurales de visor y 759 JPEG fuente reales.

### Extracción/OCR — cobertura técnica completada
- [x] Determinar resolución por generación.
- [x] Diagnosticar timeouts de Tesseract como problema de concurrencia.
- [x] Fijar concurrencia estable: `OMP_THREAD_LIMIT=1`, dos procesos.
- [x] Ejecutar benchmark estable de 40 páginas.
- [x] Procesar los 759 JPEG sin persistir OCR completo en GitHub.
- [x] Auditar las 61 páginas que `psm 3` dejó sin texto.
- [x] Identificar 59 falsos negativos recuperables por segmentación alternativa.
- [x] Congelar OCR adaptativo 0.1: `psm 3 → psm 11/6`, fallback válido con ≥5 palabras.
- [x] Reejecutar los 759 activos de extremo a extremo.
- [x] Alcanzar 757/759 activos con texto aceptado por el motor, 2 `no_text_detected`, 0 `unresolved`.
- [x] Demostrar que `text_detected` no equivale necesariamente a página textual: existen páginas fotográficas con falsos positivos OCR.

### Diagnóstico CER/WER — muestra primaria completada
- [x] Preregistrar y trabajar 48/48 posiciones primarias.
- [x] Preparar evaluador CER/WER léxico y ortográfico.
- [x] Corregir alineación a `full-page OCR → TSV → región por centro de bounding box`.
- [x] Corregir parser TSV con `csv.QUOTE_NONE`.
- [x] Registrar páginas `visual_only` fuera del denominador textual.
- [x] Mantener referencias e hipótesis OCR legibles en Drive privado, no en GitHub.
- [x] Eliminar la segunda revisión humana como requisito.
- [ ] Recalcular y congelar el resumen de **operator-reference CER/WER** global, por generación, front matter y body-only.
- [ ] Versionar una tabla derivada única de las 48 posiciones sin texto fuente.

**Estado:** CER/WER es diagnóstico respecto de una referencia de operador de una sola pasada; no se presenta como gold standard humano independiente.

### Protocolo de anotación computacional 0.2 — activo
- [x] Conservar `CODEBOOK_0_1.md` como preregistro histórico.
- [x] Crear `COMPUTATIONAL_ANNOTATION_PROTOCOL_0_2.md`.
- [x] Sustituir doble codificación/adjudicación humana por triangulación computacional reproducible.
- [x] Congelar **PAGESTRUCT_0.2**: 759/759 páginas = 494 textual, 145 mixed_text_image, 60 visual_only, 1 front_matter, 20 toc_or_navigation, 15 bibliography_or_credits y 24 unknown.
- [x] Excluir conservadoramente end matter denso no resuelto; body-only elegible = **639 páginas**.
- [x] Congelar **FRAGSEG_0.2**: **639/639 páginas**, **9,594 fragmentos**, **0 fallos**.
- [x] Publicar `fragment_manifest.csv` sin texto fuente y validar trazabilidad `book_id → page_id → fragment_id` mediante IDs y SHA-256.
- [x] Ejecutar **FRAGAUDIT_0.2**: mediana 9 tokens, máximo 158, 0 fragmentos >250 tokens; máximo de densidad 2014 reducido 113→64 fragmentos/página.
- [x] Preregistrar e implementar **RULEA_0.1** con reglas/rasgos transparentes.
- [x] Ejecutar pruebas sintéticas RULEA; el primer test detectó ausencia de infinitivos, se corrigió de forma general y el segundo terminó SUCCESS.
- [x] Ejecutar **RULEA_0.1** sobre **9,594/9,594 fragmentos**, con SHA-256 coincidente en todos los casos y sin texto publicado.
- [x] Ejecutar **RULEA_AUDIT_0.1**: invariantes lógicas en cero, uncertainty global 1.49 %; RULEA queda congelado y no se ampliará post hoc.
- [x] Preregistrar e implementar **SEMB_0.1** como estrategia semántica independiente de A.
- [x] Ejecutar preflight sintético SEMB 0.1 y **rechazarlo antes del corpus**: top-1 de acciones 3/16; prototipos colapsados (similitud media acciones ≈0.945, posiciones ≈0.959).
- [x] Comprobar que nearest-prototype y centrado no rescatan SEMB 0.1; conservarlo como versión FAILED PRE-CORPUS.
- [x] Abrir **SEMB_0.2** con `intfloat/multilingual-e5-small`, prototipos cortos, separación desarrollo/validación y `VALIDATION_B02` bloqueada antes de pruebas.
- [x] Preregistrar criterios de aceptación SEMB 0.2 y regla automática de selección de configuración sintética.
- [ ] Completar desarrollo sintético SEMB 0.2 — **run activo 31902136502**; todavía sin abrir VALIDATION_B02.
- [ ] Ejecutar VALIDATION_B02 una sola vez; sólo si pasa, permitir ejecución sobre LTMD.
- [x] Preregistrar acuerdo computacional A/B (`CLASSIFIER_AGREEMENT_SPEC_0_1.md`) antes de resultados B.
- [ ] Ejecutar B sobre corpus sólo después de superar su validación sintética.
- [ ] Calcular acuerdo/desacuerdo A/B por categoría y fragmento.
- [ ] Crear/propagar bandera `uncertain` para casos sin evidencia suficiente o con desacuerdo relevante.
- [ ] Ejecutar análisis de sensibilidad por umbral, generación, longitud y layout.

### Dataset analítico — en construcción
- [x] Fijar especificación `FRAGMENT_SEGMENTATION_SPEC_0_1.md`.
- [x] Construir manifiesto de 9,594 fragmentos sin texto fuente.
- [x] Mantener texto sólo de forma efímera durante OCR/reconstrucción; verificar identidad mediante SHA-256.
- [x] Publicar sólo metadatos, hashes, métricas y etiquetas derivadas no sustitutivas.
- [x] Publicar primera capa de etiquetas pedagógicas A y auditoría derivada.
- [ ] Construir dataset integrado:
  `book → page → fragment → tipo → acciones → posición del alumno → estabilidad → procedencia`.
- [ ] Integrar etiquetas B sólo si SEMB supera validación pre-corpus.
- [ ] Generar estadísticas pedagógicas por generación después de triangulación A/B.

## Fase 2 — prueba historiográfica computacional

Comienza cuando exista etiquetado A/B con trazabilidad completa y estabilidad computacional suficiente. **No depende de revisión humana.**

- [ ] Cuantificar tipos de actividad y acciones pedagógicas por generación.
- [ ] Comparar posiciones atribuidas al alumno.
- [ ] Examinar continuidad/ruptura 1972–1988–1993/1998–2014.
- [ ] Separar resultados body-only de front matter/layout complejo.
- [ ] Excluir o modelar separadamente casos `uncertain` y `visual_only`.
- [ ] Contrastar resultados computacionales con contexto curricular e historiografía.
- [ ] Formular al menos una hipótesis/artículo derivado del piloto.
- [ ] Construir una comparación reproducible completa.
- [ ] Evaluar si los resultados justifican escalar.

## Puerta de decisión del piloto

1. acceso reproducible al corpus — **cumplido**;
2. cobertura técnica suficiente de extracción — **cumplido**;
3. gobernanza jurídica suficiente para publicar metadatos y derivados — **provisionalmente cumplido para derivados; issue jurídico sigue abierto**;
4. diagnóstico OCR suficiente para conocer limitaciones por layout y generación — **cumplido en 48/48 posiciones diagnósticas**;
5. clasificación estructural reproducible — **cumplida: PAGESTRUCT_0.2, 759/759**;
6. segmentación computacional reproducible — **cumplida: FRAGSEG_0.2, 639/639, 9,594 fragmentos, 0 fallos**;
7. primera especificación pedagógica reproducible — **cumplida: RULEA_0.1, 9,594/9,594, auditada**;
8. estabilidad bajo segunda especificación independiente — **pendiente: SEMB 0.1 rechazado; SEMB 0.2 en desarrollo sintético**;
9. trazabilidad completa entre fuente y dato derivado — **cumplida hasta etiquetas A; pendiente integrar B/estabilidad**;
10. comparación historiográfica que produzca conocimiento adicional al catálogo original — **pendiente**;
11. costo técnico razonable para ampliar el corpus — **por evaluar al cierre del piloto**.

## Fase 3 — escalamiento controlado

Sólo después de superar la puerta de decisión:

- ampliar generaciones, grados y/o asignaturas;
- automatizar inventario e ingestión;
- estabilizar API/esquema público;
- construir buscador o interfaz comparativa;
- preparar release versionado;
- archivar release en Zenodo u otro repositorio apropiado;
- asignar DOI y formalizar citación;
- definir estrategia de artículos, datasets y productos derivados.

## Regla documental

Notion mantiene la bitácora técnica narrativa y GitHub la infraestructura reproducible. Todo cambio que afecte el método debe registrarse en ambos sistemas antes de considerarse cerrado.
