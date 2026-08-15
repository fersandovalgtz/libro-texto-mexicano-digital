# Decisión metodológica — proyecto sin revisión humana

Fecha: 2026-08-15

## Decisión

El piloto `Libro de Texto Mexicano Digital` no realizará segunda revisión humana de referencias OCR, doble codificación humana, adjudicación humana de desacuerdos ni validación manual del libro de códigos como condición de avance.

Esta decisión **supersede**, desde esta fecha, las reglas anteriores de `docs/DECISIONS.md` tituladas:

- `La segunda revisión humana debe ser independiente`;
- `No automatizar el libro de códigos antes de validación humana`.

Esas entradas se conservan como historia metodológica y no deben interpretarse como requisitos vigentes.

## Consecuencias para CER/WER

Las 48 posiciones primarias ya trabajadas se consideran un diagnóstico contra una **referencia de operador de una sola pasada**. Sus CER/WER no se describirán como gold standard independiente ni como validación humana definitiva. Su función es caracterizar fallos OCR por generación y layout, detectar falsos positivos sobre páginas visuales y orientar exclusiones/tratamientos computacionales.

## Consecuencias para anotación pedagógica

`CODEBOOK_0_1.md` se conserva como preregistro histórico de categorías. La aplicación del esquema se realizará mediante triangulación computacional:

1. clasificación A con reglas/rasgos transparentes;
2. clasificación B mediante una estrategia semántica computacional independiente;
3. cálculo de acuerdo/desacuerdo;
4. bandera `uncertain` para casos con evidencia insuficiente o inestabilidad;
5. análisis de sensibilidad por umbrales, longitud, generación y layout;
6. conservación de todas las versiones, parámetros y resultados derivados.

No habrá corrección manual de desacuerdos para producir una etiqueta final supuestamente humana.

## Criterio de rigor sustituto

La ausencia de revisión humana se compensa metodológicamente con:

- reglas preregistradas y versionadas;
- trazabilidad completa `book_id → page_id → fragment_id`;
- dos especificaciones computacionales independientes;
- medición explícita de desacuerdo;
- categorías `unknown`/`uncertain` en vez de decisiones forzadas;
- análisis de sensibilidad;
- separación de páginas `visual_only`, front matter y body text;
- registro detallado en Notion de intentos, fallos, umbrales y cambios de método;
- publicación en GitHub de código y derivados no sustitutivos.
