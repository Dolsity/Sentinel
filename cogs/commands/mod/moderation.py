from nextcord.ext import commands
import nextcord
from nextcord import Interaction
import datetime
from utils.config import embed_color, embed_error_color, owner_id
from utils.database import warnings


class Moderation(commands.Cog, name="Moderation", description="Moderation Commands"):
    def __init__(self, bot):
        self.bot = bot
    
    COG_EMOJI = "🛠"

    @commands.command(name="warn")
    async def command_warn_user(self, interaction : Interaction, user : nextcord.Member = None, *, reason : str = None):
        """Warn a user"""
        await interaction.trigger_typing()

        if interaction.author.id not in owner_id:
            embed = nextcord.Embed(
                title=":x: Error", description="You're not the owner of this bot.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user is None:
            embed = nextcord.Embed(
                title=":x: Error", description="Please specify a user to warn.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if reason is None:
            embed = nextcord.Embed(
                title=":x: Error", description="Please specify a reason for warning this user.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user.id == owner_id:
            embed = nextcord.Embed(
                title=":x: Error", description="You can't warn the owners of the bot.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user == interaction.author :
            embed = nextcord.Embed(
                title=":x: Error", description="You can't warn yourself.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        # check if user is a bot
        if user.bot:
            embed = nextcord.Embed(
                title=":x: Error", description="You can't warn bots.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        warn_data = warnings.find_one({"_id": user.id})
        if warn_data is not None:
            warnings.update_one({"_id": user.id}, {
                "$inc": {"warn_points": 2},
                "$push": {
                    "author_id": interaction.author.id,
                    "time": nextcord.utils.format_dt(datetime.datetime.now(), style='f'),
                    "reason": reason
                }
            })
        else:
            warnings.insert_one({
                "_id": user.id,
                "warn_points": 2,
                "author_id": [interaction.author.id],
                "time": [nextcord.utils.format_dt(datetime.datetime.now(), style='f')],
                "reason": [reason]
            })

        embed = nextcord.Embed(
            title=":white_check_mark: Success", description=f"{user.mention} has been warned.", color=embed_color
        )
        await interaction.send(embed=embed)


    @commands.command(name="warnings", aliases=["warns"])
    async def command_warnings(self, interaction : Interaction, user : nextcord.Member = None):
        """View a user's warnings"""
        await interaction.trigger_typing()

        if user is None:
            embed = nextcord.Embed(
                title=":x: Error", description="Please specify a user to view their warnings.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user.id == owner_id:
            embed = nextcord.Embed(
                title=":x: Error", description="You're not the owner of this bot.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        warn_data = warnings.find_one({"_id": user.id})
        if warn_data is None:
            embed = nextcord.Embed(
                title=":white_check_mark: Success", description=f"{user.mention} has no warnings.", color=embed_color
            )
            await interaction.send(embed=embed)
            return

        embed = nextcord.Embed(
            title=f"{user.name}'s Warnings",
            description=f"{user.mention} has `{warn_data['warn_points']}` warning points.",
            color=embed_color
        )

        pagination = list(zip(warn_data["author_id"], warn_data["time"], warn_data["reason"]))
        pages = [pagination[i:i + 10] for i in range(0, len(pagination), 10)]
        page = 0
        num = 1

        for i in pages:
            embed.clear_fields()
            for author_id, time, reason in i:
                embed.add_field(
                    name=f"#{num}", 
                    value=f"**Moderator:** <@{author_id}> ({author_id})\n"
                        f"**Time:** {time}\n"
                        f"**Reason:** {reason}", 
                    inline=False
                )
                num += 1
            embed.set_footer(text=f"Page {page + 1} of {len(pages)}\nUse the buttons to navigate through pages.")
            await interaction.send(embed=embed)
            page += 1

    @commands.command(name="clearwarnings", aliases=["clearwarns"])
    async def command_clearwarns(self, interaction : Interaction, user : nextcord.Member = None):
        """Clear a user's warnings"""
        await interaction.trigger_typing()

        if interaction.author.id not in owner_id:
            embed = nextcord.Embed(
                title=":x: Error", description="You're not the owner of this bot.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        if user is None:
            embed = nextcord.Embed(
                title=":x: Error", description="Please specify a user to clear their warnings.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        warn_data = warnings.find_one({"_id": user.id})
        if warn_data is None:
            embed = nextcord.Embed(
                title=":x: Error", description=f"{user.mention} has no warnings.", color=embed_error_color
            )
            await interaction.send(embed=embed)
            return
        
        warnings.delete_one({"_id": user.id})

        embed = nextcord.Embed(
            title=":white_check_mark: Success", description=f"{user.mention}'s warnings have been cleared.", color=embed_color
        )
        await interaction.send(embed=embed)

    

def setup(bot):
    bot.add_cog(Moderation(bot))