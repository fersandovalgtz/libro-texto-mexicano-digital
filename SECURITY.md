# Política de seguridad

## Versiones

La rama `main` y la release pública más reciente reciben atención de seguridad. Los tags históricos se preservan como registros inmutables y no se reescriben.

## Reporte responsable

No publique inicialmente secretos, credenciales, datos personales, rutas privadas, información que facilite explotación o material de terceros restringido. Para vulnerabilidades técnicas, utilice los mecanismos privados de reporte de seguridad de GitHub cuando estén habilitados o contacte al responsable del repositorio por un canal institucional verificable.

## Alcance

Son relevantes, entre otros:

- exposición accidental de credenciales o tokens;
- workflows con permisos excesivos;
- dependencias vulnerables con impacto reproducible;
- escritura o publicación no intencional de materiales fuente restringidos;
- fallos que comprometan integridad, hashes, manifiestos o trazabilidad de resultados.

Las discrepancias científicas, problemas de datos y propuestas metodológicas ordinarias deben gestionarse mediante issues o pull requests, no como vulnerabilidades de seguridad.

## Principio de mínimo privilegio

Los workflows, tokens y acciones automatizadas deben operar con el menor conjunto de permisos necesario. Los secretos no deben almacenarse en el repositorio ni incorporarse a artefactos de release.
