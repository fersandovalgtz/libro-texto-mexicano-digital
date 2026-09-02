# LTMD-U2 — resolución del shell institucional de los visores 2026–2027

## Alcance

Esta capa registra una observación técnica separada para los **39 objetos fuente** de LTMD-U2. Su propósito es responder una pregunta estrecha: ¿la URL canónica del objeto fuente resolvió una superficie HTML reconocible como lector institucional de CONALITEG durante el corte observado?

No resuelve todavía los activos internos del visor ni convierte el objeto en fuente admitida.

## Resultado del corte 2026-09-02

Se comprobaron individualmente las 39 URLs de `data/catalog/ltmd_u2_source_objects_2026_2027.csv`.

Resultado:

- 39/39 `reader_shell_state=resolved`;
- 39/39 `transport_observation=fetch_succeeded`;
- contenido observado `text/html`;
- título observado `CONALITEG - Lector de PDF's`;
- el método de observación no expuso un código HTTP numérico, por lo que `http_status_observation=not_exposed`;
- 39/39 permanecen en `asset_resolution_state=not_observed`;
- 39/39 permanecen en `page_count_observation=not_observed`;
- 39/39 permanecen en `source_admission_state=not_assessed`.

El registro versionado es:

`data/catalog/ltmd_u2_reader_shell_resolution_2026_09_02.csv`

## Contrato epistemológico

La resolución del shell no autoriza inferencias sobre los activos que el JavaScript del lector pudiera solicitar después de cargar la superficie HTML.

```text
reader_shell_resolved != asset_resolved
asset_resolved != source_admitted
source_admitted != ocr_available
ocr_available != text_verified
computational_candidate != semantic_ready
publicly_accessible != openly_licensed
```

Tampoco se interpreta un fallo de transporte futuro como inexistencia documental. Un estado `unresolved` o `ambiguous` sólo describe la observación de ese intento.

## Validación reproducible

El contrato entre el registro de objetos fuente y esta capa se valida con:

```bash
python scripts/validate_u2_reader_shell_resolution.py
```

El validador exige:

- cardinalidad exacta 39→39;
- correspondencia exacta de `source_object_id`, `viewer_key` y `viewer_url` con el registro canónico U2;
- unicidad de identidad;
- coherencia entre `reader_shell_state` y el resultado de transporte;
- prohibición de declarar conteo de páginas mientras `asset_resolution_state=not_observed`;
- prohibición explícita de promover `source_admission_state` desde evidencia de shell.

El esquema de fila es `schemas/ltmd_u2_reader_shell_resolution.schema.json` y las pruebas están en `tests/test_validate_u2_reader_shell_resolution.py`.

## Derechos y preservación

El CSV contiene únicamente identidad, URL institucional y observaciones técnicas no sustitutivas. No incorpora PDF, JPEG, OCR, portadas ni páginas de las obras.

La disponibilidad pública del lector sigue separada del derecho de redistribución.

## Siguiente capa

El siguiente trabajo debe resolver **activos y paginación** con un contrato distinto. Debe registrar estados positivos, negativos y ambiguos sin descargar ni versionar por defecto bytes fuente protegidos. Sólo después de identificar procedencia técnica suficiente podrá evaluarse `source_admitted` bajo la política de derechos de LTMD.
