# Estrategia de publicación científica — LTMD 0.1

Fecha: 2026-08-15

## Decisión editorial de principio

El proyecto no debe forzar un único artículo a cargar simultáneamente con construcción de corpus, auditoría OCR, segmentación, fracaso de SEMB 0.2, validación humana futura y argumento histórico longitudinal. La estrategia recomendada es separar **infraestructura/método** de **resultado histórico sustantivo**.

## Producto A — artículo de método / recurso digital

### Título provisional

**Libro de Texto Mexicano Digital: construcción, trazabilidad y validación de un corpus histórico-computacional de libros escolares mexicanos**

### Puede avanzarse antes de la referencia humana

Sí. Su contribución principal no depende de afirmar transformaciones semánticas históricas definitivas.

### Núcleo publicable

- selección de cuatro objetos piloto y distinción generación/edición;
- reconstrucción de la arquitectura de CONALITEG;
- auditoría de 759 activos reales;
- OCR adaptativo y control de calidad;
- PAGESTRUCT;
- FRAGSEG y 9,594 unidades reproducibles;
- procedencia por IDs/hashes;
- minimización de redistribución por derechos;
- RULEA/SEMB como demostración de arquitectura analítica;
- documentación transparente del fracaso de cobertura de SEMB 0.2;
- diseño preregistrado de SEMB 0.3;
- manifiesto de integridad y workflows reproducibles.

### Aporte

Un modelo replicable de edición histórico-digital y análisis computacional de libros de texto en el que la reproducibilidad no depende de redistribuir el corpus fuente completo.

### Resultado negativo valioso

La tasa de incertidumbre de SEMB 0.2 y su stress sintético deben reportarse como resultado metodológico negativo: una validación sintética demasiado estrecha puede aprobar un clasificador que no transporta al lenguaje histórico real. Este resultado justifica el stage-gate humano posterior.

## Producto B — artículo histórico-educativo

### Título provisional

**Continuidad, ruptura y sensibilidad metodológica en la acción pedagógica de los libros mexicanos de Ciencias Naturales de quinto grado, 1972–2014**

### Condición de salida

Sólo después de validar y aplicar SEMB 0.3 conforme al protocolo bloqueado.

### Aporte

Interpretar longitudinalmente las acciones pedagógicas y posiciones del alumno, articulando historia curricular, historia editorial y evidencia computacional validada.

## Producto C — dataset / release científica

Una release estable de GitHub + Zenodo podrá acompañar el Producto A o B cuando:

- se decida licencia del código y derivados;
- el inventario bibliográfico esté cerrado para el piloto;
- los artefactos críticos tengan hashes finales;
- se documente qué archivos se excluyen por derechos;
- se prepare `CITATION.cff`, changelog, versión semántica y manifiesto de reproducibilidad.

La release no necesita incluir OCR completo ni imágenes CONALITEG para ser científicamente útil.

## Producto D — expansión longitudinal

Después del piloto validado, escalar por bloques comparables antes de mezclar disciplinas:

1. Ciencias Naturales, grados 4º y 6º en las mismas generaciones;
2. conjunto 4º–6º para modelar continuidad vertical del área;
3. Matemáticas como segunda familia disciplinar;
4. Español/Lengua como contraste de régimen pedagógico;
5. Ciencias Sociales/Historia/Geografía, cuidando cambios de estructura disciplinar;
6. libros integrados de primeros grados como corpus metodológicamente distinto.

## Regla contra salami slicing

Separar productos sólo cuando cada uno tenga una pregunta y contribución propias. El artículo de método no debe duplicar tablas históricas finales; el artículo histórico no debe repetir exhaustivamente detalles de ingeniería ya publicados, sino citarlos y resumirlos.

## Prioridad actual

1. cerrar documentación histórica y de método;
2. preparar Producto A hasta estado de borrador completo;
3. no avanzar la narrativa histórica final del Producto B antes de SEMB 0.3;
4. preparar inventario de expansión sin ejecutar todavía clasificación semántica masiva.
