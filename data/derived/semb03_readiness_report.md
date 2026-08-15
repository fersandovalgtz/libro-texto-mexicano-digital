# Estado de preparación SEMB 0.3

Versión: `SEMB03_READINESS_0.1`.

**Etapa actual: `WAITING_HUMAN_REFERENCE`.**

La infraestructura pública previa a referencia humana se verifica sin abrir salidas A/B ni resultados históricos.

## Controles
- PASS — `sample_n_480`: n=480
- PASS — `sample_unique_ids`: sample_id unique
- PASS — `sample_unique_fragments`: fragment_id unique
- PASS — `roles_320_160`: {'development': 320, 'locked_validation': 160}
- PASS — `generations_balanced`: {'1972': 120, '1988': 120, '1993': 120, '2014': 120}
- PASS — `template_blinded_fields`: forbidden_present=[]
- PASS — `template_n_480`: n=480
- PASS — `opaque_sample_ids`: all IDs opaque
- PASS — `template_matches_master`: same 480 IDs
- PASS — `reliability_n_120`: n=120
- PASS — `reliability_subset_of_master`: all reliability IDs valid
- PASS — `criteria_frozen`: SEMB03_ACCEPTANCE_0.1

## Artefactos de etapas posteriores
- `human_reference_consensus`: ausente
- `development_result`: ausente
- `model_lock`: ausente
- `locked_validation_result`: ausente
- `production_manifest`: ausente

## Lectura
Mientras la etapa sea `WAITING_HUMAN_REFERENCE`, el bloqueo es deliberado: puede ampliarse la infraestructura y las pruebas sintéticas, pero no debe fabricarse una referencia humana ni abrirse la validación bloqueada.
