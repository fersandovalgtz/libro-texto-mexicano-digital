# Memorando de decisión de licencias — LTMD 0.1

Fecha: **2026-08-15**  
Estado: **decisión adoptada y materializada para v0.1.0-rc.1**.

## Decisión

LTMD adopta una política de doble licencia con separación estricta de alcance:

1. **software original LTMD:** Apache License 2.0;
2. **datos y derivados originales licenciables de LTMD:** Creative Commons Attribution 4.0 International (CC BY 4.0);
3. **materiales fuente CONALITEG/SEP/terceros:** fuera de ambas concesiones salvo derecho o autorización independiente aplicable.

La implementación se encuentra en los archivos raíz `LICENSE` y `DATA_LICENSE.md`.

## Código propio: Apache License 2.0

Apache-2.0 se aplica al software, scripts y workflows originales sobre los que el titular o los contribuidores correspondientes posean/controlen los derechos necesarios. La licencia permite reutilización, modificación y distribución bajo sus términos y contiene disposiciones expresas sobre contribuciones y patentes.

El texto oficial completo se conserva en `LICENSE`; no se sustituye por una paráfrasis.

## Datos y derivados originales: CC BY 4.0

CC BY 4.0 se aplica únicamente a los metadatos, tablas analíticas, códigos, etiquetas, métricas, estructuras originales y otros derivados propios **en la medida en que existan derechos licenciables y el licenciante posea o controle los derechos necesarios**.

`DATA_LICENSE.md` contiene:

- alcance positivo de la concesión;
- atribución recomendada;
- exclusión explícita de CONALITEG, SEP y terceros;
- exclusión de libros, páginas, PDF/JPEG, portadas, ilustraciones, texto fuente y OCR sustitutivo;
- separación respecto de la licencia de software;
- regla conservadora para materiales ambiguos o mixtos.

## Por qué se eligió CC BY 4.0 y no CC0

CC0 maximizaría reutilización, pero no exige atribución. Para este corte se privilegia CC BY 4.0 porque LTMD es una infraestructura académica cuya procedencia, autoría y citación deben permanecer explícitas, sin impedir adaptación y reutilización amplia de derivados propios.

## Por qué no NC/ND

Las restricciones NonCommercial y NoDerivatives dificultarían reutilización, transformación, validación y análisis derivados —usos centrales de una infraestructura científica. Por ello no se adoptaron para los derivados originales de LTMD.

## Separación de los materiales fuente

Ninguna licencia adoptada por LTMD pretende conceder derechos sobre obras, páginas, imágenes, ilustraciones, texto u otros materiales que el proyecto no posea o controle. El acceso público al Catálogo Histórico no se interpreta por sí mismo como licencia abierta de redistribución.

El modelo operativo continúa siendo:

`fuente oficial → descarga/reconstrucción temporal → verificación SHA-256 → análisis → persistencia de derivados permitidos → eliminación de copia temporal`.

## Irrevocabilidad y alcance

La decisión se tomó con alcance deliberadamente limitado. Los permisos concedidos válidamente bajo licencias abiertas no deben tratarse como revocables a voluntad frente a quienes ya recibieron el material bajo esos términos. Por ello `DATA_LICENSE.md` evita cualquier formulación que pueda confundirse con relicenciamiento general del corpus fuente.

## Verificación automatizada

`check-release-candidate.py` no considera suficiente la mera existencia de archivos llamados `LICENSE` y `DATA_LICENSE.md`:

- verifica marcadores sustantivos de Apache License 2.0;
- verifica CC BY 4.0;
- exige exclusión explícita CONALITEG/SEP;
- exige limitación a derechos poseídos/controlados por el licenciante;
- mantiene los derechos como una capa separada de integridad y de los gates científicos.

Tras la materialización de ambas licencias, el preflight de `v0.1.0-rc.1` registra `publish_ready=true` y `publish_blockers=[]`.

## Estado científico independiente de la licencia

Esta decisión habilita la reutilización jurídica de las contribuciones propias cubiertas, pero **no valida SEMB 0.3, no convierte SEMB 0.2 en clasificador definitivo y no autoriza resultados históricos sustantivos adicionales**. La release sigue siendo metodológica/técnica.

## Fuentes de referencia

- Apache License 2.0: https://www.apache.org/licenses/LICENSE-2.0
- Apache, aplicación/licenciamiento: https://www.apache.org/legal/apply-license
- Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/
- Creative Commons FAQ: https://creativecommons.org/faq/
- Ley Federal del Derecho de Autor — Cámara de Diputados: https://www.diputados.gob.mx/LeyesBiblio/ref/lfda.htm

## Conclusión

La combinación **Apache-2.0 para software + CC BY 4.0 para derivados originales licenciables**, acompañada por exclusiones inequívocas de materiales fuente, queda adoptada como política de `v0.1.0-rc.1`. El DOI continúa fuera de esta decisión y sólo debe incorporarse cuando exista un depósito real de la release correspondiente.
