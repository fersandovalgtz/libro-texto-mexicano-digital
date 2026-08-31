# LTMD Analytics — ruta canónica corpus-wide 0.1

Versión: **LTMD_ANALYTICS_CORPUS_WIDE_CANON_0.1**  
Fecha de decisión: **2026-08-30**

## 1. Decisión

LTMD no pasa todavía de la API temática actual al staging/producto visual como siguiente gran frente. Antes, la infraestructura FTRL-U1 debe convertirse en una capa analítica transversal sobre el universo ya procesado.

El orden canónico es:

`FTRL preservado → Índice Universal U1 → FTS5 corpus-wide → motor Analytics genérico → dimensiones/manifest → léxico y reutilización → verticales → staging → interfaz`

El staging 0.1 ya desarrollado permanece válido como paquete técnico, pero queda subordinado a esta secuencia.

## 2. Universo de referencia

El universo técnico reconstruido y reconciliado para esta fase es:

- 288 bases SQLite privadas;
- 86,549 páginas únicas;
- 492 objetos canónicos;
- 0 conflictos de identidad/hash en la reconstrucción usada por el estudio de lenguas indígenas 0.2.

Estos números son gates de construcción del Índice Universal U1. Una ejecución que no reproduzca las cardinalidades esperadas debe fallar; no se corrige mediante imputación silenciosa.

## 3. Índice Universal LTMD-U1 0.1

`scripts/build_u1_universal_index.py` fusiona las tablas privadas `pages` de FTRL en una sola base SQLite privada con:

- una fila por `page_id` único;
- identidad de visor y objeto canónico;
- generación, grado, ola, título y posición;
- hashes técnicos y métricas OCR disponibles;
- `search_text` privado;
- tabla FTS5 `pages_fts` con `unicode61 remove_diacritics 2`;
- índices B-tree para generación, grado, ola, objeto y hashes;
- manifiesto JSON text-free con cardinalidades, hashes de insumo, dimensiones y SHA-256 del índice privado.

El archivo SQLite universal **no se publica**. El manifiesto sí puede auditarse públicamente porque no contiene OCR, `page_id`, URL fuente ni rutas privadas.

## 4. Deduplificación y conflicto

La reconciliación conserva la misma frontera usada para reproducir el universo privado 0.2. Un `page_id` repetido puede deduplicarse sólo cuando coincide su fingerprint técnico compuesto por:

- objeto canónico;
- SHA-256 fuente;
- SHA-256 OCR;
- generación;
- índice de página;
- página de visor.

Una discrepancia en ese fingerprint es conflicto y bloquea la construcción.

## 5. Búsqueda full-text

FTS5 es una capa de recuperación técnica. En consecuencia:

- una coincidencia es `computational_candidate`;
- el ranking de búsqueda no constituye relevancia histórica validada;
- la ausencia de hits no demuestra ausencia histórica;
- no se publican snippets extensos ni OCR íntegro;
- filtros y agregados posteriores deben conservar procedencia y estado epistemológico.

## 6. Fases posteriores

### 6.1 Motor Analytics genérico

El motor debe dejar de depender de ledgers temáticos. Consultará el Índice Universal y podrá combinar términos/expresiones con filtros por generación, grado, ola y objeto, calculando páginas y libros únicos.

### 6.2 Dimensiones maestras

Se construirá `Corpus Analytics Manifest` con denominadores técnicamente defendibles. La taxonomía de ola sigue siendo operacional y no se presenta automáticamente como ontología curricular.

### 6.3 Léxico global

Se producirán frecuencias, dispersión, n-gramas y coocurrencias como derivados no sustitutivos. Los rankings deberán controlar longitud y dispersión bibliográfica.

### 6.4 Reutilización y similitud

Analytics deberá distinguir:

- identidad/reutilización exacta demostrada;
- similitud computacional candidata.

No se convertirá similitud textual en identidad documental.

### 6.5 Verticales

Lenguas indígenas permanece como primer vertical. Después se incorporarán verticales exploratorios sobre interculturalidad, género/familia, ciudadanía/derechos, ambiente, trabajo/economía, ruralidad/migración, nación/identidad, discapacidad/inclusión, territorio y tecnología/ciencia.

## 7. Privacidad y derechos

La separación permanece:

- **privado:** OCR, `search_text`, índice FTS5 completo, rutas internas y materiales fuente;
- **público:** código, schemas, hashes, cardinalidades, métricas, agregados y derivados no sustitutivos admitidos por la gobernanza del proyecto.

El Índice Universal no convierte el corpus fuente en un producto redistribuible.

## 8. Estado científico

Durante toda esta fase:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `computational_candidate != semantic_ready`;
- `text_verified = false` salvo evidencia humana específica;
- `semantic_ready = false` para resultados corpus-wide no validados.

La revisión humana permanece diferida, no eliminada.

## 9. Gate para staging

El staging corpus-wide sólo se activa después de:

1. construir y verificar el Índice Universal real;
2. comprobar 86,549 páginas / 492 objetos / 0 conflictos;
3. ejecutar consultas FTS5 corpus-wide sobre el índice privado;
4. fijar el contrato del motor Analytics genérico;
5. publicar un manifiesto text-free del corte usado por producto.

Hasta entonces, el paquete de staging existente se conserva como infraestructura disponible, no como siguiente fase principal.
