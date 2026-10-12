from datetime import date, timedelta, datetime
import json
from vision.extractor import fecha_en_rango_valido, validar_factura
import pytest

def test_fecha_del_mes_actual_es_valida():
    hoy = date(2026, 10, 11)
    fecha_factura = date(2026, 10, 5)
    assert fecha_en_rango_valido(fecha_factura, hoy) == True
   
def test_validar_factura():
    hoy = date(2026, 10, 11)
    datos = {"proveedor": "Prueba SAS",
        "nit": "90008696",
        "fecha": "2026-10-11", 
        "detalle": "Parqueadero",
        "valor": 3500,}
    assert validar_factura(json.dumps(datos), hoy) == datos 

def test_validar_factura_con_fecha_vieja_falla():
    hoy = date(2026, 10, 11)
    datos = {
        "proveedor": "Prueba SAS",
        "nit": "90008696",
        "fecha": "2026-07-15",      
        "detalle": "Parqueadero",
        "valor": 3500,
    }
    with pytest.raises(ValueError):
        validar_factura(json.dumps(datos), hoy)
    
def test_validar_factura_con_fecha_vacia():
    hoy = date(2026, 10, 11)
    datos = {
        "proveedor": "Prueba SAS",
        "nit": "90008696",
        "fecha": "",   
        "detalle": "Parqueadero",
        "valor": 3500,
    }
    with pytest.raises(ValueError):
        validar_factura(json.dumps(datos), hoy)

def test_validar_factura_sin_fecha():
    hoy = date(2026, 10, 11)
    datos = {
        "proveedor": "Prueba SAS",
        "nit": "90008696",  
        "detalle": "Parqueadero",
        "valor": 3500,
    }
    with pytest.raises(ValueError):
        validar_factura(json.dumps(datos), hoy)