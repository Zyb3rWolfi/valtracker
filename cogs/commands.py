import nextcord
from nextcord.ext import commands
import valorant
import os
import sqlite3
import requests

database = sqlite3.connect("database.db")
cursor = database.cursor()

class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Command to check someones stats from past 30 games
    @nextcord.slash_command(guild_ids=[1113264588545331242])
    async def account(self, interaction : nextcord.Interaction, username : str, tag: str):

        # Variables to store the total stats
        total_kills = 0
        total_deaths = 0
        total_assists = 0

        # API request to get the uuid of the player
        url = "https://api.henrikdev.xyz/valorant/v1/account/" + username + "/" + tag
        response = requests.get(url) 
        uuid = response.json()["data"]["puuid"]

        # API request to get the rank of the player
        mmr_url = "https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/" + "eu" + "/" + uuid
        mmr_response = requests.get(mmr_url)
        rank = mmr_response.json()["data"]["current_data"]["currenttierpatched"]

        # API request to get the match history of the player
        match_history = "https://api.henrikdev.xyz/valorant/v1/by-puuid/lifetime/matches/" + "eu" + "/" + uuid
        match_history_response = requests.get(match_history).json()

        # Loops through the match history
        for stats in match_history_response["data"]:
            
            # Gets the stats from the match
            kill = stats["stats"]["kills"]
            total_kills += kill

            deaths = stats["stats"]["deaths"]
            total_deaths += deaths

            assists = stats["stats"]["assists"]
            total_assists += assists

        # Embed creation
        embed = nextcord.Embed(title="Competitive Career Stats", description="", color=nextcord.Color.red())
        embed.set_author(name=username + "#" + tag, icon_url=response.json()["data"]["card"]["small"])
        embed.set_thumbnail(url=response.json()["data"]["card"]["small"])
        embed.add_field(name="Rank", value=f"{rank} <:plat3:1138237183787008010>", inline=True)
        embed.add_field(name="K/D", value=round(total_kills/total_deaths, 2), inline=True)
        embed.add_field(name="KDA", value=round((total_kills + total_assists) / total_deaths, 2), inline=True)
        embed.add_field(name="Kills", value=total_kills, inline=True)
        embed.add_field(name="Deaths", value=total_deaths, inline=True)
        embed.add_field(name="Assists", value=total_assists, inline=True)
        embed.add_field(name="Most Kills", value=f"Most Kills Goes here", inline=True)
        embed.add_field(name="Playtime", value=f"Playtime Goes here", inline=True)

        await interaction.response.send_message(embed=embed)

    # Command to link your account to your discord account
    @nextcord.slash_command(guild_ids=[1113264588545331242])    
    async def link(self, interaction : nextcord.Interaction, name : str, tag : str):

        # Variables to store the total stats
        total_kills = 0
        total_deaths = 0
        total_assists = 0

        # API request to get the uuid of the player
        url = "https://api.henrikdev.xyz/valorant/v1/account/" + name + "/" + tag
        response = requests.get(url)
        uuid = response.json()["data"]["puuid"]

        # API request to get the rank of the player
        mmr_url = "https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/" + "eu" + "/" + uuid
        mmr_response = requests.get(mmr_url)
        rank = mmr_response.json()["data"]["current_data"]["currenttierpatched"]

        # API request to get the match history of the player
        match_history = "https://api.henrikdev.xyz/valorant/v1/by-puuid/lifetime/matches/" + "eu" + "/" + uuid
        match_history_response = requests.get(match_history).json()
        last_match = match_history_response["data"][0]["meta"]["id"]

        # Loops through the match history
        for stats in match_history_response["data"]:
            
            # Gets the stats from the match
            kill = stats["stats"]["kills"]
            total_kills += kill

            deaths = stats["stats"]["deaths"]
            total_deaths += deaths

            assists = stats["stats"]["assists"]
            total_assists += assists

        # Checks if the user has already linked an account
        linked_any = cursor.execute("SELECT * FROM users WHERE linked_to=?", (interaction.user.id,)).fetchone()
        # Checks if the user has already linked the account they are trying to link
        if not linked_any:

            # Inserts the data into the database
            cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, tag, uuid, total_kills, total_deaths, total_assists, rank, 0, 0, interaction.user.id))
            cursor.execute("INSERT INTO matches VALUES(?, ?, ?)", (last_match, uuid, interaction.user.id))
            database.commit()

            embed = nextcord.Embed(title="Account Linked", description="", color=nextcord.Color.red())
            embed.set_author(name=name + "#" + tag, icon_url=response.json()["data"]["card"]["small"])
            embed.set_thumbnail(url=response.json()["data"]["card"]["small"])
            embed.add_field(name="Account Linked", value=f"Account Linked", inline=True)

            await interaction.response.send_message(embed=embed)
        # If the user has already linked an account
        else:
            if linked_any[0] == name:
                await interaction.response.send_message("Account already linked, run /unlink to unlink your account")
            else:

                await interaction.response.send_message("Account already linked to another user")
    
    # Command to check the linked account stats
    @nextcord.slash_command(guild_ids=[1113264588545331242])
    async def me(self, interaction : nextcord.Interaction):

        # Gets the data from the database
        player_data = cursor.execute("SELECT * FROM users WHERE linked_to=?", (interaction.user.id,)).fetchone()
        username = player_data[0]
        tag = player_data[1]
        kills = player_data[3]
        deaths = player_data[4]
        assists = player_data[5]
        rank = player_data[6]
        most_kills = player_data[7]
        playtime = player_data[8]
        playtime = round(playtime / 60, 2)

        # API request to get the playercard
        url = "https://api.henrikdev.xyz/valorant/v1/account/" + username + "/" + tag
        response = requests.get(url)
        playercard = response.json()["data"]["card"]["small"]

        # Embed creation
        embed = nextcord.Embed(title="Competitive Career Stats", description="", color=nextcord.Color.red())
        embed.set_author(name=username + "#" + tag, icon_url=playercard)
        embed.set_thumbnail(url=playercard)
        embed.add_field(name="Rank", value=f"{rank} <:plat3:1138237183787008010>", inline=True)
        embed.add_field(name="K/D", value=round(kills/deaths, 2), inline=True)
        embed.add_field(name="KDA", value=round((kills + assists) / deaths, 2), inline=True)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="Assists", value=assists, inline=True)
        embed.add_field(name="Most Kills", value=most_kills, inline=True)
        embed.add_field(name="Playtime", value=f"{playtime} Hours", inline=True)
        await interaction.response.send_message(embed=embed)

def setup(bot):

    bot.add_cog(Commands(bot))