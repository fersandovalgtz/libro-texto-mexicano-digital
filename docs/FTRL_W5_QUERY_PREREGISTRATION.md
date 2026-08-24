# FTRL W5 — preregistro de consultas historiográficas piloto

Versión: `LTMD_FTRL_QUERY_PROTOCOL_0.1`  
Fecha de congelamiento: **23 de agosto de 2026**  
Ámbito: **W5 Historia**.

## Objetivo

Congelar antes de observar los resultados completos una primera familia de consultas que permita probar la utilidad historiográfica de FTRL sin ajustar retrospectivamente los términos de búsqueda a los hits obtenidos.

El protocolo no anticipa que exista una frecuencia determinada de referencias masónicas ni de Benito Juárez. Su objetivo es separar tres operaciones distintas: recuperación automática, verificación documental y posterior interpretación histórica.

## Archivo autoritativo

Las expresiones ejecutables están versionadas en:

- `data/research/ltmd_ftrl_w5_preregistered_queries.csv`

El archivo conserva `query_id`, constructo, expresión FTS5, función metodológica, ola, regla de verificación y regla interpretativa.

## Consultas congeladas

### W5-MASONRY-PRIMARY

Consulta primaria de referencias explícitas a masonería y familia léxica inmediata. Incluye formas nominales y adjetivales de `masonería`, `masón` y `francmasonería`.

Regla: cada página candidata debe verificarse visualmente contra el activo fuente cuyo SHA-256 ya fue admitido. Los resultados se reportan por separado como páginas, objetos canónicos e identidades históricas.

### W5-MASONRY-SENSITIVITY

Consulta de sensibilidad mediante prefijos `mason*` y `francmason*`. Su función es recuperar variantes morfológicas y algunos patrones que podrían emerger de la normalización o del OCR.

Regla: sólo se auditan como sensibilidad los candidatos no recuperados por la consulta primaria. Un candidato exclusivo de sensibilidad **no se incorpora** al conteo primario hasta confirmar la lectura en la imagen fuente. Se documentan falsos positivos y errores OCR.

### W5-JUAREZ-CONTROL

Frase exacta `"Benito Juárez"` como control nominal de recuperación.

Regla: sirve para comprobar que la capa recupera una entidad histórica nominal de alta plausibilidad en libros de Historia. No constituye un patrón oro de exactitud OCR y un cero tampoco demostraría ausencia en la obra.

## Ejecución

Después de construir el W5 completo:

```bash
python scripts/run_ftrl_query_protocol.py \
  --db local/ftrl/ltmd_u1_w5_full_ocr_search.sqlite \
  --protocol data/research/ltmd_ftrl_w5_preregistered_queries.csv \
  --output local/ftrl/ltmd_u1_w5_query_candidates.json \
  --summary-output local/ftrl/ltmd_u1_w5_query_summary.json \
  --locator-output local/ftrl/ltmd_u1_w5_query_locators.json
```

La ruta recomendada para W5 completo es el orquestador paralelo:

```bash
python scripts/run_ftrl_w5_parallel.py \
  --workers 4 \
  --run-preregistered-queries
```

El orquestador paralelo sólo permite ejecutar el protocolo preregistrado cuando están presentes los **15 objetos canónicos completos**. Una selección parcial o `--max-pages-per-viewer` aborta si se solicita `--run-preregistered-queries`, evitando presentar resultados truncados como prueba historiográfica.

El orquestador serial heredado también conserva la opción:

```bash
python scripts/run_ftrl_w5_pilot.py --full --run-preregistered-queries
```

## Tres salidas distintas

### Candidatos locales con snippets

`--output` contiene:

- expresión de consulta;
- página candidata;
- objeto canónico;
- identidades históricas relacionadas;
- generación y grado;
- URL y SHA-256 fuente;
- confianza OCR;
- snippet FTS y ranking BM25.

Esta salida puede contener OCR textual y permanece bajo `local/` por defecto. No debe versionarse ni transferirse como artefacto público sin una evaluación de derechos separada.

### Resumen agregado sin texto

`--summary-output` contiene únicamente:

- hash del protocolo;
- hash de cada expresión;
- número exacto de páginas hit;
- número de candidatos materializados y señal de truncamiento;
- número de objetos canónicos e identidades históricas en la salida materializada;
- distribuciones por generación y grado;
- reglas de verificación e interpretación.

El resumen está diseñado para poder promoverse posteriormente como evidencia pública derivada, sujeto a la política de publicación vigente.

### Localizadores verificables sin texto

`--locator-output` conserva, por cada candidato materializado:

- `query_id`;
- `page_id` y objeto canónico;
- identidades históricas relacionadas;
- generación, grado e índices de página;
- URL fuente y SHA-256 del activo;
- SHA-256 del OCR local;
- confianza OCR y ranking BM25.

No contiene la expresión textual de la consulta ni snippets OCR. Su función es hacer posible la **verificación visual posterior contra la fuente** sin publicar el corpus reconocido. El archivo conserva además `protocol_sha256`, por lo que cada `query_id` puede vincularse con el protocolo congelado exacto.

## Reglas de análisis

1. Un mismo contenido OCR puede representar más de una identidad histórica demostrada; por ello no se mezclan `hit_pages`, objetos canónicos e identidades.
2. La consulta de sensibilidad no puede aumentar automáticamente el numerador primario.
3. Todo hit utilizado en una afirmación debe verificarse contra la página fuente.
4. Un hit irrelevante se conserva como falso positivo metodológico, no se borra del registro de auditoría.
5. Un cero se reporta como `zero hits under this protocol and technical coverage`, no como ausencia histórica demostrada.
6. Cualquier nueva variante añadida después de observar resultados debe registrarse como **post hoc** y ejecutarse por separado del protocolo 0.1.
7. El archivo de localizadores puede orientar la auditoría, pero nunca sustituye la inspección de la imagen fuente.

## Criterio para pasar a análisis histórico

La fase piloto puede considerarse metodológicamente ejecutada cuando:

- el W5 completo tenga manifiesto de corrida validado;
- el protocolo se ejecute sin truncamiento o el truncamiento quede explicitado;
- todos los hits primarios de masonería hayan sido revisados contra la fuente;
- se auditen los candidatos exclusivos de sensibilidad;
- se revise una muestra documentada del control Benito Juárez;
- el reporte final distinga recuperación, verificación e interpretación.
