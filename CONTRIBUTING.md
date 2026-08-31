# Contribuir a Libro de Texto Mexicano Digital

LTMD recibe contribuciones que mejoren datos, código, documentación, reproducibilidad y revisión metodológica sin borrar incertidumbre ni procedencia.

## Antes de proponer cambios

- abra o vincule un issue cuando el cambio modifique metodología, contratos, cobertura o resultados;
- utilice el formulario de issue que corresponda para distinguir errores técnicos, discrepancias de datos/metodología y nuevas capacidades;
- identifique la fuente o evidencia que sustenta la modificación;
- no incorpore libros, páginas, imágenes u otros materiales de terceros al repositorio sin base jurídica clara;
- mantenga separadas correcciones técnicas, propuestas semánticas y validaciones humanas;
- revise `docs/LTMD_PRODUCT_BOUNDARIES.md` cuando el cambio afecte la frontera entre LTMD Open y superficies operadas.

## Flujo de ramas y pull requests

Los cambios a `main` deben entrar normalmente mediante una rama específica y un pull request. Evite commits directos a `main`, salvo una intervención excepcional cuya urgencia y razón queden documentadas.

La plantilla de pull request forma parte del control de calidad: debe declarar propósito, evidencia, validación ejecutada, impacto científico, derechos, privacidad, reproducibilidad y riesgos. Los pull requests deben mantenerse pequeños y auditables cuando sea posible.

El título debe indicar el área modificada y la descripción debe permitir a otra persona comprender qué se cambió, por qué, cómo se verificó y qué consecuencias científicas o de compatibilidad tiene.

## Requisitos mínimos

Toda contribución debe:

1. ser reproducible o explicar por qué no puede serlo;
2. conservar identificadores documentales y relaciones de fuente;
3. incluir o actualizar pruebas, manifiestos o documentación cuando cambie comportamiento verificable;
4. actualizar `CHANGELOG.md` cuando afecte una release futura o una interfaz científica;
5. no elevar automáticamente un estado técnico a `semantic_ready`;
6. documentar incertidumbres, excepciones y resultados negativos relevantes;
7. no incorporar secretos, credenciales, rutas privadas o artefactos locales restringidos;
8. pasar los controles automatizados aplicables antes de integrarse a `main`.

## Cambios metodológicos o de datos

Una modificación de denominadores, reglas de inclusión, identidad documental, procedencia, estados de validación, contratos o interpretación de resultados exige evidencia explícita. No debe ocultarse dentro de un refactor o una corrección editorial.

`corpus_ready != semantic_ready`, `search_hit != historical_claim` y `computational_candidate != semantic_ready` son reglas de no regresión.

## Dependencias y automatización

Las actualizaciones de dependencias deben revisarse como cualquier otro cambio. Los workflows deben operar con el menor conjunto de permisos de `GITHUB_TOKEN` necesario y no deben introducir secretos en el repositorio o en artefactos públicos.

## Atribución

Las contribuciones sustantivas deben reconocerse de acuerdo con su naturaleza y alcance. Cuando una contribución tenga relevancia académica, puede documentarse con roles CRediT u otro esquema apropiado en una release posterior.

## Conducta, soporte y seguridad

Consulte `CODE_OF_CONDUCT.md`, `SUPPORT.md` y `SECURITY.md`. Los problemas de seguridad no deben publicarse con detalles explotables antes de que exista una vía razonable de mitigación.