# Flujo de trabajo del piloto

1. **Inventario** — localizar libros candidatos y registrar sólo hechos verificables.
2. **Continuidad** — identificar el grado con presencia comparable en 1972, 1988, 1993 y 2014.
3. **Procedencia** — guardar URL, fecha de acceso, identificador y notas de derechos.
4. **Copia de trabajo** — procesar localmente materiales fuente sin incorporarlos al historial de Git.
5. **Extracción** — obtener texto o OCR por página y registrar calidad.
6. **Segmentación** — identificar fragmentos, consignas, preguntas, actividades e imágenes.
7. **Anotación** — aplicar categorías del modelo de datos con muestra revisada manualmente.
8. **Validación** — estimar error de OCR y consistencia de categorías.
9. **Derivación** — producir conteos, variables y tablas publicables.
10. **Análisis** — comparar generaciones y documentar cambios, continuidades y límites.
11. **Decisión** — escalar, reformular o detener según valor científico y costo.

## Regla de reproducibilidad

Toda transformación que afecte a datos publicables debe quedar representada por código versionado o por una decisión metodológica documentada. Los pasos exclusivamente manuales deberán registrar responsable, fecha y criterio aplicado.
