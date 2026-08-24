# Protocolo de ejecución integral exhaustiva FTRL W1 Ciencias Naturales

Versión operativa: 0.2  
Estado: preregistrado antes de la primera corrida integral exhaustiva W1  
Alcance: LTMD-U1, W1 Ciencias Naturales

## Nota de supersesión

Esta versión 0.2 **supersede operativamente** a `FTRL_W1_FULL_EXECUTION_PROTOCOL_0_1.md` para cualquier afirmación de completitud exhaustiva de W1.

La versión 0.1 congeló correctamente una cohorte técnica entonces reconciliada de 37 identidades, 33 objetos canónicos y 5,926 JPEG fuente. Una auditoría posterior contra el denominador maestro `data/catalog/ltmd_u1_coverage.csv` demostró que el dominio `ciencias_naturales` contiene 40 identidades históricas. Las tres identidades ausentes de aquella cohorte no eran retenciones ni fuentes no resueltas: ya estaban materializadas y contaban con manifiestos versionados. En consecuencia, la corrida 37/37 conserva valor diagnóstico y de desarrollo, pero no puede usarse como evidencia de exhaustividad W1.

La corrección se realiza sin reescribir la capa histórica de 37 identidades. La FTRL exhaustiva une explícitamente esa capa con los manifiestos ya existentes para `H1966P6CI374`, `H1966P6CI375` y `H1993P6CI209`.

## Propósito

Este protocolo fija las condiciones de la primera ejecución integral **exhaustiva** de la Full-Text Research Layer (FTRL) sobre W1 Ciencias Naturales. Su función es impedir que el denominador, la topología de procesamiento, las cardinalidades, los criterios de completitud o las reglas de publicación se modifiquen después de observar el OCR completo.

La corrida integral es una validación técnica del corpus reconstruible y del índice de búsqueda. No constituye verificación del texto OCR, validación semántica ni evidencia suficiente para sostener afirmaciones históricas, curriculares o discursivas.

## Denominador maestro y cohorte congelada

El denominador maestro vigente fija 40 identidades históricas cuyo `operational_domain` es `ciencias_naturales`.

La reconciliación exhaustiva congela:

- **40 identidades históricas** técnicamente cubiertas;
- **36 objetos canónicos de procesamiento**;
- **4 identidades 2018** representadas mediante aliases byte-a-byte verificados hacia sus pares 2019;
- **6,516 JPEG fuente** admitidos para procesamiento;
- **3 posiciones internas** declaradas pero persistentemente no servidas: una en `LTMD-CN3-G2008` y dos en `LTMD-CN4-G2008`;
- **34 posiciones terminales sintéticas** documentadas en los objetos canónicos;
- **759 páginas** de los cuatro objetos CN5 del piloto con anclaje SHA-256 versionado.

Las cuatro relaciones 2018 → 2019 son relaciones técnicas de reutilización de bytes. No establecen por sí mismas identidad bibliográfica, igualdad editorial, equivalencia curricular ni continuidad semántica.

La cifra de 6,516 páginas describe exclusivamente activos fuente admitidos; no debe reinterpretarse como equivalencia con todas las posiciones nominales declaradas por los visores.

## Corrección exhaustiva 37 → 40

Las tres identidades incorporadas son:

1. `H1966P6CI374` — `U1-H1966P6CI374`, **MI CUADERNO DE TRABAJO DE ESTUDIO DE LA NATURALEZA**: 179 posiciones de visor, 178 JPEG fuente, una posición terminal sintética, cero huecos internos;
2. `H1966P6CI375` — `U1-H1966P6CI375`, **MI LIBRO DE ESTUDIO DE LA NATURALEZA**: 163 posiciones de visor, 162 JPEG fuente, una posición terminal sintética, cero huecos internos;
3. `H1993P6CI209` — `LTMD-CN6-G1993-DH`, **Ciencias Naturales y desarrollo humano**: 251 posiciones de visor, 250 JPEG fuente, una posición terminal sintética.

Los dos objetos de 1966 están documentados en `data/catalog/ltmd_u1_w1_1966_page_manifest.csv` y su resumen. El objeto 1993-DH está documentado en `data/expansion/cn46_page_manifest.csv` y su resumen. En los tres casos el número de hashes SHA-256 únicos coincide con el número de JPEG fuente admitidos.

La suma correctiva es 340 + 250 = 590 páginas fuente adicionales. Por tanto: 5,926 + 590 = **6,516**.

## Normalización de procedencia

W1 no parte de un único manifiesto histórico. Su procedencia exhaustiva está distribuida entre cuatro capas versionadas:

1. `data/catalog/ciencias_naturales_pending_page_manifest.csv`, para activos auditados directamente y casos con huecos persistentes documentados;
2. `data/catalog/ltmd_u1_w1_1966_page_manifest.csv`, para los dos objetos de 1966;
3. `data/expansion/cn46_page_manifest.csv`, para objetos CN4/CN6 ya auditados, incluido `LTMD-CN6-G1993-DH`;
4. `data/catalog/cn5_pilot_sha/`, para los cuatro objetos CN5 cuyo piloto quedó posteriormente anclado criptográficamente.

`data/catalog/ciencias_naturales_family_asset_readiness.csv` se conserva sin modificación como registro histórico de 37 identidades. `scripts/build_ftrl_w1_inputs.py` versión lógica 0.2 reconcilia ese registro con el denominador maestro y las tres disposiciones suplementarias, y produce bajo `local/ftrl/` un manifiesto exhaustivo de activos y un inventario exhaustivo de procesamiento.

La normalización es determinista, sin acceso de red y sin texto OCR. No sustituye a las capas documentales originales ni modifica su autoridad metodológica.

## Gate de exhaustividad previo

Antes del preflight criptográfico, `scripts/audit_ftrl_w1_exhaustive_denominator.py` debe confirmar:

- denominador maestro W1 = 40;
- registro histórico familiar = 37;
- disposiciones FTRL suplementarias = 3;
- disposiciones FTRL explícitas = 40;
- cero identidades W1 sin disposición;
- cero identidades extra fuera del denominador.

La ausencia de cualquiera de las 40 identidades bloquea la clasificación de exhaustividad.

## Gate criptográfico obligatorio

Antes de iniciar OCR, `scripts/preflight_ftrl_w1.py --require-cryptographic-ready` debe devolver `status=ready` bajo `LTMD_FTRL_W1_PREFLIGHT_0.3` y confirmar, como mínimo:

- 40 identidades históricas;
- 36 objetos canónicos;
- 4 aliases byte-a-byte;
- 6,516 JPEG fuente admitidos;
- 3 posiciones internas no servidas documentadas;
- 34 posiciones terminales sintéticas;
- 4 objetos CN5 anclados;
- 759 páginas CN5 con correspondencia de bytes respecto de la evidencia técnica previa;
- dos objetos 1966 con manifiesto SHA-256 versionado;
- `LTMD-CN6-G1993-DH` incorporado desde CN46;
- cero objetos CN46 fuera del denominador exhaustivo W1;
- cero objetos canónicos sin capa de procedencia criptográfica aceptada.

Cualquier deriva bloquea la ejecución integral.

## Ejecución

La referencia ejecutable integral es:

```bash
python scripts/run_ftrl_w1.py \
  --full \
  --workers 2 \
  --output-dir local/ftrl
```

El workflow `.github/workflows/validate-ftrl-w1-full.yml` reproduce esta ejecución en GitHub Actions con Python 3.12, Tesseract y el modelo español `spa`, y SQLite con FTS5.

La paralelización en dos shards altera únicamente la planificación del procesamiento. No modifica la cohorte, los hashes esperados, la identidad de página, el orden de concatenación final ni las reglas de aceptación. Cada descarga se verifica contra el SHA-256 versionado antes del OCR.

El antiguo sello `data/research/ltmd_u1_w1_full_run_stamp.json` queda asociado al protocolo 0.1 y no debe reactivar una corrida considerada exhaustiva. La versión 0.2 utiliza exclusivamente un nuevo sello `data/research/ltmd_u1_w1_exhaustive_full_run_stamp.json`, creado sólo después de que los gates del PR de corrección hayan pasado.

## Gates de completitud

Una corrida integral exhaustiva sólo podrá clasificarse como técnicamente validada si cumple simultáneamente:

1. 6,516 registros de página FTRL;
2. 6,516 filas en la tabla `pages` de SQLite;
3. 6,516 filas en el índice FTS5;
4. `PRAGMA integrity_check = ok`;
5. 36 objetos canónicos con páginas OCR;
6. 40 identidades históricas técnicamente representadas en la tabla de identidades;
7. cero páginas procesadas con tamaño de fuente desconocido;
8. commit Git exacto y contexto de GitHub Actions registrados en el manifiesto de corrida;
9. manifiesto FTRL con estado `validated` y ola única `W1`;
10. salida QC sin texto con cardinalidad de 6,516 páginas;
11. OCR por página, SQLite y cola detallada de QC mantenidos fuera de publicación y cubiertos por `.gitignore`;
12. artefactos públicos limitados a evidencia text-free: preflight, manifiesto agregado de corrida y resumen agregado de control de calidad.

Una falla en cualquier gate mantiene la corrida en estado diagnóstico y prohíbe declarar W1 cerrado en FTRL.

## Control de calidad OCR

Después de construir el corpus, `scripts/build_ftrl_qc_queue.py` genera una cola diagnóstica local y un resumen agregado sin texto. Se conservan los umbrales preregistrados de FTRL 0.1 para páginas sin texto recuperable, confianza ausente, baja confianza y texto excepcionalmente corto.

La cola sirve para priorizar revisión humana. Una página sin bandera no equivale a transcripción validada y una página con baja confianza no prueba, por sí sola, que el contenido OCR sea incorrecto.

## Consultas e interpretación

Esta primera corrida integral exhaustiva W1 no ejecuta consultas historiográficas preregistradas. El objetivo es demostrar reconstrucción técnica integral de la cohorte fuente-admitida y producir un mapa reproducible de calidad OCR antes de definir constructos analíticos.

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

Sólo después de una corrida integral exhaustiva válida se actualizará la hoja de ruta para pasar W1 de `cryptographic-ready` a `corpus_ready`/`ocr_available`. La etiqueta `semantic_ready` requerirá trabajo humano adicional y no puede inferirse de una ejecución técnica exitosa.
