# FTRL W5 Historia — validación integral

**Fecha:** 24 de agosto de 2026  
**Estado:** validado técnicamente  
**Alcance:** LTMD-U1, ola W5 Historia

## Resultado reproducible

La corrida integral de `LTMD_FTRL_0.1` para W5 Historia completó satisfactoriamente el pipeline de OCR por página, construcción del índice SQLite FTS5, validación de cardinalidades, comprobación de integridad y ejecución del protocolo de consultas preregistradas.

La evidencia pública de la corrida corresponde a GitHub Actions **run 32743689286**, workflow `Validate FTRL W5 full corpus`. El artefacto publicado contiene únicamente metadatos, hashes y agregados libres de texto fuente; el OCR completo, la base SQLite y los snippets permanecen bajo `local/` y no se publican.

## Cohorte y cardinalidades validadas

| Indicador | Resultado |
|---|---:|
| Identidades históricas | 18 |
| Objetos canónicos de procesamiento | 15 |
| Páginas fuente admitidas | 2,653 |
| Filas de páginas en SQLite | 2,653 |
| Filas FTS5 | 2,653 |
| Integridad SQLite | `ok` |
| Páginas sin tamaño de fuente | 0 |
| Generaciones incluidas | 1993, 2008, 2011, 2014, 2019 |
| Grados | 4, 5, 6 |

La cifra correcta y reproducible de páginas para los 15 objetos canónicos es **2,653**. La expectativa preparatoria anterior de 2,443 fue corregida antes de ejecutar el OCR integral; por tanto, ningún resultado completo fue aceptado contra una cardinalidad incorrecta.

## OCR observado

El corpus produjo **3,745,043 caracteres OCR** y **609,832 palabras OCR**. La confianza OCR media fue **88.384798**, la mediana **91.571332**, el máximo **96.838142** y el mínimo **20.722095**. Se registraron **84 páginas sin texto de búsqueda**, que permanecen explícitamente como casos que requieren auditoría; no se interpretan como páginas históricamente vacías.

El motor registrado fue Tesseract 5.3.4, idioma `spa`, PSM 3. El pipeline de OCR fue `LTMD_FTRL_OCR_0.1` y el esquema de registro `LTMD_PAGE_OCR_0.1`.

## Consultas preregistradas

El protocolo se ejecutó después de construir y validar el corpus completo. Los resultados agregados fueron:

| Consulta | Rol | Páginas candidatas exactas | Objetos canónicos | Identidades históricas |
|---|---|---:|---:|---:|
| `W5-MASONRY-PRIMARY` | primaria | 1 | 1 | 1 |
| `W5-MASONRY-SENSITIVITY` | sensibilidad OCR | 1 | 1 | 1 |
| `W5-JUAREZ-CONTROL` | control nominal | 70 | 9 | 12 |

La consulta primaria y la consulta de sensibilidad convergen en un candidato de 1993, grado 6. Esto **no constituye todavía una afirmación histórica**: el candidato debe verificarse visualmente contra el activo fuente admitido por SHA-256. La consulta de Benito Juárez funciona como control de recuperación y no como patrón oro de exactitud OCR.

## Procedencia e integridad

- GitHub Actions run: `32743689286`
- commit registrado por el manifiesto: `6c515fb66928c65a27a59691739f9fe9cd7ab3b7`
- `processing_inventory` SHA-256: `66982ca6e1d61fcbf3e2ff56dd34a819ede16fa675c8cf16ff1c19b1443d207f`
- `asset_manifest` SHA-256: `120ea791e91938ef2cdcab7f790c7fac10a16abe53aef057d36658a059320f14`
- OCR JSONL restringido SHA-256: `da57daa60a5d99d65dd8d2373edef2a8fd6148bb26f623cd82c03d80b3203bad`
- SQLite restringido SHA-256: `e80775b5ecb4d24faa857d627f98ae3404b4ef9d19564270bd6bd352c53bd14e`
- artefacto público text-free SHA-256: `4d68a0d69763a8d3ef43e74311bd37b43d4c2b743a11ac0ce205e30e634e66b1`

## Límites de inferencia

Este cierre es **técnico y reproducible**, no semántico. Se mantienen las reglas:

`corpus_ready != semantic_ready`  
`ocr_available != text_verified`  
`search_hit != historical_claim`  
`zero_hits != demonstrated_absence`

Por ello, W5 puede considerarse cerrado para construcción FTRL e indexación técnica, pero no para interpretación historiográfica de candidatos individuales hasta completar la verificación visual contra las fuentes.

## Siguiente gate

Antes de derivar resultados historiográficos deben auditarse las páginas problemáticas ya priorizadas y verificarse visualmente todos los candidatos de la consulta primaria y de sensibilidad. Después de ese gate, W5 puede funcionar como patrón metodológico para escalar FTRL a W1–W11 sin alterar la separación entre procesamiento técnico y validación humana.
