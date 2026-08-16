# Plan Maestro LTMD-U1 — cobertura integral de 542 visores

Versión: **LTMD_U1_MASTER_PLAN_0.1**  
Fecha de corte inicial: **2026-08-15**  
Universo de referencia: snapshot reproducible del Catálogo Histórico de CONALITEG ya incorporado a LTMD.

## 1. Decisión estratégica

LTMD deja de concebirse como un proyecto basado en una muestra de libros y adopta como objetivo explícito de su primera gran fase la **cobertura técnica integral del universo U1**.

**LTMD-U1 = los 542 visores únicos presentes en el snapshot vigente y congelado del Catálogo Histórico de CONALITEG utilizado por el proyecto.**

La meta principal de U1 es:

> **542/542 visores técnicamente representados de forma reproducible, con identidad documental, procedencia, resolución de activos, manifiestos, OCR técnico, PAGESTRUCT, FRAGSEG y modelado explícito de aliases/dependencia cuando corresponda.**

Esta meta técnica es distinta de la validación semántica. U1 no autoriza a aplicar un clasificador no validado a todo el corpus ni convierte automáticamente cada visor en una observación histórica independiente.

## 2. Línea base verificable

El tablero ejecutable `LTMD_U1_COVERAGE_0.2` establece la línea base:

- universo catalogado: **542/542 = 100.00%**;
- títulos normalizados: **542/542 = 100.00%**;
- familias de título normalizadas: **191**;
- activos completamente resueltos con evidencia: **36/542 = 6.64%**;
- activos con resolución parcial documentada: **2/542 = 0.37%**, separados de la cobertura completa;
- PAGESTRUCT/OCR/FRAGSEG directamente materializados: **32/542 = 5.90%**;
- cobertura FRAGSEG efectiva —incluidos cuatro aliases byte-idénticos ya representados—: **36/542 = 6.64%**;
- visores que participan en relaciones documentales registradas: **12/542 = 2.21%**;
- cobertura semántica humana validada: **0/542 = 0.00%**.

El denominador rector de U1 es siempre **viewer_key**. Las métricas de páginas y fragmentos son complementarias y no sustituyen el conteo de objetos documentales.

## 3. Dos conceptos de cobertura

### Cobertura materializada directa

Un visor cuenta como `fragseg_materialized` cuando su objeto fue procesado directamente hasta FRAGSEG y los pasos previos exigidos quedaron materializados.

### Cobertura técnica efectiva

Un visor puede contar como `effective_fragseg_coverage` sin reprocesar sus bytes cuando existe una relación de alias demostrada criptográficamente con un objeto ya procesado. Este criterio se usa, por ejemplo, para los cuatro aliases 2018→2019 de Ciencias Naturales.

La cobertura efectiva **no borra el visor ni fusiona su identidad bibliográfica**. Evita únicamente duplicar procesamiento de activos ya demostrados como idénticos.

## 4. Definición de etapas U1 por visor

Cada fila de `data/catalog/ltmd_u1_coverage.csv` conserva al menos los siguientes estados:

1. `cataloged` — el visor pertenece al snapshot U1;
2. `title_normalized` — título completo y núcleo normalizado recuperados;
3. `asset_resolved_full` / `asset_resolved_partial` — estado demostrado de activos fuente;
4. `page_manifest_ready` — manifiesto de páginas/activos materializado;
5. `ocr_ready` — capa OCR técnica terminada bajo política de no persistencia de fuente sustitutiva;
6. `pagestruct_ready` — estructura de página materializada;
7. `fragseg_materialized` — segmentación directa terminada;
8. `effective_fragseg_coverage` — cobertura directa o heredada exclusivamente mediante alias verificado;
9. `dependence_audited` — existencia de una relación documental registrada/auditada;
10. `semantic_ready` — reservado a clasificación validada; actualmente cero.

La regla fundamental es que **una etapa inferior no implica una superior**.

## 5. Arquitectura industrial

El pipeline universal de U1 será:

`catálogo → identidad documental → resolver activos → SHA-256 → OCR temporal → PAGESTRUCT → FRAGSEG → dependencia documental → corpus técnico`

La unidad de ejecución debe ser el **libro/visor**, con shards independientes y ensamblado estricto. Un fallo de un objeto no debe obligar a recalcular objetos ya válidos.

Toda reconstrucción de fuente seguirá el contrato ya probado:

1. resolver el activo esperado;
2. descargar temporalmente;
3. verificar SHA-256;
4. abortar ante discrepancia;
5. derivar sólo outputs permitidos;
6. eliminar fuente temporal;
7. no incorporar a Git imágenes, PDF u OCR íntegro sustitutivo.

## 6. Olas operativas

La taxonomía siguiente es **operativa y conservadora**. Se deriva de señales fuertes del título normalizado; no pretende describir exhaustivamente el currículo. Los títulos con más de una señal pasan a `integrados_multiarea`; los ambiguos quedan para revisión.

| Ola | Dominio operativo | Visores U1 | Cobertura efectiva actual | Restantes |
|---|---|---:|---:|---:|
| W1 | Ciencias Naturales | 40 | 36 | **4** |
| W2 | Matemáticas | 64 | 0 | **64** |
| W3 | Español/Lengua | 130 | 0 | **130** |
| W4 | Ciencias Sociales | 14 | 0 | **14** |
| W5 | Historia | 18 | 0 | **18** |
| W6 | Geografía/Atlas | 42 | 0 | **42** |
| W7 | Cívica/Ética | 30 | 0 | **30** |
| W8 | Artes | 20 | 0 | **20** |
| W9 | Educación Física | 4 | 0 | **4** |
| W10 | Integrados/multiarea | 69 | 0 | **69** |
| W11 | Otros/no clasificados | 111 | 0 | **111** |

Los 36 objetos ya cubiertos efectivamente aparecen como W0 en la cola ejecutable y no deben procesarse de nuevo.

## 7. Primera acción: cerrar W1

La ola inmediata consta sólo de cuatro visores:

- `H1966P6CI374` — *Mi cuaderno de trabajo de Estudio de la Naturaleza*;
- `H1966P6CI375` — *Mi libro de Estudio de la Naturaleza*;
- `H2008P3CI263` — *Ciencias Naturales*, 3º, con resolución parcial ya documentada;
- `H2008P4CI268` — *Ciencias Naturales*, 4º, con resolución parcial ya documentada.

Los dos objetos 1966 deben ingresar por el pipeline universal desde asset audit. Los dos objetos 2008 deben tratarse como casos de recuperación/alternativa de fuente o excepción documentada; nunca se inventarán páginas ni se reinterpretará un `internal_unserved_position` como hecho bibliográfico sin evidencia externa.

El hito W1 se considera cerrado cuando los cuatro objetos tengan una resolución técnica defendible y el tablero pueda explicar con precisión qué está materializado y qué, en su caso, permanece como excepción documental.

## 8. W2 y escalamiento posterior

Una vez cerrado W1, **Matemáticas (64 visores)** será la primera prueba de transferencia masiva a un dominio distinto. El objetivo no será aplicar semántica de Ciencias Naturales a Matemáticas, sino demostrar que el pipeline universal de corpus es estable frente a otra familia documental.

Luego seguirá Español/Lengua (130), que por su tamaño será el primer gran estrés industrial del sistema. El orden puede ajustarse por razones técnicas —por ejemplo, una arquitectura de visor excepcional—, pero cualquier cambio quedará versionado y no se basará en resultados históricos atractivos.

## 9. Capa universal vs. capas semánticas

### Universal U1

Debe alcanzar 542/542 para:

- catálogo e identidad;
- resolución o excepción explícita de activos;
- procedencia y hashes;
- OCR técnico;
- PAGESTRUCT;
- FRAGSEG;
- dependencia documental cuando exista evidencia.

### Semántica especializada

Se diseñará por dominios o problemas de investigación y deberá tener validación humana propia. Un modelo útil en Ciencias Naturales no se presume válido para Matemáticas, Español o Historia.

SEMB 0.3 del piloto continúa en `WAITING_HUMAN_REFERENCE`. No se utilizará la expansión U1 para saltarse ese gate.

## 10. KPIs rectores

El tablero de U1 reportará como mínimo:

- `cataloged / 542`;
- `asset_resolved_full / 542`;
- `ocr_ready_direct / 542`;
- `pagestruct_ready_direct / 542`;
- `fragseg_materialized_direct / 542`;
- `effective_fragseg_coverage / 542`;
- `dependence_audited / 542`;
- `semantic_ready_validated / 542`;
- cobertura por dominio y ola.

Nunca se presentará el porcentaje de catálogo como si fuera porcentaje de corpus procesado.

## 11. Control de calidad y no retroactividad

Cada ola debe:

- congelar su lista de entrada antes del procesamiento;
- conservar viewer_key/book_id y procedencia;
- registrar anomalías sin corregirlas silenciosamente;
- publicar outputs sólo después de invariantes de cardinalidad/unicidad;
- actualizar el tablero automáticamente;
- no reescribir releases históricas ya publicadas;
- producir una nueva versión si cambia una regla material de corpus.

La release `v0.1.0-rc.1` permanece como corte histórico previo a este programa U1 y no se modifica retroactivamente.

## 12. Automatización

El builder `scripts/build_ltmd_u1_coverage.py` y el workflow `.github/workflows/build-ltmd-u1-coverage.yml` recomputan el tablero a partir de artefactos reales del repositorio.

Salidas:

- `data/catalog/ltmd_u1_coverage.csv` — 542 filas, una por visor;
- `data/catalog/ltmd_u1_coverage_summary.csv` — cobertura por etapa;
- `data/catalog/ltmd_u1_domain_summary.csv` — cobertura por dominio operativo;
- `data/catalog/ltmd_u1_wave_queue.csv` — cola de procesamiento completa;
- `data/catalog/ltmd_u1_coverage.md` — tablero legible.

## 13. Criterio de éxito de U1

U1 no termina cuando haya “muchos libros” procesados. Termina cuando el tablero alcance una explicación defendible de **542/542 visores**, distinguiendo procesamiento directo, aliases verificados, excepciones documentales y dependencia entre objetos.

Ese corte constituirá el primer corpus histórico-computacional integral de LTMD para el universo definido por el snapshot U1. La expansión posterior fuera de esos 542 objetos deberá abrirse como un universo U2 separado y versionado.
