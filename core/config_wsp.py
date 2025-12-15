ACCESS_TOKEN = "EAAZAdes3a8IkBQKs3iMuVrVBZBgmwfJC4aDmYMLND2UDHXzdPhEZBC0nIBMbd7mOZC40cSZBl0Pv7ZBi1Jc5RkSCHznCwwcOKhzL69ZA4cPvJiZA2HZAXa6lQecQ8znLt64y5aZCjbZAT0F8ixZAhCUuJJ5LYZCtLG5zPoGGVcM9BCmgLeAOppGZAIZAhZBZB8bNDf6O0PEAErtRJml1hE2TjDu3YTq136DVPBbD1ORNWxe6eRuvkfP7LJZA4KSJNHsvnh6wFvapwp9jGVc9072SMWZBvMo410zp9h5DAZDZD"
APP_ID = "1791631881334921"
APP_SECRET = "0d7ddb5a4e27603b1323140bae06041a"
RECIPENT_WAID = "+541133209868"
VERSION = "v22.0"
PHONE_NUMBER_ID = "817028354825000"

import requests
import json

def enviar_wsp(token, phone_number_id, numero_cliente, mensaje):
    url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero_cliente,
        "type": "text",
        "text": {
            "body": mensaje
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

# ------------------------------
# EJEMPLO DE USO
# ------------------------------

TOKEN = "EAAZAdes3a8IkBQKs3iMuVrVBZBgmwfJC4aDmYMLND2UDHXzdPhEZBC0nIBMbd7mOZC40cSZBl0Pv7ZBi1Jc5RkSCHznCwwcOKhzL69ZA4cPvJiZA2HZAXa6lQecQ8znLt64y5aZCjbZAT0F8ixZAhCUuJJ5LYZCtLG5zPoGGVcM9BCmgLeAOppGZAIZAhZBZB8bNDf6O0PEAErtRJml1hE2TjDu3YTq136DVPBbD1ORNWxe6eRuvkfP7LJZA4KSJNHsvnh6wFvapwp9jGVc9072SMWZBvMo410zp9h5DAZDZD"
PHONE_ID ="817028354825000"
NUMERO = "5491133209868"  # siempre con código país
MENSAJE = "Hola! Este mensaje fue enviado desde la API oficial de WhatsApp 😊"

resp = enviar_wsp(TOKEN, PHONE_ID, NUMERO, MENSAJE)
print(resp)
