# Desarrollo sintético del gate SEMB 0.3

Versión: `SEMB03_GATE_SYNTH_DEV_0.1`. n=105 casos sintéticos; positivos=72; negativos=33.

> Este artefacto NO es validación humana ni autoriza producción. Sirve para decidir si hay arquitecturas plausibles que llevar al conjunto humano de desarrollo.

## Validación cruzada estratificada de 5 folds
- **SEMB 0.2, gate congelado:** balanced accuracy=0.526; sensibilidad=0.597; especificidad=0.455.
- **Margen con threshold seleccionado sólo en train de cada fold:** balanced accuracy=0.537; sensibilidad=0.681; especificidad=0.394.
- **Regresión logística sobre rasgos semánticos:** balanced accuracy=0.631; sensibilidad=0.625; especificidad=0.636.

Threshold de margen ajustado sobre todos los sintéticos, sólo como candidato para desarrollo humano posterior: **-0.004**.

## Regla de uso
La arquitectura logística y el threshold sintético pueden entrar como candidatos en G3, pero deberán compararse y calibrarse nuevamente usando exclusivamente los 320 casos humanos `development`. Ningún resultado histórico interviene en esta selección.
