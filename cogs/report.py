import discord
from discord import app_commands
from discord.ext import commands

from services.database import DatabaseService


class ReportModal(discord.ui.Modal, title="通報"):
    def __init__(self, user: discord.User, *, message: discord.Message = None):
        super().__init__()
        self.user = user
        self.message = message
        self.reason = discord.ui.TextInput(
            label=f"{user.name} を通報する理由",
            placeholder="具体的に書いてください。",
            style=discord.TextStyle.long,
            required=True,
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        if await DatabaseService.pool.fetchrow(
            "SELECT * FROM punishes WHERE id = $1", self.user.id
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    title=":x: そのユーザーは既に処罰されています。",
                    description="サーバー管理者にこのボットの `/update` コマンドを実行するようにお願いしてください。",
                    colour=discord.Colour.red(),
                ),
                ephemeral=True,
            )
            return

        channel: discord.TextChannel = interaction.client.get_channel(
            1354290958208077925
        )

        embed = (
            discord.Embed(
                title="ユーザーが通報されました", colour=discord.Colour.blurple()
            )
            .set_author(
                name=interaction.user.name, icon_url=interaction.user.display_avatar
            )
            .set_thumbnail(url=self.user.display_avatar)
            .add_field(
                name="通報したユーザー",
                value=f"{interaction.user.mention} ( `{interaction.user.name}`, `{interaction.user.id}` )",
                inline=False,
            )
            .add_field(
                name="対象ユーザー",
                value=f"{self.user.mention} ( `{self.user.name}`, `{self.user.id}` )",
                inline=False,
            )
            .add_field(name="理由", value=self.reason.value, inline=False)
        )

        if self.message is not None:
            embed.add_field(
                name="メッセージ",
                value=f'{self.message.content}\n{"\n".join([attachment.proxy_url for attachment in self.message.attachments])}',
                inline=False,
            )

        view = discord.ui.View(timeout=None)
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Global BAN",
                emoji="🧑‍⚖️",
                custom_id=f"globalban|{self.user.id}",
            )
        )

        await channel.send(embed=embed, view=view)

        await interaction.followup.send(
            embed=discord.Embed(
                title=":white_check_mark: 通報に成功しました。",
                description="ご協力ありがとうございました。",
                colour=discord.Colour.green(),
            ),
            ephemeral=True,
        )


class ReportCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ctxReportUser = app_commands.ContextMenu(
            name="ユーザーを通報",
            callback=self.reportUserContextMenu,
        )
        self.bot.tree.add_command(self.ctxReportUser)

        self.ctxReportMessage = app_commands.ContextMenu(
            name="メッセージを通報",
            callback=self.reportMessageContextMenu,
        )
        self.bot.tree.add_command(self.ctxReportMessage)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(
            self.ctxReportUser.name, type=self.ctxReportUser.type
        )
        self.bot.tree.remove_command(
            self.ctxReportMessage.name, type=self.ctxReportMessage.type
        )

    async def reportUserContextMenu(
        self, interaction: discord.Interaction, user: discord.User
    ):
        await interaction.response.send_modal(ReportModal(user))

    async def reportMessageContextMenu(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.send_modal(
            ReportModal(message.author, message=message)
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ReportCog(bot))
