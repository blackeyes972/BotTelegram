import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests
import telebot
import json
import time
import os
from gtts import gTTS
import pygame
import wikipediaapi

#Setto wikipedia in inglese
wiki_wiki = wikipediaapi.Wikipedia('en')
#Setto l'ora per recuperare le quotazioni alla data di oggi
now = int(time.time())
tstamp = now - 86400

current_time = time.time()
ct = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(current_time))

# apri il file di configurazione e leggi il token
with open("config.json", "r") as f:
    config = json.load(f)

token = config["token"]
my_api_key = config["my_api_key"]
#Questo codice crea un oggetto ReplyKeyboardMarkup, che rappresenta il menu a tendina. Viene quindi aggiunto un pulsante per ogni opzione elencata nel menu e impostato come tastiera predefinita per tutti i messaggi inviati dal bot.

keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
price_btc_button = telebot.types.KeyboardButton('/price')
graph_btc_button = telebot.types.KeyboardButton('/graph')
alert_btc_button = telebot.types.KeyboardButton('/alert')
price_eth_button = telebot.types.KeyboardButton('/price_eth')
graph_eth_button = telebot.types.KeyboardButton('/graph_eth')
alert_eth_button = telebot.types.KeyboardButton('/alert_eth')
convert_button = telebot.types.KeyboardButton('/convert')
wiki_button = telebot.types.KeyboardButton('/wiki')
keyboard.add(price_btc_button, graph_btc_button, alert_btc_button,
             price_eth_button, graph_eth_button, alert_eth_button, convert_button, wiki_button)
def main(token):

    bot = telebot.TeleBot(token)
    print(F'Launching bot at: {ct}')
    def play_audio(text):
        tts = gTTS(text=text, lang='en')
        filename = f"audio_{int(time.time())}.mp3"
        with open(filename, 'wb') as file:
            tts.write_to_fp(file)


        pygame.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        #In questo modo ogni volta che viene chiamato il metodo play_audio(), viene generato un nome di file univoco basato sul tempo corrente e viene rimosso subito dopo la riproduzione dell'audio.
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        pygame.mixer.music.stop()
        pygame.quit()
        try:
            os.remove(filename)
        except PermissionError:
            print(f"Could not remove file {filename}")

    play_audio(f"Launching bot at {ct}")

    
    @bot.message_handler(commands=['start'])
    def start_message(message):
        #Setto anche i pulsanti "reply_markup=keyboard" all'interno della funzione "bot.send_message". Questo associa la tastiera al messaggio inviato dal bot.
        bot.send_message(chat_id=message.chat.id,
                     text="Routine actions:\n"
                          "/start - bot initiation\n"
                          "/help - help\n"
                          "Specific actions and procedures:\n",
                     reply_markup=keyboard)

    @bot.message_handler(commands=['help'])
    def help_message(message):
        bot.send_message(message.chat.id, 'Routine actions:\n'
                                               '/start - bot initiation\n'
                                               '/help - help\n'
                                               'Specific actions and procedures:\n'
                                               '/price - price of Bitcoin\n'
                                               '/graph - graph price of Bitcoin (BTC) in USD over the past year\n'
                                               '/alert - send a message when the price of Bitcoin reaches a certain level\n'
                                               '/price_eth - price of Ethereum (ETH)\n'
                                               '/graph_eth - graph price of Ethereum (ETH) in USD over the past year\n'
                                               '/alert_eth - send a message when the price of Ethereum (ETH) reaches a certain level\n'
                                               '/convert - convert USD to EUR\n'
                                               '/wiki - Ask to wikipedia\n')

    @bot.message_handler(commands=['price'])
    
    def price(message):
        url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD&api_key={my_api_key}"
        response = requests.get(url).json()
        price = response["USD"]
        # Creare l'oggetto Message
        bot.send_message(chat_id=message.chat.id, text="Price of Bitcoin (BTC): $ " + str(price))
        play_audio(f"Price of Bitcoin {price}")

    @bot.message_handler(commands=['graph'])
    def grafico(message):
       
        # Specificare l'intervallo di tempo desiderato
       # start_time = "1640995200" # 2022-01-01 in formato timestamp
        end_time = str(tstamp) # Oggi in formato timestamp

        # Costruire la richiesta API
        url = "https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=365&toTs=" + end_time
        
        # Invia la richiesta e recupera i dati
        response = requests.get(url)
        data = json.loads(response.text)

        # Estrazione dei prezzi dai dati
        prices = [item["close"] for item in data["Data"]["Data"]]
        
        # disegnare il grafico del prezzo
        plt.plot(prices)
        plt.xlabel("Days")
        plt.ylabel("Price (USD)")
        plt.title("Price of Bitcoin (BTC) in USD over the past year")
        # save plot to PNG file
        plt.savefig('prices.png')
        #plt.show()
        chat_id = message.chat.id
        with open("prices.png", "rb") as f:
            bot.send_photo(chat_id, f)
        try:
            time.sleep(1)
            os.remove('prices.png')
        except PermissionError:
            print(f"Could not remove file {'prices.png'}")

    @bot.message_handler(commands=['alert'])
    def set_alert(message):
        bot.send_message(chat_id=message.chat.id, text="Enter the desired price:")
        bot.register_next_step_handler(message, set_desired_price)

    def set_desired_price(message):
        # Definire il livello di prezzo desiderato
        desired_price = int(message.text)

        while True:
            # Recuperare il prezzo attuale di Bitcoin
            url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD"
            response = requests.get(url)
            data = response.json()

            # Recuperare il prezzo di Bitcoin
            price = data["USD"]

            # Verifica se il prezzo ha raggiunto il livello desiderato
            if price >= desired_price:
                # Invia un messaggio al bot
                bot.send_message(chat_id=message.chat.id, text="The price of Bitcoin has reached the desired level! $: " +str(price))
                play_audio(f"The price of Bitcoin (BTC) has reached the desired level! {price}")
                break
            else:
                # Attendi per un certo periodo di tempo prima di controllare di nuovo il prezzo
                time.sleep(300)
    
    @bot.message_handler(commands=['convert'])
    def set_convert(message):
        bot.send_message(chat_id=message.chat.id, text="Enter the amount to be converted:")
        bot.register_next_step_handler(message, convert)
    
    def convert(message):
       # Indirizzo API per il tasso di cambio USD/EUR
        url = "https://api.exchangerate-api.com/v4/latest/USD"

        # Invia la richiesta e recupera i dati
        response = requests.get(url)
        data = response.json()

        # Recupera il tasso di cambio USD/EUR
        exchange_rate = data["rates"]["EUR"]
        try:
        # Prendi l'importo in dollari da convertire
            dollars = float(message.text)

            # Converte dollari in euro
            euros = dollars * exchange_rate

            # Invia un messaggio al bot con il risultato
            bot.send_message(chat_id=message.chat.id, text="{} USD = {:.2f} EUR".format(dollars, euros))
        except ValueError:
            # Invia un messaggio di errore se l'input non è valido
            bot.send_message(chat_id=message.chat.id, text="Invalid input. Please enter a valid amount.")

    @bot.message_handler(commands=['price_eth'])
    
    def price_eth(message):
        url = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD&api_key={my_api_key}"
        response = requests.get(url).json()
        price = response["USD"]
        # Creare l'oggetto Message
        bot.send_message(chat_id=message.chat.id, text="Price of Ethereum (ETH): $ " + str(price))
        play_audio(f"Price of Ethereum {price}")

    @bot.message_handler(commands=['graph_eth'])
    def grafico_eth(message):
       
        # Specificare l'intervallo di tempo desiderato
       # start_time = "1640995200" # 2022-01-01 in formato timestamp
        end_time = str(tstamp) # Oggi in formato timestamp

        # Costruire la richiesta API
        url = "https://min-api.cryptocompare.com/data/v2/histoday?fsym=ETH&tsym=USD&limit=365&toTs=" + end_time
        
        # Invia la richiesta e recupera i dati
        response = requests.get(url)
        data = json.loads(response.text)

        # Estrazione dei prezzi dai dati
        prices = [item["close"] for item in data["Data"]["Data"]]
        
        # disegnare il grafico del prezzo
        plt.plot(prices)
        plt.xlabel("Days")
        plt.ylabel("Price (ETH)")
        plt.title("Price of Ethereum (ETH) in USD over the past year")
        # save plot to PNG file
        plt.savefig('prices_eth.png')
        #plt.show()
        chat_id = message.chat.id
        with open("prices_eth.png", "rb") as f:
            bot.send_photo(chat_id, f)
        try:
            time.sleep(1)
            os.remove('prices_eth.png')
        except PermissionError:
            print(f"Could not remove file {'prices_eth.png'}")

    @bot.message_handler(commands=['alert_eth'])
    def set_alert_eth(message):
        bot.send_message(chat_id=message.chat.id, text="Enter the desired price (ETH):")
        bot.register_next_step_handler(message, set_desired_price_eth)

    def set_desired_price_eth(message):
        # Definire il livello di prezzo desiderato
        desired_price = int(message.text)

        while True:
            # Recuperare il prezzo attuale di Bitcoin
            url = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD"
            response = requests.get(url)
            data = response.json()

            # Recuperare il prezzo di Bitcoin
            price = data["USD"]

            # Verifica se il prezzo ha raggiunto il livello desiderato
            if price >= desired_price:
                # Invia un messaggio al bot
                bot.send_message(chat_id=message.chat.id, text="The price of Ethereum (ETH) has reached the desired level! $: " +str(price))
                play_audio(f"The price of Ethereum (ETH) has reached the desired level! {price}")
                break
            else:
                # Attendi per un certo periodo di tempo prima di controllare di nuovo il prezzo
                time.sleep(300)
    
    
    @bot.message_handler(commands=['wiki'])
    def handle_wiki_search(message):
        
        bot.send_message(chat_id=message.chat.id, text="Enter the term you want to search on Wikipedia")
        bot.register_next_step_handler(message, handle_wiki_query)
    #Dopo aver inviato un messaggio al bot per richiedere la query di ricerca di Wikipedia, il bot deve essere in grado di acquisire la query da parte dell'utente. Questo può essere fatto utilizzando un nuovo handler con bot.register_next_step_handler().
    def handle_wiki_query(message):
        query = message.text
        page = wiki_wiki.page(query)
        if page.exists():
            bot.send_message(chat_id=message.chat.id, text=page.text[0:min(len(page.text), 4096)])
            bot.send_message(chat_id=message.chat.id, text=page.title + "\n" + page.fullurl)
        else:
            bot.send_message(chat_id=message.chat.id, text='I did not find information on this topic on Wikipedia.')

    bot.polling()

if __name__ == "__main__":
    main(token)
   

   
