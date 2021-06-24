from itsnp.bot import ItsnpBot
from discord import Color, Embed
from discord.ext import commands


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

def setup(bot: ItsnpBot):
    bot.add_cog(Core(bot))