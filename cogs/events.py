import nextcord
from nextcord.ext import commands
import valorant
import os

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.client = valorant.Client(os.environ["KEY"], region="eu", locale=None)



    @nextcord.slash_command(guild_ids=[1113264588545331242])
    async def status(self, interaction : nextcord.Interaction):
        
        status = []
        status = self.client.get_platform_status().incidents
        for incident in status:
            embed = nextcord.Embed(title=incident.titles[0].content, description=incident.updates[0].translations[0].content, color=nextcord.Color.red())
            await interaction.response.send_message(embed=embed)

def setup(bot):

    bot.add_cog(Events(bot))