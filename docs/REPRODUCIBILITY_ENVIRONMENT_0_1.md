# Entorno de reproducibilidad — LTMD 0.1

Corte: **2026-08-15**  
Candidata: **v0.1.0-rc.1**

## Propósito

Este documento separa dependencias directas fijadas de dependencias proporcionadas por el runner. No pretende presentar como lock completo aquello que los workflows actuales todavía no fijan a nivel de versión de parche.

## Sistema operativo de referencia

Los workflows científicos principales se ejecutan sobre GitHub Actions con `ubuntu-24.04` o `ubuntu-latest`. Para la reproducción de la candidata se adopta **Ubuntu 24.04** como línea base de referencia.

## Python

Los pipelines técnicos de catálogo, procedencia, OCR, PAGESTRUCT y FRAGSEG usan predominantemente la biblioteca estándar de Python 3. La candidata **todavía no afirma un Python patch-level congelado** porque varios workflows invocan `python3` del runner sin `actions/setup-python` ni una versión explícita.

Esto no invalida los artefactos congelados —sus outputs están verificados por cardinalidad/hashes—, pero sí queda registrado como mejora obligatoria antes de una release estable si se desea reproducción binaria/runtimes más estricta.

## Dependencias Python directas

`requirements-release.txt` fija:

```text
sentence-transformers==5.6.1
```

Esta dependencia corresponde a SEMB 0.2. El modelo semántico se identifica como `intfloat/multilingual-e5-small` y el workflow congelado exige la revisión:

```text
fd1525a9fd15316a2d503bf26ab031a61d056e98
```

No se genera un lock transitivo artificial: las dependencias transitivas instaladas por `sentence-transformers` dependen del resolvedor de pip y deben congelarse explícitamente en una futura release estable si se requiere reconstrucción del entorno a nivel de wheel.

## OCR

El runtime OCR requiere:

```text
tesseract-ocr
tesseract-ocr-spa
```

El workflow SEMB 0.2 comprueba explícitamente `tesseract 5.3.4`. Los workflows masivos de Ola 2 instalan los mismos paquetes del sistema antes de reconstruir temporalmente cada imagen y verificarla por SHA-256.

## GitHub Actions

Acciones principales usadas en las cadenas congeladas:

- `actions/checkout@v4`
- `actions/upload-artifact@v4`
- `actions/download-artifact@v4`

La candidata conserva los YAML exactos en el repositorio y el manifiesto de integridad registra los workflows críticos que definen las capas cerradas.

## Fuente y privacidad

Las imágenes fuente se descargan sólo durante ejecución, se comprueban contra SHA-256 y se eliminan. No se requiere ni se espera que la release contenga JPEG/PDF fuente u OCR íntegro. Las carpetas `private/` y `data/work/` no deben estar versionadas.

## Nivel de reproducibilidad declarado para v0.1.0-rc.1

**Reproducibilidad de procedimiento y de artefactos derivados: alta.** Los scripts, inputs derivados, cardinalidades, hashes, workflows y controles se encuentran versionados.

**Reproducibilidad de entorno a nivel de patch/wheel: parcial.** Tesseract queda fijado en el flujo semántico; `sentence-transformers` queda fijado directamente; Python y dependencias transitivas todavía no están congelados completamente.

Esta diferencia debe mantenerse explícita en la release y no ocultarse detrás de la palabra “reproducible”.
