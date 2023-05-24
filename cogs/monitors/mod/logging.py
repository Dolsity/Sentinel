import aiohttp
import nextcord
from nextcord.ext import commands
from nextcord.utils import format_dt
from datetime import datetime
from io import BytesIO
from typing import List, Union
from utils.config import logging_channel, main_guild, embed_color
from utils.database import warnings, blacklist
from PIL import Image, ImageFont, ImageDraw


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member) -> None:

        if member.guild.id != main_guild:
            return
    
        channel = member.guild.get_channel(logging_channel)

        embed = nextcord.Embed(title="Member joined")
        embed.description=""
        embed.color = embed_color

        await member.add_roles(member.guild.get_role(891573857255829515)) # Member role

        if warnings.find_one({"_id": member.id}):
            count = len(warnings.find_one({"_id": member.id}).get('reason', []))
            embed.description+=f"**{member.display_name} has {count} warnings.**"
            embed.color = nextcord.Color.orange()

        if blacklist.find_one({"_id": member.id}):
            await member.add_roles(member.guild.get_role(1110810158105374750)) # Blacklist role
            embed.description+=f"\n**{member.display_name} is blacklisted.**"
            embed.color = nextcord.Color.red()

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field( name="User", value=f'{member} ({member.mention})', inline=True)
        embed.add_field(name="Joined Server", value=f"{format_dt(member.joined_at, style='R')}", inline=True)
        embed.add_field(name="Joined Discord", value=f"{format_dt(member.created_at, style='R')}", inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=member.id)
        await channel.send(embed=embed)

        image = Image.new("RGB", (800, 450), color="#8b7af4")
        name_text_font = ImageFont.truetype("assets/fonts/RedHatText-MediumItalic.otf", 40)
        guild_text_font = ImageFont.truetype("assets/fonts/RedHatText-MediumItalic.otf", 25)
        draw = ImageDraw.Draw(image)

        background_image = Image.new("RGBA", (750, 400), color="#6859c9")
        image.paste(background_image, (25, 25))

        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.display_avatar)) as response:
                avatar_bytes = await response.read()

        avatar_image = Image.open(BytesIO(avatar_bytes)).convert("RGBA").resize((200, 200))
        avatar_image = avatar_image.resize((200, 200))
        avatar_mask = Image.new("L", avatar_image.size, 0)
        draw_avatar_mask = ImageDraw.Draw(avatar_mask)
        draw_avatar_mask.ellipse((0, 0) + avatar_image.size, fill=255)
        avatar_image.putalpha(avatar_mask)
        image.paste(avatar_image, (300, 70), avatar_image)

        if len(member.display_name) > 10:
            member.display_name = member.display_name[:10] + "..."
        if len(member.guild.name) > 13:
            member.guild.name = member.guild.name[:13] + "..."
        name_text = f"Welcome {member.display_name} to {member.guild.name}"
        guild_text = f"You are member #{len(member.guild.members)}"
        name_text_width, name_text_height = draw.textsize(name_text, font=name_text_font)
        guild_text_width, guild_text_height = draw.textsize(guild_text, font=guild_text_font)
        draw.text(((800 - name_text_width) / 2, (650 - name_text_height) / 2), name_text, font=name_text_font, fill="#ffffff")
        draw.text(((800 - guild_text_width) / 2, (740 - guild_text_height) / 2), guild_text, font=guild_text_font, fill="#ffffff")

        with BytesIO() as image_binary:
            image.save(image_binary, format='PNG')
            image_binary.seek(0)

            file = nextcord.File(fp=image_binary, filename="card.png")

        channel = member.guild.get_channel(1110823809587617833)
        await channel.send(f"👋 Welcome, {member.mention}.\n", file=file)


    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member) -> None:
        if member.guild.id != main_guild:
            return

        channel = member.guild.get_channel(logging_channel)

        async for action in member.guild.audit_logs(limit=1, action=nextcord.AuditLogAction.kick):
            if action.target.id == member.id:
                await self.on_member_kick(action, channel)
                return

        embed = nextcord.Embed(title="Member Left")
        embed.color = embed_color
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="User", value=f'{member} ({member.mention})', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=member.id)
        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message) -> None:

        if not before.guild:
            return
        if before.guild.id != main_guild:
            return
        if not before.content or not after.content or before.content == after.content:
            return

        channel = before.guild.get_channel(logging_channel)

        embed = nextcord.Embed(title="Message Updated")
        embed.color = nextcord.Color.orange()
        embed.set_thumbnail(url=before.author.display_avatar)
        embed.add_field(name="User", value=f'{before.author} ({before.author.mention})', inline=False)

        before_content = before.content
        if len(before.content) > 400:
            before_content = before_content[0:400] + "..."

        after_content = after.content
        if len(after.content) > 400:
            after_content = after_content[0:400] + "..."

        embed.add_field(name="Old message", value=before_content, inline=False)
        embed.add_field(name="New message", value=after_content, inline=False)
        embed.add_field(name="Channel", value=before.channel.mention + f"\n\n[Link to message]({before.jump_url})", inline=False)
        embed.timestamp = datetime.now()
        embed.set_footer(text=before.author.id)
        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: nextcord.RawMessageDeleteEvent) -> None:
        message = payload.cached_message

        if not message or not message.guild:
            return
        if message.guild.id != main_guild:
            return
        if message.author.bot:
            return
        if message.content == "" or not message.content:
            return

        channel = message.guild.get_channel(logging_channel)

        embed = nextcord.Embed(title="Message Deleted")
        embed.color = nextcord.Color.red()
        embed.set_thumbnail(url=message.author.display_avatar)
        embed.add_field(name="User", value=f'{message.author} ({message.author.mention})', inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        content = message.content
        async for action in message.guild.audit_logs(limit=1, action=nextcord.AuditLogAction.message_delete):
            if action.target.id == message.author.id:
                embed.add_field(name="Deleted by", value=f'{action.user} ({action.user.mention})', inline=True)

        if len(message.content) > 400:
            content = content[0:400] + "..."
        embed.add_field(name="Message", value=content, inline=False)

        embed.set_footer(text=message.author.id)
        embed.timestamp = datetime.now()
        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: List[nextcord.Message]):
        if not messages[0].guild:
            return
        if messages[0].guild.id != main_guild:
            return

        members = set()

        channel = messages[0].guild.get_channel(logging_channel)
        output = BytesIO()
        for message in messages:
            members.add(message.author)

            string = f'{message.author} ({message.author.id}) [{message.created_at.strftime("%B %d, %Y, %I:%M %p")}]) UTC\n'
            string += message.content
            for attachment in message.attachments:
                string += f'\n{attachment.url}'

            string += "\n\n"
            output.write(string.encode('UTF-8'))
        output.seek(0)

        member_string = ""
        for i, member in enumerate(members):
            if i == len(members) - 1 and i == 0:
                member_string += f"{member.mention}"
            elif i == len(members) - 1 and i != 0:
                member_string += f"and {member.mention}"
            else:
                member_string += f"{member.mention}, "

        embed = nextcord.Embed(title="Bulk Message Deleted")
        embed.color = nextcord.Color.red()
        embed.add_field(name="Users", value=f'This batch included {len(messages)} messages from {member_string}', inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.timestamp = datetime.now()
        await channel.send(embed=embed)
        await channel.send(file=nextcord.File(output, 'message.txt'))


    @commands.Cog.listener()
    async def on_user_update(self, before: nextcord.User, after: nextcord.User):
        if before.name == after.name and before.discriminator == after.discriminator:
            return

        guild = self.bot.get_guild(main_guild)
        channel = guild.get_channel(logging_channel)

        embed = nextcord.Embed(title="Username Updated")
        embed.color = nextcord.Color.magenta()
        embed.add_field(name="Before", value=f'{before} ({before.mention})', inline=True)
        embed.add_field(name="After", value=f'{after} ({after.mention})', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=before.id)
        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        if after.guild.id != main_guild:
            return
        if not before or not after:
            return
        if before.display_name != after.display_name:
            await self.member_nick_update(before, after)
            return
        if before.display_avatar != after.display_avatar:
            await self.member_avatar_update(before, after)
            return
        if before._timeout != after._timeout:
            await self.member_timeout_update(before, after)
            return

        new_roles = [role.mention for role in after.roles if role not in before.roles]
        if new_roles:
            await self.member_roles_update(member=after, roles=new_roles, added=True)
            return

        removed_roles = [role.mention for role in before.roles if role not in after.roles]
        if removed_roles:
            await self.member_roles_update(member=after, roles=removed_roles, added=False)
            return

    async def member_nick_update(self, before, after):
        embed = nextcord.Embed(title="Member Renamed")
        embed.color = nextcord.Color.orange()
        embed.set_thumbnail(url=after.display_avatar)
        embed.add_field(name="Member", value=f'{after} ({after.mention})', inline=False)
        embed.add_field(name="Old nickname", value=f'{before.display_name}', inline=True)
        embed.add_field(name="New nickname", value=f'{after.display_name}', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=after.id)

        private = after.guild.get_channel(logging_channel)
        if private:
            await private.send(embed=embed)

    async def member_avatar_update(self, before, after):
        embed = nextcord.Embed(title="Member Avatar Updated")
        embed.color = nextcord.Color.orange()
        embed.set_thumbnail(url=after.display_avatar)
        embed.add_field(name="Member", value=f'{after} ({after.mention})', inline=False)
        embed.timestamp = datetime.now()
        embed.set_footer(text=after.id)

        private = after.guild.get_channel(logging_channel)
        if private:
            await private.send(embed=embed)

    async def member_roles_update(self, member, roles, added):
        embed = nextcord.Embed()
        if added:
            embed.title = "Member Role Added"
            embed.color = nextcord.Color.blue()
        else:
            embed.title = "Member Role Removed"
            embed.color = nextcord.Color.red()

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Member", value=f'{member} ({member.mention})', inline=True)
        embed.add_field(name="Role difference", value=', '.join(roles), inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=member.id)

        async for action in member.guild.audit_logs(limit=1, action=nextcord.AuditLogAction.member_role_update):
            # Check if bot gave user role, if so return
            if action.user.id == self.bot.user.id:
                return
            if action.target.id == member.id:
                embed.add_field(name="Updated by", value=f'{action.user} ({action.user.mention})', inline=False)

        private = member.guild.get_channel(logging_channel)
        if private:
            await private.send(embed=embed)

    async def member_timeout_update(self, before: nextcord.Member, after: nextcord.Member):
        embed = nextcord.Embed()
        if before._timeout is not None and after._timeout is None:
            embed.title = "Member Timeout Removed"
            embed.color = nextcord.Color.dark_blue()
        elif (before._timeout is None and after._timeout is not None) or (before._timeout < after._timeout):
            embed.title = "Member Timed Out"
            embed.color = nextcord.Color.greyple()
        else:
            embed.title = "Member Timeout Removed"
            embed.color = nextcord.Color.dark_blue()

        member = after
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Member", value=f'{member} ({member.mention})', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=member.id)
        private = member.guild.get_channel(logging_channel)
        if private:
            await private.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_ban(self, guild, user: Union[nextcord.User, nextcord.Member]):
        if not guild.id == main_guild:
            return

        channel = guild.get_channel(logging_channel)

        embed = nextcord.Embed(title="Member Banned")
        embed.color = nextcord.Color.red()
        embed.add_field(name="User", value=f'{user} ({user.mention})', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=user.id)

        async for action in guild.audit_logs(limit=1, action=nextcord.AuditLogAction.ban):
            if action.target.id == user.id:
                embed.title = "Member Left"
                embed.color = nextcord.Color.purple()
                embed.add_field(
                    name="Banned by", value=f'{action.user} ({action.user.mention})', inline=True)
                await channel.send(embed=embed)
                return

        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_unban(self, guild, user: nextcord.User):
        if not guild.id == main_guild:
            return

        channel = guild.get_channel(logging_channel)

        embed = nextcord.Embed(title="User Unbanned")
        embed.color = nextcord.Color.yellow()
        embed.add_field(
            name="User", value=f'{user} ({user.mention})', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=user.id)

        async for action in guild.audit_logs(limit=1, action=nextcord.AuditLogAction.unban):
            if action.target.id == user.id:
                embed.add_field(name="Unbanned by", value=f'{action.user} ({action.user.mention})', inline=True)
                await channel.send(embed=embed)
                return

        await channel.send(embed=embed)

    async def on_member_kick(self, action: nextcord.AuditLogEntry, channel: nextcord.TextChannel):
        embed = nextcord.Embed(title="Member Left")
        embed.color = nextcord.Color.purple()
        embed.add_field(name="User", value=f'{action.target} ({action.target.mention})', inline=True)
        embed.add_field(name="Kicked by", value=f'{action.user} ({action.user.mention})', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=action.user.id)
        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
        if member.guild.id != main_guild:
            return

        embed = nextcord.Embed()
        embed.color = nextcord.Color.dark_blue()
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Member", value=f'{member} ({member.mention})', inline=False)

        if before.channel is None and member in after.channel.members:
            embed.title = "Member VC Joined"
            embed.add_field(name="Joined", value=after.channel.mention, inline=True)
        elif before.channel is not None and after.channel is None:
            embed.title = "Member VC Left"
            embed.add_field(name="Left", value=before.channel.mention, inline=True)
        elif before.channel.id != after.channel.id:
            embed.title = "Member VC Moved"
            embed.add_field(name="Left", value=before.channel.mention, inline=True)
            embed.add_field(name="Joined", value=after.channel.mention, inline=True)
        else:
            return

        embed.timestamp = datetime.now()
        embed.set_footer(text=member.id)

        private = member.guild.get_channel(logging_channel)
        if private:
            await private.send(embed=embed)


    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.guild is None or interaction.guild.id != main_guild:
            return
        if interaction.type != nextcord.InteractionType.application_command:
            return
        data = interaction.data
        if data.get("type") != 1:
            return

        options = interaction.data.get("options") or []

        message_content = ""
        for option in options:
            if option.get("type") == 1:
                message_content += f"{option.get('name')} "
                for sub_option in option.get("options"):
                    message_content += f"{sub_option.get('name')}: {sub_option.get('value')} "
            else:
                message_content += f"{option.get('name')}: {option.get('value')} "

        private = interaction.guild.get_channel(logging_channel)

        embed = nextcord.Embed(title="Member Used Command",color=nextcord.Color.dark_teal())
        embed.set_thumbnail(url=interaction.user.display_avatar)
        embed.add_field(
            name="Member", value=f'{interaction.user} ({interaction.user.mention})', inline=True)
        if interaction.channel is not None:
            embed.add_field(name="Channel", value=interaction.channel.mention, inline=True)
        embed.add_field(
            name="Command", value=f'`/{data.get("name")}{" " + message_content.strip() if message_content else ""}`', inline=False)
        embed.timestamp = datetime.now()
        embed.set_footer(text=interaction.user.id)

        if private is not None:
            await private.send(embed=embed)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return


def setup(bot):
    bot.add_cog(Logging(bot))
