# LTMD-U1 W2 — estado técnico de Matemáticas 0.1

Corte: 15 de agosto de 2026.  
Estado: **ingestión técnica activa; semántica no abierta**.

## Universo congelado

W2 contiene **64 visores** de Matemáticas dentro de LTMD-U1. `claves.json` declara **13,656 posiciones**. Los 64 visores comparten la arquitectura pública estándar `x.js → claves.json → ag_clave/ag_pages`.

## Resolución de activos

La auditoría SHA-256 por 64 shards produjo:

- 59 visores `direct_asset_ready`;
- 1 visor con dos huecos internos: `H2008P4MA276`;
- 4 visores DMA 2018 con ruta declarada no servida: `H2018P3DMA`, `H2018P4DMA`, `H2018P5DMA`, `H2018P6DMA`.

Los dos huecos de `H2008P4MA276` fueron recuperados de forma unívoca mediante alineamiento de vecinos byte-idénticos, offset fijo y cero discrepancias. El manifiesto reconciliado conserva la anomalía original y añade la fuente efectiva.

Resultado reconciliado:

- **60/64 identidades con activos efectivamente resueltos**;
- **4/64 excepciones de routing aún no resueltas**;
- **2 JPEG recuperados criptográficamente**;
- ningún visor 2018 DMA recibe crédito por mera similitud de título, grado o cardinalidad.

## Dependencia documental y cómputo único

Entre los visores completos se demostraron tres aliases de contenido exacto, página por página, con SHA-256 y byte-size:

- `H1982P4MA388` → canónico `H1972P4MA083`, 258 JPEG;
- `H1982P5MA394` → canónico `H1972P5MA089`, 304 JPEG;
- `H1982P6MA399` → canónico `H1972P6MA094`, 194 JPEG.

Por tanto, las 60 identidades efectivamente resueltas corresponden a **57 contenidos canónicos que requieren cómputo**. Los tres aliases conservan identidad documental propia, pero no se vuelven a OCRizar ni segmentar.

## DMA 2018

La comparación de configuración 2018↔2019 mostró el mismo `ag_pages` por grado, pero `ag_clave` distinto. Esa evidencia es insuficiente para declarar identidad documental o byte-alias. Los cuatro DMA 2018 permanecen explícitamente fuera del cómputo mientras no exista una prueba documental o criptográfica suficiente.

## Pipeline 0.2

La ejecución W2 se versiona como 0.2 porque la auditoría empírica refutó el supuesto preparatorio de 64/64 directos.

`57 canónicos → OCR temporal SHA-verificado → PAGESTRUCT → FRAGSEG → 3 aliases heredan sólo cobertura efectiva`

Los cuatro DMA 2018 permanecen fuera de esa cadena. SEMB 0.3 de Ciencias Naturales no se aplica a Matemáticas y W2 no produce todavía inferencia pedagógica/histórica.

## Regla epistemológica

- `asset_ready` no equivale a `ocr_ready`;
- `ocr_ready` no equivale a `fragseg_ready`;
- `fragseg_ready` no equivale a `semantic_ready`;
- un alias exacto permite reutilizar cómputo, pero no elimina la identidad de catálogo;
- una recuperación puntual de página no demuestra identidad bibliográfica entre libros completos.
