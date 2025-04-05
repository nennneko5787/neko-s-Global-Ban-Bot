import discord
from discord.ext import commands, tasks


class PresenceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.presenceLoop.before_loop(self.beforePresenceLoop)
        self.presenceLoop.start()

    async def beforePresenceLoop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=20)
    async def presenceLoop(self):
        await self.bot.change_presence(
            activity=discord.Game(f"{len(self.bot.guilds)} サーバー")
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(PresenceCog(bot))
