import contextlib
import logging
import re
import traceback
from typing import Iterable, Mapping, Sequence

from aiohttp import ClientSession
from cachetools import LRUCache
from discord import (
    AllowedMentions,
    AsyncWebhookAdapter,
    Color,
    Embed,
    Forbidden,
    Guild,
    Intents,
    Message,
    NotFound,
    TextChannel,
    Webhook,
    utils,
)
from discord.ext import commands, tasks
from discord.http import HTTPClient
from tortoise import Tortoise

from models import GuildModel

from .utils.error_logging import error_to_embed

logging.basicConfig(level=logging.INFO)


class ItsnpBot(commands.Bot):
    http: HTTPClient

    def __init__(
        self,
        *,
        command_prefix: str,
        description: str,
        developement_environment: bool,
        log_webhook_url: str,
        tortoise_config: dict,
        load_extensions: bool = True,
        extensions: Sequence = (),
        loadjsk: bool = True,
        ignore_dms: bool = True,
        respond_to_ping: bool = True,
    ):
        allowed_mentions = AllowedMentions(
            users=True, replied_user=True, roles=False, everyone=False
        )
        super().__init__(
            command_prefix=self.get_custom_prefix,
            intents=Intents.all(),
            allowed_mentions=allowed_mentions,
            description=description,
            strip_after_prefix=True,
        )
        self.developement_environment = developement_environment
        self.prefix = command_prefix
        self.ignore_dms = ignore_dms
        self.respond_to_ping = respond_to_ping
        self.tortoise_config = tortoise_config
        self.log_webhook_url = log_webhook_url

        # Cache
        self.prefix_cache: Mapping[Guild.id, str] = LRUCache(1000)

        # Start connecting to DB
        self.connect_db.start()

        # Loading extensions
        if load_extensions:
            self.load_extensions(extensions)
        if loadjsk:
            self.load_extension("jishaku")

    # Properties
    @property
    def session(self) -> ClientSession:
        return self.http._HTTPClient__session

    @property
    def log_webhook(self) -> Webhook:
        return Webhook.from_url(
            self.log_webhook_url, adapter=AsyncWebhookAdapter(self.session)
        )

    # Connect to DB
    @tasks.loop(seconds=0, count=1)
    async def connect_db(self):
        logging.info("Connecting to db")
        await Tortoise.init(self.tortoise_config)
        logging.info("Database connected")

        # Auto cog reload
        if self.developement_environment:
            from .utils.autoreloader import AutoReloader

            reloader = AutoReloader(self)
            reloader.cog_watcher_task.start()

    # Util methods
    def load_extensions(self, extentions: Iterable[str]):
        for ext in extentions:
            try:
                logging.info(f"Loaded {ext}")
                self.load_extension(ext)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)

    # Getting Prefixes
    async def get_custom_prefix(self, bot: commands.Bot, message: Message) -> str:
        prefix: str = await self.determine_prefix(None, message)
        return commands.when_mentioned_or(prefix)(bot, message)

    async def determine_prefix(self, _, message: Message) -> str:
        # DMs/Group
        if not message.guild:
            return self.prefix

        # Get from cache
        guild_id = message.guild.id
        if guild_id in self.prefix_cache:
            return self.prefix_cache[guild_id]

        # Fetch from db
        guild = await GuildModel.from_guild_object(message.guild)
        self.prefix_cache[guild_id] = guild.prefix
        return guild.prefix

    def run(self, bot_token: int) -> None:
        return super().run(bot_token, bot=True, reconnect=True)

    # Listeners
    async def on_ready(self):
        logging.info(f"Logged in with {self.user.name}#{self.user.discriminator}")

    async def on_message(self, msg: Message):
        # Don't respond to any bots
        if msg.author.bot:
            return

        # Check whether to ignore DMs for everyone other than owner
        if self.ignore_dms and not msg.guild and not await self.is_owner(msg.author):
            return

        # Don't try to respond when the bot has no send perms
        if (
            msg.guild
            and msg.guild.me
            and not msg.channel.permissions_for(msg.guild.me).send_messages
        ):
            return

        # Respond with prefix on ping
        if self.respond_to_ping and f"<@!{self.user.id}>" == msg.content.strip():
            return await msg.reply(
                "My prefix here is `{}`".format(await self.determine_prefix(None, msg))
            )

        # Process commands
        await self.process_commands(msg)

    # Error listeners
    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        embeds = error_to_embed()
        context_embed = Embed(
            title="Context", description=f"**Event**: {event_method}", color=Color.red()
        )
        await self.log_webhook.send(embeds=[*embeds, context_embed])

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if self.developement_environment:
            return traceback.print_exception(type(error), error, error.__traceback__)

        if isinstance(error, commands.CommandNotFound):
            return
        if not isinstance(error, commands.CommandInvokeError):
            title = " ".join(
                re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__)
            )
            return await ctx.send(
                embed=Embed(title=title, description=str(error), color=Color.red())
            )

        # If we've reached here, the error wasn't expected
        # Report to logs
        embed = Embed(
            title="Error",
            description="An unknown error has occurred and my developer has been notified of it.",
            color=Color.red(),
        )
        with contextlib.suppress(NotFound, Forbidden):
            await ctx.send(embed=embed)

        traceback_embeds = error_to_embed(error)

        # Add message content
        info_embed = Embed(
            title="Message content",
            description="```\n" + utils.escape_markdown(ctx.message.content) + "\n```",
            color=Color.red(),
        )
        # Guild information
        value = (
            (
                "**Name**: {0.name}\n"
                "**ID**: {0.id}\n"
                "**Created**: {0.created_at}\n"
                "**Joined**: {0.me.joined_at}\n"
                "**Member count**: {0.member_count}\n"
                "**Permission integer**: {0.me.guild_permissions.value}"
            ).format(ctx.guild)
            if ctx.guild
            else "None"
        )

        info_embed.add_field(name="Guild", value=value)
        # Channel information
        if isinstance(ctx.channel, TextChannel):
            value = (
                "**Type**: TextChannel\n"
                "**Name**: {0.name}\n"
                "**ID**: {0.id}\n"
                "**Created**: {0.created_at}\n"
                "**Permission integer**: {1}\n"
            ).format(ctx.channel, ctx.channel.permissions_for(ctx.guild.me).value)
        else:
            value = (
                "**Type**: DM\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
            ).format(ctx.channel)

        info_embed.add_field(name="Channel", value=value)

        # User info
        value = (
            "**Name**: {0}\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
        ).format(ctx.author)

        info_embed.add_field(name="User", value=value)

        await self.log_webhook.send(
            content="---------------\n\n**NEW ERROR**\n\n---------------",
            embeds=[*traceback_embeds, info_embed],
        )
