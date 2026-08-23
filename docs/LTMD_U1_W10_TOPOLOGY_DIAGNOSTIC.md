# LTMD-U1 W10 — incidente de topología resuelto

Estado: **resuelto el 23 de agosto de 2026**.

## Síntoma observado

La primera ejecución diagnóstica del builder terminó antes de publicar la topología con:

```text
W10 topology produced zero canonical pages
```

## Causa

`is_canonical_processing_object` se construía internamente como entero `1`, pero el conjunto de objetos canónicos se filtraba posteriormente comparándolo con la cadena `'1'` antes de serializar a CSV. Esa incompatibilidad de tipos vaciaba artificialmente el conjunto canónico; no reflejaba ausencia de fuentes ni un problema documental del corpus.

## Corrección y verificación

La comparación fue corregida en el commit `0b2572365545ad05f17d911f6253c785b94ac7ad`. La ejecución posterior publicó correctamente `LTMD_U1_W10_PROCESSING_TOPOLOGY_0.1` con **69/69 identidades históricas preservadas**, **68/69 fuentes admitidas**, **1/69 retenida**, **68 objetos canónicos directos**, **0 aliases byte-exactos** y **11,937 páginas fuente canónicas**.

El incidente se conserva como trazabilidad de QA. Los productos vigentes son `docs/LTMD_U1_W10_PROCESSING_TOPOLOGY.md` y sus CSV asociados; este documento no representa el estado operativo actual de W10.
