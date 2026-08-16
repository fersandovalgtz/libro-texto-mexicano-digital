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
- [x] Tablero `LTMD_U1_COVERAGE_0.4`: 40/542 activos full; 36/542 FRAGSEG directo; 40/542 cobertura efectiva; 0 parciales; 0 semántica validada.
- [x] Documento de cierre: `LTMD_U1_W1_COMPLETION_2026-08-15.md`.

## Fase 4 — U1-W2: Matemáticas — ACTIVA

Universo congelado: **64 visores**.

- [x] Congelar `data/catalog/ltmd_u1_w2_scope.csv` con 64/64 visores.
- [x] Probar arquitectura de los 64 visores sin descargar páginas.
- [x] 64/64 HTML 200; 64/64 `x.js`; 64/64 señal `ag_pages`; **64/64 arquitectura dinámica estándar**.
- [x] Cuantificar `claves.json`: **13,656 posiciones declaradas**.
- [ ] Auditar empíricamente los 13,656 activos por 64 shards con SHA-256.
- [ ] Resolver aliases/huecos internos que emerjan del asset audit.
- [ ] Congelar manifiesto fuente de W2.
- [ ] Ejecutar OCR técnico por shards.
- [ ] Verificar transferencia estructural PAGESTRUCT/FRAGSEG a Matemáticas.
- [ ] Ejecutar FRAGSEG técnico.
- [ ] Actualizar tablero U1 con la cobertura efectiva de W2.

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
