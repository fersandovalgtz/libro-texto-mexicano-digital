# FTRL W5 Historia — acta de validación técnica integral

Fecha: 2026-08-24  
Workflow: `Validate FTRL W5 full corpus`  
GitHub Actions run: `32743689286`  
Estado técnico: **VALIDATED**

## Alcance validado

La corrida integral W5 procesó la cohorte fuente-admitida completa de Historia:

- 18 identidades históricas;
- 15 objetos canónicos de procesamiento;
- 2,653 páginas fuente admitidas;
- 2,653 registros FTRL;
- 2,653 filas en SQLite `pages`;
- 2,653 filas FTS5;
- `PRAGMA integrity_check = ok`;
- 0 páginas con tamaño de fuente desconocido.

La ejecución utilizó Tesseract 5.3.4, idioma `spa`, PSM 3, Python 3.12.14 y SQLite 3.45.1. El manifiesto conserva además commit, ref, hashes SHA-256 y tamaños de los artefactos reconstruibles.

## Perfil OCR observado

El corpus produjo 3,745,043 caracteres OCR y 609,832 palabras OCR. La confianza se observó en 2,569 páginas, con media 88.384798, mediana 91.571332, mínimo 20.722095 y máximo 96.838142.

**84 páginas** quedaron con `search_text` vacío y sin confianza OCR observada. Este resultado no se corrige ni se imputa silenciosamente: constituye la primera cola explícita de control de calidad posterior a la validación estructural.

## Distribución de páginas

Por generación:

- 1993: 510;
- 2008: 534;
- 2011: 563;
- 2014: 523;
- 2019: 523.

Por grado:

- 4.º: 951;
- 5.º: 983;
- 6.º: 719.

## Consultas preregistradas

El protocolo ejecutó tres consultas text-free y preservó únicamente agregados e hashes de las expresiones.

| Query | Rol | Páginas candidatas exactas | Canónicos representados | Identidades históricas representadas |
|---|---|---:|---:|---:|
| `W5-MASONRY-PRIMARY` | primary | 1 | 1 | 1 |
| `W5-MASONRY-SENSITIVITY` | sensitivity | 1 | 1 | 1 |
| `W5-JUAREZ-CONTROL` | control | 70 | 9 | 12 |

El candidato primario de masonería se ubica agregadamente en la generación 1993, grado 6. **No se contabiliza todavía como ocurrencia histórica verificada.** Debe confrontarse visualmente contra el activo fuente admitido antes de producir cualquier afirmación sustantiva. La consulta de sensibilidad tampoco se suma automáticamente al conteo primario.

El control nominal de Benito Juárez recuperó 70 páginas candidatas distribuidas en las cinco generaciones de la cohorte; funciona como control de recuperación, no como patrón oro de exactitud OCR ni como medida de cobertura historiográfica.

## Evidencia pública preservada

Se versionan únicamente:

- `data/research/validation/ltmd_u1_w5_full_run_manifest_2026-08-24.json`;
- `data/research/validation/ltmd_u1_w5_query_summary_2026-08-24.json`;
- esta acta de validación.

Los archivos OCR JSONL, el índice SQLite, las imágenes fuente y cualquier materialización con texto fuente extenso permanecen bajo `local/` o como artefactos temporales restringidos y no se incorporan al repositorio.

## Resultado científico correcto

La corrida demuestra que W5 es técnicamente reconstruible, íntegra a nivel de cardinalidad e indexación y capaz de ejecutar recuperación full-text preregistrada con procedencia verificable.

No demuestra todavía:

- exactitud OCR página por página;
- validez semántica humana;
- pertinencia historiográfica de los candidatos;
- ausencia histórica cuando una consulta produce cero hits;
- generalización automática del comportamiento de W5 a W1–W11.

Se mantienen vigentes las reglas:

- `corpus_ready != semantic_ready`;
- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`.

## Gates posteriores

El cierre de W5 requiere ahora dos carriles distintos que no deben mezclarse:

1. **QC OCR**: auditar la cola text-free de páginas problemáticas, comenzando por páginas sin `search_text`, baja confianza y las páginas preregistradas de atención prioritaria.
2. **Verificación historiográfica**: revisar visualmente los candidatos de las consultas preregistradas contra sus activos fuente y registrar confirmación, falsos positivos o errores OCR sin convertir la búsqueda en evidencia por sí sola.

Una vez preservadas esas verificaciones, W5 puede pasar de referencia técnica validada a caso metodológico listo para sustentar el escalamiento controlado de FTRL a otras cohortes U1.
