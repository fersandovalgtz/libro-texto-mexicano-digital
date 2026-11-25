# LTMD Research — control de integridad de fragmentos por página 0.1

**Estado:** auditoría de exportación privada y prueba automatizada de regresión. **No es una corrección del sitio desplegado.** Incidencia: [#182](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues/182). Fecha: 25-nov-2026.

## Hallazgo delimitado

En una exportación privada de la búsqueda exacta \`discapacidad\` (todas las generaciones, grados y libros; 25-nov-2026) hay 50 resultados visibles de 513 reportados. Los resultados #21 (visor 7) y #27 (visor 86) corresponden a la misma obra, *Proyectos de Aula, tercer grado*, ciclo 2026–2027, clave oficial \`P3PAA\`. Los fragmentos de ambos comparten **117 palabras consecutivas**; el #21 además reúne texto introductorio asociado a la página 7. La captura visual proporcionada por la persona investigadora muestra que la página 7 del visor contiene contenido introductorio y no el pasaje sustantivo atribuido.

**Diagnóstico:** potencial contaminación de la segmentación/atribución del texto de búsqueda entre páginas o un artefacto del generador de extractos. No está demostrada una causa raíz exacta, ni está comprobada visualmente la posición real del pasaje completo. La página 86 es una *candidata de contraste*, no una corrección de número acreditada. No declarar un falso positivo semántico general por este caso.

## Diferencia entre motores

El índice privado LTMD-U1 del repositorio está documentado para 86,549 páginas (1960–2019). El visor LTMD Research que generó esta exportación expone material contemporáneo del ciclo 2026–2027 y no contiene su implementación de búsqueda en este repositorio. Por eso, modificar la capa LTMD-U1 sin conocer el motor real **no corrige** los resultados ya desplegados en \`chatgpt.site\`. La futura integración debe localizar el código y la fuente de índices reales del sitio; no inventar un contrato de despliegue.

## Auditor de exportaciones

\`scripts/audit_ltmd_search_export_pages.py\` recibe un TXT privado de LTMD Research y compara únicamente fragmentos de **un mismo libro y ciclo**. Marca pares de páginas distintas que comparten al menos 32 palabras consecutivas normalizadas. Emplea n-gramas como candidatos y después confirma la longitud con una comparación de secuencias.

Uso local:

\`\`\`bash
python scripts/audit_ltmd_search_export_pages.py \
  --input "local/LTMD-discapacidad.txt" \
  --output "local/ltmd-export-audit.json"
\`\`\`

**Nunca** subir el archivo TXT original a GitHub, ni añadir la salida textual de extractos o PDFs. El informe JSON sólo contiene rango, total anunciado, orden de resultados, libro/clave/ciclo, posiciones del visor, longitud de la superposición y estado \`requires_source_review\`. No exporta el texto de los fragmentos, consulta, URLs privadas ni identificadores de imágenes de fuente. La búsqueda sobre las primeras 50 referencias **no inspecciona los otros 463 resultados**.

El algoritmo es un **detector de anomalías**, no un clasificador de errores: el mismo texto podría aparecer legítimamente en múltiples lugares, diagramas, índice, imágenes de otras páginas o citas repetidas. Cada señal requiere cotejo de la imagen oficial antes de corregir una posición.

## Criterios para reparar el motor que sirve el sitio

1. Identificar el código fuente y versión exacta del buscador desplegado, su unidad de indexación y procedencia de OCR, sin extraer ni republicar PDFs protegidos ni forzar archivos cifrados.
2. Demostrar cómo se construyen \`viewer_key\`, \`viewer_page\`, \`source_object\` y \`search_text\` para cada resultado. Validar que el fragmento de búsqueda procede **sólo del texto asociado a la misma página** y no de una concatenación interdocumental. Si una imagen de página contiene miniaturas o reproducciones de otras páginas, distinguir la presencia visual secundaria de contenido editorial sustantivo.
3. Agregar en el motor real una prueba con dos páginas ficticias: texto relevante sólo en la página B; asegurar que la página A no se presenta con un fragmento de B. Probar también citas legitimamente repetidas, páginas preliminares, índices y diferencias de paginación impresa vs. visor.
4. Revisar el par real \`P3PAA\` (visor 7 y 86) con imágenes legítimas y expediente de procedencia privado. Si se confirma, corregir la segmentación/atribución a partir de la fuente; reconstruir el índice derivado afectado; no editar manualmente una coincidencia como parche único.
5. Volver a correr exportación y escáner; exigir ausencia de la discrepancia comprobada. La ausencia de alarmas del escáner no sustituye el cotejo humano de precisión/recall.
6. Respetar el control jurídico [#2](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues/2), mantener el sitio privado y no prometer fiabilidad comercial hasta acreditarla.

## Pruebas

\`tests/test_audit_ltmd_search_export_pages.py\` cubre superposición idéntica de un pasaje simulado, dos páginas de mismo libro, aislamiento entre libros distintos, citas cortas, libros con la misma página, salida sin texto fuente, exportación parcial, errores de formato, enlace no canónico y límites de longitud. Toda la CI funciona con **textos sintéticos**. No ejecuta la exportación privada ni descarga datos reales.
