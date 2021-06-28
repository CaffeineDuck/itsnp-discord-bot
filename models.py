from discord import Guild
from discord.ext.commands import Context
from tortoise import Model, fields

from config.bot import bot_config


class GuildModel(Model):
    id = fields.BigIntField(pk=True, description="Discord ID of the guild")
    prefix = fields.CharField(
        max_length=10,
        default=bot_config.prefix,
        description="Custom prefix of the guild",
    )
    name = fields.TextField(description="Name of the guild")

    @classmethod
    async def from_guild_object(cls, guild: Guild):
        return (await cls.get_or_create(id=guild.id, name=guild.name))[0]

    @classmethod
    async def from_context(cls, ctx: Context):
        return await cls.from_guild_object(ctx.guild)

    class Meta:
        table = "guilds"
        table_description = "Represents a discord guild's settings"
