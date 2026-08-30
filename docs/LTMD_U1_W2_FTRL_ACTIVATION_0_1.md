# LTMD-U1 W2 — gate de activación FTRL 0.1

Fecha efectiva: **29 de agosto de 2026**.  
Rama de trabajo: `ftrl/w2-matematicas`.  
Base verificada de `main`: `a1f8c248966d5210860fce8651a9975a89560f9c`.

## Propósito

Este documento autoriza la reentrada controlada de W2 Matemáticas a la secuencia FTRL después del cierre de W11. La autorización abre ejecución reproducible; **no** constituye promoción anticipada del completion ledger, cierre archivístico ni validación semántica.

## Gate secuencial W11 → W2

El cierre canónico W11 quedó incorporado a `main` mediante el commit `a92f5e6e5dd06ec7be7e48bd847e8b5e0185a14d`. Después de ese cierre se verificaron satisfactoriamente los controles de `Scientific release preflight` y `build-ltmd-u1-evidence-integrity`. El commit automático posterior `a1f8c248966d5210860fce8651a9975a89560f9c` refrescó el ledger público de integridad y es la base de esta activación.

La rama `ftrl/w2-matematicas` parte exactamente de esa base. Por tanto, la precondición operativa que mantenía W2 cerrado después de W11 queda satisfecha.

## Denominador congelado de W2

- Universo histórico: **64 identidades**.
- Identidades fuente-admitidas: **60**.
- Retenciones activas: **4** (`H2018P3DMA`, `H2018P4DMA`, `H2018P5DMA`, `H2018P6DMA`).
- Aliases exact-byte documentados: **3**.
- Objetos canónicos que requieren cómputo: **57**.
- Páginas fuente canónicas técnicas: **11,945**.
- PAGESTRUCT 0.2: **11,945** páginas clasificadas.
- FRAGSEG 0.2: **10,145** páginas con ≥1 fragmento y **135,727** fragmentos técnicos.

La reconciliación de activos conserva **892 posiciones no resueltas**, todas dentro de los cuatro DMA 2018 retenidos. Ninguna de esas posiciones se imputa desde 2019.

## Estado de ciclo de vida al abrir FTRL

La activación parte del estado canónico vigente y debe conservarlo hasta que exista evidencia suficiente de cierre:

- 60 identidades W2: `ftrl_status=pending`;
- 4 DMA 2018: `ftrl_status=blocked_active_retention`;
- W2: `archival_status=not_started`;
- `text_verified=false`;
- `semantic_ready=false`.

No se permite promover esos estados únicamente por la existencia del OCR técnico 0.2, PAGESTRUCT 0.2, FRAGSEG 0.2 o este documento de gate.

## Contrato de ejecución FTRL

La corrida FTRL W2 debe cumplir simultáneamente las siguientes condiciones:

1. La matriz de cómputo debe contener exactamente los **57 objetos canónicos** y excluir los cuatro DMA 2018 y los tres aliases de recomputación.
2. Cada página procesada debe provenir del manifiesto reconciliado W2 y conservar verificación SHA-256 de la fuente efectiva.
3. Los tres aliases sólo pueden heredar cobertura después de comprobar la relación exact-byte ya registrada; mantienen identidad documental independiente.
4. La evidencia pública debe ser estrictamente `text-free`: métricas, hashes, conteos, estados y procedencia, sin OCR íntegro, snippets ni texto normalizado.
5. Los productos textuales/restringidos deben empaquetarse y cifrarse para el handoff privado conforme al canon de preservación vigente.
6. La validación global debe ser exhaustiva sobre el denominador admitido: **60 identidades = 57 canónicos computados + 3 aliases exactos**; los cuatro DMA 2018 permanecen fuera y explícitamente retenidos.
7. La promoción del completion ledger sólo puede ocurrir después de dos pruebas independientes: `computationally_validated=true` y preservación privada persistente verificada por relectura/checksum.
8. Ningún resultado FTRL puede activar por inferencia `text_verified` o `semantic_ready`.

## Criterio de cierre futuro

W2 podrá promoverse a cierre FTRL únicamente cuando el repositorio pueda demostrar, con artefactos reproducibles y evidencia archivística persistente, que las 60 identidades admitidas están cubiertas sin gaps internos no explicados y que los cuatro DMA 2018 siguen correctamente representados como retenciones activas.

Hasta entonces, este documento sólo cambia el estado operativo de **cerrado por secuencia** a **habilitado para ejecución FTRL**.
