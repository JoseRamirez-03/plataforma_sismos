IF OBJECT_ID('dbo.AuditoriaSismos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.AuditoriaSismos (
        id_auditoria INT IDENTITY(1,1) PRIMARY KEY,
        id_usgs NVARCHAR(100),
        fecha_registro DATETIME2 DEFAULT SYSDATETIME(),
        accion NVARCHAR(50)
    );
END;
GO

CREATE OR ALTER TRIGGER dbo.tr_AuditoriaSismos
ON dbo.EventosSismicos
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.AuditoriaSismos (
        id_usgs,
        accion
    )
    SELECT
        id_usgs,
        'INSERT'
    FROM inserted;
END;
GO