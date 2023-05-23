from nextcord.ext import commands
import nextcord
from nextcord import Interaction
from utils.config import embed_color, embed_error_color, owner_id
from utils.database import blacklist_user_add, blacklist_user_get, blacklist_user_remove

class Moderation(commands.Cog, name="Moderation", description="Moderation Commands"):
    def __init__(self, bot):
        self.bot = bot
    
    COG_EMOJI = "⚒️"

    @commands.command(name="blacklist", aliases=["bl"])
    async def command_blacklist_user(self, interaction : Interaction, user : nextcord.Member = None, *, reason : str = None):
        """Blacklist a user from using the bot"""
        await interaction.trigger_typing()

        if interaction.author.id not in owner_id:
            embed = nextcord.Embed(
                title=":x: Error", description="You're not the owner of this bot.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user is None:
            embed = nextcord.Embed(
                title=":x: Error", description="Please specify a user to blacklist.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if reason is None:
            embed = nextcord.Embed(
                title=":x: Error", description="Please specify a reason for blacklisting this user.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user.id == owner_id:
            embed = nextcord.Embed(
                title=":x: Error", description="You can't blacklist the owners of the bot.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user == interaction.author :
            embed = nextcord.Embed(
                title=":x: Error", description="You can't blacklist yourself.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user == user.bot:
            embed = nextcord.Embed(
                title=":x: Error", description="You can't blacklist a bot.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if blacklist_user_get(user_id=user.id) is not None:
            embed = nextcord.Embed(
                title=":x: Error", description="This user is already blacklisted.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        blacklist_user_add(user_id=user.id, author_id=interaction.author.id, reason=reason)
        embed = nextcord.Embed(
            title=":white_check_mark: Success", description=f"{user.mention} has been successfully blacklisted from using the bot.", color=embed_color
        )
        await interaction.send(embed=embed)


    @commands.command(name="unblacklist", aliases=["ubl"])
    async def command_unblacklist_user(self, interaction : Interaction, user : nextcord.Member = None):
        """Unblacklist a user from using the bot"""

        if interaction.author.id not in owner_id:
            embed = nextcord.Embed(
                title=":x: Error", description="You're not the owner of this bot.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user is None:
            embed = nextcord.Embed(
                title=":x: Error", description="Please specify a user to unblacklist.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if blacklist_user_get(user_id=user.id) is None:
            embed = nextcord.Embed(
                title=":x: Error", description="This user is not blacklisted.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        blacklist_user_remove(user_id=user.id)
        embed = nextcord.Embed(
            title=":white_check_mark: Success", description=f"{user.mention} has been successfully unblacklisted from using the bot.", color=embed_color
        )
        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))