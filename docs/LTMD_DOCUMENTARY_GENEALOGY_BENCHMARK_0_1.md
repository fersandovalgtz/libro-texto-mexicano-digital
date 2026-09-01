# LTMD Documentary Genealogy Benchmark 0.1

Versión: `LTMD_DOCUMENTARY_GENEALOGY_BENCHMARK_0.1`

## Pregunta

¿Hasta qué punto la infraestructura LTMD permite medir **persistencia, reutilización y reemplazo documental** entre generaciones de libros sin depender de validación semántica humana?

La respuesta 0.1 es afirmativa para relaciones documentales duras y descriptivas: hashes de fuente, hashes de representación textual, conteos, páginas técnicamente admisibles y candidatos de similitud con umbrales preregistrados.

## Fuente

El benchmark utiliza `data/analytics/ltmd_u1_reuse_similarity_materialization_0_1.json`, producido sobre:

- 492 objetos canónicos;
- 86,549 páginas;
- 71,274 páginas textualmente admisibles para la capa de reutilización;
- 65,488 páginas elegibles para shingles de similitud.

No publica pares, identificadores de página, texto OCR ni hashes fuente privados.

## Resultados descriptivos congelados

La snapshot pública está en:

- `data/benchmarks/ltmd_documentary_genealogy_0_1.json`

### Cobertura técnica

- páginas textualmente admisibles: **71,274 / 86,549 = 82.35%**;
- páginas excluidas por baja información: **15,275 / 86,549 = 17.65%**;
- páginas elegibles para shingles entre las admisibles: **65,488 / 71,274 = 91.88%**.

### Persistencia exacta entre generaciones

Entre los grupos de fuente exacta repetida:

- grupos repetidos: **3,347**;
- grupos que cruzan generaciones: **3,150**;
- proporción descriptiva: **94.11%**.

Entre los grupos de representación textual exacta repetida:

- grupos repetidos: **3,013**;
- grupos que cruzan generaciones: **2,758**;
- proporción descriptiva: **91.54%**.

Estas proporciones no representan el porcentaje de páginas que “no cambió”, porque la unidad del denominador es el **grupo repetido**, no todas las páginas ni todos los libros. Se publican como evidencia de que existe suficiente reutilización exacta intergeneracional para construir una genealogía documental rigurosa.

## Qué puede afirmarse

- la reutilización exacta entre generaciones es una propiedad empíricamente frecuente entre los grupos repetidos identificados por la capa 0.1;
- LTMD puede distinguir identidad exacta de fuente, identidad exacta de representación textual y similitud no exacta;
- la escala observada justifica desarrollar métricas de persistencia, reemplazo y novelty documental;
- las relaciones exactas permiten construir grafos de dependencia documental sin necesidad de etiquetado humano.

## Qué no puede afirmarse automáticamente

- que reutilización documental implique continuidad pedagógica;
- que cambio textual implique reforma conceptual;
- que similitud de shingles implique equivalencia semántica;
- que páginas idénticas hayan sido usadas de la misma forma en el aula;
- que un cambio detectado tenga causalidad atribuible a una reforma específica.

## Métricas siguientes

### Documentary Persistence Rate

Debe definirse a nivel de página/objeto con denominadores explícitos, evitando confundir grupos repetidos con páginas totales.

### Documentary Novelty Rate

Proporción de unidades de una generación que no tienen relación exacta con generaciones anteriores dentro de la cobertura técnica efectiva.

### Replacement Rate

Proporción de unidades documentales previas que dejan de estar representadas en la generación siguiente, con tratamiento explícito de huecos de cobertura.

### Documentary Half-Life

Estimación descriptiva de cuántas generaciones persiste una unidad documental antes de desaparecer o transformarse, usando análisis de supervivencia sobre relaciones de identidad/reutilización.

### Transition Graph

Grafo dirigido generación→generación con pesos de persistencia, aparición y desaparición. Las aristas exactas por hash tienen mayor fuerza epistemológica que candidatos de similitud.

### Change-point analysis

Puede aplicarse a series de tasas documentales para detectar puntos de cambio estadístico. La asociación posterior con reformas curriculares debe tratarse como interpretación histórica separada.

## Robustez requerida para 0.2

- bootstrap por objeto y generación;
- intervalos para tasas documentales;
- sensibilidad a exclusión de páginas de baja información;
- comparación source-hash vs text-hash;
- análisis con y sin candidatos near-exact;
- estabilidad de change points;
- negative controls temporalmente permutados;
- reporte explícito de cobertura efectiva por periodo.

## Posible producto científico

Título de trabajo:

**Continuidad y ruptura en los Libros de Texto Gratuitos mexicanos: una genealogía computacional del currículo escolar, 1960–2026**.

La contribución central no sería afirmar automáticamente continuidad curricular, sino ofrecer por primera vez una infraestructura reproducible para distinguir **persistencia documental exacta**, **cambio textual**, **similitud** e **interpretación histórica** en una serie nacional de libros de texto.
