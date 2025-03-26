import asyncio
import os

import discord
import dotenv
from discord.ext import commands

from services.database import DatabaseService

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.members = True


class Bot(commands.Bot):
    async def close(self):
        async with asyncio.timeout(10):
            await DatabaseService.pool.close()
        await super().close()


bot = Bot("punish!", help_command=None, intents=intents)


@bot.event
async def setup_hook():
    await DatabaseService.connect()
    await bot.load_extension("cogs.report")
    await bot.load_extension("cogs.punish")
    await bot.load_extension("cogs.ban")
    await bot.tree.sync()


bot.run(os.getenv("discord"))
