# Libro de Texto Mexicano Digital — estado científico y técnico

Corte: **16 de agosto de 2026**.

## Regla epistemológica vigente

El proyecto opera temporalmente **sin referencia humana disponible**. Esto no bloquea la expansión técnica del corpus. Continúan procedencia, OCR técnico, PAGESTRUCT, FRAGSEG, metadatos, reutilización exacta, dependencia documental, integridad y documentación reproducible.

Permanecen no validados o estacionados CER/WER contra referencia humana, confiabilidad intercodificador, consenso humano, validación SEMB03 y cualquier afirmación histórica primaria que dependa de categorías semánticas automáticas no validadas. Véase `docs/NO_HUMAN_REFERENCE_OPERATING_MODE_0_1.md`.

## Piloto de Ciencias Naturales

El piloto de Ciencias Naturales conserva su función metodológica: separó generación de catálogo, año editorial e identidad documental; estableció procedencia SHA-verificada; PAGESTRUCT; FRAGSEG; vistas de dependencia documental; y la infraestructura SEMB03. La expansión técnica puede continuar, pero el frente semántico permanece en `WAITING_HUMAN_REFERENCE`.

## LTMD-U1 W2 — Matemáticas

W2 está técnicamente cerrado.

- Universo congelado: **64 visores**.
- Identidades con activos resueltos: **60/64**.
- Objetos canónicos computados: **57**.
- Aliases byte-idénticos: **3**.
- Páginas canónicas OCR: **11,945**; SHA verificado **11,945/11,945**.
- Texto detectado: **11,812**; `no_text_detected`: **133**; `unresolved`: **0**.
- PAGESTRUCT: **11,945** páginas; FRAGSEG elegibles: **10,145**.
- FRAGSEG: **135,727** fragmentos técnicos.

Las cuatro excepciones DMA 2018 continúan explícitas y no se imputan. El cierre está documentado en `docs/LTMD_U1_W2_COMPLETION.md`.

## LTMD-U1 W3 — Español/Lengua

### Fuente y reconciliación

La topología de activos quedó reconciliada antes de abrir OCR.

- Identidades W3: **130/130** con cobertura operacional.
- Objetos canónicos que requieren cómputo único: **114**.
- Aliases de provenance: **16**.
  - **8** aliases byte-exactos directos.
  - **8** aliases de ruta 2018→2019, demostrados página por página por SHA-256 y tamaño.
- Páginas fuente canónicas autorizadas: **20,765**.
- Huecos internos persistentes: **8**, conservados sin renumeración.
- Identidades bloqueadas por fuente: **0**.

### OCR

Se creó `LTMD_U1_W3_SPANISH_OCR_0.1` con:

- verificación SHA-256 y tamaño antes de cada OCR;
- Tesseract español;
- `OMP_THREAD_LIMIT=1`;
- procesamiento serial dentro de cada visor y matriz de hasta 8 visores en paralelo;
- imágenes y OCR completo efímeros;
- persistencia exclusiva de métricas técnicas y provenance;
- 114 shards canónicos con combinador de cardinalidad exacta.

Run fuente: **GitHub Actions 31960694824**. Estado al redactar este corte: `in_progress`; el gate pasó y los primeros visores visibles terminaron en `success`.

### Cadena ya preparada

La infraestructura posterior está versionada y no se dispara hasta que exista el producto anterior completo:

`W3 OCR → W3 PAGESTRUCT → W3 FRAGSEG → exact-text reuse/document dependence`

PAGESTRUCT reutiliza la lógica estructural conservadora ya empleada en otras olas. FRAGSEG conserva IDs y secuencias sin renumeración destructiva, hace fallar cualquier shard con error de descarga/SHA/OCR de ejecución y no persiste texto completo.

La capa posterior de reutilización exacta agrupará únicamente por `text_sha256`, construirá unidades de contenido, proyección identidad→canónico y solapamiento par-a-par. La igualdad de hash se tratará sólo como reutilización textual exacta dentro de la representación técnica, nunca como equivalencia bibliográfica, curricular, pedagógica o semántica.

## Prioridades inmediatas

1. Cerrar OCR W3 con **20,765/20,765** páginas SHA verificadas y cero `unresolved`, o aislar cualquier excepción real sin imputarla.
2. Cerrar PAGESTRUCT W3 y fijar el número exacto de páginas elegibles para FRAGSEG.
3. Cerrar FRAGSEG W3 y publicar conteos, IDs únicos, páginas vacías legítimas y huecos de secuencia.
4. Construir la vista de reutilización exacta/dependencia documental W3.
5. Actualizar el manifiesto de integridad del repositorio después del cierre de esta ola, incluyendo scripts, workflows, reportes y datos derivados nuevos.
6. Actualizar artículo de métodos/recurso con la distinción explícita entre validación técnica y validación humana/semántica.

## Principio de publicación

La ausencia temporal de referencia humana cambia el **nivel de inferencia admisible**, no el estándar de ingeniería científica. Toda expansión debe mantener provenance verificable, invariantes de cardinalidad, aliases no destructivos, huecos explícitos, separación entre objeto y contenido, y límites epistemológicos visibles.
