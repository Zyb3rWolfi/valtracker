import nextcord
from nextcord.ext import commands
import requests
import os
import valorant
import json

key = os.environ["KEY"]
client = valorant.Client(key, region="eu", locale=None)

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("Ready!")

@bot.slash_command(guild_ids=[1113264588545331242])
async def rank(interaction : nextcord.Interaction, player : str):

    user = client.get_user_by_name(player)
    match = user.matchlist().history.find(queueId="competitive")

    match = match.get()

    for team in match.teams:

        players = match.players.get_all(teamId=team.teamId)

        for player in players:
            
            await interaction.response.send_message(f"{player.gameName} is {player.rank}")



bot.run(os.environ["BOT_TOKEN"])