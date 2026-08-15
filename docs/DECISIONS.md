# Registro de decisiones

## 2026-08-15 — Repositorio independiente

Se establece `fersandovalgtz/libro-texto-mexicano-digital` como repositorio propio del proyecto. No se integra a Rarámuri Histórico Digital ni a un monorepo general.

## 2026-08-15 — No almacenar indiscriminadamente archivos fuente

Los PDF, imágenes, OCR completo y otros binarios/textos extensos derivados de materiales originales de CONALITEG no se versionarán en GitHub mientras no exista una base jurídica y técnica específica que lo justifique. El repositorio conserva código, metadatos, métricas y datos derivados no sustitutivos.

## 2026-08-15 — Piloto por generaciones, no por años sueltos

El catálogo histórico se organiza en generaciones. El análisis inicial trata esas generaciones como cortes documentales que requieren contextualización curricular, evitando presentarlas como una serie anual homogénea.

## 2026-08-15 — Ciencias Naturales de quinto grado como primer dominio

Tras verificar continuidad entre los cortes seleccionados, el piloto 0.1 queda fijado en **Ciencias Naturales, quinto grado**, generaciones 1972, 1988, 1993 y 2014.

## 2026-08-15 — Separar generación, año de edición y copyright

`catalog_generation`, `edition_year` y `copyright_year` se almacenan como campos distintos. La etiqueta de generación del catálogo no se copia automáticamente como año editorial.

Casos que justifican la decisión:
- generación 1993: página legal verifica **Primera edición, 1998**;
- generación 2014: página legal verifica **Tercera edición revisada, 2014**;
- generación 1988: página legal contiene copyright SEP 1977, pero no una declaración explícita de edición; 1977 se registra sólo como `copyright_year`;
- generación 1972: el año editorial concreto sigue abierto.

## 2026-08-15 — Distinguir páginas del visor y activos fuente

`claves.json` declara 763 páginas estructurales, pero el barrido integral demostró que la última página de cada visor es sintética y carece de JPEG.

Se distinguen:
- `page_count`: páginas estructurales del visor;
- `source_asset_count`: JPEG reales;
- `asset_status`: `source_jpeg` o `terminal_synthetic`.

El corpus fuente real del piloto contiene **759 JPEG**.

## 2026-08-15 — Tesseract permanece como motor base; el primer problema era concurrencia

Los timeouts del benchmark inicial con cuatro procesos no se interpretan como evidencia de mala legibilidad ni como falla específica de la generación 1993.

Un control serial demostró que las mismas páginas podían procesarse correctamente. La configuración estable provisional queda:
- Tesseract en español;
- `psm 3`;
- `OMP_THREAD_LIMIT=1`;
- dos procesos concurrentes;
- timeout de 60 s en el barrido integral.

El barrido de 759 JPEG produjo texto en 698 activos (91.96 %) y ninguna imagen real quedó `unresolved`.

## 2026-08-15 — La confianza interna de Tesseract no es una medida de exactitud científica

Las métricas de confianza se utilizan sólo para triage y diagnóstico. La exactitud textual debe establecerse mediante CER/WER contra referencia humana preregistrada.

## 2026-08-15 — No automatizar el libro de códigos antes de validación humana

Las categorías de `CODEBOOK_0_1.md` fueron definidas antes del análisis masivo. No se diseñarán reglas o modelos que asignen definitivamente acciones pedagógicas o posiciones del alumno hasta codificar y revisar manualmente 25 fragmentos por generación.

Se preregistró un pool de 100 páginas y un protocolo de selección/codificación humana.

## 2026-08-15 — Las páginas `no_text_detected` no equivalen automáticamente a errores OCR

Las 61 páginas que produjeron cero palabras bajo `psm 3` deben auditarse antes de clasificarse. Se ejecutará fallback OCR (`psm 11`, `psm 6`) y métricas visuales. Sólo después se distinguirán falsos negativos de páginas de baja señal o alta complejidad visual.

## 2026-08-15 — Doble registro metodológico: Notion + GitHub

Se establece una bitácora técnica detallada en Notion como registro narrativo acumulativo del procedimiento. GitHub mantiene la infraestructura ejecutable y Notion conserva la secuencia de decisiones, intentos fallidos, configuraciones, límites interpretativos y cambios de criterio.

Todo hallazgo que modifique el método debe reflejarse en ambos sistemas antes de considerarse cerrado.
