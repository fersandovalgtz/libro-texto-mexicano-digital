# LTMD — auditoría de resolución de instancia bibliográfica

Versión: `LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_AUDIT_0.1`.

- Resoluciones 0.1 auditadas: **9/9**.
- `audit_pass=1`: **9/9**.
- Convergencia entre páginas distintas (`A_cross_page`): **0**.
- Declaración conjunta en la misma página (`B_same_page`): **9**.
- Años efectivos que difieren de `catalog_generation`: **4/9**.

La auditoría confirma que las nueve coincidencias cumplen la regla temporal publicada y que `catalog_generation` está excluido de la resolución. También corrige una posible sobrelectura: **sólo los casos Tier A aportan corroboración entre páginas independientes**; Tier B representa dos declaraciones estructuradas en el mismo activo fuente SHA-verificado.

## Topología de evidencia

| objeto | cohorte | año efectivo | declaración | páginas declaración | páginas ciclo | tier | difiere de cohorte |
|---|---:|---:|---|---|---|---|---|
| `H2008P1CI250` | 2008 | 2010 | `third_edition:2010` | `2` | `2` | `B_same_page` | sí |
| `H2008P2CI257` | 2008 | 2008 | `first_edition:2008` | `2` | `2;6` | `B_same_page` | no |
| `H2008P6CI286` | 2008 | 2008 | `first_edition:2008` | `2` | `2;6` | `B_same_page` | no |
| `H2011P1CI294` | 2011 | 2013 | `fourth_edition:2013` | `2` | `2` | `B_same_page` | sí |
| `H2011P2CI301` | 2011 | 2013 | `fourth_edition:2013` | `2` | `2` | `B_same_page` | sí |
| `H2014P5FCA` | 2014 | 2017 | `third_reprint:2017` | `4` | `4` | `B_same_page` | sí |
| `H2019P4FCA` | 2019 | 2019 | `fifth_edition:2019` | `2` | `2` | `B_same_page` | no |
| `H2019P5FCA` | 2019 | 2019 | `second_edition:2019` | `4` | `4` | `B_same_page` | no |
| `H2019P6FCA` | 2019 | 2019 | `second_edition:2019` | `4` | `4` | `B_same_page` | no |

## Interpretación permitida

- `A_cross_page`: candidato de año efectivo con convergencia temporal entre páginas fuente distintas.
- `B_same_page`: candidato de año efectivo derivado de una declaración conjunta edición/reimpresión + ciclo en la misma página fuente.

En ambos casos la fuente es institucional y SHA-verificada, pero `human_validated=0` sigue aplicando. La auditoría recomienda describir estos resultados como **candidatos bibliográficos resueltos por regla técnica**, no como fechas históricas definitivamente validadas por una persona.

## Interpretación no permitida

No usar Tier B como si fuera corroboración entre fuentes independientes. No interpretar que un año efectivo igual a la cohorte del catálogo fue derivado de ella; la regla y las observaciones mantienen esa variable fuera del cálculo. Los 17 objetos no resueltos permanecen sin año efectivo y no deben imputarse.
