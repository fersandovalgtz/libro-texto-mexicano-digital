# Contexto histórico-curricular del piloto — versión 0.2

Fecha: 2026-08-15

Esta versión sustituye **para análisis futuro** a `CURRICULAR_CONTEXT.md`, que se conserva como registro histórico. La regla nueva es distinguir de forma explícita entre **reforma curricular documentada**, **generación editorial del catálogo**, **edición bibliográfica del ejemplar** e **hipótesis analítica**.

## 1972 / libro superior de la reforma setentera

La reforma de primaria de 1972 reorganizó el plan en siete áreas: Lenguaje, Matemáticas, Ciencias Naturales, Ciencias Sociales, Educación Física, Actividades Artísticas y Actividades Tecnológicas. Una reproducción digital de consulta del plan SEP de 1972 describe unidades de aprendizaje como “lecciones abiertas”, organización cíclica e integración interdisciplinaria; entre las actividades integradas enumera observación, clasificación, registro de información, experimentación, formulación de soluciones y comprobaciones. Esa copia no está alojada en un repositorio oficial y por ello se usa como **fuente primaria de consulta pendiente de cotejo institucional**, no como edición crítica definitiva.

La historiografía especializada permite respaldar con mayor seguridad el contexto: Estrada Rebull (2021) reconstruye que la reforma de Ciencias Naturales fue diseñada por un equipo liderado por científicos mexicanos, coordinado por Juan Manuel Gutiérrez-Vázquez, y que los libros fueron el principal vehículo de introducción de la reforma. La autora documenta asimismo la importancia de observación y experimentación y la larga vigencia de los libros de los grados superiores.

El marco jurídico posterior inmediato se consolida en la Ley Federal de Educación de 1973. Este marco ayuda a contextualizar la reforma educativa echeverrista, pero no se usa como evidencia directa del contenido del libro.

**Hipótesis histórica precomputacional:** el libro asociado a este ciclo debería contener una presencia sustantiva de operaciones de observación, experimentación, comparación, explicación y resolución de problemas. Esta expectativa no constituye un resultado y no podrá usarse para modificar clasificadores.

**Estado bibliográfico del objeto LTMD-CN5-G1972:** `catalog_generation=1972`; `edition_year` permanece vacío. La auditoría automatizada del front matter detecta marcador de edición y copyright 1972, pero no un año explícito de edición que justifique poblar `edition_year`.

## 1988 / generación editorial con continuidad curricular por demostrar

CONALITEG reconoce 1988 como generación propia en su Catálogo Histórico. La propia institución documenta además una campaña de obras plásticas comisionadas en 1988 y utilizadas entre 1988 y 1992 en diversos Libros de Texto Gratuitos. Esto prueba una **renovación editorial/visual**, no una reforma curricular de Ciencias Naturales.

El ejemplar de quinto auditado contiene copyright SEP 1977 e ISBN 968-29-0758-6. Esos metadatos hacen metodológicamente incorrecto asignar `edition_year=1988` por inferencia. La continuidad curricular con la reforma setentera es plausible y coincide con la historiografía sobre la larga vida de los libros de Ciencias Naturales de 4º–6º, pero debe tratarse como hipótesis documental mientras no se localice normativa o documentación editorial específica de 1988 para esta asignatura/grado.

**Hipótesis histórica precomputacional:** si el corte 1988 es fundamentalmente editorial y el contenido curricular continúa la familia setentera, las diferencias 1972→1988 deberían ser menores que las asociadas con el ciclo de reforma de los noventa. Esta expectativa no puede utilizarse para elegir parámetros ni descartar resultados discordantes.

**Estado bibliográfico del objeto LTMD-CN5-G1988:** `catalog_generation=1988`; `copyright_year=1977`; ISBN 968-29-0758-6; `edition_year` vacío.

## 1993 / reforma normativa, libro de quinto editado en 1998

El Acuerdo 181, publicado el 27 de agosto de 1993, estableció un nuevo plan y programas de estudio para primaria. Entre sus propósitos se encuentran el desarrollo de habilidades intelectuales, búsqueda y selección de información, aprendizaje permanente, independencia e iniciativa en cuestiones prácticas. La implantación de los nuevos programas y libros fue gradual.

Para el objeto concreto del piloto, la página legal verificada demuestra que el libro etiquetado por CONALITEG dentro de la generación 1993 es **primera edición 1998**, ISBN 970-18-1599-8. Por tanto, el proyecto utilizará expresiones como “generación 1993 / edición 1998” y nunca “edición 1993”.

**Hipótesis histórica precomputacional:** cabe esperar una reconfiguración de la organización del conocimiento y de los vínculos entre ciencia, vida cotidiana, salud y ambiente. La existencia y magnitud de esa reconfiguración deben demostrarse en el libro y no inferirse del Acuerdo 181.

## 2014 / tercera edición revisada en el ciclo RIEB

El Acuerdo 540 generalizó para el ciclo 2010–2011 los programas de segundo y quinto grados en el marco de la Reforma Integral de la Educación Básica. El programa de Ciencias Naturales vinculado a ese acuerdo plantea formación científica básica, indagación sistemática, preguntas sobre fenómenos, resolución de situaciones problemáticas, toma de decisiones y participación en salud y ambiente. El Acuerdo 592 articuló posteriormente la Educación Básica dentro del enfoque competencial de la RIEB.

La página legal del objeto del piloto confirma: primera edición 2010, segunda edición 2011, **tercera edición revisada 2014**, D.R. SEP 2014 e ISBN 978-607-514-722-2.

**Hipótesis histórica precomputacional:** el material puede mostrar mayor explicitación de proyectos, trabajo colectivo, decisiones informadas, salud, ambiente y participación. El análisis debe distinguir entre lenguaje normativo de competencias y acciones pedagógicas efectivamente solicitadas al alumno.

## Ejes comparativos permitidos

La comparación longitudinal separará cuatro procesos que pueden o no coincidir:

1. **cambio curricular documentado** — modificaciones normativas de propósitos, contenidos y organización;
2. **cambio editorial/documental** — generaciones, diseño, paratextos, organización visual y reimpresiones;
3. **cambio pedagógico textual** — acciones solicitadas y posiciones atribuidas al alumno;
4. **cambio bibliográfico del objeto** — edición, reimpresión, copyright e ISBN del ejemplar realmente procesado.

No se asumirá una evolución lineal entre 1972, 1988, 1993/1998 y 2014.

## Jerarquía de evidencia

1. página legal o paratexto del ejemplar procesado;
2. norma o publicación institucional contemporánea al periodo;
3. fuente primaria reproducida fuera de repositorio institucional, claramente marcada como tal;
4. historiografía especializada revisada por pares;
5. inferencia analítica explícitamente declarada.

Una fuente de nivel inferior no puede contradecir silenciosamente a una de nivel superior. Las discrepancias deben conservarse y discutirse.

## Fuentes centrales

- CONALITEG, Catálogo Histórico: https://historico.conaliteg.gob.mx/
- CONALITEG, *Pintando la Educación*: https://www.conaliteg.gob.mx/pintando_la_educacion.php
- Cámara de Diputados, debate/proyecto de Ley Federal de Educación, 18-09-1973: https://cronica.diputados.gob.mx/Debates/49/1er/Ord/19730918.html
- Estrada Rebull, M. del M. (2021). DOI: https://doi.org/10.29351/rmhe.v9i18.353
- Acuerdo 181: https://sidof.segob.gob.mx/notas/docFuente/4778272
- Acuerdo 540: https://www.dof.gob.mx/nota_detalle_popup.php?codigo=5156090
- Programa de Ciencias Naturales asociado al Acuerdo 540: https://www.dof.gob.mx/nota_detalle_popup.php?codigo=5156094
- Acuerdo 592: https://www.dof.gob.mx/nota_detalle_popup.php?codigo=5205518

Para estatus de cada fuente y pendientes de localización, véase `docs/PRIMARY_SOURCE_REGISTER_0_1.md`.
