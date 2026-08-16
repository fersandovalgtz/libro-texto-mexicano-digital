# Matriz de derechos y publicación — LTMD 0.2

Fecha de revisión: **15 de agosto de 2026**  
Alcance: **v0.1.0-rc.1 / corpus escalado de Ciencias Naturales**

> Política conservadora de gestión de riesgo. No es una opinión jurídica vinculante. Una autorización o término específico emitido por CONALITEG/SEP o por el titular competente prevalece y debe incorporarse documentalmente.

## Principio rector

La existencia de acceso público a un visor **no se interpreta como licencia abierta de redistribución**. LTMD separa material fuente de terceros, copias temporales de trabajo, datos derivados no sustitutivos y código/documentación original.

## Licencias adoptadas por LTMD

Desde el corte `v0.1.0-rc.1`:

- **software original LTMD:** Apache License 2.0, materializada en [`../LICENSE`](../LICENSE);
- **datos derivados originales licenciables de LTMD:** CC BY 4.0, bajo el alcance definido en [`../DATA_LICENSE.md`](../DATA_LICENSE.md);
- **materiales fuente CONALITEG/SEP/terceros:** expresamente excluidos de esas concesiones salvo que exista un derecho o autorización independiente aplicable.

`DATA_LICENSE.md` limita la concesión a aquello sobre lo que el licenciante posea o controle derechos necesarios. La presencia de una URL, hash, identificador o hecho bibliográfico no relicencia la obra fuente ni implica reclamación de exclusividad sobre hechos no protegibles.

## Semáforo de publicación

### VERDE — publicable/versionable con trazabilidad

- identificadores LTMD (`book_id`, `page_id`, `fragment_id`);
- generación, grado, asignatura y año/edición cuando estén verificados;
- ISBN y hechos bibliográficos;
- URLs oficiales de procedencia;
- tamaños, dimensiones y SHA-256;
- estados de resolución de activos;
- métricas OCR y conteos sin transcripción íntegra;
- PAGESTRUCT/FRAGSEG como categorías y metadatos;
- códigos/etiquetas analíticas originales;
- frecuencias, agregados y resultados estadísticos;
- relaciones de alias, reutilización, revisión y reemplazo;
- manifiestos de gaps y estados técnicos;
- código, workflows y documentación propios;
- tablas derivadas que no reproduzcan expresión sustancial de la obra fuente.

### AMARILLO — trabajo interno o publicación caso por caso

- OCR completo mantenido localmente;
- transcripciones extensas;
- fragmentos textuales necesarios para ejemplos/validación;
- portadas, miniaturas y recortes;
- ilustraciones;
- embeddings u otras representaciones cuya capacidad de reconstrucción sea material;
- colecciones de muchos fragmentos que, acumulados, aproximen contenido sustancial de una obra.

La publicación requiere necesidad científica, proporcionalidad, atribución, análisis de sustitución y fundamento aplicable.

### ROJO — no publicar sin autorización/fundamento específico

- JPEG originales completos;
- PDF o reconstrucciones completas de libros;
- espejos del Catálogo Histórico;
- OCR íntegro públicamente reconstruible;
- dataset secuencial que permita reconstruir sustancialmente el texto completo;
- paquetes masivos de páginas o ilustraciones;
- redistribución a terceros de los archivos fuente descargados.

## Aplicación al corte v0.1.0-rc.1

| Componente | Estado | Política |
|---|---|---|
| Catálogo normalizado de 542 visores | Verde | metadatos/procedencia, no espejo de activos |
| Readiness 37 visores CN | Verde | estados, URLs, hashes, tamaños |
| Alias 2018→2019 | Verde | relaciones y evidencia hash; no duplicar JPEG |
| Auditoría 2008 | Verde | registrar posiciones internas no servidas sin inventar hecho bibliográfico |
| Manifiestos de páginas CN5/CN4/CN6/Ola2 | Verde | hashes/procedencia, no imagen fuente |
| Métricas OCR | Verde | métricas sin OCR íntegro |
| OCR temporal | Amarillo | procesamiento interno y eliminación posterior |
| PAGESTRUCT/FRAGSEG | Verde | categorías/metadatos derivados |
| Manifiestos de fragmentos | Verde sólo si no contienen texto fuente sustitutivo | controlar cualquier campo textual |
| SEMB 0.2 resultados/diagnósticos | Verde | derivados analíticos; resultados históricos siguen exploratorios |
| Muestra SEMB 0.3 por IDs opacos | Verde | sin gold humano ni texto fuente masivo público |
| Gold/reference humana futura | Revisión previa | decidir publicación tras el gate correspondiente |
| Imágenes/páginas completas | Rojo | no incluir en GitHub/Zenodo |
| Código LTMD | Verde | Apache License 2.0 adoptada |
| Datos derivados LTMD | Verde dentro del alcance licenciable | CC BY 4.0 con exclusiones expresas |

## Material fuente y límites

LTMD no interpreta las limitaciones y excepciones al derecho de autor como permiso general para redistribuir OCR o páginas completas. El modelo operativo permanece: reconstrucción temporal, verificación SHA-256, publicación de métricas/metadatos no sustitutivos y eliminación de copias de trabajo.

Las licencias abiertas del repositorio no se aplican a libros, páginas, imágenes, ilustraciones, portadas, texto fuente, OCR sustitutivo, marcas u otros materiales de CONALITEG/SEP o terceros.

## Operación técnica obligatoria

Para cualquier pipeline que necesite fuente protegida:

1. reconstruir/descargar temporalmente;
2. verificar SHA-256 contra el manifiesto;
3. procesar;
4. persistir únicamente outputs permitidos;
5. eliminar la copia temporal;
6. impedir que `private/`, `data/raw/` o `data/work/` entren al control de versiones.

El preflight inspecciona además los archivos rastreados y valida la sustancia de `LICENSE`/`DATA_LICENSE.md` antes de permitir `publish_ready=true`.

## Estado de la candidata

El preflight vigente registra `publish_ready=true`, `publish_blockers=[]`, `LTMD_INTEGRITY_0.6` con 166/166 artefactos críticos y recomputación SHA-256 completa sin discrepancias.

La consulta institucional a CONALITEG/SEP continúa siendo una buena práctica para ampliar futuros usos amarillos/rojos, pero no constituye un blocker para publicar código y derivados propios no sustitutivos bajo el alcance conservador ya adoptado.

## Fuentes institucionales de referencia

- Catálogo Histórico de CONALITEG: https://historico.conaliteg.gob.mx/
- Términos y condiciones de gob.mx: https://www.gob.mx/terminos
- Ley Federal del Derecho de Autor — Cámara de Diputados: https://www.diputados.gob.mx/LeyesBiblio/ref/lfda.htm
- Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/
- Apache License 2.0: https://www.apache.org/licenses/LICENSE-2.0
