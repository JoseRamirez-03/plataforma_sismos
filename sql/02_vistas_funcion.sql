CREATE OR ALTER VIEW dbo.vw_EventosSismicos
AS
SELECT
    id_usgs,
    fecha_utc,
    magnitud,
    profundidad_km,
    latitud,
    longitud,
    lugar,
    region
FROM dbo.EventosSismicos;
GO

CREATE OR ALTER VIEW dbo.vw_SismosPorRegion
AS
SELECT
    region,
    COUNT(*) AS total_sismos,
    AVG(magnitud) AS magnitud_promedio,
    MAX(magnitud) AS magnitud_maxima
FROM dbo.EventosSismicos
GROUP BY region;
GO

CREATE OR ALTER VIEW dbo.vw_EstadisticasSismicas
AS
SELECT
    COUNT(*) AS total_sismos,
    AVG(magnitud) AS magnitud_promedio,
    MAX(magnitud) AS magnitud_maxima,
    MIN(magnitud) AS magnitud_minima
FROM dbo.EventosSismicos;
GO

CREATE OR ALTER FUNCTION dbo.fn_SismosPorMagnitud
(
    @magnitud_minima DECIMAL(5,2)
)
RETURNS TABLE
AS
RETURN
(
    SELECT
        id_usgs,
        fecha_utc,
        magnitud,
        profundidad_km,
        latitud,
        longitud,
        lugar,
        region
    FROM dbo.EventosSismicos
    WHERE magnitud >= @magnitud_minima
);
GO