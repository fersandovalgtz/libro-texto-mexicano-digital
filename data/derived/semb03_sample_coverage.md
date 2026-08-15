# Cobertura de la muestra humana SEMB 0.3

Versión: `SEMB03_SAMPLE_COVERAGE_0.1`. Universo elegible FRAGSEG: **5037** fragmentos; muestra: **480**; desarrollo: 320; validación bloqueada: 160.

La muestra es deliberadamente estratificada y no es una muestra autoponderada del corpus. Por ello se publican pesos de postestratificación `N_h/n_h` por generación × tipo de candidato. Las métricas primarias preregistradas permanecen sin ponderar para respetar el diseño de validación; las métricas ponderadas podrán reportarse como análisis de transportabilidad al corpus.

## Distribución por tipo
- `activity_candidate`: población=190, muestra=39, locked=14.
- `experiment_candidate`: población=111, muestra=40, locked=16.
- `expository_candidate`: población=1504, muestra=128, locked=40.
- `instruction_candidate`: población=1350, muestra=131, locked=39.
- `project_candidate`: población=34, muestra=6, locked=1.
- `question_candidate`: población=1848, muestra=136, locked=50.

## Estratos pequeños en validación bloqueada
Se detectan **6** combinaciones generación × tipo con población >0 y menos de 5 casos locked. Esto no invalida la validación global, pero limita inferencias finas por estrato.
- 1972 `activity_candidate`: población=19, locked=2.
- 1988 `activity_candidate`: población=9, locked=2.
- 1993 `experiment_candidate`: población=28, locked=3.
- 1993 `project_candidate`: población=4, locked=0.
- 2014 `experiment_candidate`: población=32, locked=2.
- 2014 `project_candidate`: población=30, locked=1.

## Regla de uso
Los pesos se fijan antes de ver anotaciones humanas. No deben recalcularse en función del desempeño del modelo ni de las diferencias históricas.
