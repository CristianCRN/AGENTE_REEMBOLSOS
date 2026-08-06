import sqlite3
from database.modelos import DB_NAME

def guardar_gastos(proveedor, nit, fecha, detalle, valor, obra, tipo):
    try:
        with sqlite3.connect(DB_NAME) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Gastos (Proveedor, NIT, Fecha, Detalle, Valor, CC, Obra, Tipo)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """, (proveedor, nit, fecha, detalle, valor, obra, tipo))
    except Exception as e:
        print (f"Error al guardar los gastos: {e}")               
def obtener_gastos():
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM Gastos")
        return cursor.fetchall()
           
def gastos_mes(mes, ano):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT * FROM Gastos
            WHERE Fecha LIKE ? 
            ORDER BY Valor DESC
        """, (f"{ano}-{mes}%",))
        return cursor.fetchall()
