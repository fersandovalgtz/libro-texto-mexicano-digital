# Auditoría de fuentes institucionales para contexto curricular

Fecha: **15 de agosto de 2026**.

## Objetivo

Separar tres cosas que no deben confundirse: generación del Catálogo Histórico, fecha bibliográfica del ejemplar y reforma curricular. La búsqueda se orientó primero a fuentes institucionales de SEP/CONALITEG/DOF.

## Hallazgo institucional sobre las “generaciones” editoriales

El Catálogo Histórico de CONALITEG presenta explícitamente botones de generación, entre ellos 1972, 1988, 1993 y 2014. Esto demuestra que `catalog_generation` es una clasificación institucional legítima del repositorio histórico.

Sin embargo, una comunicación oficial de CONALITEG sobre su aplicación digital describe además ciclos asociados a familias visuales/editoriales: “Héroes y Patria 1960-1973”, “Juguetes 1973-1988”, “Ilustradores 1982-1988”, “Pintores 1988-1993”, “1993-2008”, seguidos por generaciones 2008-2011, 2011-2014 y 2014-2019.

Consecuencia metodológica: **una frontera de generación de CONALITEG no debe tratarse automáticamente como frontera de reforma curricular**. En particular, 1988 puede capturar un corte editorial/visual institucional aunque la hipótesis curricular de continuidad o cambio deba demostrarse por programa, contenido y estructura del libro.

Fuentes institucionales:

- CONALITEG, *Catálogo histórico de libros de texto gratuitos 1960-2020*: https://historico.conaliteg.gob.mx/
- CONALITEG, “La aplicación Conaliteg Digital nos trae de regreso los libros que nos dieron la base de nuestra educación”, 13 de febrero de 2020: https://www.gob.mx/conaliteg/prensa/la-aplicacion-conaliteg-digital-nos-trae-de-regreso-los-libros-que-nos-dieron-la-base-de-nuestra-educacion
- CONALITEG, “Conoce el Catálogo Histórico de los Libros de Texto Gratuitos”, 23 de junio de 2019: https://www.gob.mx/conaliteg/articulos/conoce-el-catalogo-historico-de-los-libros-de-texto-gratuitos

## 1972 — estado de la fuente primaria

La búsqueda institucional realizada en esta fecha no localizó una copia digital oficial inequívoca del plan/programa de primaria de 1972 que permita reemplazar por completo la contextualización historiográfica actualmente utilizada. Por tanto:

- no se añade una afirmación normativa nueva sobre 1972;
- se conserva como fuente historiográfica principal la literatura especializada ya registrada;
- la etiqueta `catalog_generation=1972` no se convierte en `edition_year=1972`;
- el año bibliográfico del ejemplar permanece `unverified` mientras el front matter no presente un marcador explícito interpretable.

Esta ausencia se considera una **laguna documental**, no evidencia de inexistencia del plan.

## 1988 — interpretación prudente

La propia CONALITEG documenta una familia/ciclo “Pintores 1988-1993”. Esto fortalece la decisión de usar 1988 como punto comparativo sin presuponer que representa una reforma curricular equivalente a 1972 o 1993. El libro concreto deberá ser interrogado como objeto documental y no como sustituto automático de una reforma.

## 1993 y 2014

La matriz existente conserva prioridad en estas dos generaciones porque ya cuenta con normas del Diario Oficial/SEP y con metadatos bibliográficos verificados del ejemplar concreto. La auditoría presente no modifica esas fechas.

## Regla para futuras ampliaciones

Toda nueva afirmación de contexto se etiquetará mentalmente en uno de estos niveles de evidencia:

1. **objeto primario** — página legal, prólogo, índice o contenido del libro identificado;
2. **norma primaria** — plan, programa, acuerdo o documento oficial de SEP/DOF;
3. **fuente institucional retrospectiva** — CONALITEG/SEP explicando su propio catálogo o política;
4. **historiografía especializada** — interpretación académica con aparato crítico.

Las categorías pueden complementarse, pero no son intercambiables.
