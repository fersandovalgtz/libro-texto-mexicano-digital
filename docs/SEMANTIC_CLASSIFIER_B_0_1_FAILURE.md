# SEMB 0.1 — fallo de preflight sintético

Fecha: 2026-08-15

## Estado

**FAILED PRE-CORPUS / NO AUTORIZADO PARA EJECUCIÓN SOBRE LTMD.**

SEMB 0.1 fue diseñado como segunda especificación independiente de RULEA 0.1, usando embeddings del modelo multilingüe pinneado y dos prototipos sintéticos por categoría. Antes de ejecutar sobre el corpus se sometió a frases held-out inventadas.

Run: `31901707791`.

Primer fallo:

- frase sintética: `Examina con atención las hojas y usa lo que notes para responder.`
- categoría esperada: `observe`
- etiquetas seleccionadas por 0.1: `experiment;decide;investigate`
- top scores: experiment 0.943013; decide 0.916677; investigate 0.910287; predict 0.908247; explain 0.906823.
- `observe` no apareció entre las cinco categorías con mayor score.

## Conclusión

No se trata como un problema de threshold aislado. Las similitudes absolutas son demasiado altas entre categorías y la categoría esperada ni siquiera obtiene ranking cercano. Por ello:

1. no se ejecuta SEMB 0.1 sobre fragmentos LTMD;
2. no se observan scores del corpus para recalibrar B;
3. se diagnostica exclusivamente con prototipos/frases sintéticas;
4. cualquier cambio de prototipos o función de score abrirá una nueva versión SEMB 0.2;
5. SEMB 0.1 se conserva como intento fallido reproducible.

Diagnósticos lanzados:

- `tests/diagnose_semantic_classifier_B.py` / workflow `Diagnose SEMB prototype geometry`;
- `tests/evaluate_semantic_scoring_alternatives.py` / workflow `Evaluate SEMB scoring alternatives`.

Ambos están prohibidos de leer corpus, etiquetas A o regex de RULEA.
