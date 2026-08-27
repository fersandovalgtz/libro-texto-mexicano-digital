# SEMB 0.3 — nota de enlace criptográfico del holdout

Esta nota complementa `SEMB03_HOLDOUT_INTEGRITY_0_1.md` sin modificar su registro histórico.

El reemplazo privado del holdout debe quedar ligado no sólo al SHA-256 del manifiesto privado, sino también al universo exacto del que se seleccionó. `scripts/prepare_semb03_private_holdout.py` registra en el compromiso público tanto el SHA-256 de `data/derived/fragment_manifest.csv` como su Git blob SHA. Ninguno de estos campos revela los 160 `fragment_id` privados.

`semb03_model_lock.json` sólo puede crearse cuando existe un compromiso válido de 160 casos, 40 por generación, que excluye las 480 identidades de la muestra pública histórica, declara `ids_public=false` y contiene hashes válidos del manifiesto privado y del manifiesto fuente.

El workflow `sample-semb03-human-reference.yml` deja de publicar muestras y funciona como auditoría de sólo lectura. El antiguo generador público exige `--legacy-audit-rebuild`; su única función futura es reproducir el artefacto histórico expuesto, nunca generar una validación final.

Esta remediación no crea referencia humana ni cambia cobertura semántica: U1 permanece en 0/542 hasta que el protocolo humano se ejecute y valide.
