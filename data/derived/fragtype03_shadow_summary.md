# FRAGTYPE 0.3 — re-tipificación shadow

Versión: `FRAGTYPE_0.3_SHADOW`. Esta capa no modifica ningún límite de fragmento, ID ni hash.

`heading_candidate` se interpreta como categoría residual de longitud y se renombra `short_residual_candidate`. La elegibilidad semántica se separa de esa etiqueta: cualquier fragmento de ≥4 tokens es elegible para futura validación, sin afirmar que deba ser clasificado correctamente por SEMB 0.2.

## Impacto potencial de cobertura
- 1972: elegibles SEMB 0.2=1797; elegibles shadow=2305; +508 unidades breves recuperables; residual total=856.
- 1988: elegibles SEMB 0.2=973; elegibles shadow=1284; +311 unidades breves recuperables; residual total=569.
- 1993: elegibles SEMB 0.2=1257; elegibles shadow=1977; +720 unidades breves recuperables; residual total=1176.
- 2014: elegibles SEMB 0.2=1010; elegibles shadow=1863; +853 unidades breves recuperables; residual total=1536.

**Total:** elegibilidad pasa de **5037** a **7429** fragmentos (+2392, 47.5% respecto al universo anterior).

## Restricción
Esta capa sólo demuestra que la exclusión anterior dependía de una etiqueta residual mal nombrada. La inclusión de estas unidades en SEMB 0.3 requerirá validación humana suplementaria; no se incorporan retroactivamente a los resultados históricos SEMB 0.2.
