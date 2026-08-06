import sqlite3
import pathlib

DB_NAME = str(pathlib.Path(__file__).parent.parent / "Reembolsos.db")

def inicializar():
    #Conexion a la base de datos con with para que guarde y cierre directamente 
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        #Crear Tabla en caso de que no exista
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Gastos (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                PROVEEDOR TEXT,
                NIT TEXT,
                FECHA TEXT,
                DETALLE TEXT,
                VALOR REAL,
                CC TEXT,
                OBRA TEXT,
                TIPO TEXT
            )
        """)
        print("Base de datos y tabla listas")

if __name__ == "__main__":
    inicializar()