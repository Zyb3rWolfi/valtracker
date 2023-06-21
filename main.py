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

    account = client.get_user_by_name("Vague Zyb3rWolfi#6666")
    match = account.matchlist().history.find(queueId="competitive")

    match = match.get()
    print(match)
bot.run(os.environ["BOT_TOKEN"])