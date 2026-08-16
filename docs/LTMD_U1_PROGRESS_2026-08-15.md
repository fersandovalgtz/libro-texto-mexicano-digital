# LTMD-U1 — corte de avance del 15 de agosto de 2026

Este documento actualiza operativamente `LTMD_U1_MASTER_PLAN_0_1` sin reescribir su línea base histórica.

## Estado U1

- Universo congelado: **542 visores**.
- Familias normalizadas de título: **191**.
- FRAGSEG materializado directamente: **36/542**.
- Cobertura técnica efectiva: **40/542**.
- Cobertura semántica humana validada: **0/542**; SEMB03 permanece en `WAITING_HUMAN_REFERENCE`.

## U1-W1 — Ciencias Naturales

**Estado: cerrado técnicamente.**

Los 40 visores del dominio operativo `ciencias_naturales` tienen cobertura técnica efectiva. Los dos objetos de 1966 fueron auditados desde activos fuente y procesados hasta FRAGSEG. Los dos objetos 2008 con huecos internos documentados fueron reconciliados mediante continuidad criptográfica estricta; las tres posiciones recuperadas conservan trazabilidad hacia la anomalía y hacia la fuente efectiva. No se inventaron páginas ni se asumió identidad bibliográfica total entre ediciones.

Resultados W1 añadidos:

- 1966: **340 JPEG fuente**, 0 huecos internos; **4,618 fragmentos** en **313** páginas elegibles.
- 2008 reconciliado: **355/355 posiciones** con SHA-256, 0 unresolved; **4,367 fragmentos** en **297/297** páginas elegibles.

El tablero U1 vigente después de W1 registra **36/542 FRAGSEG directos** y **40/542 efectivos**.

## U1-W2 — Matemáticas

**Estado: expansión técnica activa.**

Scope congelado:

- **64 visores**;
- **13,656 posiciones declaradas**;
- arquitectura de visor estándar confirmada en los 64 objetos.

La cadena no semántica quedó instrumentada como:

`asset audit SHA-256 → OCR temporal verificado → PAGESTRUCT congelado → FRAGSEG → publicación de derivados técnicos`

### Gates

1. El auditor de activos procesa cada posición declarada y distingue `source_jpeg`, `terminal_synthetic_candidate`, `internal_unserved` y `probe_error`.
2. OCR sólo puede abrirse si el consolidado contiene exactamente 64 visores, todos `direct_asset_ready`, con cero `internal_unserved` y cero `probe_errors`.
3. PAGESTRUCT sólo puede abrirse tras OCR de 64/64 visores, con todas las páginas SHA-verificadas y cero `unresolved`.
4. FRAGSEG sólo procesa páginas `textual` o `mixed_text_image` y conserva huecos legítimos de secuencia sin renumerar IDs.
5. Ningún workflow W2 llama a SEMB03 ni promueve `semantic_ready`.

### Infraestructura W2

- `scripts/audit_ltmd_u1_w2_math_assets_book.py`
- `scripts/combine_ltmd_u1_w2_math_asset_shards.py`
- `scripts/ocr_ltmd_u1_w2_math_book.py`
- `scripts/combine_ltmd_u1_w2_math_ocr.py`
- `scripts/extract_ltmd_u1_w2_math_structural_flags_book.py`
- `scripts/combine_ltmd_u1_w2_math_structural_flags.py`
- `scripts/classify_ltmd_u1_w2_math_page_structure.py`
- `scripts/segment_ltmd_u1_w2_math_fragments.py`
- `scripts/combine_ltmd_u1_w2_math_fragment_shards.py`

Workflows:

- `.github/workflows/audit-ltmd-u1-w2-math-assets.yml`
- `.github/workflows/build-ltmd-u1-w2-math-ocr.yml`
- `.github/workflows/build-ltmd-u1-w2-math-pagestruct.yml`
- `.github/workflows/build-ltmd-u1-w2-math-fragseg.yml`
- `.github/workflows/test-ltmd-u1-w2-math-infrastructure.yml`

El self-test compila la infraestructura Python, verifica la invariante **64 visores / 13,656 posiciones** y comprueba que la frontera semántica permanezca cerrada.

## Regla de avance

No se acreditará W2 en el tablero maestro por jobs parciales. Cada etapa recibe crédito únicamente cuando su artefacto consolidado final existe y satisface sus invariantes. Si el asset audit detecta huecos internos, W2 pasa primero por una fase de recuperación/excepción documentada antes de OCR.
