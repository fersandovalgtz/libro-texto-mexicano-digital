# LTMD U1-W8 — congelamiento operativo de la cohorte Artes

**Corte:** 2026-08-17  
**Ola:** `U1-W8`  
**Dominio operativo:** `artes`  
**Estado del documento:** congelamiento documental previo al procesamiento técnico

## 1. Propósito

Este documento congela la cohorte histórica y las reglas de procesamiento para `U1-W8` antes de cualquier ampliación de cobertura técnica. El congelamiento es operativo y documental: no constituye validación semántica, no establece equivalencia histórica entre objetos y no modifica por sí mismo la cobertura efectiva de U1.

La ola queda delimitada por las 20 identidades ya registradas en `data/catalog/ltmd_u1_wave_queue.csv`. Todas conservan `needs_domain_validation=True` y `needs_semantic_reference=True`. El procesamiento técnico puede avanzar bajo el estado general `WAITING_HUMAN_REFERENCE`, pero ninguna salida de esta ola debe presentarse como interpretación sustantiva validada de los libros.

## 2. Cohorte congelada: 20 identidades históricas

1. `H2008P3AR`
2. `H2008P4AR`
3. `H2008P5AR`
4. `H2008P6AR`
5. `H2010P3AR`
6. `H2010P4AR`
7. `H2010P5AR`
8. `H2010P6AR`
9. `H2011P3AR`
10. `H2011P4AR`
11. `H2011P5AR`
12. `H2011P6CI337`
13. `H2014P4ARA`
14. `H2014P5ARA`
15. `H2014P6ARA`
16. `H2018P3AR`
17. `H2018P4AR`
18. `H2018P5AR`
19. `H2018P6AR`
20. `H2019P3AR`

### Nota de identidad sobre `H2011P6CI337`

La identidad se conserva exactamente como está registrada en el catálogo maestro. Aunque el identificador contiene la secuencia `CI`, el título canónico y la asignación de la cola la sitúan en `artes` / Educación Artística. No se corrige, renombra ni reasigna a partir de la apariencia del identificador. Cualquier revisión futura deberá partir de evidencia documental explícita y dejar trazabilidad de una eventual corrección.

## 3. Estado al congelamiento

- Identidades históricas de W8: **20/20 congeladas**.
- Acción prevista en la cola: `process` para las 20 identidades.
- Alias aceptados al congelamiento: **0**.
- Identidades técnicamente incorporadas por este documento: **0**.
- Validación semántica humana aportada por este documento: **0**.
- Cobertura técnica efectiva de U1 al iniciar W8: **329/542 (60.70%)**.
- Objetos canónicos de procesamiento al iniciar W8: **298/542 (54.98%)**.

Las cifras anteriores permanecen sin cambio hasta que cada identidad satisfaga los gates técnicos y documentales aplicables. Una identidad retenida por fuente no se contabiliza como cobertura efectiva sólo por pertenecer a la ola.

## 4. Protocolo `source-first`

W8 reutiliza la arquitectura epistemológica y operativa consolidada en las olas anteriores. El orden de las operaciones es deliberado: primero se establece la fuente y su trazabilidad; después se producen derivados técnicos. No se utilizará OCR, similitud visual, título, año, grado, cardinalidad o cercanía temporal para suplir una fuente que no haya sido admitida documentalmente.

### G0 — congelamiento de cohorte

- fijar las 20 identidades históricas;
- preservar `book_id`, `viewer_key`, título y demás metadatos ya observados;
- impedir altas o bajas silenciosas durante la ejecución;
- registrar explícitamente cualquier discrepancia descubierta posteriormente.

### G1 — reconocimiento de fuente oficial

Para cada identidad se debe localizar y registrar el viewer y/o la fuente institucional observada, sin construir direcciones por analogía cuando no hayan sido efectivamente servidas o documentadas. La existencia de una ficha, viewer o configuración no equivale por sí sola a disponibilidad del árbol de activos.

### G2 — manifiesto exacto de fuente

Para cada posición realmente recuperada deben preservarse, según corresponda:

- identidad histórica y `viewer_key`;
- posición lógica o técnica observada;
- endpoint efectivamente consultado;
- respuesta/estado observado;
- tamaño de objeto;
- SHA-256 del objeto recuperado;
- tipo de medio y metadatos técnicos pertinentes.

Los manifiestos deben describir hechos observados, no completar huecos mediante patrones inferidos.

### G3 — completitud, cardinalidad y excepciones

Se debe contrastar la secuencia realmente servida con la cardinalidad esperada del viewer/configuración cuando ésta exista. Cualquier hueco se conserva como excepción trazable. No se imputa una página ausente, no se sustituye por una copia externa sin procedimiento documental explícito y no se declara completa una identidad incompleta.

### G4 — OCR y estructura por página

Sólo las fuentes admitidas pueden alimentar OCR u otros derivados textuales. Debe conservarse la relación determinista entre cada salida y su posición/fuente. La ausencia de texto OCR en una página no elimina la página del objeto documental.

### G5 — FRAGSEG

La segmentación técnica se ejecuta sobre derivados admitidos y conserva la dependencia hacia la página y la fuente. Los fragmentos son unidades computacionales; no equivalen automáticamente a unidades semánticas o históricas.

### G6 — análisis de reutilización y dependencia documental

La similitud no crea alias. Una posible reutilización técnica entre identidades requiere evidencia inequívoca de dependencia documental; la identidad de bytes y sus hashes constituye la evidencia técnica más fuerte cuando procede. Aun cuando un mismo contenido pueda procesarse una sola vez, todas las identidades históricas deben continuar representadas en la vista de objetos y su relación de dependencia debe quedar explícita.

No se aceptan alias sólo por:

- título semejante o idéntico;
- mismo grado o materia;
- año/generación próximos;
- igual número de páginas;
- similitud OCR, perceptual o visual;
- coincidencia parcial de páginas.

### G7 — cierre de ola

El cierre técnico de W8 debe producir como mínimo:

- balance por identidad histórica;
- identidades con fuente admitida;
- identidades retenidas por fuente, si existen;
- cardinalidad y verificación de hashes;
- cobertura OCR;
- producción FRAGSEG;
- dependencias/reutilizaciones demostradas;
- actualización explícita de `ltmd_u1_coverage.md`, README y documentación de estado.

Si sólo una subcohorte resulta fuente-admitida, el cierre debe denominarse exactamente como tal y las retenciones deben permanecer visibles; no se presentará como `20/20` técnico salvo evidencia suficiente.

## 5. Política de fuentes retenidas

Una identidad cuyo viewer/configuración sea conocido pero cuya fuente no pueda reconstruirse de forma completa y reproducible se mantiene como `source-retained` o equivalente. El hueco es un resultado de investigación y forma parte de la trazabilidad de LTMD.

Una fuente externa puede registrarse como pista o candidato de investigación sin convertirse automáticamente en fuente canónica. Para promoverla se requiere un expediente reproducible que establezca procedencia, características técnicas, correspondencia con el objeto histórico y límites de la inferencia.

## 6. Regla de no interpretación sustantiva

W8 es una expansión técnica del corpus. `needs_domain_validation=True` y `needs_semantic_reference=True` continúan activos para las 20 identidades. Ningún conteo de páginas, OCR, fragmentos, hashes o coincidencias debe redactarse como conclusión acerca de currículo, pedagogía, discurso, estética, ideología, autoría, edición o cambio histórico sin la fase humana/documental correspondiente.

## 7. Criterio de avance

El siguiente paso autorizado es el reconocimiento reproducible de fuentes de las 20 identidades, seguido de manifiestos y derivados para aquellas que superen los gates. Hasta que exista evidencia técnica incorporada, **W8 no aumenta la cobertura de U1**, que permanece en **329/542**.
