# FTRL LTMD-U1 — hoja de ruta de escalamiento 0.1

**Fecha:** 24 de agosto de 2026  
**Base metodológica:** W5 Historia validada integralmente  
**Objetivo:** escalar `LTMD_FTRL_0.1` desde W5 hacia LTMD-U1 sin perder trazabilidad, derechos, reproducibilidad ni separación entre procesamiento técnico e interpretación histórica.

## Principio rector

El éxito de W5 demuestra que el pipeline puede procesar una cohorte completa con verificación SHA-256, OCR por página, índice SQLite FTS5, manifiesto text-free y protocolo de consultas. No demuestra que todas las demás olas estén listas para ejecutarse sin revisión previa.

El escalamiento se gobierna por cuatro estados distintos:

- `source_ready`: existe una cohorte fuente-admitida explícita y trazable;
- `corpus_ready`: el pipeline técnico puede reconstruirse y validar cardinalidades;
- `ocr_available`: existe texto OCR generado por el pipeline;
- `semantic_ready`: existe validación humana suficiente para interpretación del constructo.

Estos estados no se colapsan entre sí.

## Orden de escalamiento recomendado

### Grupo A — olas técnicamente cerradas

Estas olas son las candidatas prioritarias para preparar inventario FTRL porque su cobertura técnica U1 está cerrada según el tablero vigente.

| Ola | Dominio | Cobertura técnica | Prioridad FTRL |
|---|---|---:|---|
| W1 | Ciencias Naturales | 40/40 | alta |
| W3 | Español / Lengua | 130/130 | alta |
| W4 | Ciencias Sociales | 14/14 | alta |
| W5 | Historia | 18/18 | validada integralmente |
| W6 | Geografía / Atlas | 42/42 | alta |
| W9 | Educación Física | 4/4 | alta |

Antes de OCR integral, cada ola debe producir su inventario canónico, manifiesto de activos, cardinalidad fuente reproducible y lista explícita de aliases o relaciones documentales. W5 funciona como patrón de aceptación, no como atajo para omitir esos gates.

### Grupo B — cohortes fuente-admitidas con identidades retenidas

Estas olas pueden escalarse sobre su cohorte admitida, pero la evidencia debe declarar explícitamente que no representa el universo nominal completo.

| Ola | Dominio | Cohorte admitida | Retenidas | Regla |
|---|---|---:|---:|---|
| W7 | Formación Cívica y Ética | 25/30 | 5 | procesar sólo cohorte admitida; no reinterpretar retenidas como ausencias |
| W8 | Artes | 16/20 | 4 | idem |
| W10 | Integrados / Multiarea | 68/69 | 1 | idem |
| W11 | Otros / No clasificados | 107/111 | 4 | idem |

Los manifiestos FTRL de estas olas deben incluir simultáneamente cardinalidad procesada y cardinalidad histórica nominal, con referencia al registro consolidado de fuentes retenidas.

### Grupo C — cobertura parcial no cerrada

| Ola | Dominio | Estado | Regla |
|---|---|---|---|
| W2 | Matemáticas | 60/64; 4 excepciones preservadas | no declarar cohorte integral; resolver o congelar formalmente las cuatro excepciones antes de cualquier afirmación de cobertura completa |

W2 puede utilizarse para pruebas técnicas parciales si el alcance se preregistra, pero no debe presentarse como un corpus FTRL integral de la ola mientras permanezcan las cuatro excepciones.

## Gate mínimo por ola

Ninguna nueva corrida integral debe aceptarse sin satisfacer, como mínimo, los siguientes controles:

1. inventario de identidades históricas congelado;
2. lista de objetos canónicos de procesamiento;
3. relación explícita de aliases, revisiones o reutilizaciones demostradas;
4. manifiesto de activos con SHA-256;
5. cardinalidad reproducible de páginas fuente;
6. cero páginas fuente con tamaño desconocido dentro de la cohorte admitida;
7. OCR reconstruible bajo `local/`;
8. SQLite y FTS5 con cardinalidad exactamente igual al corpus admitido;
9. `PRAGMA integrity_check = ok`;
10. artefacto público limitado a metadatos, hashes y agregados text-free;
11. registro separado de páginas con `zero_search_text`, baja confianza o anomalías OCR;
12. prohibición explícita de convertir hits de búsqueda en afirmaciones históricas sin verificación visual.

## Secuencia operativa

El orden recomendado para reducir riesgo es:

**W1 → W3 → W6 → W4 → W9 → W7 → W8 → W10 → W11 → W2**.

La secuencia privilegia primero cohortes técnicamente cerradas y suficientemente amplias para probar generalización; después incorpora olas con retenidas explícitas; W2 queda al final porque todavía conserva excepciones técnicas no resueltas.

No se fija aún un volumen total de páginas esperado para U1. Esa cifra deberá calcularse de manera reproducible a partir de los manifiestos canónicos de cada ola, evitando extrapolaciones o sumas manuales.

## Criterio de cierre de FTRL-U1

FTRL-U1 podrá declararse técnicamente cerrado cuando todas las olas tengan una cohorte explícitamente definida y cada cohorte haya pasado sus gates de integridad. El cierre podrá ser:

- **integral**, cuando una ola cubra todo su universo nominal;
- **fuente-admitido**, cuando existan retenidas documentadas que permanezcan fuera de procesamiento;
- **parcial**, cuando aún existan excepciones no congeladas metodológicamente.

La etiqueta de cierre deberá viajar con cualquier análisis derivado.

## Trabajo humano posterior

El escalamiento técnico no sustituye la validación semántica. Las consultas historiográficas, curriculares o discursivas deberán definir constructo, sensibilidad OCR, reglas de verificación visual y criterios de inclusión antes de interpretar patrones longitudinales.

W5 deja fijado el precedente metodológico: `corpus_ready != semantic_ready`, `ocr_available != text_verified`, `search_hit != historical_claim` y `zero_hits != demonstrated_absence`.
