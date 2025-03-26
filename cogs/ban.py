import discord
from discord import app_commands
from discord.ext import commands

from services.database import DatabaseService


class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        row = await DatabaseService.pool.fetchrow(
            "SELECT * FROM punishes WHERE id = $1", member.id
        )
        if row:
            await member.kick(
                reason=f'neko\'s Global Ban Bot によりBANされているため: {row["reason"]}'
            )
            await member.send(
                embed=discord.Embed(
                    title="あなたは neko's Global Ban Bot により**グローバルBAN**されています。",
                    description="-# 異議申し立ては https://discord.gg/rQZ3g6aCqW までどうぞ。",
                    colour=discord.Colour.red(),
                ).add_field(name="理由", value=row["reason"]),
                ephemeral=True,
            )
            return

    @app_commands.command(
        name="update", description="サーバーにいるBAN対象者を全員退出させます。"
    )
    async def updateCommand(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="現在処理中です...",
                colour=discord.Colour.green(),
            ),
            ephemeral=True,
        )
        rows = await DatabaseService.pool.fetch("SELECT * FROM punishes")
        for row in rows:
            member = interaction.guild.get_member(row["id"])
            if member is not None:
                await member.kick(
                    reason=f'neko\'s Global Ban Bot によりBANされているため: {row["reason"]}'
                )
                await member.send(
                    embed=discord.Embed(
                        title="あなたは neko's Global Ban Bot により**グローバルBAN**されています。",
                        description="-# 異議申し立ては https://discord.gg/rQZ3g6aCqW までどうぞ。",
                        colour=discord.Colour.red(),
                    ).add_field(name="理由", value=row["reason"]),
                )
        await interaction.edit_original_response(
            embed=discord.Embed(
                title=":white_check_mark: 処理が完了しました。",
                colour=discord.Colour.green(),
            ),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))
