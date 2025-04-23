from flask import Flask
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import threading

# Charger le .env
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot en ligne et prêt!"

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Lancer le bot
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

# Lancer le serveur Flask et le bot Discord en même temps
def run():
    # Démarrer Flask dans un thread séparé
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000))))
    flask_thread.start()

    # Lancer le bot
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == '__main__':
    run()
