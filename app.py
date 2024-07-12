from flask import Flask, jsonify, request
#LIBRERIAS PARA ENVIAR MENSAJES VIA WHTSAPP
import requests
import json
import pandas as pd
app = Flask(__name__)
#EJECUTAMOS ESTE CODIGO CUANDO SE INGRESE A LA RUTA ENVIAR
@app.route("/enviar/", methods=["POST", "GET"])
def enviar(phone=None, step=None):
  # Tus credenciales de WhatsApp Business API
  access_token = 'EAB1IWafZCmmkBO1Okggaoy3ByKRxx0ZA7jKFUQu5WVVAXdRvHO8U6q7XNPDKdptxSVbI8GvgUVZB7dJfQSz5VPOnb5ZBqbbcuu0z6BnC3O3BZAlkZClkkBWmas83yr6NxunAF3tSWcZB99GSXysz8XJom8uCjqZBgAq0lhDBTVNI6Oukly8cO2wI0LytMYq9fxhN9Elkun0ibb69DZCZBW9uQZD'
  phone_number_id = '309696275570080'
  recipient_phone_number = '584248365294'  # Número de teléfono del destinatario

  # URL de la API de WhatsApp
  url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

  # Encabezados de la solicitud
  headers = {
      'Authorization': f'Bearer {access_token}',
      'Content-Type': 'application/json'
  }
  if step == 'Non_step':
  # Datos del mensaje
    payload = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": phone,
      "type": "text",
      "text": {
        "preview_url": True,
        "body": "bienvenido taka taka"
      }
    }
  elif step == 'respuestamensajeinicial':
     payload = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": phone,
      "type": "interactive",
      "interactive": {
        "type": "catalog_message",
        "body": {
          "text": "este es el catalogo mi pana"
        },
        "action": {
          "parameters": {
            
          }
        },
        "footer": {
          "text": "este es el pie de pagina"
        }
      }
    }
  
  elif step == 'final':
     payload = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": phone,
      "type": "text",
      "text": {
        "preview_url": True,
        "body": "segun y que final"
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

df = pd.DataFrame({'telefono': [], 'mensaje': [], 'fecha': [], 'step': []})
f = []
steps = ['Non_step', 'respuestamensajeinicial', 'final']

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
    telefono = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    timestamp = data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO
    if (telefono not in df['telefono'].values) or (list(df['step'][df['telefono'] == telefono][-1:])[0] == 'final'):
      df.loc[len(df),:] = {'telefono':telefono , 'mensaje': mensaje, 'fecha': timestamp, 'step': 'Non_step'}
      enviar(telefono, 'Non_step')

    else:
      df.loc[len(df),:] = {'telefono':telefono , 'mensaje': mensaje, 'fecha': timestamp, 'step': steps[(steps.index(list(df['step'][df['telefono'] == telefono][-1:])[0]) + 1)]}
      enviar(telefono, list(df['step'][df['telefono'] == telefono][-1:])[0])
    #RETORNAMOS EL STATUS EN UN JSON
    return str(mensaje)

@app.route("/recibir/", methods=["POST", "GET"])
def recibir():
    
    return str(list(df.values))
#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)
