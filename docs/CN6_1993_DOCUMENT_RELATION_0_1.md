# Relación documental de los dos objetos de Ciencias Naturales de 6º en la generación CONALITEG 1993 — 0.1

Fecha: 2026-08-15

## Problema

El inventario reproducible del Catálogo Histórico detectó **dos visores distintos** para Ciencias Naturales de sexto grado dentro de `catalog_generation=1993`:

- `H1993P6CI210` — *Ciencias Naturales*;
- `H1993P6CI209` — *Ciencias Naturales y desarrollo humano*.

No deben tratarse como duplicados técnicos ni elegirse uno por conveniencia. La evidencia disponible indica que representan **dos momentos sucesivos del programa de renovación** dentro de la misma generación documental del catálogo.

## Evidencia del objeto

### `LTMD-CN6-G1993-CN` — `H1993P6CI210`

La auditoría del visor confirma 242 posiciones y 241 JPEG reales. El front matter recupera ISBN **968-29-6256-0** y señales bibliográficas asociadas con **1994, 1995 y 1996**. El cotejo dirigido de la página legal detecta secuencias de reimpresión en esos años, aunque el OCR no reconstruye limpiamente toda la serie editorial y por ello no se promueve automáticamente cada secuencia a metadato definitivo.

Una fuente contemporánea de agosto de 1999 afirma explícitamente que el libro de *Ciencias Naturales* de sexto tuvo su **primera edición en 1994** y cuatro reimpresiones entre **1995 y 1998**.

**Interpretación documental:** objeto temprano de la reforma / familia 1994–1998.

### `LTMD-CN6-G1993-DH` — `H1993P6CI209`

La auditoría del visor confirma 250 posiciones y 249 JPEG reales. Un cotejo dirigido de la página legal recupera la secuencia explícita **primera edición → 1999**.

La prensa contemporánea documentó el 30 de julio de 1999 la presentación de *Ciencias Naturales y Desarrollo Humano*, que sería estrenado por el alumnado de sexto a partir del ciclo escolar que iniciaba el 23 de agosto de 1999. La misma nota indicó que con ese texto concluía el programa de renovación de libros de primaria iniciado seis años antes. Otra pieza del 20 de agosto de 1999 afirmó directamente que el nuevo libro venía a **reemplazar** al *Ciencias Naturales* de sexto cuya primera edición había aparecido en 1994.

**Interpretación documental:** objeto de reemplazo / cierre del ciclo de renovación, primera edición 1999.

## Fuentes contemporáneas externas

- Claudia Herrera Beltrán, “Fomentar los valores, propósito de libros para sexto de primaria”, *La Jornada*, 30 de julio de 1999: https://www.jornada.com.mx/1999/07/30/sexo.html
- Elena Urrutia, “La enseñanza de la sexualidad en la escuela primaria”, *La Jornada*, 20 de agosto de 1999: https://web.jornada.com.mx/1999/08/20/urrutia.html

Estas fuentes se utilizan como evidencia histórica contemporánea de presentación, sustitución y cronología. La autoridad bibliográfica última del objeto continúa siendo su propia página legal.

## Decisión para LTMD

1. **Conservar ambos objetos.** No se elimina `CI210` al aparecer `CI209`.
2. Mantener para ambos `catalog_generation=1993`; la generación del catálogo se interpreta como una **familia documental temporalmente estratificada**, no como un único año de observación.
3. Asignar provisionalmente los roles analíticos:
   - `LTMD-CN6-G1993-CN`: `document_role=early_reform_object`;
   - `LTMD-CN6-G1993-DH`: `document_role=replacement_mature_reform_object`.
4. Tratar **1994** como año de primera edición históricamente documentado para el objeto anterior sólo después de cotejar la página legal con suficiente claridad; la fuente contemporánea puede sostener la cronología histórica, pero el campo bibliográfico del dataset debe seguir una regla de evidencia explícita.
5. `LTMD-CN6-G1993-DH` puede registrar **1999** como candidato de primera edición de alta confianza porque coincide la secuencia bibliográfica recuperada de la página legal con la documentación contemporánea; una revisión visual/bibliográfica independiente puede promover posteriormente el estatus a `verified`.

## Implicación metodológica

Este caso demuestra empíricamente que una `catalog_generation` de CONALITEG **no es una marca temporal unívoca**. Una misma generación puede contener objetos sucesivos de la misma asignatura y grado. Por ello, cualquier análisis longitudinal de LTMD debe modelar al menos:

`catalog_generation` + `edition_year` + `document_role` + `viewer_key`

Cuando exista más de un objeto por celda grado×asignatura×generación, la selección o inclusión debe justificarse históricamente y nunca resolverse mediante una deduplicación por nombre.

## Estado

`relation_status = historically_supported_pending_final_bibliographic_verification`
