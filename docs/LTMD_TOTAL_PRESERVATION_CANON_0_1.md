# Canon de preservación total y continuidad LTMD — 0.1

**Fecha:** 24 de agosto de 2026  
**Estado:** normativo para todo el proyecto LTMD  
**Ámbito:** repositorio, corpus, evidencia computacional, metadatos operativos y continuidad entre sesiones  

## 1. Decisión canónica

Libro de Texto Mexicano Digital se conserva mediante una arquitectura de tres capas complementarias:

- **GitHub**: verdad versionada, reproducible y publicable del proyecto;
- **Google Drive privado**: archivo persistente integral de los bytes y evidencias que deban conservarse, incluidos productos restringidos;
- **Notion**: memoria humana de decisiones, procedimientos, estado y continuidad entre chats/sesiones.

Ninguna de las tres capas sustituye a las otras. El proyecto no debe depender de la memoria de una conversación ni de almacenamiento efímero de CI.

## 2. Regla de preservación total

Todo artefacto necesario para **comprender, reproducir, auditar, continuar o defender científicamente** LTMD debe tener una ubicación persistente y verificable en Google Drive, o —si el byte original no puede conservarse legalmente— un registro persistente que documente su identidad, procedencia, condición de acceso, razón de no copia y estrategia de recuperación.

La preservación total incluye, cuando existan:

1. snapshots completos del árbol versionado del repositorio en hitos sustantivos;
2. código, documentación, esquemas, contratos y protocolos;
3. inventarios de fuentes, manifiestos de páginas, hashes, topologías e identificadores;
4. fuentes descargadas legítimamente que puedan conservarse en privado;
5. OCR completo, SQLite/FTS5, QC detallado y productos derivados restringidos;
6. manifiestos de ejecución, preflights, cardinalidades, checksums y evidencia text-free;
7. paquetes cifrados y material necesario para recuperación bajo el canon de seguridad;
8. releases, tags y metadatos operativos de GitHub que no formen parte del árbol Git;
9. issues, pull requests, comentarios de control y decisiones técnicas relevantes;
10. metadatos y resúmenes/logs necesarios para auditar workflows y fallos;
11. documentación de derechos, excepciones, retenciones y resultados negativos;
12. auditorías de preservación y registros de transferencia/verificación a Drive.

## 3. Simbiosis GitHub ↔ Drive

GitHub debe permitir responder **qué versión, reglas y código produjeron un resultado**. Drive debe permitir responder **dónde están los bytes persistentes necesarios para recuperarlo o reproducirlo**.

Por tanto:

- un cambio sustantivo en `main` requiere un snapshot persistente de repositorio ligado al commit y SHA-256;
- una corrida computacional con productos restringidos requiere copia persistente en Drive antes de `archival_complete=yes`;
- los artefactos de GitHub Actions son handoffs temporales, nunca archivo definitivo;
- la copia en Drive no sustituye el historial Git;
- la existencia en GitHub no elimina la obligación archivística de Drive para hitos/evidencias relevantes.

## 4. Qué constituye un cambio sustantivo

Se considera sustantivo, como mínimo, cualquier cambio en:

- denominador documental o cobertura;
- manifiestos de fuente o cardinalidades;
- topología canónica/aliases;
- OCR, indexación, QC o criterios de validación;
- ledger FTRL-U1 y estados de ola;
- contratos metodológicos o epistemológicos;
- workflows de ejecución/preservación;
- políticas de derechos y publicación;
- arquitectura de almacenamiento;
- releases, hitos científicos o cierres archivísticos.

Los commits triviales no requieren necesariamente un snapshot independiente si un snapshot posterior preserva el árbol y Git conserva el historial intermedio.

## 5. Productos restringidos y cierre archivístico

Se mantiene la distinción:

`computationally_validated != archival_complete`

Una corrida alcanza `archival_complete=yes` sólo cuando:

1. terminó con éxito y pasó sus gates técnicos;
2. el paquete o archivos esperados fueron copiados a Drive privado;
3. la copia está ligada inequívocamente a run y commit;
4. tamaño y SHA-256 fueron verificados en destino, preferentemente mediante re-descarga;
5. el destino restringido permanece privado;
6. las claves necesarias para recuperación permanecen fuera del repositorio público;
7. existe evidencia pública text-free del cierre.

El canon específico para corpus restringido continúa en `docs/LTMD_PRIVATE_CORPUS_PRESERVATION_CANON_0_1.md`.

## 6. Fuentes y derechos

La regla de preservación total no amplía derechos de copia o redistribución.

Si un original puede conservarse legítimamente en privado, se preserva en Drive. Si no puede conservarse, se preserva un registro negativo suficiente para mantenerlo dentro del universo documental y permitir trazabilidad futura. Nunca se fabrica una fuente, OCR o equivalencia para cubrir una ausencia.

## 7. GitHub: superficie pública reproducible

GitHub conserva y versiona:

- código y tests;
- documentación y protocolos;
- inventarios y metadatos publicables;
- hashes y cardinalidades;
- evidencia text-free;
- ledger y estados operativos no sensibles;
- contratos de preservación;
- referencias lógicas a Drive, sin IDs privados, claves o credenciales.

Nunca se publican en GitHub OCR íntegro restringido, SQLite con texto completo, QC detallado sensible, claves privadas o identificadores privados de Drive.

## 8. Drive: bóveda persistente integral

La raíz canónica es:

`LTMD-U1 — corpus FTRL privado`

Debe contener:

- `00_CANON_y_manifiestos/`
  - cánones/auditoría;
  - snapshots del repositorio;
  - exportaciones de metadatos operativos GitHub;
- `W1` a `W11` con corridas y productos persistentes;
- paquetes cifrados, checksums y evidencia de recuperación cuando corresponda.

La bóveda debe mantenerse privada salvo materiales que expresamente puedan compartirse.

## 9. Notion: continuidad humana

La página canónica de continuidad es **“LTMD — procedimiento canónico de preservación GitHub ↔ Google Drive”**, alojada bajo el Portafolio de macrodatos educativos del Sistema Maestro.

Notion registra:

- decisiones permanentes;
- estado resumido y próximos gates;
- reglas de cierre;
- referencias a runs/commits/issues;
- cambios de arquitectura;
- cómo retomar el proyecto en un chat nuevo.

Notion nunca es la única copia del corpus, código o evidencia.

## 10. Continuidad entre chats

Al retomar LTMD en una sesión nueva se consulta, en este orden:

1. Notion: canon y estado humano vigente;
2. GitHub `main`: ledger, protocolos, contracts, workflows e issue #15;
3. Drive: auditoría y archivos persistentes;
4. runs/artifacts activos como estado transitorio.

Si una conversación contradice una fuente versionada/auditada posterior, prevalece la evidencia posterior.

## 11. Universo exhaustivo y límites epistémicos

El universo LTMD-U1 permanece en 542 identidades. W1–W11 son particiones logísticas.

Se mantienen:

- `topology_ready != corpus_ready`;
- `preflight_ready != ftrl_validated`;
- `corpus_ready != semantic_ready`;
- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`;
- `computationally_validated != archival_complete`.

Preservar un corpus no implica validarlo semánticamente.

## 12. Procedimiento operativo mínimo

Después de cada cambio sustantivo:

1. pasar CI;
2. fusionar a `main`;
3. registrar commit/PR/issue pertinentes;
4. generar snapshot de repositorio;
5. copiarlo a Drive;
6. verificar tamaño, SHA-256 y privacidad cuando aplique;
7. actualizar auditoría/issue #15/Notion si cambió el estado canónico.

Después de cada corrida computacional:

1. validar FTRL/QC;
2. separar evidencia pública y productos restringidos;
3. empaquetar/cifrar si corresponde;
4. copiar a Drive;
5. verificar por re-descarga o checksum equivalente;
6. registrar cierre text-free;
7. actualizar ledger únicamente con estados demostrados.

## 13. Regla de suficiencia

La frase **“todo debe quedar archivado”** se interpreta de forma operativa estricta: ningún objeto relevante para la historia técnica, científica o archivística de LTMD debe quedar únicamente en un chat, un filesystem local no controlado o un artefacto temporal de CI.
