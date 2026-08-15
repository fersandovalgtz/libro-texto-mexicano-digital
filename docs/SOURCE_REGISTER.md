# Registro de fuentes — piloto 0.1

| source_id | institución | colección | URL | cobertura | formato observado | términos/derechos | decisión de uso | revisado |
|---|---|---|---|---|---|---|---|---|
| conaliteg-historico | CONALITEG | Catálogo Histórico de Libros de Texto Gratuitos | https://historico.conaliteg.gob.mx/ | 1960–2020 | visor HTML + JPEG por página; manifiesto `claves.json` | libre acceso para consulta; no se localizó licencia abierta específica para redistribución masiva; términos generales de gob.mx se conservan como referencia precautoria | publicar metadatos/código/datos derivados; mantener OCR completo e imágenes fuera de GitHub hasta aclarar | sí, revisión provisional 2026-08-15 |

## Evidencia técnica del piloto

Los cuatro ejemplares seleccionados usan una arquitectura común:

`HTML → x.js → claves.json → magazine.js → /c/{viewer_key}/{archivo}.jpg`

Conteos verificados del visor: 259 + 163 + 179 + 162 = **763 páginas**.

## Evidencia documental de derechos y acceso

- CONALITEG describe el catálogo digital como plataforma de libre acceso para consulta ciudadana.
- No se encontró en esta revisión una licencia abierta específica del Catálogo Histórico que permita asumir redistribución de imágenes o transcripciones completas.
- La política interna aplicable está documentada en `docs/DATA_GOVERNANCE.md`.
- Falta verificar los avisos de derechos contenidos en las páginas legales de los cuatro libros concretos.

Este registro deberá revisarse antes de cualquier ingestión masiva o cambio en la política de publicación.
