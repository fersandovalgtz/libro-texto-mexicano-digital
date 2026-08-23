# LTMD — metodología de búsqueda full-text

Versión: `LTMD_FTRL_SEARCH_0.1`.

## Objetivo

Establecer un protocolo reproducible para convertir una pregunta histórica en una concordancia auditable sobre la Full-Text Research Layer (FTRL).

## Niveles de evidencia

### Nivel A — coincidencia literal

Consulta de una forma exacta o una frase conocida. Ejemplo:

```text
"Benito Juárez"
```

Es útil para nombres propios y expresiones estables, pero no es exhaustivo si existen variantes ortográficas, flexivas u OCR defectuoso.

### Nivel B — conjunto de variantes preregistrado

Antes de mirar resultados interpretativos se documenta un conjunto explícito de formas:

```text
masonería OR masón OR masones OR masónica OR masónicas OR masónico OR masónicos OR francmasonería
```

El conjunto utilizado debe conservarse junto con el reporte para permitir reproducción.

### Nivel C — expansión contextual

Puede incorporar términos históricamente próximos —por ejemplo `logia`, `yorkino`, `escocés`—, pero esos términos **no son equivalentes por sí solos al concepto principal**. Sus resultados se clasifican como candidatos contextuales y requieren revisión.

### Nivel D — concepto semántico

Preguntas como “racismo”, “nación”, “familia” o “representación indígena” no pueden resolverse exhaustivamente mediante una bolsa de palabras. Requieren protocolo conceptual, muestreo/validación humana y, cuando corresponda, instrumentos semánticos separados.

## Protocolo mínimo para un reporte exhaustivo

1. Definir el concepto y el alcance temporal/documental.
2. Registrar consulta literal y variantes antes de interpretar resultados.
3. Ejecutar la consulta sobre el índice correspondiente y conservar la exportación.
4. Identificar aliases para evitar confundir reutilización técnica con evidencia independiente.
5. Revisar contra la página fuente cada coincidencia que sostendrá una afirmación.
6. Registrar falsos positivos y errores OCR observados.
7. Ejecutar búsquedas de control para variantes previsibles de OCR cuando sean materialmente relevantes.
8. Declarar la cobertura técnica efectiva y las retenciones vigentes.
9. Separar conteo de ocurrencias, páginas, objetos canónicos e identidades históricas.
10. Formular conclusiones solamente al nivel de evidencia realmente validado.

## Consulta negativa

La ausencia de hits no equivale automáticamente a ausencia histórica.

Una afirmación como “el término no aparece” exige como mínimo:

- corpus FTRL construido para todo el alcance declarado;
- validación de cardinalidad contra el manifiesto de páginas;
- índice FTS validado;
- variantes razonables cubiertas;
- evaluación del riesgo de falso negativo OCR;
- declaración de fuentes retenidas.

Por ello:

> `zero_hits != demonstrated_absence`

## Proximidad y sintaxis FTS5

SQLite FTS5 admite frases, operadores booleanos y `NEAR`. Ejemplos:

```text
"Benito Juárez"
masonería OR masón OR masones
NEAR(logia yorkino, 20)
```

Una consulta de proximidad mejora precisión contextual, pero sigue siendo recuperación, no clasificación histórica.

## Unidad de reporte

La unidad primaria es la **página canónica OCR**. Todo resultado debe conservar al menos:

- `page_id`;
- `canonical_viewer_key`;
- identidades históricas asociadas;
- generación;
- grado;
- posición fuente;
- snippet;
- `source_sha256`;
- `ocr_sha256`;
- confianza OCR cuando exista.

## Citabilidad

El snippet sirve para localización y análisis, no sustituye la inspección de la página fuente. Para una publicación, el reporte debería citar la identidad LTMD y la página/posición pertinente y conservar la versión de consulta, los hashes y la fecha de reconstrucción del corpus.

## Reproducibilidad

Una consulta reproducible se describe por:

```text
FTRL schema + OCR pipeline + source hashes + OCR hashes + index version + query + filters
```

Si alguno de estos componentes cambia, el resultado debe tratarse como una nueva ejecución, no como si fuera automáticamente idéntico al anterior.
