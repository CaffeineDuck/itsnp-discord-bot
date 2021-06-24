import os
import traceback

import watchgod
from discord.ext import commands, tasks

from itsnp.bot import ItsnpBot


class AutoReloader:
    def __init__(self, bot: ItsnpBot):
        self.bot = bot

    @tasks.loop(seconds=1)
    async def cog_watcher_task(self) -> None:
        """Watches the cogs directory for changes and reloads files"""
        async for change in watchgod.awatch(
            "itsnp/cogs", watcher_cls=watchgod.PythonWatcher
        ):
            for change_type, changed_file_path in change:
                try:
                    extension_name = changed_file_path.replace(os.path.sep, ".")[:-3]
                    if len(extension_name) > 36 and extension_name[-33] == ".":
                        continue
                    if change_type == watchgod.Change.modified:
                        try:
                            self.bot.unload_extension(extension_name)
                        except commands.ExtensionNotLoaded:
                            pass
                        finally:
                            self.bot.load_extension(extension_name)
                            print(f"AutoReloaded {extension_name}.")
                    else:
                        try:
                            self.bot.unload_extension(extension_name)
                            print(f"AutoUnloaded {extension_name}.")
                        except commands.ExtensionNotLoaded:
                            pass
                except (commands.ExtensionFailed, commands.NoEntryPointError) as e:
                    traceback.print_exception(type(e), e, e.__traceback__)
