# LTMD-U1 W7 — recuperación conservadora de confusión OCR en reimpresión

Versión: `LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.2`.

- Cohorte objetivo derivada reproduciblemente desde el audit pre-recovery: **5** objetos.
- Objetos con reimpresión recuperada por regla estrecha: **2**.
- Objetos que permanecen sin statement coincidente: **3**.

0.2 elimina la dependencia circular de 0.1: los targets se derivan de `LTMD_U1_W7_BIBLIOGRAPHIC_CANDIDATE_SUPPORT_0.1`, buscando un ciclo escolar fuerte sin edición/reimpresión fuerte que coincida con su año inicial. La tabla final de candidatos no participa en la selección.

La única normalización permitida sigue siendo `reimpresión` con `i→l/I/1` inmediatamente después de `re`. Se exige ≥2 PSM sobre la misma página SHA-verificada y coincidencia exacta con el inicio del ciclo.

## Recuperaciones

| objeto | ciclo | statement recuperado | página | PSM | tokens OCR |
|---|---|---|---:|---|---|
| `H2011P5CI326` | `2013-2014` | `third_reprint:2013` | 2 | `3;11;12` | `relmpresión` |
| `H2014P4FCA` | `2017-2018` | `third_reprint:2017` | 2 | `3;4;6;11` | `reimpresión;relmpresión` |

## Sin recuperación

- `H2008P5CI278`: permanece sin statement compatible con `2008-2009`.
- `H2011P4CI315`: permanece sin statement compatible con `2013-2014`.
- `H2011P6CI336`: permanece sin statement compatible con `2013-2014`.

## Límite epistemológico

La recuperación repara únicamente una confusión de caracteres OCR repetida y documentada. `human_validated=0` permanece. Los tres objetos no recuperados no reciben ninguna imputación y el proceso no usa `catalog_generation` para derivar fechas.
