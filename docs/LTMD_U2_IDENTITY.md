# LTMD-U2 — identidad documental de la cohorte contemporánea 2026–2027

## Alcance

LTMD-U2 es la capa contemporánea provisional de **Libro de Texto Mexicano Digital** para la primaria CONALITEG 2026–2027. Esta capa se mantiene separada de LTMD-U1 para no mezclar universos documentales, reglas de identidad ni estados de disponibilidad.

El corte inicial contiene **42 entradas de catálogo por grado** y **39 objetos fuente únicos**. La diferencia se debe a tres visores docentes compartidos entre pares de grados: `P1LPM`, `P3LPM` y `P5LPM`.

## Identidad de dos niveles

### Entrada de catálogo

Una entrada de catálogo representa la asociación editorial/pedagógica de un recurso con un grado concreto.

El identificador existente conserva esa granularidad:

```text
catalog_entry_id = CONALITEG-2026-PRIMARIA-G<grado>-<viewer_key>
```

Hay 42 entradas de catálogo en el corte 2026–2027.

### Objeto fuente

Un objeto fuente representa el visor documental único servido por CONALITEG, independientemente de cuántas entradas de catálogo lo referencien.

La identidad canónica es:

```text
source_object_id = CONALITEG:<source_cycle>:<level>:<viewer_key>
```

Para este corte:

```text
source_object_id = CONALITEG:2026:primaria:<viewer_key>
```

Hay 39 objetos fuente únicos.

`source_cycle` se toma del parámetro institucional `ciclo=` de la URL del visor, mientras `cycle_label` conserva la etiqueta editorial `2026-2027`. Ambos campos se mantienen separados deliberadamente.

## Invariantes

La materialización debe preservar:

```text
catalog_entry != source_object
viewer_key != global_document_id
publicly_accessible != openly_licensed
cataloged != source_admitted
source_admitted != ocr_available
ocr_available != text_verified
computational_candidate != semantic_ready
```

Además:

- `catalog_entry_id` debe ser único;
- `viewer_key`, `nivel` y `ciclo` de cada fila deben coincidir con los parámetros de su URL institucional;
- la combinación `CONALITEG + source_cycle + level + viewer_key` define la identidad de objeto fuente dentro de U2;
- la misma `viewer_key` en ciclos distintos produce objetos distintos;
- no se fusionan objetos entre ciclos por semejanza de título, grado o contenido;
- dos entradas que apuntan al mismo objeto fuente deben concordar en título, editor, URL, estado público y fecha de verificación;
- los únicos objetos compartidos del corte inicial son `P1LPM` (grados 1–2), `P3LPM` (3–4) y `P5LPM` (5–6).

## Artefactos

- Inventario de entradas: `data/catalog/conaliteg_primaria_2026_2027_inventory.csv`
- Registro materializado de objetos fuente: `data/catalog/ltmd_u2_source_objects_2026_2027.csv`
- Constructor/validador: `scripts/build_u2_source_objects.py`
- Esquema tipado de fila: `schemas/ltmd_u2_source_object.schema.json`
- Pruebas: `tests/test_build_u2_source_objects.py`

La materialización es determinista:

```bash
python scripts/build_u2_source_objects.py
```

El resultado debe reproducir exactamente el CSV versionado.

## Derechos y procedencia

Esta capa pública contiene **metadatos, identidades y enlaces institucionales**, no copias de las obras. La presencia de un visor público no autoriza a inferir una licencia abierta.

No se incorporan por defecto PDF, JPEG, OCR íntegro ni reconstrucciones secuenciales que sustituyan las obras fuente. Cualquier adquisición técnica posterior deberá ser temporal, trazable y compatible con `DATA_LICENSE.md`, `PROVENANCE.md` y `docs/LTMD_HISTORICAL_CONTEXT_AND_RIGHTS.md`.

## Estado científico

La creación de un `source_object_id` demuestra identidad de catálogo/visor dentro del corte definido. **No demuestra todavía resolución efectiva del visor, admisión de fuente, disponibilidad de OCR, verificación textual ni preparación semántica.**

El siguiente paso de U2 es producir un reporte reproducible de resolución técnica de los 39 visores, registrando resultados negativos o ambiguos como tales, sin convertirlos en afirmaciones de ausencia.
