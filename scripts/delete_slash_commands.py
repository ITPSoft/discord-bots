import os

import disnake
from disnake.ext import commands
from dotenv import load_dotenv

from common.constants import Server

load_dotenv()

intents = disnake.Intents.default()
bot = commands.InteractionBot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Delete all global commands
    global_commands = await bot.fetch_global_commands()
    for cmd in global_commands:
        await bot.delete_global_command(cmd.id)
        print(f"Deleted global command: {cmd.name}")
    guild_commands = await bot.fetch_guild_commands(Server.KOUZELNICI)
    for cmd in guild_commands:
        await bot.delete_guild_command(Server.KOUZELNICI, cmd.id)
        print(f"Deleted guild command: {cmd.name}")

    print("All global and guild commands deleted.")


bot.run(os.getenv("DECIM_DISCORD_TOKEN"))
