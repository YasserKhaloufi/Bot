class Message:
    def __init__(self, update_id, user_id, first_name, chat_id, message=None, user_latitude=None, user_longitude=None):
        # Il costruttore tiene conto del fatto che il messaggio possa essere un testo o una posizione
        # latitudine e longitudine sono opzionali, se non specificate saranno None
        
        self.update_id = update_id
        self.sender = user_id
        self.first_name = first_name
        self.chat_id = chat_id
        self.message = message

        # Se posizione:
        self.user_latitude = user_latitude
        self.user_longitude = user_longitude