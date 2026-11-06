import os
import math

from datetime import date, datetime
from decimal import Decimal

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from db import conectar_sql


load_dotenv()


app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)


origenes = [
    origen.strip()
    for origen in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5500"
    ).split(",")
    if origen.strip()
]

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": origenes
        }
    }
)


def modo_avanzado():
    return os.getenv("SQL_AVANZADO", "0") == "1"


def consultar_sql(consulta, parametros=()):

    conexion = conectar_sql()

    try:
        cursor = conexion.cursor()

        cursor.execute(consulta, *parametros)

        columnas = [
            columna[0]
            for columna in cursor.description
        ]

        resultados = []

        for fila in cursor.fetchall():

            registro = {}

            for columna, valor in zip(columnas, fila):

                if isinstance(valor, datetime):
                    valor = valor.isoformat() + "Z"

                elif isinstance(valor, date):
                    valor = valor.isoformat()

                elif isinstance(valor, Decimal):
                    valor = float(valor)

                registro[columna] = valor

            resultados.append(registro)

        return resultados

    finally:
        conexion.close()


def obtener_filtros():

    region = request.args.get(
        "region", ""
    ).strip()

    desde = request.args.get(
        "desde", ""
    ).strip()

    hasta = request.args.get(
        "hasta", ""
    ).strip()

    texto_magnitud = request.args.get(
        "min_mag", ""
    ).strip()

    if len(region) > 120:
        raise ValueError("La region es demasiado larga")

    if desde:
        date.fromisoformat(desde)

    if hasta:
        date.fromisoformat(hasta)

    if desde and hasta and desde > hasta:
        raise ValueError("Las fechas estan invertidas")

    magnitud = None

    if texto_magnitud:
        magnitud = float(texto_magnitud)

        if not math.isfinite(magnitud):
            raise ValueError("Magnitud no valida")

        if not -2 <= magnitud <= 10:
            raise ValueError("Magnitud fuera de rango")

    condiciones = ["1=1"]

    parametros = []

    if region:
        condiciones.append("region = ?")
        parametros.append(region)

    if desde:
        condiciones.append("fecha_utc >= ?")
        parametros.append(desde)

    if hasta:
        condiciones.append(
            "fecha_utc < DATEADD(DAY, 1, CAST(? AS DATE))"
        )
        parametros.append(hasta)

    if magnitud is not None:
        condiciones.append("magnitud >= ?")
        parametros.append(magnitud)

    return (
        " AND ".join(condiciones),
        parametros,
        region or None,
        desde or None,
        hasta or None,
        magnitud
    )


@app.errorhandler(ValueError)
def error_parametros(error):

    return jsonify({
        "error": str(error)
    }), 400


@app.route("/")
def inicio():

    return send_from_directory(
        app.static_folder,
        "index.html"
    )


@app.route("/api/estado")
def estado():

    try:
        consultar_sql(
            "SELECT DB_NAME() AS base_de_datos"
        )

        return jsonify({
            "api": "OK",
            "azure_sql": "OK",
            "base_de_datos": "sismosdb",
            "modo": (
                "avanzado"
                if modo_avanzado()
                else "basico"
            )
        })

    except Exception:

        app.logger.exception(
            "Error al conectar con Azure SQL"
        )

        return jsonify({
            "api": "OK",
            "azure_sql": "ERROR"
        }), 503


@app.route("/api/regiones")
def regiones():

    datos = consultar_sql(
        """
        SELECT DISTINCT region
        FROM dbo.EventosSismicos
        ORDER BY region
        """
    )

    return jsonify(datos)


@app.route("/api/eventos")
def eventos():

    condicion, parametros, region, desde, hasta, magnitud = (
        obtener_filtros()
    )

    if modo_avanzado():

        datos = consultar_sql(
            """
            EXEC dbo.sp_consultar_eventos
                @region = ?,
                @desde = ?,
                @hasta = ?,
                @min_mag = ?
            """,
            (region, desde, hasta, magnitud)
        )

    else:

        consulta = f"""
            SELECT TOP (500)
                id_usgs,
                fecha_utc,
                magnitud,
                profundidad_km,
                latitud,
                longitud,
                lugar,
                region
            FROM dbo.EventosSismicos
            WHERE {condicion}
            ORDER BY fecha_utc DESC
        """

        datos = consultar_sql(
            consulta,
            parametros
        )

    return jsonify(datos)


@app.route("/api/kpis")
def kpis():

    condicion, parametros, *_ = obtener_filtros()

    consulta = f"""
        SELECT
            COUNT(*) AS total,

            AVG(
                CAST(magnitud AS FLOAT)
            ) AS magnitud_promedio,

            MAX(magnitud) AS magnitud_maxima

        FROM dbo.EventosSismicos

        WHERE {condicion}
    """

    datos = consultar_sql(
        consulta,
        parametros
    )

    return jsonify(datos[0])


@app.route("/api/por-region")
def por_region():

    condicion, parametros, *_ = obtener_filtros()

    if modo_avanzado() and not request.args:

        datos = consultar_sql(
            """
            SELECT
                region,
                total,
                magnitud_promedio,
                magnitud_maxima

            FROM dbo.vw_por_region

            ORDER BY total DESC
            """
        )

    else:

        consulta = f"""
            SELECT
                region,

                COUNT(*) AS total,

                AVG(
                    CAST(magnitud AS FLOAT)
                ) AS magnitud_promedio,

                MAX(magnitud) AS magnitud_maxima

            FROM dbo.EventosSismicos

            WHERE {condicion}

            GROUP BY region

            ORDER BY total DESC
        """

        datos = consultar_sql(
            consulta,
            parametros
        )

    return jsonify(datos)


@app.route("/api/por-mes")
def por_mes():

    condicion, parametros, *_ = obtener_filtros()

    if modo_avanzado() and not request.args:

        datos = consultar_sql(
            """
            SELECT
                periodo,
                SUM(total) AS total

            FROM dbo.vw_por_mes

            GROUP BY periodo

            ORDER BY periodo
            """
        )

    else:

        consulta = f"""
            SELECT
                CONVERT(
                    CHAR(7),
                    fecha_utc,
                    126
                ) AS periodo,

                COUNT(*) AS total

            FROM dbo.EventosSismicos

            WHERE {condicion}

            GROUP BY
                CONVERT(
                    CHAR(7),
                    fecha_utc,
                    126
                )

            ORDER BY periodo
        """

        datos = consultar_sql(
            consulta,
            parametros
        )

    return jsonify(datos)


@app.route("/api/por-categoria")
def por_categoria():

    if not modo_avanzado():

        return jsonify([])

    datos = consultar_sql(
        """
        SELECT
            categoria,
            total

        FROM dbo.vw_por_categoria

        ORDER BY total DESC
        """
    )

    return jsonify(datos)


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=int(
            os.getenv("PORT", "5000")
        ),
        debug=False
    )