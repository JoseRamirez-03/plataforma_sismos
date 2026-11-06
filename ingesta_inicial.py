import argparse

from db import conectar_sql, guardar_mongo, guardar_sql_basico
from usgs import descargar_sismos, convertir_evento


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--dias", type=int, default=7)
    parser.add_argument("--min-mag", type=float, default=4.5)
    parser.add_argument("--limite", type=int, default=100)

    args = parser.parse_args()

    if not (1 <= args.dias <= 365):
        parser.error("Los dias deben estar entre 1 y 365")

    if not (-2 <= args.min_mag <= 10):
        parser.error("La magnitud debe estar entre -2 y 10")

    if not (1 <= args.limite <= 20000):
        parser.error("El limite debe estar entre 1 y 20000")

    print("================================")
    print("INGESTA DE EVENTOS SISMICOS")
    print("================================")

    print("\n1. Descargando eventos desde USGS...")

    features = descargar_sismos(
        dias=args.dias,
        magnitud=args.min_mag,
        limite=args.limite
    )

    print("Eventos descargados:", len(features))

    print("\n2. Validando informacion...")

    eventos = []
    documentos_validos = []

    for feature in features:

        evento = convertir_evento(feature)

        if evento is not None:
            eventos.append(evento)
            documentos_validos.append(feature)

    print("Eventos validos:", len(eventos))

    if not eventos:
        print("No se encontraron eventos para guardar.")
        return

    print("\n3. Guardando documentos en MongoDB Atlas...")

    guardar_mongo(documentos_validos)

    print("Documentos guardados correctamente en MongoDB.")

    print("\n4. Guardando eventos en Azure SQL...")

    conexion = conectar_sql()

    try:

        cursor = conexion.cursor()

        for evento in eventos:

            guardar_sql_basico(cursor, evento)

        conexion.commit()

        print("Eventos guardados correctamente en Azure SQL.")

    except Exception:

        conexion.rollback()

        print("Error al guardar los eventos en Azure SQL.")

        raise

    finally:

        conexion.close()

    print("\n================================")
    print("INGESTA FINALIZADA CORRECTAMENTE")
    print("================================")


if __name__ == "__main__":
    main()