# LTMD-U1 — codebook de representación de lenguas indígenas 0.1

## Propósito

Este codebook define las variables cualitativas para validar y describir páginas candidatas del estudio `LTMD-U1-INDIGENOUS-LANGUAGES-0.1`. Debe aplicarse **después de verificar visualmente la página fuente**. No se codifica una categoría por el mero tema del libro ni por una coincidencia OCR aislada.

Las categorías pueden coexistir cuando el fragmento contiene funciones diferentes observables.

## A. Estado de validación de la coincidencia

### `verified_true`
La imagen fuente confirma una referencia lingüística indígena pertinente al criterio de recuperación.

### `false_positive`
La imagen fuente demuestra que la coincidencia no es lingüísticamente pertinente o deriva de error OCR.

### `uncertain`
La imagen o el contexto no permiten decidir con seguridad.

## B. Tipo de referencia

### `explicit_general`
La página tematiza directamente `lengua(s) indígena(s)`, `lengua(s) originaria(s)`, diversidad lingüística o equivalente.

### `named_language_contextual`
Se nombra una lengua concreta y el contexto confirma que se habla de uso, hablantes, vocabulario, traducción, bilingüismo u otra función lingüística.

### `historical_terminology`
La referencia lingüística usa vocabulario histórico que requiere tratamiento específico, por ejemplo `dialecto`, `vernácula`, `castellanización` u otra denominación no equivalente automáticamente a las categorías contemporáneas.

## C. Estatus nominal

Codificar todas las formas observables pertinentes:

- `lengua`
- `idioma`
- `dialecto`
- `habla`
- `lengua_indigena`
- `lengua_originaria`
- `lengua_nacional`
- `otro`

Registrar además la forma literal breve en un campo privado de trabajo si los derechos y el protocolo lo permiten; el dataset público puede conservar sólo la categoría y una paráfrasis.

## D. Marco temporal atribuido

### `past_survival`
La lengua se presenta principalmente como supervivencia, vestigio o elemento heredado del pasado.

### `present_social_reality`
Se presenta como práctica contemporánea de una población o comunidad.

### `future_preservation`
Se orienta a continuidad, preservación, revitalización o transmisión futura.

### `mixed_temporality`
Coexisten explícitamente varias temporalidades.

## E. Agencia de hablantes

### `population_described`
Los hablantes aparecen como población cuantificada, localizada o clasificada, sin acción lingüística relevante.

### `language_users`
Los hablantes aparecen usando, hablando, leyendo, escribiendo, transmitiendo o creando en la lengua.

### `knowledge_holders`
Se reconoce conocimiento cultural/lingüístico portado por personas o comunidades.

### `political_rights_subjects`
Los hablantes aparecen como sujetos de derechos, reconocimiento, igualdad o protección contra discriminación.

## F. Relación con el español

- `spanish_centrality`
- `subordination_to_spanish`
- `bilingual_coexistence`
- `translation_mediation`
- `lexical_enrichment`
- `language_shift_or_loss`
- `no_explicit_relation`

La codificación debe basarse en formulación observable; no inferir jerarquía sólo porque ambas lenguas aparezcan en la misma página.

## G. Función territorial/demográfica

- `map_location`
- `state_or_region_distribution`
- `census_count`
- `bilingual_population`
- `monolingual_population`
- `migration_or_displacement`
- `community_localization`
- `not_applicable`

## H. Función pedagógica

Adaptada al codebook general de LTMD, puede codificarse:

- `receive_information`
- `identify`
- `classify`
- `investigate`
- `ask_family_or_community`
- `listen`
- `read`
- `write`
- `translate`
- `collect_words_or_texts`
- `create_or_produce`
- `discuss_or_value`
- `act_in_community`
- `not_applicable`

## I. Marco normativo

- `integration_national`
- `cultural_plurality`
- `heritage`
- `interculturality`
- `national_language_status`
- `linguistic_rights`
- `non_discrimination`
- `preservation`
- `no_normative_frame`

## J. Riesgo lingüístico

- `endangerment`
- `speaker_loss`
- `language_shift`
- `disappearance`
- `revitalization`
- `no_risk_frame`

## K. Polaridad valorativa

### `hierarchical_or_deficit`
El texto formula explícitamente inferiorización, déficit o jerarquía lingüística.

### `neutral_descriptive`
Predomina descripción sin valoración evidente.

### `positive_pluralist`
La lengua/diversidad se presenta explícitamente como riqueza, valor o componente positivo.

### `rights_affirming`
Se la vincula con igualdad, derechos o protección normativa.

### `ambiguous`
La valoración no puede codificarse de manera conservadora.

## L. Reglas de inferencia conservadora

1. No transformar una mención de pueblo o territorio en mención lingüística.
2. No inferir `rights_affirming` por el año de publicación.
3. No inferir `spanish_centrality` sólo por la presencia del español.
4. No convertir una actividad sobre cultura indígena en actividad lingüística si la lengua no participa funcionalmente.
5. No codificar `endangerment` sin una señal textual explícita de riesgo, pérdida o desaparición.
6. No reinterpretar retrospectivamente terminología histórica: conservar la categoría usada y analizar su función.

## M. Unidad de codificación

La unidad mínima es un segmento funcionalmente autónomo dentro de una página visualmente validada. Una misma página puede recibir múltiples códigos. El ledger debe conservar el `page_id` y, cuando sea posible, una localización del segmento dentro de la página sin redistribuir contenido expresivo sustancial.

## N. Doble codificación y acuerdo

Antes de cualquier clasificación automática:

1. seleccionar una muestra estratificada por periodo y género editorial;
2. codificarla por dos personas de manera independiente;
3. registrar desacuerdos;
4. estimar acuerdo por variable apropiada;
5. revisar definiciones una sola vez y versionar el codebook como 0.2;
6. conservar 0.1 para trazabilidad.

## O. Variables estructurales mínimas del ledger

- `validation_id`
- `page_id`
- `canonical_viewer_key`
- `generation`
- `grade`
- `domain_or_subject`
- `source_position`
- `source_asset_url`
- `source_sha256`
- `ocr_sha256`
- `query_family`
- `validation_status`
- `reference_type`
- `named_language`
- `status_label`
- `temporality`
- `speaker_agency`
- `relation_to_spanish`
- `territorial_function`
- `pedagogical_function`
- `normative_frame`
- `risk_frame`
- `evaluative_polarity`
- `coder_id`
- `validation_date`
- `notes_nonexpressive`
