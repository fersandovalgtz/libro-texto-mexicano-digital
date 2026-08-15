# Flujo de ejecución CER/WER — piloto 0.1

## Objetivo

Dejar completamente definido el procedimiento que deberá ejecutarse **después** de que exista una referencia humana revisada, sin improvisar decisiones técnicas ni publicar texto fuente.

## Capas

### Pública/reproducible

GitHub contiene:

- definición de las muestras;
- coordenadas/regiones si posteriormente se publican como metadatos;
- pipeline OCR;
- scripts de construcción de hipótesis y evaluación;
- métricas CER/WER;
- resúmenes agregados.

### Privada

Google Drive contiene:

- `human_reference_text_private`;
- `ocr_region_text_private`;
- estado de primera/segunda revisión;
- notas de transcripción que puedan reproducir material fuente.

La ubicación exacta del archivo privado se conserva en la bitácora de Notion, no en GitHub.

## Flujo primario — 48 páginas

### Paso 1 — fijar el scope

Para cada fila:

1. abrir la URL oficial;
2. seleccionar `full_page` o `crop_block`;
3. si `crop_block`, registrar `crop_x0,y0,x1,y1` normalizados;
4. no consultar CER/WER para tomar esta decisión.

Seguir `docs/OCR_REFERENCE_ALIGNMENT_PROTOCOL.md`.

### Paso 2 — transcripción humana

Completar `human_reference_text_private` leyendo la imagen fuente.

Reglas:

- no partir de la salida OCR;
- respetar orden natural de lectura;
- aplicar consistentemente reglas de encabezados, numeración y palabras partidas;
- registrar excepciones en notas.

### Paso 3 — segunda revisión

Otra revisión humana debe comprobar la transcripción y marcar:

- `second_review_status = reviewed`;
- `reference_status = reviewed`.

Si sólo existe una persona, la segunda revisión debe hacerse en otro momento y registrarse como tal.

### Paso 4 — exportar copia privada

Exportar la pestaña como CSV a un directorio privado/local de trabajo.

**No colocar el CSV privado en `data/` ni commitearlo.**

### Paso 5 — construir hipótesis OCR alineada

Ejecutar en entorno privado:

```bash
python scripts/build_private_ocr_reference_hypotheses.py \
  working/CER_WER_Primary_48_private.csv \
  --output working/CER_WER_Primary_48_with_hypothesis_private.csv
```

El script:

- usa el `selected_psm` congelado en `data/derived/ocr_page_metrics.csv`;
- ejecuta TSV sobre la página completa;
- filtra espacialmente los tokens para `crop_block`;
- conserva la hipótesis textual sólo en el archivo privado.

Método detallado: `docs/OCR_REGION_HYPOTHESIS_METHOD.md`.

### Paso 6 — calcular CER/WER

```bash
python scripts/evaluate_ocr_cer_wer.py \
  working/CER_WER_Primary_48_with_hypothesis_private.csv \
  --output data/derived/ocr_cer_wer_primary_metrics.csv
```

La salida no contiene referencia ni hipótesis textual.

### Paso 7 — auditoría

Antes de publicar métricas:

- confirmar 48 IDs esperados o documentar exclusiones justificadas;
- confirmar scope válido;
- revisar valores CER >1 o WER >1 como posibles indicadores de desalineación;
- revisar referencias con muy pocos caracteres/palabras;
- comprobar que ninguna fila marcada `reviewed` carezca de segunda revisión.

### Paso 8 — resumen

Una vez unificadas las métricas primarias y de estrés en un archivo de métricas sin texto, ejecutar:

```bash
python scripts/summarize_ocr_cer_wer.py \
  --input data/derived/ocr_cer_wer_metrics.csv \
  --output data/derived/ocr_cer_wer_summary.csv
```

## Flujo de estrés — 12 páginas

Repetir el mismo procedimiento usando la pestaña `Stress_12`.

Sus resultados deben etiquetarse `sample_type = stress` y reportarse **separados** de la muestra primaria.

No combinar automáticamente 48+12 para obtener una sola media porque la muestra de estrés sobrerrepresenta deliberadamente páginas difíciles.

## Métricas principales

### CER por página

`character edits / reference characters`

### WER por página

`word edits / reference words`

### Resumen por generación

El proyecto reportará al menos:

- n válido;
- CER ponderado por caracteres;
- media y mediana CER;
- máximo CER;
- WER ponderado por palabras;
- media y mediana WER;
- máximo WER;
- número de páginas con CER ≤2 %, ≤5 %, ≤10 % y >10 %.

Los umbrales 2/5/10 % son los criterios internos preregistrados en `EXTRACTION_SPEC.md`, no estándares universales.

## Métrica primaria vs sensibilidad

### Principal

Preservar mayúsculas/minúsculas y puntuación bajo la normalización base.

### Sensibilidad opcional

Puede ejecutarse adicionalmente:

```bash
python scripts/evaluate_ocr_cer_wer.py PRIVATE.csv --casefold ...
```

Esto responde cuánto error proviene sólo de capitalización. Debe etiquetarse como análisis de sensibilidad, nunca sustituir silenciosamente la métrica principal.

Cualquier variante que elimine puntuación exigirá una decisión documentada antes de ejecutarse.

## Publicación

Se puede publicar:

- IDs;
- scope y coordenadas;
- longitudes;
- distancias de edición;
- CER/WER;
- agregados;
- versión del pipeline.

No se publica desde este flujo:

- texto humano;
- texto OCR comparable;
- imágenes/crops fuente.

## Sincronización documental al terminar

Cuando se complete CER/WER:

1. commit de métricas/summary en GitHub;
2. registrar run/comandos/versión en Notion;
3. actualizar las 48/12 filas correspondientes en las bases de Notion con CER/WER y estado;
4. actualizar `README.md`, `ROADMAP.md`, `DECISIONS.md` e issue #3;
5. decidir si el OCR supera la puerta de calidad y qué limitaciones deben acompañar los análisis textuales posteriores.
