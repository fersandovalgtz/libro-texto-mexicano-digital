# Revisión del protocolo de consultas FTRL — 24 de agosto de 2026

## Alcance

Esta nota registra una revisión prospectiva del conjunto de consultas FTRL después de la primera corrida integral validada de W5 Historia (`run 32743689286`). La revisión afecta únicamente las ejecuciones futuras y no modifica retrospectivamente la preregistración, los manifiestos ni la evidencia producida por aquella corrida.

## Separación entre registro histórico y protocolo activo

El archivo `data/research/ltmd_ftrl_w5_preregistered_queries.csv` se conserva sin cambios como parte del registro reproducible de la corrida integral ya ejecutada. No debe interpretarse como el conjunto activo para nuevos análisis.

A partir de esta revisión, el conjunto activo de W5 es `data/research/ltmd_ftrl_w5_active_queries.csv`. El control positivo utilizado en la corrida histórica queda retirado de nuevas ejecuciones, comparaciones e interpretación. Su presencia en artefactos o registros anteriores constituye únicamente procedencia de una ejecución ya realizada.

## Reglas de uso vigentes

1. Las consultas activas producen candidatos de recuperación, no afirmaciones históricas.
2. Todo candidato que vaya a utilizarse como evidencia debe verificarse contra la imagen fuente correspondiente.
3. La sensibilidad a variantes ortográficas u OCR se utiliza como control de recuperación y no sustituye la consulta primaria.
4. `zero_hits != demonstrated_absence`: una ausencia de coincidencias OCR/FTS exige revisar cobertura, calidad OCR, variantes y páginas fuente antes de cualquier inferencia.
5. El texto OCR íntegro, los snippets y la base SQLite continúan como productos locales reconstruibles y no se publican por defecto.

## Trazabilidad

Esta revisión no invalida la corrida integral W5 ni su registro permanente. Mantiene explícitamente dos objetos distintos:

- **preregistración histórica**: describe exactamente lo que se ejecutó y debe permanecer inmutable;
- **protocolo activo**: describe lo que podrá ejecutarse en trabajos posteriores.

La separación evita reescribir la historia del experimento y, al mismo tiempo, impide que un control retirado siga propagándose a análisis futuros.
