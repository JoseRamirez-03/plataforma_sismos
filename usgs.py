import math
import requests
from datetime import datetime, timedelta, timezone

URL_USGS = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def descargar_sismos(dias=30, magnitud=4.5, limite=100):
    fin = datetime.now(timezone.utc)

    inicio = fin - timedelta(days=dias)

    parametros = {
        "format": "geojson",
        "starttime": inicio.isoformat(timespec="seconds"),
        "endtime": fin.isoformat(timespec="seconds"),
        "minmagnitude": magnitud,
        "limit": limite,
        "orderby": "time"
    }

    respuesta = requests.get(
        URL_USGS,
        params=parametros,
        timeout=60
    )

    respuesta.raise_for_status()

    datos = respuesta.json()

    return datos.get("features", [])


def convertir_evento(feature):
    try:
        propiedades = feature["properties"]

        coordenadas = feature["geometry"]["coordinates"]

        magnitud = float(propiedades["mag"])

        longitud = float(coordenadas[0])

        latitud = float(coordenadas[1])

        if not all(
            math.isfinite(v)
            for v in (magnitud, longitud, latitud)
        ):
            return None

        if not -90 <= latitud <= 90:
            return None

        if not -180 <= longitud <= 180:
            return None

        if not -2 <= magnitud <= 10:
            return None

        profundidad = coordenadas[2]

        if profundidad is not None:
            profundidad = float(profundidad)

            if not math.isfinite(profundidad):
                profundidad = None

        fecha = datetime.fromtimestamp(
            propiedades["time"] / 1000,
            tz=timezone.utc
        ).replace(tzinfo=None)

        lugar = propiedades.get("place") or "Desconocido"

        if "," in lugar:
            region = lugar.rsplit(",", 1)[-1].strip()
        else:
            region = "Sin region especifica"

        return {
            "id_usgs": str(feature["id"])[:50],
            "fecha_utc": fecha,
            "magnitud": magnitud,
            "profundidad_km": profundidad,
            "latitud": latitud,
            "longitud": longitud,
            "lugar": lugar[:400],
            "region": region[:120]
        }

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        OverflowError,
        OSError
    ):
        return None