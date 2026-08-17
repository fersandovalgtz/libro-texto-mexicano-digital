# LTMD — semántica temporal de `catalog_generation`

Versión: `LTMD_CATALOG_GENERATION_SEMANTICS_0.1`.

Corte: **16 de agosto de 2026**.

## Regla

En LTMD, `catalog_generation` representa una **etiqueta institucional de navegación/cohorte del Catálogo Histórico de CONALITEG**. No representa automáticamente el año de primera edición, edición revisada, reimpresión, impresión ni ciclo escolar del objeto servido.

Por tanto, queda prohibido usar `catalog_generation` como sustituto de una fecha bibliográfica en análisis longitudinales, modelos históricos, visualizaciones temporales o afirmaciones editoriales sin evidencia bibliográfica independiente del objeto.

## Evidencia institucional

La interfaz del Catálogo Histórico presenta la instrucción **“Indique el año en el que considera inició su educación primaria”** y ofrece, alternativamente, seleccionar una **“generación”**. La semántica operativa del control es de cohorte/navegación, no una declaración bibliográfica del año de edición de cada libro.

Fuente institucional:

- https://historico.conaliteg.gob.mx/

## Evidencia interna falsadora

`H2014P5FCA` está clasificado por el catálogo como **Generación 2014**. Sin embargo, la página legal del objeto actualmente servido por el propio dominio institucional fue descargada y verificada contra el SHA-256 y tamaño congelados en el manifiesto W7. Un ensemble OCR sobre esa página identifica de manera redundante:

- **Primera edición, 2014**.
- **Tercera reimpresión, 2017 (ciclo escolar 2017-2018)**.
- **D. R. © Secretaría de Educación Pública, 2014**.

La huella se documenta en:

- `data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.csv`
- `data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.md`

Este caso es suficiente para falsar la regla simplista `catalog_generation == publication_year`: un objeto bajo la etiqueta de catálogo 2014 contiene explícitamente una reimpresión de 2017.

## Dimensiones temporales separadas

LTMD mantendrá, conceptualmente y cuando exista evidencia, al menos las siguientes dimensiones:

| campo | significado | fuente admisible |
|---|---|---|
| `catalog_generation` | cohorte/etiqueta de navegación institucional | catálogo CONALITEG |
| `first_edition_year` | año declarado de primera edición | página legal / registro bibliográfico |
| `edition_statement` | declaración de edición, revisión o versión | página legal / registro bibliográfico |
| `reprint_year` | año declarado de reimpresión | página legal / registro bibliográfico |
| `school_cycle` | ciclo escolar declarado para la tirada/reimpresión | página legal / documentación SEP |
| `bibliographic_observation_page` | posición de la evidencia dentro del objeto | manifiesto canónico |
| `bibliographic_observation_sha256` | huella de la página que sustenta la extracción | manifiesto canónico |
| `bibliographic_extraction_method` | manual, OCR, OCR ensemble, registro externo, etc. | proceso LTMD versionado |

No todos los objetos tendrán inmediatamente todos estos campos. La ausencia se mantiene como desconocida; nunca se completa mediante el año de generación por defecto.

## Jerarquía de evidencia temporal

Para una afirmación bibliográfica de un objeto se prefiere, en este orden:

1. página legal/créditos del propio objeto institucional, con procedencia y hash;
2. registro bibliográfico institucional inequívocamente ligado al objeto;
3. reproducción externa cuya identidad documental haya sido demostrada;
4. fuente secundaria como corroboración, claramente etiquetada.

Coincidencia de título, grado, etiqueta de generación, número de páginas o cercanía cronológica no basta para asignar una fecha bibliográfica.

## Consecuencia para análisis existentes

Los cierres W3, W4 y W7, FRAGSEG, PAGESTRUCT, reutilización textual exacta y la comparación técnica W4↔W7 son principalmente descriptores de procesamiento y no necesitan reinterpretarse como cronologías editoriales.

En cambio, cualquier futuro análisis histórico que pretenda comparar “libros de 2014”, “libros de 2018”, reformas o periodos deberá decidir explícitamente qué eje temporal usa: cohorte del catálogo, primera edición, reimpresión, ciclo escolar u otro. El eje elegido debe estar respaldado por una capa bibliográfica reproducible.

## Regla para alias y continuidad

La separación temporal tampoco autoriza aliases. Dos objetos con el mismo año editorial o ciclo escolar pueden ser distintos; dos objetos bajo generaciones diferentes pueden compartir contenido. Identidad documental, continuidad textual y temporalidad bibliográfica se registran como relaciones separadas.

## Estado

Esta regla entra en vigor como contrato metodológico transversal de LTMD. Toda expansión futura del corpus y todo producto analítico deberá preservar la diferencia entre **cohorte de catálogo** y **fecha bibliográfica observada**.
