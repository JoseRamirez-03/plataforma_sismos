import os
from dotenv import load_dotenv
from db import conectar_sql, conectar_mongo

load_dotenv()

print("================================")
print("VERIFICACION DE BASES DE DATOS")
print("================================")

print("\n1. Verificando Azure SQL...")

try:
    conexion = conectar_sql()

    cursor = conexion.cursor()

    cursor.execute("SELECT DB_NAME()")

    resultado = cursor.fetchone()[0]

    print("Conexion exitosa con Azure SQL")
    print("Base de datos:", resultado)

    conexion.close()

except Exception as error:
    print("ERROR al conectar con Azure SQL")
    print(error)


print("\n2. Verificando MongoDB Atlas...")

try:
    cliente = conectar_mongo()

    cliente.admin.command("ping")

    print("Conexion exitosa con MongoDB Atlas")
    print("Base de datos:", os.environ["MONGO_DATABASE"])

    cliente.close()

except Exception as error:
    print("ERROR al conectar con MongoDB Atlas")
    print(error)


print("\n================================")
print("VERIFICACION FINALIZADA")
print("================================")