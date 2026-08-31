# LTMD-U1 — n-gramas y coocurrencias corpus-wide 0.1

Versiones: `LTMD_U1_NGRAMS_0.1` y `LTMD_U1_COOCCURRENCES_0.1`.

Esta capa deriva exclusivamente de `LTMD_U1_LEXICAL_POSITIONS_0.1`. **No vuelve a leer OCR, no vuelve a tokenizar y no vuelve a barrer FTS5.** Los términos, secuencias, pares y localizadores de página permanecen privados. GitHub publica sólo código, contratos, cardinalidades, hashes y estados epistemológicos no sustitutivos.

## Umbrales fijados antes de inspeccionar resultados

Los umbrales se fijaron antes de observar frases o pares concretos y no se ajustan retrospectivamente para favorecer resultados particulares.

**N-gramas privados:** bigramas con al menos 2 ocurrencias en 2 páginas; trigramas con al menos 3 ocurrencias en 2 páginas. **Elegibilidad pública:** bigramas ≥50 ocurrencias, ≥20 páginas y ≥10 objetos; trigramas ≥75 ocurrencias, ≥25 páginas y ≥10 objetos. La elegibilidad no autoriza por sí misma publicación literal: sólo satisface el umbral computacional de supresión.

**Coocurrencias:** pares no ordenados de términos distintos, dentro de la misma página y con distancia máxima de 5 tokens. Piso privado: ≥3 ocurrencias y ≥2 páginas. Elegibilidad pública: ≥75 ocurrencias, ≥25 páginas y ≥10 objetos, además de que cada término tenga dispersión propia de ≥20 páginas y ≥10 objetos.

## Materialización real U1

N-gramas: 13,184,868 instancias de bigrama y 13,104,392 de trigrama; 2,455,883 bigramas y 5,796,137 trigramas únicos antes del piso privado; 1,008,422 y 908,179 filas retenidas; 28,886 y 8,096 filas cumplen el umbral computacional de elegibilidad pública.

Coocurrencias: 64,208,256 parejas posicionales brutas; 10,426,262 pares únicos; 52,653,670 relaciones par-página; 2,540,432 filas retenidas y 81,451 filas que cumplen el umbral computacional de elegibilidad pública.

Los dos SQLite privados pasaron `quick_check=ok`, fueron comprimidos, archivados en la bóveda privada Analytics y **redescargados para verificar sus SHA-256**. Los resúmenes públicos no contienen rutas ni IDs de Drive.

## Estado científico

`text_verified=false`, `semantic_ready=false` y el estado por defecto es `exploratory_signal`. Frecuencia no equivale a significado; coocurrencia no equivale a relación semántica; una secuencia OCR no se convierte automáticamente en evidencia histórica validada.

## Reentrada

Con esta capa cerrada, la ruta canónica continúa con **reutilización/similitud transversal** antes de verticales adicionales, staging e interfaz.
