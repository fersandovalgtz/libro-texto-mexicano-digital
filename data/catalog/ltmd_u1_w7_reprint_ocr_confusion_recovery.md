# LTMD-U1 W7 — recuperación conservadora de confusión OCR en reimpresión

Versión: `LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.1`.

- Objetos objetivo con ciclo pero sin statement coincidente: **5**.
- Objetos con reimpresión recuperada por regla estrecha: **2**.
- Objetos que permanecen sin statement coincidente: **3**.

La única normalización permitida es la confusión OCR documentada dentro de la palabra `reimpresión`: `i` puede aparecer como `l`, `I` o `1` inmediatamente después de `re`. Se exige el mismo ordinal+año en ≥2 PSM y que el año coincida con el inicio del ciclo escolar ya observado. No se modifica ningún otro token ni se usa `catalog_generation`.

## Recuperaciones

| objeto | ciclo | statement recuperado | página | PSM | tokens OCR |
|---|---|---|---:|---|---|
| `H2011P5CI326` | `2013-2014` | `third_reprint:2013` | 2 | `3;11;12` | `relmpresión` |
| `H2014P4FCA` | `2017-2018` | `third_reprint:2017` | 2 | `3;4;6;11` | `reimpresión;relmpresión` |

## Sin recuperación

- `H2008P5CI278`: permanece sin statement que coincida con `2008-2009`.
- `H2011P4CI315`: permanece sin statement que coincida con `2013-2014`.
- `H2011P6CI336`: permanece sin statement que coincida con `2013-2014`.

## Límite epistemológico

Una recuperación aquí sólo repara una confusión de caracteres OCR dentro de un marcador bibliográfico explícito y repetido. Sigue siendo `human_validated=0`. La recuperación puede alimentar una nueva versión de observaciones/candidatos, pero no convierte el año en fecha histórica humana validada ni autoriza imputar los objetos que continúan sin match.
