import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import fnmatch
from utils.config import prefix


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
        await self.change_presence(
            status=nextcord.Status.dnd, activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=f"{len(list(self.get_all_members()))} Users")
        )

intents = nextcord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.presences = True
mentions = nextcord.AllowedMentions(everyone=False, users=True, roles=False)

bot = Bot(command_prefix=prefix, intents=intents, allowed_mentions=mentions, case_insensitive=True)


if __name__ == '__main__':
    disabled_cogs = []

    folder = "./cogs"
    ending = "*.py"

    for path, subdirs, files in os.walk(folder):
        for name in files:
            if fnmatch.fnmatch(name, ending):  # Checks if the file is a Python file
                paths = os.path.join(path, name)[2:][:-3]  # Formats the path to the file to be able to load it
                path_f = paths.replace("/", ".")
                if not path_f.split(".")[-1] in disabled_cogs:  # Checks if the cog is disabled
                    try:
                        bot.load_extension(path_f)
                        print(f"Loaded {path_f}")
                    except commands.errors.NoEntryPointError:  # Checks if the cog has a setup function
                        pass

load_dotenv()
bot.run(os.getenv('TOKEN'), reconnect=True)
