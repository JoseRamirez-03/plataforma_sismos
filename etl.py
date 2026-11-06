import os
import pandas as pd
from db import conectar_sql


def ejecutar_etl():

    print("================================")
    print("ETL DE EVENTOS SISMICOS")
    print("================================")

    print("\n1. EXTRACCION")

    conexion = conectar_sql()

    consulta = """
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
    """

    cursor = conexion.cursor()
    cursor.execute(consulta)

    columnas = [columna[0] for columna in cursor.description]
    registros = cursor.fetchall()

    cursor.close()
    conexion.close()

    datos = pd.DataFrame.from_records(
        registros,
        columns=columnas
    )

    print("Eventos extraidos:", len(datos))

    print("\n2. TRANSFORMACION")

    datos["fecha_utc"] = pd.to_datetime(
        datos["fecha_utc"],
        errors="coerce"
    )

    for columna in [
        "magnitud",
        "profundidad_km",
        "latitud",
        "longitud"
    ]:
        datos[columna] = pd.to_numeric(
            datos[columna],
            errors="coerce"
        )

    datos = datos.dropna(
        subset=["fecha_utc", "magnitud"]
    )

    datos = datos.drop_duplicates(
        subset=["id_usgs"]
    )

    datos["region"] = datos["region"].fillna(
        "Sin region especifica"
    )

    datos["mes"] = datos["fecha_utc"].dt.strftime("%Y-%m")

    datos["clasificacion"] = datos["magnitud"].apply(
        lambda magnitud:
        "Alta" if magnitud >= 6
        else "Media" if magnitud >= 5
        else "Baja"
    )

    print("Eventos validos:", len(datos))

    print("\n3. ANALISIS")

    estadisticas = datos.groupby(
        "region"
    ).agg(
        total_sismos=("id_usgs", "count"),
        magnitud_promedio=("magnitud", "mean"),
        magnitud_maxima=("magnitud", "max")
    ).reset_index()

    sismos_mes = datos.groupby(
        "mes"
    ).size().reset_index(
        name="total_sismos"
    )

    print("\nTotal de sismos:", len(datos))

    print(
        "Magnitud promedio:",
        round(datos["magnitud"].mean(), 2)
    )

    print(
        "Magnitud maxima:",
        datos["magnitud"].max()
    )

    print("\n4. CARGA DE RESULTADOS")

    os.makedirs("resultados_etl", exist_ok=True)

    datos.to_csv(
        "resultados_etl/eventos_procesados.csv",
        index=False,
        encoding="utf-8-sig"
    )

    estadisticas.to_csv(
        "resultados_etl/estadisticas_region.csv",
        index=False,
        encoding="utf-8-sig"
    )

    sismos_mes.to_csv(
        "resultados_etl/sismos_por_mes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("Archivos CSV generados correctamente")

    print("\n================================")
    print("ETL FINALIZADO CORRECTAMENTE")
    print("================================")


if __name__ == "__main__":
    ejecutar_etl()