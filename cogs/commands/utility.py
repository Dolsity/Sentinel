from nextcord.ext import commands
import nextcord
from nextcord import Interaction
from utils.config import embed_color, owner_id

class Utility(commands.Cog, name="Utility", description="Utility Commands"):
    def __init__(self, bot):
        self.bot = bot
    
    COG_EMOJI = "🔨"

    @commands.command(name="ping")
    async def command_ping(self, interaction : Interaction):
        """Latency of Fora"""
        await interaction.trigger_typing()
        embed = nextcord.Embed(
            title=f":ping_pong: Pong!", color=embed_color
        )
        embed.add_field(
            name="API Latency",
            value=f"{round(self.bot.latency*1000)}ms", inline=False
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        await interaction.send(embed=embed)

    @commands.command(name="about", aliases=["information"])
    async def command_about(self, interaction : Interaction):
        """Information about the bot"""
        await interaction.trigger_typing()

        embed = nextcord.Embed(
            title=f"Information about {self.bot.user.name}", color=embed_color
        )
        embed.set_author(
            name=self.bot.user.name, icon_url=self.bot.user.display_avatar
        )

        # mention the owners
        if isinstance(owner_id, list):
            owners = [self.bot.get_user(user_id) for user_id in owner_id]
            owners = [owner.mention for owner in owners]
            owners = ", ".join(owners)
        else:
            owners = self.bot.get_user(owner_id).mention

        embed.add_field(
            name="Information", 
            value=f"**» Developer:** {owners}\n", inline=False
        )
        embed.add_field(
            name="Statistics",
            # Amount of users in the guilds the bot is in
            value=f"**» Total Users:** {len(list(self.bot.get_all_members()))}\n"
                  f"**» API Latency:** {round(self.bot.latency*1000)}ms", inline=False
        )
        await interaction.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Utility(bot))