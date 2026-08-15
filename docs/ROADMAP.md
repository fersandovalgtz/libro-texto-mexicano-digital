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
- [x] Demostrar mediante la muestra CER/WER que `text_detected` no equivale necesariamente a página textual: existen páginas fotográficas `visual_only` con falsos positivos OCR.

### Diagnóstico CER/WER — muestra primaria completada
- [x] Preregistrar 48 posiciones primarias.
- [x] Preparar evaluador CER/WER léxico y ortográfico.
- [x] Corregir alineación a `full-page OCR → TSV → región por centro de bounding box`.
- [x] Corregir parser TSV con `csv.QUOTE_NONE`.
- [x] Preregistrar tratamiento `visual_only` sin sustitución de muestra.
- [x] Completar 12/12 posiciones de 1972.
- [x] Completar 12/12 posiciones de 1988.
- [x] Completar 12/12 posiciones de 1993.
- [x] Completar 12/12 posiciones de 2014.
- [x] Alcanzar **48/48 = 100 %** de posiciones primarias técnicamente trabajadas.
- [x] Mantener referencias e hipótesis OCR legibles en Drive privado, no en GitHub.
- [x] Registrar páginas `visual_only` separadamente del denominador CER/WER textual.
- [x] Eliminar la segunda revisión humana como requisito del proyecto.
- [ ] Recalcular y congelar el resumen de **operator-reference CER/WER** global, por generación, front matter y body-only.
- [ ] Versionar una tabla derivada única de las 48 posiciones sin texto fuente.
- [ ] Identificar layouts que requieran tratamiento diferencial o exclusión explícita en análisis léxico fino.

**Estado:** las métricas de las 48 posiciones son diagnósticas respecto de una **referencia de operador de una sola pasada**, no un gold standard humano independiente.

### Protocolo de anotación computacional 0.2 — activo
- [x] Conservar `CODEBOOK_0_1.md` como preregistro histórico.
- [x] Crear `COMPUTATIONAL_ANNOTATION_PROTOCOL_0_2.md`.
- [x] Sustituir doble codificación/adjudicación humana por triangulación computacional reproducible.
- [ ] Clasificar automáticamente las 759 páginas en `textual`, `mixed_text_image`, `visual_only`, `front_matter`, `toc_or_navigation`, `bibliography_or_credits` o `unknown`.
- [ ] Construir reglas para detectar y excluir falsos positivos OCR sobre fotografías/ilustraciones.
- [ ] Segmentar páginas textuales/mixtas en fragmentos funcionales.
- [ ] Validar trazabilidad `book_id → page_id → fragment_id`.
- [ ] Implementar clasificador multietiqueta A basado en reglas/rasgos transparentes.
- [ ] Implementar clasificador multietiqueta B basado en una estrategia semántica computacional independiente.
- [ ] Calcular acuerdo/desacuerdo A/B por categoría.
- [ ] Crear bandera `uncertain` para casos sin evidencia suficiente o con desacuerdo relevante.
- [ ] Ejecutar análisis de sensibilidad por umbral, generación, longitud y layout.

### Dataset analítico — siguiente producto
- [ ] Construir dataset:
  `book → page → fragment → tipo → acciones → posición del alumno → contenido → estabilidad → procedencia`.
- [ ] Mantener texto de trabajo en capa privada cuando sea necesario por gobernanza jurídica.
- [ ] Publicar en GitHub sólo derivados no sustitutivos y trazables.
- [ ] Generar estadísticas por generación y tipo de página.

## Fase 2 — prueba historiográfica computacional

Comienza cuando exista un dataset de fragmentos con trazabilidad completa y estabilidad computacional suficiente. **No depende de revisión humana.**

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

El piloto pasa a escalamiento si cumple simultáneamente:

1. acceso reproducible al corpus — **cumplido**;
2. cobertura técnica suficiente de extracción — **cumplido**;
3. gobernanza jurídica suficiente para publicar metadatos y derivados — **provisionalmente cumplido para derivados; issue jurídico sigue abierto**;
4. diagnóstico OCR suficiente para conocer limitaciones por layout y generación — **48/48 posiciones primarias completadas**;
5. clasificación/segmentación computacional reproducible — **pendiente**;
6. estabilidad de categorías bajo al menos dos especificaciones computacionales — **pendiente**;
7. trazabilidad completa entre fuente y dato derivado — **en construcción**;
8. comparación historiográfica que produzca conocimiento adicional al catálogo original — **pendiente**;
9. costo técnico razonable para ampliar el corpus — **por evaluar al cierre del piloto**.

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
