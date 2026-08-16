# Roadmap — LTMD

Estado vigente: **programa LTMD-U1 (542 visores)**.  
Primera release metodológica publicada: **v0.1.0-rc.1**.  
Gate semántico: **SEMB 0.3 — WAITING_HUMAN_REFERENCE**.

> Este roadmap sustituye estados antiguos del piloto que ya fueron superados. El historial permanece en Git. El objetivo actual no es decidir si LTMD debe escalar: **la decisión estratégica es escalar hasta cubrir técnicamente el universo U1 completo**.

## Fase 0 — constitución y piloto técnico — COMPLETADA

- [x] Crear repositorio independiente, esquema de identidad y gobernanza.
- [x] Seleccionar Ciencias Naturales 5º como piloto inicial.
- [x] Reconstruir arquitectura de visores y procedencia.
- [x] Construir manifiestos y hashes de fuente.
- [x] Ejecutar OCR técnico sin publicar OCR íntegro sustitutivo.
- [x] Construir PAGESTRUCT y FRAGSEG.
- [x] Materializar 9,594 fragmentos del piloto.
- [x] Ejecutar Rule A como especificación transparente.
- [x] Rechazar SEMB 0.1 antes del corpus.
- [x] Ejecutar y diagnosticar SEMB 0.2; conservarlo como resultado negativo/exploratorio.
- [x] Preregistrar SEMB 0.3 antes de referencia humana.

## Fase 1 — expansión de Ciencias Naturales y prueba industrial — COMPLETADA EN SU NÚCLEO

- [x] Expandir a CN4/CN6: 19,067 fragmentos.
- [x] Ejecutar Ola 2: 36,195 fragmentos.
- [x] Alcanzar 64,856 ocurrencias técnicas acumuladas.
- [x] Detectar y modelar reutilización CN4 1972↔1988.
- [x] Conservar dos objetos CN6 dentro de generación 1993.
- [x] Demostrar aliases 2018→2019 con 652/652 pares byte-idénticos.
- [x] Documentar dos objetos CN 2008 con posiciones internas no servidas.
- [x] Construir vistas `object`, `unique-content` y `revision`.
- [x] Publicar release metodológica `v0.1.0-rc.1`.

## Fase 2 — censo U1 y tablero maestro — COMPLETADA

- [x] Congelar U1 = **542 visores** del snapshot vigente del Catálogo Histórico.
- [x] Recuperar 542/542 títulos.
- [x] Normalizar 542/542 títulos en **191 familias**.
- [x] Construir `LTMD_U1_COVERAGE_0.2`.
- [x] Crear matriz por visor y KPIs por etapa.
- [x] Crear taxonomía operativa de dominios.
- [x] Crear cola completa de olas W1–W11.
- [x] Separar FRAGSEG directo de cobertura efectiva por alias.
- [x] Fijar línea base: 32/542 FRAGSEG directo; 36/542 cobertura efectiva; 0/542 semántica validada.

Archivos rectores:

- `LTMD_U1_MASTER_PLAN_0_1.md`
- `../data/catalog/ltmd_u1_coverage.md`
- `../data/catalog/ltmd_u1_coverage.csv`
- `../data/catalog/ltmd_u1_domain_summary.csv`
- `../data/catalog/ltmd_u1_wave_queue.csv`

## Fase 3 — U1-W1: cerrar Ciencias Naturales/Estudio de la Naturaleza — ACTIVA

Meta operacional del dominio: **40/40 cobertura efectiva**.

Línea base: **36/40**.

Objetos pendientes congelados:

- [ ] `H1966P6CI374` — *Mi cuaderno de trabajo de Estudio de la Naturaleza*.
- [ ] `H1966P6CI375` — *Mi libro de Estudio de la Naturaleza*.
- [ ] `H2008P3CI263` — *Ciencias Naturales*, 3º; resolver/documentar excepción de activo.
- [ ] `H2008P4CI268` — *Ciencias Naturales*, 4º; resolver/documentar excepción de activos.

Para 1966: `asset audit → page manifest → OCR → PAGESTRUCT → FRAGSEG → dependencia`.

Para 2008: no inventar activos. Buscar ruta/representación alternativa o conservar una excepción documental explícita. No contar como cobertura completa mientras el criterio de U1 no esté satisfecho.

## Fase 4 — U1-W2: Matemáticas — PENDIENTE

Universo operacional actual: **64 visores**.

Objetivos:

- [ ] congelar lista W2 desde `ltmd_u1_wave_queue.csv`;
- [ ] auditar arquitectura/rutas de activos por generación;
- [ ] ejecutar manifiestos SHA-256 por objeto;
- [ ] ejecutar OCR técnico por shards;
- [ ] evaluar transferibilidad de PAGESTRUCT/FRAGSEG estructural;
- [ ] no aplicar semántica de Ciencias Naturales a Matemáticas;
- [ ] actualizar tablero automáticamente.

W2 es la primera prueba de transferencia masiva del pipeline universal a una disciplina distinta.

## Fase 5 — U1-W3: Español/Lengua — PENDIENTE

Universo operacional actual: **130 visores**.

Será el primer gran estrés de escala del sistema. Debe ejecutarse por cohortes reproducibles, no como job monolítico.

## Fase 6 — U1-W4 a U1-W9 — PENDIENTE

- [ ] W4 Ciencias Sociales — 14 visores.
- [ ] W5 Historia — 18 visores.
- [ ] W6 Geografía/Atlas — 42 visores.
- [ ] W7 Cívica/Ética — 30 visores.
- [ ] W8 Artes — 20 visores.
- [ ] W9 Educación Física — 4 visores.

El orden es operacional y puede versionarse si aparece evidencia técnica que aconseje otro orden. Nunca se cambia para maximizar un resultado historiográfico.

## Fase 7 — U1-W10: materiales integrados/multiarea — PENDIENTE

Universo operacional actual: **69 visores**.

Estos objetos requieren atención adicional porque el título activa más de una señal disciplinar. Su asignación a W10 es logística; no presupone una ontología curricular.

## Fase 8 — U1-W11: otros y revisión de clasificación operacional — PENDIENTE

Universo actual: **111 visores**.

- [ ] revisar títulos sin señal disciplinar fuerte;
- [ ] crear subfamilias sólo con reglas documentadas;
- [ ] no inferir contenido a partir de claves opacas;
- [ ] completar pipeline técnico de todos los objetos restantes.

## Fase 9 — cierre técnico U1 — PENDIENTE

Criterio principal:

- [ ] **542/542 `effective_fragseg_coverage` o excepción técnica final explícitamente gobernada por el criterio U1**;
- [ ] 542/542 identidades documentales preservadas;
- [ ] aliases no duplicados como evidencia independiente;
- [ ] resolución/limitación de activos documentada por visor;
- [ ] tablero y matriz regenerados sobre el corte final;
- [ ] nuevo manifiesto de integridad;
- [ ] nueva release científica versionada.

El cierre técnico U1 no exige que 542 libros compartan un único clasificador semántico.

## Fase semántica paralela — BLOQUEADA POR REFERENCIA HUMANA

SEMB 0.3 del piloto permanece en `WAITING_HUMAN_REFERENCE`.

- [x] muestra 480 preparada;
- [x] 320 development / 160 locked validation;
- [x] 120 doble codificación de fiabilidad;
- [x] criterios de aceptación congelados;
- [x] arquitecturas candidatas congeladas;
- [x] model lock irreversible preparado;
- [ ] anotación humana genuina;
- [ ] fiabilidad interanotador;
- [ ] consenso/adjudicación;
- [ ] desarrollo dentro del espacio preregistrado;
- [ ] model lock;
- [ ] apertura única de locked validation;
- [ ] aplicación productiva sólo si supera criterios.

**No se fabrican etiquetas humanas, no se abre locked validation antes del lock y no se ajusta el modelo para producir una dirección histórica deseada.**

Los demás dominios U1 requerirán validación semántica específica cuando sus preguntas analíticas lo exijan. La capa técnica universal puede avanzar independientemente.

## Horizonte U2 — NO ABIERTO TODAVÍA

U2 comprenderá materiales relevantes fuera del snapshot U1 —otras colecciones, variantes, materiales indígenas, cuadernos, libros del maestro, antecedentes u otros repositorios— sólo después de que su alcance se defina y versione explícitamente.

U2 no se mezcla retroactivamente con el denominador 542 de U1.

## Regla documental

GitHub es la fuente reproducible del método, corpus derivado y estado de cobertura. Todo cambio material de definición, denominador, taxonomía operacional o criterio de cobertura debe versionarse. Las releases publicadas no se reescriben retroactivamente.
