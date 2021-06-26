from models import GuildModel
from discord import Color, Embed, NotFound
from discord.ext import commands

from itsnp.bot import ItsnpBot

class MessageNotRefrenced(commands.CommandError):
    def __str__(self):
        return "Please reply to the valid message you want to re-run!"

class Core(commands.Cog):
    def __init__(self, bot: ItsnpBot):
        self.bot = bot

    @commands.command(aliases=["latency"])
    async def ping(self, ctx: commands.Context):
        """Check latency of the bot"""
        latency = str(round(self.bot.latency * 1000, 1))
        await ctx.reply(
            embed=Embed(title="Pong!", description=f"{latency}ms", color=Color.blue())
        )

    @commands.command(name="changeprefix")
    async def change_prefix(self, ctx: commands.Context, prefix: str):
        """Change the prefix of the bot for that server"""
        model, _ = await GuildModel.get_or_create(id=ctx.guild.id)
        model.prefix = prefix
        await model.save()

        self.bot.prefix_cache[ctx.guild.id] = prefix
        await ctx.reply(f"The new prefix for this guild is `{prefix}`")

    @commands.command(name="re", aliases=["redo"])
    async def redo_command(self, ctx: commands.Context):
        ref = ctx.message.reference
        if not ref:
            raise MessageNotRefrenced()
        try:
            message = await ctx.channel.fetch_message(ref.message_id)
        except NotFound:
            return await ctx.reply("Couldn't find that message")
        if message.author != ctx.author:
            return
        await self.bot.process_commands(message)


def setup(bot: ItsnpBot):
    bot.add_cog(Core(bot))
