# FTRL LTMD-U1 — hoja de ruta de escalamiento 0.1

> [!IMPORTANT]
> **Documento histórico, parcialmente sustituido.** Desde el 24 de agosto de 2026, el alcance y los criterios de cierre de FTRL-U1 se rigen por [`FTRL_U1_EXHAUSTIVE_EXECUTION_PROTOCOL_0_2.md`](FTRL_U1_EXHAUSTIVE_EXECUTION_PROTOCOL_0_2.md). En particular, cualquier formulación de este documento que permita un cierre `fuente-admitido` o parcial como cierre suficiente de una ola o del proyecto **queda anulada**: las 542 identidades permanecen en el denominador, las retenciones activas son trabajo obligatorio y sólo las excepciones técnicas finales documentadas pueden cerrar una identidad sin OCR.

**Fecha:** 24 de agosto de 2026  
**Base metodológica:** W5 Historia validada integralmente  
**Objetivo original:** escalar `LTMD_FTRL_0.1` desde W5 hacia LTMD-U1 sin perder trazabilidad, derechos, reproducibilidad ni separación entre procesamiento técnico e interpretación histórica.

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

Estas olas pueden avanzar computacionalmente sobre su cohorte admitida, pero **no pueden considerarse exhaustivamente cerradas** mientras conserven una retención activa. Las retenidas permanecen en el denominador y deben resolverse o alcanzar una excepción técnica final conforme al protocolo 0.2.

| Ola | Dominio | Cohorte actualmente admitida | Retenidas | Regla vigente |
|---|---|---:|---:|---|
| W7 | Formación Cívica y Ética | 25/30 | 5 | procesar la fuente disponible y mantener las 5 como deuda obligatoria |
| W8 | Artes | 16/20 | 4 | procesar la fuente disponible y mantener las 4 como deuda obligatoria |
| W10 | Integrados / Multiarea | 68/69 | 1 | la excepción final permanece en el denominador como cierre negativo documentado |
| W11 | Otros / No clasificados | 107/111 | 4 | las excepciones finales permanecen en el denominador como cierres negativos documentados |

Los manifiestos FTRL deben incluir simultáneamente cardinalidad procesada y cardinalidad histórica nominal, con referencia al registro consolidado de fuentes retenidas.

### Grupo C — cobertura parcial no cerrada

| Ola | Dominio | Estado | Regla vigente |
|---|---|---|---|
| W2 | Matemáticas | 60/64; 4 retenciones activas | procesar las 60 disponibles y mantener las cuatro restantes como trabajo obligatorio; no declarar cierre exhaustivo |

W2 puede utilizarse para pruebas técnicas parciales si el alcance se preregistra, pero no debe presentarse como un corpus FTRL integral de la ola mientras permanezcan las cuatro retenciones activas.

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

A estos gates se añade obligatoriamente el gate global de alcance 0.2: ninguna identidad puede desaparecer del denominador maestro.

## Secuencia operativa

El orden recomendado para reducir riesgo sigue siendo:

**W1 → W3 → W6 → W4 → W9 → W7 → W8 → W10 → W11 → W2**.

El orden es exclusivamente logístico. **No autoriza detener el proyecto antes de recorrer W1–W11 ni omitir las identidades retenidas.** Después de cada ola se continúa con la deuda restante hasta satisfacer el cierre global 542/542 del protocolo 0.2.

No se fija aún un volumen total de páginas esperado para U1. Esa cifra deberá calcularse de manera reproducible a partir de los manifiestos canónicos de todas las olas, evitando extrapolaciones o sumas manuales.

## Criterio de cierre de FTRL-U1 — sustituido

La formulación anterior que admitía cierres `integral`, `fuente-admitido` o `parcial` como categorías terminales queda sustituida. A partir de 0.2:

- una corrida sobre fuente admitida es un **avance computacional**, no cierre exhaustivo si hay retenciones activas;
- una ola sólo cierra exhaustivamente cuando todas sus identidades tienen cobertura FTRL demostrada o una excepción técnica final;
- FTRL-U1 sólo cierra cuando las 542 identidades tienen disposición final y no existe ninguna `active_retention`.

Véase el criterio normativo completo en [`FTRL_U1_EXHAUSTIVE_EXECUTION_PROTOCOL_0_2.md`](FTRL_U1_EXHAUSTIVE_EXECUTION_PROTOCOL_0_2.md).

## Trabajo humano posterior

El escalamiento técnico no sustituye la validación semántica. Las consultas historiográficas, curriculares o discursivas deberán definir constructo, sensibilidad OCR, reglas de verificación visual y criterios de inclusión antes de interpretar patrones longitudinales.

W5 deja fijado el precedente metodológico: `corpus_ready != semantic_ready`, `ocr_available != text_verified`, `search_hit != historical_claim` y `zero_hits != demonstrated_absence`.
