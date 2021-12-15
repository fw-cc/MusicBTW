import logging
import datetime
import os

from logging import handlers

from discord.ext import commands


class MusicBTW(commands.Bot):
    def __init__(self, command_prefix, description=None, **options) -> None:
        super().__init__(command_prefix, description=description, **options)
        self.start_datetime = datetime.datetime.now()
        self.logging_level = logging.DEBUG
        self.logger = self.__config_logging()
        self.logger.info(f"Command prefix: {command_prefix}")
        # Any other statup stuffs can go here

    async def on_ready(self):
        path, _, cogs = next(os.walk("./bot/modules/"))
        for cog in cogs:
            # This is kinda naughty, when config eventually gets added, would be a good idea
            # to make the bot only load what it's told to from configs.
            if "__" not in cog:
                sanitised_cog_name = f"{path}{cog}".lstrip("./").replace("/", ".").rstrip(".py")
                try:
                    self.logger.info(f"Loading {sanitised_cog_name}")
                    self.load_extension(sanitised_cog_name)
                except commands.ExtensionAlreadyLoaded:
                    self.logger.debug(f"{sanitised_cog_name} already loaded")
                except Exception as e:
                    self.logger.exception(e)
    
    def __config_logging(self, outdir="./logs"):
        logger = logging.getLogger("MusicBTW")
        logger.setLevel(self.logging_level)
        formatter = logging.Formatter('[{asctime}] [{levelname:}] {name}: {message}',
                                      '%Y-%m-%d %H:%M:%S', style='{')
        # file_log = handlers.RotatingFileHandler(f'{outdir}/{self.start_datetime.strftime("%Y%m%d_%H%M%S")}.log',
        #                                         encoding="utf-8", mode="a", backupCount=3, maxBytes=10000000)
        console_log = logging.StreamHandler()
        # file_log.setFormatter(formatter)
        console_log.setFormatter(formatter)
        # logger.addHandler(file_log)
        logger.addHandler(console_log)
        logger.debug("Logging configured")
        return logger


if __name__ == "__main__":
    input("This script is not to be called directly, invoke ./run.py instead.\n\nPress any key to exit.")
    exit()