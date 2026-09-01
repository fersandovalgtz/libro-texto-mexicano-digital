# LTMD v0.2.0-rc.1 — notas de release

Fecha de metadata candidata: 31 de agosto de 2026.

`v0.2.0-rc.1` representa un corte científico reproducible de **LTMD Open** posterior a `v0.1.0-rc.1`. No declara estabilidad 1.0 y no convierte deuda de validación humana o jurídica en evidencia confirmada.

## Alcance científico

- Universo operativo LTMD-U1: **542/542 visores censados**.
- Cobertura técnica efectiva: **524/542 (96.68%)**.
- Objetos canónicos de procesamiento: **492/542 (90.77%)**.
- Validación semántica humana: **0/542**.
- Se conservan separadas identidad documental, cobertura técnica, OCR disponible, validación humana e interpretación histórica.

## Cambios técnicos principales

- Consolidación corpus-wide de LTMD-U1 con registro explícito de **18 retenciones** técnicas.
- Full-Text Research Layer (`LTMD_FTRL_0.1`) reconstruible localmente, con verificación SHA-256, OCR por página, normalización conservadora y búsqueda SQLite FTS5.
- LTMD Analytics 0.1 integrado a la arquitectura y cubierto por un gate de pruebas independiente.
- Ledger de integridad y validadores reproducibles para la superficie pública U1.
- Los artefactos fuente restringidos, OCR íntegro y bases locales permanecen fuera de GitHub por defecto.

## Gobernanza y calidad

- `Repository quality`, `Scientific release preflight` y `LTMD Analytics tests` son gates de la candidata.
- El endurecimiento #132 impide que nuevos workflows o workflows modificados introduzcan/conserven escrituras directas (`contents: write` / `git push`) sin fallar CI.
- La deuda heredada de workflows con permisos de escritura se mantiene visible y se migra por lotes bajo #133.
- La protección efectiva de `main` y los metadatos externos de descubrimiento se gobiernan en #119 y son condición previa a publicar esta release.

## Deuda científica explícita

Esta release **no** cierra ni reinterpreta:

- #95: inspección visual de las 457 páginas `explicit_general` del estudio de lenguas indígenas;
- #123: validación OCR CER/WER con referencia humana preregistrada;
- #124: validación humana del libro de códigos 0.1;
- #4: cuatro excepciones de routing W2 Matemáticas 2018;
- #5: cinco fuentes W7 retenidas sin alias heurístico;
- #2: categorías amarilla/roja de derechos sobre derivados CONALITEG/SEP.

Guardas obligatorias:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `computational_candidate != semantic_ready`;
- `zero_hits != demonstrated_absence`.

## Derechos y preservación

No se redistribuyen masivamente JPEG, PDF, páginas fuente ni OCR íntegro de materiales con derechos no aclarados. El código original y los derivados propios permanecen sujetos a las licencias documentadas en el repositorio.

No se incorpora DOI en `CITATION.cff`, `codemeta.json` ni README antes de un depósito real y verificable. Después de congelar y publicar `v0.2.0-rc.1`, debe evaluarse el depósito en Zenodo y sólo entonces sincronizar el DOI asignado.

## Gate de publicación

Antes de crear el tag/release deben cumplirse simultáneamente:

- [ ] #119 cerrado con `main` protegido y metadatos de descubrimiento completos;
- [ ] `Repository quality` verde;
- [ ] `Scientific release preflight` verde;
- [ ] `LTMD Analytics tests` verde;
- [ ] ausencia de secretos, OCR íntegro y material fuente restringido versionado;
- [ ] metadata CFF/CodeMeta/VERSION/README/CHANGELOG sincronizada.

La existencia de esta rama o de estas notas **no equivale** a que la release esté publicada.
