from openai import OpenAI
import json
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# ── API ──
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
CAMPOS_FACTURA = ["proveedor", "nit", "detalle", "valor"]

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
    }}
    OJO tener en cuanta que es posible que hayan muchos items, cada item debe de contener su valor, de resto todos comparten
    la empresa, el nit y la fecha, no inventes datos, ni trates de rellenar datos faltante, adicionalmente relaciona palabras, subtotal es igual a valor
    Devuelve SOLO un objeto JSON plano con estos campos.
    Si hay varios items, combina las descripciones en "detalle"
    y suma los valores en "valor".
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

def validar_factura(datos):
    resultado = {k.lower(): v for k , v in json.loads(datos).items()}
    
    # Validar campos principales
    for campo in CAMPOS_FACTURA:
        if campo not in resultado:
            raise ValueError(f"JSON incompleto, falta campo principal: {campo}")
    
    # Validar que haya al menos un item
    if len(resultado["detalle"]) == 0:
        raise ValueError("La factura no tiene items")
    
    return resultado
