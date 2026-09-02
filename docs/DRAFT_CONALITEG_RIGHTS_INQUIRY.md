# Borrador de consulta institucional a CONALITEG sobre reutilización académica

**Estado:** borrador actualizado; **no enviado**.

**Canal institucional identificado:** `info@conaliteg.gob.mx`

## Asunto sugerido

Consulta sobre procesamiento académico y publicación de datos derivados de libros de texto CONALITEG

## Texto sugerido

A quien corresponda en la Comisión Nacional de Libros de Texto Gratuitos:

Mi nombre es Fernando Sandoval Gutiérrez y soy responsable científico del proyecto académico **Libro de Texto Mexicano Digital (LTMD)**, desarrollado con identidad institucional de la Universidad Centro de Estudios Especializados en Educación Superior, Cuauhtémoc. El proyecto estudia histórica y computacionalmente los libros de texto gratuitos de México con criterios de trazabilidad, reproducibilidad y ciencia abierta.

Trabajamos con dos tipos de fuentes institucionales: materiales del **Catálogo Histórico** y la cohorte vigente de **primaria 2026–2027** publicada en el portal oficial de CONALITEG. Nuestro repositorio público contiene código, metadatos, identificadores, URLs de procedencia, hashes, conteos, métricas y otros derivados no sustitutivos; no redistribuimos por defecto los PDF, imágenes de página ni el OCR íntegro de las obras fuente.

En la cohorte vigente 2026–2027 identificamos 42 entradas de catálogo correspondientes a 39 objetos fuente únicos. Para verificar procedencia e integridad técnica, los 39 PDF institucionales fueron recorridos temporalmente para conciliar tamaño y calcular SHA-256; los cuerpos fuente se descartaron después del procesamiento y no se publicaron ni conservaron como parte de la capa pública de LTMD.

Adicionalmente observamos que los 39 PDF requieren contraseña para acceso de contenido mediante tres implementaciones independientes de PDF (`pypdf`, PyMuPDF y `pikepdf`) cuando se prueba únicamente contraseña vacía. LTMD **no pretende descubrir, recuperar, adivinar, neutralizar ni eludir contraseñas o controles de acceso**. Registramos ese estado sólo como evidencia técnica y hemos detenido cualquier inferencia sobre texto embebido u OCR hasta contar con una vía legítima y suficientemente clara.

Con el propósito de mantener una política compatible con los derechos de autor y con las condiciones institucionales aplicables, agradecería su orientación sobre los siguientes puntos:

1. ¿Está permitido realizar procesamiento local u OCR de los libros disponibles en el Catálogo Histórico para investigación académica cuando las imágenes y el OCR completo se conservan únicamente como material de trabajo privado y no se redistribuyen?
2. ¿La misma posibilidad aplica a los materiales del catálogo vigente 2026–2027, o existen condiciones distintas para la colección contemporánea?
3. ¿Puede publicarse abiertamente un dataset derivado que contenga metadatos, identificadores, URLs oficiales, hashes, conteos, métricas, etiquetas analíticas, frecuencias y otros resultados no sustitutivos, sin incluir imágenes originales ni texto íntegro?
4. ¿Existe alguna autorización, licencia o política específica para publicar transcripciones OCR parciales o completas de materiales CONALITEG en repositorios académicos como GitHub o Zenodo? De existir, ¿qué límites, atribuciones o condiciones deben observarse?
5. Para documentar metodología y resultados, ¿pueden reproducirse fragmentos textuales breves como ejemplos de investigación debidamente citados? ¿Existe alguna extensión o condición recomendada por la institución?
6. ¿Puede utilizarse una miniatura de portada o de una página en una interfaz académica o publicación científica, o se requiere autorización específica, particularmente cuando la portada incorpora obra artística o material de terceros?
7. ¿Los derechos o autorizaciones sobre estos usos deben solicitarse a CONALITEG, a la Secretaría de Educación Pública o a otra instancia dependiendo de la edición y de sus titulares?
8. ¿Existen términos de uso específicos del Catálogo Histórico o del catálogo vigente 2026–2027 distintos de los términos generales de gob.mx?
9. En el caso de materiales que el visor oficial permite consultar públicamente pero cuyo PDF exige contraseña para acceso de contenido mediante software PDF independiente, ¿existe una vía institucional autorizada para investigación computacional/OCR, o debe entenderse que ese tipo de procesamiento requiere una autorización expresa previa?

Nuestro interés es mantener una política de ciencia abierta compatible con los derechos aplicables, preservar atribución y procedencia institucional y evitar cualquier redistribución o procesamiento no autorizado. Si estas preguntas corresponden a otra área de CONALITEG o de la SEP, agradecería mucho que nos indicaran el canal competente.

Agradezco su orientación.

Atentamente,

**Fernando Sandoval Gutiérrez**  
Responsable científico — *Libro de Texto Mexicano Digital (LTMD)*  
Universidad Centro de Estudios Especializados en Educación Superior, Cuauhtémoc

## Registro antes del envío

Antes de enviar este mensaje se deberá registrar:

- fecha;
- cuenta de correo utilizada;
- destinatario exacto;
- versión del texto enviada;
- cualquier adjunto o liga incluida;
- respuesta y fecha de recepción;
- nombre/cargo del funcionario que responda, si está disponible;
- interpretación operativa resultante y cambios requeridos en `DATA_GOVERNANCE.md`, `RIGHTS_PUBLICATION_MATRIX.md` y el issue #2.

No debe asumirse que el silencio o la ausencia de respuesta equivale a autorización.
