# LTMD-U1 — Corpus Analytics Manifest 0.1

Versión: **LTMD_U1_CORPUS_ANALYTICS_MANIFEST_0.1**

## Función

Este manifiesto fija el universo computacional que puede utilizar LTMD Analytics antes del staging. No es un catálogo bibliográfico nuevo ni una capa semántica: es un contrato reproducible de denominadores, cobertura técnica, dimensiones operacionales y calidad OCR agregada.

Se construye desde tres fuentes canónicas: el Índice Universal U1 privado, el tablero público de cobertura U1 y el registro público de retenciones/excepciones. Si esas fuentes no reconcilian, el constructor falla.

## Universo fijado

El corte 0.1 exige:

- 542 identidades históricas U1;
- 524 identidades con cobertura técnica efectiva;
- 492 objetos canónicos de procesamiento;
- 86,549 páginas indexadas y 86,549 filas FTS5;
- residual 18 = 13 `active_retention` + 5 `final_exception`;
- 0 identidades con validación semántica humana incorporada.

La diferencia entre 542 identidades históricas y 492 objetos canónicos preserva relaciones técnicas demostradas y excepciones; no autoriza aliases heurísticos.

## Dimensiones

El manifiesto calcula directamente desde el Índice Universal denominadores por generación, grado y ola operacional, además de todas las celdas no vacías generación × grado × ola. El corte real contiene **267 celdas no vacías**. Cada celda registra únicamente páginas y objetos canónicos únicos.

La taxonomía `wave` sigue siendo logística/operacional y no se convierte en ontología curricular. Estos denominadores permiten que una consulta de Analytics use exactamente el mismo subuniverso en numerador y denominador.

## Cobertura técnica

El constructor no copia a ciegas las cifras del tablero. Verifica que la suma de las once olas coincida con los totales de identidades planificadas, cobertura efectiva, objetos canónicos y residual; que el residual global sea igual al registro de fuentes retenidas; que `active_retention + final_exception` sea exactamente el residual; que su distribución por ola coincida; y que los 492 objetos canónicos del tablero coincidan con el Índice Universal.

## Calidad OCR

El manifiesto agrega `ocr_confidence_mean` a escala corpus. Esta cifra es una señal producida por el motor OCR y **no** es CER, WER, corrección humana ni `text_verified`.

La salida utiliza explícitamente:

`engine_confidence_only_not_CER_WER_or_human_text_verification`

El corte real tiene confianza disponible para 80,968 páginas y no disponible para 5,581.

## Estado epistemológico

El contrato mantiene:

```text
ocr_available = true
text_verified = false
corpus_ready_for_computational_retrieval = true
semantic_ready = false
default_result_state = exploratory_signal
human_validation_deferred_not_cancelled = true
```

Reglas obligatorias: `ocr_available != text_verified`; `corpus_ready != semantic_ready`; `search_hit != historical_claim`; `zero_hits != demonstrated_absence`.

## Privacidad y publicación

El manifiesto no incorpora OCR, `search_text`, snippets, `page_id`, claves de libro, URLs fuente, hashes de páginas/OCR ni paths privados. La copia integral del manifiesto de operación se preserva en el archivo privado de LTMD Analytics; GitHub conserva el constructor, el esquema y una huella/resumen agregado del corte.

El Índice Universal completo continúa privado y no debe publicarse.

## Integridad

El Corpus Analytics Manifest 0.1 se vincula al Índice Universal canónico mediante su SHA-256. Una reconstrucción contra otro índice debe fallar si se solicita el gate criptográfico y el hash no coincide.

## Secuencia canónica

Con este contrato cerrado, el siguiente frente es construir los derivados corpus-wide de **léxico, dispersión, n-gramas y coocurrencias**. La reutilización/similitud transversal y los verticales temáticos siguen después. Staging e interfaz permanecen downstream.
