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

## Reutilización documental

LTMD modela explícitamente la dependencia entre objetos cuando existen páginas o fragmentos reutilizados, revisados, reemplazados o byte-idénticos. La independencia estadística o histórica no se presume a partir de diferencias de catálogo.

## Trazabilidad de cambios

Las transformaciones sustantivas deben poder seguirse desde la fuente hasta el producto derivado mediante Git, manifiestos, reportes de integridad, documentación de ola y, en releases, artefactos congelados. La ausencia de evidencia suficiente debe representarse como ausencia o incertidumbre, no como dato inferido silenciosamente.
