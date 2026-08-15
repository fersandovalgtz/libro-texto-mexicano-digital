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

Un control serial demostró que las mismas páginas podían procesarse correctamente. La configuración estable queda:
- Tesseract 5.3.4 en español en el runner productivo;
- `OMP_THREAD_LIMIT=1`;
- dos procesos concurrentes;
- timeout de 60 s.

## 2026-08-15 — OCR adaptativo 0.1

El barrido basal con `psm 3` detectó texto en 698 de 759 JPEG y dejó 61 casos con cero palabras. La auditoría posterior mostró que **59 de esas 61 páginas eran falsos negativos del modo basal**.

La regla adaptativa queda:
1. `psm 3` basal;
2. si produce cero palabras o falla, ejecutar `psm 11` y `psm 6`;
3. aceptar un fallback sólo si produce al menos 5 palabras;
4. si ambos son aceptables, elegir el de mayor conteo.

Segundo barrido integral: **757/759 páginas con texto (99.74 %), 2 `no_text_detected`, 0 `unresolved`**. Modos elegidos: psm3=698; psm11=7; psm6=52.

Los dos casos restantes pertenecen a 2014: visor 157 es objetivamente blanco y visor 102 es predominantemente visual/texto marginal de calidad insuficiente.

## 2026-08-15 — La confianza interna de Tesseract no es una medida de exactitud científica

Las métricas de confianza se utilizan sólo para triage y diagnóstico. La exactitud textual debe establecerse mediante CER/WER contra referencia humana preregistrada.

## 2026-08-15 — Dos familias CER/WER

Antes de consolidar resultados se fijaron dos familias:

- **ortográfica:** conserva mayúsculas, acentos y puntuación lingüística después de neutralizar artefactos de layout;
- **léxica:** además aplica `casefold` y neutraliza puntuación/símbolos como separadores, conservando letras, diacríticos y números.

La familia **léxica** es el criterio principal para decidir viabilidad del análisis histórico-computacional. La ortográfica funciona como control de fidelidad editorial.

La muestra primaria se reportará también estratificada en:
- front matter: legal + índice = 8 páginas;
- cuerpo del libro: 40 páginas posicionales.

La viabilidad pedagógica se juzgará principalmente sobre las 40 páginas corporales, sin borrar ni ocultar los resultados del front matter.

## 2026-08-15 — La hipótesis CER/WER debe proceder del OCR de página completa

**Corrección metodológica crítica.** El primer lote experimental ejecutó Tesseract directamente sobre recortes humanos. Esto no reproduce el pipeline real, que procesa la página completa.

A partir de esta decisión:
1. la imagen completa se procesa con el `selected_psm` del pipeline adaptativo;
2. se conserva TSV privado de página completa;
3. la región humana se fija independientemente del OCR;
4. una palabra TSV se incluye en la hipótesis regional si el **centro geométrico de su bounding box** cae dentro de la región;
5. se reconstruye la hipótesis regional en el orden TSV;
6. se normaliza y calcula CER/WER.

Las métricas obtenidas previamente mediante `crop → OCR` quedan como calibración histórica y están **superseded para agregados científicos**.

La lógica reproducible está en `scripts/extract_region_from_tsv.py` y la justificación en `docs/OCR_REGION_ALIGNMENT_ADDENDUM_2026-08-15.md`.

## 2026-08-15 — Tesseract TSV se parsea con quoting desactivado

Durante la validación de 1988, visor 155, Tesseract produjo un token que comienza con una comilla doble literal (`"mantenerla`). El extractor regional utilizaba `csv.DictReader` con el comportamiento CSV por defecto. Como Tesseract TSV es texto separado por tabuladores y **no un archivo CSV con campos entrecomillados**, una comilla OCR no balanceada podía interpretarse erróneamente como inicio de campo citado y absorber filas posteriores del TSV.

La regla queda congelada así:

- todo TSV de Tesseract se lee con `delimiter='\t'` y `quoting=csv.QUOTE_NONE`;
- una comilla producida por OCR se trata como parte literal del token;
- no se corrigen ni eliminan comillas antes de reconstruir la hipótesis regional;
- el cambio es de **parsing**, no de reconocimiento OCR, por lo que cualquier métrica afectada debe recalcularse desde el TSV original;
- se añadió una prueba de regresión que verifica que un token con comilla inicial no absorba las filas siguientes.

La corrección está implementada en `scripts/extract_region_from_tsv.py` y cubierta por `tests/test_extract_region_from_tsv.py`.

## 2026-08-15 — La segunda revisión humana debe ser independiente [SUPERSEDED]

Una doble lectura de la referencia por el mismo operador puede detectar errores materiales pero **no cuenta como segunda revisión**. Las métricas CER/WER permanecen provisionales hasta que otra revisión humana independiente verifique región, orden de lectura, caracteres, cifras, palabras y correspondencia con la imagen.

**Estado:** regla histórica, superseded por la decisión posterior `Proyecto sin revisión humana` del 15-ago-2026. No constituye un requisito vigente.

## 2026-08-15 — Material textual de validación en Drive privado

GitHub no alojará referencias humanas ni hipótesis OCR legibles. La hoja privada `LTMD — referencia humana OCR privada` en Google Drive conserva:
- regiones;
- transcripciones humanas;
- hipótesis regionales del pipeline;
- estados de revisión;
- métricas de validación.

Notion conserva estados, métricas y narrativa metodológica, **no el texto fuente**.

## 2026-08-15 — Transporte cifrado para datos privados generados en CI

Cuando sea indispensable recuperar desde el runner datos privados para validación, sólo se admitirán artifacts que contengan **ciphertext**, nunca imágenes/OCR legibles. La clave privada permanece local y se destruye después de sincronizar Drive/Notion.

Se registró un incidente previo en el que tres JPEG fueron subidos como artifact efímero de un día. Ese mecanismo fue retirado y no debe repetirse.

El procedimiento optimizado para pequeños lotes empaqueta imagen fuente + TXT/TSV productivo **dentro de un bundle cifrado**, mientras el artifact público contiene únicamente ciphertext y un manifiesto técnico no textual.

## 2026-08-15 — No automatizar el libro de códigos antes de validación humana [SUPERSEDED]

Las categorías de `CODEBOOK_0_1.md` fueron definidas antes del análisis masivo. No se diseñarán reglas o modelos que asignen definitivamente acciones pedagógicas o posiciones del alumno hasta codificar y revisar manualmente 25 fragmentos por generación.

Se preregistró un pool de 100 páginas y un protocolo de selección/codificación humana.

**Estado:** regla histórica, superseded por la decisión posterior `Proyecto sin revisión humana` del 15-ago-2026. No constituye un requisito vigente.

## 2026-08-15 — Doble registro metodológico: Notion + GitHub

Se establece una bitácora técnica detallada en Notion como registro narrativo acumulativo del procedimiento. GitHub mantiene la infraestructura ejecutable y Notion conserva la secuencia de decisiones, intentos fallidos, configuraciones, límites interpretativos y cambios de criterio.

Todo hallazgo que modifique el método debe reflejarse en ambos sistemas antes de considerarse cerrado.

## 2026-08-15 — Proyecto sin revisión humana

El proyecto no realizará segunda revisión humana de referencias OCR, doble codificación humana, adjudicación humana de desacuerdos ni validación manual del libro de códigos como condición de avance. Esta decisión supersede expresamente las dos reglas históricas marcadas arriba como `[SUPERSEDED]`.

Las 48 posiciones CER/WER se interpretan como diagnóstico contra una **referencia de operador de una sola pasada**, no como gold standard humano independiente. Su función es caracterizar fallos OCR por generación/layout y detectar páginas visuales o problemáticas.

La anotación pedagógica se realizará mediante triangulación computacional: especificación A con reglas/rasgos transparentes; especificación B con estrategia semántica independiente; medición de acuerdo/desacuerdo; bandera `uncertain`; análisis de sensibilidad; y conservación de versiones, parámetros y trazabilidad. No habrá corrección manual de desacuerdos para fabricar una etiqueta final adjudicada.

Documento detallado asociado: `docs/DECISION_NO_HUMAN_REVIEW_2026-08-15.md`.
