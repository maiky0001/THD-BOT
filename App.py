import os
import discord
from discord.ext import commands
from flask import Flask
import threading

# Récupérer le token de la variable d'environnement
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Code du bot Discord
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

# Commande de test pour vérifier que le bot fonctionne
@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")

# Route pour le serveur Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot est en ligne et fonctionne !"

# Fonction pour démarrer le bot Discord en tâche d'arrière-plan
def run_bot():
    bot.run(TOKEN)

# Démarrer le bot dans un thread séparé
def start_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    # Démarrer le bot dans un thread séparé
    threading.Thread(target=run_bot).start()

    # Démarrer Flask
    start_flask()
