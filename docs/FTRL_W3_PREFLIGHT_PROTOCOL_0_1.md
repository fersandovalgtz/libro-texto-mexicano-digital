# FTRL LTMD-U1 W3 Español/Lengua — protocolo de preflight 0.1

**Fecha:** 24 de agosto de 2026  
**Estado:** preparación técnica; no activa OCR FTRL integral  
**Autoridad superior:** `FTRL_U1_EXHAUSTIVE_EXECUTION_PROTOCOL_0_2.md`

## Propósito

Congelar y validar la topología de entrada de W3 antes de cualquier corrida FTRL. Este preflight reutiliza exclusivamente evidencia técnica ya versionada y no promueve resultados semánticos ni declara W3 como corpus FTRL terminado.

## Denominador y topología congelados

- 130 identidades documentales W3 (`operational_domain=espanol_lengua`).
- 114 objetos canónicos de procesamiento.
- 16 identidades cubiertas por relaciones técnicas demostradas: 8 aliases byte-exactos y 8 resoluciones de ruta 2018→2019 con coincidencia SHA-256 y tamaño por activo.
- 20,765 JPEG fuente canónicos con SHA-256 y tamaño conocidos.
- 109 posiciones terminales sintéticas en los objetos canónicos.
- 7 objetos canónicos con huecos internos explícitos; 8 posiciones internas no servidas en total.
- 0 identidades W3 en `active_retention` o `final_exception` del registro residual U1.

Los ocho huecos son posiciones de página documentadas en representaciones digitales por lo demás cubiertas; no se rellenan, sustituyen ni renumeran. Su existencia no autoriza inferir ausencia bibliográfica en la edición física.

## Evidencia OCR previa

Existe una capa OCR técnica anterior para los 114 objetos canónicos y 20,765 páginas, con verificación SHA-256 y cero páginas marcadas como `unresolved`. Esa capa funciona únicamente como **ancla técnica de cardinalidad y procedencia**. No equivale a una corrida FTRL validada y no permite promover `corpus_ready`, `text_verified` ni `semantic_ready`.

## Gates del preflight

El preflight debe fallar si cambia cualquiera de estos invariantes:

1. denominador W3 distinto de 130;
2. conjunto de identidades distinto del inventario maestro;
3. número de objetos canónicos distinto de 114;
4. número o mapeo de aliases distinto de 16;
5. manifiesto canónico distinto de 20,765 páginas;
6. fuente con tamaño no positivo o SHA-256 inválido;
7. más o menos de 8 huecos internos documentados;
8. una relación 2018→2019 sin resolución completa o sin igualdad de SHA-256/tamaño;
9. una identidad W3 apareciendo como retención/excepción global sin revisión explícita del protocolo;
10. cualquier intento de presentar el OCR previo como validación FTRL o semántica.

## Activación posterior

Mientras W1 permanezca como gate técnico activo, este protocolo sólo autoriza **preflight y normalización de inputs**. La corrida FTRL integral W3 requiere una activación posterior deliberada después del cierre técnico de W1 conforme a la secuencia logística vigente.

La preservación privada de cualquier futura corrida integral W3 deberá cumplir además `LTMD_PRIVATE_CORPUS_PRESERVATION_CANON_0_1.md` y conservar OCR/SQLite/QC completos en la bóveda privada de Google Drive.

## Separación epistemológica

`preflight_ready != corpus_ready`  
`prior_ocr_anchor != ftrl_validated`  
`ocr_available != text_verified`  
`corpus_ready != semantic_ready`  
`search_hit != historical_claim`
