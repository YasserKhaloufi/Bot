# Author: Yasser Khaloufi
# Date: 19/01/2023
# Version: 1.0

"""
Nota: GLOBAL SCOPE
      nella versione precedente user_latitude e longitude erano dichiarati solo se il messaggio era una posizione, 
      più precisamente all'interno di un else che controllava se il messaggio era un testo o una posizione,
      all'interno del while(true) del main. Tuttavia lo script funzionava lo stesso, dato che in python, nonostante
      si dichiari una variabile all'interno di un blocco, questa è visibile anche all'esterno, dunque anche a fronte
      di cicli while diversi, il valore di queste variabili veniva conservato finchè non veniva inviata una nuova posizione.
      
      In questa nuova versione, lo script non funzionerebbe, dato che ho spostato la parte di codice che si occupa di
      distinguere messaggi da posizioni all'interno della classe TelegramBot, all'interno di un metodo, dunque
      le variabili user_latitude e user_longitude sono visibili solo all'interno di quel metodo, e non qui nel main.
      Perciò, per risolvere il problema, ho dichiarato le suddette variabili all'inizio dello script.
          
"""

from requests import *
from time import sleep
from connect import create_connection
from math import radians, cos, sin, sqrt, atan2
import TelegramBot
import Message
from Segreto import BOT_TOKEN
import os

# (Le variabili con identificatore in maiuscolo sono costanti)
Bot = TelegramBot.TelegramBot(BOT_TOKEN) # Definisco il bot

user_states = {} # Vedi esempio alla fine del file
user_latitude = None
user_longitude = None

while(True):
    os.system('cls')

    messages = Bot.read_messages() # Ricavo i messaggi ricevuti

    for m in messages: # Ciclo tutti i messaggi ricevuti, se non ce ne sono, il ciclo non viene eseguito
        
        # Ricavo i campi del messaggio
        print("Messaggio ricevuto:\n","ID:", m.update_id, "\nDa:" , m.first_name, "\nContenuto:" , m.message)
        
        # GESTIONE INPUT
        if m.sender in user_states: # Se l'utente è presente nel dizionario, allora so che l'utente il messaggio è un input relativo ad un comando precedentemente inviato
            
            cnx, cursor = create_connection() # Nella maggior parte dei casi serve connettersi al DB per gestire l'input, quindi effettuo subito la connessione preventivamente
            
            # Se è la prima volta che ricevo un messaggio dall'utente
            if user_states[m.sender] == "setNome": 
                # Inserisco l'utente nella tabella utenti
                query = "INSERT INTO utenti (ID, Nome) VALUES (%s, %s)"
                values = (m.sender, m.message) # il message contiene il nome che l'utente vuole utilizzare
                
                # Eseguo la query
                cursor.execute(query, values)
                cnx.commit()
                
                answer = "Nome impostato correttamente."
                user_states.pop(m.sender) # Rimuovo l'utente dal dizionario, sennà gestirei sempre lo stesso comando
                
            # Altrimenti, in tutti gli altri casi...
            else:
                # Se l'utente esiste
                cursor.execute("SELECT ID FROM utenti WHERE ID = %s", (m.sender,))
                if cursor.fetchone() != None:
                    
                    if user_states[m.sender] == "setCarburante":
                        # Ne aggiorno il campo Carburante
                        query = "UPDATE utenti SET Carburante = %s WHERE ID = %s"
                        values = (m.message, m.sender)
                        cursor.execute(query, values)
                        cnx.commit()
                        
                        answer = "Carburante impostato correttamente."
                        user_states.pop(m.sender)
                        
                    elif user_states[m.sender] == "setCapacita":
                        # Ne aggiorno il campo Capacita
                        query = "UPDATE utenti SET Capacita = %s WHERE ID = %s"
                        values = (m.message, m.sender)
                        cursor.execute(query, values)
                        cnx.commit()
                        
                        answer = "Capacità impostata correttamente."
                        user_states.pop(m.sender)
                        
                    elif user_states[m.sender] == "setDistanza":
                        # Ne aggiorno il campo Distanza
                        query = "UPDATE utenti SET Distanza = %s WHERE ID = %s"
                        values = (m.message, m.sender)
                        cursor.execute(query, values)
                        cnx.commit()
                        
                        answer = "Distanza impostata correttamente."
                        user_states.pop(m.sender)
                        
                    elif user_states[m.sender] == "cerca":   
                        # Se l'utente ha settato carburante e distanza max procedo
                        cursor.execute("SELECT Carburante FROM utenti WHERE ID = %s", (m.sender,)); carburante = cursor.fetchone()
                        cursor.execute("SELECT Distanza FROM utenti WHERE ID = %s", (m.sender,)); distanza = cursor.fetchone()
                        
                        user_latitude = m.user_latitude
                        user_longitude = m.user_longitude
                        
                        if carburante != None and distanza != None:
                            answer = "Stazione più conveniente o più vicina?\n 1) Più conveniente\n 2) Più vicina"
                            user_states.pop(m.sender)
                            user_states[m.sender] = "cerca_"
                        else: # Altrimenti, lo avviso
                            answer = "Carburante o distanza mancanti, impostali con /setcarburante, /setdistanza."
                            user_states.pop(m.sender)
                            
                    elif user_states[m.sender] == "cerca_":
                        # Ricavo le stazioni con carburante giusto
                        cursor.execute("SELECT Carburante FROM utenti WHERE ID = %s", (m.sender,)); carburante = cursor.fetchone()
                        query = "SELECT * FROM carburanti JOIN impianti ON idImpianto = impianti.ID WHERE carburanti.Tipo = '" + carburante[0] + "'"
                        cursor.execute(query)
                        stazioni = cursor.fetchall()
                        
                        # Campi dopo join: 
                        """
                            00: ID
                            01: Tipo Carburante
                            02: Prezzo
                            03: --
                            04: --
                            05: ID
                            06: Gestore
                            07: Nome
                            08: Tipo impianto
                            09: --
                            10: Indirizzo
                            11: Comune
                            12: Provincia
                            13: Latitudine
                            14: Longitudine
                        """

                        cursor.execute("SELECT Distanza FROM utenti WHERE ID = %s", (m.sender,)); distanza = cursor.fetchone() # Ricavo la distanza massima che l'utente è disposto a percorrere
                        # Mantieni solo le stazioni che si trovano entro la distanza massima (utilizzo una comprehension)
                        stazioni = [stazione for stazione in stazioni if calculate_distance(user_latitude, user_longitude, float(stazione[13]), float(stazione[14])) <= float(distanza[0])]
                        
                        # Fra le satzioni rimaste
                        if m.message == "1":
                            # Ricavo quella più conveniente
                            stazione = min(stazioni, key=lambda stazione: float(stazione[2]))
                            answer = "La stazione più conveniente è " + stazione[7] + " a " + str(float(stazione[2])) + "€/L"
                        elif m.message == "2":
                            # Ricardo quella più vicina
                            stazione = min(stazioni, key=lambda stazione: calculate_distance(user_latitude, user_longitude, float(stazione[13]), float(stazione[14])))
                            answer = "La stazione più vicina è " + stazione[7] + " a " + str(calculate_distance(user_latitude, user_longitude, float(stazione[13]), float(stazione[14]))) + "km"
                        
                        answer += "\nOpenStreetMap: https://www.openstreetmap.org/#map=18/" + str(stazione[13]) + "/" + str(stazione[14])
                        
                else: # Altrimenti
                        answer = "Prima imposta il tuo nome con /setnome."
                        
            
        # GESTIONE COMANDI     
        else:
            
            # Potrei utilizzare una serie di if, ma è più comodo usare un dizionario, in fondo al file mi sono appuntato perchè
            def handle_command(message):
                
                def setNome():
                    user_states[m.sender] = "setNome"
                    return "Ok, come vuoi essere chiamato?"
                
                def setCarburante():
                    user_states[m.sender] = "setCarburante"
                    
                    # Ricavo i tipi di carburante dal DB e li inserisco nella risposta
                    cnx, cursor = create_connection()
                    query = "SELECT DISTINCT Tipo FROM carburanti"
                    cursor.execute(query)
                    carburanti = cursor.fetchall()
                    cursor.close()
                    cnx.close()
                    
                    temp = "Ok, che tipo di carburante utilizzi?\n"
                    for carburante in carburanti:
                        temp += carburante[0] + "\n"
                    return temp
                                
                def setCapacita():
                    user_states[m.sender] = "setCapacita"
                    return "Ok, quanto è capiente il tuo serbatoio?"
                
                def setDistanza():
                    user_states[m.sender] = "setDistanza"
                    return "Ok, quanto sei disposto a percorrere?"
                
                def cerca():
                    user_states[m.sender] = "cerca"
                    return "Ok, dammi la tua posizione."
                
                def myData():
                    cnx, cursor = create_connection()
                    query = "SELECT * FROM utenti WHERE ID = %s"
                    cursor.execute(query, (m.sender,))
                    user = cursor.fetchone()
                    cursor.close()
                    cnx.close()
                    
                    if user != None:
                        return "Nome: " + user[1] + "\nCarburante: " + user[2] + "\nCapacità: " + str(user[3]) + "\nDistanza: " + str(user[4])
                    else:
                        return "Prima imposta il tuo nome con /setnome."
                    
                def default():
                    return "Comando non riconosciuto."
                
                # Per mappare il comando ricevuto con la rispettiva funzione da eseguire, uso un dizionario
                commands = {
                    "/setnome": setNome,
                    "/setcarburante": setCarburante,
                    "/setcapacita": setCapacita,
                    "/setdistanza": setDistanza,
                    "/cerca": cerca,
                    "/mydata" : myData
                }
                
                func = commands.get(message, default) # Ricavo la funzione da eseguire, se il comando non è presente, eseguo la funzione di default
                return func()
        
            answer = handle_command(m.message)
            
        # RISPOSTA
        """ Ricavo l'ID della chat a cui rispondere (ricorda che se devi rispondere al singolo utente, devi usare l'ID dell'utente, non della chat,
        in questo caso non fa differenza, visto che la chat è solamente tra il bot e l'utente) """
        Bot.send_message_to_chat(m.chat_id, answer) #Invio la risposta

    sleep(2)

    # Formula di Haversine per calcolare la distanza tra due punti
    def calculate_distance(lat1, lon1, lat2, lon2):
        # Raggio della Terra
        R = 6371.0

        # Conversione in radianti
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        # Differenza di longitudine e latitudine
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        # Formula di Haversine
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

""" 
Ricorda: 
 "The BotFather allows you to define commands for your bot, but it doesn't handle the logic of how your bot responds to those commands. 
  That's something you need to implement in your script."
  
  Definire i comandi permessi con BotFather non è essenziale, ma è comodo per avere un elenco dei comandi disponibili 
"""

"""
Esempio di utlizzio dizionario user_states:
 Quando un utente invia /setnome, ne salvo lo stato in questo dizionario, 
 così da poter sapere al prossimo ciclo che il nuovo messaggio inviatomi sarà, molto probabilmente, il nome che l'utente vuole impostare.
 In sostanza ogni volta che ricevo un messaggio, controllo se l'utente da cui l'ho ricevuto è presente nel dizionario,
 se sì, allora so che l'utente aveva precedentemente inviato un comando che richiede un input, quindi lo gestisco di conseguenza,
 altrimenti si tratta di un normale comando.
"""

"""
Come mai ho usato un dizionario per gestire i comandi invece che serie di elif?:
"Using a dictionary to simulate a switch-case structure can be more efficient and cleaner than using a series of elif statements, 
 especially when dealing with a large number of cases.

 The dictionary approach has a constant lookup time regardless of the number of cases, 
 while the elif approach has a lookup time that grows linearly with the number of cases, 
 as each condition must be checked sequentially until a match is found."
 
 E comunque assomiglia più ad un tradizionale switch-case...
"""

""" 
# Test risposta:

if e["message"]["text"] == "/test":
    answer = "This is a test response."
            
    # Ricavo l'ID della chat a cui rispondere (ricorda che se devi rispondere al singolo utente, devi usare l'ID dell'utente, non della chat,
    # in questo caso non fa differenza, visto che la chat è solamente tra il bot e l'utente)
    chat_id = e["message"]["chat"]["id"] 
            
    #Invio la risposta
    request = "sendMessage"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{request}"
    parameters = {"chat_id": chat_id, "text": answer}
    post(url, params=parameters) 
"""