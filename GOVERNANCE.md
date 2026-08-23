# Gobernanza de Libro de Texto Mexicano Digital

## Alcance

Este documento define la gobernanza mínima de **Libro de Texto Mexicano Digital (LTMD)** como infraestructura de investigación. Su finalidad es mantener separadas la evidencia documental, el procesamiento computacional, la validación humana y las interpretaciones histórico-educativas.

## Autoridad de las capas

LTMD distingue, al menos, cinco niveles de autoridad:

1. **fuente institucional o documental**, que conserva la identidad del objeto de origen;
2. **resolución técnica**, que documenta activos, rutas, hashes, OCR y segmentación;
3. **datos derivados**, que pueden ser reproducibles sin ser todavía evidencia semántica validada;
4. **validación humana**, que debe quedar identificada, fechada y vinculada con el protocolo aplicado;
5. **interpretación histórica**, que solo puede apoyarse en capas cuyo alcance y limitaciones estén explícitos.

`corpus_ready` no implica `semantic_ready`. Ningún cierre técnico autoriza por sí mismo una afirmación histórica, curricular o semántica.

## Decisiones y cambios

Los cambios que alteren definiciones, denominadores, contratos de datos, criterios de inclusión, procedimientos de validación o resultados publicados deben:

- quedar versionados en Git;
- documentarse en `CHANGELOG.md` o en una nota metodológica específica;
- conservar trazabilidad hacia la evidencia previa;
- evitar reescrituras retrospectivas de releases publicadas;
- declarar cualquier ruptura de compatibilidad o cambio de estimando.

## Datos de terceros y derechos

El repositorio no presume derechos sobre libros, páginas, imágenes, texto fuente, marcas u otros materiales de SEP/CONALITEG o de terceros. Las licencias del repositorio cubren únicamente software y productos derivados respecto de los cuales exista capacidad jurídica para licenciarlos. Véase `DATA_LICENSE.md`.

## Revisión humana y automatización

La automatización puede ampliar cobertura, verificar integridad y producir candidatos; no sustituye la validación humana cuando el constructo investigado la requiere. Los resultados negativos, ambiguos o retenidos se conservan como parte de la evidencia metodológica y no se corrigen mediante imputación silenciosa.

## Responsabilidad académica

La coordinación del proyecto mantiene la responsabilidad sobre releases, documentación metodológica, integridad de la procedencia y comunicación pública de las limitaciones. Contribuciones externas deben seguir `CONTRIBUTING.md` y quedar atribuidas de forma verificable.

## Evolución

Esta política es versionada. Toda modificación sustantiva debe acompañar la evolución científica del proyecto y preservar la interpretabilidad de las versiones anteriores.
