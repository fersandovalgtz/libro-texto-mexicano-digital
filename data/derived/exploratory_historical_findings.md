# LTMD — hallazgos exploratorios computacionales 0.1

Esta capa es **exploratoria/post hoc** respecto de los resultados históricos ya calculados. No modifica las tablas preregistradas. El ranking usa únicamente |Δ pp| del consenso A∩B y publica además los CSV completos.

- Hallazgos directionally robust totales: **21**.
- Hallazgos con dirección method-sensitive A/B: **14**.

## 1972 → 1988

Robustos: 4; method-sensitive: 2.

### Diez robustos de mayor magnitud
- `action_family / reasoning`: consenso 20.000% → 0.000% (-20.00 pp; decrease); ΔA=-26.67 pp; ΔB=-10.48 pp.
- `action / compare`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-6.67 pp; ΔB=-6.67 pp.
- `position / reasoner`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-26.67 pp; ΔB=-5.71 pp.
- `position_family / inquiry_reasoning`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-26.67 pp; ΔB=-21.90 pp.

### Direcciones method-sensitive
- `action / explain`: ΔA=-13.33 pp (decrease), ΔB=+0.95 pp (increase).
- `action / solve`: ΔA=-6.67 pp (decrease), ΔB=+8.57 pp (increase).

## 1988 → 1993

Robustos: 5; method-sensitive: 4.

### Diez robustos de mayor magnitud
- `action / create`: consenso 0.000% → 6.667% (+6.67 pp; increase); ΔA=+6.67 pp; ΔB=+12.38 pp.
- `action / observe`: consenso 0.000% → 6.667% (+6.67 pp; increase); ΔA=+6.67 pp; ΔB=+20.00 pp.
- `action / solve`: consenso 0.000% → 6.667% (+6.67 pp; increase); ΔA=+6.67 pp; ΔB=+4.76 pp.
- `action_family / reasoning`: consenso 0.000% → 6.667% (+6.67 pp; increase); ΔA=+6.67 pp; ΔB=+17.14 pp.
- `position / observer`: consenso 0.000% → 6.667% (+6.67 pp; increase); ΔA=+6.67 pp; ΔB=+13.33 pp.

### Direcciones method-sensitive
- `action_family / observation_measurement`: ΔA=+6.67 pp (increase), ΔB=-8.57 pp (decrease).
- `action_family / production_interaction`: ΔA=+6.67 pp (increase), ΔB=-1.90 pp (decrease).
- `position / reasoner`: ΔA=+6.67 pp (increase), ΔB=-14.29 pp (decrease).
- `position_family / inquiry_reasoning`: ΔA=+13.33 pp (increase), ΔB=-4.76 pp (decrease).

## 1993 → 2014

Robustos: 5; method-sensitive: 5.

### Diez robustos de mayor magnitud
- `action / create`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-6.67 pp; ΔB=-26.67 pp.
- `action / solve`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-6.67 pp; ΔB=-16.67 pp.
- `action_family / production_interaction`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-6.67 pp; ΔB=-26.67 pp.
- `action_family / observation_measurement`: consenso 6.667% → 8.333% (+1.67 pp; increase); ΔA=+10.00 pp; ΔB=+13.33 pp.
- `position / observer`: consenso 6.667% → 8.333% (+1.67 pp; increase); ΔA=+10.00 pp; ΔB=+3.33 pp.

### Direcciones method-sensitive
- `action / explain`: ΔA=+8.33 pp (increase), ΔB=-16.67 pp (decrease).
- `action / observe`: ΔA=+10.00 pp (increase), ΔB=-11.67 pp (decrease).
- `action_family / reasoning`: ΔA=+1.67 pp (increase), ΔB=-26.67 pp (decrease).
- `position / receiver`: ΔA=-31.67 pp (decrease), ΔB=+10.00 pp (increase).
- `position_family / reception_execution`: ΔA=-28.33 pp (decrease), ΔB=+11.67 pp (increase).

## 1972 → 2014

Robustos: 7; method-sensitive: 3.

### Diez robustos de mayor magnitud
- `action_family / reasoning`: consenso 20.000% → 8.333% (-11.67 pp; decrease); ΔA=-18.33 pp; ΔB=-20.00 pp.
- `position / observer`: consenso 0.000% → 8.333% (+8.33 pp; increase); ΔA=+16.67 pp; ΔB=+10.00 pp.
- `position / receiver`: consenso 0.000% → 8.333% (+8.33 pp; increase); ΔA=+1.67 pp; ΔB=+16.67 pp.
- `position_family / reception_execution`: consenso 0.000% → 8.333% (+8.33 pp; increase); ΔA=+18.33 pp; ΔB=+11.67 pp.
- `action / compare`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-6.67 pp; ΔB=-6.67 pp.
- `action / solve`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-6.67 pp; ΔB=-3.33 pp.
- `position / reasoner`: consenso 6.667% → 0.000% (-6.67 pp; decrease); ΔA=-18.33 pp; ΔB=-20.00 pp.

### Direcciones method-sensitive
- `action / explain`: ΔA=-5.00 pp (decrease), ΔB=+3.33 pp (increase).
- `action / observe`: ΔA=+16.67 pp (increase), ΔB=-11.67 pp (decrease).
- `position / instruction_follower`: ΔA=+16.67 pp (increase), ΔB=-5.00 pp (decrease).

## Regla de lectura

Los robustos pueden convertirse en hipótesis historiográficas, pero la magnitud/ranking es exploratoria. Las categorías method-sensitive no sostienen por sí solas una afirmación histórica principal. Para estabilidad de positivos debe consultarse `exploratory_category_stability.csv`, especialmente `positive_jaccard`, no sólo el acuerdo binario dominado por ceros.

Versión: `EXPLORE_FINDINGS_0.1`.
