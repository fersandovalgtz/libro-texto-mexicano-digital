# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante historia de la educación, humanidades digitales, análisis computacional y ciencia abierta.

## Estado actual

**LTMD adopta como objetivo de su primera gran fase la cobertura integral del universo histórico disponible en el snapshot U1 del Catálogo Histórico de CONALITEG: 542 visores. W1 Ciencias Naturales, W3 Español/Lengua, W4 Ciencias Sociales y W5 Historia están cerradas técnicamente; W2 Matemáticas conserva cuatro excepciones de routing sin imputación; W6 Geografía/Atlas está activa únicamente en fase `source-first`.**

Corte documental de esta actualización: **16 de agosto de 2026**.

El tablero reproducible `LTMD_U1_COVERAGE_0.6`, recompuesto desde la cola maestra y las actas de cierre W1–W5, reporta:

- universo U1 censado: **542/542** identidades documentales;
- cobertura técnica efectiva cerrada o resuelta: **262/542 (48.34%)**;
- objetos canónicos de procesamiento: **236/542 (43.54%)**;
- cobertura semántica humana validada: **0/542**;
- W6 Geografía/Atlas: **42** identidades en auditoría de fuente, todavía sin incorporarse a la cobertura técnica efectiva.

`corpus_ready` **no equivale** a `semantic_ready`. Las ocurrencias técnicas de fragmento tampoco equivalen a observaciones históricas independientes: LTMD representa explícitamente reutilización, revisión, reemplazo, aliases y dependencia documental.

## Objetivo maestro LTMD-U1: 542/542

El universo operativo **LTMD-U1** está fijado en **542 visores únicos**. El tablero vivo [`data/catalog/ltmd_u1_coverage.md`](data/catalog/ltmd_u1_coverage.md) mantiene dos denominadores distintos: identidades documentales técnicamente representadas y objetos canónicos realmente procesados. Esta distinción impide inflar el corpus cuando una identidad se resuelve mediante un alias o una ruta criptográficamente demostrada.

| Ola | Dominio operacional | Plan | Cobertura efectiva | Canónicos | Estado |
|---|---|---:|---:|---:|---|
| W1 | `ciencias_naturales` | 40 | 40 | 36 | cerrada |
| W2 | `matematicas` | 64 | 60 | 57 | parcial; 4 excepciones preservadas |
| W3 | `espanol_lengua` | 130 | 130 | 114 | cerrada |
| W4 | `ciencias_sociales` | 14 | 14 | 14 | cerrada |
| W5 | `historia` | 18 | 18 | 15 | cerrada |
| W6 | `geografia_atlas` | 42 | 0 | 0 | `source-first` activa |
| W7 | `civica_etica` | 30 | 0 | 0 | en cola |
| W8 | `artes` | 20 | 0 | 0 | en cola |
| W9 | `educacion_fisica` | 4 | 0 | 0 | en cola |
| W10 | `integrados_multiarea` | 69 | 0 | 0 | en cola |
| W11 | `otros_no_clasificados` | 111 | 0 | 0 | en cola |

La meta U1 es alcanzar **542/542 visores técnicamente representados**, mediante procesamiento directo o relaciones de fuente demostradas, conservando siempre identidad documental y excepciones. Este objetivo no autoriza a extrapolar clasificadores semánticos de un dominio a otro sin validación humana propia.

El programa completo está en **[`docs/LTMD_U1_MASTER_PLAN_0_1.md`](docs/LTMD_U1_MASTER_PLAN_0_1.md)**, el tablero vivo en **[`data/catalog/ltmd_u1_coverage.md`](data/catalog/ltmd_u1_coverage.md)** y la cola integral en `data/catalog/ltmd_u1_wave_queue.csv`.

### U1-W1 — Ciencias Naturales: CERRADA

El dominio operativo `ciencias_naturales` contiene **40 visores** y queda en **40/40 de cobertura efectiva**. Treinta y seis están procesados directamente hasta FRAGSEG y cuatro son aliases 2018→2019 demostrados byte por byte. El cierre detallado está en [`docs/LTMD_U1_W1_COMPLETION_2026-08-15.md`](docs/LTMD_U1_W1_COMPLETION_2026-08-15.md).

W1 incorporó además dos materiales de *Estudio de la Naturaleza* de 1966 y resolvió criptográficamente las tres posiciones internas no servidas de los dos libros 2008 sin borrar la anomalía original ni falsear procedencia.

### U1-W2 — Matemáticas: PARCIAL CON EXCEPCIONES PRESERVADAS

W2 está congelada en **64 visores**. Tiene **60/64 identidades con activos efectivamente resueltos** y **57 objetos canónicos computados**. Cuatro visores DMA 2018 conservan excepciones de routing no resueltas; no se imputan ni se sustituyen por similitud de título, año o cardinalidad. La capa FRAGSEG directamente computada contiene **135,727 fragmentos técnicos**. El cierre vigente está en [`docs/LTMD_U1_W2_COMPLETION.md`](docs/LTMD_U1_W2_COMPLETION.md).

### U1-W3 — Español/Lengua: CERRADA

W3 cubre **130/130 identidades** mediante **114 objetos canónicos** y 16 aliases/provenance relations demostradas. Se verificaron **20,765 páginas**, PAGESTRUCT habilitó **17,337 páginas** y FRAGSEG produjo **222,490 fragmentos técnicos**. El análisis de reutilización exacta conserva la dependencia documental en lugar de asumir independencia entre generaciones. Véase [`docs/LTMD_U1_W3_COMPLETION.md`](docs/LTMD_U1_W3_COMPLETION.md).

### U1-W4 — Ciencias Sociales: CERRADA

W4 cubre **14/14 identidades y objetos canónicos**. Se procesaron **2,414 páginas**, PAGESTRUCT habilitó **2,018 páginas** y FRAGSEG produjo **21,380 fragmentos técnicos**. Véase [`docs/LTMD_U1_W4_COMPLETION.md`](docs/LTMD_U1_W4_COMPLETION.md).

### U1-W5 — Historia: CERRADA

W5 cubre **18/18 identidades históricas** mediante **15 objetos canónicos**. Tres entradas 2018 se resuelven operacionalmente a rutas 2019 después de revalidar **523/523 activos** por SHA-256 y tamaño, sin fusionar las identidades documentales de catálogo. OCR verificó **2,653/2,653 páginas**, PAGESTRUCT habilitó **2,243** y FRAGSEG produjo **32,645 fragmentos técnicos**. El análisis de reutilización exacta obtuvo **25,492 unidades textuales exactas únicas** y **105 pares de visores** con al menos una unidad compartida. Véase [`docs/LTMD_U1_W5_COMPLETION.md`](docs/LTMD_U1_W5_COMPLETION.md).

### U1-W6 — Geografía/Atlas: SOURCE-FIRST ACTIVA

W6 está congelada en **42 visores**. El registro central `claves.json` declara **7,766 posiciones**. Cuarenta y un visores presentan la arquitectura HTML dinámica estándar; `H1993P5GE204` (*Atlas de Geografía Universal*) se conserva como excepción de arquitectura HTML, aunque sí cuenta con declaración en el registro central. Esta ola permanece deliberadamente antes de OCR: primero deben auditarse posición por posición los activos servidos, sus hashes, huecos, terminales, rutas alternativas y posibles relaciones de identidad.

## Release publicada

La primera release candidate metodológica pública es **[`v0.1.0-rc.1`](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/releases/tag/v0.1.0-rc.1)**.

Antes de crear el tag, el preflight reproducible demostró `rc_technical_ready=true`, `publish_ready=true`, cero failures/blockers, `LTMD_INTEGRITY_0.6` 166/166 y recomputación SHA-256 completa en PASS. El tag conserva ese corte histórico; el programa U1 posterior evoluciona en `main` y no modifica retroactivamente la release.

**El DOI de Zenodo está pendiente hasta que exista un registro real del depósito.** LTMD no anticipa ni inventa identificadores persistentes.

Documentos del paquete de release:

- [`VERSION`](VERSION)
- [`CHANGELOG.md`](CHANGELOG.md)
- [`LICENSE`](LICENSE) — software propio, Apache License 2.0
- [`DATA_LICENSE.md`](DATA_LICENSE.md) — derivados originales licenciables, CC BY 4.0
- [`docs/RELEASE_NOTES_v0.1.0-rc.1.md`](docs/RELEASE_NOTES_v0.1.0-rc.1.md)
- [`docs/REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md`](docs/REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md)
- [`data/derived/release_candidate_preflight.json`](data/derived/release_candidate_preflight.json)

## Pregunta general

¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

## Arquitectura científica

```text
catálogo institucional
        ↓
identidad documental / viewer_key / book_id
        ↓
resolución de activos + SHA-256
        ↓
OCR temporal
        ↓
PAGESTRUCT
        ↓
FRAGSEG
        ↓
metadatos y hashes
        ↓
validación humana de constructo
        ↓
clasificación validada
        ↓
análisis histórico
```

Para dependencia documental se mantienen vistas reversibles: **object view**, **unique-content view** y **revision view**.

## Ciencias Naturales — primer dominio U1 cerrado

La familia estricta contiene 37 visores; la taxonomía operativa U1 incorpora además materiales afines de *Estudio de la Naturaleza*, para un dominio de **40 visores**.

El cierre W1 dejó:

- 40/40 activos completamente resueltos;
- 36/40 procesados directamente hasta FRAGSEG;
- 4/40 cubiertos mediante aliases 2018→2019 byte-idénticos;
- 0/40 restantes efectivos.

Los cuatro aliases 2018→2019 se fundamentan en **652/652 pares byte-idénticos**. Los dos libros 2008 originalmente presentaban tres posiciones internas no servidas; las tres fueron recuperadas unívocamente mediante alineamiento criptográfico con seis anchors vecinos y cero discrepancias, preservando en el manifiesto reconciliado tanto la URL original fallida como la fuente efectiva.

## Piloto CN5 y SEMB

El piloto utiliza _Ciencias Naturales_ de quinto grado en generaciones 1972, 1988, 1993 y 2014. Es la única capa que llega actualmente a Rule A, SEMB 0.2 y comparación semántica exploratoria.

SEMB 0.2 produjo **99.49% de incertidumbre global** y se conserva como resultado metodológico negativo/diagnóstico. No se bajaron umbrales retrospectivamente para maximizar diferencias históricas.

## SEMB 0.3: referencia humana preregistrada

La infraestructura prehumana contiene **480 casos**: 320 `development`, 160 `locked_validation` y 120 reservados para doble codificación de fiabilidad. Los criterios de aceptación, arquitecturas candidatas y stage gates quedaron congelados antes de observar anotaciones humanas.

Etapa actual: **`WAITING_HUMAN_REFERENCE`**.

La expansión U1 puede continuar técnicamente, pero no se usa para fabricar etiquetas humanas ni para transformar tendencias exploratorias de SEMB 0.2 en narrativa histórica confirmada. Matemáticas, Español, Historia y otros dominios requerirán validación semántica específica cuando sus preguntas analíticas lo exijan.

## Dependencia documental

LTMD no supone independencia por `catalog_generation`. En CN4 1972↔1988, 188/214 páginas alineables son byte-idénticas en la misma posición. Las relaciones documentales, reutilizaciones, reemplazos y aliases forman parte del estimando y de la trazabilidad.

## Catálogo maestro reproducible

El snapshot institucional indexado contiene **542 claves de visor, 542/542 visores alcanzables, 542/542 títulos recuperados y 191 familias de título nuclear**. La identidad documental se fundamenta en `book_id` + `viewer_key`; `catalog_generation` no se usa automáticamente como `edition_year`.

## Derechos, licencias y reutilización

El software original de LTMD se distribuye bajo **Apache License 2.0**. Los datos derivados originales sobre los cuales el licenciante posea o controle derechos necesarios se ofrecen bajo **CC BY 4.0**.

Estas licencias no se aplican a libros, PDF, JPEG, páginas, portadas, ilustraciones, texto fuente, OCR sustitutivo, marcas ni otros materiales de CONALITEG/SEP o terceros. Las fuentes necesarias se reconstruyen temporalmente, se verifican contra SHA-256 y se eliminan después del procesamiento.

## Reproducibilidad e integridad científica

El corte publicado `v0.1.0-rc.1` utiliza `LTMD_INTEGRITY_0.6`. Los artefactos U1 posteriores pertenecen a la evolución de `main` y deberán integrarse en un corte de integridad posterior; nunca se atribuyen retroactivamente al tag publicado.

## Publicación científica

LTMD separa dos productos:

1. **artículo de método/recurso digital** — [`docs/METHODS_ARTICLE_DRAFT_0_2.md`](docs/METHODS_ARTICLE_DRAFT_0_2.md);
2. **artículo histórico-educativo** — bloqueado hasta superar SEMB 0.3 y reconstruir la inferencia bajo unidades documentales defendibles.

## Documentación central

La entrada recomendada es el **[Índice maestro de método](docs/METHOD_INDEX.md)**. Para la expansión integral, consulte el **[Plan Maestro LTMD-U1](docs/LTMD_U1_MASTER_PLAN_0_1.md)**, el **[tablero vivo](data/catalog/ltmd_u1_coverage.md)** y las actas de cierre W1–W5.

## Regla epistemológica

LTMD privilegia una regla sencilla: **una cifra reproducible no es automáticamente una afirmación válida**. Cada salto —fuente, identidad documental, OCR, estructura, fragmentación, clasificación e inferencia— debe conservar evidencia suficiente para ser auditado independientemente.

## Citación

Mientras no exista un DOI versionado real, use la metadata de [`CITATION.cff`](CITATION.cff), el tag `v0.1.0-rc.1` y la GitHub Release correspondiente. Cuando Zenodo archive la release, deberá utilizarse el DOI versionado real de ese corte científico.
