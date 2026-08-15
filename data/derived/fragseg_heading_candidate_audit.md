# Auditoría de `heading_candidate` en FRAGSEG

Versión: `FRAGSEG_HEADING_AUDIT_0.1`. Esta auditoría usa sólo metadatos persistidos. No lee OCR ni clasificadores semánticos.

## Advertencia de constructo

`heading_candidate` no es un detector tipográfico de encabezados. En FRAGSEG es una categoría residual basada en longitud: después de descartar señales de evaluación, proyecto, experimento, actividad, pregunta e instrucción, una unidad de ≤12 tokens y ≤100 caracteres recibe esa etiqueta. Por ello, su prevalencia no debe interpretarse como prevalencia histórica de encabezados reales.

## Perfil por generación

- 1972: 856/2809 (30.47%) `heading_candidate`; 40.65% de esos candidatos tienen <4 tokens y 59.35% tienen 4–12 tokens; 94.74% de las páginas contienen al menos uno.
- 1988: 569/1631 (34.89%) `heading_candidate`; 45.34% de esos candidatos tienen <4 tokens y 54.66% tienen 4–12 tokens; 96.05% de las páginas contienen al menos uno.
- 1993: 1176/2513 (46.80%) `heading_candidate`; 38.78% de esos candidatos tienen <4 tokens y 61.22% tienen 4–12 tokens; 98.06% de las páginas contienen al menos uno.
- 2014: 1536/2641 (58.16%) `heading_candidate`; 44.47% de esos candidatos tienen <4 tokens y 55.53% tienen 4–12 tokens; 100.00% de las páginas contienen al menos uno.

## Consecuencia metodológica

El crecimiento histórico de esta categoría debe tratarse como una señal de fragmentación/longitud hasta que una validación visual independiente determine qué proporción corresponde a encabezados tipográficos verdaderos. No debe utilizarse como hallazgo histórico primario ni como razón automática para excluir texto de SEMB 0.3.
