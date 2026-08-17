# LTMD — política de candidatos de instancia bibliográfica

Versión: `LTMD_BIBLIOGRAPHIC_INSTANCE_POLICY_0.1`.

## Producto vigente

La fuente vigente para cualquier uso de cronología de ejemplar es:

- `data/catalog/ltmd_bibliographic_instance_candidates.csv`
- `data/catalog/ltmd_bibliographic_instance_candidates.md`
- versión actual: `LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.3`.

La tabla histórica `LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1` y su audit posterior se conservan como **traza metodológica del proceso de endurecimiento**, pero quedan **supersedidos para interpretación y publicación**. No deben citarse como una lista de fechas bibliográficas definitivamente resueltas.

## Estado vigente

Sobre 26 objetos con observaciones bibliográficas:

- candidatos técnicos con año: **11**;
- sin candidato estricto: **15**;
- Tier A — declaración editorial y ciclo en páginas independientes: **0**;
- Tier B — declaración conjunta + página corroborante adicional: **2**;
- Tier C — declaración conjunta en una sola página: **9**;
- candidatos cuyo año difiere de `catalog_generation`: **6/11**.

La diferencia 6/11 respecto de la cohorte de catálogo confirma empíricamente que `catalog_generation` no puede tratarse como año bibliográfico por defecto.

## Regla de candidato

Un candidato de año sólo existe cuando:

1. hay exactamente un `school_cycle` fuerte y válido para el objeto;
2. existe exactamente una declaración de edición/reimpresión cuyo año coincide con el inicio de ese ciclo;
3. ambas observaciones conservan página y SHA-256 de evidencia;
4. `catalog_generation` está explícitamente excluido del cálculo;
5. cualquier reparación OCR utilizada proviene de una regla acotada, versionada y reproducible.

La regla no selecciona el año máximo, el ordinal máximo ni la declaración “más reciente”.

## Recuperación OCR permitida actualmente

La única reparación OCR incorporada es `LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.2`:

- objetivo derivado reproduciblemente desde el audit pre-recovery;
- normalización limitada a la confusión `reimpresión` con `i→l/I/1` inmediatamente después de `re`;
- ≥2 PSM sobre la misma página SHA-verificada;
- año igual al inicio del ciclo fuerte ya observado.

Esta regla añadió dos statements:

- `H2011P5CI326`: `third_reprint:2013`;
- `H2014P4FCA`: `third_reprint:2017`.

No existe fuzzy matching bibliográfico general.

## Tiers de evidencia

### Tier A — `A_cross_page_independent`

La declaración editorial/reimpresión y el ciclo escolar se sostienen en páginas fuente disjuntas. Es el nivel técnico más fuerte definido actualmente.

**Cobertura actual: 0.**

### Tier B — `B_joint_plus_extra_page_corroboration`

La declaración editorial/reimpresión y el ciclo coexisten en al menos una misma página, y además existe una página adicional que corrobora parte de la temporalidad.

**Cobertura actual: 2.**

### Tier C — `C_joint_same_page_only`

La correspondencia depende de una declaración conjunta en una misma página fuente SHA-verificada.

**Cobertura actual: 9.**

Tier B y C son evidencia primaria reproducible, pero no deben describirse como corroboración completamente independiente.

## Lenguaje permitido

Se puede escribir:

- “candidato técnico de año bibliográfico”;
- “declaración de edición/reimpresión compatible con el inicio del ciclo observado”;
- “evidencia Tier B/Tier C”; 
- “OCR técnico, `human_validated=0`”.

## Lenguaje no permitido

Mientras no exista validación humana suficiente, no se debe escribir:

- “fecha bibliográfica definitiva”;
- “año de publicación demostrado” cuando la fuente sólo demuestra reimpresión/ciclo;
- “confirmado por dos fuentes independientes” para Tier B o C;
- “edición vigente” derivada automáticamente del ordinal o año mayor;
- “generación 2014 = libro publicado en 2014”.

## Objetos sin candidato

Los 15 objetos restantes permanecen explícitamente sin año efectivo candidato bajo la regla vigente:

- 12 carecen de `school_cycle` fuerte en la ventana bibliográfica auditada;
- 3 tienen ciclo fuerte, pero ninguna edición/reimpresión compatible incluso después de la recuperación OCR estrecha.

No se imputan desde la cohorte del catálogo, títulos vecinos, otras generaciones, similitud OCR o reutilización textual.

## Uso en análisis histórico

Los candidatos pueden utilizarse para:

- control de calidad de metadatos;
- priorización de validación humana;
- análisis de sensibilidad;
- diseño de una futura cronología bibliográfica.

No deben mezclarse sin etiqueta con fechas humanas validadas. Cualquier artículo o visualización que los use deberá publicar el tier de evidencia y la cobertura de datos faltantes.

Véanse también:

- `docs/HISTORICAL_ANALYSIS_PLAN_0_3.md`;
- `docs/DATA_MODEL.md`;
- `docs/DATA_GOVERNANCE.md`;
- `data/catalog/ltmd_bibliographic_observations.md`;
- `data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.md`.
