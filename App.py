from flask import Flask
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

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

# Récupérer le port depuis la variable d'environnement ou 5000 par défaut
port = int(os.getenv("PORT", 5000))

# Lancer le serveur Flask et le bot Discord en même temps
def run():
    bot.loop.create_task(run_bot())
    app.run(host="0.0.0.0", port=port)  # Lancer Flask sur le port correct

async def run_bot():
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == '__main__':
    run()
