from requests import *
import Message
import os

class TelegramBot:
    # Costruttore: alla crezione, costruisco l'URL base per le chiamate all'API e imposto l'ID di update a 0
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/"
        self.last_update_id = 0

    # I seguenti metodi sfruttano le richieste HTTP per interagire con l'API di Telegram

    # Principalmente richiedo gli ultimi messaggi a partire da un dato ID di update
    def get_updates(self):
        method = "getUpdates" 
        parameters = {"offset": self.last_update_id} # Passo l'ultimo updateID ricevuto per evitare di ricevere messaggi già ricevuti
        resp = get(self.base_url + method, params=parameters) # Costruisco l'URL ed eseguo la richiesta, con i parametri passati
        data = resp.json() # Converto la risposta in JSON
        return data["result"] # Ritorno solo il campo "result" della risposta, che contiene i messaggi
    
    def read_messages(self):
        data = self.get_updates()
        messages = []
        
        for e in data: # Ciclo tutti i messaggi ricevuti
            
            update_id = e["update_id"]
            user_id = e["message"]["from"]["id"]
            chat_id = e["message"]["chat"]["id"]
            first_name = e["message"]["from"]["first_name"]
            
            # Il messaggio può essere un testo o una posizione
            if "text" in e["message"]:
                message = e["message"]["text"]
                messages.append(Message.Message(update_id, user_id, first_name, chat_id, message)) # Aggiungo il messaggio alla lista di messaggi da ritornare
            else:
                user_latitude = e["message"]["location"]["latitude"]
                user_longitude = e["message"]["location"]["longitude"]
                messages.append(Message.Message(update_id, user_id, first_name, chat_id, None, user_latitude, user_longitude)) # Idem
                
            self.update_last_id(update_id) # Aggiorno, mano mano che scorro i messaggi, l'updateID, così da partire da quello successivo all'ultimo ricevuto al prossimo ciclo di while
        
        # Imposto l'updateID all'ID che avrebbe il messaggio successivo solo se ho ricevuto almeno un messaggio
        if(len(messages) > 0):
            self.last_update_id += 1
        
        return messages

    def update_last_id(self, new_id):
        self.last_update_id = new_id

    # Invio chat/utente
    
    def send_message_to_chat(self, chat_id, text):
        method = "sendMessage"
        parameters = {"chat_id": chat_id, "text": text}
        resp = post(self.base_url + method, params=parameters)
        return resp.json()

    def send_message_to_user(self, user_id, text):
        method = "sendMessage"
        parameters = {"user_id": user_id, "text": text}
        resp = post(self.base_url + method, params=parameters)
        return resp.json()

    
        