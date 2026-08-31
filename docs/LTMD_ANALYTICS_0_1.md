# LTMD Analytics 0.1 — arquitectura de producto y contrato epistemológico

Versión: **LTMD_ANALYTICS_0.1**  
Fecha de decisión: **2026-08-30**

## 1. Propósito

LTMD Analytics es la capa operada de consulta, agregación, comparación, visualización y exportación construida sobre la infraestructura científica de LTMD. Su valor no reside en revender libros fuente ni en redistribuir OCR íntegro, sino en reducir el trabajo necesario para formular y explorar preguntas longitudinales con trazabilidad documental.

El flujo P0 es:

`buscar → filtrar → comparar → visualizar → exportar → citar`

La identidad pública prioritaria del producto es institucional: **Universidad Centro de Estudios Especializados en Educación Superior, Cuauhtémoc (Universidad CEEES)**. La autoría y responsabilidad científica individual se preservan donde sean necesarias para citación, procedencia, licencias, ORCID, releases o responsabilidad metodológica.

## 2. Separación de capas

### LTMD Open

Repositorio público de metodología, código, metadatos, métricas, esquemas, documentación y derivados no sustitutivos que puedan publicarse legítimamente.

### LTMD Analytics

Experiencia operada para búsqueda longitudinal, filtros, agregaciones, comparación, visualización, exportación y citación. Puede consumir reconstrucciones privadas de FTRL, pero no expone automáticamente texto OCR, bytes fuente o materiales cuya redistribución no esté autorizada.

### LTMD Services

Servicios especializados: datasets derivados a medida, API operada, informes, estudios, integración institucional, soporte y curaduría.

## 3. Estados epistemológicos obligatorios

Toda superficie de Analytics debe distinguir al menos estos estados:

- `technical_metadata`: identidad, procedencia o métrica técnica verificable;
- `computational_candidate`: observación recuperada por regla, búsqueda o modelo, pendiente de validación humana del constructo;
- `exploratory_signal`: agregado derivado de candidatos computacionales, apto para exploración y priorización de investigación;
- `human_validated` / `semantic_ready`: reservado exclusivamente para observaciones que hayan superado el protocolo humano aplicable.

Reglas permanentes:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `computational_candidate != semantic_ready`;
- una tendencia atractiva no justifica modificar thresholds retrospectivamente;
- la interfaz nunca debe omitir el estado epistemológico de una salida.

## 4. Privacidad y derechos

La capa de producto no debe publicar por defecto:

- JPEG/PDF fuente;
- OCR íntegro;
- reconstrucciones secuenciales que sustituyan al libro;
- fragmentos extensos;
- rutas privadas, secretos o claves de preservación.

Sí puede trabajar con metadatos, conteos, tasas, frecuencias, hashes públicos admisibles, estados, etiquetas, distribuciones, agregados y otros derivados no sustitutivos conforme a la gobernanza del proyecto.

## 5. Primer vertical: lenguas indígenas

El primer vertical demostrable de LTMD Analytics utiliza el estudio `LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2` como fuente computacional preregistrada.

El rerun permanece separado de la validación humana. Las páginas recuperadas mantienen `validation_status=not_visually_validated` mientras no exista revisión humana.

El vertical debe permitir explorar:

- páginas candidatas por generación;
- páginas `explicit_general` y `named_language_contextual`;
- libros candidatos por generación;
- distribución por grado y ola/dominio;
- lenguas nombradas por generación, grado y dominio;
- términos explícitos por generación;
- tasas por 1,000 páginas cuando exista denominador técnico válido;
- exportación de agregados públicos seguros.

El vertical **no** debe presentar los conteos como prevalencia histórica validada ni afirmar significado contextual más allá de las reglas de recuperación.

## 6. Data mart público-seguro 0.1

`scripts/build_indigenous_analytics_mart.py` transforma el ledger privado de candidatos en cinco tablas derivadas:

1. `ltmd_analytics_indigenous_generation_0_1.csv`;
2. `ltmd_analytics_indigenous_strata_0_1.csv`;
3. `ltmd_analytics_indigenous_language_matrix_0_1.csv`;
4. `ltmd_analytics_indigenous_explicit_terms_0_1.csv`;
5. `ltmd_analytics_indigenous_validation_state_0_1.csv`.

La salida excluye deliberadamente `page_id`, URL fuente, hashes de página/OCR, texto OCR, snippets, formas textuales por página y otras columnas que aumentarían el riesgo de reconstrucción o exposición innecesaria.

Cada fila de agregados incorpora `epistemic_state` y sólo utiliza `computational_candidate` o `exploratory_signal` en esta versión.

## 7. Ejecución

```bash
python scripts/build_indigenous_analytics_mart.py \
  --candidate-ledger /ruta/privada/ltmd_u1_indigenous_languages_candidate_ledger_0_2.csv \
  --generation-summary /ruta/privada/ltmd_u1_indigenous_languages_generation_summary_0_2.csv \
  --output-dir /ruta/de/salida
```

El denominador por generación es opcional. Si no se proporciona, Analytics conserva conteos pero deja vacías las tasas por 1,000 páginas en lugar de inventar un denominador.

## 8. Contrato de interfaz P0

Una consulta de Analytics debe poder producir, como mínimo:

```json
{
  "query": "lenguas indígenas",
  "filters": {
    "generation": ["1993", "2014"],
    "grade_code": ["5", "6"],
    "wave": ["W3", "W7"]
  },
  "result_state": "exploratory_signal",
  "metrics": {
    "candidate_pages": 0,
    "candidate_books": 0
  },
  "provenance": {
    "analysis_version": "LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2",
    "analytics_version": "LTMD_ANALYTICS_INDIGENOUS_0.1"
  }
}
```

Los valores anteriores son estructura, no resultados reales.

## 9. Roadmap inmediato

P0:

1. materializar el data mart del vertical de lenguas indígenas;
2. fijar contrato de respuesta y filtros;
3. implementar una API de consulta sobre derivados, no sobre OCR expuesto;
4. construir interfaz mínima de búsqueda/filtros;
5. añadir comparación longitudinal y visualización;
6. exportar resultados derivados con procedencia y estado epistemológico;
7. instrumentar uso para validar comercialmente el producto.

P1 sólo después de un P0 funcional:

- guardado de consultas;
- workspaces de investigación;
- colaboración;
- API con autenticación/cuotas;
- segundo vertical temático;
- informes y datasets a medida integrados al flujo comercial.

## 10. Validación humana diferida

La decisión operativa de 2026-08-30 difiere temporalmente la revisión humana sin eliminarla. Los protocolos, ledgers, colas y muestras preregistradas deben conservarse íntegros.

Analytics puede avanzar con resultados computacionales explícitamente etiquetados; no puede usar la ausencia de revisión humana como razón para promover resultados a `semantic_ready`.
