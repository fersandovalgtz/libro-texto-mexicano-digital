# Figura — Pipeline y stage gates de LTMD 0.1

Esta figura es la fuente canónica en Mermaid para el diagrama metodológico del artículo. Puede exportarse posteriormente a SVG/PDF para la revista sin redibujar la lógica.

```mermaid
flowchart TD
    A[Catálogo Histórico CONALITEG] --> B[Descubrimiento de objeto y visor]
    B --> C[Inventario bibliográfico<br/>generación ≠ edición]
    B --> D[Reconstrucción del visor<br/>HTML → x.js → claves.json → JPEG]
    D --> E[Auditoría de activos y procedencia]
    E --> F[Copias temporales de página]
    F --> G[OCR adaptativo<br/>métricas, no redistribución íntegra]
    G --> H[PAGESTRUCT 0.2<br/>función documental]
    H --> I[FRAGSEG 0.2<br/>fragmentos + IDs + SHA-256]
    I --> J[RULEA 0.1]
    I --> K[SEMB 0.2 bloqueado]
    K --> L[Diagnóstico de cobertura<br/>99.49% incertidumbre]
    L --> M[Stress sintético independiente]
    M --> N[SEMB 0.3: muestra ciega 480]
    N --> O[320 development]
    N --> P[160 locked validation]
    N --> Q[120 doble codificación]
    Q --> R[Fiabilidad + adjudicación humana]
    R --> O
    O --> S[GroupKFold por page_id<br/>grid preregistrado]
    S --> T[Selección de candidato]
    T --> U[MODEL LOCK<br/>código + config + hashes]
    U --> P
    P --> V{Criterios preregistrados<br/>superados?}
    V -- no --> W[No producción histórica<br/>documentar fallo]
    V -- sí --> X[SEMB 0.3 productivo<br/>corpus congelado]
    X --> Y[Comparación longitudinal]
    J --> Y
    Y --> Z[Robusto vs sensible al método]

    I --> AA[FRAGTYPE 0.3 SHADOW]
    AA --> AB[5,037 → 7,429<br/>elegibles potenciales]
    AB --> AC[160 unidades breves<br/>validación suplementaria]
    AC --> X

    E --> AD[Manifiesto SHA-256]
    G --> AD
    I --> AD
    N --> AD
    U --> AD
```

## Lectura de la figura

La figura distingue tres ideas que deben conservarse en cualquier versión gráfica:

1. **procedencia y estructura preceden a la semántica**;
2. el fracaso de SEMB 0.2 no se borra: funciona como antecedente que justifica el nuevo stage gate humano;
3. los 160 casos de validación permanecen aislados hasta que existe un `MODEL LOCK`.

## Convenciones para versión editorial

- Las cajas de fuente/procedencia deben diferenciarse visualmente de las de inferencia semántica.
- El camino `no` de la validación debe permanecer visible; no dibujar un pipeline que presuponga éxito.
- `FRAGTYPE 0.3 SHADOW` se muestra como rama de corrección de constructo, no como reemplazo retroactivo de FRAGSEG 0.2.
- El manifiesto de integridad debe aparecer como capa transversal.
