from discord import Color, Embed
from discord.ext import Cog, commands

from itsnp.bot import ItsnpBot


class Core(Cog):
    def __init__(self, bot: ItsnpBot):
        self.bot = bot

    @commands.command(aliases=["latency"])
    async def ping(self, ctx: commands.Context):
        """Check latency of the bot"""
        latency = str(round(self.bot.latency * 1000, 1))
        await ctx.send(
            embed=Embed(title="Pong!", description=f"{latency}ms", color=Color.blue())
        )


def setup(bot: ItsnpBot):
    bot.add_cog(Core(bot))
