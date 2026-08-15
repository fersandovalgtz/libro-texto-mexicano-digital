# SEMB 0.2 frente a batería sintética independiente

Versión: `SEMB02_SYNTH_STRESS_EVAL_0.1`. Batería: `SEMB03_SYNTH_STRESS_0.1`.

> Diagnóstico sintético: no sustituye referencia humana y no contiene texto del corpus histórico.

## Gate de acción
- n=105; balanced accuracy=0.526; sensibilidad=0.597; especificidad=0.455.
- Falsos positivos en negativos de estrés: 53.3%; falsos positivos que además superan buffer de certeza: 13.3%.
- En positivos, tasa de pérdida por gate: 40.3%; sin superar el buffer de certeza: 94.4%.

## Categorías
- Acciones: top-1=75.0%; inclusión de etiqueta esperada en salida final=54.2%; incertidumbre=95.8%.
- Posiciones: top-1=63.0%; inclusión de etiqueta esperada=70.4%; incertidumbre=51.9%.

## Interpretación permitida
La batería sirve para localizar fallos estructurales y construir casos de regresión antes de la referencia humana. No autoriza elegir parámetros por su efecto en diferencias históricas ni demuestra validez externa.
