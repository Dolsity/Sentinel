from nextcord.ext import commands
import nextcord
from nextcord import Interaction
from nextcord.utils import format_dt
from utils.config import embed_color, owner_id

class Utility(commands.Cog, name="Utility", description="Utility Commands"):
    def __init__(self, bot):
        self.bot = bot
    
    COG_EMOJI = "🔨"

    @commands.command(name="ping")
    async def command_ping(self, interaction : Interaction):
        """Latency of the bot"""
        await interaction.trigger_typing()
        embed = nextcord.Embed(
            title=f":ping_pong: Pong!", color=embed_color
        )
        embed.add_field(
            name="API Latency",
            value=f"{round(self.bot.latency*1000)}ms", inline=False
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        await interaction.reply(embed=embed, mention_author=False)


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
            value=f"**» Developer(s):** {owners}\n", inline=False
        )
        embed.add_field(
            name="Statistics",
            # Amount of users in the guilds the bot is in
            value=f"**» Total Users:** {len(list(self.bot.get_all_members()))}\n"
                  f"**» API Latency:** {round(self.bot.latency*1000)}ms", inline=False
        )
        await interaction.reply(embed=embed, mention_author=False)


    @commands.command(name="userinfo", aliases=["ui"])
    async def command_userinfo(self, interaction : Interaction, user : nextcord.Member = None):
        """Information about a user"""
        await interaction.trigger_typing()

        user = user or interaction.author

        embed = nextcord.Embed(
            title=f"Information about {user.name}", color=embed_color
        )
        embed.set_author(
            name=user.name, icon_url=user.display_avatar
        )
        
        embed.add_field(
            name="Basic Information",
            value=f"**User:** {user.mention} ({user.id})\n"
                  f"**Created:** {format_dt(user.created_at, style='R')}\n"
                  f"**Joined:** {format_dt(user.joined_at, style='R')}\n"
                  f"**Top Role:** {user.top_role.mention}", inline=False
        )
        roles = [role.mention for role in user.roles[1:]]
        roles.reverse()
        roles = ", ".join(roles)
        embed.add_field(
            name="Roles",
            value=f"{roles}", inline=False
        )
        embed.set_thumbnail(url=user.display_avatar)
        await interaction.reply(embed=embed, mention_author=False)


    @commands.command(name="serverinfo", aliases=["si"])
    async def command_serverinfo(self, interaction : Interaction):
        """Information about the server"""
        await interaction.trigger_typing()

        embed = nextcord.Embed(
            description=f"{interaction.guild.name} ({interaction.guild.id})", color=embed_color
        )
        embed.set_author(
            name=interaction.guild.name, icon_url=interaction.guild.icon
        )

        embed.add_field(
            name="Basic Information",
            value=f"**Created:** {format_dt(interaction.guild.created_at, style='R')}\n"
                  f"**Owner:** {interaction.guild.owner.mention}\n"
                  f"**Members:** {interaction.guild.member_count}\n"
                  f"**Channels:** {len(interaction.guild.channels)}\n"
                  f"**Roles:** {len(interaction.guild.roles)}\n"
                  f"**Emojis:** {len(interaction.guild.emojis)}\n"
                  f"**Boosts:** {interaction.guild.premium_subscription_count}\n"
                  f"**Boost Level:** {interaction.guild.premium_tier}", inline=False
        )
        embed.set_thumbnail(url=interaction.guild.icon)

        await interaction.reply(embed=embed, mention_author=False)


    @commands.command(name="avatar", aliases=["av"])
    async def command_avatar(self, interaction : Interaction, user : nextcord.Member = None):
        """Get a user's avatar"""
        await interaction.trigger_typing()

        user = user or interaction.author

        embed = nextcord.Embed(
            title=f"{user.name}'s avatar", color=embed_color
        )
        embed.set_image(url=user.display_avatar)

        await interaction.reply(embed=embed, mention_author=False)

    
    @commands.command(name="roleinfo", aliases=["ri"])
    async def command_roleinfo(self, interaction : Interaction, role : nextcord.Role):
        """Information about a role"""
        await interaction.trigger_typing()

        embed = nextcord.Embed(
            title=f"Information about {role.name}", color=embed_color
        )
        embed.add_field(
            name="Basic Information",
            value=f"**Name:** {role.mention}\n"
                  f"**ID:** {role.id}\n"
                  f"**Created:** {format_dt(role.created_at, style='R')}\n"
                  f"**Color:** {role.color}\n"
                  f"**Position:** {role.position}\n"
                  f"**Mentionable:** {role.mentionable}\n", inline=False
        )
        embed.set_thumbnail(url=interaction.guild.icon)
        await interaction.reply(embed=embed, mention_author=False)


    @commands.command(name="channelinfo", aliases=["ci"])
    async def command_channelinfo(self, interaction : Interaction, channel : nextcord.TextChannel = None):
        """Information about a channel"""
        await interaction.trigger_typing()

        channel = channel or interaction.channel

        embed = nextcord.Embed(
            title=f"Information about {channel.name}", color=embed_color
        )
        embed.add_field(
            name="Basic Information",
            value=f"**Name:** {channel.mention}\n"
                  f"**ID:** {channel.id}\n"
                  f"**Created:** {format_dt(channel.created_at, style='R')}\n"
                  f"**Category:** {channel.category}\n"
                  f"**Position:** {channel.position}\n"
                  f"**NSFW:** {channel.is_nsfw()}\n", inline=False
        )
        embed.set_thumbnail(url=interaction.guild.icon)
        await interaction.reply(embed=embed, mention_author=False)

def setup(bot):
    bot.add_cog(Utility(bot))