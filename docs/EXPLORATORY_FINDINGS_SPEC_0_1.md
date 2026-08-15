# Hallazgos exploratorios — especificación 0.1

Fecha: 2026-08-15

## Naturaleza

Esta especificación se crea **después** de que existen los derivados de `HISTORICAL_COMPARISON_SPEC_0_1.md`. Por tanto, no es preregistro confirmatorio. Su función es ordenar transparentemente los resultados existentes para lectura historiográfica y generación de hipótesis, sin alterar los cálculos preregistrados.

## Entradas

- `historical_transitions.csv`;
- `historical_action_prevalence.csv`;
- `historical_position_prevalence.csv`;
- `historical_family_prevalence.csv`;
- `classifier_AB_category_agreement.csv`;
- `classifier_AB_agreement_summary.csv`.

No se lee texto fuente ni fragmentos OCR.

## Salidas

1. `exploratory_robust_transitions.csv`: **todas** las combinaciones categoría/familia/transición con `directionally_robust=1`, una fila por consenso, acompañadas de los deltas A y B correspondientes.
2. `exploratory_method_sensitive_transitions.csv`: todas las combinaciones con `method_sensitive_direction=1`.
3. `exploratory_category_stability.csv`: acuerdo positivo A/B y diferencia de prevalencias por categoría y generación.
4. `exploratory_historical_findings.md`: inventario transparente, no una selección confirmatoria.

## Ranking

Para facilitar lectura, dentro de cada transición se ordenan los hallazgos robustos por:

1. valor absoluto de `difference_pp` del consenso, descendente;
2. dominio (`action`, `position`, `action_family`, `position_family`);
3. nombre de categoría alfabéticamente.

El informe muestra los primeros 10 por transición **pero también publica el CSV completo de todos los robustos**. Por tanto, el top-10 no elimina resultados ni se utiliza como prueba de significancia.

## Hallazgos method-sensitive

Se listan completos, sin ranking favorable. Una dirección A/B opuesta no se convierte en conclusión histórica; se marca explícitamente como sensibilidad metodológica.

## Acuerdo categorial

`exploratory_category_stability.csv` conserva por categoría/generación:

- prevalencia A;
- prevalencia B;
- diferencia absoluta de prevalencias;
- binary agreement;
- positive Jaccard;
- n11/n10/n01/n00.

Para evitar que el alto acuerdo en ceros oculte discrepancias de positivos, el informe prioriza `positive_jaccard` sobre `binary_agreement` al discutir estabilidad sustantiva.

## Uso

Los resultados de esta capa pueden sugerir:

- hipótesis historiográficas;
- categorías que requieren cautela;
- posibles argumentos para artículo;
- análisis de contexto curricular que conviene contrastar.

No cambian RULEA, SEMB, A/B agreement ni los derivados históricos preregistrados.
