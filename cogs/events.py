import nextcord
from nextcord.ext import commands, tasks
import sqlite3
import os
import requests

database = sqlite3.connect("database.db")
cursor = database.cursor()

headers = {
    "Authorization" : os.environ["KEY"]
}

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.update.start()

    
    @tasks.loop(seconds=60)
    async def update(self):
        print("Updating")
        
        # Get all players from database
        players = cursor.execute("SELECT * FROM users").fetchall()

        # Loop through all players
        for player in players:
            uuid = player[2]
            # Get last match from database
            match = cursor.execute("SELECT * FROM matches WHERE puuid = ?", (player[2],)).fetchone()

            # If no match found
            if not match:
                print("No match found")
            
            # If match found
            else:
                
                # Gets latest match data from the API and saves the mode and the id of the match
                request = requests.get("https://api.henrikdev.xyz/valorant/v1/by-puuid/lifetime/matches/" + "eu" + "/" + player[2] + "?size=1").json()
                match_id = request["data"][0]["meta"]["id"]
                mode = request["data"][0]["meta"]["mode"]

                time_wasted = requests.get("https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/" + "eu" + "/" + player[2]).json()
                time_wasted = time_wasted["data"][0]["metadata"]["game_length"]
                time_wasted = time_wasted / 60

                rank = requests.get("https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr/" + "eu" + "/" + player[2]).json()
                rank = rank["data"]["currenttierpatched"]

                player_card = requests.get("https://api.henrikdev.xyz/valorant/v1/by-puuid/account" + "/" + uuid, headers=headers).json()
                player_card = player_card["data"]["card"]["small"]
                
                # If the match id is the same as the last match id in the database
                if match_id != match[0]:
                    
                    # If the mode is competitive
                    if mode == "Competitive":
                        
                        # Sets the variables from the database to get the total stats
                        total_kills = player[3]
                        total_deaths = player[4]
                        total_assists = player[5]
                        total_time = player[8]
                        most_kills = player[7]
                        print(total_time)

                        # Gets the data from the latest match via the API
                        kills = request["data"][0]["stats"]["kills"]
                        deaths = request["data"][0]["stats"]["deaths"]
                        assists = request["data"][0]["stats"]["assists"]
                        team_on = request["data"][0]["stats"]["team"]
                        hs = round(((request["data"][0]["stats"]["shots"]["head"]) / (request["data"][0]["stats"]["shots"]["body"] + request["data"][0]["stats"]["shots"]["leg"] + request["data"][0]["stats"]["shots"]["head"]) * 100), 2)
                        teams = request["data"][0]["teams"]

                        # Does maths stuff
                        total_kills += kills
                        total_deaths += deaths
                        total_assists += assists
                        total_time += time_wasted
                        print(total_time)
                        won = "Match WON " + str(teams["red"]) + ":" + str(teams["blue"])
                        lost = "Match LOST " + str(teams["red"]) + ":" + str(teams["blue"])

                        if team_on == "Red":
                            if teams["red"] > teams["blue"]:
                                embed = nextcord.Embed(title=won, description=f"{player[0]}#{player[1]}", color=nextcord.Color.green())
                            else:
                                embed = nextcord.Embed(title=lost + teams["red"] + ":" + teams["blue"], description=f"{player[0]}#{player[1]}", color=nextcord.Color.red())
                        else:
                            if teams["blue"] > teams["red"]:
                                embed = nextcord.Embed(title=won + teams["red"] + ":" + teams["blue"], description=f"{player[0]}#{player[1]}", color=nextcord.Color.green())
                            else:
                                embed = nextcord.Embed(title=won + teams["red"] + ":" + teams["blue"], description=f"{player[0]}#{player[1]}", color=nextcord.Color.red())

                        # Embed creation
                        embed.set_thumbnail(url=player_card)
                        embed = nextcord.Embed(title="Match Overview", description=f"For {player[0]}#{player[1]}", color=nextcord.Color.red())
                        embed.add_field(name="K/D", value=round(kills/deaths, 2), inline=True)
                        embed.add_field(name="KDA", value=round((kills + assists) / deaths, 2), inline=True)
                        embed.add_field(name="Kills", value=kills, inline=True)
                        embed.add_field(name="Deaths", value=deaths, inline=True)
                        embed.add_field(name="Assists", value=assists, inline=True)
                        embed.add_field(name="HS%", value=hs, inline=True)

                        # Gets the channel
                        channel = self.bot.get_channel(1138218881517895700)
                        if most_kills < kills:

                            most_kills = kills
                        
                        try:
                            print("Sending embed")
                            # Sends the embed
                            await channel.send(embed=embed)

                            # Updates the database
                            cursor.execute("UPDATE users SET kills = ?, deaths = ?, assists = ?, rank = ?, playtime = ?, most_kills = ? WHERE uuid = ?", (total_kills, total_deaths, total_assists, rank, total_time, most_kills, player[2],))
                            cursor.execute("UPDATE matches SET last_match = ? WHERE puuid = ?", (match_id, player[2],))
                            database.commit()

                        except:
                            pass



def setup(bot):

    bot.add_cog(Events(bot))