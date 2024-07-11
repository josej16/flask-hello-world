from flask import Flask, jsonify, request
#LIBRERIAS PARA ENVIAR MENSAJES VIA WHTSAPP
import requests
import json
app = Flask(__name__)
#EJECUTAMOS ESTE CODIGO CUANDO SE INGRESE A LA RUTA ENVIAR
@app.route("/enviar/", methods=["POST", "GET"])
def enviar(phone=None):
  # Tus credenciales de WhatsApp Business API
  access_token = 'EAB1IWafZCmmkBO2DyguRIVy2KAnNAMKwE8uhZBsTfUVpnzZA5xtHFYNrE31LkfnGsxV17kHioK1KNoHIOvyqSQb3MCxfO9598V8WPqQjp6tfn0YTLZBKZB9NK8FkEZAtdBWSAJXpaIE5k8RihOFOPnpkNrB8BevpuMh0pQ0SzwnzfmRhhPyBVQkBKcmpUSMKSYiTZA1sndpP7TOKFqDaAYZD'
  phone_number_id = '309696275570080'
  recipient_phone_number = '584248365294'  # Número de teléfono del destinatario

  # URL de la API de WhatsApp
  url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

  # Encabezados de la solicitud
  headers = {
      'Authorization': f'Bearer {access_token}',
      'Content-Type': 'application/json'
  }
  if phone == None:
  # Datos del mensaje
    payload = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": recipient_phone_number,
      "type": "text",
      "text": {
        "preview_url": True,
        "body": "As requested, here'\''s the link to our latest product: https://www.meta.com/quest/quest-3/"
      }
    }
  else:
     payload = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": phone,
      "type": "text",
      "text": {
        "preview_url": True,
        "body": "As requested, here'\''s the link to our latest product: https://www.meta.com/quest/quest-3/"
      }
    }
  # Enviar el mensaje
  response = requests.post(url, headers=headers, data=json.dumps(payload))

# Verificar el resultado
  if response.status_code == 200:
      return "Mensaje enviado exitosamente. osi osi"
  else:
      print(f"Error al enviar el mensaje: {response.status_code}")
      print(response.text)


f = []

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    #SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        #SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "takataka":
            #ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            #SI NO SON IGUALES RETORNAMOS UN MENSAJE DE ERROR
          return "Error de autentificacion."
    #RECIBIMOS TODOS LOS DATOS ENVIADO VIA JSON
    data=request.get_json()
    #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
    mensaje="Telefono:"+data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje=mensaje+"|Mensaje:"+data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO
    f.append(data)
    enviar(data['entry'][0]['changes'][0]['value']['messages'][0]['from'])
    #RETORNAMOS EL STATUS EN UN JSON
    return str(mensaje)

@app.route("/recibir/", methods=["POST", "GET"])
def recibir():
    
    return str(f)
#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)
