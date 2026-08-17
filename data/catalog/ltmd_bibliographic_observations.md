# LTMD — observaciones bibliográficas reproducibles

Versión: `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.1`.

Observaciones materializadas: **4**.
Objetos con observaciones: **1** (`H2014P5FCA`).

Esta capa separa las fechas bibliográficas observadas de `catalog_generation`. No completa años ausentes por cohorte de catálogo y no importa ISBN desde fuentes secundarias.

## Observaciones

| objeto | generación catálogo | campo | valor | evidencia |
|---|---:|---|---|---|
| `H2014P5FCA` | 2014 | `first_edition_year` | `2014` | pág. 4, SHA `2289b5a4d1cde813…` |
| `H2014P5FCA` | 2014 | `reprint_statement` | `third_reprint` | pág. 4, SHA `2289b5a4d1cde813…` |
| `H2014P5FCA` | 2014 | `reprint_year` | `2017` | pág. 4, SHA `2289b5a4d1cde813…` |
| `H2014P5FCA` | 2014 | `school_cycle` | `2017-2018` | pág. 4, SHA `2289b5a4d1cde813…` |

## Contrato

- Cada valor debe tener una página fuente identificada y una huella criptográfica concordante con el manifiesto canónico.
- `catalog_generation` es contexto de navegación/cohorte, no fuente del valor bibliográfico.
- `human_validated=0` indica que la extracción procede de OCR técnico; no invalida la procedencia de la página, pero conserva separada la futura validación humana de la transcripción.
- La expansión a otros objetos debe añadir reglas reproducibles específicas y nunca rellenar valores desconocidos por cercanía temporal.

Véase `docs/LTMD_CATALOG_GENERATION_SEMANTICS_0_1.md`.
