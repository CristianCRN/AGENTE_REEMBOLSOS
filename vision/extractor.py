from openai import OpenAI
import json
import base64
import os
from dotenv import load_dotenv
from datetime import date, timedelta, datetime

load_dotenv()

# ── API ──
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
CAMPOS_FACTURA = ["proveedor", "nit", "detalle", "valor", "fecha"]

def leer_factura_tirilla(imagen_bytes):
    imagen = base64.b64encode(imagen_bytes).decode("utf-8")
    prompt = f"""
    Eres un experto en lectura de facturas en tirilla, debes de sacar en una estructura JSON los siguientes datos:
    {{
        "proveedor": "",
        "nit": "",
        "fecha": "Formato YYYY-MM-DD", 
        "detalle": "",
        "valor": 0,
        "Subtotal": null,
        "IVA": null,
    }}
    OJO tener en cuanta que es posible que hayan muchos items, cada item debe de contener su valor, de resto todos comparten
    la empresa, el nit y la fecha, no inventes datos, ni trates de rellenar datos faltante, adicionalmente relaciona palabras, subtotal es igual a valor
    Devuelve SOLO un objeto JSON plano con estos campos, Si hay varios items, combina las descripciones en "detalle" y suma los valores en "valor".
    Busca un campo que diga literlamente Total, Total a Pagar, Valor Total o Total Pagado, si este existe usa ese valor tal cual
    Si no existe ese campo pero ves un valor que se llame Subtotal e IVA como lineas separadas, entonces extrae cada uno por separado subtotal, IVA
    y el valor sumado que te entrega el programa es el que guardas,
    si ves una fecha escrita a mano en formato DD/MM/AAAA en el documento, úsala como la fecha del gasto; ignora cualquier cuadrícula de casillas
    marcadas o raspadas.
    Ojo todas las facturas estan en pesos colombianos, para que no confundas el separador de miles como separador de decimal.
    Si encuentras un campo Total explícito, usa ese valor en valor y deja subtotal e iva como null. Si no hay Total
    pero sí ves Subtotal e IVA como líneas separadas, pon esos dos valores en los campos subtotal e iva tal cual los ves, sin sumarlos tú
    dejas valor en 0.
    El campo iva debe ser un valor en pesos, nunca un porcentaje 
    si solo ves IVA 19% sin un monto en pesos asociado, no tienes información suficiente para ese campo: déjalo como null.
    """
    response = client.chat.completions.create(
        model = "gpt-4o",
        messages= [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url":{
                "url":f"data:image/jpeg;base64,{imagen}"
            }}
            ] }],
        response_format={"type": "json_object"},
        temperature=0
    )
    
    respuesta=response.choices[0].message.content
    #print ("Devolvio", respuesta)
    return  respuesta

def fecha_en_rango_valido(fecha_factura, hoy=None):
    hoy = hoy or date.today()
    primer_dia_mes_actual = hoy.replace(day=1)
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
    primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
    return primer_dia_mes_anterior <= fecha_factura <= hoy
   
def validar_factura(datos, hoy=None):
    resultado = {k.lower(): v for k , v in json.loads(datos).items()}
    
    # Validar campos principales
    for campo in CAMPOS_FACTURA:
        if campo not in resultado:
            raise ValueError(f"JSON incompleto, falta campo principal: {campo}")
        
    
    # Validar que haya al menos un item
    if len(resultado["detalle"]) == 0:
        raise ValueError("La factura no tiene items")
    
    if resultado.get("subtotal") is not None and resultado.get("iva") is not None:
        resultado["valor"] = resultado["subtotal"] + resultado["iva"]
    if resultado["valor"] == 0:
        raise ValueError ("No se pudo leer bien el valor total, por favor toma una fotografia mejor o escribe el valor total")
    
    try:
        fecha_factura = datetime.strptime(resultado["fecha"], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError("No se pudo verificar la fecha de la factura, por favor toma una fotografía en mejor calidad o escribe la fecha a mano en una esquina de la factura")
    
    if not fecha_en_rango_valido(fecha_factura, hoy):
        raise ValueError("La factura es de un mes no valido no se puede registrar, por favor toma fotografías de reembolsos del mes actual o del mes anterior")
    
    return resultado
