# Decisiones técnicas

## Sobre el pipeline

El pipeline de datos está orquestado en el script `scripts/pipeline.py`, que implementa
el pipeline en tres etapas:
	*** extracción 
		extrae datos horarios de temperatura y precipitación de la API pública Open-Meteo 
		para la CDMX.
	***	transformación
		limpia los datos y los  transforma con pandas (conversión de fechas, filtrado
		por rango de horario, detección de nulos y negativos [estos se imprimen en pantalla]).
	*** exportación
		exporta a CSV y a una base de datos SQLite local sobre la cual se ejecutan 
		cuatro consultas de análisis.

## Sobre las consultas SQL

Las cuatro consultas están en `sql/consultas.sql` y se ejecutan dinámicamente
desde `pipeline.py`, que lee el archivo y separa las consultas por `;`. 
Es el archivo SQL desde donde se lee las consultas directamente.

**Consulta A — temperatura promedio por día**
	agrupa por día calendario y promedia la temperatura. Se ordena DESC para 
	ver primero los días más calurosos.

**Consulta B — horas con precipitación**
	filtra únicamente las horas donde llovió (precipitacion_mm > 0) y las 
	ordena cronológicamente [ASC en fecha]. Si no llovió en el periodo, el 
	resultado es vacío (también es información).

**Consulta C — variación térmica**
	calcula la diferencia entre máxima y mínima por día. Se usa LIMIT 1 para 
	devolver únicamente el día que tuvo la mayor oscilación.

**Consulta D — resumen diario**
	en una sola consulta se encuentran los cuatro indicadores por día: 
	mínima, máxima, promedio y precipitación acumulada.

## Sobre las dificultades encontradas

Los datos obtenidos de la API de Open-Meteo llegaron limpios: sin nulos, 
sin negativos y sin formatos inconsistentes. Entre las dificultades técnicas 
podemos nombrar, únicamente, la lógica de detección de registros problemáticos: 
la primera versión que escribí contaba celdas, no filas. Se corrigió usando 
`.any(axis=1)` para contar más bien los registros afectados.

## Sobre otras decisiones importantes

**SQLite sobre PostgreSQL:** 
	este ejercicio se trata de uno a nivel local, y de un alcance bastante acotado. Así,
	SQLite resulta suficiente, no hay necesidad de levantar un servidor (que PostgreSQL, 
	por ejemplo, habría necesitado). En un entorno de producción, probablemente
	usaría PostgreSQL, que es con lo que tengo experiencia en el proyecto SIIES de la UNAM.

**`requests` con `raise_for_status()`:** 
	tomé la decisión de manejar los errores HTTP de forma explícita en lugar de solo 
	verificar el status code. Esto permite capturar cualquier código de error 4xx o 5xx 
	de forma limpia y con suficiente consistencia.

**Timeout**
	se usó un timeout=10 en la API para evitar bloqueos indefinidos.

**Filtro de horario 06:00–22:00:** 
	las horas requeridas por el ejercicio. Además, podemos ver que probablemente se trata de
	horas operativas relevantes (fuera queda la alta noche y la madrugada).
	
**Nulos y negativos**
	únicamente se muestra la cantidad de registros con nulos o negativos, no se los elimina
	(¿podrían ser datos relevantes a futuro?)
	
**Librerías**
	`requests` 
		para el consumo de la API. Es la librería estándar de Python para HTTP 
	`pandas` 
		para la transformación, usada por el manejo de datos tabulares 
	`sqlite3` 

## Sobre el futuro

Podrían corregirse: 

- Parametrizar fechas y coordenadas via argumentos de línea de comandos
- Escribir pruebas unitarias para las funciones de limpieza
- Orquestar el pipeline con Airflow para ejecución programada
- Cambiar las rutas a pathlib en vez de correrse desde la raíz