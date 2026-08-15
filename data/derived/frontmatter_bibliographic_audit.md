# Auditoría bibliográfica automatizada de front matter

Versión: `FRONTMATTER_BIB_AUDIT_0.1`. Se inspeccionan páginas 1–8 de las cuatro generaciones. El OCR es temporal; sólo se publican señales y candidatos bibliográficos derivados.

## Señales detectadas
- 1972: páginas con marcador de edición=4; candidatos de año de edición=ninguno; copyright=1972; impresión=ninguno; páginas con ISBN=ninguna; ISBN candidatos=ninguno.
- 1988: páginas con marcador de edición=2; candidatos de año de edición=ninguno; copyright=1977; impresión=ninguno; páginas con ISBN=2; ISBN candidatos=968-29-0758-6.
- 1993: páginas con marcador de edición=2; candidatos de año de edición=1998; copyright=ninguno; impresión=1998; páginas con ISBN=2; ISBN candidatos=970-18-1599-8.
- 2014: páginas con marcador de edición=2; candidatos de año de edición=1962,2010,2011,2014,2017,2018,2019; copyright=2011,2014,2017,2018; impresión=2014; páginas con ISBN=2; ISBN candidatos=ninguno.

## Regla de interpretación
Una coincidencia de regex es un candidato técnico, no una verificación bibliográfica por sí sola. La ausencia de marcador explícito impide convertir automáticamente el año de la generación del catálogo en `edition_year`. Los metadatos ya verificados por inspección de página legal conservan prioridad.
