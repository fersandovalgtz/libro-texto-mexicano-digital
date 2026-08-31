# LTMD: límites entre infraestructura abierta y servicios operados

**Estado:** documento normativo de arquitectura pública  
**Fecha de adopción:** 31 de agosto de 2026

Libro de Texto Mexicano Digital (LTMD) combina una infraestructura científica abierta con superficies operadas de investigación y servicios. Esta separación evita confundir apertura científica, derechos sobre materiales fuente y capacidades comerciales.

## 1. LTMD Open

Este repositorio constituye la superficie canónica de **LTMD Open**. Publica, cuando jurídica y científicamente corresponde:

- código y contratos técnicos;
- metodología, protocolos y documentación;
- metadatos, hashes y manifiestos de integridad;
- esquemas y derivados originales publicables;
- pruebas, validadores y mecanismos de reproducibilidad;
- releases, citación, procedencia y gobernanza.

LTMD Open debe permanecer auditable y reproducible. Una capacidad comercial no justifica degradar la trazabilidad, ocultar metodología necesaria para interpretar resultados ni reescribir retroactivamente una release.

## 2. LTMD Research

**LTMD Research** es la superficie operada orientada al trabajo de investigación. Puede ofrecer búsqueda avanzada, comparación longitudinal, visualización, exportación, espacios de trabajo, colaboración, cómputo y otras capacidades gestionadas.

La existencia de LTMD Research no convierte los materiales fuente de terceros en activos exclusivos de LTMD. Tampoco modifica por sí sola las licencias del software o de los derivados publicados en este repositorio.

## 3. LTMD Services

**LTMD Services** agrupa capacidades operadas o especializadas, por ejemplo API, estudios y datasets derivados a medida, soporte, curaduría y validación especializada.

Los servicios deben respetar las mismas fronteras epistemológicas del repositorio: una señal automática no se presenta como validación humana y un resultado de búsqueda no se convierte por sí mismo en afirmación histórica.

## 4. Frontera de datos y derechos

Por defecto, permanecen fuera del repositorio público:

- PDF, JPEG, páginas o reproducciones extensas de materiales fuente de terceros cuando no exista fundamento jurídico suficiente para redistribuirlos;
- OCR íntegro reconstruido a partir de esos materiales cuando pueda operar como sustituto de la fuente;
- índices full-text, caches, bases SQLite y otros artefactos locales que contengan texto fuente restringido;
- credenciales, secretos, rutas privadas y ledgers operativos que no deban publicarse.

GitHub puede publicar código de reconstrucción, contratos, métricas, hashes y agregados no sustitutivos cuando sean lícitos y científicamente defendibles.

## 5. Identidad institucional y autoría científica

La identidad de producto puede presentarse institucionalmente como **Universidad CEEES → LTMD / LTMD Research / LTMD Services**. La institucionalización de la marca no debe borrar autoría, procedencia o responsabilidad científica cuando éstas sean necesarias para citación, ORCID, licencias, propiedad intelectual, releases o integridad metodológica.

## 6. Regla de no regresión

Toda contribución pública debe preservar al menos estas separaciones:

`source_material != open_licensed_asset`

`ocr_available != text_verified`

`search_hit != historical_claim`

`computational_candidate != semantic_ready`

`operated_service != exclusive_ownership_of_source_material`

## 7. Criterio para nuevas funciones

Una nueva función se prioriza si aumenta valor científico verificable, reduce trabajo del investigador, mejora trazabilidad o fortalece una capacidad operada sostenible. Si no satisface con claridad al menos uno de esos criterios, debe justificarse antes de incorporarse al núcleo.

Este documento define límites de producto y publicación. No sustituye `LICENSE`, `DATA_LICENSE.md`, `GOVERNANCE.md`, `PROVENANCE.md` ni los protocolos científicos específicos.