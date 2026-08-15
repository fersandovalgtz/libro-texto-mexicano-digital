# Diagnóstico de incertidumbre SEMB 0.2

Versión: `SEMB02_UNCERTAINTY_DIAG_0.1`. Este diagnóstico usa únicamente metadatos y puntuaciones ya persistidas; no accede al texto OCR ni modifica umbrales.

## Resultado ejecutivo

- Fragmentos totales: **9594**.
- Incertidumbre global persistida: **9545 (99.49%)**.
- Fragmentos excluidos de clasificación por `heading_candidate` o longitud <4 tokens: **4557 (47.50%)**.
- Fragmentos elegibles no omitidos: **5037**.
- En elegibles, la regla del gate de acción bloquea **4491 (89.16%)**: margen <0 o dentro del buffer [0, 0.02).
- Tras superar el gate+buffer, el margen entre las dos mejores acciones bloquea **387 (7.68%)** adicional.
- La regla de margen de posición (<0.01) bloquea **3769 (74.83%)** de los elegibles.
- Sólo **49 (0.97%)** de los elegibles satisfacen simultáneamente las reglas de certeza de acción y posición.

## Distribuciones centrales en fragmentos elegibles

- `action_gate_margin_B`: mediana **0.0019**, p75 **0.0114**, p90 **0.0206**. Umbral de certeza práctica vigente: **0.0200**.
- `action_margin_B`: mediana **0.0054**, p75 **0.0106**, p90 **0.0176**. Umbral: **0.0100**.
- `position_margin_B`: mediana **0.0053**, p75 **0.0100**, p90 **0.0161**. Umbral: **0.0100**.

## Lectura metodológica

La capa SEMB 0.2 no debe recalibrarse observando qué umbral produce la narrativa histórica más atractiva. Los archivos por generación, tipo de fragmento, longitud y cuantiles permiten localizar el mecanismo de incertidumbre sin usar los contrastes históricos como función objetivo. Si se desarrolla SEMB 0.3, sus parámetros deben fijarse con evidencia independiente del corpus histórico (validación sintética ampliada y, preferentemente, una muestra humana estratificada y ciega a la generación), bloquearse y sólo después aplicarse al corpus congelado.

## Archivos asociados

- `semb02_uncertainty_diagnostic.csv`: resumen total y por generación.
- `semb02_uncertainty_by_candidate_type.csv`: diagnóstico por tipo FRAGSEG.
- `semb02_uncertainty_by_token_bin.csv`: diagnóstico por longitud.
- `semb02_uncertainty_quantiles.csv`: cuantiles de gate, márgenes y longitud.
