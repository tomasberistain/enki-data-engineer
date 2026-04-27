-- Consulta A: Temperatura promedio por día (orden: del más caluroso al más frío [DESC])

SELECT 
	DATE(fecha) AS dia,
	ROUND(AVG(temperatura_c),2) AS temp_promedio
FROM clima
GROUP BY DATE(fecha)
ORDER BY temp_promedio DESC;



-- Consulta B: Horas con precipitación mayor a 0 mm, ordenadas cronológicamente [fecha ASC]

SELECT 
    DATE(fecha) AS dia,
    TIME(fecha) AS hora,
    precipitacion_mm
FROM clima
WHERE precipitacion_mm > 0
ORDER BY fecha ASC;



-- Consulta C: Día con mayor variación térmica 

SELECT 
    DATE(fecha) AS dia,
    ROUND(MAX(temperatura_c) - MIN(temperatura_c), 2) AS variacion_termica
FROM clima
GROUP BY DATE(fecha)
ORDER BY variacion_termica DESC
LIMIT 1;



-- Consulta D: Resumen diario

SELECT 
    DATE(fecha) AS dia,
    ROUND(MIN(temperatura_c), 2) AS temp_minima,
    ROUND(MAX(temperatura_c), 2) AS temp_maxima,
    ROUND(AVG(temperatura_c), 2) AS temp_promedio,
    ROUND(SUM(precipitacion_mm), 2) AS precipitacion_total
FROM clima
GROUP BY DATE(fecha)
ORDER BY dia ASC;