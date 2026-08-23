# LTMD — procedencia OCR de la Full-Text Research Layer

Versión: `LTMD_FTRL_PROVENANCE_0.1`.

## Principio

FTRL no acepta como texto de investigación una transcripción desligada de su activo fuente. Cada registro OCR debe poder remontarse a un JPEG fuente admitido y verificado criptográficamente.

## Cadena mínima

```text
viewer_key
→ source_asset_url
→ source_sha256 esperado
→ bytes recuperados
→ source_sha256 observado
→ Tesseract + versión + idioma + PSM
→ ocr_text_raw
→ ocr_sha256
→ normalización de búsqueda
→ search_text_sha256
→ SQLite FTS5
```

Si el hash observado del activo fuente no coincide con el manifiesto, el pipeline se detiene para esa ejecución. No se “acepta por similitud” una página diferente.

## Texto OCR bruto

`ocr_text_raw` es la salida TXT producida por el motor OCR fijado para la ejecución. No se corrigen silenciosamente nombres, fechas, ortografía ni puntuación.

El hash:

```text
SHA256(UTF-8(ocr_text_raw))
```

se conserva como `ocr_sha256`.

## Texto normalizado

`search_text` existe únicamente para mejorar recuperación. No reemplaza el OCR bruto y posee su propio `search_text_sha256`.

Toda transformación debe ser explícita, pequeña y versionada.

## Confianza

La confianza media se calcula sobre tokens de nivel palabra (`level=5`) con confianza no negativa en la salida TSV de Tesseract. Es una métrica operativa; no es una probabilidad calibrada de exactitud histórica.

## Alias y dependencia documental

Cuando LTMD ya ha demostrado que una identidad histórica es un alias exacto de otra fuente canónica, FTRL no repite innecesariamente OCR de los mismos bytes. La base `identities` preserva la correspondencia histórica con el objeto canónico.

Por ello deben distinguirse:

- **páginas OCR canónicas**;
- **identidades históricas cubiertas**;
- **ocurrencias textuales**.

No son el mismo denominador.

## Versiones que invalidan reutilización automática

Una transcripción anterior no se reutiliza con `--resume` si cambia cualquiera de los siguientes elementos:

- `source_sha256`;
- `pipeline_version`;
- versión de Tesseract;
- idioma;
- PSM.

Esto impide mezclar silenciosamente OCR producido bajo configuraciones distintas.

## Artefactos locales y artefactos públicos

Los artefactos que contienen texto fuente extenso se consideran locales/reconstruibles por defecto:

```text
local/ftrl/*.jsonl
local/ftrl/*.sqlite
local/ftrl/**/assets/*
```

El repositorio público conserva código, metadatos, hashes, esquemas y documentación. Publicar posteriormente una transcripción completa requeriría una evaluación separada de derechos, finalidad, necesidad y condiciones de redistribución.

## Límite interpretativo

La cadena criptográfica demuestra qué bytes dieron origen a qué transcripción. No demuestra que el OCR sea lingüísticamente perfecto ni que un término recuperado tenga el significado histórico que se le atribuye.

> procedencia técnica fuerte ≠ validación semántica humana
