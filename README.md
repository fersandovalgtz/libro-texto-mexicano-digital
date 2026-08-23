<p align="center">
  <img src="assets/repository-header-es.svg" alt="Libro de Texto Mexicano Digital — infraestructura abierta de investigación" width="100%">
</p>

<p align="center">
  <strong>Infraestructura abierta para estudiar longitudinalmente los libros de texto mexicanos con historia de la educación, humanidades digitales, análisis computacional y ciencia abierta.</strong><br>
  <sub>Identidad documental · integridad SHA-256 · OCR · segmentación · dependencia documental · validación humana · reproducibilidad</sub>
</p>

<p align="center">
  <a href="https://github.com/fersandovalgtz/libro-texto-mexicano-digital/releases/tag/v0.1.0-rc.1"><img src="https://img.shields.io/badge/release-v0.1.0--rc.1-172033?style=flat-square" alt="Release v0.1.0-rc.1"></a>
  <a href="CITATION.cff"><img src="https://img.shields.io/badge/citación-CFF%201.2-4b5563?style=flat-square" alt="CFF 1.2"></a>
  <a href="codemeta.json"><img src="https://img.shields.io/badge/metadatos-CodeMeta%203.1-3b5b92?style=flat-square" alt="CodeMeta 3.1"></a>
  <a href="FAIR_ASSESSMENT.md"><img src="https://img.shields.io/badge/FAIR%2FFAIR4RS-autoevaluación-2d6a4f?style=flat-square" alt="FAIR FAIR4RS"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/software-Apache--2.0-172033?style=flat-square" alt="Apache 2.0"></a>
  <a href="DATA_LICENSE.md"><img src="https://img.shields.io/badge/derivados-CC%20BY%204.0-7a263a?style=flat-square" alt="CC BY 4.0"></a>
</p>

<p align="center">
  <a href="https://github.com/fersandovalgtz/libro-texto-mexicano-digital/actions"><img src="https://img.shields.io/github/actions/workflow/status/fersandovalgtz/libro-texto-mexicano-digital/release-preflight.yml?branch=main&style=flat-square&label=CI%20%2F%20QA" alt="CI QA"></a>
  <img src="https://img.shields.io/badge/universo%20U1-542%20visores-455B55?style=flat-square" alt="542 visores U1">
  <img src="https://img.shields.io/badge/cobertura%20técnica-417%2F542%20·%2076.94%25-455B55?style=flat-square" alt="417 de 542 cobertura técnica">
  <img src="https://img.shields.io/badge/canónicos-386%2F542%20·%2071.22%25-5b4b8a?style=flat-square" alt="386 objetos canónicos">
  <img src="https://img.shields.io/badge/validación%20semántica%20humana-0%2F542-b7791f?style=flat-square" alt="0 de 542 validados semánticamente por humanos">
</p>

<p align="center">
  <a href="https://orcid.org/0000-0002-3168-6725"><img src="https://img.shields.io/badge/ORCID-0000--0002--3168--6725-A6CE39?style=flat-square&logo=orcid&logoColor=white" alt="ORCID"></a>
  <a href="https://github.com/fersandovalgtz/libro-texto-mexicano-digital/commits/main"><img src="https://img.shields.io/github/last-commit/fersandovalgtz/libro-texto-mexicano-digital?style=flat-square&label=último%20commit" alt="Último commit"></a>
  <a href="https://github.com/fersandovalgtz/libro-texto-mexicano-digital/stargazers"><img src="https://img.shields.io/github/stars/fersandovalgtz/libro-texto-mexicano-digital?style=flat-square&logo=github" alt="Stars"></a>
  <a href="https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues"><img src="https://img.shields.io/github/issues/fersandovalgtz/libro-texto-mexicano-digital?style=flat-square" alt="Issues"></a>
</p>

<p align="center">
  <a href="#qué-es-ltmd"><strong>Qué es</strong></a> ·
  <a href="#estado-científico"><strong>Estado científico</strong></a> ·
  <a href="#arquitectura-de-evidencia">Arquitectura</a> ·
  <a href="#reproducibilidad">Reproducibilidad</a> ·
  <a href="#derechos-y-licencias">Derechos</a> ·
  <a href="#citación">Citar</a> ·
  <a href="FAIR_ASSESSMENT.md">FAIR</a> ·
  <a href="GOVERNANCE.md">Gobernanza</a> ·
  <a href="PROVENANCE.md">Procedencia</a> ·
  <a href="README.en.md">English</a>
</p>

## Qué es LTMD

**Libro de Texto Mexicano Digital (LTMD)** es una infraestructura de investigación para construir un corpus histórico-computacional trazable de libros de texto mexicanos y estudiar cambios en currículo, lenguaje pedagógico, actividades escolares, valores, representaciones sociales y recursos visuales.

El proyecto no trata un visor de catálogo, un archivo, una generación editorial y un contenido textual como si fueran la misma unidad. Mantiene separadas la **identidad documental**, la **resolución de activos**, el **procesamiento técnico**, los **datos derivados**, la **validación humana** y la **interpretación histórica**.

> [!IMPORTANT]
> `corpus_ready` **no equivale** a `semantic_ready`. Una ola técnicamente cerrada puede ser reproducible y completa dentro de su alcance sin constituir todavía evidencia semántica validada por personas expertas.

## Estado científico

Corte documental de referencia: **23 de agosto de 2026**.

| Indicador | Estado |
|---|---:|
| Universo histórico operativo LTMD-U1 | **542 / 542 visores censados** |
| Cobertura técnica efectiva cerrada o resuelta | **417 / 542 (76.94%)** |
| Objetos canónicos de procesamiento | **386 / 542 (71.22%)** |
| Validación semántica humana | **0 / 542** |
| Release metodológica publicada | **v0.1.0-rc.1** |
| DOI de LTMD | **pendiente; no se anticipa** |

### Cobertura U1

| Ola | Dominio | Estado |
|---|---|---|
| W1 | Ciencias Naturales | cerrada técnicamente (40/40) |
| W2 | Matemáticas | parcial; 4 excepciones preservadas (60/64) |
| W3 | Español / Lengua | cerrada técnicamente (130/130) |
| W4 | Ciencias Sociales | cerrada técnicamente (14/14) |
| W5 | Historia | cerrada técnicamente (18/18) |
| W6 | Geografía / Atlas | cerrada técnicamente (42/42) |
| W7 | Formación Cívica y Ética | cohorte fuente-admitida cerrada; 5 retenidas (25/30) |
| W8 | Artes | cohorte fuente-admitida cerrada; 4 retenidas (16/20) |
| W9 | Educación Física | cerrada técnicamente (4/4) |
| W10 | Integrados / Multiarea | cohorte fuente-admitida cerrada; 1 retenidas (68/69) |
| W11 | Otros / No clasificados | en cola (111) |

El tablero reproducible se mantiene en [`data/catalog/ltmd_u1_coverage.md`](data/catalog/ltmd_u1_coverage.md) y el programa general en [`docs/LTMD_U1_MASTER_PLAN_0_1.md`](docs/LTMD_U1_MASTER_PLAN_0_1.md).

## Pregunta general

> ¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

## Arquitectura de evidencia

```text
catálogo institucional
        ↓
identidad documental / viewer_key / book_id
        ↓
resolución de activos + SHA-256
        ↓
OCR temporal
        ↓
PAGESTRUCT
        ↓
FRAGSEG
        ↓
metadatos, relaciones y hashes
        ↓
validación humana del constructo
        ↓
clasificación validada
        ↓
análisis histórico
```

LTMD conserva relaciones de reutilización, revisión, reemplazo y alias en lugar de presumir independencia entre generaciones editoriales. Las vistas de objeto, contenido único y revisión permiten estudiar dependencia documental sin borrar la identidad histórica de los visores.

Consulte [`PROVENANCE.md`](PROVENANCE.md) y [`GOVERNANCE.md`](GOVERNANCE.md).

## Principios de integridad científica

1. **La fuente no se corrige silenciosamente.** Fallos, huecos y excepciones permanecen documentados.
2. **La similitud no crea identidad documental.** Los aliases requieren evidencia verificable.
3. **La automatización no fabrica referencia humana.** Las etiquetas humanas solo existen cuando fueron producidas mediante el protocolo correspondiente.
4. **Los resultados negativos cuentan.** Incertidumbre, baja precisión o ausencia de evidencia se preservan como resultados metodológicos.
5. **Una release es un corte histórico.** El avance posterior de `main` no se atribuye retroactivamente a un tag publicado.

## Reproducibilidad

La infraestructura utiliza scripts versionados, GitHub Actions, manifiestos, hashes SHA-256, documentación por ola y reportes de integridad. La candidata metodológica pública [`v0.1.0-rc.1`](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/releases/tag/v0.1.0-rc.1) conserva un corte reproducible anterior a la expansión U1 posterior.

Para reconstrucción de releases se documentan dependencias en [`requirements-release.txt`](requirements-release.txt). Los protocolos, manuales, reportes y planes científicos se encuentran en [`docs/`](docs/).

La política general de calidad está en [`SCIENTIFIC_REPOSITORY_STANDARD.md`](SCIENTIFIC_REPOSITORY_STANDARD.md) y la autoevaluación FAIR/FAIR4RS en [`FAIR_ASSESSMENT.md`](FAIR_ASSESSMENT.md).

## Publicación y metadatos

LTMD expone metadatos para humanos y máquinas mediante:

- [`CITATION.cff`](CITATION.cff), compatible con la función **Cite this repository** de GitHub;
- [`codemeta.json`](codemeta.json), en CodeMeta 3.1;
- [`VERSION`](VERSION) y [`CHANGELOG.md`](CHANGELOG.md);
- releases de GitHub con notas y reportes de reproducibilidad;
- documentación de procedencia, gobernanza y licencias.

**No se declara DOI de LTMD hasta que exista un depósito real y verificable.** Esta decisión evita crear identificadores ficticios o inconsistentes entre GitHub y un archivo de preservación.

## Derechos y licencias

El software original de LTMD se distribuye bajo **Apache License 2.0**. Los datos derivados originales sobre los que exista capacidad jurídica para licenciar se ofrecen bajo las condiciones descritas en [`DATA_LICENSE.md`](DATA_LICENSE.md).

Estas licencias **no** se extienden automáticamente a libros, PDF, JPEG, portadas, ilustraciones, texto fuente, marcas u otros materiales de SEP/CONALITEG o terceros. La estrategia de procesamiento prioriza reconstrucción temporal, verificación de integridad y no redistribución de fuentes cuando los derechos no lo permiten.

## Contribución y gobernanza

Las contribuciones son bienvenidas cuando preservan procedencia, reproducibilidad y separación entre estados técnicos y semánticos. Véanse [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), [`SECURITY.md`](SECURITY.md) y [`GOVERNANCE.md`](GOVERNANCE.md).

## Citación

GitHub puede generar citas desde [`CITATION.cff`](CITATION.cff). Para la candidata metodológica publicada:

> Sandoval Gutierrez, Fernando. 2026. *Libro de Texto Mexicano Digital*, versión 0.1.0-rc.1. GitHub release. https://github.com/fersandovalgtz/libro-texto-mexicano-digital/releases/tag/v0.1.0-rc.1

Cuando exista un depósito real en Zenodo u otro archivo con identificador persistente, el DOI deberá incorporarse de forma coherente a `CITATION.cff`, `codemeta.json`, la release y esta sección.

## Responsable

**Fernando Sandoval Gutierrez**  
ORCID: [0000-0002-3168-6725](https://orcid.org/0000-0002-3168-6725)

---

<p align="center">
  <strong>LTMD documenta lo que sabe, lo que infiere y lo que todavía no puede afirmar.</strong>
</p>
