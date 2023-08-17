import nextcord
from nextcord.ext import commands
import os
import sqlite3

database = sqlite3.connect("database.db")
cursor = database.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(name TEXT, tag TEXT, uuid TEXT, kills INTEGER, deaths INTEGER, assists INTEGER, rank TEXT, most_kills INTEGER, playtime INTEGER)")


intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

cogs = [
    "cogs.commands",
    "cogs.events"
]

@bot.event
async def on_ready():
    print("Ready!")

if __name__ == "__main__":

    for cog in cogs:
        bot.load_extension(cog)



bot.run(os.environ["BOT_TOKEN"])