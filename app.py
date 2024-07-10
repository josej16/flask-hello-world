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
      print("Mensaje enviado exitosamente")
  else:
      print(f"Error al enviar el mensaje: {response.status_code}")
      print(response.text)
#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)
