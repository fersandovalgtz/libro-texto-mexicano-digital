# LTMD-U1 W11 — sondeo archivístico de URLs fuente retenidas

Versión: `LTMD_U1_W11_WAYBACK_PROBE_0.1`.

- Huecos consultados: **5/5**.
- Huecos con ≥1 captura CDX 200: **0/5**.
- Registros de captura únicos por digest/consulta: **0**.
- Consultas fallidas tras reintentos: **4**.

## Resultado por posición

| viewer | página | índice | capturas | primera | última | roles |
|---|---:|---:|---:|---|---|---|
| `H2014P1EAM` | 41 | 41 | 0 | — | — | — |
| `H2014P2EAM` | 13 | 13 | 0 | — | — | — |
| `H2014P2EAM` | 17 | 17 | 0 | — | — | — |
| `H2014P3COL` | 130 | 130 | 0 | — | — | — |
| `H2014P3MOR` | 15 | 15 | 0 | — | — | — |

## Consultas no concluyentes
- `H2014P2EAM` página 13, `exact_https` — `CDX probe failed for https://historico.conaliteg.gob.mx/c/H2014P2EAM/013.jpg: URLError: <urlopen error [Errno 111] Connection refused>`.
- `H2014P2EAM` página 17, `exact_https` — `CDX probe failed for https://historico.conaliteg.gob.mx/c/H2014P2EAM/017.jpg: URLError: <urlopen error [Errno 111] Connection refused>`.
- `H2014P3COL` página 130, `http_transport_variant` — `CDX probe failed for http://historico.conaliteg.gob.mx/c/H2014P3COL/130.jpg: URLError: <urlopen error [Errno 111] Connection refused>`.
- `H2014P3MOR` página 15, `exact_https` — `CDX probe failed for https://historico.conaliteg.gob.mx/c/H2014P3MOR/015.jpg: URLError: <urlopen error [Errno 111] Connection refused>`.

## Regla

Una captura CDX sólo demuestra que Internet Archive indexó una respuesta 200 para la misma ruta institucional (o su variante de transporte HTTP). No demuestra todavía que el cuerpo archivado sea un JPEG válido ni autoriza su incorporación. Cualquier candidato deberá descargarse de forma temporal desde la captura identificada, verificarse por tipo/tamaño/SHA-256 y conservar timestamp, URL original y procedencia archivística. No se consultan páginas de otros libros como sustitutos.

La ausencia de captura en este sondeo se conserva como resultado negativo acotado; no prueba que nunca haya existido otra copia fuera de los índices consultados.
