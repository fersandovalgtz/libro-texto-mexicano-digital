# Protocolo de ejecución integral FTRL W1 Ciencias Naturales

Versión operativa: 0.1  
Estado: preregistrado antes de la primera corrida integral W1  
Alcance: LTMD-U1, W1 Ciencias Naturales

## Propósito

Este protocolo fija las condiciones de la primera ejecución integral de la Full-Text Research Layer (FTRL) sobre la cohorte fuente-admitida de W1 Ciencias Naturales. Su función es impedir que la cohorte, las cardinalidades, los criterios de completitud o las reglas de publicación se modifiquen después de observar el OCR completo.

La corrida integral es una validación técnica del corpus reconstruible y del índice de búsqueda. No constituye verificación del texto OCR, validación semántica ni evidencia suficiente para sostener afirmaciones históricas, curriculares o discursivas.

## Cohorte congelada

La reconciliación documental vigente fija:

- 37 identidades históricas técnicamente cubiertas;
- 33 objetos canónicos de procesamiento;
- 4 identidades 2018 representadas mediante aliases byte-a-byte verificados hacia sus pares 2019;
- 5,926 JPEG fuente admitidos para procesamiento;
- 3 posiciones internas declaradas pero persistentemente no servidas: una en `LTMD-CN3-G2008` y dos en `LTMD-CN4-G2008`;
- 759 páginas de los cuatro objetos CN5 del piloto con anclaje SHA-256 versionado.

Las cuatro relaciones 2018 → 2019 son relaciones técnicas de reutilización de bytes. No establecen por sí mismas identidad bibliográfica, igualdad editorial, equivalencia curricular ni continuidad semántica.

La cifra de 5,926 páginas describe exclusivamente los activos fuente admitidos y no debe reinterpretarse como equivalencia con todas las posiciones nominales declaradas por los visores.

## Normalización de procedencia

W1 no parte de un único manifiesto histórico. Su procedencia está distribuida entre tres capas versionadas:

1. `data/catalog/ciencias_naturales_pending_page_manifest.csv`, para activos auditados directamente y casos con huecos persistentes documentados;
2. `data/expansion/cn46_page_manifest.csv`, para objetos CN4/CN6 ya auditados en la expansión técnica;
3. `data/catalog/cn5_pilot_sha/`, para los cuatro objetos CN5 cuyo piloto quedó posteriormente anclado criptográficamente.

`scripts/build_ftrl_w1_inputs.py` reconcilia esas capas en dos archivos derivados bajo `local/ftrl/`: un manifiesto de activos compatible con FTRL y un inventario de procesamiento compatible con el índice. La normalización es determinista, sin acceso de red y sin texto OCR. No sustituye a las capas documentales originales ni modifica su autoridad metodológica.

## Ejecución

La referencia ejecutable integral es:

```bash
python scripts/run_ftrl_w1.py \
  --full \
  --workers 2 \
  --output-dir local/ftrl
```

El workflow `.github/workflows/validate-ftrl-w1-full.yml` reproduce esta ejecución en GitHub Actions con Python 3.12, Tesseract y el modelo español `spa`, y SQLite con FTS5.

La paralelización en dos shards altera únicamente la planificación del procesamiento. No modifica la cohorte, los hashes esperados, la identidad de página, el orden de concatenación final ni las reglas de aceptación. Cada descarga sigue verificándose contra el SHA-256 versionado antes de OCR.

## Gate previo obligatorio

Antes de iniciar OCR, `scripts/preflight_ftrl_w1.py --require-cryptographic-ready` debe devolver un estado `ready` bajo `LTMD_FTRL_W1_PREFLIGHT_0.2` y confirmar, como mínimo:

- 37 identidades históricas;
- 33 objetos canónicos;
- 4 aliases byte-a-byte;
- 5,926 JPEG fuente admitidos;
- 3 posiciones internas no servidas documentadas;
- 4 objetos CN5 anclados;
- 759 páginas CN5 con correspondencia de bytes respecto de la evidencia técnica previa;
- cero objetos canónicos sin capa de procedencia criptográfica aceptada.

Cualquier deriva bloquea la ejecución integral.

## Gates de completitud

Una corrida integral sólo podrá clasificarse como técnicamente validada si cumple simultáneamente:

1. 5,926 registros de página FTRL;
2. 5,926 filas en la tabla `pages` de SQLite;
3. 5,926 filas en el índice FTS5;
4. `PRAGMA integrity_check = ok`;
5. 33 objetos canónicos con páginas OCR;
6. 37 identidades históricas técnicamente representadas en la tabla de identidades;
7. cero páginas procesadas con tamaño de fuente desconocido;
8. commit Git exacto y contexto de GitHub Actions registrados en el manifiesto de corrida;
9. manifiesto FTRL con estado `validated` y ola única `W1`;
10. salida QC sin texto con cardinalidad de 5,926 páginas;
11. OCR por página, SQLite y cola detallada de QC mantenidos fuera de publicación y cubiertos por `.gitignore`;
12. artefactos públicos limitados a evidencia text-free: preflight, manifiesto agregado de corrida y resumen agregado de control de calidad.

Una falla en cualquier gate mantiene la corrida en estado diagnóstico y prohíbe declarar W1 cerrado en FTRL.

## Control de calidad OCR

Después de construir el corpus, `scripts/build_ftrl_qc_queue.py` genera una cola diagnóstica local y un resumen agregado sin texto. Se conservan los umbrales preregistrados de FTRL 0.1 para páginas sin texto recuperable, confianza ausente, baja confianza y texto excepcionalmente corto.

La cola sirve para priorizar revisión humana. Una página sin bandera no equivale a transcripción validada y una página con baja confianza no prueba, por sí sola, que el contenido OCR sea incorrecto.

## Consultas e interpretación

Esta primera corrida integral W1 no ejecuta consultas historiográficas preregistradas. El objetivo es demostrar reconstrucción técnica integral de la cohorte fuente-admitida y producir un mapa reproducible de calidad OCR antes de definir constructos analíticos.

Se mantienen como reglas obligatorias:

- `source_ready != text_verified`;
- `ocr_available != text_verified`;
- `corpus_ready != semantic_ready`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`;
- un alias técnico no equivale a identidad bibliográfica;
- una posición no servida no puede reinterpretarse como ausencia de contenido curricular;
- toda página utilizada como evidencia sustantiva debe verificarse contra el activo fuente.

## Evidencia pública esperada

Una ejecución integral válida podrá publicar exclusivamente:

- `ltmd_u1_w1_preflight.json`;
- `ltmd_u1_w1_full_run_manifest.json`;
- `ltmd_u1_w1_full_qc_summary.json`.

Estos artefactos contienen cardinalidades, hashes, métricas agregadas y contexto de ejecución, pero excluyen el texto OCR, las imágenes fuente, snippets y el índice SQLite.

## Criterio de avance

Sólo después de una corrida integral válida se actualizará la hoja de ruta para pasar W1 de `cryptographic-ready` a `corpus_ready`/`ocr_available`. La etiqueta `semantic_ready` requerirá trabajo humano adicional y no puede inferirse de una ejecución técnica exitosa.
