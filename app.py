from flask import Flask, jsonify, request
#LIBRERIAS PARA ENVIAR MENSAJES VIA WHTSAPP
from heyoo import WhatsApp
app = Flask(__name__)
#EJECUTAMOS ESTE CODIGO CUANDO SE INGRESE A LA RUTA ENVIAR
@app.route("/enviar/", methods=["POST", "GET"])
def enviar():
    #TOKEN DE ACCESO DE FACEBOOK
    token='EAB1IWafZCmmkBO7GF3PcaaPrZARcDviFROAAH53W6r4zOCa7ZCZAZCmTe07hjWAB0cV7UqKyQHSqcA48z4zQEmruk2WQI8EzjCHCF2bZBsZBw8RQAhSN8rjuWBgMIJHQPQTZCfivo38vizl64moq55Cp6y3ZCI7nnlGwNQ7CFVVcdZCcuWZBovXkmem4qmod5x5JM0hs1CeDGIlaLLOZAv34BnEZD'
    #IDENTIFICADOR DE NÚMERO DE TELÉFONO
    idNumeroTeléfono='309696275570080'
    #TELEFONO QUE RECIBE (EL DE NOSOTROS QUE DIMOS DE ALTA)
    telefonoEnvia='584248365294'
    #MENSAJE A ENVIAR
    textoMensaje="wuwuwuwuwuwuwuwuwuwuuwuww"
    #URL DE LA IMAGEN A ENVIAR
    urlImagen='https://i.imgur.com/r5lhxgn.png'
    #INICIALIZAMOS ENVIO DE MENSAJES
    mensajeWa=WhatsApp(token,idNumeroTeléfono)
    #ENVIAMOS UN MENSAJE DE TEXTO
    mensajeWa.send_message(textoMensaje,telefonoEnvia)
    #ENVIAMOS UNA IMAGEN
    mensajeWa.send_image(image=urlImagen,recipient_id=telefonoEnvia,)
    return "mensaje enviado exitosamente"
#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)
