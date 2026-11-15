# LTMD-U1 — revisión preliminar de tasas y no sustitución (15-nov-2026)

**Estado:** propuesta de control técnico-metodológico interno; no dictamen jurídico, no autorización de liberar nuevas celdas, no promoción semántica, no despliegue. Referencias: #171, #2, PR #179 y [matriz de derechos 0.2](RIGHTS_PUBLICATION_MATRIX_0_2.md).

## Clasificación de salidas

| Salida | Tratamiento |
| --- | --- |
| Conteos y tasas por generación/cohorte que ya derivan exclusivamente de agregados públicos versionados | Mantener como exploratorios bajo el semáforo verde interno, sin nueva publicación comercial. Documentar denominador, versión, cobertura y unidades. |
| Conteos de candidatos por grado/ola/lengua ya presentes en agregados públicos | Mantener límites existentes; no afirmar ausencia ni sumar categorías superpuestas. |
| Nuevos denominadores exactos por generación × grado × ola y sus tasas | Retener privados hasta revisión específica, incluyendo combinaciones de consultas, exportación y diferencia de totales. |
| Celdas con pocos objetos o sin coincidencias, tasas redondeadas, filtros acumulados | Examinar inferencia y composición; no asignar umbral universal sin evaluación de corpus. |
| OCR íntegro, libros, imágenes, fragmentos sustitutivos, reconstrucciones | No publicar conforme a la matriz vigente. |

Una tasa exacta y un numerador conocido pueden revelar el denominador: si c > 0 y r > 0, N = 1000c/r; el redondeo reduce precisión pero no garantiza protección. No introducir tasas nuevas mediante exportaciones, endpoints o filtros combinados mientras su divulgación no haya sido evaluada. Las técnicas de control estadístico se consideran por analogía metodológica, no como exigencia jurídica europea aplicable al corpus.

## Condiciones para avanzar

1. Inventariar los campos y combinaciones que el atlas/JSON/API permiten obtener; comparar con el conjunto de datos ya publicado y reconocer posibles inferencias por diferencia.
2. Determinar en entorno privado si las nuevas salidas pueden reconstruir información restringida o identificar indebidamente contenido, con revisión documental de derechos. Conservar el manifiesto completo fuera de Git, CI y del sitio.
3. Distinguir tasa de candidatos de prevalencia histórica; conservar null para denominadores no divulgados, no interpolar generaciones y no interpretar dominios operativos como asignaturas verificadas. La conciliación de 140/140 estratos con 267 celdas privadas fue documentada anteriormente; no se reejecutó aquí.
4. Verificar pruebas del PR #179 y revisar comparabilidad, luego decidir si corresponde integrar una versión exploratoria con los datos ya admitidos. No fusionar ni desplegar por esta nota.

## Robustez numérica

Se reemplazó la comparación que podía aceptar NaN en los tres validadores (preview, dataset y conciliación). Se exige math.isfinite antes de cotejar la tasa con el valor recomputado y se incorporaron nueve casos de regresión sintéticos (NaN, +inf, -inf para cada componente). No se declara éxito de CI hasta constatar el resultado. Ningún agregado real fue modificado.

## Fuentes consultadas

- Ley Federal del Derecho de Autor, texto con reforma DOF 14-05-2026: https://sc.inegi.org.mx/repositorioNormateca/LFDA.pdf (arts. 14, 107–110 y 148; distinción entre idea/datos, expresión, compilación y excepciones limitadas).
- Catálogo histórico CONALITEG: https://historico.conaliteg.gob.mx/ (acceso público no equivale a licencia de redistribución).
- Eurostat, Statistical confidentiality: https://ec.europa.eu/eurostat/en/web/main/about-us/statistical-confidentiality (supresión, redondeo e intervalos como referencias técnicas, no garantía de no reconstrucción).

La política de #2 permanece abierta. No se presume autorización por silencio institucional. No se aprueba un nuevo producto, suscripción, gasto, despliegue ni modificación de licencias.
