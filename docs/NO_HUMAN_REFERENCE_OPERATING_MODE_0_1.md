# LTMD — modo operativo sin referencia humana 0.1

Fecha de activación: **2026-08-16**.

## Propósito

El proyecto *Libro de Texto Mexicano Digital* continuará temporalmente sin una referencia humana disponible para validación textual o semántica. Esta condición se trata como una restricción epistemológica explícita, no como un bloqueo general del proyecto.

## Capas autorizadas

Pueden seguir desarrollándose y publicándose como productos técnicos reproducibles:

- descubrimiento y auditoría de visores;
- procedencia de activos y verificación SHA-256/tamaño;
- resolución de routing y aliases byte-exactos;
- manifiestos de páginas y preservación de huecos digitales sin renumeración;
- OCR técnico y métricas de cobertura;
- PAGESTRUCT;
- FRAGSEG;
- hashes de contenido y reutilización textual exacta;
- deduplicación no destructiva y vistas occurrence/content-unit/revision;
- dependencia documental y grafos de reutilización;
- metadatos bibliográficos y contexto curricular sustentado en fuentes;
- integridad, versionado, reproducibilidad, documentación y empaquetado de releases;
- análisis descriptivos puramente técnicos que no requieran verdad terreno semántica.

## Capas estacionadas

Permanecen explícitamente no validadas o cerradas mientras no exista referencia humana:

- CER/WER contra transcripción humana de referencia;
- desempeño de clasificadores pedagógicos/semánticos contra gold standard;
- confiabilidad intercodificador;
- consenso humano;
- model lock y locked validation de SEMB03;
- afirmaciones históricas primarias que dependan de categorías semánticas automáticas no validadas.

`SEMB03` conserva por tanto el estado epistemológico `WAITING_HUMAN_REFERENCE`; ese estado no debe interpretarse como que el resto del corpus deba detenerse.

## Uso permitido de señales automáticas no validadas

Reglas léxicas, embeddings, clusters, tópicos u otros métodos no supervisados pueden desarrollarse únicamente como **exploración técnica/provisional**. Sus resultados deben etiquetarse de manera visible como no validados y no pueden sustituir una referencia humana ni convertirse en el fundamento exclusivo de una conclusión histórica fuerte.

## Regla para FRAGSEG y PAGESTRUCT

PAGESTRUCT y FRAGSEG son capas técnicas. Sus categorías describen estructura o candidatos de segmentación; no constituyen por sí mismas clases pedagógicas verdaderas. `short_residual_candidate`, `question_candidate`, `instruction_candidate` y categorías análogas deben conservar el sufijo/carácter de *candidate* cuando no hayan sido validadas.

## Regla para reutilización exacta

La igualdad de `text_sha256` demuestra únicamente igualdad del texto OCR normalizado reconstruido por la tubería de segmentación correspondiente. Es evidencia reproducible de reutilización textual exacta dentro de esa representación técnica, pero **no demuestra por sí sola equivalencia bibliográfica, curricular, pedagógica o semántica**.

La arquitectura debe conservar simultáneamente:

1. **object view** — cada identidad de catálogo/documento permanece identificable;
2. **unique-content view** — contenidos técnicos idénticos pueden agruparse por hash;
3. **revision/dependence view** — se documentan relaciones de reutilización, reemplazo, alias o revisión sin deduplicación destructiva.

## Política de publicación

Mientras este modo esté activo:

- los artículos de método/recurso pueden continuar;
- los resultados técnicos de cobertura, procedencia, reutilización y dependencia documental pueden reportarse con sus límites;
- los resultados históricos semánticos deben presentarse como exploratorios o reservarse hasta validación suficiente;
- ningún informe debe sugerir que la confianza interna de Tesseract equivale a exactitud textual validada.

## Criterio de salida

Este modo sólo se modifica cuando exista una referencia humana genuina suficientemente documentada para la tarea correspondiente. La llegada de referencia humana no invalida las capas técnicas producidas durante este periodo; simplemente habilita nuevas capas de evaluación y aumenta el nivel de inferencia admisible.
