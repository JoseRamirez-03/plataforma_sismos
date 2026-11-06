SELECT DB_NAME() AS BaseDeDatos;

SELECT COUNT(*) AS TotalSismos
FROM dbo.EventosSismicos;

SELECT TOP 10
    id_usgs,
    fecha_utc,
    magnitud,
    profundidad_km,
    latitud,
    longitud,
    lugar,
    region
FROM dbo.EventosSismicos
ORDER BY fecha_utc DESC;

SELECT
    id_usgs,
    COUNT(*) AS Cantidad
FROM dbo.EventosSismicos
GROUP BY id_usgs
HAVING COUNT(*) > 1;