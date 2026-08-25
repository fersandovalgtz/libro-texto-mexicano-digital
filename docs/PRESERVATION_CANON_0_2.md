# LTMD — canon de preservación 0.2

**Estado:** canónico para el proyecto `libro-texto-mexicano-digital`.

## 1. Principio rector

LTMD mantiene tres capas distintas y no intercambiables:

- **GitHub**: código, documentación, metadatos públicos permitidos, historia de versiones, pruebas reproducibles y evidencia pública sin texto restringido.
- **Google Drive privado**: archivo persistente de fuentes y derivados que no deben publicarse indiscriminadamente, incluidos OCR, SQLite/FTS5, QC, manifiestos y paquetes de preservación.
- **Notion**: índice humano, memoria operativa y registro de decisiones; nunca es la única fuente de verdad técnica o archivística.

## 2. Regla de unicidad para el corpus textual

Al cierre de LTMD-U1, Google Drive deberá contener **una sola versión completa, privada, íntegra y verificable de todo el material textual o equivalente derivado de los Libros de Texto Gratuitos (LTG)** que sea necesario para investigación y reproducción interna del corpus.

Esa versión integral debe reunir, según corresponda:

1. OCR por página o unidad equivalente;
2. identificadores persistentes y relación con la identidad histórica y el objeto canónico;
3. SQLite/FTS5 u otra representación estructurada de consulta;
4. manifiestos de procedencia y cobertura;
5. controles de calidad y estados epistemológicos;
6. checksums criptográficos;
7. información suficiente para reconstruir la correspondencia fuente → página → texto derivado sin depender de artefactos efímeros de CI.

La copia integral de Drive es **archivo privado de preservación**, no una autorización para redistribuir texto o imágenes sujetos a restricciones.

## 3. Snapshots del repositorio

Los snapshots completos del repositorio son mecanismos de contingencia, no un historial paralelo a Git.

Regla operativa:

- conservar **un único snapshot integral vigente del repositorio con historia Git completa**;
- reemplazarlo únicamente en hitos archivísticos mayores, no en cada commit o checkpoint;
- antes de reemplazarlo, verificar integridad, clonabilidad/reconstrucción y checksum;
- una vez verificado el nuevo snapshot, el snapshot anterior puede eliminarse de Drive;
- los estados intermedios permanecen preservados por la propia historia Git, los PR, los commits, los tags/releases y la evidencia de CI.

No deben acumularse snapshots completos redundantes de ~100–200 MB por cambios menores.

## 4. Artefactos de GitHub Actions

Los artefactos de Actions son **handoffs temporales**, no almacenamiento permanente.

Para corridas FTRL/OCR:

- los paquetes privados deben cifrarse antes de cualquier subida pública o semipública;
- la evidencia pública debe permanecer libre de texto restringido;
- los handoffs relevantes se copian al archivo privado de Drive sólo hasta que exista una consolidación integral verificada;
- una vez consolidada y verificada la versión integral de una ola o del corpus, los handoffs redundantes pueden eliminarse de Drive conforme a este canon.

## 5. Estados científicos separados del archivo

La preservación no modifica por sí sola el estado epistemológico del corpus.

Se mantienen como conceptos distintos:

- `corpus_ready != semantic_ready`
- `ocr_available != text_verified`
- `search_hit != historical_claim`
- `zero_hits != demonstrated_absence`
- `final_exception != source_resolved`
- `computationally_validated != archival_complete`

Una ola sólo puede declararse `archival_complete=true` cuando su material privado necesario está persistido, verificado y cubierto por manifiestos/checksums. `text_verified` requiere validación independiente del texto y no se infiere del éxito del OCR.

## 6. Política de ahorro de almacenamiento

Se considera redundante y eliminable, después de verificación:

- snapshots completos superseded del repositorio;
- duplicados byte-a-byte o reconstrucciones equivalentes del mismo snapshot;
- handoffs temporales ya absorbidos por una consolidación integral verificada;
- copias intermedias que no añaden cobertura, procedencia, evidencia o capacidad de reconstrucción.

Se conserva aquello que aporte una función archivística distinta: fuente, corpus derivado integral, manifiesto, checksum, QC, evidencia reproducible o historia Git.

## 7. Regla final de cierre de LTMD-U1

Antes de declarar LTMD-U1 archivísticamente cerrado se deberá demostrar que:

- existe **exactamente una copia integral canónica del material textual/derivado de los LTG en Drive privado**;
- su cobertura coincide con el universo final documentado de U1 y sus excepciones;
- no depende de artefactos temporales de GitHub Actions;
- puede reconstruirse y auditarse mediante manifiestos y checksums;
- los duplicados y snapshots superseded han sido depurados;
- GitHub conserva la historia técnica y reproducible del proyecto sin alojar indiscriminadamente material restringido.

Este canon prevalece sobre prácticas anteriores de acumulación de snapshots por checkpoint.