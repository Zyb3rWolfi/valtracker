import nextcord
from nextcord.ext import commands
import os
import sqlite3
import requests
import datetime

database = sqlite3.connect("database.db")
cursor = database.cursor()

headers = {
    "Authorization" : os.environ["KEY"]
}

class Select(nextcord.ui.Select):
    def __init__(self, uuid):
        self.uuid = uuid

        options = []
        i = 0
        matches = requests.get("https://api.henrikdev.xyz/valorant/v1/by-puuid/lifetime/matches/" + "eu" + "/" + uuid).json()
        matches = matches["data"]

        for match in matches:
            if i == 10:
                break
            date = match["meta"]["started_at"]
            date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
            date = date.date()

            game_score = str(match["teams"]["red"]) + " - " + str(match["teams"]["blue"])

            kills = match["stats"]["kills"]
            deaths = match["stats"]["deaths"]
            assists = match["stats"]["assists"]
            score = match["stats"]["score"]

            options.append(nextcord.SelectOption(label=f"{i} Results: {game_score}",description=f"Kils: {kills} | Deaths: {deaths} | Assists: {assists} | Score: {score}"))
            i += 1
            
        super().__init__(placeholder="Select a match",max_values=1,min_values=1,options=options)
    
    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0].split(" ")[0]
        matches = requests.get("https://api.henrikdev.xyz/valorant/v1/by-puuid/lifetime/matches/" + "eu" + "/" + self.uuid).json()
        match = matches["data"][int(value)]

        player_card = requests.get("https://api.henrikdev.xyz/valorant/v1/by-puuid/account" + "/" + self.uuid, headers=headers).json()
        player_card = player_card["data"]["card"]["small"]


        kills = match["stats"]["kills"]
        deaths = match["stats"]["deaths"]
        assists = match["stats"]["assists"]
        score = match["stats"]["score"]
        head = match["stats"]["shots"]["head"]
        body = match["stats"]["shots"]["body"]
        leg = match["stats"]["shots"]["leg"]
        time_started = match["meta"]["started_at"]
        time_started = datetime.datetime.strptime(time_started, "%Y-%m-%dT%H:%M:%S.%f%z")
        hs = round(((head) / (body + leg + head) * 100), 2)
        teams = matches["data"][int(value)]["teams"]

        embed = nextcord.Embed(title="Match Results: " + str(teams["red"]) + " - " + str(teams["blue"]), description=f"For " + matches["name"], color=nextcord.Color.red())
        embed.set_thumbnail(url=player_card)
        embed.add_field(name="K/D", value=round(kills/deaths, 2), inline=True)
        embed.add_field(name="KDA", value=round((kills + assists) / deaths, 2), inline=True)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="Assists", value=assists, inline=True)
        embed.add_field(name="HS%", value=hs, inline=True)
        embed.set_footer(text=f"{time_started.date()} | {time_started.time()}")

        await interaction.response.send_message(embed=embed)

class SelectView(nextcord.ui.View):
    def __init__(self,uuid, *, timeout = 180,):
        self.uuid = uuid
        super().__init__(timeout=timeout)
        self.add_item(Select(self.uuid))

class MatchHistory(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=[1113264588545331242])
    async def setup(self, interaction : nextcord.Interaction):
        i = 0
        query = "SELECT * FROM users"
        users = cursor.execute(query).fetchall()

        for user in users:

            uuid = user[2]

            fetch_matches = requests.get("https://api.henrikdev.xyz/valorant/v1/by-puuid/lifetime/matches/" + "eu" + "/" + uuid).json()
            for match in fetch_matches["data"]:
                match_id = match["meta"]["id"]
                query = "INSERT INTO match_history VALUES(?, ?)"
                cursor.execute(query, (match_id, uuid))
                database.commit()

        await interaction.response.send_message("Done!", ephemeral=True)
    
    @nextcord.slash_command(guild_ids=[1113264588545331242])
    async def history(self, interaction : nextcord.Interaction):
        i = 0
        query = "SELECT * FROM users WHERE linked_to = ?"
        user = cursor.execute(query, (interaction.user.id,)).fetchone()

        matches = requests.get("https://api.henrikdev.xyz/valorant/v1/by-puuid/lifetime/matches/" + "eu" + "/" + user[2]).json()
        matches = matches["data"]

        embed = nextcord.Embed(title="Match history", description="Select a match from the dropdown", color=nextcord.Color.green())
        
        await interaction.response.send_message(embed=embed, ephemeral=True, view=SelectView(user[2]))


def setup(bot):
    bot.add_cog(MatchHistory(bot))