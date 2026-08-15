# Diagnóstico sintético de cabezales semánticos SEMB 0.3

Versión: `SEMB03_LABEL_HEADS_SYNTH_DEV_0.1`. Diseño: tres folds, reteniendo un ejemplo por categoría en cada fold.

> No es validación humana. Evalúa separabilidad del espacio semántico y calidad relativa de los anchors sobre casos sintéticos claros.

## Acciones
- Anchors congelados SEMB 0.2, top-1: **75.0%**.
- Centroides aprendidos con 2 ejemplos/categoría, CV: **64.6%**.
- Híbrido anchor+centroide, CV: **79.2%**.

## Posiciones
- Anchors congelados SEMB 0.2, top-1: **63.0%**.
- Centroides aprendidos con 2 ejemplos/categoría, CV: **63.0%**.
- Híbrido anchor+centroide, CV: **77.8%**.

## Uso
Si los centroides superan claramente los anchors, la representación E5 conserva señal útil y SEMB 0.3 debe considerar cabezales supervisados/prototípicos. Si no mejoran, conviene evaluar una representación/modelo distinto en el conjunto humano de desarrollo.
