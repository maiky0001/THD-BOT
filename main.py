import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Modal, TextInput
from datetime import datetime
import csv
import os

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

registered_teams = []
validated_payments = set()
payment_proofs = {}
created_channels = {}

ADMIN_IDS = [528285212854190111]  # Ton ID Discord
GUILD_ID = 1363467607809982495    # ID du serveur Discord
CATEGORY_NAME = "Équipes Boarding Brawl"

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print(f"Erreur : Le bot ne trouve pas le serveur avec l'ID {GUILD_ID}.")
    else:
        print(f"Bot connecté au serveur : {guild.name}")
        try:
            synced = await bot.tree.sync(guild=guild)
            print(f"Commandes slash synchronisées ({len(synced)})")
        except Exception as e:
            print(f"Erreur de synchronisation : {e}")
    reminders.start()

@bot.tree.command(name="inscription", description="Inscrire une équipe", guild=discord.Object(id=GUILD_ID))
async def inscription(interaction: discord.Interaction):
    await interaction.response.send_modal(InscriptionModal())

@bot.tree.command(name="payer", description="Envoyer la preuve de paiement", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(nom_equipe="Nom de l'équipe")
async def payer(interaction: discord.Interaction, nom_equipe: str):
    if not interaction.attachments:
        await interaction.response.send_message("Merci de joindre une capture d’écran de votre paiement.", ephemeral=True)
        return
    attachment_url = interaction.attachments[0].url
    payment_proofs[nom_equipe] = attachment_url
    await interaction.response.send_message(f"Preuve de paiement reçue pour **{nom_equipe}**. En attente de validation par un admin.", ephemeral=True)

@bot.tree.command(name="valider", description="Valider un paiement (admin)", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(nom_equipe="Nom de l'équipe")
async def valider(interaction: discord.Interaction, nom_equipe: str):
    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("Tu n’as pas la permission de faire ça.", ephemeral=True)
        return
    if nom_equipe not in payment_proofs:
        await interaction.response.send_message("Aucune preuve de paiement trouvée pour cette équipe.", ephemeral=True)
        return
    validated_payments.add(nom_equipe)
    await interaction.response.send_message(f"Paiement validé pour **{nom_equipe}** !")

@bot.tree.command(name="statuts", description="Voir les statuts des paiements", guild=discord.Object(id=GUILD_ID))
async def statuts(interaction: discord.Interaction):
    if not registered_teams:
        await interaction.response.send_message("Aucune équipe enregistrée.")
        return
    msg = "**Statuts de paiement :**
"
    for team in registered_teams:
        statut = "Payé" if team['nom'] in validated_payments else "En attente"
        msg += f"- {team['nom']}: {statut}
"
    await interaction.response.send_message(msg)

@bot.tree.command(name="equipes", description="Afficher les équipes inscrites", guild=discord.Object(id=GUILD_ID))
async def equipes(interaction: discord.Interaction):
    if not registered_teams:
        await interaction.response.send_message("Aucune équipe inscrite pour le moment.")
        return
    msg = "**Équipes inscrites :**
"
    for i, team in enumerate(registered_teams, start=1):
        status = "Payé" if team['nom'] in validated_payments else "En attente"
        msg += f"{i}. {team['nom']} - Capitaine: {team['capitaine_discord']} - Statut: {status}
"
    await interaction.response.send_message(msg)

@bot.tree.command(name="aide", description="Afficher les commandes disponibles", guild=discord.Object(id=GUILD_ID))
async def aide(interaction: discord.Interaction):
    help_text = (
        "**Commandes disponibles :**
"
        "/inscription - Inscription via modal
"
        "/payer <NomEquipe> + pièce jointe (screenshot)
"
        "/valider <NomEquipe> (admin seulement)
"
        "/statuts - Voir les paiements
"
        "/equipes - Voir les équipes
"
        "/aide - Ce message"
    )
    await interaction.response.send_message(help_text, ephemeral=True)

@tasks.loop(hours=6)
async def reminders():
    guild = bot.get_guild(GUILD_ID)
    if guild:
        general = discord.utils.get(guild.text_channels, name="taverne")
        if general:
            await general.send("⛵ **Rappel : Le tournoi Boarding Brawl approche ! N’oubliez pas de vous inscrire et d’envoyer votre paiement !** 🏴‍☠️")

class InscriptionModal(Modal, title="Inscription Boarding Brawl"):
    equipe = TextInput(label="Nom de l'équipe")
    capitaine = TextInput(label="Pseudo In-Game du capitaine")
    membre1 = TextInput(label="Membre 1 (@ ou pseudo)", required=False)
    membre2 = TextInput(label="Membre 2 (@ ou pseudo)", required=False)
    membre3 = TextInput(label="Membre 3 (@ ou pseudo)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = [
            self.equipe.value,
            self.capitaine.value,
            self.membre1.value or "N/A",
            self.membre2.value or "N/A",
            self.membre3.value or "N/A",
            interaction.user.name,
            now
        ]
        with open("inscriptions.csv", "a", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(data)

        registered_teams.append({
            "nom": self.equipe.value,
            "capitaine_ig": self.capitaine.value,
            "capitaine_discord": interaction.user.name
        })
        await interaction.response.send_message(f"✅ Équipe **{self.equipe.value}** inscrite avec succès !", ephemeral=True)
        guild = bot.get_guild(GUILD_ID)
        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if not category:
            category = await guild.create_category(CATEGORY_NAME)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel_name = self.equipe.value.lower().replace(" ", "-")
        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        created_channels[self.equipe.value] = channel.id

bot.run(os.getenv("TOKEN"))
