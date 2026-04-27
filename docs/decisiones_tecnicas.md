# Decisiones Técnicas — Evaluación Data Engineer

## ¿Qué hace el pipeline?

El script `scripts/pipeline.py` implementa un pipeline de tres etapas:
extrae datos horarios de temperatura y precipitación de la API pública Open-Meteo
para la CDMX, los limpia y transforma con pandas (conversión de fechas, filtrado
por horario, detección de nulos y negativos), y los exporta a CSV y a una base de
datos SQLite local sobre la cual se ejecutan cuatro consultas de análisis.

## Decisiones importantes

**SQLite sobre PostgreSQL:** dado que el ejercicio es local y de alcance acotado,
SQLite es suficiente y elimina la necesidad de levantar un servidor. En un entorno
de producción usaría PostgreSQL, que es con lo que tengo experiencia en el proyecto
SIIES de la UNAM.

**`requests` con `raise_for_status()`:** elegí manejar errores HTTP de forma
explícita en lugar de solo verificar el status code manualmente, porque permite
capturar cualquier código de error 4xx o 5xx de forma limpia y consistente.

**Filtro de horario 06:00–22:00:** interpretado como horas operativas relevantes
para análisis de movilidad urbana, que es el contexto del caso.

## ¿Qué mejoraría con más tiempo?

- Parametrizar fechas y coordenadas via argumentos de línea de comandos
- Agregar logging estructurado en lugar de prints
- Escribir pruebas unitarias para las funciones de limpieza
- Orquestar el pipeline con Airflow para ejecución programada