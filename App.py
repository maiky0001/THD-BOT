from flask import Flask
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Charger le .env
load_dotenv()

app = Flask(__name__)

port = int(os.getenv("PORT", 5000))  # Définit le port ou utilise 5000 par défaut
app.run(host="0.0.0.0", port=port)

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
    bot.loop.create_task(run_bot())
    app.run(debug=True, use_reloader=False)  # use_reloader=False pour éviter de redémarrer le serveur Flask à chaque changement

async def run_bot():
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == '__main__':
    run()

