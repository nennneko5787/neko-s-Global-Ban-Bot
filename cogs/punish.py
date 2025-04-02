import traceback

import discord
from discord.ext import commands

from services.database import DatabaseService


class PunishModal(discord.ui.Modal, title="処罰"):
    def __init__(self, user: discord.User):
        super().__init__()
        self.user = user
        self.reason = discord.ui.TextInput(
            label=f"{user.name} をグローバルBANする理由",
            placeholder="具体的に書いてください。",
            style=discord.TextStyle.long,
            required=True,
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        await DatabaseService.pool.execute(
            """
                INSERT INTO punishes (id, reason) VALUES ($1, $2)
            """,
            self.user.id,
            self.reason.value,
        )

        await interaction.followup.send("punished.")


class PunishCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command
    async def pardon(self, ctx: commands.Context, userId: int):
        try:
            await DatabaseService.pool.execute(
                """
                    DELETE FROM punishes WHERE id = $1
                """,
                userId,
            )
            await ctx.reply("OK, pardoned")
        except:
            await ctx.reply(f"```py\n{traceback.format_exc()}```\n")

    async def punish(self, interaction: discord.Interaction, customFields: list[str]):
        await interaction.response.send_modal(
            PunishModal(await self.bot.fetch_user(int(customFields[1])))
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try:
            if interaction.data["component_type"] == 2:
                customId = interaction.data["custom_id"]
                customFields = customId.split("|")
                if customFields[0] == "globalban":
                    await self.punish(interaction, customFields)
        except KeyError:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(PunishCog(bot))
