# Arquitecturas candidatas preregistradas para SEMB 0.3

Versión: `SEMB03_CANDIDATES_0.1`

## Objetivo

Congelar antes de observar referencia humana el espacio de arquitecturas que podrá compararse con los 320 casos `development`. Esto reduce grados de libertad analíticos y evita inventar una arquitectura después de ver qué funciona mejor en casos particulares.

Ninguna arquitectura podrá usar generación, año, página, posición histórica, salidas Rule A, resultados SEMB 0.2 del corpus ni contrastes históricos como feature de predicción. `page_id` sólo se utilizará para agrupar folds y evitar fuga entre fragmentos de una misma página.

## Esquema de validación durante desarrollo humano

La comparación de candidatos se realizará mediante **5-fold GroupKFold por `page_id`** sobre los 320 casos de desarrollo. Todos los fragmentos de una página deberán permanecer en el mismo fold. Las decisiones de hiperparámetros se basarán únicamente en predicciones out-of-fold de desarrollo.

Después de seleccionar una configuración, se reentrenará/ajustará sobre los 320 casos completos, se registrarán hashes y parámetros y se ejecutará `lock_semb03_model.py` antes de abrir validación.

## GATE — detección de tarea/acción

Se comparan exactamente estas familias:

### G0 — baseline congelado SEMB 0.2

Diferencia entre máxima similitud a anchors positivos y máxima similitud a anchors negativos, threshold 0.0. Se conserva sólo como baseline.

### G1 — gate de margen escalar recalibrado

Misma variable `gate_margin`, con threshold seleccionado únicamente dentro de desarrollo. Grid preregistrado: de −0.050 a +0.050 inclusive en pasos de 0.001.

Objetivo: maximizar balanced accuracy out-of-fold. Desempate: mayor mínimo entre sensibilidad y especificidad; segundo desempate: threshold con menor valor absoluto.

### G2 — gate logístico semántico

Regresión logística L2 con `class_weight=balanced`, sobre 12 rasgos de similitud ya definidos en `SEMB03_GATE_SYNTH_DEV_0.1`:

- `gate_pos_max`;
- `gate_neg_max`;
- `gate_margin`;
- top-1, top-2 y margen de acciones;
- top-1, top-2 y margen de posiciones;
- similitud con `receiver`;
- similitud con `instruction_follower`;
- similitud con `reasoner`.

Valores de C permitidos: `{0.1, 0.5, 1.0, 2.0}`. Estandarización aprendida exclusivamente dentro de cada fold. No se permiten features históricas ni metadatos de generación.

### Selección del gate

Primero se descartan configuraciones cuya sensibilidad o especificidad out-of-fold sea <0.75. Entre las restantes se maximiza balanced accuracy. Si ninguna cumple ambos mínimos, se elige la mayor balanced accuracy sólo como candidato fallido y **no** se interpreta como evidencia de suficiencia; la validación bloqueada conserva sus criterios preregistrados.

## ACTION HEAD — 16 acciones pedagógicas

Se comparan:

### A0 — anchors SEMB 0.2 congelados

Baseline sin aprendizaje humano.

### A1 — híbrido anchors + centroides sintéticos

Promedio unitario 50/50 entre anchor SEMB 0.2 y centroide sintético por categoría derivado de `SEMB03_SYNTH_STRESS_0.1`. Es un baseline sintético fijo.

### A2 — híbrido anchors + centroides humanos de desarrollo

Para cada categoría se calcula un centroide de los positivos humanos **dentro del fold de entrenamiento**. Se mezcla con el anchor congelado usando α para el centroide humano en `{0.25, 0.50, 0.75}`. Si una categoría no tiene positivos suficientes en un fold, se utiliza el anchor fijo para esa categoría.

### A3 — híbrido triple

Anchor congelado + centroide sintético + centroide humano. Pesos permitidos, normalizados, pertenecen a este conjunto cerrado:

- `(0.50, 0.25, 0.25)`;
- `(0.34, 0.33, 0.33)`;
- `(0.25, 0.25, 0.50)`

en el orden `(anchor, synthetic, human)`.

## POSITION HEAD — 9 posiciones del estudiante

Se comparan las mismas cuatro familias P0–P3, análogas a A0–A3.

## Regla multilabel

Para acciones, máximo 3 etiquetas; para posiciones, máximo 2. El ancho relativo respecto al top score (`band`) se selecciona de `{0.00, 0.01, 0.02, 0.03, 0.04, 0.05}` usando desarrollo out-of-fold.

Objetivo de selección: macro-F1 entre categorías con presencia suficiente en el fold, con micro-F1 como desempate. No se podrá cambiar el máximo de etiquetas después de observar resultados humanos sin versionar un protocolo nuevo.

## Incertidumbre/cobertura

La incertidumbre se separará de la clasificación. Una etiqueta predicha no se convertirá automáticamente en 'incierta' sólo porque el top-1/top-2 sea pequeño sin calibración empírica.

Se permitirán dos señales de certeza:

1. probabilidad/calibración del gate para `actionable`;
2. margen normalizado entre scores para cabezales de acciones/posiciones.

Los thresholds de certeza se seleccionarán exclusivamente con predicciones out-of-fold de los 320 casos de desarrollo, buscando maximizar cobertura sujeta a:

- precision de la decisión `actionable` ≥0.80 entre casos declarados ciertos;
- F1 de acciones y posiciones no inferior en más de 0.03 al máximo out-of-fold de la arquitectura seleccionada;
- cobertura objetivo ≥0.70 cuando sea alcanzable.

Si 70% de cobertura no es alcanzable bajo esas restricciones, se documentará en desarrollo; no se relajarán criterios usando la validación bloqueada.

## Selección final antes de lock

La configuración final se define con una regla jerárquica:

1. gate que satisfaga sensibilidad/especificidad de desarrollo y maximice balanced accuracy;
2. action head que maximice macro-F1 bajo el grid cerrado;
3. position head que maximice macro-F1 bajo el grid cerrado;
4. calibración de certeza que maximice cobertura bajo restricciones anteriores;
5. reentrenamiento en los 320 casos;
6. serialización completa de configuración, métricas out-of-fold y código;
7. lock criptográfico;
8. una sola evaluación en 160 casos bloqueados.

## Regla de fracaso

El hecho de que una arquitectura sea la mejor del grid no implica que sea suficiente. Si sus métricas de desarrollo son débiles, puede bloquearse como experimento para validación sólo si se justifica metodológicamente; pero un FAIL en validación no podrá repararse usando los mismos 160 casos.
