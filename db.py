import os
import pyodbc
from pymongo import MongoClient, ReplaceOne
from dotenv import load_dotenv

load_dotenv()


def conectar_sql():
    cadena = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER=tcp:{os.environ['SQL_SERVER']},1433;"
        f"DATABASE={os.environ['SQL_DATABASE']};"
        f"UID={os.environ['SQL_USER']};"
        f"PWD={os.environ['SQL_PASSWORD']};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    return pyodbc.connect(cadena, timeout=30)


def conectar_mongo():
    return MongoClient(
        os.environ["MONGO_URI"],
        serverSelectionTimeoutMS=15000
    )


def guardar_mongo(features):
    if not features:
        return

    cliente = conectar_mongo()

    try:
        base = cliente[os.environ["MONGO_DATABASE"]]
        coleccion = base["eventos_raw"]

        operaciones = []

        for feature in features:
            documento = {
                "_id": feature["id"],
                "evento": feature
            }

            operaciones.append(
                ReplaceOne(
                    {"_id": feature["id"]},
                    documento,
                    upsert=True
                )
            )

        coleccion.bulk_write(
            operaciones,
            ordered=False
        )

    finally:
        cliente.close()


def guardar_sql_basico(cursor, evento):
    datos = (
        evento["id_usgs"],
        evento["fecha_utc"],
        evento["magnitud"],
        evento["profundidad_km"],
        evento["latitud"],
        evento["longitud"],
        evento["lugar"],
        evento["region"]
    )

    cursor.execute(
        """
        SELECT 1
        FROM dbo.EventosSismicos
        WHERE id_usgs = ?
        """,
        evento["id_usgs"]
    )

    existe = cursor.fetchone()

    if existe:
        cursor.execute(
            """
            UPDATE dbo.EventosSismicos
            SET fecha_utc = ?,
                magnitud = ?,
                profundidad_km = ?,
                latitud = ?,
                longitud = ?,
                lugar = ?,
                region = ?,
                actualizado_en = SYSUTCDATETIME()
            WHERE id_usgs = ?
            """,
            evento["fecha_utc"],
            evento["magnitud"],
            evento["profundidad_km"],
            evento["latitud"],
            evento["longitud"],
            evento["lugar"],
            evento["region"],
            evento["id_usgs"]
        )

    else:
        cursor.execute(
            """
            INSERT INTO dbo.EventosSismicos
            (
                id_usgs,
                fecha_utc,
                magnitud,
                profundidad_km,
                latitud,
                longitud,
                lugar,
                region
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            *datos
        )


def guardar_sql_avanzado(cursor, evento):
    cursor.execute(
        """
        EXEC dbo.sp_guardar_evento
            @id_usgs = ?,
            @fecha_utc = ?,
            @magnitud = ?,
            @profundidad_km = ?,
            @latitud = ?,
            @longitud = ?,
            @lugar = ?,
            @region = ?
        """,
        evento["id_usgs"],
        evento["fecha_utc"],
        evento["magnitud"],
        evento["profundidad_km"],
        evento["latitud"],
        evento["longitud"],
        evento["lugar"],
        evento["region"]
    )