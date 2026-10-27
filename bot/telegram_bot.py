import io
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from vision.extractor import leer_factura_tirilla, validar_factura
from database.operaciones import guardar_gastos
from reportes.generador_excel import generar_reporte
def main():
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    conversaciones = {}

    async def start(update, context):
        await update.message.reply_text(
            "¡Hola! Soy Nexa tu asistente de reembolsos. Cuéntame qué necesitas."
        )

    async def recibir_texto(update, context):
        chat_id = update.message.chat.id
        texto = update.message.text
        
        if chat_id not in conversaciones:
            await update.message.reply_text(
                "Para registrar un gasto, mándame la foto de la factura"
            )
            return
        
        paso = conversaciones[chat_id]["paso"]
        
        if paso == "esperando_tipo":
            tipos_validos= ["contable", "no contable"]
            if texto.lower() not in tipos_validos:
                await update.message.reply_text("No entendi, Por favor solo contestar Contable o No Contable")
                return
            conversaciones[chat_id]["datos"]["tipo"]= texto.lower()
            conversaciones[chat_id]["paso"]="esperando_obra"
            await update.message.reply_text("¿A qué obra corresponde este gasto?")

        elif paso == "esperando_obra":
            conversaciones[chat_id]["datos"]["obra"]= texto.lower()
            datos = conversaciones[chat_id]["datos"]
            guardar_gastos(
                datos["proveedor"],
                datos["nit"],
                datos["fecha"],
                datos["detalle"],
                datos["valor"],
                datos["obra"],
                datos["tipo"]
                )
            del conversaciones[chat_id]
            await update.message.reply_text("Gasto registrado con exito")
    
    async def recibir_foto(update, context):
        chat_id = update.message.chat_id
        foto = update.message.photo[-1]   
        archivo = await foto.get_file() 
        imagen_bytes = await archivo.download_as_bytearray()
        try:
            resultado = leer_factura_tirilla(imagen_bytes)
            imagen = validar_factura(resultado)
            #imagen = leer_factura_tirilla(imagen_bytes)
            conversaciones[chat_id] = {
                "paso": "esperando_tipo",
                "datos": imagen   
                }
            await update.message.reply_text(
            f"""Imagen recibida con exito.
            Proveedor: {imagen['proveedor']},
            Fecha: {imagen['fecha']},
            Valor: {imagen['valor']},
            ¿Es Contable o No Contable?
            """
            )
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")
            #await update.message.reply_text("No se pudo leer bien la tirilla, trata mejorando la foto")
            
            
    async def reporte(update, context):
        try:
            if not context.args or len(context.args)< 2:
                await update.message.reply_text("Error. Usa el formato: /reporte MM AAAA")
                return  
            mes=context.args[0]
            ano=context.args[1]
            generar_reporte(mes,ano)
            await update.message.reply_document(document=open("Reembolsos.xlsx", "rb"))
        except Exception as e:
            await update.message.reply_text("No se pudo obtener de manera exitosa el reporte")
        
        
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, recibir_foto))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_texto))
    app.add_handler(CommandHandler("reporte", reporte))
        
    print("Bot corriendo...")
    app.run_polling()
if __name__ == "__main__":
    main()
        
