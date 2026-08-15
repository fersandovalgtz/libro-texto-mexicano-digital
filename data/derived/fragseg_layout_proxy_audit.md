# Auditoría de layout para `heading_candidate`

Versión: `FRAGSEG_LAYOUT_PROXY_0.1`. Muestra determinista: 20 `heading_candidate` + 20 `expository_candidate` por generación (n=160).

La auditoría reconstruye OCR sólo temporalmente, verifica SHA-256 y persiste únicamente rasgos geométricos. No constituye validación humana de encabezados.

## Resumen
- 1972 heading_candidate: n=20, mediana height-ratio=1.0, ≥1.2=5.0%, mayúsculas ≥80%=0.0%, puntuación terminal=70.0%.
- 1972 expository_candidate: n=20, mediana height-ratio=1.0, ≥1.2=0.0%, mayúsculas ≥80%=0.0%, puntuación terminal=85.0%.
- 1988 heading_candidate: n=20, mediana height-ratio=1.0, ≥1.2=5.0%, mayúsculas ≥80%=0.0%, puntuación terminal=60.0%.
- 1988 expository_candidate: n=20, mediana height-ratio=1.0, ≥1.2=0.0%, mayúsculas ≥80%=0.0%, puntuación terminal=100.0%.
- 1993 heading_candidate: n=20, mediana height-ratio=1.0, ≥1.2=25.0%, mayúsculas ≥80%=5.0%, puntuación terminal=40.0%.
- 1993 expository_candidate: n=20, mediana height-ratio=1.0, ≥1.2=10.0%, mayúsculas ≥80%=0.0%, puntuación terminal=85.0%.
- 2014 heading_candidate: n=20, mediana height-ratio=0.9375, ≥1.2=15.0%, mayúsculas ≥80%=0.0%, puntuación terminal=50.0%.
- 2014 expository_candidate: n=20, mediana height-ratio=1.0, ≥1.2=10.0%, mayúsculas ≥80%=0.0%, puntuación terminal=80.0%.

## Uso permitido
Los rasgos de layout sirven para estimar si la categoría residual posee saliencia tipográfica distinta de texto expositivo. No autorizan llamar “encabezado real” a un fragmento individual ni sustituir una auditoría visual independiente.
