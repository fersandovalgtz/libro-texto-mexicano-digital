# LTMD-U1 — demostración local del atlas longitudinal 0.1

**Estado:** evidencia reproducible del flujo de análisis visual, **no** despliegue institucional. Vinculado al alcance de la issue [#171](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues/171). La puerta técnica de staging/API, los derechos [#2](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues/2) y la validación humana permanecen abiertas donde corresponda.

## Qué entrega

Genera un único archivo HTML autónomo (sin CDN, JavaScript remoto, credenciales ni OCR) desde **tres derivados públicos existentes** y su manifiesto SHA-256:

- `ltmd_analytics_indigenous_generation_0_1.csv`: 11 generaciones y tasas candidatas por 1,000 páginas;
- `ltmd_analytics_indigenous_explicit_terms_0_1.csv`: 45 agregaciones por término y generación;
- `ltmd_analytics_indigenous_validation_state_0_1.csv`: 1,151 observaciones pendientes de revisión visual.

**Ejecución en el repositorio:**

```bash
python scripts/build_ltmd_u1_atlas_preview.py --output /tmp/ltmd_u1_atlas_preview.html
python -m pytest -q tests/test_build_ltmd_u1_atlas_preview.py
```

El archivo resultante puede abrirse sin servidor y contiene: serie longitudinal interactiva, filtros, comparación entre generaciones, detalle de términos y exportación JSON no sustitutiva. Conserva el corte, manifiesto, estados de evidencia y denominadores. No añade un nuevo vertical, no consulta las SQLite privadas y no utiliza CDN.

## Límites científicos

- Los 1,151 candidatos no son «1,151 afirmaciones históricas verificadas»; todas las páginas permanecen `not_visually_validated` y `semantic_ready=false`.
- Los cortes 1960, 1966, 1972, 1982, 1988, 1993, 2008, 2011, 2014, 2018 y 2019 no representan una serie anual continua. Se prohíbe interpolar años faltantes.
- El mismo contenido o libro puede figurar en generaciones diferentes por reutilización editorial. Una suma de `candidate_books` entre generaciones no es un conteo de libros únicos.
- Las categorías `explicit_general` y `named_language_contextual` se solapan; tampoco deben sumarse como si fueran exclusivas.
- Las tablas por término pueden tener coincidencias superpuestas; no se suman para afirmar páginas únicas.
- Las tasas usan el denominador de corpus declarado por generación, no población estudiantil, ni libros totales, ni composición de niveles curriculares homogéneos.
- La visualización es una capa exploratoria: la promoción a `human_validated` requiere un protocolo de cotejo visual externo.

## Seguridad y gobierno

- Validación estricta de encabezados CSV para impedir inclusión involuntaria de `page_id` o texto OCR.
- Verificación criptográfica de los insumos frente al manifiesto de `data/analytics`. Se tolera únicamente normalización de saltos CRLF → LF en el checkout Git (comparación SHA-256 con recodificación exacta); no se admiten modificaciones de contenido.
- Rechazo de cambios científicos de estado y de tasas incompatibles con denominadores.
- Sin transferencias a terceros, cookies, pagos, registro de usuarios, archivos fuente ni exportaciones textuales.
- Regla #2: sólo agregados y derivados no sustitutivos; el archivo HTML no debería publicarse sin la validación de la infraestructura y los derechos del producto.

## Puertas para cerrar #171

La presente demostración no cierra #171. Para cumplir íntegramente el issue faltan la auditoría de las cohortes comparables y los denominadores de estratos/dominios, el manifiesto longitudinal general y la comprobación bajo CI del repositorio. La interfaz comercial institucional exige además staging de la API y revisión posterior de suscripciones y licencias.


## Integración longitudinal opcional (15-nov-2026)

```sh
python scripts/build_ltmd_u1_atlas_preview.py --longitudinal --output /tmp/ltmd_u1_atlas_preview.html
```

La bandera integra la salida del constructor reproducible de dataset 0.2, con los cinco CSV admitidos y la cobertura operativa versionada. Comprueba identidad del manifiesto SHA-256, coincidencia de generaciones, estados epistemológicos y ausencia de denominadores/tasas estratificados privados. La vista añade tabla de cinco cohortes observadas, filtros de generación/grado/ola, filtro de lengua limitado a su tabla y exportación JSON de los estratos/lenguas seleccionados con filtros y procedencia. El filtro de lengua no recalcula el total de estrato; la UI no suma categorías solapadas ni transforma una fila ausente en cero. Las tasas de generación y cohorte usan páginas indexadas del mismo conjunto de cortes. Para estratos y lenguas solo se muestran los conteos previamente admitidos; los dos campos de tasa/denominador siguen null en la exportación. La función proyecta una lista cerrada de campos y rechaza datos no finitos al serializar.

CI genera el HTML integrado y lo conserva temporalmente como artefacto `ltmd-u1-atlas-integrated-preview` (14 días). Se añaden cinco casos de prueba sintéticos sobre proyección, no divulgación, procedencia y consistencia longitudinal. No se afirma validación de interacción en navegador sin ejecutarla; no se publica en producción ni se incorpora información privada. Las puertas #171/#2 y staging permanecen abiertas.
