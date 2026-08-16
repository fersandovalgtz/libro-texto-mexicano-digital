# LTMD-U1 W1 — cierre técnico de Ciencias Naturales / Estudio de la Naturaleza

Fecha de cierre: **2026-08-15**  
Estado: **COMPLETADA**  
Tablero de cobertura: **LTMD_U1_COVERAGE_0.4**

## Resultado ejecutivo

La primera ola del programa integral LTMD-U1 queda técnicamente cerrada.

El dominio operativo `ciencias_naturales` contiene **40 visores**. El tablero recomputado registra:

- activos completamente resueltos: **40/40**;
- FRAGSEG directamente materializado: **36/40**;
- cobertura FRAGSEG efectiva: **40/40**;
- restantes efectivos: **0**;
- estado del dominio: `completed_domain`.

Los cuatro visores que no se reprocesan directamente son aliases 2018→2019 previamente demostrados por identidad byte a byte. Se conserva su identidad de catálogo y no se duplica evidencia.

A escala U1 completa, el cierre W1 deja:

- **542/542** visores catalogados;
- **40/542 (7.38%)** activos completamente resueltos;
- **36/542 (6.64%)** con manifiesto/OCR/PAGESTRUCT/FRAGSEG directo;
- **40/542 (7.38%)** con cobertura FRAGSEG efectiva;
- **0/542** resoluciones parciales activas en el tablero;
- **0/542** cobertura semántica humana validada.

## 1966: dos objetos nuevos incorporados

Se incorporaron:

- `H1966P6CI374` — *Mi cuaderno de trabajo de Estudio de la Naturaleza*;
- `H1966P6CI375` — *Mi libro de Estudio de la Naturaleza*.

### Fuentes

La auditoría empírica de todas las posiciones declaró:

- CI374: 179 posiciones; **178 JPEG fuente + 1 terminal sintético**; cero huecos internos;
- CI375: 163 posiciones; **162 JPEG fuente + 1 terminal sintético**; cero huecos internos;
- total: **340 JPEG**, todos hasheados por SHA-256.

### OCR

- **340/340** páginas verificadas por SHA;
- **339/340** con texto detectado;
- 1 `no_text_detected`;
- **0 unresolved**.

### PAGESTRUCT

Sobre 340 páginas:

- textual: 261;
- mixed text-image: 52;
- visual: 3;
- navegación: 5;
- unknown: 19;
- elegibles para FRAGSEG: **313**.

### FRAGSEG

Los dos objetos generaron **4,618 fragmentos**:

- CI374: 2,547;
- CI375: 2,071.

Distribución total:

- `activity_candidate`: 29;
- `experiment_candidate`: 24;
- `expository_candidate`: 946;
- `instruction_candidate`: 736;
- `question_candidate`: 257;
- `short_residual_candidate`: 2,626.

## 2008: recuperación criptográfica y procesamiento completo

Los dos objetos eran:

- `H2008P3CI263` / `LTMD-CN3-G2008`;
- `H2008P4CI268` / `LTMD-CN4-G2008`.

El recurso público no servía originalmente tres posiciones internas:

- CN3 VP94;
- CN4 VP76;
- CN4 VP96.

### Recuperación estricta

Las tres posiciones se recuperaron de forma **unívoca** mediante continuidad criptográfica, no por coincidencia de título:

- CN3 VP94 → `H1993P3CI153` VP94;
- CN4 VP76 → `H1993P4CI191` VP76;
- CN4 VP96 → `H1993P4CI191` VP96.

En los tres casos:

- offset fijo: **0**;
- anchors vecinos byte-idénticos: **6**;
- discrepancias: **0**.

El manifiesto reconciliado conserva simultáneamente:

1. la URL 2008 original no servida;
2. el estado original `internal_unserved`;
3. la URL efectiva de recuperación;
4. SHA-256 y tamaño del activo recuperado;
5. visor/generación de recuperación;
6. anchors y discrepancias.

La recuperación técnica no se interpreta como identidad bibliográfica total entre ediciones.

### Manifiesto reconciliado

- CN3: **178/178 fuentes efectivas**, 1 recuperada;
- CN4: **177/177 fuentes efectivas**, 2 recuperadas;
- total: **355 JPEG efectivos**;
- unresolved efectivos: **0**.

### OCR

- **355/355** SHA verificados;
- **355/355** con texto detectado;
- `unresolved`: **0**.

### PAGESTRUCT

De 355 páginas:

- textual: 236;
- mixed text-image: 61;
- elegibles para FRAGSEG: **297**;
- el resto se conserva como visual, navegación, bibliografía/créditos o `unknown` según la lógica conservadora.

### FRAGSEG

Los dos objetos produjeron **4,367 fragmentos**:

- CN3: 1,959;
- CN4: 2,408.

Distribución total:

- `activity_candidate`: 89;
- `experiment_candidate`: 27;
- `expository_candidate`: 668;
- `instruction_candidate`: 586;
- `project_candidate`: 7;
- `question_candidate`: 779;
- `short_residual_candidate`: 2,211.

## Incremento de corpus por W1

W1 añadió:

- 1966: **4,618 fragmentos**;
- 2008: **4,367 fragmentos**;
- incremento W1: **8,985 fragmentos técnicos**.

El corpus directo acumulado pasa de **64,856** a **73,841 ocurrencias técnicas de fragmento**.

Estas ocurrencias no deben leerse como observaciones históricas independientes. Se mantienen aliases, reutilización, revisiones y procedencia documental.

## Transferencia industrial

W1 demostró dos capacidades que son necesarias para escalar al universo:

1. **ingestión directa de objetos históricos nuevos** bajo el mismo contrato SHA → OCR → PAGESTRUCT → FRAGSEG;
2. **recuperación de anomalías de fuente** sin fabricar contenido, mediante alineamiento criptográfico y procedencia reversible.

La siguiente ola activa es **U1-W2 Matemáticas**, con 64 visores. Su alcance ya está congelado y su arquitectura pública fue auditada antes de iniciar el procesamiento masivo.

## Frontera epistemológica

El cierre W1 es **técnico**, no semántico. SEMB 0.3 permanece en `WAITING_HUMAN_REFERENCE`. No se aplicará automáticamente el modelo semántico de Ciencias Naturales a Matemáticas ni a los demás dominios.
