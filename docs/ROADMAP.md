# Roadmap

## Fase 0 — constitución del proyecto — completada

- [x] Definir identidad, alcance y unidad de análisis.
- [x] Registrar fuentes y restricciones jurídicas provisionales.
- [x] Diseñar esquema mínimo de metadatos.
- [x] Seleccionar corpus piloto.
- [x] Crear repositorio independiente y reglas de gobernanza.

## Fase 1 — piloto 0.1 — en curso avanzado

### Corpus e infraestructura — completado
- [x] Fijar Ciencias Naturales, quinto grado, como corpus inicial.
- [x] Verificar continuidad en generaciones 1972, 1988, 1993 y 2014.
- [x] Inventariar los cuatro libros y separar generación, edición y copyright.
- [x] Reconstruir arquitectura de los visores.
- [x] Construir manifiesto reproducible.
- [x] Distinguir 763 páginas estructurales de visor y 759 JPEG fuente reales.

### Extracción/OCR — viabilidad demostrada
- [x] Determinar resolución por generación.
- [x] Diagnosticar timeouts de Tesseract como problema de concurrencia.
- [x] Fijar configuración estable: español, `psm 3`, `OMP_THREAD_LIMIT=1`, dos procesos.
- [x] Ejecutar benchmark estable de 40 páginas.
- [x] Procesar técnicamente los 759 JPEG sin persistir OCR completo.
- [x] Alcanzar texto detectado en 91.96 % de los activos.
- [ ] Auditar las 61 páginas sin texto basal mediante fallback OCR + métricas visuales.

### Validación de calidad — en preparación
- [x] Preregistrar 48 páginas para CER/WER.
- [x] Preparar evaluador CER/WER.
- [ ] Completar transcripción/referencia humana.
- [ ] Calcular CER/WER global y por generación.
- [ ] Decidir si alguna generación requiere preprocesamiento específico.

### Validación del libro de códigos — en preparación
- [x] Preregistrar `CODEBOOK_0_1.md` antes del análisis masivo.
- [x] Preregistrar pool de 100 páginas, 25 por generación.
- [x] Fijar protocolo de selección/codificación humana.
- [ ] Inventariar tipos funcionales en el pool.
- [ ] Seleccionar 25 fragmentos por generación.
- [ ] Codificar manualmente los 100 fragmentos.
- [ ] Revisar desacuerdos y estabilizar `CODEBOOK_0_2.md` si procede.

### Dataset analítico — pendiente
- [ ] Diseñar reglas/modelos de segmentación después de la validación humana.
- [ ] Segmentar libro → página → fragmento.
- [ ] Generar dataset derivado sin publicar texto fuente extenso.
- [ ] Validar trazabilidad `book_id → page_id → fragment_id`.

## Fase 2 — prueba historiográfica

Sólo comienza cuando la validación humana permita interpretar las categorías.

- [ ] Cuantificar tipos de actividad y acciones pedagógicas por generación.
- [ ] Comparar posiciones atribuidas al alumno.
- [ ] Examinar continuidad/ruptura 1972–1988–1993/1998–2014.
- [ ] Contrastar resultados computacionales con contexto curricular e historiografía.
- [ ] Formular al menos una hipótesis/artículo derivado del piloto.
- [ ] Construir una comparación reproducible completa.
- [ ] Evaluar si los resultados justifican escalar.

## Puerta de decisión del piloto

El piloto sólo pasa a escalamiento si cumple simultáneamente:

1. acceso reproducible al corpus;
2. gobernanza jurídica suficiente para publicar metadatos y derivados;
3. OCR utilizable, medido con CER/WER y no sólo confianza interna;
4. libro de códigos estable después de validación humana;
5. trazabilidad completa entre fuente y dato derivado;
6. comparación historiográfica que produzca conocimiento adicional al catálogo original;
7. costo técnico/humano razonable para ampliar el corpus.

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
