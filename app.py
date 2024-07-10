from flask import Flask, jsonify, request
#LIBRERIAS PARA ENVIAR MENSAJES VIA WHTSAPP
import requests
import json
app = Flask(__name__)
#EJECUTAMOS ESTE CODIGO CUANDO SE INGRESE A LA RUTA ENVIAR
@app.route("/enviar/", methods=["POST", "GET"])
def enviar():
  # Tus credenciales de WhatsApp Business API
  access_token = 'EAB1IWafZCmmkBO9r9nljATnZBZCWudDS1ZBatZC12G7FYZCFtAhOiOm47ZBrkjJfSdXU46VdLAMDB71RSfAyXUZAwBN3L8kUL9Hsv0tFYeqOmmLQYUzrwj4TRNxVe6DltBYo7ZAIJfmCzGfo6n7pJtZBqnmV9PMIWp9o3tVvG6Wzc0ZC3XSwMKpoRgWI1j9QGCcZBkiBGADg6DlVfn7XA4l3TJ74'
  phone_number_id = '309696275570080'
  recipient_phone_number = '584248365294'  # Número de teléfono del destinatario

  # URL de la API de WhatsApp
  url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

  # Encabezados de la solicitud
  headers = {
      'Authorization': f'Bearer {access_token}',
      'Content-Type': 'application/json'
  }

  # Datos del mensaje
  payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "584248365294",
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
      return f"Error al enviar el mensaje: {response.status_code}"

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
    #RETORNAMOS EL STATUS EN UN JSON
    return str(mensaje)


#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)
