from requests import *
from Segreto import BOT_TOKEN

base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Test getMe
"""method = "getMe" 

resp = get(base_url + method) # Costruisco l'URL ed eseguo la richiesta, con i parametri passati
if(resp.status_code == 200):
    if(resp.json()["ok"]):
        data = resp.json()["result"] # Converto la risposta in JSON
        print(data)"""


# Test sendMessage
"""method = "sendMessage"
username = "127056385" # User id a caso (non esiste)
text = "Ciao, sono un messaggio di prova!"

resp = post(base_url + method, {"chat_id": username, "text": text}) # I parametri sono passati in JSON

if(resp.status_code == 200):
    if(resp.json()["ok"]):
        data = resp.json()["result"] # Converto la risposta in JSON
        print(data)"""