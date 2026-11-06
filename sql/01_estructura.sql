CREATE TABLE dbo.EventosSismicos (
    id_usgs NVARCHAR(50) NOT NULL PRIMARY KEY,
    fecha_utc DATETIME2 NOT NULL,
    magnitud DECIMAL(4,2) NOT NULL,
    profundidad_km DECIMAL(8,2),
    latitud DECIMAL(9,6) NOT NULL,
    longitud DECIMAL(9,6) NOT NULL,
    lugar NVARCHAR(400) NOT NULL,
    region NVARCHAR(120) NOT NULL,
    actualizado_en DATETIME2 DEFAULT SYSUTCDATETIME()
);