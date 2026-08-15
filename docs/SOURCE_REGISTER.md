# Registro de fuentes — piloto 0.1

| source_id | institución | colección | URL | cobertura | formato observado | términos/derechos | decisión de uso | revisado |
|---|---|---|---|---|---|---|---|---|
| conaliteg-historico | CONALITEG | Catálogo Histórico de Libros de Texto Gratuitos | https://historico.conaliteg.gob.mx/ | generaciones históricas de LTG | visor HTML + JPEG por página; manifiesto `claves.json` | consulta pública explícita; sin licencia abierta específica localizada; términos generales de gob.mx como referencia precautoria; avisos de derechos específicos en páginas legales | publicar código, metadatos, métricas, hashes y datos derivados no sustitutivos; mantener OCR completo e imágenes fuera de GitHub; solicitar aclaración para categorías amarillas/rojas | sí, revisión ampliada 2026-08-15 |
| gobmx-terminos | Gobierno de México | Términos y condiciones de gob.mx | https://www.gob.mx/terminos | portal gob.mx | HTML | visualización/descarga personal no comercial; restricciones a reproducción, exhibición pública, distribución y transferencia | usar como referencia precautoria; no tratar como licencia abierta | sí, 2026-08-15 |
| lfda-vigente | Cámara de Diputados | Ley Federal del Derecho de Autor | https://www.diputados.gob.mx/LeyesBiblio/ref/lfda.htm | legislación federal vigente | HTML + documentos legales | última reforma indicada: 14-05-2026; limitaciones a derechos patrimoniales deben interpretarse según texto vigente | fundamento legal contextual; no usar como autorización automática para corpus íntegro | sí, 2026-08-15 |
| lfda-art148 | Orden Jurídico Nacional | LFDA, artículo 148 | https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17068.html | artículo 148 | HTML | contempla citas y reproducción de partes para investigación bajo condiciones, incluida no afectación de explotación normal, cita de fuente y no alteración | permite fundamentar cautelosamente citas/partes en investigación; no se extiende automáticamente a OCR/libros completos | sí, 2026-08-15 |

## Evidencia técnica del piloto

Los cuatro ejemplares seleccionados usan una arquitectura común:

`HTML → x.js → claves.json → magazine.js → /c/{viewer_key}/{archivo}.jpg`

`claves.json` declara 763 páginas estructurales; la auditoría integral verifica **759 JPEG fuente** y **4 páginas terminales sintéticas**.

## Ejemplares del piloto y avisos legales

| book_id | generación | página legal | evidencia relevante |
|---|---:|---:|---|
| LTMD-CN5-G1972 | 1972 | visor 4 | página legal/corporativa localizada; no se ha identificado aviso inequívoco que permita inferir condición abierta |
| LTMD-CN5-G1988 | 1988 | visor 2 | `Derechos reservados SEP, 1977`; ISBN 968-29-0758-6 |
| LTMD-CN5-G1993 | 1993 | visor 2 | Primera edición 1998; SEP 1998; ISBN 970-18-1599-8 |
| LTMD-CN5-G2014 | 2014 | visor 2 | D.R. SEP 2014; Tercera edición revisada 2014; ISBN 978-607-514-722-2 |

## Evidencia documental de acceso

CONALITEG publicó en 2019 que pone el Catálogo Histórico en línea a disposición de estudiantes y población general para conocer materiales producidos desde 1960. Se registra como evidencia de **consulta pública**, no como licencia de redistribución.

Fuente: https://www.gob.mx/conaliteg/articulos/conoce-el-catalogo-historico-de-los-libros-de-texto-gratuitos?idiom=es

## Política resultante

### Publicación ordinaria permitida por política interna

- metadatos y procedencia;
- manifiestos/identificadores;
- métricas OCR y de imagen;
- hashes;
- CER/WER;
- códigos y etiquetas de investigación;
- frecuencias y estadísticas;
- datos derivados no sustitutivos;
- código y documentación.

### Material mantenido fuera del repositorio público

- imágenes fuente;
- OCR completo;
- transcripciones extensas;
- páginas/portadas/miniaturas salvo revisión específica;
- colecciones de fragmentos que puedan reconstruir una parte sustancial del libro.

La matriz detallada se encuentra en `docs/RIGHTS_PUBLICATION_MATRIX.md`.

## Consulta institucional pendiente

Se preparó `docs/DRAFT_CONALITEG_RIGHTS_INQUIRY.md` para consultar al canal institucional `info@conaliteg.gob.mx` sobre OCR de investigación, datasets derivados, fragmentos, miniaturas y publicación académica. **No se ha enviado.**

## Regla de revisión

Este registro debe revisarse:

1. si CONALITEG/SEP responde la consulta;
2. antes de publicar cualquier OCR, fragmento extenso, imagen o miniatura;
3. antes de una liberación con DOI que incorpore material expresivo fuente;
4. si cambian los términos del portal o la legislación relevante.
