import os

from itsnp import ItsnpBot

os.environ.setdefault("JISHAKU_HIDE", "1")
os.environ.setdefault("JISHAKU_RETAIN", "1")
os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")

if __name__ == "__main__":
    from config.bot import bot_config
    from config.conf import conf
    from tortoise_config import tortoise_config

    extensions = [
        "itsnp.cogs.core",
        "itsnp.cogs.info",
        "itsnp.cogs.music"
    ]

    bot = ItsnpBot(
        command_prefix=bot_config.prefix,
        developement_environment=bot_config.developement_environment,
        log_webhook_url=conf.log_webhook,
        tortoise_config=tortoise_config,
        description="Bot for ITSNP Discord Server",
        ignore_dms=False,
        loadjsk=True,
        load_extensions=True,
        respond_to_ping=True,
        extensions=extensions,
    )

    bot.run(bot_config.token)
