# LTMD — política de recuperación de matrices GitHub Actions 0.1

LTMD ejecuta ingestiones grandes mediante matrices por viewer/contenido canónico. Durante W2 Matemáticas se observó que GitHub Actions puede mostrar el workflow padre como `queued` aun después de que todos los shards de datos hayan terminado y publicado artifacts, y puede retrasar la instanciación del job `combine`.

## Regla

Una anomalía de orquestación **no autoriza a recomputar automáticamente** OCR, SHA, PAGESTRUCT o FRAGSEG que ya hayan terminado correctamente.

Antes de cualquier cancelación o recovery se exige:

1. contar exactamente los jobs de datos esperados;
2. demostrar que cada shard está `completed/success`;
3. demostrar la cardinalidad exacta de artifacts esperados;
4. comprobar si `combine` ya fue instanciado;
5. sólo si el parent shell permanece atascado y `combine` no puede ejecutarse, cerrar administrativamente el shell;
6. descargar los artifacts existentes y ejecutar únicamente el combinador;
7. conservar cualquier recovery como una operación de infraestructura, no como un nuevo experimento analítico.

## W2 OCR como caso de prueba

En OCR 0.2 de Matemáticas se produjeron 57/57 artifacts canónicos. El guardrail se negó repetidamente a cancelar mientras detectó shards activos. Al concluir el último shard, GitHub finalmente instanció `combine` como job 59 (`gate + 57 OCR + combine`), y el combine terminó correctamente. Por tanto, **no se utilizó el recovery preparado** y no se repitió ninguna página OCR.

## Despacho entre capas

Para evitar depender de pushes realizados por `github-actions[bot]`, las fases posteriores pueden despacharse explícitamente mediante `gh workflow run`, siempre después de que el artefacto final de la fase anterior haya sido validado y publicado.

La secuencia W2 0.2 queda:

`OCR combine → PAGESTRUCT → FRAGSEG → tablero + informe de cierre → checkpoint de integridad`.

## Alcance científico

Esta política regula únicamente orquestación/reintentos. No cambia algoritmos, parámetros, hashes, unidades documentales, criterios de cobertura ni reglas de inferencia.