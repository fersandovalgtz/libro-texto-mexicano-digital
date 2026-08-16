# LTMD-U1 W3 — arquitectura de ejecución 0.1

W3 contiene 130 visores y 23,894 posiciones declaradas. La experiencia de W2 muestra que el aislamiento por viewer es científicamente útil, pero instalar dependencias pesadas en 130 runners separados introduce sobrecarga innecesaria. Este documento fija una arquitectura de ejecución que conserva trazabilidad por viewer sin confundir aislamiento documental con unidad física de job.

## Principio

La **unidad documental** sigue siendo el viewer/libro. La **unidad de ejecución** puede ser un batch reproducible que procese varios viewers secuencialmente bajo el mismo entorno, siempre que cada viewer produzca artefactos separados y pueda invalidarse/reintentarse de manera identificable.

## Capa de activos

La auditoría de activos no requiere Tesseract. Puede mantenerse altamente paralela por viewer o batch porque sólo solicita bytes, calcula SHA-256 y descarta imágenes.

Contrato obligatorio:

- usar `ag_clave` institucional de `claves.json`;
- conservar `viewer_ui=standard_x_js|horizontal_x_horizontal_js`;
- un CSV por viewer;
- 404 final y 404 interno permanecen estados distintos;
- ningún JPEG fuente se persiste.

## OCR/PAGESTRUCT/FRAGSEG

Después de resolver activos y aliases, la ejecución pesada deberá preferir los **14 batches deterministas** ya congelados, o sub-batches derivados de ellos sin mezclar generaciones.

Dentro de cada runner:

1. instalar Tesseract español una sola vez;
2. iterar únicamente los contenidos canónicos asignados al batch;
3. reconstruir una página a la vez;
4. verificar SHA-256 antes de OCR;
5. eliminar la imagen inmediatamente después del procesamiento;
6. emitir un artefacto independiente por viewer;
7. fallar el batch si cualquier viewer presenta una violación de procedencia; el recovery puede volver a ejecutar sólo ese batch.

La agregación final sigue exigiendo cardinalidad exacta por viewer y por página. Agrupar cómputo no agrupa evidencia histórica.

## Paralelismo

El plan base usa 14 batches con techo de 2,500 posiciones declaradas y sin mezcla de generaciones. Se puede ejecutar varios batches en paralelo, pero el grado de paralelismo es una decisión de infraestructura, no un parámetro analítico.

## Deduplicación previa

Antes de OCR se debe ejecutar:

`asset audit → reconciliación → exact-alias audit → canonical compute set`

Sólo los contenidos canónicos reciben OCR/PAGESTRUCT/FRAGSEG. Los aliases heredan cobertura efectiva únicamente después de materializar el canónico.

## Reintentos y carreras

W2 mostró que GitHub Actions puede terminar todos los matrix shards y retrasar la instanciación de `combine`. Para W3:

- los shards/batches publican artifacts retenidos temporalmente;
- el combinador exige la cardinalidad exacta esperada;
- no se reejecuta OCR válido por una carrera de orquestación;
- si el parent run queda atascado, se verifica primero que todos los jobs de datos estén terminales en success y después se recuperan los artifacts existentes;
- los despachos entre capas deben ser explícitos, no depender de pushes del bot.

## Límite científico

Esta optimización reduce tiempo de infraestructura. No modifica OCR, PAGESTRUCT, FRAGSEG, denominadores, aliases, reglas de procedencia ni criterios semánticos. No autoriza a transferir SEMB 0.3 a Español/Lengua.
