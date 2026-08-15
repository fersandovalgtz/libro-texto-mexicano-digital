# Cobertura de la muestra humana SEMB 0.3

Versión: `SEMB03_SAMPLE_COVERAGE_0.2`. Universo elegible FRAGSEG: **5037** fragmentos; muestra: **480**; desarrollo: 320; validación bloqueada: 160.

La muestra es deliberadamente estratificada y no es autoponderada. Se congelan pesos descriptivos `N_h/n_h` por generación × tipo y generación × longitud. Las métricas primarias preregistradas permanecen sin ponderar; los pesos sólo sirven para análisis de transportabilidad al corpus.

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

## Diversidad de páginas
- 1972: muestra 120 fragmentos en **82 páginas** de 208 elegibles; máximo 4 fragmentos de una misma página; locked 40 fragmentos en **34 páginas**, máximo 2 por página.
- 1988: muestra 120 fragmentos en **79 páginas** de 151 elegibles; máximo 4 fragmentos de una misma página; locked 40 fragmentos en **36 páginas**, máximo 2 por página.
- 1993: muestra 120 fragmentos en **78 páginas** de 154 elegibles; máximo 5 fragmentos de una misma página; locked 40 fragmentos en **35 páginas**, máximo 2 por página.
- 2014: muestra 120 fragmentos en **73 páginas** de 118 elegibles; máximo 5 fragmentos de una misma página; locked 40 fragmentos en **33 páginas**, máximo 3 por página.
- Total: 480 fragmentos abarcan **312 páginas**; los 160 locked abarcan **138 páginas**.

## Longitud
- `4-12` tokens: población=1902, muestra=162, locked=62.
- `13-30` tokens: población=2304, muestra=245, locked=72.
- `31-60` tokens: población=653, muestra=56, locked=19.
- `61-120` tokens: población=177, muestra=17, locked=7.
- `>120` tokens: población=1, muestra=0, locked=0.
- Mediana de longitud: universo=15 tokens; muestra=16.0 tokens.

## Regla de uso
Los pesos y diagnósticos de diversidad se fijan antes de ver anotaciones humanas. No deben recalcularse en función del desempeño del modelo ni de las diferencias históricas. La dependencia entre fragmentos de una misma página deberá respetarse en análisis de incertidumbre posteriores.
