# LTMD-U1 W7 — criterios de aceptación para resolver fuentes retenidas

Estado: activo mientras exista al menos una identidad W7 con `ocr_source_admitted=0`.

## Identidades

- `H2014P5FCA`: un hueco interno aislado, página lógica 104 / `104.jpg`.
- `H2018P3FCA`.
- `H2018P4FCA`.
- `H2018P5FCA`.
- `H2018P6FCA`.

## Condición mínima para una resolución

Una identidad sólo puede cambiar de retenida a fuente admitida si la cadena de evidencia permite reconstruir el objeto sin imputación. La resolución debe producir simultáneamente:

1. identificación inequívoca de la fuente recuperada;
2. procedencia documentada y URL/identificador persistente o archivístico;
3. correspondencia determinista entre posiciones del visor LTMD y posiciones recuperadas;
4. hashes criptográficos de los bytes recuperados;
5. separación explícita entre activo institucional original, captura archivada y reproducción externa derivada;
6. actualización reproducible del gate de admisibilidad;
7. regeneración únicamente de las etapas downstream afectadas;
8. nueva versión del manifiesto de integridad antes de declarar cerrado el cambio.

## Evidencia suficiente posible

- bytes recuperados del URI institucional exacto;
- captura archivada verificable del mismo URI exacto;
- ruta alternativa derivable de código/metadatos institucionales, no por tanteo;
- reproducción oficial inequívocamente identificada como el mismo objeto, con alineación posicional demostrada.

## Evidencia insuficiente por sí sola

No autoriza una sustitución ninguno de los siguientes hechos aislados:

- mismo título o grado;
- mismo número de páginas;
- generación de catálogo próxima;
- coincidencia de primera edición o año;
- similitud visual;
- similitud OCR;
- reutilización textual exacta parcial;
- existencia de un libro 2019 del mismo grado;
- resultado negativo de un archivo web cuando su índice no respondió válidamente.

## Estado reproducible actual

Véase `docs/LTMD_U1_W7_WITHHELD_SOURCE_RESEARCH_0_3.md` y `data/catalog/ltmd_u1_w7_withheld_viewer_presence.md`. Las cinco identidades permanecen presentes en la configuración/visor institucional; ninguna tiene todavía evidencia suficiente para levantar su retención.
