import nextcord
from nextcord.ext import commands
import os
from extensions import initial_extensions
from utils.config import prefix, main_guild, owner_id


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix


    async def process_commands(self, message):
        if not self.is_ready():
            await message.channel.send("I'm not ready to process commands yet. Please wait a few seconds.")
            return

        ctx = await self.get_context(message, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    
    async def on_ready(self):
        print(f"Logged in as {self.user.name} - {self.user.id}")
        await self.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=f"{self.prefix}help"))

intents = nextcord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.presences = True
mentions = nextcord.AllowedMentions(everyone=False, users=True, roles=False)

bot = Bot(command_prefix=prefix, intents=intents, allowed_mentions=mentions, case_insensitive=True)



if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


bot.run(os.getenv('TOKEN'), reconnect=True)