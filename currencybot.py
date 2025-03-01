import telebot
import requests
import re
import os
import threading
import time
from flask import Flask

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

CURRENCY_API_URL = "https://v6.exchangerate-api.com/v6/5d1b71b70708406fecea761b/latest/USD"

def get_exchange_rate(currency):
    try:
        response = requests.get(CURRENCY_API_URL)
        data = response.json()
        if "UZS" in data['conversion_rates'] and currency in data['conversion_rates']:
            usd_to_uzs = data['conversion_rates']["UZS"]
            currency_to_usd = data['conversion_rates'][currency]
            rate = usd_to_uzs / currency_to_usd
            return round(rate, 2)
        return None
    except Exception:
        return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = ("👋 Hello! Send a message like:\n"
            "💵 `100 USD` - Convert 100 dollars to UZS\n"
            "💶 `50 EUR` - Convert 50 euros to UZS")
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def convert_currency(message):
    match = re.match(r'(\d+)\s*(USD|EUR)', message.text.upper())
    if match:
        amount = int(match.group(1))
        currency = match.group(2)
        rate = get_exchange_rate(currency)
        if rate:
            converted_amount = round(amount * rate, 2)
            bot.send_message(message.chat.id, f"✅ {amount} {currency} = {converted_amount} UZS 🇺🇿")
        else:
            bot.send_message(message.chat.id, "❌ Failed to retrieve exchange rate.")
    else:
        bot.send_message(message.chat.id, "⚠ Please enter a valid format (e.g., `100 USD` or `50 EUR`).")

# Flask web server to bind a port for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Currency Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Render assigns a PORT
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Start Flask server in a separate thread
    print("✅ Bot is running...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
