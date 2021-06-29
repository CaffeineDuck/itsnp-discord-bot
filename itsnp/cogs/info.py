import random

import discord
from discord import member
from discord.ext import commands

from itsnp.bot import ItsnpBot


class Info(commands.Cog):
    def __init__(self, bot: ItsnpBot) -> None:
        self.bot = bot

    @commands.command()
    async def serverinfo(self, ctx: commands.Context):
        """Embed Information of server"""

        # find_bots = sum(1 for member in ctx.guild.members if member.bot
        bots = len([member for member in ctx.guild.members if member.bot])
        embed = discord.Embed(
            title=f"Server Information of  **{ctx.guild.name}**",
            color=discord.Color(random.randint(0, 0xFFFFFF)),
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon_url)
        if ctx.guild.banner:
            embed.set_image(url=ctx.guild.banner_url_as(format="png"))

        embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
        embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
        embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="Bots", value=bots, inline=True)
        embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
        embed.add_field(name="Region", value=ctx.guild.region, inline=True)
        embed.add_field(name="Created", value=ctx.guild.created_at, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx: commands.Context, user: discord.Member = None):
        """Embeds Tagged user's info"""
        user = user or ctx.author

        show_roles = (
            ", ".join(
                [
                    role.mention
                    for role in sorted(
                        user.roles, key=lambda role: role.position, reverse=True
                    )
                    if role.id != ctx.guild.default_role.id
                ]
            )
            if len(user.roles) > 1
            else "None"
        )

        embed = discord.Embed(
            title=f"Some Info about {user.display_name}",
            colour=0x2ECC71,
        )
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="Full name", value=user, inline=True)
        embed.add_field(
            name="Nickname",
            value=user.nick if hasattr(user, "nick") else "None",
            inline=True,
        )
        embed.add_field(name="Account created on", value=user.created_at, inline=True)
        embed.add_field(name="Joined this server", value=user.joined_at, inline=True)
        embed.add_field(name="Roles", value=show_roles, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def mods(self, ctx: commands.Context):
        """Show the list of online Mods And Admins"""
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "<:IDLE:858009713644142602>"},
            "dnd": {"users": [], "emoji": "<:DND:858009229624213555>"},
            "offline": {"users": [], "emoji": "⚫"},
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += (
                    f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"
                )

        await ctx.send(f"**Active Mods & Admin In: {ctx.guild.name}**\n{message}")

    @commands.command()
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Embed  mentioned user avatar"""
        if not member:
            member = ctx.message.author

        usrav = member.avatar_url
        usrname = member.display_name
        embed = discord.Embed(
            title=f"{usrname}'s Avatar",
            color=discord.Color(random.randint(0, 0xFFFFFF)),
        )
        embed.set_image(url=usrav)
        await ctx.send(embed=embed)

    @commands.command()
    async def links(self, ctx: commands.Context):
        """Sends Social Media Links Of Itsnp"""
        platform = discord.Embed(
            title="**You can Find Us at-**",
            description="""
        [Facebook Group](http://tiny.cc/itsnpgroup)
        [Instagram](http://tiny.cc/itsnpig)
        [Youtube](http://tiny.cc/itsnpyt )
        [Discord Server](http://tiny.cc/itsnpdiscord)
        [Twitter](http://tiny.cc/itsnptwitter)
         """,
            color=0x2ECC71,
        )
        platform.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=platform)


def setup(bot: ItsnpBot):
    bot.add_cog(Info(bot))
