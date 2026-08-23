# Procedencia y trazabilidad

**Libro de Texto Mexicano Digital (LTMD)** adopta una cadena de procedencia explícita para que cada resultado pueda interpretarse de acuerdo con la evidencia que lo sustenta.

## Cadena de procedencia

```text
catálogo / visor institucional
        ↓
identidad documental
        ↓
resolución de activos
        ↓
hash SHA-256 y verificación
        ↓
OCR temporal
        ↓
PAGESTRUCT
        ↓
FRAGSEG
        ↓
derivados computacionales
        ↓
validación humana, cuando corresponda
        ↓
análisis histórico
```

## Principios

- La identidad documental no se fusiona por similitud de título, año, grado o contenido.
- Un alias o relación de fuente debe apoyarse en evidencia verificable; cuando se utiliza identidad byte a byte, se conserva la prueba criptográfica correspondiente.
- Los activos fuente de terceros no se convierten por defecto en contenido redistribuible del repositorio.
- OCR, segmentación, clasificación y validación humana son capas distintas.
- Las excepciones de routing, huecos, fallos de fuente y ambigüedades permanecen visibles.
- Una release conserva el estado metodológico y científico de su fecha; el avance posterior de `main` no modifica retrospectivamente ese corte.

## Identificadores y evidencia

Los artefactos técnicos deben conservar, cuando aplique, `book_id`, `viewer_key`, ruta o identificador de origen, hashes, fecha o corte de adquisición, versión del pipeline y relaciones documentales. Los scripts y manifiestos son parte de la evidencia reproducible.

## Fuentes archivadas

Una captura de un archivo web no sustituye automáticamente a la fuente institucional ausente. Para que una representación archivada pueda considerarse candidata de recuperación técnica debe conservar, como mínimo:

- la URL institucional original exacta y la posición documental a la que corresponde;
- el servicio o archivo de preservación utilizado y el timestamp de captura;
- la URL de replay o identificador equivalente;
- el código de respuesta, tipo de contenido y tamaño observado;
- el digest proporcionado por el archivo, cuando exista, y su verificación contra el cuerpo recuperado;
- un SHA-256 calculado por LTMD sobre el cuerpo recuperado temporalmente;
- la versión del procedimiento que realizó la recuperación y la decisión de admisibilidad resultante.

La existencia de metadata CDX, Memento u otro índice de archivo sólo demuestra una captura registrada; no demuestra por sí sola que el cuerpo sea correcto, completo o único. Si distintas capturas verificables de una misma posición producen cuerpos diferentes, la recuperación se considera ambigua y no se promueve automáticamente. La ausencia de captura en un sondeo acotado se registra como resultado negativo de ese sondeo, no como prueba de inexistencia universal.

Los cuerpos archivados se usan temporalmente para verificación y procesamiento cuando la política de derechos lo permite; no se incorporan a Git por defecto.

## Reutilización documental

LTMD modela explícitamente la dependencia entre objetos cuando existen páginas o fragmentos reutilizados, revisados, reemplazados o byte-idénticos. La independencia estadística o histórica no se presume a partir de diferencias de catálogo.

## Trazabilidad de cambios

Las transformaciones sustantivas deben poder seguirse desde la fuente hasta el producto derivado mediante Git, manifiestos, reportes de integridad, documentación de ola y, en releases, artefactos congelados. La ausencia de evidencia suficiente debe representarse como ausencia o incertidumbre, no como dato inferido silenciosamente.
