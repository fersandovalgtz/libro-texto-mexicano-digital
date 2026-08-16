# Roadmap — LTMD

Estado vigente: **programa LTMD-U1 (542 visores)**.  
Primera release metodológica publicada: **v0.1.0-rc.1**.  
Gate semántico: **SEMB 0.3 — WAITING_HUMAN_REFERENCE**.

> El objetivo estratégico vigente es cubrir técnicamente el universo U1 completo. El progreso técnico del corpus y la validación semántica son carriles distintos.

## Fase 0 — constitución y piloto técnico — COMPLETADA

- [x] Repositorio, identidad y gobernanza.
- [x] Piloto Ciencias Naturales 5º.
- [x] Procedencia, manifiestos y SHA-256.
- [x] OCR técnico, PAGESTRUCT y FRAGSEG.
- [x] 9,594 fragmentos piloto.
- [x] Rule A y diagnóstico SEMB 0.2.
- [x] SEMB 0.3 preregistrado antes de referencia humana.

## Fase 1 — expansión de Ciencias Naturales y prueba industrial — COMPLETADA

- [x] CN4/CN6: 19,067 fragmentos.
- [x] Ola 2: 36,195 fragmentos.
- [x] Dependencia CN4 1972↔1988.
- [x] Dos objetos CN6 bajo generación 1993.
- [x] Aliases 2018→2019: 652/652 pares byte-idénticos.
- [x] Release metodológica `v0.1.0-rc.1`.

## Fase 2 — censo U1 y tablero maestro — COMPLETADA

- [x] U1 = **542 visores**.
- [x] 542/542 títulos recuperados.
- [x] 191 familias de título normalizadas.
- [x] Taxonomía operacional y colas W1–W11.
- [x] Tablero por etapas y por dominio.
- [x] Separación entre FRAGSEG directo y cobertura efectiva por alias.

## Fase 3 — U1-W1: Ciencias Naturales / Estudio de la Naturaleza — COMPLETADA

Meta: **40/40 cobertura efectiva**.  
Resultado: **40/40**.

### 1966

- [x] `H1966P6CI374` — *Mi cuaderno de trabajo de Estudio de la Naturaleza*.
- [x] `H1966P6CI375` — *Mi libro de Estudio de la Naturaleza*.
- [x] 340 JPEG fuente hasheados; cero huecos internos.
- [x] OCR 340/340 SHA; 0 unresolved.
- [x] PAGESTRUCT: 313 páginas elegibles.
- [x] FRAGSEG: **4,618 fragmentos**.

### 2008

- [x] `H2008P3CI263` / `LTMD-CN3-G2008`.
- [x] `H2008P4CI268` / `LTMD-CN4-G2008`.
- [x] Recuperar criptográficamente las tres posiciones internas no servidas.
- [x] Tres recuperaciones unívocas, cada una con 6 anchors byte-idénticos, offset 0 y 0 discrepancias.
- [x] Manifiesto reconciliado preservando URL/estado original y fuente efectiva.
- [x] 355/355 fuentes efectivas; 0 unresolved.
- [x] OCR 355/355 SHA; 0 unresolved.
- [x] PAGESTRUCT: 297 páginas elegibles.
- [x] FRAGSEG: **4,367 fragmentos**.

### Cierre W1

- [x] Incremento W1: **8,985 fragmentos**.
- [x] Corpus directo acumulado: **73,841 ocurrencias técnicas**.
- [x] Ciencias Naturales: **40/40 cobertura efectiva**.
- [x] Documento de cierre: `LTMD_U1_W1_COMPLETION_2026-08-15.md`.

## Fase 4 — U1-W2: Matemáticas — ACTIVA

Universo congelado: **64 visores**.  
Posiciones declaradas: **13,656**.  
Estado de fuente actual: **60/64 identidades efectivamente resueltas; 57 contenidos canónicos de cómputo; 4 excepciones DMA 2018**.

### Censo, arquitectura y activos — COMPLETADOS

- [x] Congelar `data/catalog/ltmd_u1_w2_scope.csv` con 64/64 visores.
- [x] Probar arquitectura de los 64 visores sin descargar páginas.
- [x] 64/64 HTML 200; 64/64 `x.js`; 64/64 señal `ag_pages`; **64/64 arquitectura dinámica estándar**.
- [x] Cuantificar `claves.json`: **13,656 posiciones declaradas**.
- [x] Auditar empíricamente las 13,656 posiciones por 64 shards con SHA-256.
- [x] Resultado crudo: 59 `direct_asset_ready`, 1 libro 2008 con dos huecos internos y 4 DMA 2018 con ruta no servida.
- [x] Recuperar unívocamente los dos huecos de `H2008P4MA276` mediante anchors byte-idénticos, offset fijo y cero discrepancias.
- [x] Construir manifiesto reconciliado que conserva anomalía original + fuente efectiva.
- [x] Alcanzar **60/64** de resolución efectiva de activos.
- [x] Mantener sin imputar `H2018P3DMA`, `H2018P4DMA`, `H2018P5DMA`, `H2018P6DMA`.
- [x] Auditar configuración DMA 2018↔2019: mismo `ag_pages`, distinto `ag_clave`; evidencia insuficiente para promover alias.

### Dependencia documental y deduplicación — COMPLETADAS

- [x] Detectar tres aliases byte-idénticos completos:
  - `H1982P4MA388` → `H1972P4MA083`, 258 JPEG;
  - `H1982P5MA394` → `H1972P5MA089`, 304 JPEG;
  - `H1982P6MA399` → `H1972P6MA094`, 194 JPEG.
- [x] Conservar las identidades de catálogo separadas.
- [x] Reducir la unidad de cómputo de 60 identidades resueltas a **57 contenidos canónicos**.
- [x] Registrar relaciones documentales y recuperaciones de página en `data/catalog/ltmd_u1_w2_math_document_relationships.csv`.

### Pipeline técnico 0.2 — EN EJECUCIÓN

- [x] Versionar OCR/PAGESTRUCT/FRAGSEG como 0.2 para reflejar la topología empírica 57 canónicos + 3 aliases + 4 excepciones.
- [x] Gate OCR: sólo 57 canónicos; descarga desde campos `effective_*`; SHA y byte-size obligatorios.
- [x] Preparar PAGESTRUCT 0.2 con las mismas reglas estructurales congeladas.
- [x] Preparar FRAGSEG 0.2 con las mismas reglas de segmentación congeladas.
- [ ] Completar OCR técnico 0.2 de los 57 contenidos canónicos.
- [ ] Completar PAGESTRUCT 0.2.
- [ ] Completar FRAGSEG 0.2.
- [ ] Promover los tres aliases a cobertura FRAGSEG efectiva sólo cuando su canónico esté materializado.
- [ ] Cerrar W2 en **60/64 cobertura técnica efectiva** mientras persistan las cuatro excepciones 2018.

### Tablero U1

- [x] `LTMD_U1_COVERAGE_0.5`: **100/542 activos completamente resueltos (18.45%)** y **96/542 manifiestos de fuente listos (17.71%)**.
- [ ] Promover OCR/PAGESTRUCT/FRAGSEG W2 únicamente después de sus artefactos finales.

Documento de estado: `LTMD_U1_W2_MATHEMATICS_STATUS_0_1.md`.

W2 es la primera prueba de transferencia masiva del **pipeline universal** a una disciplina distinta. No se aplica semántica de Ciencias Naturales a Matemáticas.

## Fase 5 — U1-W3: Español/Lengua — PENDIENTE

Universo operacional: **130 visores**. Será el primer gran estrés de escala después de Matemáticas y debe ejecutarse por cohortes reproducibles.

## Fase 6 — U1-W4 a U1-W9 — PENDIENTE

- [ ] W4 Ciencias Sociales — 14 visores.
- [ ] W5 Historia — 18 visores.
- [ ] W6 Geografía/Atlas — 42 visores.
- [ ] W7 Cívica/Ética — 30 visores.
- [ ] W8 Artes — 20 visores.
- [ ] W9 Educación Física — 4 visores.

## Fase 7 — U1-W10: integrados/multiarea — PENDIENTE

- [ ] 69 visores.
- [ ] Conservar asignación operacional sin confundirla con ontología curricular.

## Fase 8 — U1-W11: otros / revisión operacional — PENDIENTE

- [ ] 111 visores.
- [ ] Revisar títulos sin señal disciplinar fuerte.
- [ ] Crear subfamilias sólo con reglas documentadas.
- [ ] No inferir contenido a partir de claves opacas.

## Fase 9 — cierre técnico U1 — PENDIENTE

- [ ] **542/542 `effective_fragseg_coverage` o excepción técnica final explícita bajo criterio U1**.
- [ ] 542/542 identidades documentales preservadas.
- [ ] Aliases no duplicados como evidencia independiente.
- [ ] Resolución/limitación de activos documentada por visor.
- [ ] Tablero y matriz regenerados sobre corte final.
- [ ] Nuevo manifiesto de integridad.
- [ ] Nueva release científica versionada.

El cierre técnico U1 no exige que los 542 objetos compartan un único clasificador semántico.

## Fase semántica paralela — BLOQUEADA POR REFERENCIA HUMANA

SEMB 0.3 del piloto permanece en `WAITING_HUMAN_REFERENCE`.

- [x] muestra 480 preparada;
- [x] 320 development / 160 locked validation;
- [x] 120 doble codificación de fiabilidad;
- [x] criterios y arquitecturas congelados;
- [x] model lock irreversible preparado;
- [ ] anotación humana genuina;
- [ ] fiabilidad interanotador;
- [ ] consenso/adjudicación;
- [ ] desarrollo preregistrado;
- [ ] model lock;
- [ ] apertura única de locked validation;
- [ ] producción sólo si supera criterios.

**No se fabrican etiquetas humanas, no se abre locked validation antes del lock y no se ajusta el modelo para producir una dirección histórica deseada.**

## Horizonte U2 — NO ABIERTO TODAVÍA

U2 comprenderá materiales relevantes fuera del snapshot U1 sólo después de definir y versionar explícitamente su denominador. No se mezcla retroactivamente con el 542 de U1.

## Regla documental

GitHub es la fuente reproducible del método, corpus derivado y estado de cobertura. Todo cambio material de definición, denominador, taxonomía operacional o criterio de cobertura debe versionarse. Las releases publicadas no se reescriben retroactivamente.
