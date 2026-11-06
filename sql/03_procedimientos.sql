CREATE OR ALTER PROCEDURE dbo.sp_ConsultarSismos
    @magnitud_minima DECIMAL(5,2) = 0
AS
BEGIN
    SET NOCOUNT ON;

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
    ORDER BY fecha_utc DESC;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_EstadisticasSismos
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        COUNT(*) AS total_sismos,
        AVG(magnitud) AS magnitud_promedio,
        MAX(magnitud) AS magnitud_maxima,
        MIN(magnitud) AS magnitud_minima
    FROM dbo.EventosSismicos;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_SismosPorRegion
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        region,
        COUNT(*) AS total_sismos,
        AVG(magnitud) AS magnitud_promedio,
        MAX(magnitud) AS magnitud_maxima
    FROM dbo.EventosSismicos
    GROUP BY region
    ORDER BY total_sismos DESC;
END;
GO