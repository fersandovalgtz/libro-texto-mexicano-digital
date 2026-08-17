# LTMD-U1 W7 — investigación de fuentes retenidas 0.4

Versión: `LTMD_U1_W7_WITHHELD_SOURCE_RESEARCH_0.4`.

Corte: **17 de agosto de 2026**.

Este corte continúa la investigación reproducible de las cinco identidades W7 retenidas por fuente. **No modifica `ocr_source_admitted`, no crea aliases y no incorpora archivos externos como fuente canónica.** Su objetivo es registrar nuevas pistas documentales públicas y distinguir con precisión entre existencia de una reproducción externa, caracterización bibliográfica y admisión de fuente.

## Estado heredado

Permanecen vigentes las cinco retenciones:

| identidad | estado de fuente | problema |
|---|---|---|
| `H2014P5FCA` | `withheld_source_gap` | 224/225 JPEG institucionales servidos; falta la página lógica 104 / `104.jpg` |
| `H2018P3FCA` | `withheld_source_subtree_unserved` | visor/configuración institucional presentes; subárbol de activos observado no servido |
| `H2018P4FCA` | `withheld_source_subtree_unserved` | visor/configuración institucional presentes; subárbol de activos observado no servido |
| `H2018P5FCA` | `withheld_source_subtree_unserved` | visor/configuración institucional presentes; subárbol de activos observado no servido |
| `H2018P6FCA` | `withheld_source_subtree_unserved` | visor/configuración institucional presentes; subárbol de activos observado no servido |

Las cardinalidades institucionales congeladas continúan siendo 114, 130, 226 y 210 posiciones para `H2018P3FCA`–`H2018P6FCA`.

## 1. Nueva pista: índice público contemporáneo del ciclo 2018–2019

Se localizó un índice público de libros de primaria publicado originalmente en agosto de 2018 que agrupa explícitamente los materiales de tercero a sexto bajo el rótulo **“Reimpresión 2018-2019”** y enlaza *Formación Cívica y Ética* para los cuatro grados retenidos.

Referencia de descubrimiento:

- `https://www.cicloescolar.mx/libros-de-texto-gratuitos-primaria-2018/`

Este hallazgo no demuestra identidad byte a byte con los objetos `H2018P3FCA`–`H2018P6FCA`, pero sí establece una pista temporal y bibliográfica concreta para búsquedas acotadas: reproducciones públicas presentadas en 2018 como libros de *Formación Cívica y Ética* del ciclo 2018–2019.

## 2. Dos endpoints PDF estáticos observables

La navegación pública permite derivar, desde enlaces explícitos del propio sitio y no desde heurística de nombres, al menos dos endpoints PDF estáticos:

- cuarto grado: `https://cdn.cicloescolar.mx/2018-2019/primaria/4/Primaria_Cuarto_Grado_Formacion_Civica_y_Etica_Libro_de_texto.pdf`;
- sexto grado: `https://cdn.cicloescolar.mx/2018-2019/primaria/6/Primaria_Sexto_Grado_Formacion_Civica_y_Etica_Libro_de_texto.pdf`.

Las páginas de procedencia identifican respectivamente materia, nivel, grado, ciclo escolar 2018–2019 y formato PDF:

- `https://www.cicloescolar.mx/formacion-civica-y-etica-cuarto-2018/`;
- `https://www.cicloescolar.mx/formacion-civica-y-etica-sexto-2018-2019/`.

**Estado LTMD:** `external_candidate_discovered`. La existencia de estos endpoints no levanta la retención. Antes de cualquier uso se requiere una recuperación reproducible y una comparación contra evidencia institucional del mismo objeto.

## 3. Corroboración bibliográfica secundaria para el ciclo 2018–2019

Una reproducción secundaria públicamente indexada de *Formación Cívica y Ética. Sexto grado* expone en su página legal la secuencia:

- primera edición: **2014**;
- cuarta reimpresión: **2017**;
- ciclo escolar: **2018–2019**;
- ISBN mostrado: **978-607-514-808-3**.

Además, materiales de dosificación escolar del mismo ciclo citan de manera agregada *Formación Cívica y Ética* de tercero a sexto como **cuarta reimpresión 2017 (ciclo escolar 2018–2019)**.

Esta evidencia es bibliográfica y secundaria. **No se transfiere automáticamente** a cada identidad H2018 ni se incorpora todavía a `LTMD_BIBLIOGRAPHIC_OBSERVATIONS`, porque LTMD exige evidencia por objeto y cadena de procedencia explícita.

## 4. Hipótesis acotada que sí queda autorizada para prueba

A diferencia de un barrido abierto por Internet, el nuevo hallazgo permite una prueba limitada y falsable para `H2018P4FCA` y `H2018P6FCA`:

1. recuperar el PDF externo únicamente desde el endpoint enlazado por la página de procedencia;
2. congelar SHA-256, tamaño, número de páginas PDF y metadatos técnicos del archivo recibido;
3. identificar dentro del PDF la página legal y registrar edición, reimpresión, ciclo e ISBN sin normalización inferencial;
4. comparar cardinalidad y secuencia con las 130 y 210 posiciones institucionales esperadas, sin asumir que página PDF = página lógica;
5. buscar anchors textuales/visuales en posiciones deterministas que puedan contrastarse con otras reproducciones institucionales o con evidencia conservada del mismo linaje;
6. sólo si la correspondencia de objeto y posición resulta inequívoca, evaluar si la reproducción puede clasificarse como fuente documental derivada bajo los criterios vigentes.

Para tercero y quinto grado se conserva por ahora únicamente la pista del índice público hasta que se obtenga un endpoint reproducible equivalente sin construir rutas por analogía.

## 5. Lo que este corte NO permite concluir

No se concluye que:

- los cuatro PDF externos sean byte-idénticos a los activos CONALITEG no servidos;
- la etiqueta pública “2018–2019” equivalga a `catalog_generation=2018`;
- la cuarta reimpresión 2017 pueda imputarse automáticamente a tercero, cuarto, quinto y sexto;
- la coincidencia de cardinalidad, si apareciera, sea suficiente para identidad;
- los endpoints externos puedan sustituir sin más al subárbol institucional ausente;
- `H2018P3FCA`–`H2018P6FCA` deban resolverse mediante alias 2018→2019.

## 6. Decisión

Las cinco retenciones continúan vigentes. El incremento 0.4 cambia únicamente el mapa de investigación:

- la vía 2018 deja de depender sólo de probes negativos del routing institucional;
- existen ahora reproducciones externas contemporáneas y endpoints estáticos concretos para al menos cuarto y sexto grado;
- la siguiente prueba debe ser **documental y posicional**, no de similitud global;
- cualquier incorporación futura deberá conservar la distinción entre `source_jpeg` institucional, reproducción externa, reconstrucción derivada y evidencia bibliográfica.

La regla de aceptación de `LTMD_U1_W7_WITHHELD_SOURCE_ACCEPTANCE_CRITERIA` permanece sin cambios: **una nueva pista puede justificar una prueba; no puede, por sí sola, levantar una retención.**
